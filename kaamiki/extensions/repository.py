"""\
GitHub Repository Directive
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 29 October, 2025
Last updated on: 02 November, 2025

This module defines a custom `repository` directive for this sphinx
theme. The directive allows embedding GitHub repository details on the
document.

The `repository` directive is designed to extend reStructuredText (rST)
capabilities by injecting structured metadata about the content, which
can be styled or processed further using Jinja2 templates.

The `repository` directive can be used in reStructuredText documents as
follows::

    .. code-block:: rst

        .. repository:: xames3/xa

The above snippet will be processed and rendered according to the
theme's Jinja2 template, producing a final HTML output.
"""

from __future__ import annotations

import os.path as p
import typing as t

import docutils.nodes as nodes
import jinja2
from docutils.parsers import rst

if t.TYPE_CHECKING:
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "repository"
here: str = p.dirname(__file__)
templates: str = "../base/templates"
html = p.join(p.abspath(p.join(here, templates)), "repository.html.jinja")

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
    """Custom `repository` directive for reStructuredText.

    This class defines the behavior of the `repository` directive,
    including how it processes options and content, and how it generates
    nodes to be inserted into the document tree.

    The directive supports the following options::

        - `stars`: Boolean flag to show stars.
        - `issues`: Boolean flag to show the issue count.
    """

    has_content = True
    # TODO (xames3): Need to add support for boolean checks for
    # rendering either options or both. Currently, both are shown.
    option_spec = {  # noqa: RUF012
        "stars": rst.directives.flag,
        "issues": rst.directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        """Parse directive options and create an `repository` node.

        This method gathers all options provided by the user (if any) in
        the `repository` directive, constructs a new `node` instance,
        and returns it wrapped in a list.

        The returned node is then placed into the document tree at the
        directive's location. Further processing will convert the node
        into HTML or other formats.

        :return: A list containing a single `node` element.
        """
        self.assert_has_content()
        self.options["repo"] = "".join(self.content)
        attributes: dict[str, str] = {}
        attributes["text"] = template.render(**self.options)
        attributes["format"] = "html"
        return [nodes.raw(**attributes)]


def visit(self: HTMLTranslator, node: node) -> None:
    """Handle the entry processing of the `repository` node during HTML
    generation.

    This method is called when the HTML translator encounters the
    `repository` node in the document tree. It retrieves the relevant
    attributes from the node (if any) and uses Jinja2 templating to
    produce the final HTML output. Since the `repository` node does not
    require any actions, the method currently acts as a placeholder.

    :param self: The HTML translator instance.
    :param node: The `repository` node being processed.
    """


def depart(self: HTMLTranslator, node: node) -> None:
    """Handle the exit processing of the `repository` node during HTML
    generation.

    This method is invoked after the node's HTML representation has been
    fully processed and added to the output. Since the `repository` node
    does not require any closing actions, the method currently acts as a
    placeholder.

    :param self: The HTML translator instance.
    :param node: The `repository` node being processed.
    """
