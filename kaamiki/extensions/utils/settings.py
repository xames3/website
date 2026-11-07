"""\
Theme Settings
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 07 November 2026

Kaamiki's settings, their defaults and the helpers that read them.
"""

from __future__ import annotations

import copy
import json
import os
import os.path as p
import re
import typing as t
from datetime import datetime as dt

from sphinx.locale import _
from sphinx.util import logging

from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import icons
from kaamiki.extensions.utils.checks import fail

if t.TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Mapping

    from sphinx.application import Sphinx
    from sphinx.config import Config
    from sphinx.environment import BuildEnvironment

type Rule = Callable[[t.Any], object]

logger = logging.getLogger(__name__)

NAME: t.Final[str] = "kaamiki"
PREFIX: t.Final[str] = f"{NAME}_"
# NOTE(xames3): A rough average, adults read non-fiction at about
# 238 words a minute: https://doi.org/10.1016/j.jml.2019.104047
WORDS_PER_MINUTE: t.Final[int] = 238
TONES: t.Final[tuple[str, ...]] = ("red", "yellow", "blue", "green")
PALETTE: t.Final[dict[str, str]] = {
    "red": "357.87 68.98% 57%",
    "yellow": "38.9 100% 57.06%",
    "blue": "205.88 100% 50%",
    "green": "131.25 41.03% 45.88%",
}
CREDIT: t.Final[str] = "https://github.com/xames3/website"
BOUNDS: t.Final[dict[str, tuple[float, float]]] = {
    "avatar_size": (16, 64),
    "description_length": (50, 300),
    "gap": (0, 4),
    "interval": (2, 15),
    "logo_size": (8, 64),
    "margin": (0, 8),
    "pace": (24, 240),
    "show_more_after": (3, 8),
    "show_previous_next_cards_count": (1, 7),
    "start": (1, 10800),
    "ticker": (0, 999_999_999),
    "ticker_duration": (0.1, 5),
    "toctree_maxdepth": (0, 4),
    "underline_width": (0.5, 4),
    "underline_wobble": (0, 2),
    "code_explain_budget": (1, 100),
    "code_explain_limit": (1, 300),
    "code_explain_memory": (128, 4096),
    "code_explain_output_limit": (1, 128),
    "code_explain_timeout": (1, 60),
    "code_explain_lineno": (0, 10000),
    "words_per_minute": (100, 350),
}
GAPS: t.Final[float] = BOUNDS["gap"][1]
MARGINS: t.Final[float] = BOUNDS["margin"][1]
SHOW_MORE_AFTER: t.Final[int] = 5
RELATED_PAGES: t.Final[int] = 5
DESCRIPTION_LENGTH: t.Final[int] = 200
HEADER_LEAD_LENGTH: t.Final[int] = 90
HEADER_SUBTITLE_FIELD: t.Final[str] = "km-header-subtitle"
HEADER_NO_SUBTITLE_FIELD: t.Final[str] = "km-header-no-subtitle"
PROJECT: t.Final[dict[str, str]] = {
    "author": "",
    "avatar": "",
    "email": "",
    "source": "#",
}
FA_FREE: t.Final[str] = (
    "https://ka-f.fontawesome.com/releases/v7.3.1/css/free.min.css"
)
# NOTE(xames3): The hash of the stylesheet above, which has to be worked
# out again when the release changes: `openssl dgst -sha384 -binary
# free.min.css | openssl base64 -A`.
# https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity
FA_FREE_INTEGRITY: t.Final[str] = (
    "sha384-eX9o/tJQBecFQ7gYpZvr9Gkhl26eYO6KrYj5maf6JhoXmZ2sLSycaT48proNJxFq"
)
RELEASE_KINDS: t.Final[tuple[str, ...]] = (
    "added",
    "changed",
    "deprecated",
    "fixed",
    "removed",
)
DEFAULTS: t.Final[dict[str, t.Any]] = {
    "accordion_marker": "plus",
    "accordion_marker_position": "after",
    "button_colours": {},
    "button_icon_position": "before",
    "button_scheme": "light",
    "copy_headerlinks": True,
    "embed_css": [],
    "embed_iframe_hosts": [],
    "embed_js": [],
    "embed_js_loading": "defer",
    "fa_icons": {},
    "fa_kit": None,
    "fa_style": icons.DEFAULT_STYLE,
    "favicons": {},
    "feedback": {},
    "header_buttons": {},
    "internal_hosts": [],
    "last_updated_on_fmt": "",
    "license": {},
    "links_in_new_tab": True,
    "logo_size": None,
    "open_graph": {},
    "project": {},
    "release_kinds": {},
    "release_version_fmt": "%Y.%m.%d",
    "role_colours": {},
    "sharpie_colour": "yellow",
    "show_404": True,
    "show_breadcrumbs": True,
    "show_credit": False,
    "show_feedback": None,
    "show_more": True,
    "show_more_after": SHOW_MORE_AFTER,
    "show_page_last_updated": True,
    "show_previous_next_cards": True,
    "show_previous_next_cards_count": RELATED_PAGES,
    "show_previous_next_pages": False,
    "show_scrolltop": False,
    "show_searchbox": True,
    "show_sitemap": True,
    "toctree_in_header": True,
    "sidebar_buttons": {},
    "tab_icon_position": "before",
    "toctree_includehidden": True,
    "toctree_maxdepth": 0,
    "toctree_titles_only": True,
    "underline_colour": "#FF9800",
    "underline_width": 2.5,
    "underline_wobble": 1.0,
    "code_explain_budget": 25,
    "code_explain_cache": True,
    "code_explain_comprehensions": False,
    "code_explain_events": "line, return",
    "code_explain_limit": 100,
    "code_explain_memory": 1024,
    "code_explain_output_limit": 64,
    "code_explain_python": None,
    "code_explain_pythonpath": [],
    "code_explain_run": False,
    "code_explain_timeout": 10,
    "words_per_minute": WORDS_PER_MINUTE,
    "youtube_allow": (
        "accelerometer; clipboard-write; encrypted-media; gyroscope;"
        " picture-in-picture; web-share"
    ),
    "youtube_click_to_load": True,
    "youtube_privacy": True,
    "youtube_referrer_policy": "strict-origin-when-cross-origin",
}
GROUPS: t.Final[dict[str, dict[str, str]]] = {
    "icons": {
        "style": "fa_style",
        "kit": "fa_kit",
        "names": "fa_icons",
    },
    "show": {
        "not_found": "show_404",
        "breadcrumbs": "show_breadcrumbs",
        "credit": "show_credit",
        "feedback": "show_feedback",
        "more": "show_more",
        "more_after": "show_more_after",
        "page_last_updated": "show_page_last_updated",
        "previous_next_cards": "show_previous_next_cards",
        "previous_next_cards_count": "show_previous_next_cards_count",
        "previous_next_pages": "show_previous_next_pages",
        "scrolltop": "show_scrolltop",
        "searchbox": "show_searchbox",
        "sitemap": "show_sitemap",
    },
    "toctree": {
        "in_header": "toctree_in_header",
        "includehidden": "toctree_includehidden",
        "maxdepth": "toctree_maxdepth",
        "titles_only": "toctree_titles_only",
    },
    "code_explain": {
        "budget": "code_explain_budget",
        "cache": "code_explain_cache",
        "comprehensions": "code_explain_comprehensions",
        "events": "code_explain_events",
        "limit": "code_explain_limit",
        "memory": "code_explain_memory",
        "output_limit": "code_explain_output_limit",
        "python": "code_explain_python",
        "pythonpath": "code_explain_pythonpath",
        "run": "code_explain_run",
        "timeout": "code_explain_timeout",
    },
    "youtube": {
        "allow": "youtube_allow",
        "click_to_load": "youtube_click_to_load",
        "privacy": "youtube_privacy",
        "referrer_policy": "youtube_referrer_policy",
    },
    "accordion": {
        "marker": "accordion_marker",
        "marker_position": "accordion_marker_position",
    },
    "button": {
        "colours": "button_colours",
        "icon_position": "button_icon_position",
        "scheme": "button_scheme",
    },
    "tab": {"icon_position": "tab_icon_position"},
    "embed": {
        "css": "embed_css",
        "iframe_hosts": "embed_iframe_hosts",
        "js": "embed_js",
        "js_loading": "embed_js_loading",
    },
    "links": {
        "internal_hosts": "internal_hosts",
        "new_tab": "links_in_new_tab",
    },
    "roles": {
        "colours": "role_colours",
        "sharpie_colour": "sharpie_colour",
        "underline_colour": "underline_colour",
        "underline_width": "underline_width",
        "underline_wobble": "underline_wobble",
    },
    "release": {"kinds": "release_kinds", "version_fmt": "release_version_fmt"},
    "site": {
        "project": "project",
        "license": "license",
        "open_graph": "open_graph",
        "favicons": "favicons",
        "logo_size": "logo_size",
        "feedback": "feedback",
        "header_buttons": "header_buttons",
        "sidebar_buttons": "sidebar_buttons",
        "last_updated_fmt": "last_updated_on_fmt",
        "copy_headerlinks": "copy_headerlinks",
        "words_per_minute": "words_per_minute",
    },
}
PATHS: t.Final[dict[str, str]] = {
    key: f"{NAME}.conf.{group}.{attr}"
    for group, members in GROUPS.items()
    for attr, key in members.items()
}
FLAT: t.Final[dict[str, str]] = {
    path.replace(".conf.", "_").replace(".", "_"): key
    for key, path in PATHS.items()
}
PARSE_TIME: t.Final[tuple[str, ...]] = (
    "accordion_marker",
    "accordion_marker_position",
    "button_colours",
    "button_icon_position",
    "button_scheme",
    "embed_iframe_hosts",
    "fa_kit",
    "fa_style",
    "internal_hosts",
    "links_in_new_tab",
    "project",
    "release_kinds",
    "release_version_fmt",
    "role_colours",
    "sharpie_colour",
    "tab_icon_position",
    "underline_colour",
    "underline_width",
    "underline_wobble",
    "code_explain_budget",
    "code_explain_cache",
    "code_explain_comprehensions",
    "code_explain_events",
    "code_explain_limit",
    "code_explain_memory",
    "code_explain_output_limit",
    "code_explain_python",
    "code_explain_pythonpath",
    "code_explain_run",
    "code_explain_timeout",
    "youtube_allow",
    "youtube_click_to_load",
    "youtube_privacy",
    "youtube_referrer_policy",
)
PAGE_SWITCHES: t.Final[tuple[str, ...]] = (
    "show_breadcrumbs",
    "show_credit",
    "show_feedback",
    "show_more",
    "show_page_last_updated",
    "show_previous_next_cards",
    "show_previous_next_pages",
    "show_scrolltop",
    "show_searchbox",
    "toctree_in_header",
)
WHOLE_NUMBERS: t.Final[tuple[str, ...]] = (
    "show_more_after",
    "show_previous_next_cards_count",
    "words_per_minute",
    "logo_size",
    "toctree_maxdepth",
    "code_explain_budget",
    "code_explain_limit",
    "code_explain_memory",
    "code_explain_output_limit",
    "code_explain_timeout",
)
REAL_NUMBERS: t.Final[tuple[str, ...]] = ("underline_width", "underline_wobble")
ALIGNMENTS: t.Final[tuple[str, ...]] = ("left", "center", "right")
SIZES: t.Final[tuple[str, ...]] = ("small", "medium", "large")
CHOICES: t.Final[dict[str, tuple[str, ...]]] = {
    "accordion_marker": ("plus", "down", "right"),
    "accordion_marker_position": ("before", "after"),
    "button_icon_position": ("before", "after"),
    "embed_js_loading": ("defer", "async", "normal"),
    "fa_style": ("solid", "regular", "light", "thin"),
    "tab_icon_position": ("before", "after"),
}


TRACE_EVENTS: t.Final[tuple[str, ...]] = ("call", "line", "return")
SCHEMES: t.Final[tuple[str, ...]] = ("light", "dark", "chevron", *TONES)
REFERRERS: t.Final[tuple[str, ...]] = (
    "no-referrer",
    "no-referrer-when-downgrade",
    "origin",
    "origin-when-cross-origin",
    "same-origin",
    "strict-origin",
    "strict-origin-when-cross-origin",
    "unsafe-url",
)
PERMISSIONS: t.Final[tuple[str, ...]] = (
    "accelerometer",
    "autoplay",
    "clipboard-write",
    "encrypted-media",
    "fullscreen",
    "gyroscope",
    "picture-in-picture",
    "web-share",
)
UNREAD_OPTIONS: t.Final[tuple[str, ...]] = (
    "body_max_width",
    "body_min_width",
    "globaltoc_collapse",
    "globaltoc_includehidden",
    "globaltoc_maxdepth",
    "nosidebar",
    "sidebarwidth",
)
CARDS: t.Final[tuple[str, ...]] = ("summary", "summary_large_image")
FAVICONS: t.Final[tuple[str, ...]] = (
    "manifest",
    "size_96",
    "size_180",
    "size_svg",
)
TIME_DIRECTIVES: t.Final[re.Pattern[str]] = re.compile(r"%[aAbBdHIjmMpSyYZz%]")


def boolean(value: object) -> None:
    """Check a setting is `True` or `False` and nothing like them."""
    if type(value) is not bool:
        raise TypeError(f"expected True or False, got {value!r}")


def whole(low: float, high: float) -> Rule:
    """Make a check for a whole number from `low` to `high`."""

    def rule(value: t.Any) -> None:
        """Check the whole number."""
        if type(value) is not int:
            raise TypeError(f"expected a whole number, got {value!r}")
        if not low <= value <= high:
            raise ValueError(f"expected {low:g} to {high:g}, got {value}")

    return rule


def real(low: float, high: float) -> Rule:
    """Make a check for a number from `low` to `high`."""

    def rule(value: t.Any) -> None:
        """Check the number."""
        if type(value) not in (int, float):
            raise TypeError(f"expected a number, got {value!r}")
        if not low <= value <= high:
            raise ValueError(f"expected {low:g} to {high:g}, got {value:g}")

    return rule


def string(read: Callable[[str], t.Any]) -> Rule:
    """Make a check for a string that `read` accepts."""

    def rule(value: t.Any) -> None:
        """Check the string and read it."""
        if not isinstance(value, str):
            raise TypeError(f"expected a string, got {value!r}")
        read(value)

    return rule


def many(read: Callable[[str], t.Any]) -> Rule:
    """Make a check for a list of strings that `read` accepts."""

    def rule(value: t.Any) -> None:
        """Check each string in the list, and that none is twice."""
        if not isinstance(value, (list, tuple)):
            raise TypeError(f"expected a list, got {value!r}")
        for each in value:
            if not isinstance(each, str):
                raise TypeError(f"expected a list of strings, got {each!r}")
            read(each)
        if len(set(value)) != len(value):
            raise ValueError("expected a list with nothing twice")

    return rule


def table(key: Callable[[str], t.Any], read: Rule) -> Rule:
    """Make a check for a dict whose keys `key` and values `read`
    accept.
    """

    def rule(value: t.Any) -> None:
        """Check each name and each value of the dict."""
        if not isinstance(value, dict):
            raise TypeError(f"expected a dict, got {value!r}")
        for name, each in value.items():
            if not isinstance(name, str):
                raise TypeError(
                    f"expected names that are strings, got {name!r}"
                )
            key(name)
            try:
                read(each)
            except (TypeError, ValueError) as error:
                raise ValueError(f"{name!r}: {error}") from error

    return rule


def shape(**fields: Rule) -> Rule:
    """Make a check for a dict that has only the fields named."""

    def rule(value: t.Any) -> None:
        """Check each field of the dict."""
        if not isinstance(value, dict):
            raise TypeError(f"expected a dict, got {value!r}")
        for name, each in value.items():
            if name not in fields:
                raise ValueError(
                    f"{name!r} is not one of {', '.join(sorted(fields))}"
                )
            try:
                fields[name](each)
            except (TypeError, ValueError) as error:
                raise ValueError(f"{name!r}: {error}") from error

    return rule


def lower(read: Callable[[str | None], t.Any]) -> Callable[[str], t.Any]:
    """Make a check for a name that has to be written in lowercase."""

    def rule(value: str) -> t.Any:
        """Check the name is lowercase and read it."""
        if value != value.lower():
            raise ValueError(f"expected {value.lower()!r}, names are lowercase")
        return read(value)

    return rule


def moment(directives: re.Pattern[str]) -> Callable[[str], None]:
    """Make a check for a date format that only has known directives."""

    def rule(value: str) -> None:
        """Check the format has only known date directives."""
        left = directives.sub("", value)
        if "%" in left:
            raise ValueError(
                f"expected a date format with %a %A %b %B %d %H %I %j %m %M"
                f" %p %S %y %Y %Z %z, got {value!r}"
            )

    return rule


def ending(suffix: str, read: Callable[[str], t.Any]) -> Callable[[str], str]:
    """Make a check for an address or a file name ending a certain way."""

    def check(value: str) -> str:
        """Check the value and what it ends with."""
        read(value)
        if not value.endswith(suffix):
            raise ValueError(f"expected a name ending {suffix}, got {value!r}")
        return value

    return check


def listed_in(
    allowed: tuple[str, ...], separator: str
) -> Callable[[str], None]:
    """Make a check for a string of words joined by `separator`."""

    def read(value: str) -> None:
        """Check each word of the string."""
        for each in value.split(separator):
            checks.word(*allowed)(each)

    return read


EMAIL_ONLY: t.Final = checks.pattern(checks.EMAIL, "an email address")
STATIC_NAME: t.Final = checks.pattern(checks.FILE, "a file name")
ATTRIBUTES: t.Final = checks.pattern(
    r"(?:(?:data|aria)-[a-z][\w:-]*=(?:\"[^\"<>]*\"|'[^'<>]*')\s*)+",
    'data or aria attributes like data-x="y"',
)
OG_LOCALE: t.Final = checks.pattern(
    r"[a-z]{2,3}_[A-Z]{2}", "a locale like en_GB"
)
OG_TYPES: t.Final[tuple[str, ...]] = (
    "website",
    "article",
    "book",
    "profile",
    "music.song",
    "music.album",
    "music.playlist",
    "music.radio_station",
    "video.movie",
    "video.episode",
    "video.tv_show",
    "video.other",
)
OG_TYPE: t.Final = checks.word(*OG_TYPES)
TWITTER_HANDLE: t.Final = checks.pattern(
    r"@[A-Za-z0-9_]{1,15}", "a handle like @xames3"
)


def role_icon(value: t.Any) -> None:
    """Check one icon a site sets, as a name or as a Pro and Free pair."""
    if not isinstance(value, dict):
        string(checks.icon)(value)
        return
    shape(pro=string(checks.icon), free=string(checks.icon))(value)
    if not value:
        raise ValueError("expected a pro or a free icon, got neither")
    if "free" in value:
        try:
            icons.Icons().classes(value["free"])
        except ValueError as error:
            raise ValueError(f"'free': {error}") from error


def site_icons(value: t.Any) -> None:
    """Check the icons a site sets, which only `BLANK_ROLES` may leave
    empty.
    """
    if isinstance(value, dict):
        value = {
            key: each
            for key, each in value.items()
            if each != "" or key not in icons.BLANK_ROLES
        }
    table(checks.word(*icons.ROLE_ICONS), role_icon)(value)


def button(value: t.Any) -> None:
    """Check a header or sidebar button."""
    if not isinstance(value, dict) or "url" not in value:
        raise ValueError("expected a dict with a url")
    shape(
        url=string(checks.link),
        icon=string(checks.icon),
        extras=string(lambda _: ATTRIBUTES(_.strip())),
    )(value)


RULES: t.Final[dict[str, Rule]] = {
    "accordion_marker": checks.word(*CHOICES["accordion_marker"]),
    "accordion_marker_position": checks.word(
        *CHOICES["accordion_marker_position"]
    ),
    "button_icon_position": checks.word(*CHOICES["button_icon_position"]),
    "copy_headerlinks": boolean,
    "embed_js_loading": checks.word(*CHOICES["embed_js_loading"]),
    "fa_style": checks.word(*CHOICES["fa_style"]),
    "links_in_new_tab": boolean,
    "tab_icon_position": checks.word(*CHOICES["tab_icon_position"]),
    "show_404": boolean,
    "show_breadcrumbs": boolean,
    "show_credit": boolean,
    "show_more": boolean,
    "show_page_last_updated": boolean,
    "show_previous_next_cards": boolean,
    "show_previous_next_pages": boolean,
    "show_scrolltop": boolean,
    "show_searchbox": boolean,
    "show_sitemap": boolean,
    "toctree_in_header": boolean,
    "toctree_includehidden": boolean,
    "toctree_titles_only": boolean,
    "code_explain_cache": boolean,
    "code_explain_comprehensions": boolean,
    "code_explain_run": boolean,
    "youtube_click_to_load": boolean,
    "youtube_privacy": boolean,
    "show_feedback": boolean,
    **{key: whole(*BOUNDS[key]) for key in WHOLE_NUMBERS},
    **{key: real(*BOUNDS[key]) for key in REAL_NUMBERS},
    "button_scheme": string(checks.text),
    "sharpie_colour": string(checks.text),
    "underline_colour": string(checks.text),
    "fa_kit": string(checks.kit),
    "last_updated_on_fmt": string(moment(TIME_DIRECTIVES)),
    "release_version_fmt": string(moment(TIME_DIRECTIVES)),
    "code_explain_events": string(listed_in(TRACE_EVENTS, ", ")),
    "youtube_allow": string(listed_in(PERMISSIONS, "; ")),
    "youtube_referrer_policy": checks.word(*REFERRERS),
    "internal_hosts": many(checks.host),
    "embed_iframe_hosts": many(checks.host),
    "embed_css": many(ending(".css", STATIC_NAME)),
    "embed_js": many(ending(".js", STATIC_NAME)),
    "code_explain_pythonpath": many(checks.text),
    "code_explain_python": string(checks.text),
    "button_colours": table(lower(checks.slug), string(checks.colour)),
    "role_colours": table(lower(checks.slug), string(checks.colour)),
    "release_kinds": table(lower(checks.slug), checks.word(*TONES)),
    "fa_icons": site_icons,
    "favicons": shape(**dict.fromkeys(FAVICONS, string(STATIC_NAME))),
    "header_buttons": table(checks.text, button),
    "sidebar_buttons": table(checks.text, button),
    "license": shape(name=string(checks.text), url=string(checks.web)),
    "feedback": shape(
        type=checks.word("mail", "link"),
        url=string(checks.link),
        subject=string(checks.text),
        title=string(checks.text),
        description=string(checks.text),
        button=string(checks.text),
        icon=string(checks.icon),
        split=boolean,
    ),
    "open_graph": shape(
        card=checks.word(*CARDS),
        description=string(checks.text),
        description_length=whole(*BOUNDS["description_length"]),
        enable=boolean,
        image=string(checks.link),
        image_alt=string(checks.text),
        locale=string(OG_LOCALE),
        site_name=string(checks.text),
        twitter_site=string(TWITTER_HANDLE),
        type=string(OG_TYPE),
    ),
    "project": shape(
        author=string(checks.text),
        avatar=string(checks.link),
        email=string(EMAIL_ONLY),
        source=string(lambda _: _ if _ == "#" else checks.web(_)),
    ),
}


def stored[V](env: BuildEnvironment, key: str, default: V) -> V:
    """Hold something Kaamiki keeps on the build environment.

    It is pickled with the environment, so it is there for the next
    build, and it is prefixed `km_` so it can't be mistaken for
    Sphinx's.

    :param env: The build environment.
    :param key: What it's called, without the prefix.
    :param default: What to hold when nothing is yet.
    :return: What is held, which the caller may change.
    """
    held: V = env.__dict__.setdefault(f"km_{key}", default)
    return held


def kept[V](env: BuildEnvironment, key: str, value: V) -> V | None:
    """Replace something Kaamiki keeps on the build environment.

    :param env: The build environment.
    :param key: What it's called, without the prefix.
    :param value: What to hold from now on.
    :return: What was held at the last build, or `None` at the first.
    """
    before = env.__dict__.get(f"km_{key}")
    env.__dict__[f"km_{key}"] = value
    return before


def option(key: str) -> str:
    """Spell a setting the way `conf.py` writes it.

    :param key: The setting's name without the prefix, `show_more`.
    :return: Its place on `kaamiki.conf`, `kaamiki.conf.show.more`.
    """
    return PATHS[key]


def flat(key: str) -> str:
    """Spell a setting the way Sphinx and a `-D` know it.

    :param key: The setting's name without the prefix, `show_more`.
    :return: Its name in Sphinx's configuration, the group and the name
        joined by underscores, `kaamiki_show_more`.
    """
    return PATHS[key].replace(".conf.", "_").replace(".", "_")


def register(app: Sphinx) -> None:
    """Make every setting a Sphinx configuration value.

    Sphinx then knows the name, hands Kaamiki the default and sends
    pages back through reading, or writing, when the value changes.
    Kaamiki checks the values itself, so Sphinx is asked to leave their
    types alone.

    :param app: The Sphinx application instance.
    """
    for key, default in DEFAULTS.items():
        value: t.Any = copy.deepcopy(default)
        if key in REAL_NUMBERS:
            value = _constant(value)
        app.add_config_value(
            flat(key),
            value,
            "env" if key in PARSE_TIME else "html",
            types=t.Any,
        )


def site_values(config: Config) -> dict[str, t.Any]:
    """Collect what a site's `conf.py` and `-D` wrote.

    Sphinx has no public way to read what `conf.py` wrote as opposed to
    what it knows, so this reaches for `_raw_config`. Every check of a
    setting starts from the names found here, and so does Sphinx's
    credit, so a Sphinx that moves it stops the build and doesn't let
    wrong settings through.

    :param config: The Sphinx configuration.
    :return: The names and their values, a `-D` over what `conf.py` said.
    :raises KaamikiError: When this Sphinx has no `_raw_config`.
    """
    raw: dict[str, t.Any] | None = getattr(config, "_raw_config", None)
    if raw is None:
        fail(
            "this Sphinx has no Config._raw_config, which Kaamiki reads to"
            " check what conf.py wrote; use a Sphinx that Kaamiki supports"
            f" or report it at {CREDIT}/issues"
        )
    return {**raw, **config.overrides}


def pair(app: Sphinx) -> None:
    """Stop unless the extension and the theme are used together.

    :param app: The Sphinx application instance.
    :raises KaamikiError: For `html_theme = "kaamiki"` without
        `kaamiki` in `extensions` and for `kaamiki` in `extensions`
        with any other `html_theme`.
    """
    config = app.config
    conf = p.join(app.confdir, "conf.py")
    if NAME not in config.extensions:
        fail(
            f"extensions: expected {NAME!r} in it, the {NAME} theme needs"
            f" its extension, so add {NAME!r} to extensions in conf.py",
            conf,
        )
    if config.html_theme != NAME:
        fail(
            f"html_theme: expected {NAME!r} because {NAME!r} is in"
            f" extensions, got {config.html_theme!r}. The extension only"
            f" works with its own theme, so set html_theme = {NAME!r} in"
            " conf.py",
            conf,
        )


def switch(argument: str) -> bool:
    """Read a switch a `-D` gave, `0` or `1` as Sphinx's own are.

    :param argument: The value as written.
    :return: Whether it's on.
    :raises ValueError: For anything else.
    """
    if argument not in ("0", "1"):
        raise ValueError(f"expected 0 or 1, got {argument!r}")
    return argument == "1"


ENTRIES: t.Final[dict[tuple[str, str], Callable[[str], t.Any]]] = {
    ("feedback", "split"): switch,
    ("open_graph", "description_length"): checks.integer(
        *map(int, BOUNDS["description_length"])
    ),
    ("open_graph", "enable"): switch,
}


def overrides(app: Sphinx, config: Config) -> None:
    """Read the numbers and switches a `-D` on the command line gave.

    Sphinx reads a `-D` by the type of the setting's default, so a
    setting with no default to go by (`None`) or a number with a
    point arrives as text. A number is read the way an option's is, by
    `checks.integer` or `checks.number`, and a switch is `0` or `1`.

    A `-D name.key=value` has been moved into the setting's dictionary
    by now, as text, so the entries of `ENTRIES` that are switches or
    numbers are read there.

    :param app: The Sphinx application instance.
    :param config: The Sphinx configuration.
    :raises KaamikiError: For a value that isn't one the setting takes.
    """
    del app
    for key, rule in RULES.items():
        name = flat(key)
        value = config.overrides.get(name)
        if not isinstance(value, str):
            continue
        read: Callable[[str], t.Any]
        if rule is boolean:
            read = switch
        elif key in WHOLE_NUMBERS:
            read = checks.integer(*map(int, BOUNDS[key]))
        elif key in REAL_NUMBERS:
            read = checks.number(*BOUNDS[key])
        else:
            continue
        try:
            config[name] = read(value)
        except ValueError as error:
            fail(f"-D {name}={value}: {error}")
    for (key, entry), read in ENTRIES.items():
        found = config[flat(key)]
        value = found.get(entry) if isinstance(found, dict) else None
        if isinstance(value, str):
            try:
                found[entry] = read(value)
            except ValueError as error:
                fail(f"-D {flat(key)}.{entry}={value}: {error}")


def _constant(value: t.Any) -> Callable[[Config], t.Any]:
    """Wrap a default in a function, which Sphinx calls for the value.

    A float's plain default makes Sphinx drop a `-D` for it with a
    warning, where a function's lets the text through.

    :param value: The default.
    :return: A function that returns it.
    """
    return lambda _: value


class Group:
    """One group of Kaamiki's settings, `kaamiki.conf.icons` for one."""

    def __init__(self, name: str, given: dict[str, t.Any]) -> None:
        """Make the group, which shares what a site set with the
        others.
        """
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_given", given)

    def _key(self, attr: str) -> str:
        """Find the setting an attribute stands for."""
        members = GROUPS[self._name]
        if attr not in members:
            raise AttributeError(
                f"{type(self).__name__!r} object has no attribute {attr!r}",
                name=attr,
                obj=self,
            )
        return members[attr]

    def __getattr__(self, attr: str) -> t.Any:
        """Read what a site set, or Kaamiki's own default."""
        key = self._key(attr)
        if key in self._given:
            return self._given[key]
        value = DEFAULTS[key]
        if isinstance(value, dict | list):
            return self._given.setdefault(key, copy.deepcopy(value))
        return value

    def __setattr__(self, attr: str, value: t.Any) -> None:
        """Check a setting the moment a site sets it."""
        key = self._key(attr)
        _check_value(key, value, "")
        self._given[key] = value

    def __dir__(self) -> list[str]:
        """List the settings of the group."""
        return list(GROUPS[self._name])

    def __repr__(self) -> str:
        """Show the settings the group has."""
        return f"<{NAME}.conf.{self._name}: {', '.join(GROUPS[self._name])}>"


class IconSettings(Group):
    """The group of settings about icons."""

    names: dict[str, str]

    def update(
        self, names: Mapping[str, str] | None = None, /, **more: str
    ) -> None:
        """Add to Kaamiki's icon names, so a site lists the ones it
        changes.

        :param names: Icon names and the icons they take.
        :param more: The same, as keywords.
        """
        self.names = {**self.names, **(names or {}), **more}


class Conf:
    """Every setting of Kaamiki, which `conf.py` sets with
    `kaamiki.conf`.
    """

    given: dict[str, t.Any]
    icons: IconSettings
    show: Group
    toctree: Group
    code_explain: Group
    youtube: Group
    accordion: Group
    button: Group
    tab: Group
    embed: Group
    links: Group
    roles: Group
    release: Group
    site: Group

    def __init__(self) -> None:
        """Make the object with every group in it."""
        given: dict[str, t.Any] = {}
        object.__setattr__(self, "given", given)
        for name in GROUPS:
            made = IconSettings if name == "icons" else Group
            object.__setattr__(self, name, made(name, given))

    def __setattr__(self, name: str, value: t.Any) -> None:
        """Refuse a group that isn't there and a group set as a whole."""
        if name in GROUPS:
            raise AttributeError(
                f"{NAME}.conf.{name} is a group, set one of its settings"
            )
        raise AttributeError(f"{NAME}.conf has no group {name!r}")

    def __dir__(self) -> list[str]:
        """List the groups."""
        return list(GROUPS)

    def __repr__(self) -> str:
        """Show the groups."""
        return f"<{NAME}.conf: {', '.join(GROUPS)}>"


CONF: t.Final[Conf] = Conf()


def apply(app: Sphinx, config: Config) -> None:
    """Hand what `conf.py` set on `kaamiki.conf` to Sphinx.

    A `-D` on the command line wins over `conf.py`, as it does for
    Sphinx's own settings.

    :param app: The Sphinx application instance.
    :param config: The Sphinx configuration.
    """
    del app
    for key, value in CONF.given.items():
        if flat(key) not in config.overrides:
            config[flat(key)] = copy.deepcopy(value)


def validate(app: Sphinx) -> None:
    """Check every setting a site gave Kaamiki.

    :param app: The Sphinx application instance.
    :raises KaamikiError: For the first thing wrong. `_read` refuses a
        `kaamiki_` name written in `conf.py`, a `-D` for a name that
        isn't one of Kaamiki's and a value that is `None` or of the
        wrong type, spelling or range. The other `_check_` helpers
        refuse an icon or a colour Kaamiki can't draw, Sphinx's own
        `html_baseurl` and `html_last_updated_fmt` written wrongly, the
        `KAAMIKI_FA_KIT` environment variable, settings that contradict
        each other, a file that isn't in `html_static_path`, a folder
        or a Python that isn't there, a date format that can't be read
        back and a theme option the sidebar doesn't read.
    """
    config = app.config
    conf = p.join(app.confdir, "conf.py")
    given = _read(config, conf)
    _check_kit(given, conf)
    _check_icons(config, given, conf)
    _check_colours(given, conf)
    _check_site(config, conf)
    _check_buttons(given, conf)
    _check_pairs(config, given, conf)
    _check_static(app, given, conf)
    _check_theme(config, conf)
    _check_code_explain(app, given, conf)
    _check_dates(given, conf)
    _check_translation(app, given, conf)


def _read(config: Config, conf: str) -> dict[str, t.Any]:
    """Read the settings a site gave, refusing the ones that aren't
    right.

    Settings are set on `kaamiki.conf`, which `apply` has handed to
    Sphinx by now, or with a `-D`. A `kaamiki_` name written in
    `conf.py` is none of them.
    """
    given: dict[str, t.Any] = {}
    for name, value in site_values(config).items():
        if not name.startswith(PREFIX) or name in config.overrides:
            continue
        key = FLAT.get(name)
        if (
            key is not None
            and isinstance(DEFAULTS[key], dict)
            and isinstance(value, dict)
            and all(isinstance(_, str) for _ in value.values())
        ):
            given[key] = config[name]
            continue
        fail(f"{name} is not a Kaamiki setting", conf)
    for key in CONF.given:
        if flat(key) not in config.overrides:
            given[key] = config[flat(key)]
    for name in sorted(config.overrides):
        if not name.startswith(PREFIX):
            continue
        if name not in FLAT:
            fail(f"{name} is not a Kaamiki setting", conf)
        given[FLAT[name]] = config[name]
    for key, value in given.items():
        _check_value(key, value, conf)
    return given


def _check_value(key: str, value: t.Any, conf: str) -> None:
    """Check one setting against its rule."""
    if value is None:
        if DEFAULTS[key] is not None:
            fail(f"{option(key)} is None, leave it out for the default", conf)
        return
    try:
        RULES[key](value)
    except (TypeError, ValueError) as error:
        fail(f"{option(key)}: {error}", conf)


def _check_kit(given: dict[str, t.Any], conf: str) -> None:
    """Check the Font Awesome kit an environment variable names."""
    kit = os.environ.get(icons.KIT_VARIABLE)
    if kit and not given.get("fa_kit"):
        try:
            string(checks.kit)(kit)
        except (TypeError, ValueError) as error:
            fail(f"environment variable {icons.KIT_VARIABLE}: {error}", conf)


def _check_icons(config: Config, given: dict[str, t.Any], conf: str) -> None:
    """Check every icon a setting names."""
    drawn = icons.Icons.of(config)
    for key, each in given.get("fa_icons", {}).items():
        try:
            drawn.custom(each)
        except ValueError as error:
            fail(f"kaamiki.conf.icons.names[{key!r}]: {error}", conf)
    for place, spec in (
        ("feedback", given.get("feedback", {}).get("icon")),
        *(
            (f"{kind}[{name!r}]", each.get("icon"))
            for kind in ("header_buttons", "sidebar_buttons")
            for name, each in given.get(kind, {}).items()
        ),
    ):
        try:
            drawn.custom(spec)
        except ValueError as error:
            fail(f"{NAME}.conf.site.{place}: icon: {error}", conf)


def _check_colours(given: dict[str, t.Any], conf: str) -> None:
    """Check the colours a role is drawn in."""
    colours = {**given.get("role_colours", {})}
    for key in ("sharpie_colour", "underline_colour"):
        if key in given:
            try:
                checks.colour(given[key], (*TONES, *colours))
            except (TypeError, ValueError) as error:
                fail(f"{option(key)}: {error}", conf)


def _check_site(config: Config, conf: str) -> None:
    """Check the Sphinx values Kaamiki reads, the address and the
    date.
    """
    base = config.html_baseurl
    if base:
        try:
            checks.site(base)
        except (TypeError, ValueError) as error:
            fail(f"html_baseurl: {error}", conf)
    stamp = config.html_last_updated_fmt
    if stamp:
        try:
            moment(TIME_DIRECTIVES)(stamp)
        except (TypeError, ValueError) as error:
            fail(f"html_last_updated_fmt: {error}", conf)


def _check_buttons(given: dict[str, t.Any], conf: str) -> None:
    """Check the button scheme and the colours a site adds."""
    scheme = given.get("button_scheme")
    if scheme is not None and scheme not in (
        *SCHEMES,
        *given.get("button_colours", {}),
    ):
        fail(
            f"kaamiki.conf.button.scheme: expected {', '.join(SCHEMES)}"
            f" or a name in kaamiki.conf.button.colours, got {scheme!r}",
            conf,
        )
    for key, own, noun in (
        ("button_colours", SCHEMES, "colours"),
        ("role_colours", TONES, "colours"),
        ("release_kinds", RELEASE_KINDS, "groups"),
    ):
        for name in given.get(key, {}):
            if name in own:
                fail(
                    f"{option(key)}: {name!r} is one of Kaamiki's own {noun}",
                    conf,
                )


def _check_pairs(config: Config, given: dict[str, t.Any], conf: str) -> None:
    """Check the settings that only make sense together."""
    feedback = given.get("feedback", {})
    if feedback and given.get("show_feedback") is False:
        fail(
            "kaamiki.conf.site.feedback is set but"
            " kaamiki.conf.show.feedback is False",
            conf,
        )
    if given.get("show_feedback") is True and not (
        given.get("project", {}).get("email") or feedback.get("url")
    ):
        fail(
            "kaamiki.conf.show.feedback is True but there is nowhere to send"
            " feedback: set an email in kaamiki.conf.site.project or a url in"
            " kaamiki.conf.site.feedback",
            conf,
        )
    if feedback.get("split") and not (
        given.get("project", {}).get("email") or feedback.get("url")
    ):
        fail(
            "kaamiki.conf.site.feedback: split needs a button, set an email in"
            " kaamiki.conf.site.project or a url",
            conf,
        )
    if "show_more_after" in given and given.get("show_more") is False:
        fail(
            "kaamiki.conf.show.more_after is set but"
            " kaamiki.conf.show.more is False",
            conf,
        )
    if (
        "show_previous_next_cards_count" in given
        and given.get("show_previous_next_cards") is False
    ):
        fail(
            "kaamiki.conf.show.previous_next_cards_count is set but"
            " kaamiki.conf.show.previous_next_cards is False",
            conf,
        )
    if "show_previous_next_cards_count" in given and given.get(
        "show_previous_next_pages"
    ):
        fail(
            "kaamiki.conf.show.previous_next_cards_count is set but"
            " kaamiki.conf.show.previous_next_pages is True, which shows the"
            " buttons and no cards",
            conf,
        )
    if given.get("show_previous_next_cards") is False and not given.get(
        "show_previous_next_pages"
    ):
        fail(
            "kaamiki.conf.show.previous_next_cards and"
            " kaamiki.conf.show.previous_next_pages are both off, a page"
            " needs one of them to lead on, so turn the buttons on",
            conf,
        )
    if feedback.get("type") == "link" and "url" not in feedback:
        fail("kaamiki.conf.site.feedback: type 'link' needs a url", conf)
    if "url" in feedback and feedback.get("type") != "link":
        fail("kaamiki.conf.site.feedback: a url needs type 'link'", conf)
    terms = given.get("license", {})
    if "url" in terms and "name" not in terms:
        fail("kaamiki.conf.site.license: a url needs a name", conf)
    style = given.get("fa_style")
    if style in ("light", "thin") and not icons.Icons.of(config).kit:
        fail(
            f"kaamiki.conf.icons.style: {style!r} needs a Font Awesome Pro"
            f" kit, set kaamiki.conf.icons.kit or {icons.KIT_VARIABLE}",
            conf,
        )
    drawn = config.html_theme_options.get("logo") or config.html_logo
    if given.get("logo_size") is not None and not drawn:
        fail(
            "kaamiki.conf.site.logo_size is set but the site has no logo, set"
            " html_theme_options['logo'] or html_logo",
            conf,
        )


def _check_static(app: Sphinx, given: dict[str, t.Any], conf: str) -> None:
    """Check the files a site names are in `html_static_path`."""
    statics = [p.join(app.confdir, _) for _ in app.config.html_static_path]

    def present(name: str) -> bool:
        """Say whether a static folder has the file."""
        return any(p.isfile(p.join(_, name)) for _ in statics)

    logo = app.config.html_theme_options.get("logo")
    if logo not in (None, ""):
        if not isinstance(logo, str):
            fail(
                f"html_theme_options['logo']: expected a file name, got "
                f"{logo!r}",
                conf,
            )
        try:
            STATIC_NAME(logo)
        except ValueError as error:
            fail(f"html_theme_options['logo']: {error}", conf)
        if not present(logo):
            fail(
                f"html_theme_options['logo']: {logo!r} is not in"
                " html_static_path",
                conf,
            )
    for key, found in (
        ("embed_css", given.get("embed_css", [])),
        ("embed_js", given.get("embed_js", [])),
        ("favicons", given.get("favicons", {}).values()),
    ):
        for name in found:
            if not present(name):
                fail(
                    f"{option(key)}: {name!r} is not in html_static_path", conf
                )


def _check_theme(config: Config, conf: str) -> None:
    """Check the theme options are ones Kaamiki's sidebar reads."""
    for name in UNREAD_OPTIONS:
        if name in config.html_theme_options:
            fail(
                f"html_theme_options[{name!r}]: Kaamiki's sidebar is fixed,"
                " so this changes nothing, and the navigation is set with the"
                " kaamiki.conf.toctree settings",
                conf,
            )


def _check_code_explain(
    app: Sphinx, given: dict[str, t.Any], conf: str
) -> None:
    """Check the folders and Python a `code-explain` is run with."""
    for entry in given.get("code_explain_pythonpath", []):
        if not p.isdir(p.join(app.srcdir, entry)):
            fail(
                f"kaamiki.conf.code_explain.pythonpath: {entry!r} is not a"
                " directory",
                conf,
            )
    python = given.get("code_explain_python")
    if python is not None and not given.get("code_explain_run"):
        fail(
            "kaamiki.conf.code_explain.python is set but"
            " kaamiki.conf.code_explain.run is False, so nothing runs with it",
            conf,
        )
    if python is not None and not p.isfile(python):
        fail(
            f"kaamiki.conf.code_explain.python: {python!r} is not a file", conf
        )


def _check_dates(given: dict[str, t.Any], conf: str) -> None:
    """Check the date formats a site wrote."""
    for key in ("release_version_fmt", "last_updated_on_fmt"):
        if given.get(key) and "%" not in given[key]:
            fail(f"{option(key)}: {given[key]!r} has no date directive", conf)
    if given.get("release_version_fmt"):
        sample = dt.fromisoformat("2026-01-02").strftime(
            given["release_version_fmt"]
        )
        try:
            dt.strptime(sample, given["release_version_fmt"])  # noqa: DTZ007
        except ValueError, re.error:
            fail(
                "kaamiki.conf.release.version_fmt: expected a format that reads"
                " back what it writes, got one that does not",
                conf,
            )


def _check_translation(app: Sphinx, given: dict[str, t.Any], conf: str) -> None:
    """Check the date format a language's catalogue gives.

    It only counts when the site sets no format of its own.
    """
    if app.config.html_last_updated_fmt or given.get("last_updated_on_fmt"):
        return
    try:
        moment(TIME_DIRECTIVES)(str(_("%d %B %Y")))
    except (TypeError, ValueError) as error:
        fail(
            f"the translation of '%d %B %Y' into {app.config.language}:"
            f" {error}",
            conf,
        )


@t.overload
def setting(
    config: Config,
    key: t.Literal[
        "code_explain_cache",
        "code_explain_comprehensions",
        "code_explain_run",
        "copy_headerlinks",
        "links_in_new_tab",
        "show_404",
        "show_breadcrumbs",
        "show_credit",
        "show_more",
        "show_page_last_updated",
        "show_previous_next_cards",
        "show_previous_next_pages",
        "show_scrolltop",
        "show_searchbox",
        "show_sitemap",
        "toctree_in_header",
        "toctree_includehidden",
        "toctree_titles_only",
        "youtube_click_to_load",
        "youtube_privacy",
    ],
) -> bool: ...


@t.overload
def setting(config: Config, key: t.Literal["show_feedback"]) -> bool | None: ...


@t.overload
def setting(
    config: Config,
    key: t.Literal[
        "accordion_marker",
        "accordion_marker_position",
        "button_icon_position",
        "button_scheme",
        "code_explain_events",
        "embed_js_loading",
        "fa_style",
        "last_updated_on_fmt",
        "release_version_fmt",
        "sharpie_colour",
        "tab_icon_position",
        "underline_colour",
        "youtube_allow",
        "youtube_referrer_policy",
    ],
) -> str: ...


@t.overload
def setting(
    config: Config, key: t.Literal["code_explain_python", "fa_kit"]
) -> str | None: ...


@t.overload
def setting(
    config: Config,
    key: t.Literal[
        "code_explain_budget",
        "code_explain_limit",
        "code_explain_memory",
        "code_explain_output_limit",
        "code_explain_timeout",
        "show_more_after",
        "show_previous_next_cards_count",
        "toctree_maxdepth",
        "words_per_minute",
    ],
) -> int: ...


@t.overload
def setting(config: Config, key: t.Literal["logo_size"]) -> int | None: ...


@t.overload
def setting(
    config: Config, key: t.Literal["underline_width", "underline_wobble"]
) -> float: ...


@t.overload
def setting(
    config: Config,
    key: t.Literal[
        "code_explain_pythonpath",
        "embed_css",
        "embed_iframe_hosts",
        "embed_js",
        "internal_hosts",
    ],
) -> list[str]: ...


@t.overload
def setting(
    config: Config,
    key: t.Literal[
        "button_colours", "favicons", "release_kinds", "role_colours"
    ],
) -> dict[str, str]: ...


@t.overload
def setting(
    config: Config,
    key: t.Literal[
        "fa_icons",
        "feedback",
        "header_buttons",
        "license",
        "open_graph",
        "project",
        "sidebar_buttons",
    ],
) -> dict[str, t.Any]: ...


@t.overload
def setting(config: Config, key: str) -> t.Any: ...


def setting(config: Config, key: str) -> t.Any:
    """Read one of Kaamiki's settings.

    The type it gives back is the one the setting takes, for a `key`
    written out, and `Any` for one worked out.

    :param config: The Sphinx configuration.
    :param key: The setting's name without the prefix, `show_more` for
        `kaamiki.conf.show.more`.
    :return: What the site set or Kaamiki's own default, which is a
        copy for a list or a dict so no caller can change it.
    """
    value = config[flat(key)]
    if value is None:
        return copy.deepcopy(DEFAULTS[key])
    return copy.deepcopy(value)


def reread(
    app: Sphinx,
    env: BuildEnvironment,
    added: set[str],
    changed: set[str],
    removed: set[str],
) -> list[str]:
    """Send every page back through reading when the kit or the address
    changes.

    Sphinx reads every page again by itself when a setting in
    `PARSE_TIME` changes, as they are all `env` values. It can't see
    two things that end up in the pages: the Font Awesome kit the
    `KAAMIKI_FA_KIT` environment variable names and `html_baseurl`,
    which Sphinx only registers for the HTML builders.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param added: The pages Sphinx found new.
    :param changed: The pages Sphinx found changed.
    :param removed: The pages Sphinx found gone.
    :return: Every page when the kit or the address isn't what it was
        at the last build, and none otherwise or at the first build,
        where every page is new anyway.
    """
    del added, changed, removed
    now = json.dumps([icons.Icons.of(app.config).kit, app.config.html_baseurl])
    before = kept(env, "settings", now)
    return sorted(env.found_docs) if before not in (None, now) else []
