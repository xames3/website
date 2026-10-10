"""\
Reading Utilities
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 09 October, 2026

The helpers that work out how long a page takes to read.
"""

from __future__ import annotations

import typing as t
from math import ceil

from docutils import nodes
from sphinx.util import logging

from kaamiki.extensions.utils.doctree import buried
from kaamiki.extensions.utils.doctree import findall
from kaamiki.extensions.utils.settings import SHOW_MORE_AFTER
from kaamiki.extensions.utils.settings import WORDS_PER_MINUTE
from kaamiki.extensions.utils.settings import setting

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.config import Config

logger = logging.getLogger(__name__)


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


def reading_speed(config: Config) -> int:
    """Read `words_per_minute`, falling back when it isn't a number.

    :param config: The Sphinx configuration.
    :return: Words a minute, at least one.
    """
    value = setting(config, "words_per_minute")
    try:
        speed = int(value)
    except TypeError, ValueError:
        speed = 0
    if speed < 1:
        logger.warning(
            "words_per_minute needs a whole number above zero, got %r;"
            " using %d",
            value,
            WORDS_PER_MINUTE,
            type="kaamiki",
        )
        return WORDS_PER_MINUTE
    return speed


def reading_time(doctree: nodes.document | None, config: Config) -> int:
    """Work out roughly how many minutes a page takes to read.

    Code isn't counted. Sadly, no one reads code these days because of
    shitty AI slop.

    :param doctree: The resolved doctree or `None` for generated
        pages.
    :param config: The Sphinx configuration, for `words_per_minute`.
    :return: Minutes, rounded up.
    """
    return ceil(wordcount(doctree) / reading_speed(config))


def reading_length(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Decide whether a page is long enough to fold up.

    :param app: The Sphinx application instance.
    :param pagename: The name of the page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree or `None` for generated
        pages.
    """
    del pagename, templatename
    options = app.config.html_context
    minutes = reading_time(doctree, app.config)
    after = int(options.get("km_show_more_after", SHOW_MORE_AFTER))
    context["km_show_show_more"] = (
        bool(options.get("km_show_show_more", True)) and minutes >= after
    )
