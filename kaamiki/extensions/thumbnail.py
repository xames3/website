"""\
YouTube Thumbnail Directive
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 06 September 2025
Last updated on: 15 November 2026

A `thumbnail` directive that shows a YouTube video's still and links to it::

    .. thumbnail:: https://www.youtube.com/watch?v=jNQXAC9IVRw
       :title: Me at the zoo
       :greyscale:
"""

from __future__ import annotations

import typing as t
from urllib.parse import urlsplit

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.roles import steady
from kaamiki.extensions.utils import KaamikiDirective
from kaamiki.extensions.utils import Option
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import opens_new_tab
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import phrase
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import unlinked
from kaamiki.extensions.utils import worded
from kaamiki.extensions.utils import youtube_id
from kaamiki.extensions.utils import youtube_still

template: t.Final[str] = "directives/thumbnail.html.jinja"
TEXTS: t.Final[tuple[str, ...]] = ("title", "channel", "caption")


class Thumbnail(KaamikiDirective):
    """The `thumbnail` directive.

    The argument is the link of a YouTube video, or only its id. The
    thumbnail links to the link as written, so it must be an `http` or
    `https` link. When the thumbnail does not have the title or the
    channel, the script of the page gets them from YouTube. Until they
    arrive, or when they do not arrive, the thumbnail shows "YouTube
    video" and "Watch on YouTube". The link checker gets the picture of
    the video, so `linkcheck` fails and names a video that is deleted or
    private. `kaamiki.conf.youtube.privacy` of the site is for players,
    so it does not change the thumbnail.

    Options::

        - `title`: The title of the video.
        - `channel`: The name of the channel.
        - `caption`: A line of text below the channel, parsed as rST.
        - `greyscale`: Show the still in grey until a reader hovers on
          it. Without it, the still shows in colour.
        - `name`: A name for links.
        - `class`: More classes for the thumbnail.
    """

    required_arguments = 1
    final_argument_whitespace = False
    title = Option(checks.text)
    channel = Option(checks.text)
    caption = Option(checks.text)
    greyscale = Option(rst.directives.flag)

    class Node(nodes.Element):
        """The thumbnail and its parsed text, which `visit` writes."""

    def build(self) -> list[nodes.Node]:
        """Make the node of the thumbnail with its parsed text.

        :return: The node, the `raw` node from `trail` for the link
            checker and what the parser reported.
        """
        src = self.arguments.pop().strip()
        vid = youtube_id(src)
        if vid is None:
            self.fail(f"expected a YouTube video link or id, got {src!r}")
        try:
            checks.link(src, schemes=("http", "https"))
        except ValueError as error:
            self.fail(str(error))
        if not urlsplit(src).netloc:
            src = f"https://www.youtube.com/watch?v={vid}"
        options = self.options
        texts = {each: options.pop(each) for each in TEXTS if each in options}
        options["greyscale"] = self.greyscale
        options["classes"] = options.pop("class", [])
        options["src"] = src
        options["new_tab"] = opens_new_tab(src, self.config)
        options["video_id"] = vid
        options["thumbnail"] = youtube_still(vid)
        node = self.locate(self.Node("", **options))
        self.add_name(node)
        messages: list[nodes.Node] = []
        for field, written in texts.items():
            parsed, reported = parse(self, written, field)
            unlinked(self, parsed, f"a {field}")
            worded(self, parsed, f"a {field}")
            steady(
                self,
                parsed,
                f"a {field}",
                "which the script doesn't run inside a link",
            )
            node.append(parsed)
            messages.extend(reported)
        return [node, *trail(self, options, ("thumbnail",)), *messages]

    @staticmethod
    def plain(node: Thumbnail.Node) -> list[nodes.Node]:
        """Write a thumbnail as words, for a builder that writes no HTML.

        :param node: The thumbnail's node.
        :return: A paragraph for each text and a paragraph with a link
            to the video.
        """
        found: list[nodes.Node] = [
            nodes.paragraph("", "", *each.children)
            for each in node.children
            if isinstance(each, phrase)
        ]
        link = nodes.reference("", node["src"], refuri=node["src"])
        return [*found, nodes.paragraph("", "", link)]


html.draws(Thumbnail.Node, template)
