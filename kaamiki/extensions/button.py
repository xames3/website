"""\
Button Directive
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 29 April, 2026
Last updated on: 12 June, 2026

This module defines a custom `button` directive for the Kaamiki Sphinx
Theme. The directive allows adding a button directly within the
document.

The `button` directive is designed to extend reStructuredText (rST)
capabilities by injecting structured metadata about the content, which
can be styled or processed further using Jinja2 templates.

The `button` directive can be used in reStructuredText documents as
follows::

    .. code-block:: rst

        .. button:: https://www.w3schools.com/tags/movie.mp4
            :fa-icon: video
            :scheme: primary

            Watch it here!

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

name: t.Final[str] = "button"
here: str = p.dirname(__file__)
templates: str = "../base/templates"
html = p.join(p.abspath(p.join(here, templates)), "button.html.jinja")

with open(html) as f:
    template = jinja2.Template(f.read())


def scheme(argument: str) -> str:
    """Validate scheme choice."""
    return rst.directives.choice(argument, ("primary", "secondary"))


class node(nodes.Element):
    """Class to represent a custom node in the document tree.

    This class extends the `nodes.Element` from `docutils`, serving as
    the container for the parsed information. The node will ultimately
    be transformed into HTML or other output formats by the relevant
    Sphinx translators.
    """


class directive(rst.Directive):
    """Custom `button` directive for reStructuredText.

    This class defines the behaviour of the `button` directive, including
    how it processes options and content, and how it generates nodes to
    be inserted into the document tree.

    The directive supports the following options::

        - `fa-icon`: Optional FontAwesome icon
        - `scheme`: Default colour scheme for the button
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        "fa-icon": rst.directives.unchanged,
        "scheme": scheme,
    }

    def run(self) -> list[nodes.Node]:
        """Parse directive options and create an `button` node.

        This method gathers all options provided by the user (if any) in
        the `button` directive, constructs a new `node` instance, and
        returns it wrapped in a list.

        The returned node is then placed into the document tree at the
        directive's location. Further processing will convert the node
        into HTML or other formats.

        :return: A list containing a single `node` element.
        """
        self.assert_has_content()
        self.options["url"] = rst.directives.uri(self.arguments.pop().strip())
        self.options["faicon"] = self.options.pop("fa-icon", None)
        self.options["text"] = "\n".join(self.content).strip()
        attributes: dict[str, str] = {}
        attributes["text"] = template.render(**self.options)
        attributes["format"] = "html"
        return [nodes.raw(**attributes)]


def visit(self: HTMLTranslator, node: node) -> None:
    """Handle the entry processing of the `button` node during HTML
    generation.

    This method is called when the HTML translator encounters the
    `button` node in the document tree. It retrieves the relevant
    attributes from the node (if any) and uses Jinja2 templating to
    produce the final HTML output. Since the `button` node does not
    require any actions, the method currently acts as a placeholder.

    :param self: The HTML translator instance.
    :param node: The `button` node being processed.
    """


def depart(self: HTMLTranslator, node: node) -> None:
    """Handle the exit processing of the `button` node during HTML
    generation.

    This method is invoked after the node's HTML representation has been
    fully processed and added to the output. Since the `button` node
    does not require any closing actions, the method currently acts as a
    placeholder.

    :param self: The HTML translator instance.
    :param node: The `button` node being processed.
    """
