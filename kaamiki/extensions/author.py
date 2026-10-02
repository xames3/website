"""\
Author Directive
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February, 2025
Last updated on: 29 September, 2026

An `author` directive that renders the byline under a page title::

    .. author:: Akshay Mestry
       :avatar: https://example.com/avatar.png
       :target: https://github.com/xames3

The name is the argument. Anything left out falls back to the
`project` entry in `html_context`. The widget comes from
`author.html.jinja` and carries the page's reading time.
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import ICONS
from kaamiki.extensions.utils import PROJECT
from kaamiki.extensions.utils import reading_time
from kaamiki.extensions.utils import render
from kaamiki.extensions.utils import trail

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "author"
template: t.Final[str] = "author.html.jinja"


class node(nodes.Element):
    """The parsed directive, waiting for `visit` to write it out."""


class directive(rst.Directive):
    """The `author` directive.

    Options::

        - `avatar`: URL of the author's picture. Falls back to the
          `avatar` in `project` and is left out when neither has one.
        - `target`: Where the name links to, a profile or a mailto.
        - `background`: One or more image URLs to fade through behind
          the title.
    """

    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {  # noqa: RUF012
        "avatar": rst.directives.uri,
        "target": rst.directives.uri,
        "background": rst.directives.unchanged,
    }

    def run(self) -> list[nodes.Node]:
        """Collect the options and return the node.

        Only what the page writes goes on the node. `visit` fills in the
        rest from `project` as the page is written, so the rST wins and
        `conf.py` is the fallback. The name is also the page's author,
        unless its `.. Author:` comment, read before the page was
        parsed, named one first.

        :return: The node, followed by the `raw` nodes `trail` returns
            for the link checker.
        """
        self.options["name"] = self.arguments.pop().strip()
        env = self.state.document.settings.env
        metadata = env.metadata.setdefault(env.docname, {})
        metadata.setdefault("author", self.options["name"])
        element = node("", **self.options)
        return [element, *trail(self.options)]


def visit(self: HTMLTranslator, node: node) -> None:
    """Write the widget out when the HTML writer reaches the node.

    :param self: The HTML translator, whose body this appends to.
    :param node: The `author` node and its attributes.
    """
    context = self.builder.config.html_context
    attributes = dict(node.attributes)
    attributes["project"] = context.get("km_project") or PROJECT
    attributes["fa_icons"] = context.get("km_fa_icons") or ICONS
    attributes["minutes"] = max(1, reading_time(node.document))
    self.body.append(render(template, **attributes))


def html_page_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Name the page's author for the `<head>`.

    `provenance` and the directive have already put the page's
    `.. Author:` comment or else its byline, in its metadata. A page
    with neither or one with no doctree at all, goes by the project's
    author, which is `conf.py`'s unless `html_context` says otherwise.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree or `None` for generated
        pages.
    """
    meta: dict[str, str] = context.get("meta") or {}
    project = app.config.html_context.get("km_project") or {}
    context["km_author"] = (
        meta.get("author") or project.get("author") or app.config.author
    )
