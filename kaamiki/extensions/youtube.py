"""\
YouTube Directive
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February 2025
Last updated on: 08 October 2026

A `youtube` directive that embeds a video in the page::

    .. youtube:: https://www.youtube.com/watch?v=PhabJpIPONI
       :startfrom: 90
       :privacy:

       What it's about.
"""

from __future__ import annotations

import re
import typing as t
import urllib.parse as urlparse

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils import toggle
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import visitor
from kaamiki.extensions.utils import youtube_id

name: t.Final[str] = "youtube"
template: t.Final[str] = "youtube.html.jinja"
LANGUAGE: re.Pattern[str] = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
RATIO: re.Pattern[str] = re.compile(
    r"^(\d+(?:\.\d+)?)\s*[:/]\s*(\d+(?:\.\d+)?)$"
)


def tongue(argument: str) -> str:
    """Check the `language` option reads as a language code.

    :param argument: The value written in the rST.
    :return: The code, like `en` or `pt-BR`.
    :raises ValueError: When it isn't one.
    """
    if not LANGUAGE.match(argument.strip()):
        raise ValueError(f"expected a language code like en, got {argument!r}")
    return argument.strip()


def ratio(argument: str) -> str:
    """Check the `ratio` option reads as a width and a height.

    :param argument: The value written in the rST, as `4:3` or `16/9`.
    :return: The ratio as CSS writes it, `4 / 3`.
    :raises ValueError: When it isn't one.
    """
    found = RATIO.match(argument.strip())
    if found is None or not float(found[1]) or not float(found[2]):
        raise ValueError(f"expected a ratio like 16:9, got {argument!r}")
    return f"{found[1]} / {found[2]}"


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
        - `privacy`: Embed from `youtube-nocookie.com`. `false` embeds
          from `youtube.com` when the site's `youtube_privacy` is on.
        - `controls`: `0` hides the player controls.
        - `loop`: Play it over and over.
        - `mute`: Start with the sound off.
        - `language`: The player's language and the captions' as a
          code, like `en` or `pt-BR`.
        - `ratio`: The player's shape, as `4:3`. Defaults to `16:9`.
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
        "privacy": toggle,
        "controls": rst.directives.nonnegative_int,
        "loop": rst.directives.flag,
        "mute": rst.directives.flag,
        "language": tongue,
        "ratio": ratio,
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
        private = self.options.get(
            "privacy", setting(config, "youtube_privacy")
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
        if "controls" in self.options:
            params["controls"] = int(self.options["controls"])
        if "endat" in self.options:
            params["end"] = self.options["endat"]
        if "loop" in self.options:
            params["loop"] = 1
            params["playlist"] = vid
        if "mute" in self.options:
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
        self.options["ratio"] = self.options.get("ratio", "")
        self.options["allow"] = str(setting(config, "youtube_allow"))
        self.options["referrer"] = str(
            setting(config, "youtube_referrer_policy")
        )
        text = self.options.pop("caption", None) or "\n".join(self.content)
        caption, messages = parse(self, text.strip(), "caption")
        element = node("", caption, **self.options)
        return [element, *trail(self.options, ("src",)), *messages]


visit = visitor(template)
