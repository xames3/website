"""\
Custom Roles
============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February 2025
Last updated on: 26 October 2026

Kaamiki's custom inline roles.
"""

import functools
import re
import typing as t
from hashlib import sha256
from random import Random
from urllib.parse import quote
from urllib.parse import unquote

import docutils.nodes as nodes
from sphinx.domains import Domain
from sphinx.roles import Keyboard

from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import findall
from kaamiki.extensions.utils import glyph
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils.settings import BOUNDS
from kaamiki.extensions.utils.settings import PALETTE
from kaamiki.extensions.utils.settings import PRO_STYLES
from kaamiki.extensions.utils.settings import TONES
from kaamiki.extensions.utils.settings import icon_style

if t.TYPE_CHECKING:
    from collections.abc import Set as AbstractSet

    from sphinx.writers.html import HTMLTranslator

DECLARATION: re.Pattern[str] = re.compile(
    r"[a-z][a-z-]{1,40}: ?[A-Za-z0-9#%.,() /_+-]{1,100}"
)
LAYOUT: t.Final[frozenset[str]] = frozenset(
    {
        "bottom",
        "content",
        "inset",
        "left",
        "pointer-events",
        "position",
        "right",
        "top",
        "z-index",
    }
)
DURATION: re.Pattern[str] = re.compile(r"([0-9]{1,5}(?:\.[0-9]{1,3})?)(ms|s)")
UNITS: t.Final[tuple[tuple[int, str], ...]] = (
    (10**9, "b"),
    (10**6, "m"),
    (10**3, "k"),
)
ROTATE_LENGTH: t.Final[int] = 45
ROLES: t.Final[tuple[str, ...]] = (
    "email",
    "rotate",
    "sharpie",
    "stylise",
    "ticker",
    "underline",
)
ICONS: t.Final[dict[str, str]] = {
    "brands": "fa-brands",
    "duotone": "fa-duotone",
    "light": "fa-light",
    "regular": "fa-regular",
    "solid": "fa-solid",
    "thin": "fa-thin",
}
SYSTEMS: t.Final[dict[str, tuple[str, ...]]] = {
    "mac": (),
    "windows": ("km-windows",),
    "linux": ("km-linux",),
}
GLYPH: re.Pattern[str] = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


class ink(nodes.inline):
    """Text wearing a style, a sharpie or a pencil underline.

    It stays a text node, so the reading time, search index and page
    description see the words and not the markup.
    """


class rotor(ink):
    """The first of some words, which take turns in its place.

    Like an inked text it stays a text node, holding the first word.
    """


def _visit(self: HTMLTranslator, node: ink) -> None:
    """Open the span that carries the style.

    :param self: The HTML translator, whose body this appends to.
    :param node: The inked text.
    """
    self.body.append(self.starttag(node, "span", "", style=node["style"]))


def _moves(node: rotor) -> bool:
    """Tell whether the words take turns here or the first one stays.

    They stay inside a link, which is a toctree, a `:ref:` or a
    `:doc:`, and in a title rendered on its own, which is what the
    breadcrumbs, the page's tab and the previous and next pages get.

    :param node: The rotating words.
    :return: `True` for text in the page itself.
    """
    parent = node.parent
    while parent is not None:
        if isinstance(parent, nodes.reference):
            return False
        if isinstance(parent, nodes.title) and isinstance(
            parent.parent, nodes.document
        ):
            return False
        parent = parent.parent
    return True


def _visit_rotor(self: HTMLTranslator, node: rotor) -> None:
    """Open the span the words take turns in, if they do here.

    :param self: The HTML translator, whose body this appends to.
    :param node: The rotating words.
    """
    if _moves(node):
        attributes: dict[str, t.Any] = {"data-km-words": node["words"]}
        self.body.append(self.starttag(node, "span", "", **attributes))


def _depart_rotor(self: HTMLTranslator, node: rotor) -> None:
    """Close the span, if one was opened.

    :param self: The HTML translator, whose body this appends to.
    :param node: The rotating words.
    """
    if _moves(node):
        self.body.append("</span>")


def _visit_glyph(self: HTMLTranslator, node: glyph) -> None:
    """Open the span that carries the icon.

    :param self: The HTML translator, whose body this appends to.
    :param node: The icon.
    """
    attributes: dict[str, t.Any] = {"aria-hidden": "true"}
    self.body.append(self.starttag(node, "span", "", **attributes))


def _depart(self: HTMLTranslator, node: ink | glyph) -> None:
    """Close the span.

    :param self: The HTML translator, whose body this appends to.
    :param node: The inked text or the icon (unused).
    """
    del node
    self.body.append("</span>")


def _split(text: str) -> tuple[str, str | None]:
    """Split a role's text into its label and what sits in angles.

    :param text: What was written inside the role.
    :return: The label and the value between `<` and `>` or `None`
        when there isn't one.
    """
    if "<" not in text:
        return text, None
    element, value = text.split("<", 1)
    return element.strip(), value.rstrip().removesuffix(">").strip()


def _reject(
    inliner: t.Any, rawtext: str, lineno: int, message: str
) -> tuple[list[nodes.Node], list[nodes.system_message]]:
    """Report a bad role and hand docutils a problematic node.

    :param inliner: The docutils inliner that called the role.
    :param rawtext: The whole role, markup and all.
    :param lineno: The line the role sits on.
    :param message: What's wrong with it.
    :return: The problematic node and the message, as docutils wants
        them.
    """
    msg = inliner.reporter.error(
        message, nodes.literal_block(rawtext, rawtext), line=lineno
    )
    return [inliner.problematic(rawtext, rawtext, msg)], [msg]


def _query(value: str) -> dict[str, str]:
    """Split the settings after a `?` into names and values.

    :param value: What followed the `?`, settings joined by `&`.
    :return: Each setting's name and its value, empty for a bare name.
    :raises ValueError: When a setting is given twice.
    """
    found: dict[str, str] = {}
    for part in value.split("&"):
        part = part.strip()
        if not part:
            continue
        key, _, number = part.partition("=")
        key = key.strip().lower()
        if key in found:
            raise ValueError(f"{key!r} is given twice")
        found[key] = number.strip()
    return found


def _colour(config: t.Any, value: str) -> str:
    """Check a colour a role names and write it the way CSS reads it.

    :param config: The Sphinx configuration.
    :param value: A colour or the name of one.
    :return: The colour, `hsl(...)` for a name Kaamiki or the site
        gave one and `#abc` for a hex colour.
    :raises ValueError: When it's none of those.
    """
    names = setting(config, "role_colours")
    value = checks.colour(value, (*TONES, *names))
    if value in names:
        value = names[value]
    elif value in PALETTE:
        value = PALETTE[value]
    return value if value.startswith("#") else f"hsl({value})"


def _decimal(given: str | None, name: str, site: float) -> float:
    """Read a width or a wobble written after a `?`, or the site's.

    :param given: What was written, or `None` for the site's.
    :param name: `width` or `wobble`.
    :param site: The site's own.
    :return: The number.
    :raises ValueError: When it's not a number in the range it takes.
    """
    low, high = BOUNDS[f"underline_{name}"]
    if given is None:
        return site
    try:
        return checks.number(low, high)(given)
    except ValueError as error:
        raise ValueError(f"{name} {error}") from error


def _short(number: int) -> str:
    """Wrap a number in k, m or b, to one decimal, halves rounding up.

    :param number: The number to wrap.
    :return: The number as written when it's under a thousand.
    """
    if number < 1000:
        return str(number)
    for size, suffix in UNITS:
        tenths = (number * 10 + size // 2) // size
        if tenths >= 10:
            whole, tenth = divmod(tenths, 10)
            return f"{whole}.{tenth}".removesuffix(".0") + suffix
    raise AssertionError(number)


def _underline_svg(
    color: str, seed: str, width: float = 2.5, wobble: float = 1.0
) -> tuple[str, str]:
    """Draw two wobbly strokes for a (fake) hand-drawn underline.

    The wobble is seeded, so the same underline comes out the same on
    every build.

    :param color: The stroke colour, already checked.
    :param seed: What the wobble is drawn from, so the same underline in
        the same place comes out the same on every build.
    :param width: How thick the stroke is.
    :param wobble: How far the stroke strays, `0` being straight.
    :return: The left-to-right and right-to-left SVGs.
    """
    uniform = Random(sha256(seed.encode()).digest()).uniform
    segments = 7
    step = 500 / segments

    def stroke(start: float, stop: float) -> str:
        """Generate a wobbly path between two y anchors."""
        x0 = uniform(1.5, 2.5)
        y0 = start + uniform(-0.4, 0.4) * wobble
        points = [f"M{x0:.1f} {y0:.1f}"]
        for index in range(1, segments):
            mid = start + (stop - start) * index / segments
            midx = step * index - uniform(0, step * 0.4) * wobble
            midy = mid + uniform(-1.2, 1.2) * wobble
            x = step * index + uniform(-2, 2) * wobble
            y = mid + uniform(-0.8, 0.8) * wobble
            points.append(f"Q{midx:.1f} {midy:.1f} {x:.1f} {y:.1f}")
        x1 = uniform(497, 499)
        y1 = stop + uniform(-0.4, 0.4) * wobble
        points.append(f"L{x1:.1f} {y1:.1f}")
        return " ".join(points)

    def make_svg(start: float, stop: float) -> str:
        path = stroke(start, stop)
        return (
            "<svg xmlns='http://www.w3.org/2000/svg'"
            " viewBox='0 0 500 8' preserveAspectRatio='none'>"
            f"<path d='{path}' fill='none' stroke='{color}'"
            f" stroke-width='{width:g}' stroke-linecap='round'/>"
            "</svg>"
        )

    return make_svg(5.5, 2.5), make_svg(2.5, 5.5)


def stylise(
    role: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: t.Any,
    options: dict[str, t.Any] | None = None,
    content: list[t.Any] | None = None,
) -> tuple[list[nodes.Node], list[nodes.system_message]]:
    """Put CSS on a run of text.

    The text reads `label <css>`::

        Text is normal, but now it's :stylise:`red <color: red;>`.

    :param role: The role name, as written (unused).
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role sits on, for error reporting.
    :param inliner: The docutils inliner that called this.
    :param options: Role options (unused).
    :param content: Role content (unused).
    :return: The styled text and the error messages if the text doesn't
        split on a `<`.
    """
    del role, options, content
    element, style = _split(text)
    if style is None:
        return _reject(inliner, rawtext, lineno, f"Invalid style: {text!r}")
    found = [_.strip() for _ in style.split(";") if _.strip()]
    if not element or not found or len(style) > 200:
        return _reject(inliner, rawtext, lineno, f"Invalid style: {text!r}")
    for each in found:
        if (
            not DECLARATION.fullmatch(each)
            or "url(" in each.lower()
            or each.partition(":")[0].strip().startswith(tuple(LAYOUT))
        ):
            return _reject(
                inliner, rawtext, lineno, f"Invalid style declaration: {each!r}"
            )
    return [ink(rawtext, element, style="; ".join(found) + ";")], []


def email(
    role: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: t.Any,
    options: dict[str, t.Any] | None = None,
    content: list[t.Any] | None = None,
) -> tuple[list[nodes.Node], list[nodes.system_message]]:
    """Write a `mailto` link.

    The subject is the page title unless the address names one after a
    `?subject=`. Without a label the address is the label::

        Send me an :email:`email <xa@mes3.dev>`.
        Send me an :email:`email <xa@mes3.dev?subject=Hello hello!!>`.

    :param role: The role name, as written (unused).
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role sits on, for error reporting.
    :param inliner: The docutils inliner that called this.
    :param options: Role options (unused).
    :param content: Role content (unused).
    :return: One `reference` node and the error messages if the text
        doesn't split on a `<` or the address asks for more than a
        subject.
    """
    del role, options, content
    alt, rest = _split(text)
    if rest is None:
        return _reject(inliner, rawtext, lineno, f"Invalid email: {text!r}")
    href, equals, subject = rest.partition("?")
    if not checks.EMAIL.fullmatch(href.strip()):
        return _reject(
            inliner, rawtext, lineno, f"Invalid email address: {href.strip()!r}"
        )
    if equals:
        key, equals, subject = subject.partition("=")
        if key.strip() != "subject" or not equals or not subject.strip():
            return _reject(
                inliner,
                rawtext,
                lineno,
                f"Invalid email setting: {key.strip()!r}; it takes "
                f"subject=text",
            )
        if len(subject.strip()) > 150:
            return _reject(
                inliner, rawtext, lineno, "Invalid email subject: too long"
            )
    alt = alt or href.strip()
    if not subject.strip():
        subject = next(
            (_.astext() for _ in findall(inliner.document, nodes.title)), ""
        )
    refuri = f"mailto:{href.strip()}"
    if subject.strip():
        refuri += f"?subject={quote(unquote(subject.strip()))}"
    return [nodes.reference(rawtext, alt, refuri=refuri)], []


def sharpie(
    role: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: t.Any,
    options: dict[str, t.Any] | None = None,
    content: list[t.Any] | None = None,
) -> tuple[list[nodes.Node], list[nodes.system_message]]:
    """Run a highlighter over a run of text.

    The colour is the site's `sharpie_colour`, yellow, unless the role
    names one, either as a colour or as one of the
    site's `role_colours`::

        This is :sharpie:`important` information.
        This is :sharpie:`critical <red>` information.

    :param role: The role name, as written (unused).
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role sits on, for error reporting.
    :param inliner: The docutils inliner that called this.
    :param options: Role options (unused).
    :param content: Role content (unused).
    :return: The highlighted text and the error messages if the colour
        looks like markup.
    """
    del role, options, content
    element, color = _split(text)
    config = inliner.document.settings.env.config
    try:
        color = _colour(config, color or str(setting(config, "sharpie_colour")))
    except ValueError as error:
        return _reject(inliner, rawtext, lineno, f"Invalid colour: {error}")
    if not element.strip():
        return _reject(
            inliner, rawtext, lineno, f"Invalid sharpie: no text in {text!r}"
        )
    style = f"--km-sharpie-color: {color};"
    return [ink(rawtext, element, classes=["km-sharpie"], style=style)], []


def underline(
    role: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: t.Any,
    options: dict[str, t.Any] | None = None,
    content: list[t.Any] | None = None,
) -> tuple[list[nodes.Node], list[nodes.system_message]]:
    """Draw a pencil underline beneath a run of text.

    The colour, width and wobble are the site's `underline_colour`,
    `underline_width` and `underline_wobble`, orange, 2.5 and 1, unless
    the role names its own after the text. The colour comes first, then
    the width and wobble after a `?`, an `&` between them::

        This is :underline:`notable` content.
        This is :underline:`notable <red>` content.
        This is :underline:`notable <red?width=3&wobble=0>` content.

    The width runs from 0.5 to 4 and the wobble from 0, which is
    straight, to 2.

    :param role: The role name, as written (unused).
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role sits on, for error reporting.
    :param inliner: The docutils inliner that called this.
    :param options: Role options (unused).
    :param content: Role content (unused).
    :return: The underlined text and the error messages if the colour
        looks like markup or the width or wobble is off.
    """
    del role, options, content
    element, rest = _split(text)
    config = inliner.document.settings.env.config
    color, _, query = (rest or "").partition("?")
    try:
        given = _query(query)
        color = _colour(
            config, color.strip() or str(setting(config, "underline_colour"))
        )
        width = _decimal(
            given.pop("width", None),
            "width",
            setting(config, "underline_width"),
        )
        wobble = _decimal(
            given.pop("wobble", None),
            "wobble",
            setting(config, "underline_wobble"),
        )
    except ValueError as error:
        return _reject(inliner, rawtext, lineno, f"Invalid underline: {error}")
    if given or not element.strip():
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"Invalid underline setting: {', '.join(given) or text!r};"
            " it takes width and wobble",
        )
    seed = f"{inliner.document.settings.env.docname}:{lineno}:{rawtext}"
    # NOTE(xames3): A `#` and a `%` have to be percent-encoded inside a
    # data URI.
    # https://datatracker.ietf.org/doc/html/rfc2397
    ltr, rtl = (
        quote(_, safe="/:=,.' <>-")
        for _ in _underline_svg(color, seed, width, wobble)
    )
    style = (
        f'--km-ul-fwd: url("data:image/svg+xml,{ltr}");'
        f' --km-ul-ret: url("data:image/svg+xml,{rtl}");'
    )
    return [ink(rawtext, element, classes=["km-pencil"], style=style)], []


def ticker(
    role: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: t.Any,
    options: dict[str, t.Any] | None = None,
    content: list[t.Any] | None = None,
) -> tuple[list[nodes.Node], list[nodes.system_message]]:
    """Roll a number up from zero.

    The text reads `number`, then `short` and `duration` after a `?`,
    both optional and in either order. `short` wraps the number in k, m
    or b, a whole number shows without it. The duration is in `s` or
    `ms`, from 0.1s to 5s, 2s unless the role gives one. The count
    starts when the number scrolls into view::

        We've :ticker:`2025` stars.
        We've :ticker:`2025?short` stars.
        We've :ticker:`2025?short&duration=1s` stars.

    :param role: The role name, as written (unused).
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role sits on, for error reporting.
    :param inliner: The docutils inliner that called this.
    :param options: Role options (unused).
    :param content: Role content (unused).
    :return: The number and the error messages if it isn't a whole
        number or a setting is off.
    """
    del role, options, content
    number, _, rest = text.partition("?")
    try:
        count = checks.integer(*map(int, BOUNDS["ticker"]))(number.strip())
        given = _query(rest)
    except ValueError as error:
        return _reject(inliner, rawtext, lineno, f"Invalid ticker: {error}")
    short = given.pop("short", None) is not None
    seconds = 2.0
    if "duration" in given:
        found = DURATION.fullmatch(given.pop("duration"))
        if not found:
            return _reject(
                inliner,
                rawtext,
                lineno,
                "Invalid ticker duration: write it in s or ms, 1s or 500ms",
            )
        seconds = float(found[1]) / (1000 if found[2] == "ms" else 1)
    if given:
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"Invalid ticker setting: {', '.join(given)};"
            " it takes short and duration",
        )
    low, high = BOUNDS["ticker_duration"]
    if not low <= seconds <= high:
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"Invalid ticker duration: use a time from {low:g}s to {high:g}s",
        )
    label = _short(count) if short else str(count)
    style = f"--km-ticker-duration: {round(seconds * 1000)}ms;"
    return [ink(rawtext, label, classes=["km-ticker"], style=style)], []


def rotate(
    role: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: t.Any,
    options: dict[str, t.Any] | None = None,
    content: list[t.Any] | None = None,
) -> tuple[list[nodes.Node], list[nodes.system_message]]:
    """Swap a word for the next one, again and again.

    The text lists the words, split by `|`. The first one is what the
    page, its search and a reader without scripts get. In the page the
    rest take its place one by one while the words are on screen, in
    the font, size and colour of the text around them. Where a title is
    shown for something else, in the navbar, the sidebar, the
    breadcrumbs, a toctree or a link, the first word stays as text::

        Rebuilding NumPy to :rotate:`understand|learn|rebuild` it.

    A word is at most 45 characters long. Emoji and text that runs
    right to left are not supported.

    :param role: The role name, as written (unused).
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role sits on, for error reporting.
    :param inliner: The docutils inliner that called this.
    :param options: Role options (unused).
    :param content: Role content (unused).
    :return: The first word and the error messages if there aren't two
        words or one of them is empty.
    """
    del role, options, content
    words = [" ".join(word.split()) for word in text.split("|")]
    if len(words) < 2 or not all(words):
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"Invalid rotate: write two or more words split by |, not {text!r}",
        )
    longest = max(words, key=len)
    if len(longest) > ROTATE_LENGTH:
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"Invalid rotate: a word is at most {ROTATE_LENGTH} characters"
            f" long, {longest!r} has {len(longest)}",
        )
    attributes = {"classes": ["km-rotate"], "words": "|".join(words)}
    return [rotor(rawtext, words[0], **attributes)], []


def _icon(
    style: str | None,
    role: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: t.Any,
    options: dict[str, t.Any] | None = None,
    content: list[t.Any] | None = None,
) -> tuple[list[nodes.Node], list[nodes.system_message]]:
    """Draw a Font Awesome icon.

    The text reads `name` and then any classes, a space between each.
    The role names the style, `fa-icon:brands`, `fa-icon:light`,
    `fa-icon:regular`, `fa-icon:solid`, `fa-icon:thin` or
    `fa-icon:duotone`. A plain `fa-icon` draws in the site's `fa_style`::

        Watch on :fa-icon:brands:`youtube` or listen :fa-icon:`headphones`.
        Show some :fa-icon:solid:`heart km-red` love.

    :param style: The Font Awesome style class, bound by `setup`, or
        `None` for the site's `fa_style`.
    :param role: The role name, as written (unused).
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role sits on, for error reporting.
    :param inliner: The docutils inliner that called this.
    :param options: Role options (unused).
    :param content: Role content (unused).
    :return: The icon and the error messages if the name or a class
        looks like anything but one.
    """
    del role, options, content
    config = inliner.document.settings.env.config
    if style is None:
        style = f"fa-{icon_style(config)}"
    elif style in PRO_STYLES and not setting(config, "fa_kit"):
        style = "fa-solid"
    if not text.split():
        return _reject(inliner, rawtext, lineno, "Invalid icon: it is empty")
    name, *classes = text.split()
    name = name.removeprefix("fa-")
    if not GLYPH.fullmatch(name):
        return _reject(inliner, rawtext, lineno, f"Invalid icon: {name!r}")
    for found in classes:
        if not checks.MODIFIERS.fullmatch(found):
            return _reject(
                inliner, rawtext, lineno, f"Invalid icon class: {found!r}"
            )
    node = glyph(rawtext, classes=[style, f"fa-{name}", "km-glyph", *classes])
    return [node], []


def _keys(
    system: str,
    role: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: t.Any,
    options: dict[str, t.Any] | None = None,
    content: list[t.Any] | None = None,
) -> tuple[list[nodes.Node], list[nodes.system_message]]:
    """Write a keyboard shortcut the way a system prints it.

    It reads like Sphinx's `kbd`, keys joined by `-`, `+` or `^`. The
    role names the system, `kbd:mac`, `kbd:windows` or `kbd:linux`::

        Copy with :kbd:mac:`Cmd-C` or :kbd:windows:`Ctrl-C`.

    :param system: The system, bound by `setup`.
    :param role: The role name, as written.
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role sits on, for error reporting.
    :param inliner: The docutils inliner that called this.
    :param options: Role options.
    :param content: Role content (unused).
    :return: The keys and the error messages, which are none.
    """
    del content
    options = {**(options or {}), "classes": list(SYSTEMS[system])}
    return Keyboard()(role, rawtext, text, lineno, inliner, options)


class quiet(Domain):
    """A domain that holds no data, so a parallel build has nothing to
    merge.
    """

    def merge_domaindata(
        self, docnames: AbstractSet[str], otherdata: dict[str, t.Any]
    ) -> None:
        """Take nothing from the other processes.

        :param docnames: The pages they read.
        :param otherdata: What they kept, which is nothing.
        """


class fa_icon(quiet):
    """The `fa-icon:` roles, one for each Font Awesome style."""

    name: t.ClassVar[str] = "fa-icon"
    label: t.ClassVar[str] = "Font Awesome"
    roles = {  # noqa: RUF012
        key: functools.partial(_icon, style) for key, style in ICONS.items()
    }


class kbd(quiet):
    """The `kbd:` roles, one for each system."""

    name: t.ClassVar[str] = "kbd"
    label: t.ClassVar[str] = "Keyboard"
    roles = {  # noqa: RUF012
        key: functools.partial(_keys, key) for key in SYSTEMS
    }
