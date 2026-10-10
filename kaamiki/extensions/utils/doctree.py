"""\
Doctree Utilities
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 09 October 2026

The helpers that walk a doctree and pick prose out of it.
"""

from __future__ import annotations

import typing as t
from uuid import uuid4

from docutils import nodes
from sphinx.builders.gettext import MessageCatalogBuilder

from kaamiki.extensions.utils.text import clip

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from sphinx.application import Sphinx

FURNITURE: tuple[type, ...] = (
    nodes.Admonition,
    nodes.figure,
    nodes.literal_block,
    nodes.table,
    nodes.topic,
)
TRANSLATED: t.Final[frozenset[str]] = frozenset(
    {
        "km-fb-button",
        "km-fb-description",
        "km-fb-title",
        "km-pg-description",
        "km-pg-image-alt",
        "km-pg-title",
    }
)


def findall[T: nodes.Element](
    node: nodes.Node,
    element: type[T],
) -> Iterator[T]:
    """Walk a doctree for every node of one type.

    :param node: Where to start looking.
    :param element: The node type to look for.
    :return: Every match, in document order.
    """
    return t.cast("Iterator[T]", node.findall(element))


def buried(paragraph: nodes.Element) -> bool:
    """Say whether a paragraph sits inside an admonition, table or code
    block.

    Figures and topics count too. Lifted out of those, a line reads as
    a non-sequitur.

    :param paragraph: The paragraph to place.
    :return: `True` when it has one of those for an ancestor.
    """
    parent: nodes.Element | None = paragraph.parent
    while parent is not None and not isinstance(parent, FURNITURE):
        parent = parent.parent
    return parent is not None


def standfirst(doctree: nodes.document | None, limit: int) -> str:
    """Pull the page's lead, the line right under the title.

    :param doctree: The resolved doctree or `None` for generated
        pages.
    :param limit: Longest the result may be.
    :return: The lead or an empty string when the page hasn't got
        one.
    """
    if doctree is None:
        return ""
    for paragraph in findall(doctree, nodes.paragraph):
        if "km-lead" not in (paragraph.get("classes") or []):
            continue
        if buried(paragraph):
            continue
        text = " ".join(paragraph.astext().split())
        if text:
            return clip(text, limit)
    return ""


def summarise(doctree: nodes.document | None, limit: int) -> str:
    """Fall back to a page's first usable paragraph.

    :param doctree: The resolved doctree or `None` for generated
        pages.
    :param limit: Longest the result may be.
    :return: A single-line summary or an empty string when the page
        has no usable prose.
    """
    if doctree is None:
        return ""
    for paragraph in findall(doctree, nodes.paragraph):
        if buried(paragraph):
            continue
        text = " ".join(paragraph.astext().split())
        if len(text) >= 40:
            return clip(text, limit)
    return ""


def offer(app: Sphinx, doctree: nodes.document) -> None:
    """Hand the words in a page's own fields to `gettext`.

    Sphinx lifts these fields out of the page before `gettext` sees
    them, so a copy of each is left in a container only a `gettext`
    build gets. This runs ahead of Sphinx's metadata collector.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read.
    """
    if not isinstance(app.builder, MessageCatalogBuilder):
        return
    info = next(findall(doctree, nodes.docinfo), None)
    if info is None:
        return
    box = nodes.container()
    for field in findall(info, nodes.field):
        if field[0].astext() not in TRANSLATED:
            continue
        for paragraph in findall(field[1], nodes.paragraph):
            copy = paragraph.deepcopy()
            copy.uid = uuid4().hex  # type: ignore[attr-defined]
            box += copy
    if len(box):
        doctree += box
