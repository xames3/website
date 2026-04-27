"""\
YouTube Thumbnail Directive
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 06 September, 2025
Last updated on: 02 November, 2025

This module defines a custom `thumbnail` directive for this sphinx theme.
The directive allows embedding a YouTube video thumbnail card directly
within the document.

The `thumbnail` directive is designed to extend reStructuredText (rST)
capabilities by fetching metadata from a YouTube URL and rendering a
styled card.

The `thumbnail` directive can be used in reStructuredText documents as
follows::

    .. thumbnail:: https://www.youtube.com/watch?v=dQw4w9WgXcQ
        :title: Never Gonna Give You Up
        :channel: Rick Astley

The above snippet will be processed and rendered according to the
theme's Jinja2 template, producing a final HTML output.
"""

from __future__ import annotations

import os.path as p
import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst
import jinja2

if t.TYPE_CHECKING:
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "thumbnail"
here: str = p.dirname(__file__)
templates: str = "../base/templates"
html = p.join(p.abspath(p.join(here, templates)), "thumbnail.html.jinja")

with open(html) as f:
    template = jinja2.Template(f.read())


class node(nodes.Element):
    """Class to represent a custom node in the document tree.

    This class extends the `nodes.Element` from `docutils`, serving as
    the container for the parsed information. The node will ultimately
    be transformed into HTML or other output formats by the relevant
    Sphinx translators.
    """


class directive(rst.Directive):
    """Custom `thumbnail` directive for reStructuredText.

    This class defines the behavior of the `thumbnail` directive,
    including how it processes options and content, and how it generates
    nodes to be inserted into the document tree.
    """

    has_content = True

    def run(self) -> list[nodes.Node]:
        """Parse directive options and create an `thumbnail` node.

        This method gathers all options provided by the user (if any) in
        the `thumbnail` directive, constructs a new `node` instance, and
        returns it wrapped in a list.

        The returned node is then placed into the document tree at the
        directive's location. Further processing will convert the node
        into HTML or other formats.

        :return: A list containing a single `node` element.

        .. deprecated:: 8.9.2025

            [1] Deprecated using `requests` and `BeautifulSoup` for
                fetching and parsing YouTube metadata. This approach
                was unreliable due to frequent changes in YouTube's HTML
                structure and super long build times.
            [2] The directive now uses YouTube's oEmbed endpoint to
                fetch video metadata in a more stable and efficient
                manner.
        """
        self.assert_has_content()
        src = rst.directives.uri(self.content.pop())
        vid = src
        if "youtu.be/" in src:
            vid = src.rsplit("/", 1)[-1].split("?", 1)[0]
        elif "watch?v=" in src:
            vid = src.split("v=", 1)[-1].split("&", 1)[0]
        self.options["src"] = src
        self.options["video_id"] = vid
        self.options["thumbnail"] = (
            f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"
        )
        attributes: dict[str, str] = {}
        attributes["text"] = template.render(**self.options)
        attributes["format"] = "html"
        return [nodes.raw(**attributes)]


def visit(self: HTMLTranslator, node: node) -> None:
    """Handle the entry processing of the `thumbnail` node during HTML
    generation.

    This method is called when the HTML translator encounters the
    `thumbnail` node in the document tree. It retrieves the relevant
    attributes from the node (if any) and uses Jinja2 templating to
    produce the final HTML output. Since the `thumbnail` node does not
    require any actions, the method currently acts as a placeholder.

    :param self: The HTML translator instance.
    :param node: The `thumbnail` node being processed.
    """


def depart(self: HTMLTranslator, node: node) -> None:
    """Handle the exit processing of the `thumbnail` node during HTML
    generation.

    This method is invoked after the node's HTML representation has been
    fully processed and added to the output. Since the `thumbnail` node
    does not require any closing actions, the method currently acts as a
    placeholder.

    :param self: The HTML translator instance.
    :param node: The `thumbnail` node being processed.
    """
