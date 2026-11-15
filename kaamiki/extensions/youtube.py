"""\
YouTube Directive
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February 2025
Last updated on: 15 November 2026

A `youtube` directive that embeds a video in the page::

    .. youtube:: https://www.youtube.com/watch?v=jNQXAC9IVRw
       :start: 90
       :caption: What it's about.

The player loads when it's clicked and comes from
`youtube-nocookie.com`, unless the site's
`kaamiki.conf.youtube.click_to_load` and
`kaamiki.conf.youtube.privacy` say otherwise. The picture it shows
until then is the video's own either way.
"""

from __future__ import annotations

import typing as t
import urllib.parse as urlparse

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import KaamikiDirective
from kaamiki.extensions.utils import Option
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import phrase
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import values
from kaamiki.extensions.utils import worded
from kaamiki.extensions.utils import youtube_id
from kaamiki.extensions.utils import youtube_still
from kaamiki.extensions.utils.icons import Icons
from kaamiki.extensions.utils.links import youtube_start
from kaamiki.extensions.utils.settings import BOUNDS

template: t.Final[str] = "directives/youtube.html.jinja"
RATIOS: t.Final[tuple[str, ...]] = ("16:9", "4:3", "21:9", "1:1", "9:16")
SECONDS: t.Final[tuple[float, float]] = BOUNDS["start"]


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


class Youtube(KaamikiDirective):
    """The `youtube` directive.

    The argument is the link of a YouTube video, or only its id. The
    link checker gets the picture of the video, so `linkcheck` fails and
    names a video that is deleted or private.

    Options::

        - `autoplay`: Play the video, without sound, when it loads. The
          player loads immediately, so you cannot use `click-to-load` or
          `auto-load` with it. `muted` is on already.
        - `closed-captions`: Show the closed captions.
        - `caption`: A line of text below the player, parsed as rST.
        - `start`: The second to start from, 1 to 10800. Without it, the
          `t=` of a pasted link sets it.
        - `end`: The second to stop at, 1 to 10800, after `start`.
        - `privacy`: Embed from `youtube-nocookie.com`. The picture of a
          click-to-load player stays the picture of the video. It is on
          by default, so use it only on a site with
          `kaamiki.conf.youtube.privacy` off.
        - `no-privacy`: Embed from `youtube.com` when
          `kaamiki.conf.youtube.privacy` of the site is on.
        - `hide-controls`: Do not show the controls of the player. It
          needs `autoplay`, because without controls nothing can play
          the video.
        - `loop`: Play it again and again.
        - `muted`: Start without sound. `autoplay` does this already.
        - `player-language`: The language of the player and of the
          captions, as a code, as `en` or `pt-BR`.
        - `ratio`: The shape of the player, `16:9`, `4:3`, `21:9`, `1:1`
          or `9:16`. The default is `16:9`.
        - `click-to-load`: Show the picture of the video, and load the
          player when a reader clicks it. It is on by default, so use it
          only on a site with `kaamiki.conf.youtube.click_to_load` off.
        - `auto-load`: Load the player with the page when
          `kaamiki.conf.youtube.click_to_load` of the site is on.
        - `name`: A name for links.
        - `class`: More classes for the player.
    """

    required_arguments = 1
    final_argument_whitespace = False
    autoplay = Option(rst.directives.flag)
    closed_captions = Option(rst.directives.flag)
    caption = Option(checks.text)
    start = Option(checks.integer(*map(int, SECONDS)))
    end = Option(checks.integer(*map(int, SECONDS)))
    privacy = Option(rst.directives.flag)
    no_privacy = Option(rst.directives.flag)
    hide_controls = Option(rst.directives.flag)
    loop = Option(rst.directives.flag)
    muted = Option(rst.directives.flag)
    player_language = Option(language)
    ratio = Option(checks.word(*RATIOS))
    click_to_load = Option(rst.directives.flag)
    auto_load = Option(rst.directives.flag)

    class Node(nodes.Element):
        """The player and its parsed caption, which `visit` writes."""

    def switch(
        self, on: str, off: str, site: object, setting_name: str
    ) -> bool:
        """Work out whether a setting a site can set is on for a player.

        :param on: The option that turns it on, like `privacy`.
        :param off: The option that turns it off, like `no-privacy`.
        :param site: Whether the site has it on.
        :param setting_name: The site's setting, for the message.
        :return: Whether it's on for this player.
        :raises rst.DirectiveError: For both options at once and for
            one that changes nothing, as the site has it that way
            already.
        """
        turned_on, turned_off = on in self.options, off in self.options
        if turned_on and turned_off:
            self.fail(f":{on}: not allowed with :{off}:")
        if turned_on and site:
            self.fail(f":{on}: does nothing, {setting_name} is on already")
        if turned_off and not site:
            self.fail(f":{off}: does nothing, {setting_name} is off already")
        return turned_on or (bool(site) and not turned_off)

    def build(self) -> list[nodes.Node]:
        """Build the embed URL and return the player's node.

        :return: The node, followed by the `raw` node `trail` returns
            for the link checker and anything the caption reported.
        """
        src = self.arguments.pop().strip()
        vid = youtube_id(src)
        if vid is None:
            self.fail(f"expected a YouTube video link or id, got {src!r}")
        if not urlparse.urlsplit(src).netloc:
            src = f"https://www.youtube.com/watch?v={vid}"
        options = self.options
        if "start" not in options and (found := youtube_start(src)):
            low, high = SECONDS
            if not low <= found <= high:
                self.fail(
                    f"expected a start time in the link from {low:g}"
                    f" to {high:g} seconds, got {found!r}"
                )
            options["start"] = found
        if "end" in options and options["end"] <= options.get("start", 0):
            self.fail(f":end: expected after :start:, got {options['end']!r}")
        if "muted" in options and "autoplay" in options:
            self.fail(
                ":muted: not allowed with :autoplay:, which is muted already"
            )
        config = self.config
        private = self.switch(
            "privacy",
            "no-privacy",
            values(config).youtube.privacy,
            "kaamiki.conf.youtube.privacy",
        )
        facade = False
        if "autoplay" in options:
            for each in ("click-to-load", "auto-load"):
                if each in options:
                    self.fail(
                        f":{each}: not allowed with :autoplay:,"
                        " which loads the player at once"
                    )
        else:
            facade = self.switch(
                "click-to-load",
                "auto-load",
                values(config).youtube.click_to_load,
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
        self.options["still"] = youtube_still(vid)
        self.options["ratio"] = self.options.get("ratio", "").replace(
            ":", " / "
        )
        if "hide-controls" in options and "autoplay" not in options:
            self.fail(
                ":hide-controls: needs :autoplay:, since nothing else plays it"
            )
        allow = str(values(config).youtube.allow).split("; ")
        if "autoplay" in options or facade:
            allow = [*dict.fromkeys([*allow, "autoplay"])]
        self.options["allow"] = "; ".join(allow)
        self.options["referrer"] = str(values(config).youtube.referrer_policy)
        text = self.options.pop("caption", "")
        caption, messages = parse(self, text.strip(), "caption")
        if text.strip():
            worded(self, caption, "a caption")
        element = self.locate(self.Node("", caption, **self.options))
        self.add_name(element)
        return [element, *trail(self, self.options, ("still",)), *messages]

    @staticmethod
    def plain(node: Youtube.Node) -> list[nodes.Node]:
        """Write a player as words, for a builder that writes no HTML.

        :param node: The player's node.
        :return: A paragraph with its caption, when it has one, and one
            with the video's address, written as a link to itself.
        """
        found: list[nodes.Node] = [
            nodes.paragraph("", "", *each.children)
            for each in node.children
            if isinstance(each, phrase) and each.children
        ]
        link = nodes.reference("", node["watch"], refuri=node["watch"])
        return [*found, nodes.paragraph("", "", link)]


html.draws(Youtube.Node, template)
