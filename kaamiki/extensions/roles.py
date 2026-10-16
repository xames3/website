"""\
Custom Roles
============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February 2025
Last updated on: 16 October 2026

Kaamiki's custom inline roles.
"""

import re
import typing as t
from hashlib import sha256
from random import Random
from urllib.parse import quote

import docutils.nodes as nodes

from kaamiki.extensions.utils import findall
from kaamiki.extensions.utils import setting

if t.TYPE_CHECKING:
    from sphinx.writers.html import HTMLTranslator

# A colour lands inside an attribute and in `underline`'s case inside
# an SVG nested in a data URI in that attribute. Nothing legitimate in
# there needs a quote or an angle bracket, so anything carrying one is
# an author mistake rather than a colour.
COLOUR: re.Pattern[str] = re.compile(r"^[#\w(),.%\s/-]+$")
WIDTHS: t.Final[tuple[float, float]] = (0.5, 4.0)
WOBBLES: t.Final[tuple[float, float]] = (0.0, 2.0)
SECONDS: t.Final[tuple[float, float]] = (0.1, 10.0)
DURATION: re.Pattern[str] = re.compile(r"^(\d+(?:\.\d+)?)(ms|s)$")
UNITS: t.Final[tuple[tuple[int, str], ...]] = (
    (10**9, "b"),
    (10**6, "m"),
    (10**3, "k"),
)
# NOTE(xames3): A hyphen can't sit in a function's name, so `setup`
# registers the icon roles from this, each with its Font Awesome style.
ICONS: t.Final[dict[str, str]] = {
    "fab-icon": "fa-brands",
    "fal-icon": "fa-light",
    "far-icon": "fa-regular",
    "fas-icon": "fa-solid",
}
GLYPH: re.Pattern[str] = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CLASS: re.Pattern[str] = re.compile(r"^[\w-]+$")


class ink(nodes.inline):
    """Text wearing a style, a sharpie or a pencil underline.

    It stays a text node, so the reading time, search index and page
    description see the words and not the markup.
    """


class glyph(nodes.inline):
    """A Font Awesome icon, an empty span the stylesheet draws into."""


def _visit(self: HTMLTranslator, node: ink) -> None:
    """Open the span that carries the style.

    :param self: The HTML translator, whose body this appends to.
    :param node: The inked text.
    """
    self.body.append(self.starttag(node, "span", "", style=node["style"]))


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


def _options(value: str | None) -> tuple[str, dict[str, str]]:
    """Split what sits in a role's angles into a colour and settings.

    :param value: What was between `<` and `>` or `None`.
    :return: The colour, empty when there's none, and the settings.
    :raises ValueError: When there's more than one colour.
    """
    colour = ""
    found: dict[str, str] = {}
    for part in (value or "").split(";"):
        part = part.strip()
        if not part:
            continue
        key, equals, number = part.partition("=")
        if equals:
            found[key.strip().lower()] = number.strip()
        elif colour:
            raise ValueError(f"{part!r} after the colour {colour!r}")
        else:
            colour = part
    return colour, found


def _colour(config: t.Any, value: str) -> str:
    """Look a colour up among the names the site gave colours.

    :param config: The Sphinx configuration.
    :param value: A colour or the name of one.
    :return: The colour the name stands for or the value as written.
    """
    names = {
        str(key).strip().lower(): str(colour).strip()
        for key, colour in setting(config, "role_colours").items()
    }
    return names.get(value.strip().lower(), value.strip())


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
    return [ink(rawtext, element, style=style)], []


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

    The subject is the page title unless the role names one after a
    pipe. Without a label the address is the label::

        Send me an :email:`email <xa@mes3.dev>`.
        Send me an :email:`email <xa@mes3.dev | Hello hello!!>`.

    :param role: The role name, as written (unused).
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role sits on, for error reporting.
    :param inliner: The docutils inliner that called this.
    :param options: Role options (unused).
    :param content: Role content (unused).
    :return: One `reference` node and the error messages if the text
        doesn't split on a `<`.
    """
    del role, options, content
    alt, rest = _split(text)
    if rest is None:
        return _reject(inliner, rawtext, lineno, f"Invalid email: {text!r}")
    href, _, subject = rest.partition("|")
    alt = alt or href.strip()
    if not subject.strip():
        subject = next(
            (_.astext() for _ in findall(inliner.document, nodes.title)), ""
        )
    refuri = f"mailto:{href.strip()}"
    if subject.strip():
        refuri += f"?subject={quote(subject.strip())}"
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
    color = _colour(config, color or str(setting(config, "sharpie_colour")))
    if not COLOUR.match(color):
        return _reject(inliner, rawtext, lineno, f"Invalid colour: {color!r}")
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
    the role names its own after the text, a semicolon between them::

        This is :underline:`notable` content.
        This is :underline:`notable <red>` content.
        This is :underline:`notable <red; width=3; wobble=0>` content.

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
    try:
        color, given = _options(rest)
    except ValueError as exc:
        return _reject(inliner, rawtext, lineno, f"Invalid underline: {exc}")
    color = _colour(config, color or str(setting(config, "underline_colour")))
    if not COLOUR.match(color):
        return _reject(inliner, rawtext, lineno, f"Invalid colour: {color!r}")
    width = float(given.pop("width", setting(config, "underline_width")))
    wobble = float(given.pop("wobble", setting(config, "underline_wobble")))
    if given:
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"Invalid underline setting: {', '.join(given)};"
            " it takes width and wobble",
        )
    for name, number, (low, high) in (
        ("width", width, WIDTHS),
        ("wobble", wobble, WOBBLES),
    ):
        if not low <= number <= high:
            return _reject(
                inliner,
                rawtext,
                lineno,
                f"Invalid underline {name}: use a number from {low:g}"
                f" to {high:g}",
            )
    seed = f"{inliner.document.settings.env.docname}:{lineno}:{rawtext}"
    # NOTE(xames3): A `#` has to be percent-encoded inside a data URI.
    # https://datatracker.ietf.org/doc/html/rfc2397
    ltr, rtl = (
        _.replace("#", "%23")
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

    The text reads `number`, then `short` and a duration after pipes,
    both optional and in either order. `short` wraps the number in k, m
    or b, a whole number shows without it. The duration is in `s` or
    `ms`, from 0.1s to 10s, 2s unless the role gives one. The count
    starts when the number scrolls into view::

        We've :ticker:`2025` stars.
        We've :ticker:`2025 | short` stars.
        We've :ticker:`2025 | short | 1s` stars.

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
    number, *given = (_.strip() for _ in text.split("|"))
    if not number.isascii() or not number.isdecimal():
        return _reject(inliner, rawtext, lineno, f"Invalid number: {number!r}")
    short = False
    seconds = 2.0
    seen: set[str] = set()
    for part in given:
        found = DURATION.match(part)
        kind = "short" if part == "short" else "duration" if found else ""
        if not kind or kind in seen:
            return _reject(
                inliner,
                rawtext,
                lineno,
                f"Invalid ticker setting: {part!r}; it takes short"
                " and a duration, once each",
            )
        seen.add(kind)
        if found:
            seconds = float(found[1]) / (1000 if found[2] == "ms" else 1)
        else:
            short = True
    low, high = SECONDS
    if not low <= seconds <= high:
        return _reject(
            inliner,
            rawtext,
            lineno,
            f"Invalid ticker duration: use a time from {low:g}s to {high:g}s",
        )
    label = _short(int(number)) if short else str(int(number))
    style = f"--km-ticker-duration: {round(seconds * 1000)}ms;"
    return [ink(rawtext, label, classes=["km-ticker"], style=style)], []


def _icon(
    style: str,
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
    The role names the style, `fab-icon` for brands, `fal-icon` for
    light, `far-icon` for regular and `fas-icon` for solid::

        Watch on :fab-icon:`youtube` or listen :far-icon:`headphones`.
        Show some :fas-icon:`heart km-red` love.

    :param style: The Font Awesome style class, bound by `setup`.
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
    name, *classes = text.split()
    if not GLYPH.match(name):
        return _reject(inliner, rawtext, lineno, f"Invalid icon: {name!r}")
    for found in classes:
        if not CLASS.match(found):
            return _reject(
                inliner, rawtext, lineno, f"Invalid icon class: {found!r}"
            )
    node = glyph(rawtext, classes=[style, f"fa-{name}", "km-glyph", *classes])
    return [node], []
