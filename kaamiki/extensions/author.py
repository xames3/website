"""\
Author Directive
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February, 2025
Last updated on: 27 June, 2026

This module defines a custom `author` directive for the Kaamiki Sphinx
Theme. The directive allows embedding details directly within the
document.

The `author` directive is designed to extend reStructuredText (rST)
capabilities by injecting structured metadata about the content, which
can be styled or processed further using Jinja2 templates.

The `author` directive can be used in reStructuredText documents as
follows::

    .. code-block:: rst

        .. author:: Akshay Mestry
            :avatar: https://example.com/avatar.png
            :target: https://github.com/xames3

The above snippet will be processed and rendered according to the
theme's Jinja2 template, producing a final HTML output.

.. versionchanged:: 19.10.2025

    The options `author`, `email`, and `github` are now optional and can
    default to project's details specified in `conf.py`.

.. deprecated:: 19.10.2025

    Removed the custom subject header in favour of page title.

.. deprecated:: 15.01.2026

    Removed usage of Email, Bio, and LinkedIn metadata.

.. versionchanged:: 24.04.2026

    URL field is now generic and not specific to GitHub.

.. versionadded:: 27.06.2026

    Directive now supports optional background(s) which fades through
    the title/author section.
"""

from __future__ import annotations

import os.path as p
import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst
import jinja2

if t.TYPE_CHECKING:
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "author"
here: str = p.dirname(__file__)
templates: str = "../base/templates"
html = p.join(p.abspath(p.join(here, templates)), "author.html.jinja")

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
    """Custom `author` directive for reStructuredText.

    This class defines the behaviour of the `author` directive,
    including how it processes options and content, and how it generates
    nodes to be inserted into the document tree.

    The directive supports the following options::

        - `avatar`: A URL to the author's avatar image.
        - `target`: Author's link (profile, portfolio, or mailto etc.).

    .. versionchanged:: 19.10.2025

        The options `author`, `email`, and `github` are now optional
        and can default to project's details specified in `conf.py`.

    .. deprecated:: 17.03.2026

        The `timestamp` option is now deprecated as it's not being
        rendered.

    .. versionchanged:: 24.04.2026

        URL field is now generic and not specific to GitHub.

    .. versionadded:: 27.06.2026

        Directive now supports optional background(s) which fades
        through the title/author section.
    """

    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {  # noqa: RUF012
        "avatar": rst.directives.uri,
        "target": rst.directives.uri,
        "background": rst.directives.unchanged,
    }

    def run(self) -> list[nodes.Node]:
        """Parse directive options and create an `author` node.

        This method gathers all options provided by the user (if any) in
        the `author` directive, constructs a new `node` instance, and
        returns it wrapped in a list.

        The returned node is then placed into the document tree at the
        directive's location. Further processing will convert the node
        into HTML or other formats.

        :return: A list containing a single `node` element.

        .. versionchanged:: 19.10.2025

            Added support for default context variables picked from
            the `html_context` object in `conf.py`.

        .. note::

            The `option_spec` will take precedence over the
            `html_context` values.
        """
        self.options["name"] = self.arguments.pop().strip()
        ctx = self.state.document.settings.env.config.html_context
        self.options.update(ctx)
        element = node("\n".join(self.content), **self.options)
        return [element]


def visit(self: HTMLTranslator, node: node) -> None:
    """Handle the entry processing of the `author` node during HTML
    generation.

    This method is called when the HTML translator encounters the
    `author` node in the document tree. It retrieves the relevant
    attributes from the node (if any) and uses Jinja2 templating to
    produce the final HTML output.

    :param self: The HTML translator instance responsible for rendering
        nodes into HTML.
    :param node: The `author` node containing parsed attributes.

    """
    self.body.append(template.render(**node.attributes))


def depart(self: HTMLTranslator, node: node) -> None:
    """Handle the exit processing of the `author` node during HTML
    generation.

    This method is invoked after the node's HTML representation has been
    fully processed and added to the output. Since the `author` node
    does not require any closing actions, the method currently acts as a
    placeholder.

    :param self: The HTML translator instance.
    :param node: The `author` node being processed.
    """
