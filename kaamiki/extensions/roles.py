"""\
Custom Roles
============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February 2025
Last updated on: 07 November 2026

Kaamiki's custom inline roles.
"""

from __future__ import annotations

import functools
import re
import typing as t
from hashlib import sha256
from random import Random
from urllib.parse import quote
from urllib.parse import unquote

import docutils.nodes as nodes
import docutils.parsers.rst as rst
from docutils.parsers.rst.directives import misc
from docutils.utils import unescape
from sphinx.domains import Domain
from sphinx.roles import Keyboard

from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import findall
from kaamiki.extensions.utils import glyph
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils.icons import Icons
from kaamiki.extensions.utils.settings import BOUNDS
from kaamiki.extensions.utils.settings import PALETTE
from kaamiki.extensions.utils.settings import TONES
from kaamiki.extensions.utils.text import tidy

if t.TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Iterable
    from collections.abc import Sequence
    from collections.abc import Set as AbstractSet

    from docutils.parsers.rst import Directive
    from docutils.parsers.rst import states
    from sphinx.application import Sphinx
    from sphinx.config import Config
    from sphinx.writers.html import HTMLTranslator

DECLARATION: re.Pattern[str] = re.compile(
    r"[a-z][a-z-]{1,40}: ?[A-Za-z0-9#%.,() /_+-]{1,100}"
)
TEXT: t.Final[frozenset[str]] = frozenset(
    {
        "background-color",
        "color",
        "font-family",
        "font-size",
        "font-style",
        "font-variant",
        "font-variant-caps",
        "font-variant-numeric",
        "font-weight",
        "letter-spacing",
        "text-decoration",
        "text-decoration-color",
        "text-decoration-line",
        "text-decoration-style",
        "text-decoration-thickness",
        "text-shadow",
        "text-transform",
        "text-underline-offset",
        "word-spacing",
    }
)
SIZE_LIMITS: t.Final[dict[str, int]] = {"em": 4, "px": 64, "rem": 4, "%": 400}
SIZE: re.Pattern[str] = re.compile(r"([0-9]+(?:\.[0-9]+)?)(em|px|rem|%)")
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
STYLE_CLASSES: t.Final[dict[str, str]] = {
    "brands": "fa-brands",
    "duotone": "fa-duotone",
    "light": "fa-light",
    "regular": "fa-regular",
    "solid": "fa-solid",
    "thin": "fa-thin",
}
SYSTEMS: t.Final[dict[str, tuple[str, ...]]] = {
    "mac": (),
    "windows": ("km-key--windows",),
    "linux": ("km-key--linux",),
}
GLYPH: re.Pattern[str] = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
BAR: re.Pattern[str] = re.compile(r"(?<!\x00)\|")
VALUE: re.Pattern[str] = re.compile(r"(?:^|(?<=\s))<([^<]*)(?<!\x00)>\Z")
OPENED: re.Pattern[str] = re.compile(r"(?:^|(?<=\s))<(?=\S)[^>]*\Z")
Reply = tuple[list[nodes.Node], list[nodes.system_message]]


class base:
    """A role that `.. role::` can build another on.

    Docutils reads `options` to learn what the block under `.. role::`
    may hold, so a role carries its own: `class`, which every role
    takes, and whatever else it lets a site preset.
    """

    def __init__(
        self,
        function: Callable[..., Reply],
        options: dict[str, Callable[[str | None], t.Any]] | None = None,
    ) -> None:
        """Wrap a role function with the options it takes.

        :param function: The role function.
        :param options: The options besides `class`, each with the
            check for its value.
        """
        self.function = function
        self.options = {"class": checks.classes, **(options or {})}
        functools.update_wrapper(self, function)

    def __call__(
        self,
        name: str,
        rawtext: str,
        text: str,
        lineno: int,
        inliner: states.Inliner,
        options: dict[str, t.Any] | None = None,
        content: Sequence[str] = (),
    ) -> Reply:
        """Call the role function, with options that are never `None`.

        :param name: The role name, as written.
        :param rawtext: The whole role, markup and all.
        :param text: What was written inside it.
        :param lineno: The line the role's paragraph starts on, for
            error reporting.
        :param inliner: The docutils inliner that called this.
        :param options: The classes and presets of a custom role.
        :param content: Role content.
        :return: The nodes and the error messages.
        """
        return self.function(
            name, rawtext, text, lineno, inliner, options or {}, content
        )


def accepts(
    **options: Callable[[str | None], t.Any],
) -> Callable[[Callable[..., Reply]], base]:
    """Make a role function a `base` that takes the options given.

    :param options: Each option a custom role may preset, with the
        check for its value.
    :return: The decorator.
    """

    def decorate(function: Callable[..., Reply]) -> base:
        return base(function, options)

    return decorate


def _classes(options: dict[str, t.Any]) -> list[str]:
    """Read the classes a custom role gives what it draws.

    :param options: The options the role was called with.
    :return: The classes, the role's own name unless `.. role::` said
        otherwise.
    """
    return list(options.get("classes", []))


class ink(nodes.inline):
    """Text wearing a style, a sharpie or a pencil underline.

    It stays a text node, so the reading time, search index and page
    description see the words and not the markup.
    """


class rotor(ink):
    """The first of some words, which take turns in its place.

    Like an inked text it stays a text node, holding the first word.
    """


def steady(
    directive: Directive,
    found: Iterable[nodes.Node] | nodes.Node,
    part: str,
    why: str,
) -> None:
    """Refuse `:rotate:` in a text that has to stay where it is.

    :param directive: The directive that has the text.
    :param found: The parsed text or the nodes it came to.
    :param part: What the text is, `a title` for one.
    :param why: Why it can't move, for the message.
    :raises rst.DirectiveError: When the text holds rotating words.
    """
    for each in [found] if isinstance(found, nodes.Node) else found:
        if any(isinstance(_, rotor) for _ in each.findall()):
            raise directive.error(
                f"{directive.name}: expected {part} that stays put, got"
                f" :rotate:, {why}"
            )


def _visit(self: HTMLTranslator, node: ink) -> None:
    """Open the span that carries the style, if the text is in the page
    itself.

    :param self: The HTML translator, whose body this appends to.
    :param node: The inked text.
    """
    if _moves(node):
        self.body.append(self.starttag(node, "span", "", style=node["style"]))


def _moves(node: ink) -> bool:
    """Tell whether an inked text keeps its style here or is plain.

    It's plain inside a link, which is a toctree, a `:ref:` or a
    `:doc:`, and in a title rendered on its own, which is what the
    breadcrumbs, the page's tab and the previous and next pages get.
    The rotating words show their first one there.

    :param node: The inked text or the rotating words.
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
    """Close the span, if one was opened.

    :param self: The HTML translator, whose body this appends to.
    :param node: The inked text or the icon.
    """
    if isinstance(node, ink) and not _moves(node):
        return
    self.body.append("</span>")


def _split(text: str, what: str) -> tuple[str, str | None]:
    """Split a role's text into its label and what sits in angles.

    The value is a last `<...>` that opens the text or follows a space,
    the way docutils reads `text <target>`, so `x < 5` and `List<int>`
    are labels. An escaped angle is no angle.

    :param text: What was written inside the role, escapes and all.
    :param what: What the value is, `a colour` say.
    :return: The label and the value between `<` and `>`, both with
        their escapes undone, or `None` when there isn't a value.
    :raises ValueError: When a value isn't closed or is empty.
    """
    found = VALUE.search(text)
    if found is None:
        if OPENED.search(text):
            raise ValueError(
                f"expected {what} between < and >, got {unescape(text)!r}"
            )
        return unescape(text).strip(), None
    value = unescape(found[1]).strip()
    if not value:
        raise ValueError(f"expected {what} between < and >, got none")
    return unescape(text[: found.start()]).strip(), value


def _placed(inliner: states.Inliner, rawtext: str, lineno: int) -> int:
    """Find the line a role is on.

    docutils gives a role the line its paragraph starts on, so a role
    further down is looked for in the source from there.

    :param inliner: The docutils inliner that called the role.
    :param rawtext: The whole role, markup and all.
    :param lineno: The line the role's paragraph starts on.
    :return: The line, or `lineno` when the source can't be read.
    """
    try:
        source, start = inliner.reporter.get_source_and_line(lineno)
    except AttributeError:
        return lineno
    if source is None or start is None:
        return lineno
    try:
        with open(source, encoding="utf-8") as fd:
            lines = fd.read().splitlines()[start - 1 :]
    except OSError, ValueError:
        return lineno
    first = (rawtext.splitlines() or [""])[0]
    return lineno + next((n for n, _ in enumerate(lines) if first in _), 0)


def _reject(
    inliner: states.Inliner, rawtext: str, lineno: int, message: str
) -> tuple[list[nodes.Node], list[nodes.system_message]]:
    """Report a bad role and hand docutils a problematic node.

    :param inliner: The docutils inliner that called the role.
    :param rawtext: The whole role, markup and all.
    :param lineno: The line the role's paragraph starts on.
    :param message: What's wrong with it.
    :return: The problematic node and the message, as docutils wants
        them.
    """
    msg = inliner.reporter.error(
        message,
        nodes.literal_block(rawtext, rawtext),
        line=_placed(inliner, rawtext, lineno),
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


def _colour(config: Config, value: str) -> str:
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

    A number moves up a unit only when it rounds to a thousand of the
    one it's in, so 950000 is `950k` and 999950 is `1m`.

    :param number: The number to wrap.
    :return: The number as written when it's under a thousand.
    """
    if number < 1000:
        return str(number)
    index = next(n for n, (size, _) in enumerate(UNITS) if number >= size)
    size = UNITS[index][0]
    if index and (number * 10 + size // 2) // size >= 10000:
        index -= 1
    size, suffix = UNITS[index]
    whole, tenth = divmod((number * 10 + size // 2) // size, 10)
    return f"{whole}.{tenth}".removesuffix(".0") + suffix


def _underline_svg(
    colour: str, seed: str, width: float, wobble: float
) -> tuple[str, str]:
    """Draw two wobbly strokes for a (fake) hand-drawn underline.

    The wobble is seeded, so the same underline comes out the same on
    every build.

    :param colour: The stroke colour, already checked.
    :param seed: What the wobble is drawn from, so the same underline
        in the same place comes out the same on every build.
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
            f"<path d='{path}' fill='none' stroke='{colour}'"
            f" stroke-width='{width:g}' stroke-linecap='round'/>"
            "</svg>"
        )

    return make_svg(5.5, 2.5), make_svg(2.5, 5.5)


def _declared(each: str) -> bool:
    """Tell whether a CSS declaration is one the role may write.

    :param each: One declaration, like `color: red`.
    :return: `True` when it styles text and nothing more: a property of
        `TEXT`, no `url()` and a `font-size` that stays readable.
    """
    if not DECLARATION.fullmatch(each) or "url(" in each.lower():
        return False
    name, _, value = each.partition(":")
    if name.strip() not in TEXT:
        return False
    if name.strip() != "font-size":
        return True
    size = SIZE.fullmatch(value.strip())
    return size is not None and float(size[1]) <= SIZE_LIMITS[size[2]]


def _style(argument: str | None) -> str:
    """Read the CSS a custom role presets.

    :param argument: The declarations as written.
    :return: The declarations, joined and ending in `;`.
    :raises ValueError: For a style over 200 characters or a
        declaration that doesn't style text.
    """
    style = (argument or "").strip()
    found = [_.strip() for _ in style.split(";") if _.strip()]
    if not found or len(style) > 200:
        raise ValueError(
            f"expected a style up to 200 characters, got {argument!r}"
        )
    for each in found:
        if not _declared(each):
            raise ValueError(
                f"expected a text declaration like color: red, got {each!r}"
            )
    return "; ".join(found) + ";"


@accepts(style=_style)
def stylise(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: states.Inliner,
    options: dict[str, t.Any],
    content: list[t.Any],
) -> Reply:
    """Put CSS on a run of text.

    The text reads `label <css>`, or only `label` for a role that
    presets the `style`. Only properties that style text are allowed,
    `color`, `font-size` up to 4rem and `text-decoration` among them::

        Text is normal, but now it's :stylise:`red <color: red;>`.

    :param name: The role name, as written (unused).
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role's paragraph starts on, for error
        reporting.
    :param inliner: The docutils inliner that called this.
    :param options: The classes and `style` of a custom role.
    :param content: Role content (unused).
    :return: The styled text and the error messages if the text doesn't
        split on a `<` and no `style` was preset.
    """
    del name, content
    said = unescape(text)
    try:
        element, style = _split(text, "a style")
    except ValueError as error:
        return _reject(inliner, rawtext, lineno, f"stylise: {error}")
    if style is None:
        style = options.get("style")
    if style is None:
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"stylise: expected text like `words <color: red;>`, got {said!r}",
        )
    found = [_.strip() for _ in style.split(";") if _.strip()]
    if not element or not found or len(style) > 200:
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"stylise: expected text like `words <color: red;>` and a style"
            f" up to 200 characters, got {said!r}",
        )
    for each in found:
        if not _declared(each):
            return _reject(
                inliner,
                rawtext,
                lineno,
                f"stylise: expected a text declaration like color: red, got"
                f" {each!r}",
            )
    return [
        ink(
            rawtext,
            element,
            classes=_classes(options),
            style="; ".join(found) + ";",
        )
    ], []


@accepts(subject=lambda _: checks.text(_, 150))
def email(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: states.Inliner,
    options: dict[str, t.Any],
    content: list[t.Any],
) -> Reply:
    """Write a `mailto` link.

    The subject is the page's title, once the page is read, unless the
    address names one after a `?subject=` or a custom role presets the
    `subject`. Without a label the address is the label, with the angle
    brackets or without them::

        Send me an :email:`email <xa@mes3.dev>`.
        Send me an :email:`email <xa@mes3.dev?subject=Hello hello!!>`.
        Write to :email:`xa@mes3.dev` or :email:`<xa@mes3.dev>`.

    :param name: The role name, as written (unused).
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role's paragraph starts on, for error
        reporting.
    :param inliner: The docutils inliner that called this.
    :param options: The classes and `subject` of a custom role.
    :param content: Role content (unused).
    :return: One `reference` node and the error messages if the address
        isn't one or it asks for more than a subject.
    """
    del name, content
    try:
        alt, rest = _split(text, "an address")
    except ValueError as error:
        return _reject(inliner, rawtext, lineno, f"email: {error}")
    if rest is None:
        alt, rest = "", alt
    href, asked, subject = rest.partition("?")
    href = href.strip()
    if not checks.EMAIL.fullmatch(href):
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"email: expected an email address, got {href!r}",
        )
    if asked:
        key, equals, subject = subject.partition("=")
        subject = tidy(subject)
        if re.search(r"&[A-Za-z]+=", subject):
            return _reject(
                inliner,
                rawtext,
                lineno,
                "email: expected only subject=text, got more after it",
            )
        if key.strip().lower() != "subject" or (not equals and subject):
            return _reject(
                inliner,
                rawtext,
                lineno,
                f"email: expected subject=text, got {key.strip()!r}",
            )
        if not subject:
            return _reject(
                inliner,
                rawtext,
                lineno,
                "email: expected some text after subject=, got none",
            )
        if len(subject) > 150:
            return _reject(
                inliner,
                rawtext,
                lineno,
                "email: expected a subject up to 150 characters, got a longer"
                " one",
            )
    subject = subject or tidy(options.get("subject", ""))
    refuri = f"mailto:{href}"
    if subject:
        refuri += f"?subject={quote(unquote(subject))}"
    link = nodes.reference(
        rawtext, alt or href, refuri=refuri, classes=_classes(options)
    )
    if not subject:
        link["titled"] = True
    return [link], []


@accepts(colour=checks.text)
def sharpie(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: states.Inliner,
    options: dict[str, t.Any],
    content: list[t.Any],
) -> Reply:
    """Run a highlighter over a run of text.

    The colour is the site's `kaamiki.conf.roles.sharpie_colour`,
    yellow, unless a custom role presets the `colour` or the role names
    one, either as a colour or as one of the site's
    `kaamiki.conf.roles.colours`::

        This is :sharpie:`important` information.
        This is :sharpie:`critical <red>` information.

    :param name: The role name, as written (unused).
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role's paragraph starts on, for error
        reporting.
    :param inliner: The docutils inliner that called this.
    :param options: The classes and `colour` of a custom role.
    :param content: Role content (unused).
    :return: The highlighted text and the error messages if the colour
        looks like markup.
    """
    del name, content
    config = inliner.document.settings.env.config
    preset = options.get("colour") or str(setting(config, "sharpie_colour"))
    try:
        element, colour = _split(text, "a colour")
        colour = _colour(config, colour or preset)
    except ValueError as error:
        return _reject(inliner, rawtext, lineno, f"sharpie: {error}")
    if not element:
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"sharpie: expected some text, got none in {unescape(text)!r}",
        )
    style = f"--km-sharpie-colour: {colour};"
    classes = ["km-sharpie", *_classes(options)]
    return [ink(rawtext, element, classes=classes, style=style)], []


@accepts(
    colour=checks.text,
    width=checks.number(*BOUNDS["underline_width"]),
    wobble=checks.number(*BOUNDS["underline_wobble"]),
)
def underline(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: states.Inliner,
    options: dict[str, t.Any],
    content: list[t.Any],
) -> Reply:
    """Draw a pencil underline beneath a run of text.

    The colour, width and wobble are the site's
    `kaamiki.conf.roles.underline_colour`,
    `kaamiki.conf.roles.underline_width`
    and `kaamiki.conf.roles.underline_wobble`, orange, 2.5 and 1,
    unless a custom role presets its own or the role names its own
    after the text. The colour comes first, then the width and wobble
    after a `?`, an `&` between them::

        This is :underline:`notable` content.
        This is :underline:`notable <red>` content.
        This is :underline:`notable <red?width=3&wobble=0>` content.

    The width runs from 0.5 to 4 and the wobble from 0, which is
    straight, to 2.

    :param name: The role name, as written (unused).
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role's paragraph starts on, for error
        reporting.
    :param inliner: The docutils inliner that called this.
    :param options: The classes, `colour`, `width` and `wobble` of a
        custom role.
    :param content: Role content (unused).
    :return: The underlined text and the error messages if the colour
        looks like markup or the width or wobble is off.
    """
    del name, content
    config = inliner.document.settings.env.config
    preset = options.get("colour") or str(setting(config, "underline_colour"))
    try:
        element, rest = _split(text, "a colour or settings")
        colour, asked, query = (rest or "").partition("?")
        if asked and not query.strip():
            raise ValueError("expected width or wobble after ?, got none")
        given = _query(query)
        colour = _colour(config, colour.strip() or preset)
        width = _decimal(
            given.pop("width", None),
            "width",
            options.get("width", setting(config, "underline_width")),
        )
        wobble = _decimal(
            given.pop("wobble", None),
            "wobble",
            options.get("wobble", setting(config, "underline_wobble")),
        )
    except ValueError as error:
        return _reject(inliner, rawtext, lineno, f"underline: {error}")
    if given or not element:
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"underline: expected some text and width or wobble, got"
            f" {', '.join(given) or unescape(text)!r}",
        )
    seed = f"{inliner.document.settings.env.docname}:{lineno}:{rawtext}"
    # NOTE(xames3): A `#` and a `%` have to be percent-encoded inside a
    # data URI.
    # https://datatracker.ietf.org/doc/html/rfc2397
    ltr, rtl = (
        quote(_, safe="/:=,.' <>-")
        for _ in _underline_svg(colour, seed, width, wobble)
    )
    style = (
        f'--km-underline-forward: url("data:image/svg+xml,{ltr}");'
        f' --km-underline-return: url("data:image/svg+xml,{rtl}");'
    )
    classes = ["km-pencil", *_classes(options)]
    return [ink(rawtext, element, classes=classes, style=style)], []


def _duration(argument: str | None) -> float:
    """Read how long a ticker takes to count, in seconds.

    :param argument: The duration as written, like `1s` or `500ms`.
    :return: The seconds.
    :raises ValueError: When it isn't a duration or isn't from the
        least to the most a ticker takes.
    """
    written = (argument or "").strip()
    found = DURATION.fullmatch(written)
    if not found:
        raise ValueError(
            f"expected a duration like 1s or 500ms, got {written!r}"
        )
    seconds = float(found[1]) / (1000 if found[2] == "ms" else 1)
    low, high = BOUNDS["ticker_duration"]
    if not low <= seconds <= high:
        raise ValueError(
            f"expected a duration from {low:g}s to {high:g}s, got {seconds:g}s"
        )
    return seconds


@accepts(short=rst.directives.flag, duration=_duration)
def ticker(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: states.Inliner,
    options: dict[str, t.Any],
    content: list[t.Any],
) -> Reply:
    """Roll a number up from zero.

    The text reads `number`, then `short` and `duration` after a `?`,
    both optional and in either order. `short` wraps the number in k, m
    or b and takes no value, a whole number shows without it. The
    duration is in `s` or `ms`, from 0.1s to 5s, 2s unless the role
    gives one or a custom role presets it. The count starts when the
    number scrolls into view::

        We've :ticker:`2025` stars.
        We've :ticker:`2025?short` stars.
        We've :ticker:`2025?short&duration=1s` stars.

    :param name: The role name, as written (unused).
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role's paragraph starts on, for error
        reporting.
    :param inliner: The docutils inliner that called this.
    :param options: The classes, `short` and `duration` of a custom
        role.
    :param content: Role content (unused).
    :return: The number and the error messages if it isn't a whole
        number or a setting is off.
    """
    del name, content
    number, asked, rest = unescape(text).partition("?")
    try:
        count = checks.integer(*map(int, BOUNDS["ticker"]))(number.strip())
        if asked and not rest.strip():
            raise ValueError("expected short or duration after ?, got none")
        given = _query(rest)
    except ValueError as error:
        return _reject(inliner, rawtext, lineno, f"ticker: {error}")
    if given.get("short"):
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"ticker: expected short with no value, got {given['short']!r}",
        )
    short = given.pop("short", None) is not None or "short" in options
    seconds = options.get("duration", 2.0)
    if "duration" in given:
        try:
            seconds = _duration(given.pop("duration"))
        except ValueError as error:
            return _reject(inliner, rawtext, lineno, f"ticker: {error}")
    if given:
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"ticker: expected short or duration, got {', '.join(given)}",
        )
    label = _short(count) if short else str(count)
    style = f"--km-ticker-duration: {round(seconds * 1000)}ms;"
    classes = ["km-ticker", *_classes(options)]
    return [ink(rawtext, label, classes=classes, style=style)], []


@accepts()
def rotate(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: states.Inliner,
    options: dict[str, t.Any],
    content: list[t.Any],
) -> Reply:
    """Swap a word for the next one, again and again.

    The text lists the words, split by `|`. The first one is what the
    page, its search and a reader without scripts get. In the page the
    rest take its place one by one while the words are on screen, in
    the font, size and colour of the text around them. Where a title is
    shown for something else, in the navbar, the sidebar, the
    breadcrumbs, a toctree or a link, the first word stays as text::

        Rebuilding NumPy to :rotate:`understand|learn|rebuild` it.

    A word is at most 45 characters long, counted as code points, and
    holds no `|`. The words keep the quotes they were written with.

    :param name: The role name, as written (unused).
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role's paragraph starts on, for error
        reporting.
    :param inliner: The docutils inliner that called this.
    :param options: The classes of a custom role.
    :param content: Role content (unused).
    :return: The first word and the error messages if there aren't two
        words or one of them is empty, too long or holds a `|`.
    """
    del name, content
    words = [tidy(unescape(_)) for _ in BAR.split(text)]
    if len(words) < 2 or not all(words):
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"rotate: expected two or more words split by |, got"
            f" {unescape(text)!r}",
        )
    barred = next((_ for _ in words if "|" in _), None)
    if barred is not None:
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"rotate: expected words without |, got {barred!r}",
        )
    longest = max(words, key=len)
    if len(longest) > ROTATE_LENGTH:
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"rotate: expected words up to {ROTATE_LENGTH} characters, got"
            f" {longest!r} with {len(longest)}",
        )
    attributes = {
        "classes": ["km-rotate", *_classes(options)],
        "words": "|".join(words),
        "support_smartquotes": False,
    }
    return [rotor(rawtext, words[0], **attributes)], []


def _icon(
    style: str | None,
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: states.Inliner,
    options: dict[str, t.Any],
    content: list[t.Any],
) -> Reply:
    """Draw a Font Awesome icon.

    The text reads `name` and then any classes, a space between each.
    The role names the style, `fa-icon:brands`, `fa-icon:light`,
    `fa-icon:regular`, `fa-icon:solid`, `fa-icon:thin` or
    `fa-icon:duotone`. A plain `fa-icon` draws in the site's
    `kaamiki.conf.icons.style`::

        Watch on :fa-icon:brands:`youtube` or listen :fa-icon:`music`.
        Show some :fa-icon:solid:`heart km-tone--red` love.

    :param style: The Font Awesome style class, bound when the module
        is imported by `icon` and `fa_icon.roles`, or `None` for the
        site's `kaamiki.conf.icons.style`.
    :param name: The role name, as written (unused).
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role's paragraph starts on, for error
        reporting.
    :param inliner: The docutils inliner that called this.
    :param options: The classes of a custom role.
    :param content: Role content (unused).
    :return: The icon and the error messages if the name or a class
        looks like anything but one.
    """
    del name, content
    config = inliner.document.settings.env.config
    text = unescape(text)
    if not text.split():
        return _reject(
            inliner, rawtext, lineno, "fa-icon: expected an icon name, got none"
        )
    name, *classes = text.split()
    name = name.removeprefix("fa-")
    if not GLYPH.fullmatch(name):
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"fa-icon: expected a name like star, got {name!r}",
        )
    for found in classes:
        if not checks.MODIFIERS.fullmatch(found):
            return _reject(
                inliner,
                rawtext,
                lineno,
                f"fa-icon: expected a Font Awesome size or animation or a km-"
                f" colour, got {found!r}",
            )
    spec = " ".join(filter(None, [style, f"fa-{name}"]))
    try:
        drawn = Icons.of(config).classes(spec).split()
    except ValueError as error:
        return _reject(inliner, rawtext, lineno, f"fa-icon: {error}")
    return [
        glyph(
            rawtext,
            classes=[*drawn, "km-glyph", *classes, *_classes(options)],
        )
    ], []


def _keys(
    system: str,
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: states.Inliner,
    options: dict[str, t.Any],
    content: list[t.Any],
) -> Reply:
    """Write a keyboard shortcut the way a system prints it.

    It reads like Sphinx's `kbd`, keys joined by `-`, `+` or `^`. The
    role names the system, `kbd:mac`, `kbd:windows` or `kbd:linux`::

        Copy with :kbd:mac:`Cmd-C` or :kbd:windows:`Ctrl-C`.

    :param system: The system, bound when the module is imported by
        `kbd.roles`.
    :param name: The role name, as written.
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role's paragraph starts on, for error
        reporting.
    :param inliner: The docutils inliner that called this.
    :param options: The classes of a custom role.
    :param content: Role content (unused).
    :return: The keys and the error messages, which are none.
    """
    del content
    classes = [*SYSTEMS[system], *_classes(options)]
    options = {**options, "classes": classes}
    return Keyboard()(name, rawtext, text, lineno, inliner, options)


icon = base(functools.partial(_icon, None))


class role(misc.Role):
    """The `role` directive, which also checks the colour a role presets.

    docutils checks the other presets as it reads them. A colour is
    only a name until the site's `kaamiki.conf.roles.colours` are
    known, so this checks it where the role is made and the line is the
    right one.
    """

    def run(self) -> Sequence[nodes.Node]:
        """Make the role and check the colour it presets.

        :return: The messages docutils gives.
        :raises rst.DirectiveError: When the colour is none Kaamiki
            knows.
        """
        found = super().run()
        if any(
            isinstance(_, nodes.system_message) and _["level"] >= 3
            for _ in found
        ):
            return found
        match = self.argument_pattern.match(self.content[0])
        made, _ = rst.roles.role(
            match[1] if match else "",
            t.cast("t.Any", self.state_machine.language),
            self.lineno,
            self.state.reporter,
        )
        preset = getattr(made, "supplied_options", {}).get("colour")
        if preset:
            config = self.state.document.settings.env.config
            try:
                _colour(config, preset)
            except ValueError as error:
                raise self.error(f"role: :colour: {error}") from error
        return found


def subjects(app: Sphinx, doctree: nodes.document) -> None:
    """Give an email link with no subject the page's title for one.

    The role can't, since the title isn't known while a page is read,
    and in a translated paragraph or a `rst_prolog` substitution it
    never is. Once the page is read, the title is in the tree.

    :param app: The Sphinx application instance (unused).
    :param doctree: The page, just read.
    """
    del app
    section = next(findall(doctree, nodes.section), None)
    title = tidy(section[0].astext()) if section is not None else ""
    for link in findall(doctree, nodes.reference):
        if "titled" not in link:
            continue
        del link["titled"]
        if title:
            link["refuri"] += f"?subject={quote(title)}"


class quiet(Domain):
    """A domain that holds no data, so a parallel build has nothing to
    merge.

    Its roles are `base` ones, so a custom role can be built on any of
    them.
    """

    def role(self, name: str) -> base | None:
        """Hand docutils a role that knows its full name and its
        options.

        :param name: The role's name inside the domain.
        :return: The role, or `None` when the domain has none by that
            name.
        """
        found = self.roles.get(name)
        if found is None:
            return None
        full = f"{self.name}:{name}"
        return base(
            lambda _, *rest: found(full, *rest),
            getattr(found, "options", {}),
        )

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
        key: base(functools.partial(_icon, style))
        for key, style in STYLE_CLASSES.items()
    }


class kbd(quiet):
    """The `kbd:` roles, one for each system."""

    name: t.ClassVar[str] = "kbd"
    label: t.ClassVar[str] = "Keyboard"
    roles = {  # noqa: RUF012
        key: base(functools.partial(_keys, key)) for key in SYSTEMS
    }
