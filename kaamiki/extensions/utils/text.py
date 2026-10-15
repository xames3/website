"""\
Text Utilities
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 15 October 2026

The helpers that flatten and shorten text. These don't need their own
module as of now, but I think I'll expand these helpers in future as
Kaamiki grows.
"""

import re
from html import unescape

TAG_RE: re.Pattern[str] = re.compile(r"</?[A-Za-z][^<>]*>")


def plain(text: str) -> str:
    """Flatten rendered HTML down to bare text."""
    return " ".join(unescape(TAG_RE.sub("", text)).split())


def tidy(text: str) -> str:
    """Collapse the whitespace in plain text."""
    return " ".join(text.split())


def clip(text: str, limit: int) -> str:
    """Cut a line down to length on a word boundary, `...` included."""
    if len(text) <= limit:
        return text
    room = max(0, limit - 3)
    cut = text[:room]
    if text[room : room + 1] != " ":
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(",;:.") + "..."
