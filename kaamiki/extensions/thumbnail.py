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
from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import located
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import opens_new_tab
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import phrase
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import unlinked
from kaamiki.extensions.utils import worded
from kaamiki.extensions.utils import youtube_id
from kaamiki.extensions.utils import youtube_still

name: t.Final[str] = "thumbnail"
template: t.Final[str] = "directives/thumbnail.html.jinja"
TEXTS: t.Final[tuple[str, ...]] = ("title", "channel", "caption")


class Thumbnail(nodes.Element):
    """The thumbnail and its parsed text, waiting for `visit`."""


class directive(rst.Directive):
    """The `thumbnail` directive.

    The argument is a YouTube video link or just its id. The thumbnail
    links to a link as it's written, so it has to be an `http` or an
    `https` one. The page's script asks YouTube for the title and the
    channel of any the thumbnail isn't given, and the thumbnail shows
    "YouTube video" and "Watch on YouTube" until they arrive or when
    they don't. The link checker is given the video's picture, so
    `linkcheck` fails and names a video that's been deleted or made
    private.
    The site's `kaamiki.conf.youtube.privacy` is for players, so it
    changes nothing here.

    Options::

        - `title`: The video's title.
        - `channel`: The channel's name.
        - `caption`: A line of text under the channel, parsed as rST.
        - `greyscale`: Draw the still in grey until it's hovered. It's
          drawn in colour without it.
        - `name`: A name to link to.
        - `class`: More classes for the thumbnail.
    """

    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "title": checks.text,
        "channel": checks.text,
        "caption": checks.text,
        "greyscale": rst.directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the thumbnail's text and return its node.

        :return: The node, followed by the `raw` node `trail` returns
            for the link checker and anything the text reported.
        """
        src = self.arguments.pop().strip()
        vid = youtube_id(src)
        if vid is None:
            raise self.error(
                f"thumbnail: expected a YouTube video link or id, got {src!r}"
            )
        try:
            checks.link(src, schemes=("http", "https"))
        except ValueError as error:
            raise self.error(f"thumbnail: {error}") from error
        if not urlsplit(src).netloc:
            src = f"https://www.youtube.com/watch?v={vid}"
        config = self.state.document.settings.env.config
        texts = {_: self.options.pop(_) for _ in TEXTS if _ in self.options}
        self.options["classes"] = self.options.pop("class", [])
        self.options["src"] = src
        self.options["new_tab"] = opens_new_tab(src, config)
        self.options["greyscale"] = "greyscale" in self.options
        self.options["video_id"] = vid
        self.options["thumbnail"] = youtube_still(vid)
        element = located(self, Thumbnail("", **self.options))
        named(self, element)
        messages: list[nodes.Node] = []
        for field, text in texts.items():
            parsed, reported = parse(self, text, field)
            unlinked(self, parsed, f"a {field}")
            worded(self, parsed, f"a {field}")
            steady(
                self,
                parsed,
                f"a {field}",
                "which the script doesn't run inside a link",
            )
            element.append(parsed)
            messages.extend(reported)
        return [element, *trail(self, self.options, ("thumbnail",)), *messages]


def plain(node: Thumbnail) -> list[nodes.Node]:
    """Write a thumbnail as words, for a builder that draws no HTML.

    :param node: The thumbnail's node.
    :return: A paragraph for each text it has and one with the video's
        address, written as a link to itself.
    """
    found: list[nodes.Node] = [
        nodes.paragraph("", "", *_.children)
        for _ in node.children
        if isinstance(_, phrase)
    ]
    link = nodes.reference("", node["src"], refuri=node["src"])
    return [*found, nodes.paragraph("", "", link)]


html.draws(Thumbnail, template)


node = Thumbnail
