"""\
Reading Utilities
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 07 November 2026

The helpers that work out how long a page takes to read.
"""

from __future__ import annotations

import typing as t
from math import ceil

from docutils import nodes
from sphinx import addnodes

from kaamiki.extensions.utils.directives import toggle
from kaamiki.extensions.utils.doctree import alternatives
from kaamiki.extensions.utils.doctree import annotated
from kaamiki.extensions.utils.settings import setting

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

    :param node: Where to start counting.
    :return: The words in its paragraphs, none from what `SKIPPED`
        names or a table of contents, and the most any one panel of a
        set of `alternatives` has.
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
    """Count the words in a page's prose.

    :param doctree: The resolved doctree or `None` for generated
        pages.
    :return: The number of words counted.
    """
    return 0 if doctree is None else words(doctree)


def reading_time(doctree: nodes.document | None, config: Config) -> int:
    """Work out roughly how many minutes a page takes to read.

    :param doctree: The resolved doctree or `None` for generated
        pages.
    :param config: The Sphinx configuration, for
        `kaamiki.conf.site.words_per_minute`.
    :return: Minutes, rounded up.
    """
    speed: int = setting(config, "words_per_minute")
    return ceil(wordcount(doctree) / speed)


def show_more(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Decide whether a page is long enough to fold up.

    A page that takes less than `kaamiki.conf.show.more_after` minutes
    to read never folds, whatever `kaamiki.conf.show.more` or the
    page's `:km-show-more:` says. Those only switch the fold off, or
    back on, for a page that's long enough.

    :param app: The Sphinx application instance.
    :param pagename: The name of the page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree or `None` for generated
        pages.
    """
    del pagename, templatename
    config = app.config
    after = int(config.html_context["km_show_more_after"])
    meta: dict[str, str] = context.get("meta") or {}
    on = (
        toggle(meta["km-show-more"])
        if "km-show-more" in meta
        else setting(config, "show_more")
    )
    long_enough = reading_time(doctree, config) >= after
    context["km_show_more"] = bool(on and long_enough)
