"""\
Custom Roles
============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February, 2025
Last updated on: 10 September, 2026

The theme's inline roles: `style`, `email`, `mark` and `underline`.
Every public function here is registered as a role of the same name,
so a helper in this module takes a leading underscore.

.. versionadded:: 10.9.2026

    A colour is checked against `COLOUR` before it reaches an
    attribute. Nothing legitimate in a colour needs a quote or an angle
    bracket, so anything carrying one is reported rather than pasted
    into the markup.

.. versionchanged:: 10.9.2026

    [1] Every role escapes its text. They build HTML with f-strings, so
        an `&` or a `<` in the content landed in the output raw, and a
        quote in a colour could close the `style` attribute and open a
        new one.
    [2] `email` uses `utils.findall` rather than the deprecated
        `.traverse()`.
    [3] `email` survives a page with no title, and text with no `<`,
        instead of raising at build time. Its subject is URL-encoded.

.. deprecated:: 10.9.2026

    [1] `underline_svg` is now `_underline_svg`. It was being handed to
        docutils as a role of its own.
    [2] `mark` and `underline` no longer shuffle their parameters about
        to look used. Both genuinely use `rawtext`, `lineno` and
        `inliner` now that they can report a bad colour.
"""

from __future__ import annotations

import re
import typing as t
from html import escape
from random import uniform
from urllib.parse import quote

import docutils.nodes as nodes

from kaamiki.extensions.utils import findall

# A colour lands inside an attribute, and in `underline`'s case inside
# an SVG nested in a data URI in that attribute. Nothing legitimate in
# there needs a quote or an angle bracket, so anything carrying one is
# an author mistake rather than a colour.
COLOUR: re.Pattern[str] = re.compile(r"^[#\w(),.%\s/-]+$")


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


def _underline_svg(color: str) -> tuple[str, str]:
    """Draw two wobbly strokes for a hand-drawn underline.

    :param color: The stroke colour, already checked.
    :return: The left-to-right and right-to-left SVGs.
    """
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

        Text is normal, but now it is :style:`red <color: red;>`.

    :param role: The role name, as written.
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role sits on, for error reporting.
    :param inliner: The docutils inliner that called this.
    :param options: Role options, unused.
    :param content: Role content, unused.
    :return: One `raw` node, and the error messages if the text does
        not split on a `<`.
    """
    # NOTE(xames3): The parameters `role`, `options` and `content` are
    # currently unused but are included to match the expected signature
    # for a Sphinx role function.
    role = role or ""
    options = options or {}
    content = content or []
    try:
        element, style = map(str.strip, text.split("<", 1))
        style = style.rstrip(">")
    except ValueError:
        msg = inliner.reporter.error(
            f"Invalid style: {text!r}",
            nodes.literal_block(rawtext, rawtext),
            line=lineno,
        )
        return [inliner.problematic(rawtext, rawtext, msg)], [msg]
    raw = f'<span style="{escape(style, quote=True)}">{escape(element)}</span>'
    return [nodes.raw(text=raw, format="html")], []


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

    :param role: The role name, as written.
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role sits on, for error reporting.
    :param inliner: The docutils inliner that called this.
    :param options: Role options, unused.
    :param content: Role content, unused.
    :return: One `reference` node, and the error messages if the text
        does not split on a `<`.
    """
    # NOTE(xames3): The parameters `role`, `options` and `content` are
    # currently unused but are included to match the expected signature
    # for a Sphinx role function.
    role = role or ""
    options = options or {}
    content = content or []
    if "<" not in text:
        return _reject(inliner, rawtext, lineno, f"Invalid email: {text!r}")
    subject = ""
    for title in findall(inliner.document, nodes.title):
        subject = title.astext().strip()
        break
    alt, rest = text.split("<", 1)
    alt = alt.strip()
    if "|" in rest:
        href, _, subject = rest.partition("|")
        subject = subject.strip(">").strip()
    else:
        href = rest.strip(">")
    refuri = f"mailto:{href.strip()}?subject={quote(subject)}"
    return [nodes.reference(rawtext, alt, refuri=refuri, line=lineno)], []


def mark(
    role: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: t.Any,
    options: dict[str, t.Any] | None = None,
    content: list[t.Any] | None = None,
) -> tuple[list[nodes.Node], list[nodes.system_message]]:
    """Run a highlighter pen over a run of text.

    The colour is yellow unless the role names one::

        This is :mark:`important` information.
        This is :mark:`critical <red>` information.

    :param role: The role name, as written.
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role sits on, for error reporting.
    :param inliner: The docutils inliner that called this.
    :param options: Role options, unused.
    :param content: Role content, unused.
    :return: One `raw` node, and the error messages if the colour looks
        like markup.
    """
    # NOTE(xames3): `role`, `options` and `content` are unused but are
    # included to match the signature docutils expects of a role.
    role = role or ""
    options = options or {}
    content = content or []
    if "<" in text:
        element, color = map(str.strip, text.split("<", 1))
        color = color.rstrip(">").strip()
    else:
        element = text
        color = "yellow"
    if not COLOUR.match(color):
        return _reject(inliner, rawtext, lineno, f"Invalid colour: {color!r}")
    raw = f'<span class="marker" style="--marker-color: {color};">'
    raw += f"{escape(element)}</span>"
    return [nodes.raw(text=raw, format="html")], []


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

    :param role: The role name, as written.
    :param rawtext: The whole role, markup and all.
    :param text: What was written inside it.
    :param lineno: The line the role sits on, for error reporting.
    :param inliner: The docutils inliner that called this.
    :param options: Role options, unused.
    :param content: Role content, unused.
    :return: One `raw` node, and the error messages if the colour looks
        like markup.
    """
    # NOTE(xames3): `role`, `options` and `content` are unused but are
    # included to match the signature docutils expects of a role.
    role = role or ""
    options = options or {}
    content = content or []
    if "<" in text:
        element, color = map(str.strip, text.split("<", 1))
        color = color.rstrip(">").strip()
    else:
        element = text
        color = "#FF9800"
    if not COLOUR.match(color):
        return _reject(inliner, rawtext, lineno, f"Invalid colour: {color!r}")
    ltr, rtl = _underline_svg(color)
    ltr = ltr.replace("#", "%23")
    rtl = rtl.replace("#", "%23")
    raw = (
        '<span class="pencil" '
        f'style="--ul-fwd: url(&quot;data:image/svg+xml,{ltr}&quot;); '
        f'--ul-ret: url(&quot;data:image/svg+xml,{rtl}&quot;);"'
        f">{escape(element)}</span>"
    )
    return [nodes.raw(text=raw, format="html")], []
