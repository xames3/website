"""\
Class Aliases
=============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 27 October 2026
Last updated on: 07 November 2026

The classes an author writes in rST and the BEM classes they become.
"""

from __future__ import annotations

import typing as t
from types import MappingProxyType

from docutils import nodes

from kaamiki.extensions.utils.doctree import findall

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from sphinx.application import Sphinx

ALIASES: t.Final[Mapping[str, str]] = MappingProxyType(
    {
        "km-figure-fuzzy-blur": "km-figure--fuzzy-blur",
        "km-figure-greyscale": "km-figure--greyscale",
        "km-figure-pixelated-blur": "km-figure--pixelated-blur",
        "km-figure-zoom": "km-figure--zoom",
        "km-text-lead": "km-text--lead",
        "km-text-pre-section": "km-text--pre-section",
        "km-text-subsection": "km-text--subsection",
        "km-tone-blue": "km-tone--blue",
        "km-tone-green": "km-tone--green",
        "km-tone-red": "km-tone--red",
        "km-tone-yellow": "km-tone--yellow",
    }
)


def spell(app: Sphinx, doctree: nodes.document) -> None:
    """Swap each alias on a page for the BEM class it stands for.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read.
    """
    del app
    for element in findall(doctree, nodes.Element):
        classes = element.get("classes")
        if classes:
            element["classes"] = [ALIASES.get(_, _) for _ in classes]
