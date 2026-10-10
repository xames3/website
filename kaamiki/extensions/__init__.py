"""\
Theme Extension Manager
=======================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February 2025
Last updated on: 09 October, 2026

All of Kaamiki's custom directives.
"""

from __future__ import annotations

import typing as t

from . import author
from . import button
from . import embed
from . import release
from . import repository
from . import thumbnail
from . import video
from . import youtube
from .explainer import walkthrough

if t.TYPE_CHECKING:
    import types

directives: t.Sequence[types.ModuleType] = (
    author,
    button,
    embed,
    release,
    repository,
    thumbnail,
    video,
    walkthrough,
    youtube,
)
