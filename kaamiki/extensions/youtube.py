"""\
YouTube Directive
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February, 2025
Last updated on: 12 September, 2026

A `youtube` directive that embeds a video in the page::

    .. youtube:: https://www.youtube.com/watch?v=PhabJpIPONI
       :startfrom: 90
       :privacy:

       What it is about.

Both URL forms are accepted. The options become query parameters on the
embed URL, and the player comes from `youtube.html.jinja`.

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
import urllib.parse as urlparse

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import render

name: t.Final[str] = "youtube"
template: t.Final[str] = "youtube.html.jinja"


class directive(rst.Directive):
    """The `youtube` directive.

    Options::

        - `autoplay`: Play the video as soon as it loads.
        - `showcaptions`: Turn closed captions on.
        - `caption`: A line of text under the player.
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

        .. versionchanged:: 10.9.2026

            [1] Renders through `utils.render`, so the caption is
                escaped on its way into the template instead of being
                dropped into the markup as-is.
            [2] The `raw` node carries the video URL as its `source`,
                which is where `linkcheck` looks. Every embed was being
                skipped by the link checker.
        """
        vid = src = rst.directives.uri(self.arguments.pop().strip())
        if "youtu.be/" in src:
            vid = src.rsplit("/", 1)[-1].split("?", 1)[0]
        elif "watch?v=" in src:
            vid = src.split("v=", 1)[-1].split("&", 1)[0]
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
        self.options["caption"] = "\n".join(self.content).strip()
        attributes: dict[str, str] = {}
        attributes["source"] = src
        attributes["text"] = render(template, **self.options)
        attributes["format"] = "html"
        return [nodes.raw(**attributes)]
