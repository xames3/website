"""\
Kaamiki Extension Manager
=========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February 2025
Last updated on: 04 November 2026

All of Kaamiki's custom directives.
"""

from __future__ import annotations

import typing as t

from . import accordion
from . import block
from . import button
from . import byline
from . import carousel
from . import columns
from . import embed
from . import release
from . import repository
from . import tabs
from . import thumbnail
from . import video
from . import youtube
from .code import explain
from .code import version

if t.TYPE_CHECKING:
    import types
    from collections.abc import Sequence

directives: Sequence[types.ModuleType] = (
    accordion,
    block,
    button,
    byline,
    carousel,
    columns,
    embed,
    explain,
    release,
    repository,
    tabs,
    thumbnail,
    version,
    video,
    youtube,
)
