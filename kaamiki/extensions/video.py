"""\
Video Directive
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February 2025
Last updated on: 07 November 2026

A `video` directive that embeds a video in the page::

    .. video:: https://www.w3schools.com/tags/movie.mp4
       :autoplay:
       :caption: A short clip.

The caption is parsed as rST. More sources, a poster and subtitles
go in options::

    .. video:: _static/clip.mp4
       :sources: _static/clip.webm
       :poster: _static/clip.png
       :track: en=_static/clip.en.vtt, hi=_static/clip.hi.vtt
"""

from __future__ import annotations

import os.path as p
import re
import typing as t
from urllib.parse import urlsplit

import docutils.nodes as nodes
import docutils.parsers.rst as rst
from babel import Locale

from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import listed
from kaamiki.extensions.utils import located
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import phrase
from kaamiki.extensions.utils import relative_to_page
from kaamiki.extensions.utils import shipped
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import visitor
from kaamiki.extensions.utils import worded

if t.TYPE_CHECKING:
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "video"
template: t.Final[str] = "directives/video.html.jinja"
PRELOAD: t.Final[tuple[str, ...]] = ("none", "metadata", "auto")
KINDS: t.Final[tuple[str, ...]] = (
    "video/mp4",
    "video/webm",
    "video/ogg",
    "video/quicktime",
)
# The types a browser tries, by extension. Chromium won't try
# video/quicktime, so a .mov is written as video/mp4, which plays the
# H.264 a phone records, and .ogg holds video here, not audio.
# https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/Containers
TYPES: t.Final[dict[str, tuple[str, ...]]] = {
    ".mp4": ("video/mp4",),
    ".m4v": ("video/mp4",),
    ".webm": ("video/webm",),
    ".ogv": ("video/ogg",),
    ".ogg": ("video/ogg",),
    ".mov": ("video/mp4", "video/quicktime"),
}
FILES: t.Final[re.Pattern[str]] = re.compile(
    r".+\.(?:mp4|m4v|webm|ogv|ogg|mov)", re.IGNORECASE
)
CAPTIONS: t.Final[re.Pattern[str]] = re.compile(r".+\.vtt", re.IGNORECASE)
SOURCES: t.Final[int] = 4
TRACKS: t.Final[int] = 8


def extension(url: str) -> str:
    """Read the extension off a video's address.

    :param url: The address or path, as written.
    :return: The extension in lower case with its dot, or nothing.
    """
    return p.splitext(urlsplit(url).path)[1].lower()


class Video(nodes.Element):
    """The video and its parsed caption, waiting for `visit`."""


class directive(rst.Directive):
    """The `video` directive.

    Options::

        - `autoplay`: Play the video, muted, as soon as it loads.
          `muted` is on already.
        - `caption`: A line of text under the video, parsed as rST.
        - `type`: The video's MIME type, when its extension doesn't
          say. It overrides the type each extension stands for, which
          is `video/mp4` for `.mov` too, and it can't disagree with an
          extension Kaamiki knows.
        - `sources`: More files of the same video, comma-separated, for
          browsers that can't play the first.
        - `poster`: The picture shown until the video plays, an address
          or a path of a `.jpg`, `.png`, `.webp`, `.avif`, `.gif` or
          `.svg`.
        - `preload`: How much the browser fetches ahead: `none`,
          `metadata` or `auto`. `none` is not allowed with `autoplay`.
        - `loop`: Play it over and over.
        - `muted`: Start with the sound off.
        - `hide-controls`: Hide the player controls, which are shown
          without it. It needs `autoplay`, or there is no way to play
          the video.
        - `track`: Captions, as `language=file` and comma-separated, up
          to 8. A language or a file can be in it once.
        - `name`: A name to link to.
        - `class`: More classes for the video.

    A phone plays the video in the page, with full screen one tap away
    in its controls.
    """

    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "autoplay": rst.directives.flag,
        "caption": checks.text,
        "type": checks.word(*KINDS),
        "sources": checks.text,
        "poster": checks.picture,
        "preload": checks.word(*PRELOAD),
        "loop": rst.directives.flag,
        "muted": rst.directives.flag,
        "hide-controls": rst.directives.flag,
        "track": checks.text,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the caption and return the video's node.

        :return: The node, followed by the `raw` node `trail` returns
            for the link checker and anything the caption reported.
        """
        options = self.options
        url = self.address(self.arguments.pop(), options.get("type"))
        known = TYPES.get(extension(url), ())
        given = options.pop("type", None)
        if given and known and given not in known:
            raise self.error(
                f"video: :type: expected {' or '.join(known)} for {url!r},"
                f" got {given}"
            )
        sources = [{"url": url, "type": given or "".join(known[:1])}]
        more = listed(options.pop("sources", ""))
        if len(more) > SOURCES or len({url, *more}) != len(more) + 1:
            raise self.error(
                f"video: :sources: expected at most {SOURCES} besides the"
                f" video, got {len(more)}"
            )
        for each in more:
            found = self.address(each, where=":sources:")
            sources.append(
                {
                    "url": each,
                    "type": "".join(TYPES.get(extension(found), ())[:1]),
                }
            )
        tracks: list[dict[str, str]] = []
        entries = listed(options.pop("track", ""))
        if len(entries) > TRACKS:
            raise self.error(
                f"video: :track: expected at most {TRACKS} captions, got"
                f" {len(entries)}"
            )
        seen: dict[tuple[str, str], str] = {}
        for entry in entries:
            code, equals, file = (_.strip() for _ in entry.partition("="))
            if not equals or not CAPTIONS.fullmatch(file):
                raise self.error(
                    f"video: :track: expected language=file.vtt, got {entry!r}"
                )
            for what, value in (("language", code), ("file", file)):
                first = seen.setdefault((what, value), entry)
                if first is not entry:
                    raise self.error(
                        f"video: :track: expected each {what} once, got"
                        f" {value!r} in {first!r} and {entry!r}"
                    )
            try:
                checks.link(file)
                shipped(self, file, ":track:")
                checks.language(code)
                if not checks.LOCALE.fullmatch(code):
                    raise ValueError(
                        f"expected a language code like en or pt-BR, got"
                        f" {code!r}"
                    )
                locale = code.replace("-", "_")
                label = Locale.parse(locale).get_display_name(locale) or code
            except ValueError as error:
                raise self.error(f"video: :track: {error}") from error
            tracks.append({"lang": code, "url": file, "label": label})
        if "hide-controls" in options and "autoplay" not in options:
            raise self.error(
                "video: :hide-controls: needs :autoplay:, since nothing else"
                " plays it"
            )
        if "autoplay" in options and options.get("preload") == "none":
            raise self.error(
                "video: :preload: none not allowed with :autoplay:, which"
                " fetches the video at once"
            )
        if "autoplay" in options and "muted" in options:
            raise self.error(
                "video: :muted: not allowed with :autoplay:, which is muted "
                "already"
            )
        self.options["classes"] = self.options.pop("class", [])
        self.options["sources"] = sources
        self.options["tracks"] = tracks
        self.options["player"] = self.player()
        if "poster" in options:
            shipped(self, options["poster"], ":poster:")
        text = self.options.pop("caption", "")
        caption, messages = parse(self, text.strip(), "caption")
        if text.strip():
            worded(self, caption, "a caption")
        element = located(self, Video("", caption, **self.options))
        named(self, element)
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

    def address(
        self,
        argument: str,
        kind: str | None = None,
        where: str = "the address",
    ) -> str:
        """Check a video's address and that it says what it is.

        :param argument: The address as written.
        :param kind: The MIME type the directive gives it, if one.
        :param where: What the address was written as.
        :return: The address.
        :raises rst.DirectiveError: For one that isn't an address or a
            video file the extension doesn't say so and no `:type:`
            does.
        """
        try:
            found = checks.link(argument, schemes=("http", "https"))
        except ValueError as error:
            raise self.error(f"video: {error}") from error
        if not FILES.fullmatch(urlsplit(found).path) and not kind:
            raise self.error(
                f"video: expected a .mp4, .m4v, .webm, .ogv, .ogg or .mov file,"
                f" got {found!r}; give its :type: if it is a video"
            )
        return shipped(self, found, where)

    def player(self) -> dict[str, str | None]:
        """Work out the attributes the `<video>` tag is written with.

        An empty value is how a boolean attribute is written.

        :return: The attributes, with `None` for the ones to leave out.
        """
        options = self.options
        autoplay = "autoplay" in options
        return {
            "controls": None if "hide-controls" in options else "",
            "autoplay": "" if autoplay else None,
            "muted": "" if autoplay or "muted" in options else None,
            "playsinline": "",
            "loop": "" if "loop" in options else None,
            "poster": options.get("poster"),
            "preload": options.get("preload"),
        }


def prepare(
    self: HTMLTranslator, attributes: dict[str, t.Any]
) -> dict[str, t.Any]:
    """Turn the paths the video was given into addresses.

    :param self: The HTML translator writing the page.
    :param attributes: The node's attributes.
    :return: A copy of them with the sources, captions and poster
        resolved against the page.
    """
    found = dict(attributes)
    found["sources"] = [
        {**_, "url": relative_to_page(self, _["url"])}
        for _ in attributes["sources"]
    ]
    found["tracks"] = [
        {**_, "url": relative_to_page(self, _["url"])}
        for _ in attributes["tracks"]
    ]
    if attributes.get("poster"):
        found["poster"] = relative_to_page(self, attributes["poster"])
        found["player"] = {**attributes["player"], "poster": found["poster"]}
    return found


def plain(node: Video) -> list[nodes.Node]:
    """Write a video as words, for a builder that draws no HTML.

    :param node: The video's node.
    :return: A paragraph with its caption, when it has one, and one
        with the video's address, written as a link to itself.
    """
    found: list[nodes.Node] = [
        nodes.paragraph("", "", *_.children)
        for _ in node.children
        if isinstance(_, phrase) and _.children
    ]
    url = node["sources"][0]["url"]
    link = nodes.reference("", url, refuri=url)
    return [*found, nodes.paragraph("", "", link)]


visit = visitor(template, prepare)


node = Video
