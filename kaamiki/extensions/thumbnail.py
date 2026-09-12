"""\
YouTube Thumbnail Directive
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 06 September, 2025
Last updated on: 11 September, 2026

This module defines a custom `thumbnail` directive for the Kaamiki
Sphinx Theme. The directive allows embedding a YouTube video thumbnail
card directly within the document.

The `thumbnail` directive is designed to extend reStructuredText (rST)
capabilities by fetching metadata from a YouTube URL and rendering a
styled card.

The `thumbnail` directive can be used in reStructuredText documents as
follows::

    .. thumbnail:: https://www.youtube.com/watch?v=dQw4w9WgXcQ

The above snippet will be processed and rendered according to the
theme's Jinja2 template, producing a final HTML output.

.. versionchanged:: 10.9.2026

    Rendering goes through `utils.render`, one shared Jinja environment
    for the whole theme with autoescaping switched on. The old per-
    module templates had escaping off, so a video title carrying an `&`,
    a `<` or a stray quote quietly emitted broken markup.

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

name: t.Final[str] = "thumbnail"
template: t.Final[str] = "thumbnail.html.jinja"


class directive(rst.Directive):
    """Custom `thumbnail` directive for reStructuredText.

    This class defines the behaviour of the `thumbnail` directive,
    including how it processes options and content and how it
    generates nodes to be inserted into the document tree.
    """

    required_arguments = 1
    final_argument_whitespace = False

    def run(self) -> list[nodes.Node]:
        """Parse directive options and create an `thumbnail` node.

        This method gathers all options provided by the user (if any)
        in the `thumbnail` directive, constructs a new `node` instance,
        and returns it wrapped in a list.

        The returned node is then placed into the document tree at the
        directive's location. Further processing will convert the node
        into HTML or other formats.

        :return: A list containing a single `node` element.

        .. deprecated:: 8.9.2025

            [1] Deprecated using `requests` and `BeautifulSoup` for
                fetching and parsing YouTube metadata. This approach was
                unreliable due to frequent changes in YouTube's HTML
                structure and super long build times.
            [2] The directive now uses YouTube's oEmbed endpoint to
                fetch video metadata in a more stable and efficient
                manner.

        .. versionchanged:: 10.9.2026

            Renders through `utils.render`, so the video title is
            escaped on its way into the template instead of being
            dropped into the markup as-is.

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
        attributes["text"] = render(template, **self.options)
        attributes["format"] = "html"
        return [nodes.raw(**attributes)]
