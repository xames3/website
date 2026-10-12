"""\
YouTube Thumbnail Directive
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 06 September 2025
Last updated on: 09 October 2026

A `thumbnail` directive that renders a YouTube video as a card::

    .. thumbnail:: https://www.youtube.com/watch?v=dQw4w9WgXcQ
        :title: Rick Rolled
        :grayscale:
"""

from __future__ import annotations

import typing as t
from urllib.parse import urlsplit

import docutils.nodes as nodes
import docutils.parsers.rst as rst

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
    """The card and its parsed title and channel, waiting for `visit`."""


class directive(rst.Directive):
    """The `thumbnail` directive.

    Options::

        - `title`: User-provided YouTube video title.
        - `channel`: User-provided YouTube video channel name.
        - `grayscale`: Draws the still in grey until it's hovered.
    """

    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        "title": rst.directives.unchanged_required,
        "channel": rst.directives.unchanged_required,
        "grayscale": rst.directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the card's text and return its node.

        :return: The node, followed by the `raw` node `trail` returns
            for the link checker and anything the text reported.
        """
        src = rst.directives.uri(self.arguments.pop().strip())
        vid = youtube_id(src)
        if vid is None:
            raise self.error(f"thumbnail found no YouTube video in {src!r}")
        if not urlsplit(src).netloc:
            src = f"https://www.youtube.com/watch?v={vid}"
        config = self.state.document.settings.env.config
        texts = {_: self.options.pop(_) for _ in TEXTS if _ in self.options}
        self.options["src"] = src
        self.options["new_tab"] = opens_new_tab(src, config)
        grayscale = setting(config, "thumbnail_grayscale")
        if "grayscale" in self.options:
            grayscale = not grayscale
        self.options["grayscale"] = grayscale
        self.options["video_id"] = vid
        self.options["thumbnail"] = (
            # NOTE(xames3): YouTube doesn't document this URL, but it
            # has served stills this way for years.
            f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"
        )
        element = node("", **self.options)
        messages: list[nodes.Node] = []
        for field, text in texts.items():
            parsed, reported = parse(self, text, field)
            element.append(parsed)
            messages.extend(reported)
        return [element, *trail(self.options, ("src",)), *messages]


visit = visitor(template)
