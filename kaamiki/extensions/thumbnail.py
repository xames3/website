"""\
YouTube Thumbnail Directive
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 06 September, 2025
Last updated on: 29 September, 2026

A `thumbnail` directive that renders a YouTube video as a card::

    .. thumbnail:: https://www.youtube.com/watch?v=dQw4w9WgXcQ

Both URL forms are accepted. The video id is pulled out of the URL and
used to build the still image and the card itself comes from
`thumbnail.html.jinja`.
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import render
from kaamiki.extensions.utils import youtube_id

name: t.Final[str] = "thumbnail"
template: t.Final[str] = "thumbnail.html.jinja"


class directive(rst.Directive):
    """The `thumbnail` directive.

    `:title:` and `:channel:` write the card's text into the page. Left
    out, the card reads "YouTube Video" until the script fetches the
    real ones, which it cannot do for a video YouTube has taken down.
    """

    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        "title": rst.directives.unchanged_required,
        "channel": rst.directives.unchanged_required,
    }

    def run(self) -> list[nodes.Node]:
        """Render the card and return it as a raw node.

        :return: A list holding the one `raw` node.
        """
        src = rst.directives.uri(self.arguments.pop().strip())
        vid = youtube_id(src)
        if vid is None:
            raise self.error(f"thumbnail found no YouTube video in {src!r}")
        self.options["src"] = src
        self.options["video_id"] = vid
        self.options["thumbnail"] = (
            f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"
        )
        attributes: dict[str, str] = {}
        attributes["source"] = src
        attributes["text"] = render(template, **self.options)
        attributes["format"] = "html"
        return [nodes.raw(**attributes)]
