"""\
Video Directive
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February, 2025
Last updated on: 29 September, 2026

A `video` directive that embeds a video in the page::

    .. video:: https://www.w3schools.com/tags/movie.mp4
       :autoplay:

       A short clip.

The options and the content are rendered through `video.html.jinja`
and handed back as a raw node.
"""

from __future__ import annotations

import mimetypes
import typing as t
from urllib.parse import urlsplit

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import render

name: t.Final[str] = "video"
template: t.Final[str] = "video.html.jinja"


class directive(rst.Directive):
    """The `video` directive.

    Options::

        - `autoplay`: Play the video, muted, as soon as it loads.
        - `caption`: A line of text under the video. The directive's
          body does the same and the option wins when both are there.
        - `type`: The video's MIME type, when its extension does not
          say.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        "autoplay": rst.directives.flag,
        "caption": rst.directives.unchanged,
        "type": rst.directives.unchanged,
    }

    def run(self) -> list[nodes.Node]:
        """Render the template and return it as a raw node.

        :return: A list holding the one `raw` node.
        """
        url = rst.directives.uri(self.arguments.pop().strip())
        guessed, _ = mimetypes.guess_type(urlsplit(url).path)
        self.options["url"] = url
        self.options["autoplay"] = "autoplay" in self.options
        self.options["type"] = self.options.get("type") or guessed or ""
        self.options["caption"] = (
            self.options.get("caption") or "\n".join(self.content)
        ).strip()
        attributes: dict[str, str] = {}
        attributes["source"] = self.options["url"]
        attributes["text"] = render(template, **self.options)
        attributes["format"] = "html"
        return [nodes.raw(**attributes)]
