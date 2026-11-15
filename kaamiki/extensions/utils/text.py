"""\
Text Utilities
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 08 November 2026

The helpers that flatten, tidy and shorten text, and level the captions
of a table of contents.
"""

import re
import typing as t
from html import unescape

CAPTION: t.Final[re.Pattern[str]] = re.compile(
    r'(<p class="caption") role="heading">'
)
TAG_RE: t.Final[re.Pattern[str]] = re.compile(r"</?[A-Za-z][^<>]*>")


def tidy(text: str) -> str:
    """Collapse the whitespace in plain text.

    :param text: The text.
    :return: It with each run of whitespace made a single space.
    """
    return " ".join(text.split())


def plain(text: str) -> str:
    """Flatten rendered HTML down to bare text.

    :param text: The HTML.
    :return: Its text, tidied.
    """
    return tidy(unescape(TAG_RE.sub("", text)))


def clip(text: str, limit: int) -> str:
    """Cut a line down to length, `...` included.

    It cuts at the last space that fits, and in the middle of a word
    when the first word is longer than the room there is.

    :param text: The line.
    :param limit: The most characters it may have, `...` included.
    :return: The line, cut when it's longer than `limit`.
    :raises ValueError: For a limit under 4.
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

    Sphinx writes a caption as `role="heading"` and leaves the level
    out, which a screen reader needs to announce it.

    :param fragment: The table of contents as HTML.
    :return: The table of contents with every caption at level 2.
    """
    return CAPTION.sub(r'\1 role="heading" aria-level="2">', fragment)
