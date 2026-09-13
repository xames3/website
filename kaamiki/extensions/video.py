"""\
Video Directive
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February, 2025
Last updated on: 12 September, 2026

A `video` directive that embeds a video in the page::

    .. video:: https://www.w3schools.com/tags/movie.mp4
       :autoplay:

       A short clip.

The options and the content are rendered through `video.html.jinja`
and handed back as a raw node.

.. versionchanged:: 10.9.2026

    Rendering goes through `utils.render`, which has autoescaping on.
    The per-module templates it replaced had it off, so a caption
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

name: t.Final[str] = "video"
template: t.Final[str] = "video.html.jinja"


class directive(rst.Directive):
    """The `video` directive.

    Options::

        - `autoplay`: Play the video as soon as it loads.
        - `caption`: A line of text under the video.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        "autoplay": rst.directives.flag,
        "caption": rst.directives.unchanged,
    }

    def run(self) -> list[nodes.Node]:
        """Render the template and return it as a raw node.

        :return: A list holding the one `raw` node.

        .. versionchanged:: 10.9.2026

            [1] Renders through `utils.render`, so the caption is
                escaped on its way into the template instead of being
                dropped into the markup as-is.
            [2] The `raw` node carries the video URL as its `source`,
                which is where `linkcheck` looks. Every embed was being
                skipped by the link checker.
        """
        self.options["url"] = rst.directives.uri(self.arguments.pop().strip())
        self.options["caption"] = "\n".join(self.content).strip()
        attributes: dict[str, str] = {}
        attributes["source"] = self.options["url"]
        attributes["text"] = render(template, **self.options)
        attributes["format"] = "html"
        return [nodes.raw(**attributes)]
