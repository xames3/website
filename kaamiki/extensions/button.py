"""\
Button Directive
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 29 April, 2026
Last updated on: 12 September, 2026

A `button` directive that renders a link as a button::

    .. button:: https://www.w3schools.com/tags/movie.mp4
       :fa-icon: video
       :scheme: primary

       Watch it here!

The content is the label. The markup comes from `button.html.jinja`.

.. versionchanged:: 10.9.2026

    Rendering goes through `utils.render`, which has autoescaping on.
    The per-module templates it replaced had it off, so a label
    carrying an `&`, a `<` or a stray quote emitted broken markup.

.. deprecated:: 10.9.2026

    [1] The module-level path fiddling has moved to `utils`, along with
        the `jinja2` import. `template` is now just the filename.
    [2] Dropped the `node` class and the `visit`/`depart` pair. This
        directive hands back a `nodes.raw` and never reaches a
        translator, so all three only existed to keep the registration
        loop happy.
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import render

name: t.Final[str] = "button"
template: t.Final[str] = "button.html.jinja"
SCHEMES: t.Final[tuple[str, str]] = ("primary", "secondary")


def scheme(argument: str) -> str:
    """Check the `scheme` option against the two allowed values.

    :param argument: The value written in the rST.
    :return: The value, once it is known to be one of the schemes.

    .. versionchanged:: 10.9.2026

        `docutils` is untyped, so the choice comes back as `Any`. The
        cast marks that boundary.
    """
    return rst.directives.choice(argument, SCHEMES)


class directive(rst.Directive):
    """The `button` directive.

    Options::

        - `fa-icon`: A Font Awesome icon name, without its style.
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

        .. versionchanged:: 10.9.2026

            [1] Renders through `utils.render`, so the label is escaped
                on its way into the template instead of being dropped
                into the markup as-is.
            [2] The `raw` node carries the button's URL as its
                `source`, which is where `linkcheck` looks. Every
                button was being skipped by the link checker.
        """
        self.assert_has_content()
        self.options["url"] = rst.directives.uri(self.arguments.pop().strip())
        self.options["faicon"] = self.options.pop("fa-icon", None)
        self.options["text"] = "\n".join(self.content).strip()
        attributes: dict[str, str] = {}
        attributes["source"] = self.options["url"]
        attributes["text"] = render(template, **self.options)
        attributes["format"] = "html"
        return [nodes.raw(**attributes)]
