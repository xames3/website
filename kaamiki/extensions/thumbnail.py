"""\
YouTube Thumbnail Directive
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 06 September 2025
Last updated on: 25 October 2026

A `thumbnail` directive that renders a YouTube video as a block::

    .. thumbnail:: https://www.youtube.com/watch?v=dQw4w9WgXcQ
        :title: Rick Rolled
        :greyscale:
"""

import typing as t
from urllib.parse import urlsplit

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import opens_new_tab
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import visitor
from kaamiki.extensions.utils import youtube_id

name: t.Final[str] = "thumbnail"
template: t.Final[str] = "directives/thumbnail.html.jinja"
TEXTS: t.Final[tuple[str, ...]] = ("title", "channel")


class node(nodes.Element):
    """The block and its parsed title and channel, waiting for `visit`."""


class directive(rst.Directive):
    """The `thumbnail` directive.

    Options::

        - `title`: The video's title.
        - `channel`: The channel's name.
        - `greyscale`: Draws the still in grey until it's hovered. It
          is drawn in colour without it.
        - `name`: A name to link to.
        - `class`: More classes for the block.
    """

    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "title": checks.text,
        "channel": checks.text,
        "greyscale": rst.directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the block's text and return its node.

        :return: The node, followed by the `raw` node `trail` returns
            for the link checker and anything the text reported.
        """
        src = self.arguments.pop().strip()
        vid = youtube_id(src)
        if vid is None:
            raise self.error(f"thumbnail: no YouTube video found in {src!r}")
        if not urlsplit(src).netloc:
            src = f"https://www.youtube.com/watch?v={vid}"
        config = self.state.document.settings.env.config
        texts = {_: self.options.pop(_) for _ in TEXTS if _ in self.options}
        self.options["classes"] = self.options.pop("class", [])
        self.options["src"] = src
        self.options["new_tab"] = opens_new_tab(src, config)
        self.options["greyscale"] = "greyscale" in self.options
        self.options["video_id"] = vid
        self.options["private"] = bool(setting(config, "youtube_privacy"))
        if not self.options["private"]:
            self.options["thumbnail"] = (
                # NOTE(xames3): YouTube doesn't document this URL, but it
                # has served stills this way for years.
                f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"
            )
        element = node("", **self.options)
        named(self, element)
        messages: list[nodes.Node] = []
        for field, text in texts.items():
            parsed, reported = parse(self, text, field)
            element.append(parsed)
            messages.extend(reported)
        return [element, *trail(self.options, ("src",)), *messages]


visit = visitor(template)
