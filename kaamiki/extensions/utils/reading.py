"""\
Reading Utilities
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 15 November 2026

The helpers that find how long a page takes to read.
"""

from __future__ import annotations

import typing as t
from math import ceil

from docutils import nodes
from sphinx import addnodes

from kaamiki.extensions.utils.directives import toggle
from kaamiki.extensions.utils.doctree import alternatives
from kaamiki.extensions.utils.doctree import annotated
from kaamiki.extensions.utils.hooks import on
from kaamiki.extensions.utils.settings import NAME
from kaamiki.extensions.utils.settings import values

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.config import Config

SKIPPED: t.Final[tuple[type, ...]] = (
    annotated,
    addnodes.compact_paragraph,
    nodes.literal_block,
    nodes.table,
)


def words(node: nodes.Node) -> int:
    """Count the words in the prose of a node.

    :param node: The node to start from.
    :return: The words in its paragraphs, without what `SKIPPED` names
        or a table of contents, and only the largest panel of a set of
        `alternatives`.
    """
    if isinstance(node, SKIPPED) or (
        isinstance(node, nodes.topic) and "contents" in node["classes"]
    ):
        return 0
    if isinstance(node, nodes.paragraph):
        return len(node.astext().split())
    if not isinstance(node, nodes.Element):
        return 0
    counts = [words(_) for _ in node.children]
    return (
        max(counts, default=0)
        if isinstance(node, alternatives)
        else sum(counts)
    )


def wordcount(doctree: nodes.document | None) -> int:
    """Count the words in the prose of a page.

    :param doctree: The resolved doctree, or `None` for a generated
        page.
    :return: The number of words.
    """
    return 0 if doctree is None else words(doctree)


def reading_time(doctree: nodes.document | None, config: Config) -> int:
    """Find approximately how many minutes a page takes to read.

    :param doctree: The resolved doctree, or `None` for a generated
        page.
    :param config: The Sphinx configuration, for
        `kaamiki.conf.site.words_per_minute`.
    :return: The minutes, rounded up.
    """
    speed: int = values(config).site.words_per_minute
    return ceil(wordcount(doctree) / speed)


@on("html-page-context")
def show_more(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Find whether a page is long enough to fold.

    :param app: The Sphinx application instance. A page that takes less
        than `kaamiki.conf.show.more_after` minutes to read never
        folds. `kaamiki.conf.show.more` and `:km-show-more:` only set
        the fold off or on for a page that is long enough.
    :param pagename: The page that is written.
    :param templatename: The template that writes it.
    :param context: The context of the page, changed in place.
    :param doctree: The resolved doctree, or `None` for a generated
        page.
    """
    del pagename, templatename
    config = app.config
    after = values(config).show.more_after
    meta: dict[str, str] = context.get("meta") or {}
    on = (
        toggle(meta["km-show-more"])
        if "km-show-more" in meta
        else values(config).show.more
    )
    long_enough = reading_time(doctree, config) >= after
    context[NAME]["show.more"] = bool(on and long_enough)
