"""\
Video Directive
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February 2025
Last updated on: 15 November 2026

A `video` directive that embeds a video in the page::

    .. video:: https://example.com/clip.mp4
       :autoplay:
       :caption: A short clip.

The caption is parsed as rST. More sources, a poster and subtitles go
in options. Here the files are yours, in `html_static_path`::

    .. video:: _static/clip.mp4
       :sources: _static/clip.webm
       :poster: _static/clip.png
       :track: en=_static/clip.en.vtt, hi=_static/clip.hi.vtt

A phone plays the video in the page. Its controls have a button for
full screen.
"""

from __future__ import annotations

import os.path as p
import re
import typing as t
from urllib.parse import urlsplit

import docutils.nodes as nodes
import docutils.parsers.rst as rst
from babel import Locale

from kaamiki.extensions.utils import KaamikiDirective
from kaamiki.extensions.utils import Option
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import listed
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import phrase
from kaamiki.extensions.utils import relative_to_page
from kaamiki.extensions.utils import shipped
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import worded

if t.TYPE_CHECKING:
    from sphinx.writers.html import HTMLTranslator

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
    """Read the extension of the address of a video.

    :param url: The address or the path, as written.
    :return: The extension in lower case with its dot, or nothing.
    """
    return p.splitext(urlsplit(url).path)[1].lower()


class Video(KaamikiDirective):
    """The `video` directive.

    Options::

        - `autoplay`: Play the video, without sound, when it loads.
          `muted` is on already.
        - `caption`: A line of text below the video, parsed as rST.
        - `type`: The MIME type of the video, when its extension
          does not tell it. It must agree with an extension that
          Kaamiki knows. Without it, a `.mov` is `video/mp4`. It
          can be `video/quicktime`.
        - `sources`: More files of the same video, with a comma
          between each, for browsers that cannot play the first
          file.
        - `poster`: The picture that shows until the video plays,
          as an address or a path of a `.jpg`, `.png`, `.webp`,
          `.avif`, `.gif` or `.svg`.
        - `preload`: How much the browser gets before the video
          plays, `none`, `metadata` or `auto`. You cannot use
          `none` with `autoplay`.
        - `loop`: Play it again and again.
        - `muted`: Start without sound.
        - `hide-controls`: Do not show the controls of the player.
          It needs `autoplay`, because without controls nothing can
          play the video.
        - `track`: Captions, as `language=file`, with a comma
          between each, to a maximum of 8. Each language and each
          file can occur only one time.
        - `name`: A name for links.
        - `class`: More classes for the video.
    """

    required_arguments = 1
    final_argument_whitespace = False
    autoplay = Option(rst.directives.flag)
    caption = Option(checks.text)
    type = Option(checks.word(*KINDS))
    sources = Option(checks.text)
    poster = Option(checks.picture)
    preload = Option(checks.word(*PRELOAD))
    loop = Option(rst.directives.flag)
    muted = Option(rst.directives.flag)
    hide_controls = Option(rst.directives.flag)
    track = Option(checks.text)

    class Node(nodes.Element):
        """The video and its parsed caption, which `visit` writes."""

    def build(self) -> list[nodes.Node]:
        """Parse the caption and give the node of the video.

        :return: The node, the `raw` node from `trail` for the link
            checker, and what the caption reported.
        """
        options = self.options
        url = self.address(self.arguments.pop(), options.get("type"))
        known = TYPES.get(extension(url), ())
        given = options.pop("type", None)
        if given and known and given not in known:
            self.fail(
                f":type: expected {' or '.join(known)} for {url!r},"
                f" got {given!r}"
            )
        sources = [{"url": url, "type": given or "".join(known[:1])}]
        more = listed(options.pop("sources", ""))
        if len(more) > SOURCES:
            self.fail(
                f":sources: expected at most {SOURCES} besides the"
                f" video, got {len(more)}"
            )
        files = [url, *more]
        if len(set(files)) != len(files):
            repeated = next(_ for _ in files if files.count(_) > 1)
            self.fail(
                f":sources: expected each file once, got {repeated!r}"
                " more than once"
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
            self.fail(
                f":track: expected at most {TRACKS} captions, got"
                f" {len(entries)}"
            )
        seen: dict[tuple[str, str], str] = {}
        for entry in entries:
            code, equals, file = (_.strip() for _ in entry.partition("="))
            if not equals or not CAPTIONS.fullmatch(file):
                self.fail(f":track: expected language=file.vtt, got {entry!r}")
            for what, value in (("language", code), ("file", file)):
                first = seen.setdefault((what, value), entry)
                if first is not entry:
                    self.fail(
                        f":track: expected each {what} once, got"
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
                self.fail(f":track: {error}")
            tracks.append({"lang": code, "url": file, "label": label})
        if "hide-controls" in options and "autoplay" not in options:
            self.fail(
                ":hide-controls: needs :autoplay:, since nothing else plays it"
            )
        if "autoplay" in options and options.get("preload") == "none":
            self.fail(
                ":preload: expected metadata or auto with :autoplay:,"
                " got 'none'"
            )
        if "autoplay" in options and "muted" in options:
            self.fail(
                ":muted: not allowed with :autoplay:, which is muted already"
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
        element = self.locate(self.Node("", caption, **self.options))
        self.add_name(element)
        urls = {
            "urls": " ".join(
                [
                    *(_["url"] for _ in sources),
                    *(_["url"] for _ in tracks),
                    self.options.get("poster", ""),
                ]
            )
        }
        return [element, *trail(self, urls, ("urls",)), *messages]

    def address(
        self,
        argument: str,
        kind: str | None = None,
        where: str = "the address",
    ) -> str:
        """Check the address of a video, and that it tells its type.

        :param argument: The address as written.
        :param kind: The MIME type from the directive, if it gives one.
        :param where: How the address was written.
        :return: The address.
        :raises rst.DirectiveError: For a value that is not an address,
            or a video file whose extension does not tell its type when
            no `:type:` does.
        """
        try:
            found = checks.link(argument, schemes=("http", "https"))
        except ValueError as error:
            self.fail(str(error))
        if not FILES.fullmatch(urlsplit(found).path) and not kind:
            self.fail(
                "expected a .mp4, .m4v, .webm, .ogv, .ogg or .mov file"
                f" or a :type: for it, got {found!r}"
            )
        return shipped(self, found, where)

    def player(self) -> dict[str, str | None]:
        """Find the attributes of the `<video>` tag.

        :return: The attributes, with `None` for those to leave out. An
            empty value is how a boolean attribute is written.
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

    @staticmethod
    def plain(node: Video.Node) -> list[nodes.Node]:
        """Write a video as words, for a builder without HTML.

        :param node: The node of the video.
        :return: A paragraph with its caption, when it has one, and a
            paragraph with the address of the video as a link to
            itself.
        """
        found: list[nodes.Node] = [
            nodes.paragraph("", "", *each.children)
            for each in node.children
            if isinstance(each, phrase) and each.children
        ]
        url = node["sources"][0]["url"]
        link = nodes.reference("", url, refuri=url)
        return [*found, nodes.paragraph("", "", link)]


def prepare(
    self: HTMLTranslator, attributes: dict[str, t.Any]
) -> dict[str, t.Any]:
    """Change the paths of the video into addresses.

    :param self: The HTML translator that writes the page.
    :param attributes: The attributes of the node.
    :return: A copy of them, with the sources, the captions and the
        poster resolved against the page.
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


html.draws(Video.Node, template, prepare)
