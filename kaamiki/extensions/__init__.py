"""\
Theme Extension Manager
=======================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February, 2025
Last updated on: 29 September, 2026

The theme's directives live one to a module. `directives` is the list
`kaamiki.setup()` walks to register them; a module joins the theme by
being imported here and named in it.
"""

from __future__ import annotations

import typing as t

from . import author
from . import button
from . import embed
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
    repository,
    thumbnail,
    video,
    walkthrough,
    youtube,
)
