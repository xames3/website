"""\
YouTube Directive
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February 2025
Last updated on: 07 November 2026

A `youtube` directive that embeds a video in the page::

    .. youtube:: https://www.youtube.com/watch?v=PhabJpIPONI
       :start: 90
       :caption: What it's about.

The player loads when it's clicked and comes from
`youtube-nocookie.com`, unless the site's
`kaamiki.conf.youtube.click_to_load` and
`kaamiki.conf.youtube.privacy` say otherwise. The picture it shows
until then is the video's own either way.
"""

import typing as t
import urllib.parse as urlparse

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import located
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import phrase
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import visitor
from kaamiki.extensions.utils import worded
from kaamiki.extensions.utils import youtube_id
from kaamiki.extensions.utils.icons import Icons
from kaamiki.extensions.utils.links import youtube_start
from kaamiki.extensions.utils.settings import BOUNDS

name: t.Final[str] = "youtube"
template: t.Final[str] = "directives/youtube.html.jinja"
RATIOS: t.Final[tuple[str, ...]] = ("16:9", "4:3", "21:9", "1:1", "9:16")


def language(argument: str | None) -> str:
    """Check the language of the player and its captions.

    :param argument: The code as written, like `en` or `pt-BR`.
    :return: The code.
    :raises ValueError: When it isn't a language code Babel knows or
        isn't written with a `-`, the way YouTube reads it.
    """
    code = checks.language(argument)
    if not checks.LOCALE.fullmatch(code):
        raise ValueError(
            f"expected a language code like en or pt-BR, got {argument!r}"
        )
    return code


class Youtube(nodes.Element):
    """The player and its parsed caption, waiting for `visit`."""


class directive(rst.Directive):
    """The `youtube` directive.

    Options::

        - `autoplay`: Play the video, muted, as soon as it loads. The
          player loads at once, so it takes neither `click-to-load`
          nor `auto-load`, and `muted` is on already.
        - `closed-captions`: Turn closed captions on.
        - `caption`: A line of text under the player, parsed as rST.
        - `start`: Seconds to start playing from, 1 to 10800. A pasted
          link's own `t=` is used when it isn't written.
        - `end`: Seconds to stop playing at, 1 to 10800 and after
          `start`.
        - `privacy`: Embed from `youtube-nocookie.com`, the picture of
          a click-to-load player staying the video's own. It's on
          without it, so it only works for a site that turned
          `kaamiki.conf.youtube.privacy` off.
        - `no-privacy`: Embed from `youtube.com`, even though the
          site's `kaamiki.conf.youtube.privacy` is on.
        - `hide-controls`: Hide the player controls, which are shown
          without it. It needs `autoplay`, or there is no way to play
          the video.
        - `loop`: Play it over and over.
        - `muted`: Start with the sound off. `autoplay` does that
          already.
        - `player-language`: The player's language and the captions' as
          a code, like `en` or `pt-BR`.
        - `ratio`: The player's shape, `16:9`, `4:3`, `21:9`, `1:1` or
          `9:16`. Defaults to `16:9`.
        - `click-to-load`: Show the video's picture and load the player
          once it's clicked. It's on without it, so it only works for a
          site that turned `kaamiki.conf.youtube.click_to_load` off.
        - `auto-load`: Load the player with the page, even though
          the site's `kaamiki.conf.youtube.click_to_load` is on.
        - `name`: A name to link to.
        - `class`: More classes for the player.
    """

    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "autoplay": rst.directives.flag,
        "closed-captions": rst.directives.flag,
        "caption": checks.text,
        "start": checks.integer(*map(int, BOUNDS["start"])),
        "end": checks.integer(*map(int, BOUNDS["start"])),
        "privacy": rst.directives.flag,
        "no-privacy": rst.directives.flag,
        "hide-controls": rst.directives.flag,
        "loop": rst.directives.flag,
        "muted": rst.directives.flag,
        "player-language": language,
        "ratio": checks.word(*RATIOS),
        "click-to-load": rst.directives.flag,
        "auto-load": rst.directives.flag,
    }

    def switch(self, on: str, off: str, site: object, name: str) -> bool:
        """Work out whether something a site can set is on for a
        player.

        :param on: The option that turns it on, like `privacy`.
        :param off: The option that turns it off, like `no-privacy`.
        :param site: Whether the site has it on.
        :param name: The site's setting, for the message.
        :return: Whether it's on for this player.
        :raises rst.DirectiveError: For both options at once and for
            one that changes nothing, as the site has it that way
            already.
        """
        turned_on, turned_off = on in self.options, off in self.options
        if turned_on and turned_off:
            raise self.error(f"youtube: :{on}: not allowed with :{off}:")
        if turned_on and site:
            raise self.error(
                f"youtube: :{on}: does nothing, {name} is on already"
            )
        if turned_off and not site:
            raise self.error(
                f"youtube: :{off}: does nothing, {name} is off already"
            )
        return turned_on or (bool(site) and not turned_off)

    def run(self) -> list[nodes.Node]:
        """Build the embed URL and return the player's node.

        :return: The node, followed by the `raw` node `trail` returns
            for the link checker and anything the caption reported.
        """
        src = self.arguments.pop().strip()
        vid = youtube_id(src)
        if vid is None:
            raise self.error(
                f"youtube: expected a YouTube video link, got {src!r}"
            )
        if not urlparse.urlsplit(src).netloc:
            src = f"https://www.youtube.com/watch?v={vid}"
        options = self.options
        if "start" not in options and (found := youtube_start(src)):
            low, high = BOUNDS["start"]
            if not low <= found <= high:
                raise self.error(
                    f"youtube: expected a start time in the link from {low:g}"
                    f" to {high:g} seconds, got {found!r}"
                )
            options["start"] = found
        if "end" in options and options["end"] <= options.get("start", 0):
            raise self.error(
                f"youtube: :end: expected after :start:, got {options['end']!r}"
            )
        if "muted" in options and "autoplay" in options:
            raise self.error(
                "youtube: :muted: not allowed with :autoplay:, which is "
                "muted already"
            )
        config = self.state.document.settings.env.config
        private = self.switch(
            "privacy",
            "no-privacy",
            setting(config, "youtube_privacy"),
            "kaamiki.conf.youtube.privacy",
        )
        facade = False
        if "autoplay" in options:
            for each in ("click-to-load", "auto-load"):
                if each in options:
                    raise self.error(
                        f"youtube: :{each}: not allowed with :autoplay:,"
                        " which loads the player at once"
                    )
        else:
            facade = self.switch(
                "click-to-load",
                "auto-load",
                setting(config, "youtube_click_to_load"),
                "kaamiki.conf.youtube.click_to_load",
            )
        domain = (
            "https://www.youtube-nocookie.com"
            if private
            else "https://www.youtube.com"
        )
        # Every player parameter:
        # https://developers.google.com/youtube/player_parameters
        params = {
            "start": self.options.get("start", 0),
            "autoplay": 1 if "autoplay" in self.options else 0,
            "cc_load_policy": 1 if "closed-captions" in self.options else 0,
            "rel": 0,
            "playsinline": 1,
        }
        if "hide-controls" in self.options:
            params["controls"] = 0
        if "end" in self.options:
            params["end"] = self.options["end"]
        if "loop" in self.options:
            params["loop"] = 1
            params["playlist"] = vid
        if "muted" in self.options or "autoplay" in self.options:
            params["mute"] = 1
        if "player-language" in self.options:
            params["hl"] = self.options["player-language"]
            params["cc_lang_pref"] = self.options["player-language"]
        url = f"{domain}/embed/{vid}?{urlparse.urlencode(params)}"
        self.options["classes"] = self.options.pop("class", [])
        self.options["url"] = url
        self.options["src"] = src
        self.options["watch"] = f"https://www.youtube.com/watch?v={vid}"
        self.options["video_id"] = vid
        self.options["facade"] = facade
        self.options["private"] = private
        self.options["play"] = Icons.of(config).classes("fa-solid fa-play")
        self.options["still"] = (
            f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"
        )
        self.options["ratio"] = self.options.get("ratio", "").replace(
            ":", " / "
        )
        if "hide-controls" in options and "autoplay" not in options:
            raise self.error(
                "youtube: :hide-controls: needs :autoplay:, since nothing else"
                " plays it"
            )
        allow = str(setting(config, "youtube_allow")).split("; ")
        if "autoplay" in options or facade:
            allow = [*dict.fromkeys([*allow, "autoplay"])]
        self.options["allow"] = "; ".join(allow)
        self.options["referrer"] = str(
            setting(config, "youtube_referrer_policy")
        )
        text = self.options.pop("caption", "")
        caption, messages = parse(self, text.strip(), "caption")
        if text.strip():
            worded(self, caption, "a caption")
        element = located(self, Youtube("", caption, **self.options))
        named(self, element)
        return [element, *trail(self.options, ("src",)), *messages]


def plain(node: Youtube) -> list[nodes.Node]:
    """Write a player as words, for a builder that draws no HTML.

    :param node: The player's node.
    :return: A paragraph with its caption, when it has one, and one
        with the video's address, written as a link to itself.
    """
    found: list[nodes.Node] = [
        nodes.paragraph("", "", *_.children)
        for _ in node.children
        if isinstance(_, phrase) and _.children
    ]
    link = nodes.reference("", node["watch"], refuri=node["watch"])
    return [*found, nodes.paragraph("", "", link)]


visit = visitor(template)


node = Youtube
