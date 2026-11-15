"""\
Kaamiki Extension Manager
=========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February 2025
Last updated on: 15 November 2026

The extension modules of Kaamiki. Each module is imported here, so
that its directives, nodes and hooks are recorded.
"""

from __future__ import annotations

from . import accordion
from . import block
from . import button
from . import byline
from . import carousel
from . import columns
from . import embed
from . import nesting
from . import release
from . import repository
from . import tabs
from . import thumbnail
from . import video
from . import youtube
from .code import explain
from .code import version

__all__: list[str] = [
    "accordion",
    "block",
    "button",
    "byline",
    "carousel",
    "columns",
    "embed",
    "explain",
    "nesting",
    "release",
    "repository",
    "tabs",
    "thumbnail",
    "version",
    "video",
    "youtube",
]
