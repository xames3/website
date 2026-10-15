"""\
Theme Extension Manager
=======================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February 2025
Last updated on: 15 October 2026

All of Kaamiki's custom directives.
"""

import typing as t

from . import author
from . import button
from . import embed
from . import release
from . import repository
from . import thumbnail
from . import video
from . import youtube
from .explainer import attempts
from .explainer import walkthrough

if t.TYPE_CHECKING:
    import types
    from collections.abc import Sequence

directives: Sequence[types.ModuleType] = (
    attempts,
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
