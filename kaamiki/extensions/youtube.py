"""\
YouTube Directive
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February 2025
Last updated on: 12 October 2026

A `youtube` directive that embeds a video in the page::

    .. youtube:: https://www.youtube.com/watch?v=PhabJpIPONI
       :startfrom: 90
       :privacy:

       What it's about.
"""

import functools
import typing as t
import urllib.parse as urlparse

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import visitor
from kaamiki.extensions.utils import youtube_id

name: t.Final[str] = "youtube"
template: t.Final[str] = "directives/youtube.html.jinja"
RATIOS: t.Final[tuple[str, ...]] = ("16:9", "4:3", "21:9", "1:1", "9:16")


class node(nodes.Element):
    """The player and its parsed caption, waiting for `visit`."""


class directive(rst.Directive):
    """The `youtube` directive.

    Options::

        - `autoplay`: Play the video as soon as it loads.
        - `showcaptions`: Turn closed captions on.
        - `caption`: A line of text under the player. It wins over the
          directive's body.
        - `startfrom`: Seconds to start playing from.
        - `endat`: Seconds to stop playing at.
        - `privacy`: Embed from `youtube-nocookie.com`, which a site
          can do for every player with its `youtube_privacy`.
        - `hide-controls`: Hide the player controls, which are shown
          without it.
        - `loop`: Play it over and over.
        - `muted`: Start with the sound off.
        - `language`: The player's language and the captions' as a
          code, like `en` or `pt-BR`.
        - `ratio`: The player's shape, `16:9`, `4:3`, `21:9`, `1:1` or
          `9:16`. Defaults to `16:9`.
        - `click-to-load`: Show the video's picture and load the player
          once it's clicked.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        "autoplay": rst.directives.flag,
        "showcaptions": rst.directives.flag,
        "caption": rst.directives.unchanged,
        "startfrom": rst.directives.positive_int,
        "endat": rst.directives.positive_int,
        "privacy": rst.directives.flag,
        "hide-controls": rst.directives.flag,
        "loop": rst.directives.flag,
        "muted": rst.directives.flag,
        "language": rst.directives.unchanged_required,
        "ratio": functools.partial(rst.directives.choice, values=RATIOS),
        "click-to-load": rst.directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        """Build the embed URL and return the player's node.

        :return: The node, followed by the `raw` node `trail` returns
            for the link checker and anything the caption reported.
        """
        src = rst.directives.uri(self.arguments.pop().strip())
        vid = youtube_id(src)
        if vid is None:
            raise self.error(f"youtube found no video in {src!r}")
        config = self.state.document.settings.env.config
        private = "privacy" in self.options or setting(
            config, "youtube_privacy"
        )
        domain = (
            "https://www.youtube-nocookie.com"
            if private
            else "https://www.youtube.com"
        )
        # NOTE(xames3): Checkout more options at their website.
        # https://developers.google.com/youtube/player_parameters
        params = {
            "start": self.options.get("startfrom", 0),
            "autoplay": 1 if "autoplay" in self.options else 0,
            "cc_load_policy": 1 if "showcaptions" in self.options else 0,
            "rel": 0,
            "playsinline": 1,
        }
        if "hide-controls" in self.options:
            params["controls"] = 0
        if "endat" in self.options:
            params["end"] = self.options["endat"]
        if "loop" in self.options:
            params["loop"] = 1
            params["playlist"] = vid
        if "muted" in self.options:
            params["mute"] = 1
        if "language" in self.options:
            params["hl"] = self.options["language"]
            params["cc_lang_pref"] = self.options["language"]
        url = f"{domain}/embed/{vid}?{urlparse.urlencode(params)}"
        self.options["url"] = url
        self.options["src"] = src
        self.options["watch"] = f"https://www.youtube.com/watch?v={vid}"
        self.options["video_id"] = vid
        self.options["facade"] = "click-to-load" in self.options
        self.options["private"] = bool(private)
        self.options["ratio"] = self.options.get("ratio", "").replace(
            ":", " / "
        )
        self.options["allow"] = str(setting(config, "youtube_allow"))
        self.options["referrer"] = str(
            setting(config, "youtube_referrer_policy")
        )
        text = self.options.pop("caption", None) or "\n".join(self.content)
        caption, messages = parse(self, text.strip(), "caption")
        element = node("", caption, **self.options)
        return [element, *trail(self.options, ("src",)), *messages]


visit = visitor(template)
