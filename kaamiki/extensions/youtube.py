"""\
YouTube Directive
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February 2025
Last updated on: 25 October 2026

A `youtube` directive that embeds a video in the page::

    .. youtube:: https://www.youtube.com/watch?v=PhabJpIPONI
       :start-from: 90
       :privacy:

       What it's about.
"""

import typing as t
import urllib.parse as urlparse

import docutils.nodes as nodes
import docutils.parsers.rst as rst
from babel import Locale
from babel import UnknownLocaleError

from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import visitor
from kaamiki.extensions.utils import youtube_id
from kaamiki.extensions.utils.settings import BOUNDS

name: t.Final[str] = "youtube"
template: t.Final[str] = "directives/youtube.html.jinja"
RATIOS: t.Final[tuple[str, ...]] = ("16:9", "4:3", "21:9", "1:1", "9:16")


def language(argument: str | None) -> str:
    """Check the language of the player and its captions.

    :param argument: The code as written, like `en` or `pt-BR`.
    :return: The code.
    :raises ValueError: When it isn't a language code babel knows.
    """
    code = (argument or "").strip()
    if not checks.LOCALE.fullmatch(code):
        raise ValueError(
            f"expected a language code like en or pt-BR, got {argument!r}"
        )
    try:
        Locale.parse(code.replace("-", "_"))
    except (ValueError, UnknownLocaleError) as error:
        raise ValueError(
            f"expected a language code like en or pt-BR, got {code!r}"
        ) from error
    return code


class node(nodes.Element):
    """The player and its parsed caption, waiting for `visit`."""


class directive(rst.Directive):
    """The `youtube` directive.

    Options::

        - `autoplay`: Play the video, muted, as soon as it loads.
        - `show-captions`: Turn closed captions on.
        - `caption`: A line of text under the player. It wins over the
          directive's body.
        - `start-from`: Seconds to start playing from.
        - `end-at`: Seconds to stop playing at.
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
        - `name`: A name to link to.
        - `class`: More classes for the player.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "autoplay": rst.directives.flag,
        "show-captions": rst.directives.flag,
        "caption": checks.text,
        "start-from": checks.integer(*map(int, BOUNDS["startfrom"])),
        "end-at": checks.integer(*map(int, BOUNDS["startfrom"])),
        "privacy": rst.directives.flag,
        "hide-controls": rst.directives.flag,
        "loop": rst.directives.flag,
        "muted": rst.directives.flag,
        "language": language,
        "ratio": checks.word(*RATIOS),
        "click-to-load": rst.directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        """Build the embed URL and return the player's node.

        :return: The node, followed by the `raw` node `trail` returns
            for the link checker and anything the caption reported.
        """
        src = self.arguments.pop().strip()
        vid = youtube_id(src)
        if vid is None:
            raise self.error(f"youtube: no video found in {src!r}")
        if not urlparse.urlsplit(src).netloc:
            src = f"https://www.youtube.com/watch?v={vid}"
        options = self.options
        if "end-at" in options and options["end-at"] <= options.get(
            "start-from", 0
        ):
            raise self.error("youtube: :end-at: must be after :start-from:")
        if "caption" in options and self.content:
            raise self.error("youtube: :caption: not allowed with a body")
        if "click-to-load" in options and "autoplay" in options:
            raise self.error(
                "youtube: :click-to-load: not allowed with :autoplay:"
            )
        if "muted" in options and "autoplay" in options:
            raise self.error(
                "youtube: :muted: not allowed with :autoplay:, which is "
                "muted already"
            )
        config = self.state.document.settings.env.config
        if "privacy" in options and setting(config, "youtube_privacy"):
            raise self.error(
                "youtube: :privacy: is on already through youtube_privacy"
            )
        private = "privacy" in options or setting(config, "youtube_privacy")
        domain = (
            "https://www.youtube-nocookie.com"
            if private
            else "https://www.youtube.com"
        )
        # NOTE(xames3): Checkout more options at their website.
        # https://developers.google.com/youtube/player_parameters
        params = {
            "start": self.options.get("start-from", 0),
            "autoplay": 1 if "autoplay" in self.options else 0,
            "cc_load_policy": 1 if "show-captions" in self.options else 0,
            "rel": 0,
            "playsinline": 1,
        }
        if "hide-controls" in self.options:
            params["controls"] = 0
        if "end-at" in self.options:
            params["end"] = self.options["end-at"]
        if "loop" in self.options:
            params["loop"] = 1
            params["playlist"] = vid
        if "muted" in self.options or "autoplay" in self.options:
            params["mute"] = 1
        if "language" in self.options:
            params["hl"] = self.options["language"]
            params["cc_lang_pref"] = self.options["language"]
        url = f"{domain}/embed/{vid}?{urlparse.urlencode(params)}"
        self.options["classes"] = self.options.pop("class", [])
        self.options["url"] = url
        self.options["src"] = src
        self.options["watch"] = f"https://www.youtube.com/watch?v={vid}"
        self.options["video_id"] = vid
        self.options["facade"] = "click-to-load" in self.options
        self.options["private"] = bool(private)
        self.options["ratio"] = self.options.get("ratio", "").replace(
            ":", " / "
        )
        allow = str(setting(config, "youtube_allow")).split("; ")
        if "autoplay" in options or "click-to-load" in options:
            allow = [*dict.fromkeys([*allow, "autoplay"])]
        self.options["allow"] = "; ".join(allow)
        self.options["referrer"] = str(
            setting(config, "youtube_referrer_policy")
        )
        text = self.options.pop("caption", None) or "\n".join(self.content)
        caption, messages = parse(self, text.strip(), "caption")
        element = node("", caption, **self.options)
        named(self, element)
        return [element, *trail(self.options, ("src",)), *messages]


visit = visitor(template)
