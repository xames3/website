"""\
Custom Roles
============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February, 2025
Last updated on: 17 February, 2026

This module provides custom roles for this sphinx theme that provides a
way to add features to the document.
"""

from __future__ import annotations

import typing as t
from random import uniform

import docutils.nodes as nodes


def underline_svg(color: str) -> str:
    """Generate an SVG path to mimic a rough underline.

    Each call produces two slightly different wobbly strokes so that
    no two underlines look exactly the same, mimicking a hand-drawn
    pencil line.
    """
    mid = 3.0
    segments = 7
    step = 500 / segments

    def stroke_path() -> str:
        """Generate random paths."""
        pts = [f"M{uniform(1.5, 2.5):.1f} {uniform(mid - 0.8, mid + 0.8):.1f}"]
        for idx in range(1, segments):
            cx = step * idx - uniform(0, step * 0.4)
            cy = uniform(mid - 1.5, mid + 1.5)
            x = step * idx + uniform(-2, 2)
            y = uniform(mid - 1.0, mid + 1.0)
            pts.append(f"Q{cx:.1f} {cy:.1f} {x:.1f} {y:.1f}")
        pts.append(
            f"L{uniform(497, 499):.1f} {uniform(mid - 0.8, mid + 0.8):.1f}"
        )
        return " ".join(pts)

    path1 = stroke_path()
    path2 = stroke_path()
    return (
        "<svg xmlns='http://www.w3.org/2000/svg'"
        " viewBox='0 0 500 6' preserveAspectRatio='none'>"
        f"<path d='{path1}' fill='none' stroke='{color}'"
        " stroke-width='3' stroke-linecap='round'/>"
        f"<path d='{path2}' fill='none' stroke='{color}'"
        " stroke-width='3.25' stroke-linecap='round'/>"
        "</svg>"
    )


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
    :param lineno: The line number where the role was encountered in the
        source text.
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
    # NOTE(xames3): The parameters `role`, `options`, and `content` are
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
    :param lineno: The line number where the role was encountered in the
        source text.
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
    # NOTE(xames3): The parameters `role`, `options`, and `content` are
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
    :param lineno: The line number where the role was encountered in the
        source text.
    :param inliner: The inliner instance that called the role function.
    :param options: Additional options passed to the role function,
        defaults to `None`.
    :param content: Content passed to the role function, defaults
        to `None`.
    :return: A tuple of list with a single `nodes.raw` object
        representing the highlighted text and a list of system messages
        generated during processing (typically empty if no errors).
    """
    # NOTE(xames3): The parameters `role`, `rawtext`, `options`, `lineno`,
    # `inliner`, and `content` are currently unused but are included to match
    # the expected signature for a Sphinx role function.
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
    :param lineno: The line number where the role was encountered in the
        source text.
    :param inliner: The inliner instance that called the role function.
    :param options: Additional options passed to the role function,
        defaults to `None`.
    :param content: Content passed to the role function, defaults
        to `None`.
    :return: A tuple of list with a single `nodes.raw` object
        representing the underlined text and a list of system messages
        generated during processing (typically empty if no errors).
    """
    # NOTE(xames3): The parameters `role`, `rawtext`, `options`, `lineno`,
    # `inliner`, and `content` are currently unused but are included to match
    # the expected signature for a Sphinx role function.
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
    svg = underline_svg(color).replace("#", "%23")
    raw = (
        '<span class="pencil" '
        f'style="background-image: url(&quot;data:image/svg+xml,{svg}&quot;);"'
        f">{element}</span>"
    )
    return [nodes.raw(text=raw, format="html")], []
