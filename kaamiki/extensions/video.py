"""\
Video Directive
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February, 2025
Last updated on: 02 November, 2025

This module defines a custom `video` directive for this sphinx theme. The
directive allows embedding a video directly within the document.

The `video` directive is designed to extend reStructuredText (rST)
capabilities by injecting structured metadata about the content, which
can be styled or processed further using Jinja2 templates.

The `video` directive can be used in reStructuredText documents as
follows::

    .. code-block:: rst

        .. video:: https://www.w3schools.com/tags/movie.mp4

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

name: t.Final[str] = "video"
here: str = p.dirname(__file__)
templates: str = "../base/templates"
html = p.join(p.abspath(p.join(here, templates)), "video.html.jinja")

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
    """Custom `video` directive for reStructuredText.

    This class defines the behavior of the `video` directive, including
    how it processes options and content, and how it generates nodes to
    be inserted into the document tree.

    The directive supports the following options::

        - `autoplay`: Boolean flag to either autoplay the video on load.
        - `caption`: Video caption.
    """

    has_content = True
    option_spec = {  # noqa: RUF012
        "autoplay": rst.directives.flag,
        "caption": rst.directives.unchanged,
    }

    def run(self) -> list[nodes.Node]:
        """Parse directive options and create an `video` node.

        This method gathers all options provided by the user (if any) in
        the `video` directive, constructs a new `node` instance, and
        returns it wrapped in a list.

        The returned node is then placed into the document tree at the
        directive's location. Further processing will convert the node
        into HTML or other formats.

        :return: A list containing a single `node` element.
        """
        self.assert_has_content()
        self.options["url"] = rst.directives.uri("\n".join(self.content))
        attributes: dict[str, str] = {}
        attributes["text"] = template.render(**self.options)
        attributes["format"] = "html"
        return [nodes.raw(**attributes)]


def visit(self: HTMLTranslator, node: node) -> None:
    """Handle the entry processing of the `video` node during HTML
    generation.

    This method is called when the HTML translator encounters the
    `video` node in the document tree. It retrieves the relevant
    attributes from the node (if any) and uses Jinja2 templating to
    produce the final HTML output. Since the `video` node does not
    require any actions, the method currently acts as a placeholder.

    :param self: The HTML translator instance.
    :param node: The `video` node being processed.
    """


def depart(self: HTMLTranslator, node: node) -> None:
    """Handle the exit processing of the `video` node during HTML
    generation.

    This method is invoked after the node's HTML representation has been
    fully processed and added to the output. Since the `video` node
    does not require any closing actions, the method currently acts as a
    placeholder.

    :param self: The HTML translator instance.
    :param node: The `video` node being processed.
    """
