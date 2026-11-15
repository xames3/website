"""\
Text Utilities
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 15 November 2026

The helpers that flatten, tidy and shorten text, and give a level to the
captions of a table of contents.
"""

import re
import typing as t
from html import unescape

CAPTION: t.Final[re.Pattern[str]] = re.compile(
    r'(<p class="caption") role="heading">'
)
TAG_RE: t.Final[re.Pattern[str]] = re.compile(r"</?[A-Za-z][^<>]*>")


def tidy(text: str) -> str:
    """Make each run of whitespace in plain text one space.

    :param text: The text.
    :return: The text with each run of whitespace as one space.
    """
    return " ".join(text.split())


def plain(text: str) -> str:
    """Change rendered HTML to plain text.

    :param text: The HTML.
    :return: Its text, tidied.
    """
    return tidy(unescape(TAG_RE.sub("", text)))


def clip(text: str, limit: int) -> str:
    """Cut a line to a length, with `...` at the end.

    :param text: The line.
    :param limit: The maximum number of characters, with `...`.
    :return: The line. A longer line is cut at the last space that fits, or in a
        word when the first word is too long.
    :raises ValueError: For a limit less than 4.
    """
    if limit < 4:
        raise ValueError(f"expected a limit of 4 or more, got {limit}")
    if len(text) <= limit:
        return text
    room = limit - 3
    cut = text[:room]
    if text[room : room + 1] != " ":
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(",;:.") + "..."


def levelled(fragment: str) -> str:
    """Give each caption in a table of contents a heading level.

    :param fragment: The table of contents as HTML.
    :return: The table of contents with each caption at level 2. Sphinx writes a
        caption as `role="heading"` without a level, and a screen reader needs
        the level.
    """
    return CAPTION.sub(r'\1 role="heading" aria-level="2">', fragment)
