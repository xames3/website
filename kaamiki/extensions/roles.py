"""\
Custom Roles
============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February, 2025
Last updated on: 29 April, 2026

This module provides custom roles for the Kaamiki Sphinx Theme that
provides a way to add features to the document.
"""

from __future__ import annotations

import typing as t
from random import uniform

import docutils.nodes as nodes


def underline_svg(color: str) -> tuple[str, str]:
    """Fake two SVG strokes for a double-pass hand-drawn underline."""
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
    """Apply inline styling to text.

    This function allows for applying a CSS style to a piece of text
    within reStructuredText using a role syntax. The expected input
    format is `text <style>`. If the input format is invalid, an error
    is reported.

    Example::

        .. code-block:: rst

            Text is normal, but now its in :style:`red <color: red;>`.

    :param role: The role name used in the source text.
    :param rawtext: The entire markup text representing the role.
    :param text: The text by the user.
    :param lineno: The line number where the role was encountered in
        the source text.
    :param inliner: The inliner instance that called the role function.
    :param options: Additional options passed to the role function,
        defaults to `None`.
    :param content: Content passed to the role function, defaults
        to `None`.
    :return: A tuple of list with a single `nodes.raw` object
        representing the styled text and a list of system messages
        generated during processing (typically empty if no errors).
    :raises: None, but will report an error message if the input format
        is invalid.
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
    raw = f'<span style="{style}">{element}</span>'
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
    """Create a `mailto` link.

    This function generates a `mailto` link. By default, it populates
    the subject with the current page's title, but it can be overridden
    these defaults directly in the role.

    Example::

        .. code-block:: rst

            Send me an :email:`email <xa@mes3.dev>`.

        .. code-block:: rst

            Send me an :email:`email <xa@mes3.dev | Hello hello!!>`

    :param role: The role name used in the source text.
    :param rawtext: The entire markup text representing the role.
    :param text: The text by the user, which becomes the link text.
    :param lineno: The line number where the role was encountered in
        the source text.
    :param inliner: The inliner instance that called the role function.
    :param options: Additional options passed to the role function,
        defaults to `None`.
    :param content: Content passed to the role function, defaults
        to `None`.
    :return: A tuple of list with a single `nodes.raw` object
        representing the styled text and a list of system messages
        generated during processing (typically empty if no errors).
    :raises: None, but will report an error message if the input format
        is invalid.
    """
    # NOTE(xames3): The parameters `role`, `options` and `content` are
    # currently unused but are included to match the expected signature
    # for a Sphinx role function.
    role = role or ""
    options = options or {}
    content = content or []
    titles = inliner.document.traverse(nodes.title)
    subject = titles[0].children[-1].astext().strip()
    alt, rest = text.split("<", 1)
    alt = alt.strip()
    if "|" in rest:
        href, *subject = rest.split("|", 1)
        subject = subject[0].strip(">")
    else:
        href = rest.strip(">")
    refuri = f"mailto:{href.strip()}?subject={subject}"
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
    """Apply a marker/highlighter effect to text.

    This function wraps text in a span with a highlighter-style
    background that resembles a hand-drawn marker stroke. An optional
    color can be specified; the default color is yellow.

    Example::

        .. code-block:: rst

            This is :mark:`important` information.

        .. code-block:: rst

            This is :mark:`critical <red>` information.

    :param role: The role name used in the source text.
    :param rawtext: The entire markup text representing the role.
    :param text: The text by the user.
    :param lineno: The line number where the role was encountered in
        the source text.
    :param inliner: The inliner instance that called the role function.
    :param options: Additional options passed to the role function,
        defaults to `None`.
    :param content: Content passed to the role function, defaults
        to `None`.
    :return: A tuple of list with a single `nodes.raw` object
        representing the highlighted text and a list of system messages
        generated during processing (typically empty if no errors).
    """
    # NOTE(xames3): The parameters `role`, `rawtext`, `options`,
    # `lineno`, `inliner` and `content` are currently unused but are
    # included to match the expected signature for a Sphinx role
    # function.
    role = rawtext or role or ""
    lineno = lineno or inliner
    options = options or {}
    content = content or []
    if "<" in text:
        element, color = map(str.strip, text.split("<", 1))
        color = color.rstrip(">").strip()
    else:
        element = text
        color = "yellow"
    raw = f'<span class="marker" style="--marker-color: {color};">'
    raw += f"{element}</span>"
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
    """Apply a pencil-style underline to text.

    This function wraps text in a span with a hand-drawn pencil-style
    underline. An optional color can be specified; the default color is
    orange.

    Example::

        .. code-block:: rst

            This is :underline:`notable` content.

        .. code-block:: rst

            This is :underline:`notable <red>` content.

    :param role: The role name used in the source text.
    :param rawtext: The entire markup text representing the role.
    :param text: The text by the user.
    :param lineno: The line number where the role was encountered in
        the source text.
    :param inliner: The inliner instance that called the role function.
    :param options: Additional options passed to the role function,
        defaults to `None`.
    :param content: Content passed to the role function, defaults
        to `None`.
    :return: A tuple of list with a single `nodes.raw` object
        representing the underlined text and a list of system messages
        generated during processing (typically empty if no errors).
    """
    # NOTE(xames3): The parameters `role`, `rawtext`, `options`,
    # `lineno`, `inliner` and `content` are currently unused but are
    # included to match the expected signature for a Sphinx role
    # function.
    role = rawtext or role or ""
    lineno = lineno or inliner
    options = options or {}
    content = content or []
    if "<" in text:
        element, color = map(str.strip, text.split("<", 1))
        color = color.rstrip(">").strip()
    else:
        element = text
        color = "#FF9800"
    ltr, rtl = underline_svg(color)
    ltr = ltr.replace("#", "%23")
    rtl = rtl.replace("#", "%23")
    raw = (
        '<span class="pencil" '
        f'style="--ul-fwd: url(&quot;data:image/svg+xml,{ltr}&quot;); '
        f'--ul-ret: url(&quot;data:image/svg+xml,{rtl}&quot;);"'
        f">{element}</span>"
    )
    return [nodes.raw(text=raw, format="html")], []
