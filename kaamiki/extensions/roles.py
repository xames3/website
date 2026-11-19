"""\
Custom Roles
============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February 2025
Last updated on: 19 November 2026

The custom inline roles of Kaamiki.
"""

from __future__ import annotations

import copy
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
from sphinx.util.docutils import SphinxRole

from kaamiki.extensions.utils import Option
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
    from sphinx.util.typing import RoleFunction
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
ROLL_LENGTH: t.Final[int] = 45
SWEEP_LENGTH: t.Final[int] = 120
STYLE_CLASSES: t.Final[dict[str, str]] = {
    "brands": "fa-brands",
    **{
        key: f"fa-{key}"
        for key in [*checks.FAMILY_STYLES["classic"], *checks.FAMILY_STYLES]
        if key != "classic"
    },
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


class KaamikiRole(SphinxRole):
    """The base of each Kaamiki role."""

    registry: t.ClassVar[dict[str, KaamikiRole]] = {}
    role: t.ClassVar[str]
    spec: t.ClassVar[dict[str, Callable[[str | None], t.Any]]]
    base_classes: t.ClassVar[tuple[str, ...]] = ()

    def __init_subclass__(
        cls,
        *,
        name: str = "",
        alone: bool = True,
        abstract: bool = False,
        **kwargs: t.Any,
    ) -> None:
        """Record the role and collect the options that it presets.

        :param name: The name of the role in rST and in its messages.
            The default is the name of the class in lower case.
        :param alone: Whether the role is recorded in `registry`. A
            role that only a domain gives is not.
        :param abstract: Whether the class is only a base for other
            roles. Then it is not recorded or checked.
        :param kwargs: What the parent class takes.
        :raises TypeError: When the docstring does not list each option
            that the role presets, or when another role has the name.
        """
        super().__init_subclass__(**kwargs)
        if abstract:
            return
        cls.role = name or cls.__name__.lower()
        cls.spec = {
            "class": checks.classes,
            **{key: each.check for key, each in Option.of(cls).items()},
        }
        Option.documented(cls, cls.spec)
        if not alone:
            return
        if other := KaamikiRole.registry.get(cls.role):
            raise TypeError(
                f"{cls.__qualname__}: expected a new role name, got"
                f" {cls.role!r} of {type(other).__qualname__}"
            )
        KaamikiRole.registry[cls.role] = cls()

    def __init__(self) -> None:
        """Give docutils the options that `.. role::` can preset."""
        self.options = dict(self.spec)

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
        """Use a copy of the role on some text.

        :param name: The name of the role, as written.
        :param rawtext: All of the role, with its markup.
        :param text: The text in the role, with its escapes.
        :param lineno: The line where the paragraph of the role starts,
            for the error messages.
        :param inliner: The docutils inliner that called the role.
        :param options: The classes and presets of a custom role. Only
            the copy gets them, because docutils reads the `options` of
            the role itself to know what `.. role::` can preset.
        :param content: The content of the role.
        :return: The nodes and the error messages. A `ValueError` from
            `run` becomes a problematic node, with the name of the role
            before the message.
        """
        used = copy.copy(self)
        used.name, used.rawtext, used.text = name, rawtext, text
        used.lineno, used.inliner, used.content = lineno, inliner, content
        used.options = options or {}
        try:
            return used.run()
        except ValueError as error:
            return used.reject(f"{self.role}: {error}")

    @property
    def said(self) -> str:
        """The text in the role, without its escapes."""
        return unescape(self.text)

    @property
    def classes(self) -> list[str]:
        """The classes of the role, then those of `.. role::`."""
        return [*self.base_classes, *self.options.get("classes", [])]

    @property
    def line(self) -> int:
        """The line of the role, else `lineno` when it is not found."""
        try:
            source, start = self.get_source_info()
        except AttributeError:
            return self.lineno
        if source is None or start is None:
            return self.lineno
        try:
            with open(source, encoding="utf-8") as fd:
                lines = fd.read().splitlines()[start - 1 :]
        except OSError, ValueError:
            return self.lineno
        first = (self.rawtext.splitlines() or [""])[0]
        found = (n for n, _ in enumerate(lines) if first in _)
        return self.lineno + next(found, 0)

    def run(self) -> Reply:
        """Make the nodes of the role.

        :return: The nodes and the messages.
        :raises NotImplementedError: Always. Each role writes its own.
        """
        raise NotImplementedError

    def fail(self, message: str) -> t.NoReturn:
        """Stop the role with a message.

        :param message: The message, without the name of the role.
        :raises ValueError: Always. The call of the role reports it.
        """
        raise ValueError(message)

    def reject(self, message: str) -> Reply:
        """Report a wrong role, and give docutils a problematic node.

        :param message: What is wrong with the role.
        :return: The problematic node and the message, as docutils
            expects them.
        """
        msg = self.inliner.reporter.error(
            message,
            nodes.literal_block(self.rawtext, self.rawtext),
            line=self.line,
        )
        return [self.inliner.problematic(self.rawtext, self.rawtext, msg)], [
            msg
        ]

    def split(self, what: str) -> tuple[str, str | None]:
        """Split the text into its label and the value in angles.

        :param what: What the value is, as `a colour`. The value is a
            last `<...>` at the start of the text or after a space, as
            docutils reads `text <target>`. Thus `x < 5` and
            `List<int>` are labels, and an escaped angle is not an
            angle.
        :return: The label and the value between `<` and `>`, without
            their escapes, or `None` when there is no value.
        :raises ValueError: When a value is not closed, or is empty.
        """
        found = VALUE.search(self.text)
        if found is None:
            if OPENED.search(self.text):
                self.fail(
                    f"expected {what} between < and >, got {self.said!r}"
                )
            return self.said.strip(), None
        value = unescape(found[1]).strip()
        if not value:
            self.fail(f"expected {what} between < and >, got none")
        return unescape(self.text[: found.start()]).strip(), value


class Ink(nodes.inline):
    """Text with a style, a sharpie or a pencil underline."""


class Turning(Ink):
    """The first of the words that show one after another."""


def steady(
    directive: Directive,
    found: Iterable[nodes.Node] | nodes.Node,
    part: str,
    why: str,
) -> None:
    """Refuse `:roll:` and `:sweep:` in a text that must not move.

    :param directive: The directive that has the text.
    :param found: The parsed text or its nodes.
    :param part: What the text is, as `a title`.
    :param why: Why it cannot move, for the message.
    :raises rst.DirectiveError: When the text has turning words.
    """
    for each in [found] if isinstance(found, nodes.Node) else found:
        moving = next(each.findall(Turning), None)
        if moving is not None:
            role = "sweep" if "km-sweep" in moving["classes"] else "roll"
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

    :param node: The inked text or the turning words.
    :return: `True` for text in the page itself. The text is plain in a
        link (a toctree, a `:ref:` or a `:doc:`) and in a title that
        shows alone, as in the breadcrumbs, the tab of the page and the
        previous and next pages. There, turning words show only the
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


@html.opens(Turning)
def visit_turning(self: HTMLTranslator, node: Turning) -> None:
    """Open the span for the turning words, if they turn here.

    :param self: The HTML translator, whose body this appends to.
    :param node: The turning words.
    """
    if _moves(node):
        attributes: dict[str, t.Any] = {"data-km-words": node["words"]}
        self.body.append(self.starttag(node, "span", "", **attributes))


@html.closes(Turning)
def depart_turning(self: HTMLTranslator, node: Turning) -> None:
    """Close the span, if one is open.

    :param self: The HTML translator, whose body this appends to.
    :param node: The turning words.
    """
    if _moves(node):
        self.body.append("</span>")


@html.opens(glyph)
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


class Stylise(KaamikiRole):
    """The `stylise` role, which puts CSS on some text.

    Text::

        `label <css>`, or only `label` when the role presets `style`.
        Only properties that style text are permitted, as `color`,
        `font-size` to 4rem and `text-decoration`.

    Options::

        - `style`: The CSS for text without `<css>`, up to 200
          characters.
        - `class`: More classes for the text.
    """

    style = Option(_style)

    def run(self) -> Reply:
        """Put CSS on the text.

        :return: The styled text, and no error messages.
        :raises ValueError: When the text has no `<` and no `style` is
            preset, or a declaration does not style text.
        """
        element, style = self.split("a style")
        if style is None:
            style = self.style
        if style is None:
            self.fail(
                f"expected text like `words <color: red;>`, got {self.said!r}"
            )
        found = [_.strip() for _ in style.split(";") if _.strip()]
        if not element or not found or len(style) > 200:
            self.fail(
                "expected text like `words <color: red;>` and a style up to"
                f" 200 characters, got {self.said!r}"
            )
        for each in found:
            if not _declared(each):
                self.fail(
                    f"expected a text declaration like color: red, got"
                    f" {each!r}"
                )
        style = "; ".join(found) + ";"
        return [
            Ink(self.rawtext, element, classes=self.classes, style=style)
        ], []


class Email(KaamikiRole):
    """The `email` role, which writes a `mailto` link.

    Text::

        `label <address>`, or only the address, with or without
        angles. The address can have `?subject=`. Else the subject is
        the preset `subject`, or the title of the page after the page
        is read.

    Options::

        - `subject`: The subject of an address without one, up to 150
          characters.
        - `class`: More classes for the link.
    """

    subject = Option(functools.partial(checks.text, maximum=150), default="")

    def run(self) -> Reply:
        """Write the `mailto` link.

        :return: One `reference` node, and no error messages.
        :raises ValueError: When the address is wrong or asks for more
            than a subject.
        """
        alt, rest = self.split("an address")
        if rest is None:
            alt, rest = "", alt
        href, asked, subject = rest.partition("?")
        href = href.strip()
        if not checks.EMAIL.fullmatch(href):
            self.fail(f"expected an email address, got {href!r}")
        if asked:
            key, equals, subject = subject.partition("=")
            subject = tidy(subject)
            if re.search(r"&[A-Za-z]+=", subject):
                self.fail("expected only subject=text, got more after it")
            if key.strip().lower() != "subject" or (not equals and subject):
                self.fail(f"expected subject=text, got {key.strip()!r}")
            if not subject:
                self.fail("expected some text after subject=, got none")
            if len(subject) > 150:
                self.fail(
                    "expected a subject up to 150 characters, got a longer one"
                )
        subject = subject or tidy(self.subject)
        refuri = f"mailto:{href}"
        if subject:
            refuri += f"?subject={quote(unquote(subject))}"
        link = nodes.reference(
            self.rawtext, alt or href, refuri=refuri, classes=self.classes
        )
        if not subject:
            link["titled"] = True
        return [link], []


class Sharpie(KaamikiRole):
    """The `sharpie` role, which puts a highlighter on some text.

    Text::

        `label` or `label <colour>`. The colour is a colour or one of
        `kaamiki.conf.roles.colours`.

    Options::

        - `colour`: The colour of text without `<colour>`. The default
          is `kaamiki.conf.roles.sharpie_colour`, which is yellow.
        - `class`: More classes for the text.
    """

    base_classes = ("km-sharpie",)
    colour = Option(setting="sharpie_colour")

    def run(self) -> Reply:
        """Highlight the text.

        :return: The highlighted text, and no error messages.
        :raises ValueError: When the text is empty or the colour looks
            like markup.
        """
        element, colour = self.split("a colour")
        colour = _colour(self.config, colour or self.colour)
        if not element:
            self.fail(f"expected some text, got none in {self.said!r}")
        style = f"--km-sharpie-colour: {colour};"
        return [
            Ink(self.rawtext, element, classes=self.classes, style=style)
        ], []


class Underline(KaamikiRole):
    """The `underline` role, which draws a pencil line below some text.

    Text::

        `label`, `label <colour>` or `label <colour?width=3&wobble=0>`.
        The width is from 0.5 to 4, and the wobble is from 0
        (straight) to 2.

    Options::

        - `colour`: The colour of the line. The default is
          `kaamiki.conf.roles.underline_colour`, which is orange.
        - `width`: The thickness of the line. The default is
          `kaamiki.conf.roles.underline_width`, which is 2.5.
        - `wobble`: How much the line moves. The default is
          `kaamiki.conf.roles.underline_wobble`, which is 1.
        - `class`: More classes for the text.
    """

    base_classes = ("km-pencil",)
    colour = Option(setting="underline_colour")
    width = Option(setting="underline_width")
    wobble = Option(setting="underline_wobble")

    def run(self) -> Reply:
        """Underline the text.

        :return: The underlined text, and no error messages. A `#` and
            a `%` in the SVG are percent-encoded, as a data URI needs
            (RFC 2397).
        :raises ValueError: When the text is empty, the colour looks
            like markup, or the width or the wobble is wrong.
        """
        element, rest = self.split("a colour or settings")
        colour, asked, query = (rest or "").partition("?")
        if asked and not query.strip():
            self.fail("expected width or wobble after ?, got none")
        given = _query(query)
        colour = _colour(self.config, colour.strip() or self.colour)
        width = _decimal(given.pop("width", None), "width", self.width)
        wobble = _decimal(given.pop("wobble", None), "wobble", self.wobble)
        if given or not element:
            self.fail(
                f"expected some text and width or wobble, got"
                f" {', '.join(given) or self.said!r}"
            )
        seed = f"{self.env.docname}:{self.lineno}:{self.rawtext}"
        ltr, rtl = (
            quote(_, safe="/:=,.' <>-")
            for _ in _underline_svg(colour, seed, width, wobble)
        )
        style = (
            f'--km-underline-forward: url("data:image/svg+xml,{ltr}");'
            f' --km-underline-return: url("data:image/svg+xml,{rtl}");'
        )
        return [
            Ink(self.rawtext, element, classes=self.classes, style=style)
        ], []


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


class Ticker(KaamikiRole):
    """The `ticker` role, which counts a number up from zero.

    Text::

        `number`, then optional `short` and `duration` after a `?`, in
        any sequence. The count starts when the number scrolls into
        view.

    Options::

        - `short`: Write the number with k, m or b.
        - `duration`: How long the count takes, in `s` or `ms`, from
          0.1s to 5s. The default is 2s.
        - `class`: More classes for the number.
    """

    base_classes = ("km-ticker",)
    short = Option(rst.directives.flag)
    duration = Option(_duration)

    def run(self) -> Reply:
        """Count the number.

        :return: The number, and no error messages.
        :raises ValueError: When it is not a whole number or a setting
            is wrong.
        """
        number, asked, rest = self.said.partition("?")
        count = checks.integer(*map(int, BOUNDS["ticker"]))(number.strip())
        if asked and not rest.strip():
            self.fail("expected short or duration after ?, got none")
        given = _query(rest)
        if given.get("short"):
            self.fail(f"expected short with no value, got {given['short']!r}")
        short = given.pop("short", None) is not None or self.short
        seconds = self.duration
        if "duration" in given:
            seconds = _duration(given.pop("duration"))
        if given:
            self.fail(f"expected short or duration, got {', '.join(given)}")
        label = _short(count) if short else str(count)
        style = (
            f"--km-motion-ticker: {round(seconds * 1000)}ms;"
            if seconds is not None
            else ""
        )
        return [
            Ink(self.rawtext, label, classes=self.classes, style=style)
        ], []


class Turns(KaamikiRole, abstract=True):
    """The base of `roll` and `sweep`, whose parts take turns."""

    noun: t.ClassVar[str]
    limit: t.ClassVar[int]

    def run(self) -> Reply:
        """Read the parts, split by `|`.

        :return: The first part, and no error messages.
        :raises ValueError: When there are fewer than two parts, or a
            part is empty, longer than `limit` code points or has a
            `|`.
        """
        words = [tidy(unescape(_)) for _ in BAR.split(self.text)]
        if len(words) < 2 or not all(words):
            self.fail(
                f"expected two or more {self.noun} split by |, got"
                f" {self.said!r}"
            )
        barred = next((_ for _ in words if "|" in _), None)
        if barred is not None:
            self.fail(f"expected {self.noun} without |, got {barred!r}")
        longest = max(words, key=len)
        if len(longest) > self.limit:
            self.fail(
                f"expected {self.noun} up to {self.limit} characters, got"
                f" {longest!r} with {len(longest)}"
            )
        attributes = {
            "classes": self.classes,
            "words": "|".join(words),
            "support_smartquotes": False,
        }
        return [Turning(self.rawtext, words[0], **attributes)], []


class Roll(Turns):
    """The `roll` role, which shows its words one after another.

    Text::

        The words, with `|` between them, each with a maximum of 45
        code points. The page, its search and a reader without scripts
        get the first word. On screen, the other words replace it one
        by one, in the font, size and colour of the text around them,
        and each letter rolls to the new letter from the left. In the
        navbar, the sidebar, the breadcrumbs, a toctree or a link, the
        first word stays as text. The words keep their quotes.

    Options::

        - `class`: More classes for the words.
    """

    base_classes = ("km-roll",)
    noun = "words"
    limit = ROLL_LENGTH


class Sweep(Turns):
    """The `sweep` role, which wipes its phrases in one after another.

    Text::

        The phrases, with `|` between them, each a full title or a word
        with a maximum of 120 code points. It is as `roll`, but a light
        moves across the text, and the old phrase fades out behind it
        as the new one comes in. The page, its search and a reader
        without scripts get the first phrase. In the navbar, the
        sidebar, the breadcrumbs, a toctree or a link, the first phrase
        stays as text. The phrases keep their quotes.

    Options::

        - `class`: More classes for the phrases.
    """

    base_classes = ("km-sweep",)
    noun = "phrases"
    limit = SWEEP_LENGTH


class Icon(KaamikiRole, name="fa-icon"):
    """The `fa-icon` role, which draws a Font Awesome icon.

    Text::

        The name, then classes, with a space between each. The classes
        are Font Awesome sizes and animations, or classes like
        `km-tone--red`.

    Options::

        - `class`: More classes for the icon.
    """

    def __init__(self, style: str | None = None) -> None:
        """Make the role for one Font Awesome style.

        :param style: The Font Awesome style or family class, or `None`
            for `kaamiki.conf.icons.style`. `FaIcon` makes one role for
            each of `STYLE_CLASSES`: `fa-icon:solid` for a style, and
            `fa-icon:jelly` for a family, which draws in its own style.
            For `fa-icon:sharp:light`, it is the family and the style,
            as `fa-sharp fa-light`.
        """
        super().__init__()
        self.style = style

    def run(self) -> Reply:
        """Draw the icon.

        :return: The icon, and no error messages.
        :raises ValueError: When the name or a class is not part of an
            icon, or the family does not have the style.
        """
        family, _, style = (self.style or "").partition(" ")
        if style:
            checks.paired(family, style)
        if not self.said.split():
            self.fail("expected an icon name, got none")
        name, *classes = self.said.split()
        name = name.removeprefix("fa-")
        if not GLYPH.fullmatch(name):
            self.fail(f"expected a name like star, got {name!r}")
        for found in classes:
            if not checks.MODIFIERS.fullmatch(found):
                self.fail(
                    "expected a Font Awesome size or animation, or a class"
                    f" like km-tone--red, got {found!r}"
                )
        spec = " ".join(filter(None, [self.style, f"fa-{name}"]))
        drawn = Icons.of(self.config).classes(spec).split()
        classes = [*drawn, "km-glyph", *classes, *self.classes]
        return [glyph(self.rawtext, classes=classes)], []


class Keys(KaamikiRole, name="kbd", alone=False):
    """The `kbd:` roles, which write a shortcut as a system prints it.

    Text::

        The keys, joined by `-`, `+` or `^`, as for the `kbd` of
        Sphinx.

    Options::

        - `class`: More classes for the keys.
    """

    def __init__(self, system: str) -> None:
        """Make the role for one system.

        :param system: The system. `Kbd` makes the roles `kbd:mac`,
            `kbd:windows` and `kbd:linux`.
        """
        super().__init__()
        self.system = system

    def run(self) -> Reply:
        """Write the keys with the `kbd` role of Sphinx.

        :return: The keys, and no error messages.
        """
        classes = [*SYSTEMS[self.system], *self.classes]
        return Keyboard()(
            f"{self.role}:{self.system}",
            self.rawtext,
            self.text,
            self.lineno,
            self.inliner,
            {**self.options, "classes": classes},
        )


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

    def role(self, name: str) -> RoleFunction | None:
        """Give docutils a role with its full name and options.

        :param name: The name of the role in the domain.
        :return: The role, or `None` when the domain has no role with
            that name. The roles are `KaamikiRole` roles, so a custom
            role can use each of them as a base.
        """
        return self.roles.get(name)

    def merge_domaindata(
        self, docnames: AbstractSet[str], otherdata: dict[str, t.Any]
    ) -> None:
        """Take nothing from the other processes.

        :param docnames: The pages that they read.
        :param otherdata: What they kept, which is nothing.
        """


class FaIcon(Quiet):
    """The `fa-icon:` roles, one for each style or family of icons."""

    name: t.ClassVar[str] = "fa-icon"
    label: t.ClassVar[str] = "Font Awesome"
    roles = {  # noqa: RUF012
        key: Icon(style) for key, style in STYLE_CLASSES.items()
    }

    def role(self, name: str) -> RoleFunction | None:
        """Give docutils a role for a style, a family, or the two.

        :param name: The name of the role in the domain, as `solid`,
            `jelly` or `sharp:light`, with the family first.
        :return: The role, or `None` when Font Awesome has no such
            family or style. The family and the style are checked
            when the role is used.
        """
        family, _, style = name.partition(":")
        if not style:
            return super().role(name)
        if f"fa-{family}" in checks.FAMILIES and (
            f"fa-{style}" in checks.STYLES
        ):
            return Icon(f"fa-{family} fa-{style}")
        return None


class Kbd(Quiet):
    """The `kbd:` roles, one for each system."""

    name: t.ClassVar[str] = "kbd"
    label: t.ClassVar[str] = "Keyboard"
    roles = {key: Keys(key) for key in SYSTEMS}  # noqa: RUF012
