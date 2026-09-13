"""\
YouTube Thumbnail Directive
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 06 September, 2025
Last updated on: 12 September, 2026

A `thumbnail` directive that renders a YouTube video as a card::

    .. thumbnail:: https://www.youtube.com/watch?v=dQw4w9WgXcQ

Both URL forms are accepted. The video id is pulled out of the URL and
used to build the still image, and the card itself comes from
`thumbnail.html.jinja`.

.. versionchanged:: 10.9.2026

    Rendering goes through `utils.render`, which has autoescaping on.
    The per-module templates it replaced had it off, so a video title
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

name: t.Final[str] = "thumbnail"
template: t.Final[str] = "thumbnail.html.jinja"


class directive(rst.Directive):
    """The `thumbnail` directive. It takes no options."""

    required_arguments = 1
    final_argument_whitespace = False

    def run(self) -> list[nodes.Node]:
        """Render the card and return it as a raw node.

        :return: A list holding the one `raw` node.

        .. deprecated:: 8.9.2025

            Stopped scraping YouTube with `requests` and
            `BeautifulSoup`. It broke whenever YouTube changed its
            markup and made builds very slow. The metadata comes from
            YouTube's oEmbed endpoint instead.

        .. versionchanged:: 10.9.2026

            [1] Renders through `utils.render`, so the video title is
                escaped on its way into the template instead of being
                dropped into the markup as-is.
            [2] The `raw` node carries the video URL as its `source`,
                which is where `linkcheck` looks. Every video on the
                page was being skipped by the link checker.
        """
        vid = src = rst.directives.uri(self.arguments.pop().strip())
        if "youtu.be/" in src:
            vid = src.rsplit("/", 1)[-1].split("?", 1)[0]
        elif "watch?v=" in src:
            vid = src.split("v=", 1)[-1].split("&", 1)[0]
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
