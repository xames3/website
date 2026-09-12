"""\
Theme Extension Manager
=======================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February, 2025
Last updated on: 10 September, 2026

This module manages Kaamiki Sphinx Theme's custom directive and roles.

.. deprecated:: 19.10.2025

    The `tagged` directive is now deprecated as it didn't serve any
    specific purpose or was being used in any way.

.. versionchanged:: 31.8.2026

    The `iframe` directive is now registered as `embed`, since it covers
    inline content and external HTML fragments and not just iframes.
"""

from __future__ import annotations

import typing as t

from . import author
from . import button
from . import embed
from . import picture
from . import repository
from . import thumbnail
from . import video
from . import youtube

if t.TYPE_CHECKING:
    import types

directives: t.Sequence[types.ModuleType] = (
    author,
    button,
    embed,
    picture,
    repository,
    thumbnail,
    video,
    youtube,
)
