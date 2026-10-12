"""\
Video Directive
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February 2025
Last updated on: 08 October 2026

A `video` directive that embeds a video in the page::

    .. video:: https://www.w3schools.com/tags/movie.mp4
       :autoplay:

       A short clip.

The caption is parsed as rST. More sources, a poster and captions
go in options::

    .. video:: /_static/clip.mp4
       :sources: /_static/clip.webm
       :poster: /_static/clip.png
       :track: en=/_static/clip.en.vtt, hi=/_static/clip.hi.vtt
"""

from __future__ import annotations

import mimetypes
import typing as t
from urllib.parse import urlsplit

import docutils.nodes as nodes
import docutils.parsers.rst as rst
from babel import Locale
from babel.core import UnknownLocaleError

from kaamiki.extensions.utils import listed
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import toggle
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import visitor

name: t.Final[str] = "video"
template: t.Final[str] = "directives/video.html.jinja"
PRELOAD: t.Final[tuple[str, ...]] = ("none", "metadata", "auto")


def preload(argument: str) -> str:
    """Check the `preload` option against the values a browser knows.

    :param argument: The value written in the rST.
    :return: The value, once it's known to be one of them.
    """
    return rst.directives.choice(argument, PRELOAD)


def language(code: str) -> str:
    """Name a language in itself, `en` as `English`.

    :param code: The language code, as in `en` or `pt-BR`.
    :return: The name or the code when Babel doesn't know it.
    """
    locale = code.replace("-", "_")
    try:
        return Locale.parse(locale).get_display_name(locale) or code
    except ValueError, UnknownLocaleError:
        return code


class node(nodes.Element):
    """The video and its parsed caption, waiting for `visit`."""


class directive(rst.Directive):
    """The `video` directive.

    Options::

        - `autoplay`: Play the video, muted, as soon as it loads.
        - `caption`: A line of text under the video. It wins over the
          directive's body.
        - `type`: The video's MIME type, when its extension doesn't
          say.
        - `sources`: More files of the same video, comma-separated, for
          browsers that can't play the first.
        - `poster`: The picture shown until the video plays.
        - `preload`: How much the browser fetches ahead: `none`,
          `metadata` or `auto`.
        - `loop`: Play it over and over.
        - `muted`: Start with the sound off.
        - `controls`: `false` hides the player controls.
        - `track`: Captions, as `language=file` and comma-separated.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        "autoplay": rst.directives.flag,
        "caption": rst.directives.unchanged,
        "type": rst.directives.unchanged,
        "sources": rst.directives.unchanged_required,
        "poster": rst.directives.uri,
        "preload": preload,
        "loop": rst.directives.flag,
        "muted": rst.directives.flag,
        "controls": toggle,
        "track": rst.directives.unchanged_required,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the caption and return the video's node.

        :return: The node, followed by the `raw` node `trail` returns
            for the link checker and anything the caption reported.
        """
        url = rst.directives.uri(self.arguments.pop().strip())
        guessed, _ = mimetypes.guess_type(urlsplit(url).path)
        kind = self.options.pop("type", None) or guessed or ""
        sources = [{"url": url, "type": kind}]
        for more in listed(self.options.pop("sources", None)):
            guess, _ = mimetypes.guess_type(urlsplit(more).path)
            sources.append({"url": more, "type": guess or ""})
        tracks: list[dict[str, str]] = []
        for entry in listed(self.options.pop("track", None)):
            code, found, file = (_.strip() for _ in entry.partition("="))
            if not (code and found and file):
                raise self.error(
                    f"video track needs language=file, like en=clip.vtt;"
                    f" got {entry!r}"
                )
            tracks.append({"lang": code, "url": file, "label": language(code)})
        self.options["url"] = url
        self.options["sources"] = sources
        self.options["tracks"] = tracks
        self.options["player"] = self.player()
        text = self.options.pop("caption", None) or "\n".join(self.content)
        caption, messages = parse(self, text.strip(), "caption")
        element = node("", caption, **self.options)
        urls = {
            "urls": " ".join(
                [
                    *(_["url"] for _ in sources),
                    *(_["url"] for _ in tracks),
                    self.options.get("poster", ""),
                ]
            )
        }
        return [element, *trail(urls, ("urls",)), *messages]

    def player(self) -> dict[str, str | None]:
        """Work out the attributes the `<video>` tag is written with.

        An empty value is how a boolean attribute is written.

        :return: The attributes, with `None` for the ones to leave out.
        """
        options = self.options
        autoplay = "autoplay" in options
        return {
            "controls": "" if options.get("controls", True) else None,
            "autoplay": "" if autoplay else None,
            "muted": "" if autoplay or "muted" in options else None,
            "playsinline": "" if autoplay else None,
            "loop": "" if "loop" in options else None,
            "poster": options.get("poster"),
            "preload": options.get("preload"),
        }


visit = visitor(template)
