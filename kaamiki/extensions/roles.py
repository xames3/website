"""\
Custom Roles
============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February, 2025
Last updated on: 29 September, 2026

The theme's inline roles: `stylise`, `email`, `sharpie` and `underline`.
Every public function here is registered as a role of the same name,
so a helper in this module takes a leading underscore.
"""

from __future__ import annotations

import re
import typing as t
from hashlib import sha256
from random import Random
from urllib.parse import quote

import docutils.nodes as nodes

from kaamiki.extensions.utils import findall

if t.TYPE_CHECKING:
    from sphinx.writers.html import HTMLTranslator

# A colour lands inside an attribute and in `underline`'s case inside
# an SVG nested in a data URI in that attribute. Nothing legitimate in
# there needs a quote or an angle bracket, so anything carrying one is
# an author mistake rather than a colour.
COLOUR: re.Pattern[str] = re.compile(r"^[#\w(),.%\s/-]+$")


class ink(nodes.inline):
    """A run of text wearing a style, a sharpie or a pencil underline.

    The text stays a text node, so the reading time, the search index
    and a page's description see the words and not the markup drawn
    around them.
    """


def _visit(self: HTMLTranslator, node: ink) -> None:
    """Open the span that carries the style.

    :param self: The HTML translator, whose body this appends to.
    :param node: The inked text.
    """
    self.body.append(self.starttag(node, "span", "", style=node["style"]))


def _depart(self: HTMLTranslator, node: ink) -> None:
    """Close the span.

    :param self: The HTML translator, whose body this appends to.
    :param node: The inked text (unused).
    """
    self.body.append("</span>")


def _split(text: str) -> tuple[str, str | None]:
    """Split a role's text into its label and what sits in angles.

    :param text: What was written inside the role.
    :return: The label and the value between `<` and `>` or `None`
        when there is not one.
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
    :param message: What is wrong with it.
    :return: The problematic node and the message, as docutils wants
        them.
    """
    msg = inliner.reporter.error(
        message, nodes.literal_block(rawtext, rawtext), line=lineno
    )
    return [inliner.problematic(rawtext, rawtext, msg)], [msg]


def _underline_svg(color: str, seed: str) -> tuple[str, str]:
    """Draw two wobbly strokes for a hand-drawn underline.

    :param color: The stroke colour, already checked.
    :param seed: What the wobble is drawn from, so the same underline in
        the same place comes out the same on every build.
    :return: The left-to-right and right-to-left SVGs.
    """
    uniform = Random(sha256(seed.encode()).digest()).uniform
    segments = 7
    step = 500 / segments

    def stroke(start: float, stop: float) -> str:
        """Generate a wobbly path between two y anchors."""
        points = [f"M{uniform(1.5, 2.5):.1f} {start + uniform(-0.4, 0.4):.1f}"]
        for index in range(1, segments):
            mid = start + (stop - start) * index / segments
            midx = step * index - uniform(0, step * 0.4)
            midy = mid + uniform(-1.2, 1.2)
            x = step * index + uniform(-2, 2)
            y = mid + uniform(-0.8, 0.8)
            points.append(f"Q{midx:.1f} {midy:.1f} {x:.1f} {y:.1f}")
        points.append(
            f"L{uniform(497, 499):.1f} {stop + uniform(-0.4, 0.4):.1f}"
        )
        return " ".join(points)

    def make_svg(start: float, stop: float) -> str:
        path = stroke(start, stop)
        return (
            "<svg xmlns='http://www.w3.org/2000/svg'"
            " viewBox='0 0 500 8' preserveAspectRatio='none'>"
            f"<path d='{path}' fill='none' stroke='{color}'"
            " stroke-width='2.5' stroke-linecap='round'/>"
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

        Text is normal, but now it is :stylise:`red <color: red;>`.

    :param role: The role name, as written (unused).
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role sits on, for error reporting.
    :param inliner: The docutils inliner that called this.
    :param options: Role options (unused).
    :param content: Role content (unused).
    :return: The styled text and the error messages if the text does
        not split on a `<`.
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
    pipe::

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
        does not split on a `<`.
    """
    del role, options, content
    alt, rest = _split(text)
    if rest is None:
        return _reject(inliner, rawtext, lineno, f"Invalid email: {text!r}")
    href, _, subject = rest.partition("|")
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

    The colour is yellow unless the role names one::

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
    color = color or "yellow"
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

    The colour is orange unless the role names one::

        This is :underline:`notable` content.
        This is :underline:`notable <red>` content.

    :param role: The role name, as written (unused).
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role sits on, for error reporting.
    :param inliner: The docutils inliner that called this.
    :param options: Role options (unused).
    :param content: Role content (unused).
    :return: The underlined text and the error messages if the colour
        looks like markup.
    """
    del role, options, content
    element, color = _split(text)
    color = color or "#FF9800"
    if not COLOUR.match(color):
        return _reject(inliner, rawtext, lineno, f"Invalid colour: {color!r}")
    seed = f"{inliner.document.get('source', '')}:{lineno}:{rawtext}"
    ltr, rtl = (_.replace("#", "%23") for _ in _underline_svg(color, seed))
    style = (
        f'--km-ul-fwd: url("data:image/svg+xml,{ltr}");'
        f' --km-ul-ret: url("data:image/svg+xml,{rtl}");'
    )
    return [ink(rawtext, element, classes=["km-pencil"], style=style)], []
