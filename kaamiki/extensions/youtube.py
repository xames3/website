"""\
YouTube Directive
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February, 2025
Last updated on: 30 September, 2026

A `youtube` directive that embeds a video in the page::

    .. youtube:: https://www.youtube.com/watch?v=PhabJpIPONI
       :startfrom: 90
       :privacy:

       What it is about.

Both URL forms are accepted. The options become query parameters on the
embed URL and the player comes from `youtube.html.jinja`.
"""

from __future__ import annotations

import typing as t
import urllib.parse as urlparse

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import render
from kaamiki.extensions.utils import youtube_id

name: t.Final[str] = "youtube"
template: t.Final[str] = "youtube.html.jinja"


class directive(rst.Directive):
    """The `youtube` directive.

    Options::

        - `autoplay`: Play the video as soon as it loads.
        - `showcaptions`: Turn closed captions on.
        - `caption`: A line of text under the player. The directive's
           body does the same and the option wins when both are
           there.
        - `startfrom`: Seconds to start playing from.
        - `privacy`: Embed from `youtube-nocookie.com`.
        - `modestbranding`: Kept for older pages; always on now.
        - `controls`: `0` hides the player controls.
        - `playsinline`: Kept for older pages; always on now.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        "autoplay": rst.directives.flag,
        "showcaptions": rst.directives.flag,
        "caption": rst.directives.unchanged,
        "startfrom": rst.directives.positive_int,
        "privacy": rst.directives.flag,
        "modestbranding": rst.directives.flag,
        "controls": rst.directives.nonnegative_int,
        "playsinline": rst.directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        """Build the embed URL and return the player as a raw node.

        :return: A list holding the one `raw` node.
        """
        src = rst.directives.uri(self.arguments.pop().strip())
        vid = youtube_id(src)
        if vid is None:
            raise self.error(f"youtube found no video in {src!r}")
        domain = (
            "https://www.youtube-nocookie.com"
            if "privacy" in self.options
            else "https://www.youtube.com"
        )
        params = {
            "start": self.options.get("startfrom", 0),
            "autoplay": 1 if "autoplay" in self.options else 0,
            "cc_load_policy": 1 if "showcaptions" in self.options else 0,
            "modestbranding": 1,
            "rel": 0,
            "playsinline": 1,
        }
        if "controls" in self.options:
            params["controls"] = int(self.options["controls"])
        url = f"{domain}/embed/{vid}?{urlparse.urlencode(params)}"
        self.options["url"] = url
        self.options["caption"] = (
            self.options.get("caption") or "\n".join(self.content)
        ).strip()
        attributes: dict[str, str] = {}
        attributes["source"] = src
        attributes["text"] = render(template, **self.options)
        attributes["format"] = "html"
        return [nodes.raw(**attributes)]
