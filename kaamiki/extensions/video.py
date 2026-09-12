"""\
Video Directive
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February, 2025
Last updated on: 10 September, 2026

This module defines a custom `video` directive for the Kaamiki Sphinx
Theme. The directive allows embedding a video directly within the
document.

The `video` directive is designed to extend reStructuredText (rST)
capabilities by injecting structured metadata about the content, which
can be styled or processed further using Jinja2 templates.

The `video` directive can be used in reStructuredText documents as
follows::

    .. code-block:: rst

        .. video:: https://www.w3schools.com/tags/movie.mp4

The above snippet will be processed and rendered according to the
theme's Jinja2 template, producing a final HTML output.

.. versionchanged:: 10.9.2026

    Rendering goes through `utils.render`, one shared Jinja environment
    for the whole theme with autoescaping switched on. The old per-
    module templates had escaping off, so a caption carrying an `&`, a
    `<` or a stray quote quietly emitted broken markup.

.. deprecated:: 10.9.2026

    [1] The module-level `here`, `templates` and `html` path fiddling
        has moved out to `utils`, along with the `jinja2` import. Every
        directive was opening its own template at import time and
        building a bare `jinja2.Template` off it, which is a daft thing
        to do seven times over. `template` is now just the filename.
    [2] Dropped the `node` class and the `visit`/`depart` pair. This
        directive hands back a `nodes.raw` and never goes anywhere near
        a translator, so all three were dead weight that only existed to
        keep the registration loop happy.
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import render

name: t.Final[str] = "video"
template: t.Final[str] = "video.html.jinja"


class directive(rst.Directive):
    """Custom `video` directive for reStructuredText.

    This class defines the behaviour of the `video` directive, including
    how it processes options and content and how it generates nodes to
    be inserted into the document tree.

    The directive supports the following options::

        - `autoplay`: Boolean flag to autoplay the video on load.
        - `caption`: Video caption.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        "autoplay": rst.directives.flag,
        "caption": rst.directives.unchanged,
    }

    def run(self) -> list[nodes.Node]:
        """Parse directive options and create an `video` node.

        This method gathers all options provided by the user (if any)
        in the `video` directive, constructs a new `node` instance and
        returns it wrapped in a list.

        The returned node is then placed into the document tree at the
        directive's location. Further processing will convert the node
        into HTML or other formats.

        :return: A list containing a single `node` element.

        .. versionchanged:: 10.9.2026

            Renders through `utils.render`, so the caption is escaped on
            its way into the template instead of being dropped into the
            markup as-is.

        """
        self.options["url"] = rst.directives.uri(self.arguments.pop().strip())
        self.options["caption"] = "\n".join(self.content).strip()
        attributes: dict[str, str] = {}
        attributes["text"] = render(template, **self.options)
        attributes["format"] = "html"
        return [nodes.raw(**attributes)]
