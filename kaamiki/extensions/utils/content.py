"""\
Content Rules
=============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 15 November 2026
Last updated on: 15 November 2026

The one pass that checks each page against the content rules of the
settings. A setting declares its rule with `Value(content=...)`, and
this pass runs each rule on each page that is read.
"""

from __future__ import annotations

import typing as t

from docutils import nodes

from kaamiki.extensions.utils.checks import fail
from kaamiki.extensions.utils.hooks import on
from kaamiki.extensions.utils.settings import Settings
from kaamiki.extensions.utils.settings import option

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx

    from kaamiki.extensions.utils.settings import Content

RULED: t.Final[tuple[tuple[str, Content], ...]] = tuple(
    (key, each.content)
    for key, each in Settings.schema.items()
    if each.content is not None
)


def place(node: nodes.Element) -> str:
    """Say where a node is, as `source:line`.

    :param node: The node that a rule found.
    :return: The file and the line. docutils gives a comment the line
        after it when a blank line follows, so the line of a comment is
        found in the file.
    """
    source = str(node.source or "")
    line = node.line or 0
    if isinstance(node, nodes.comment) and source:
        with open(source, encoding="utf-8") as f:
            lines = f.read().splitlines()
        said = f".. {node.astext()}"
        line = next(
            (n for n, _ in enumerate(lines, 1) if _.strip() == said), line
        )
    return f"{source}:{line}" if line else source


@on("doctree-read")
def content_rules(app: Sphinx, doctree: nodes.document) -> None:
    """Check a page against the content rules of the settings.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read.
    :raises KaamikiError: For the first problem, with the file, the
        line and the setting, as `kaamiki.conf.site.last_updated_fmt`.
    """
    for key, rule in RULED:
        for node, problem in rule(app.config, doctree):
            fail(f"{option(key)}: {problem}", place(node))
