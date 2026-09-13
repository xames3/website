"""\
Author Directive
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February, 2025
Last updated on: 12 September, 2026

An `author` directive that renders the byline under a page title::

    .. author:: Akshay Mestry
       :avatar: https://example.com/avatar.png
       :target: https://github.com/xames3

The name is the argument. Anything left out falls back to the
`project` entry in `html_context`. The widget comes from
`author.html.jinja` and carries the page's reading time.

.. versionchanged:: 19.10.2025

    The author details are optional and fall back to the project
    details in `conf.py`.

.. deprecated:: 19.10.2025

    Removed the custom subject header in favour of the page title.

.. deprecated:: 15.01.2026

    Removed the email, bio and LinkedIn metadata.

.. versionchanged:: 24.04.2026

    The URL field is generic rather than GitHub-specific.

.. versionadded:: 27.06.2026

    Optional background images, which fade through behind the title.

.. versionchanged:: 10.9.2026

    [1] Rendering goes through `utils.render`, which has autoescaping
        on. The per-module templates it replaced had it off, so a name
        or avatar URL carrying an `&`, a `<` or a stray quote emitted
        broken markup.
    [2] The reading time is worked out at write time and rendered with
        the widget. It was counted in the browser before, so the same
        page had two counts that did not always agree.
    [3] `trail` returns the avatar, target and background URLs beside
        the node, where `linkcheck` can see them.

.. deprecated:: 10.9.2026

    [1] The module-level path fiddling has moved to `utils`, along with
        the `jinja2` import. `template` is now just the filename.
    [2] Dropped the empty `depart`. It existed only because `add_node`
        wants a pair; the theme falls back to the shared no-op in
        `utils` when a directive doesn't define one.
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import reading_time
from kaamiki.extensions.utils import render
from kaamiki.extensions.utils import trail

if t.TYPE_CHECKING:
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "author"
template: t.Final[str] = "author.html.jinja"


class node(nodes.Element):
    """The parsed directive, waiting for `visit` to write it out."""


class directive(rst.Directive):
    """The `author` directive.

    Options::

        - `avatar`: URL of the author's picture.
        - `target`: Where the name links to, a profile or a mailto.
        - `background`: One or more image URLs to fade through behind
          the title.

    .. deprecated:: 17.03.2026

        The `timestamp` option is gone; nothing rendered it.
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

        `html_context` is merged in behind the directive's own options,
        so a value written in the rST wins over the one in `conf.py`.

        :return: The node, followed by the `raw` nodes `trail` returns
            for the link checker.

        .. versionchanged:: 19.10.2025

            Values not given fall back to `html_context`.
        """
        self.options["name"] = self.arguments.pop().strip()
        ctx = self.state.document.settings.env.config.html_context
        self.options.update(ctx)
        element = node("\n".join(self.content), **self.options)
        return [element, *trail(self.options)]


def visit(self: HTMLTranslator, node: node) -> None:
    """Write the widget out when the HTML writer reaches the node.

    :param self: The HTML translator, whose body this appends to.
    :param node: The `author` node and its attributes.

    .. versionchanged:: 10.9.2026

        The reading time is worked out here rather than in the browser,
        so the page has one count instead of two.
    """
    attributes = dict(node.attributes)
    attributes["minutes"] = max(1, reading_time(node.document))
    self.body.append(render(template, **attributes))
