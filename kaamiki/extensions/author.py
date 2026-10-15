"""\
Author Directive
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February 2025
Last updated on: 12 October 2026

An `author` directive that renders the byline under a page title::

    .. author:: Akshay Mestry
       :avatar: https://example.com/avatar.png
       :url: https://github.com/xames3
       :avatar-size: 24
"""

import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import fields
from kaamiki.extensions.utils import opens_new_tab
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import reading_time
from kaamiki.extensions.utils import render
from kaamiki.extensions.utils import rooted
from kaamiki.extensions.utils import seconds
from kaamiki.extensions.utils import trail

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "author"
template: t.Final[str] = "directives/author.html.jinja"
INTERVAL: t.Final[float] = 3.0


class node(nodes.Element):
    """The parsed directive, waiting for `visit` to write it out."""


class directive(rst.Directive):
    """The `author` directive.

    Options::

        - `avatar`: URL of the author's picture.
        - `url`: Where the name links to, a profile or a mailto.
        - `background`: One or more image URLs to fade through behind
          the title.
        - `avatar-size`: The picture's width and height in pixels.
          Defaults to 20.
        - `interval`: Seconds each background stays, at least 3.
          Defaults to 7.
        - `hide-reading-time`: Hides the reading time, which is shown
          without it.
        - `hide-copy-url`: Hides the copy button, which is shown
          without it.
    """

    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {  # noqa: RUF012
        "avatar": rst.directives.uri,
        "url": rst.directives.uri,
        "background": rst.directives.unchanged,
        "avatar-size": rst.directives.positive_int,
        "interval": seconds,
        "hide-reading-time": rst.directives.flag,
        "hide-copy-url": rst.directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        """Collect the options and return the node.

        Only what the page writes goes on the node, `visit` fills in
        the rest from `project`. The name also becomes the page's
        author, unless its `.. Author:` comment named one first, and
        the first background, when written, becomes a fallback for its
        social image.

        :return: The node, followed by the `raw` nodes `trail` returns
            for the link checker and anything the name reported.
        """
        text = self.arguments.pop().strip()
        if self.options.get("interval", INTERVAL) < INTERVAL:
            raise self.error(
                f"author needs an interval of {INTERVAL:g} seconds or more"
            )
        options = self.options
        options["reading_time"] = "hide-reading-time" not in options
        options["copy_url"] = "hide-copy-url" not in options
        if "avatar-size" in options:
            options["avatar_size"] = options["avatar-size"]
        env = self.state.document.settings.env
        metadata = env.metadata.setdefault(env.docname, {})
        metadata.setdefault("author", text)
        pictures = self.options.get("background", "").split()
        if pictures:
            metadata.setdefault("km-pg-background", pictures[0])
        words, messages = parse(self, text, "name")
        element = node("", words, **self.options)
        return [element, *trail(self.options), *messages]


def visit(self: HTMLTranslator, node: node) -> None:
    """Write the widget out when the HTML writer reaches the node.

    :param self: The HTML translator, whose body this appends to.
    :param node: The `author` node, its attributes and its name.
    :raises nodes.SkipNode: Always, since the name is written already.
    """
    config = self.builder.config
    context = config.html_context
    attributes = dict(node.attributes)
    attributes.update(fields(self, node))
    attributes["project"] = context["km_project"]
    url = attributes.get("url") or attributes["project"]["source"]
    attributes["new_tab"] = opens_new_tab(url, config)
    attributes["fa_icons"] = context["km_fa_icons"]
    attributes["minutes"] = max(1, reading_time(node.document, config))
    avatar = attributes.get("avatar") or attributes["project"]["avatar"]
    attributes["avatar"] = rooted(self, avatar)
    background = attributes.get("background", "").split()
    pictures = [rooted(self, _) for _ in background]
    attributes["data"] = {"data-km-background": " ".join(pictures) or None}
    if pictures and "interval" in attributes:
        attributes["data"]["data-km-interval"] = round(
            attributes["interval"] * 1000
        )
    self.body.append(render(template, **attributes))
    raise nodes.SkipNode


def html_page_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Name the page's author for the `<head>`.

    The `.. Author:` comment or the byline wins, then the project's
    author.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree or `None` for generated
        pages.
    """
    del pagename, templatename, doctree
    meta: dict[str, str] = context.get("meta") or {}
    project = app.config.html_context["km_project"]
    context["km_author"] = (
        meta.get("author") or project.get("author") or app.config.author
    )
