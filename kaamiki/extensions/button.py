"""\
Button Directive
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 29 April, 2026
Last updated on: 29 September, 2026

A `button` directive that renders a link as a button::

    .. button:: https://www.w3schools.com/tags/movie.mp4
       :fa-icon: video
       :scheme: primary

       Watch it here!

The content is the label. The markup comes from `button.html.jinja`.
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import elsewhere
from kaamiki.extensions.utils import icon
from kaamiki.extensions.utils import render

name: t.Final[str] = "button"
template: t.Final[str] = "button.html.jinja"
SCHEMES: t.Final[tuple[str, str]] = ("primary", "secondary")


def scheme(argument: str) -> str:
    """Check the `scheme` option against the two allowed values.

    :param argument: The value written in the rST.
    :return: The value, once it is known to be one of the schemes.

    """
    return rst.directives.choice(argument, SCHEMES)


class directive(rst.Directive):
    """The `button` directive.

    Options::

        - `fa-icon`: A Font Awesome icon, as `video`, `fa-video` or
          `far fa-video`. One without a style is drawn solid.
        - `scheme`: `primary` or `secondary`.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        "fa-icon": rst.directives.unchanged,
        "scheme": scheme,
    }

    def run(self) -> list[nodes.Node]:
        """Render the button and return it as a raw node.

        :return: A list holding the one `raw` node.
        """
        self.assert_has_content()
        config = self.state.document.settings.env.config
        self.options["url"] = rst.directives.uri(self.arguments.pop().strip())
        self.options["faicon"] = icon(self.options.pop("fa-icon", None))
        self.options["text"] = "\n".join(self.content).strip()
        self.options["new_tab"] = elsewhere(
            self.options["url"], config.html_baseurl
        ) and config.html_context.get("km_open_links_in_new_tab", True)
        attributes: dict[str, str] = {}
        attributes["source"] = self.options["url"]
        attributes["text"] = render(template, **self.options)
        attributes["format"] = "html"
        return [nodes.raw(**attributes)]
