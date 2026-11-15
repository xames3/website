"""\
Custom Roles
============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February 2025
Last updated on: 15 November 2026

The custom inline roles of Kaamiki.
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
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import values
from kaamiki.extensions.utils.hooks import on
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

DECLARATION: t.Final[re.Pattern[str]] = re.compile(
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
SIZE: t.Final[re.Pattern[str]] = re.compile(
    r"([0-9]+(?:\.[0-9]+)?)(em|px|rem|%)"
)
DURATION: t.Final[re.Pattern[str]] = re.compile(
    r"([0-9]{1,5}(?:\.[0-9]{1,3})?)(ms|s)"
)
UNITS: t.Final[tuple[tuple[int, str], ...]] = (
    (10**9, "b"),
    (10**6, "m"),
    (10**3, "k"),
)
SWAP_LENGTH: t.Final[int] = 45
SWEEP_LENGTH: t.Final[int] = 120
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
GLYPH: t.Final[re.Pattern[str]] = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
BAR: t.Final[re.Pattern[str]] = re.compile(r"(?<!\x00)\|")
VALUE: t.Final[re.Pattern[str]] = re.compile(
    r"(?:^|(?<=\s))<([^<]*)(?<!\x00)>\Z"
)
OPENED: t.Final[re.Pattern[str]] = re.compile(r"(?:^|(?<=\s))<(?=\S)[^>]*\Z")
Reply = tuple[list[nodes.Node], list[nodes.system_message]]


class KaamikiRole:
    """A Kaamiki role, which `.. role::` can also use as a base."""

    registry: t.ClassVar[dict[str, KaamikiRole]] = {}

    def __init__(
        self,
        function: Callable[..., Reply],
        options: dict[str, Callable[[str | None], t.Any]] | None = None,
        *,
        name: str = "",
    ) -> None:
        """Wrap a role function with the options that it takes.

        :param function: The role function.
        :param options: The options other than `class`, each with the
            check for its value. docutils reads `options` to know what
            the block below `.. role::` can hold.
        :param name: The name of the role in rST. With it, the role is
            recorded in `registry`.
        """
        self.function = function
        self.options = {"class": checks.classes, **(options or {})}
        functools.update_wrapper(self, function)
        if name:
            KaamikiRole.registry[name] = self

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

        :param name: The name of the role, as written.
        :param rawtext: All of the role, with its markup.
        :param text: The text in the role.
        :param lineno: The line where the paragraph of the role starts,
            for the error messages.
        :param inliner: The docutils inliner that called the role.
        :param options: The classes and presets of a custom role.
        :param content: The content of the role.
        :return: The nodes and the error messages.
        """
        return self.function(
            name, rawtext, text, lineno, inliner, options or {}, content
        )


def role(
    name: str = "", **options: Callable[[str | None], t.Any]
) -> Callable[[Callable[..., Reply]], KaamikiRole]:
    """Give docutils a role with its full name and options.

    :param name: The name of the role in rST. The default is the name
        of the function.
    :param options: Each option that a custom role can preset, with the
        check for its value.
    :return: The decorator.
    """

    def record(function: Callable[..., Reply]) -> KaamikiRole:
        return KaamikiRole(function, options, name=name or function.__name__)

    return record


def _classes(options: dict[str, t.Any]) -> list[str]:
    """Read the classes that a custom role gives to its text.

    :param options: The options of the role.
    :return: The classes. The default is the name of the role, unless
        `.. role::` sets others.
    """
    return list(options.get("classes", []))


class Ink(nodes.inline):
    """Text with a style, a sharpie or a pencil underline."""


class Swapper(Ink):
    """The first of the words that show one after another."""


def steady(
    directive: Directive,
    found: Iterable[nodes.Node] | nodes.Node,
    part: str,
    why: str,
) -> None:
    """Refuse `:swap:` and `:sweep:` in a text that must not move.

    :param directive: The directive that has the text.
    :param found: The parsed text or its nodes.
    :param part: What the text is, as `a title`.
    :param why: Why it cannot move, for the message.
    :raises rst.DirectiveError: When the text has swapping words.
    """
    for each in [found] if isinstance(found, nodes.Node) else found:
        moving = next(each.findall(Swapper), None)
        if moving is not None:
            role = "sweep" if "km-sweep" in moving["classes"] else "swap"
            raise directive.error(
                f"{directive.name}: expected {part} that stays put, got"
                f" :{role}:, {why}"
            )


@html.opens(Ink)
def visit(self: HTMLTranslator, node: Ink) -> None:
    """Open the span with the style, unless the text is plain.

    :param self: The HTML translator, whose body this appends to.
    :param node: The inked text.
    """
    if _moves(node):
        style = {"style": node["style"]} if node["style"] else {}
        self.body.append(self.starttag(node, "span", "", **style))


def _moves(node: Ink) -> bool:
    """Say whether inked text keeps its style here, or is plain.

    :param node: The inked text or the swapping words.
    :return: `True` for text in the page itself. The text is plain in a
        link (a toctree, a `:ref:` or a `:doc:`) and in a title that
        shows alone, as in the breadcrumbs, the tab of the page and the
        previous and next pages. There, swapping words show only the
        first word.
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


@html.opens(Swapper)
def visit_swapper(self: HTMLTranslator, node: Swapper) -> None:
    """Open the span for the swapping words, if they swap here.

    :param self: The HTML translator, whose body this appends to.
    :param node: The swapping words.
    """
    if _moves(node):
        attributes: dict[str, t.Any] = {"data-km-words": node["words"]}
        self.body.append(self.starttag(node, "span", "", **attributes))


@html.closes(Swapper)
def depart_swapper(self: HTMLTranslator, node: Swapper) -> None:
    """Close the span, if one is open.

    :param self: The HTML translator, whose body this appends to.
    :param node: The swapping words.
    """
    if _moves(node):
        self.body.append("</span>")


@html.opens(glyph, elsewhere="skip")
def visit_glyph(self: HTMLTranslator, node: glyph) -> None:
    """Open the span with the icon.

    :param self: The HTML translator, whose body this appends to.
    :param node: The icon.
    """
    attributes: dict[str, t.Any] = {"aria-hidden": "true"}
    self.body.append(self.starttag(node, "span", "", **attributes))


html.closes(glyph, "</span>")


@html.closes(Ink)
def depart(self: HTMLTranslator, node: Ink) -> None:
    """Close the span, if one is open.

    :param self: The HTML translator, whose body this appends to.
    :param node: The inked text.
    """
    if _moves(node):
        self.body.append("</span>")


def _split(text: str, what: str) -> tuple[str, str | None]:
    """Split the text of a role into its label and the value in angles.

    :param text: The text in the role, with its escapes. The value is a
        last `<...>` at the start of the text or after a space, as
        docutils reads `text <target>`. Thus `x < 5` and `List<int>`
        are labels, and an escaped angle is not an angle.
    :param what: What the value is, as `a colour`.
    :return: The label and the value between `<` and `>`, without their
        escapes, or `None` when there is no value.
    :raises ValueError: When a value is not closed, or is empty.
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
    """Find the line of a role.

    :param inliner: The docutils inliner that called the role.
    :param rawtext: All of the role, with its markup.
    :param lineno: The line where the paragraph of the role starts.
        docutils gives this line, so a role further down is found in
        the source from there.
    :return: The line, or `lineno` when the source cannot be read.
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
    """Report a wrong role, and give docutils a problematic node.

    :param inliner: The docutils inliner that called the role.
    :param rawtext: All of the role, with its markup.
    :param lineno: The line where the paragraph of the role starts.
    :param message: What is wrong with the role.
    :return: The problematic node and the message, as docutils expects
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

    :param value: The text after the `?`, with `&` between the
        settings.
    :return: The name and the value of each setting, empty for a bare
        name.
    :raises ValueError: When a setting occurs two times.
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
    """Check the colour that a role names, and write it for CSS.

    :param config: The Sphinx configuration.
    :param value: A colour, or the name of a colour.
    :return: The colour: `hsl(...)` for a name that Kaamiki or the site
        gave, and `#abc` for a hex colour.
    :raises ValueError: When it is not one of these.
    """
    names = values(config).roles.colours
    value = checks.colour(value, (*TONES, *names))
    if value in names:
        value = names[value]
    elif value in PALETTE:
        value = PALETTE[value]
    return value if value.startswith("#") else f"hsl({value})"


def _decimal(given: str | None, name: str, site: float) -> float:
    """Read a width or a wobble after a `?`, or the value of the site.

    :param given: The text, or `None` for the value of the site.
    :param name: `width` or `wobble`.
    :param site: The value of the site.
    :return: The number.
    :raises ValueError: When it is not a number in its range.
    """
    low, high = BOUNDS[f"underline_{name}"]
    if given is None:
        return site
    try:
        return checks.number(low, high)(given)
    except ValueError as error:
        raise ValueError(f"{name} {error}") from error


def _short(number: int) -> str:
    """Write a number with k, m or b, to one decimal, with halves up.

    :param number: The number to write.
    :return: The short number, or the number as written when it is less
        than a thousand. A number goes to the next unit only when it
        rounds to a thousand of its unit, so 950000 is `950k` and
        999950 is `1m`.
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
    """Draw two wobbly strokes that look like a hand-drawn underline.

    :param colour: The colour of the stroke, already checked.
    :param seed: The source of the wobble, so that the same underline
        in the same place is the same in each build.
    :param width: The thickness of the stroke.
    :param wobble: How much the stroke moves, `0` for straight.
    :return: The left-to-right and the right-to-left SVG.
    """
    uniform = Random(sha256(seed.encode()).digest()).uniform
    segments = 7
    step = 500 / segments

    def stroke(start: float, stop: float) -> str:
        """Draw a wobbly path between two heights.

        :param start: The height where the stroke starts.
        :param stop: The height where the stroke stops.
        :return: The path.
        """
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
    """Say whether the role can write a CSS declaration.

    :param each: One declaration, as `color: red`.
    :return: `True` when it only styles text: a property of `TEXT`, no
        `url()`, and a `font-size` that stays readable.
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
    """Read the CSS that a custom role presets.

    :param argument: The declarations as written.
    :return: The declarations, joined, with `;` at the end.
    :raises ValueError: For a style of more than 200 characters, or a
        declaration that does not style text.
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


@role(style=_style)
def stylise(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: states.Inliner,
    options: dict[str, t.Any],
    content: list[t.Any],
) -> Reply:
    """Put CSS on some text.

    :param name: The name of the role, as written (unused).
    :param rawtext: All of the role, with its markup.
    :param text: The text in the role, as `label <css>`, or only
        `label` when the role presets `style`. Only properties that
        style text are permitted, as `color`, `font-size` to 4rem and
        `text-decoration`.
    :param lineno: The line where the paragraph of the role starts, for
        the error messages.
    :param inliner: The docutils inliner that called the role.
    :param options: The classes and the `style` of a custom role.
    :param content: The content of the role (unused).
    :return: The styled text, and the error messages when the text has
        no `<` and no `style` is preset.
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
        Ink(
            rawtext,
            element,
            classes=_classes(options),
            style="; ".join(found) + ";",
        )
    ], []


@role(subject=functools.partial(checks.text, maximum=150))
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

    :param name: The name of the role, as written (unused).
    :param rawtext: All of the role, with its markup.
    :param text: The text in the role, as `label <address>`, or only
        the address, with or without angles. The address can have
        `?subject=`. Else the subject is the preset `subject`, or the
        title of the page after the page is read.
    :param lineno: The line where the paragraph of the role starts, for
        the error messages.
    :param inliner: The docutils inliner that called the role.
    :param options: The classes and the `subject` of a custom role.
    :param content: The content of the role (unused).
    :return: One `reference` node, and the error messages when the
        address is wrong or asks for more than a subject.
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


@role(colour=checks.text)
def sharpie(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: states.Inliner,
    options: dict[str, t.Any],
    content: list[t.Any],
) -> Reply:
    """Put a highlighter on some text.

    :param name: The name of the role, as written (unused).
    :param rawtext: All of the role, with its markup.
    :param text: The text in the role, as `label` or `label <colour>`.
        The colour is a colour or one of `kaamiki.conf.roles.colours`.
        Else it is the preset `colour`, or
        `kaamiki.conf.roles.sharpie_colour`, which is yellow.
    :param lineno: The line where the paragraph of the role starts, for
        the error messages.
    :param inliner: The docutils inliner that called the role.
    :param options: The classes and the `colour` of a custom role.
    :param content: The content of the role (unused).
    :return: The highlighted text, and the error messages when the
        colour looks like markup.
    """
    del name, content
    config = inliner.document.settings.env.config
    preset = options.get("colour") or values(config).roles.sharpie_colour
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
    return [Ink(rawtext, element, classes=classes, style=style)], []


@role(
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
    """Draw a pencil underline below some text.

    :param name: The name of the role, as written (unused).
    :param rawtext: All of the role, with its markup.
    :param text: The text in the role, as `label`, `label <colour>` or
        `label <colour?width=3&wobble=0>`. The width is from 0.5 to 4,
        and the wobble is from 0 (straight) to 2. The defaults are the
        presets of a custom role, else
        `kaamiki.conf.roles.underline_colour`, `underline_width` and
        `underline_wobble`: orange, 2.5 and 1.
    :param lineno: The line where the paragraph of the role starts, for
        the error messages.
    :param inliner: The docutils inliner that called the role.
    :param options: The classes, `colour`, `width` and `wobble` of a
        custom role.
    :param content: The content of the role (unused).
    :return: The underlined text, and the error messages when the
        colour looks like markup, or the width or the wobble is wrong.
        A `#` and a `%` in the SVG are percent-encoded, as a data URI
        needs (RFC 2397).
    """
    del name, content
    config = inliner.document.settings.env.config
    preset = options.get("colour") or values(config).roles.underline_colour
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
            options.get("width", values(config).roles.underline_width),
        )
        wobble = _decimal(
            given.pop("wobble", None),
            "wobble",
            options.get("wobble", values(config).roles.underline_wobble),
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
    ltr, rtl = (
        quote(_, safe="/:=,.' <>-")
        for _ in _underline_svg(colour, seed, width, wobble)
    )
    style = (
        f'--km-underline-forward: url("data:image/svg+xml,{ltr}");'
        f' --km-underline-return: url("data:image/svg+xml,{rtl}");'
    )
    classes = ["km-pencil", *_classes(options)]
    return [Ink(rawtext, element, classes=classes, style=style)], []


def _duration(argument: str | None) -> float:
    """Read how long a ticker counts, in seconds.

    :param argument: The duration as written, as `1s` or `500ms`.
    :return: The seconds.
    :raises ValueError: When it is not a duration, or not in the range
        of a ticker.
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


@role(short=rst.directives.flag, duration=_duration)
def ticker(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: states.Inliner,
    options: dict[str, t.Any],
    content: list[t.Any],
) -> Reply:
    """Count a number up from zero.

    :param name: The name of the role, as written (unused).
    :param rawtext: All of the role, with its markup.
    :param text: The text in the role, as `number`, then optional
        `short` and `duration` after a `?`, in any sequence. `short`
        writes the number with k, m or b. The duration is in `s` or
        `ms`, from 0.1s to 5s, and the default is the preset or 2s. The
        count starts when the number scrolls into view.
    :param lineno: The line where the paragraph of the role starts, for
        the error messages.
    :param inliner: The docutils inliner that called the role.
    :param options: The classes, `short` and `duration` of a custom
        role.
    :param content: The content of the role (unused).
    :return: The number, and the error messages when it is not a whole
        number or a setting is wrong.
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
    seconds = options.get("duration")
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
    style = (
        f"--km-ticker-duration: {round(seconds * 1000)}ms;"
        if seconds is not None
        else ""
    )
    classes = ["km-ticker", *_classes(options)]
    return [Ink(rawtext, label, classes=classes, style=style)], []


def _turns(
    role: str,
    noun: str,
    limit: int,
    classes: list[str],
    rawtext: str,
    text: str,
    lineno: int,
    inliner: states.Inliner,
) -> Reply:
    """Read the parts of `:swap:` or `:sweep:`.

    :param role: The name of the role, for the messages.
    :param noun: What the parts are, for the messages.
    :param limit: The maximum characters of a part, counted as code
        points.
    :param classes: The classes of the text.
    :param rawtext: All of the role, with its markup.
    :param text: The text in the role.
    :param lineno: The line where the paragraph of the role starts, for
        the error messages.
    :param inliner: The docutils inliner that called the role.
    :return: The first part, and the error messages when there are
        fewer than two parts or a part is empty, too long or has a `|`.
    """
    words = [tidy(unescape(_)) for _ in BAR.split(text)]
    if len(words) < 2 or not all(words):
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"{role}: expected two or more {noun} split by |, got"
            f" {unescape(text)!r}",
        )
    barred = next((_ for _ in words if "|" in _), None)
    if barred is not None:
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"{role}: expected {noun} without |, got {barred!r}",
        )
    longest = max(words, key=len)
    if len(longest) > limit:
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"{role}: expected {noun} up to {limit} characters, got"
            f" {longest!r} with {len(longest)}",
        )
    attributes = {
        "classes": classes,
        "words": "|".join(words),
        "support_smartquotes": False,
    }
    return [Swapper(rawtext, words[0], **attributes)], []


@role()
def swap(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: states.Inliner,
    options: dict[str, t.Any],
    content: list[t.Any],
) -> Reply:
    """Change a word to the next word, again and again.

    :param name: The name of the role, as written (unused).
    :param rawtext: All of the role, with its markup.
    :param text: The words, with `|` between them, each with a maximum
        of 45 code points. The page, its search and a reader without
        scripts get the first word. On screen, the other words replace
        it one by one, in the font, size and colour of the text around
        them, and each letter rolls to the new letter from the left. In
        the navbar, the sidebar, the breadcrumbs, a toctree or a link,
        the first word stays as text. The words keep their quotes.
    :param lineno: The line where the paragraph of the role starts, for
        the error messages.
    :param inliner: The docutils inliner that called the role.
    :param options: The classes of a custom role.
    :param content: The content of the role (unused).
    :return: The first word, and the error messages when there are
        fewer than two words or a word is empty, too long or has a `|`.
    """
    del name, content
    classes = ["km-swap", *_classes(options)]
    return _turns(
        "swap",
        "words",
        SWAP_LENGTH,
        classes,
        rawtext,
        text,
        lineno,
        inliner,
    )


@role()
def sweep(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: states.Inliner,
    options: dict[str, t.Any],
    content: list[t.Any],
) -> Reply:
    """Wipe a title or a word out and the next one in, again and again.

    :param name: The name of the role, as written (unused).
    :param rawtext: All of the role, with its markup.
    :param text: The phrases, with `|` between them, each a full title
        or a word with a maximum of 120 code points. It is as `swap`,
        but a light moves across the text, and the old phrase fades out
        behind it as the new one comes in. The page, its search and a
        reader without scripts get the first phrase. In the navbar, the
        sidebar, the breadcrumbs, a toctree or a link, the first phrase
        stays as text. The phrases keep their quotes.
    :param lineno: The line where the paragraph of the role starts, for
        the error messages.
    :param inliner: The docutils inliner that called the role.
    :param options: The classes of a custom role.
    :param content: The content of the role (unused).
    :return: The first phrase, and the error messages when there are
        fewer than two phrases or a phrase is empty, too long or has a
        `|`.
    """
    del name, content
    classes = ["km-swap", "km-sweep", *_classes(options)]
    return _turns(
        "sweep",
        "phrases",
        SWEEP_LENGTH,
        classes,
        rawtext,
        text,
        lineno,
        inliner,
    )


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

    :param style: The Font Awesome style class, bound by `icon` and
        `FaIcon.roles` at import, or `None` for
        `kaamiki.conf.icons.style`. The roles are `fa-icon:brands`,
        `fa-icon:light`, `fa-icon:regular`, `fa-icon:solid`,
        `fa-icon:thin`, `fa-icon:duotone` and `fa-icon`.
    :param name: The name of the role, as written (unused).
    :param rawtext: All of the role, with its markup.
    :param text: The text in the role: the name, then classes, with a
        space between each.
    :param lineno: The line where the paragraph of the role starts, for
        the error messages.
    :param inliner: The docutils inliner that called the role.
    :param options: The classes of a custom role.
    :param content: The content of the role (unused).
    :return: The icon, and the error messages when the name or a class
        is not part of an icon.
    """
    del name, content
    config = inliner.document.settings.env.config
    text = unescape(text)
    if not text.split():
        return _reject(
            inliner,
            rawtext,
            lineno,
            "fa-icon: expected an icon name, got none",
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
                "fa-icon: expected a Font Awesome size or animation, or a"
                f" class like km-tone--red, got {found!r}",
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
    """Write a keyboard shortcut as a system prints it.

    :param system: The system, bound by `Kbd.roles` at import. The
        roles are `kbd:mac`, `kbd:windows` and `kbd:linux`.
    :param name: The name of the role, as written.
    :param rawtext: All of the role, with its markup.
    :param text: The keys, joined by `-`, `+` or `^`, as for the `kbd`
        of Sphinx.
    :param lineno: The line where the paragraph of the role starts, for
        the error messages.
    :param inliner: The docutils inliner that called the role.
    :param options: The classes of a custom role.
    :param content: The content of the role (unused).
    :return: The keys, and no error messages.
    """
    del content
    classes = [*SYSTEMS[system], *_classes(options)]
    options = {**options, "classes": classes}
    return Keyboard()(name, rawtext, text, lineno, inliner, options)


icon = KaamikiRole(functools.partial(_icon, None), name="fa-icon")


class CustomRole(misc.Role):
    """The `role` directive, which checks the preset colour."""

    def run(self) -> Sequence[nodes.Node]:
        """Make the role and check the colour that it presets.

        :return: The messages that docutils gives. docutils checks the
            other presets when it reads them. A colour is only a name
            until `kaamiki.conf.roles.colours` is known, so this checks
            it.
        :raises rst.DirectiveError: When Kaamiki does not know the
            colour.
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


@on("doctree-read")
def subjects(app: Sphinx, doctree: nodes.document) -> None:
    """Give an email link without a subject the title of the page.

    :param app: The Sphinx application instance (unused).
    :param doctree: The page, just read. The title comes from the tree
        after the page is read.
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


class Quiet(Domain):
    """A domain without data, so a parallel build merges nothing."""

    def role(self, name: str) -> KaamikiRole | None:
        """Give docutils a role with its full name and options.

        :param name: The name of the role in the domain.
        :return: The role, or `None` when the domain has no role with
            that name. The roles are `KaamikiRole` roles, so a custom
            role can use each of them as a base.
        """
        found = self.roles.get(name)
        if found is None:
            return None
        full = f"{self.name}:{name}"
        return KaamikiRole(
            lambda _, *rest: found(full, *rest),
            getattr(found, "options", {}),
        )

    def merge_domaindata(
        self, docnames: AbstractSet[str], otherdata: dict[str, t.Any]
    ) -> None:
        """Take nothing from the other processes.

        :param docnames: The pages that they read.
        :param otherdata: What they kept, which is nothing.
        """


class FaIcon(Quiet):
    """The `fa-icon:` roles, one for each Font Awesome style."""

    name: t.ClassVar[str] = "fa-icon"
    label: t.ClassVar[str] = "Font Awesome"
    roles = {  # noqa: RUF012
        key: KaamikiRole(functools.partial(_icon, style))
        for key, style in STYLE_CLASSES.items()
    }


class Kbd(Quiet):
    """The `kbd:` roles, one for each system."""

    name: t.ClassVar[str] = "kbd"
    label: t.ClassVar[str] = "Keyboard"
    roles = {  # noqa: RUF012
        key: KaamikiRole(functools.partial(_keys, key)) for key in SYSTEMS
    }
