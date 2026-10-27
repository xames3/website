"""\
Reading Utilities
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 26 October 2026

The helpers that work out how long a page takes to read.
"""

import typing as t
from math import ceil

from docutils import nodes

from kaamiki.extensions.utils.directives import toggle
from kaamiki.extensions.utils.doctree import buried
from kaamiki.extensions.utils.doctree import findall
from kaamiki.extensions.utils.settings import setting

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.config import Config


def wordcount(doctree: nodes.document | None) -> int:
    """Count the words in a page's prose, skipping what `buried` skips.

    :param doctree: The resolved doctree or `None` for generated
        pages.
    :return: The number of words counted.
    """
    if doctree is None:
        return 0
    return sum(
        len(paragraph.astext().split())
        for paragraph in findall(doctree, nodes.paragraph)
        if not buried(paragraph)
    )


def reading_time(doctree: nodes.document | None, config: Config) -> int:
    """Work out roughly how many minutes a page takes to read.

    Code isn't counted, since a reader skims it. Neither are the notes of
    a walkthrough, which a reader scrolls through rather than reads.

    :param doctree: The resolved doctree or `None` for generated
        pages.
    :param config: The Sphinx configuration, for `words_per_minute`.
    :return: Minutes, rounded up.
    """
    speed: int = setting(config, "words_per_minute")
    return ceil(wordcount(doctree) / speed)


def reading_length(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Decide whether a page is long enough to fold up.

    A page that takes less than `show_more_after` minutes to read never
    folds, whatever `show_more` or the page's `:km-show-more:` says. Those
    only switch the fold off, or back on, for a page that's long enough.

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
