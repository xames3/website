"""\
Theme Settings
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 12 October 2026

Kaamiki's settings, their defaults and the helpers that read them.
"""

from __future__ import annotations

import json
import typing as t

from sphinx.util import logging

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.config import Config
    from sphinx.environment import BuildEnvironment

# NOTE(xames3): A rough average, adults read non-fiction at about
# 238 words a minute: https://doi.org/10.1016/j.jml.2019.104047
WORDS_PER_MINUTE: t.Final[int] = 230  # for nice proper multiple of 5
LOGO_SIZES: t.Final[tuple[int, int]] = (8, 64)
SHOW_MORE_AFTER: t.Final[int] = 5
PROJECT: t.Final[dict[str, str]] = {
    "author": "",
    "avatar": "",
    "email": "",
    "source": "#",
}
ICONS: t.Final[dict[str, str]] = {
    "breadcrumb_home": "fa-solid fa-house",
    "breadcrumb_separator_child": "fa-solid fa-angle-right",
    "breadcrumb_separator_parent": "fa-solid fa-angles-right",
    "copy_url": "fa-solid fa-link",
    "dark_mode": "fa-solid fa-moon",
    "external_link": "fa-solid fa-arrow-up-right-from-square",
    "feedback": "fa-solid fa-paper-plane",
    "light_mode": "fa-solid fa-sun",
    "menu": "fa-solid fa-bars",
    "next_button": "fa-solid fa-arrow-right",
    "play": "fa-solid fa-play",
    "previous_button": "fa-solid fa-arrow-left",
    "reading_time": "fa-regular fa-clock",
    "search": "fa-solid fa-magnifying-glass",
    "show_more": "fa-solid fa-chevron-down",
}
# NOTE(xames3): Brands wear `fa-brands` and the rest `fa-solid`, every
# one of them is in Font Awesome Free. A language it has no brand for
# gets what suits it best: a terminal for shells, a code file for C.
LANGUAGE_ICONS: t.Final[tuple[tuple[str, frozenset[str]], ...]] = (
    (
        "fa-brands fa-python",
        frozenset({"py", "py3", "pycon", "python", "python3"}),
    ),
    (
        "fa-brands fa-js",
        frozenset({"javascript", "js", "jsx", "node", "nodejs"}),
    ),
    ("fa-brands fa-typescript", frozenset({"ts", "tsx", "typescript"})),
    ("fa-brands fa-rust", frozenset({"rs", "rust"})),
    ("fa-brands fa-golang", frozenset({"go", "golang"})),
    ("fa-brands fa-java", frozenset({"java"})),
    ("fa-brands fa-swift", frozenset({"swift"})),
    ("fa-brands fa-r-project", frozenset({"r", "rscript"})),
    ("fa-brands fa-php", frozenset({"php", "php3", "php4", "php5"})),
    ("fa-brands fa-erlang", frozenset({"erl", "erlang"})),
    ("fa-brands fa-html5", frozenset({"html", "xhtml"})),
    ("fa-brands fa-css3-alt", frozenset({"css"})),
    ("fa-brands fa-sass", frozenset({"sass", "scss"})),
    ("fa-brands fa-less", frozenset({"less"})),
    ("fa-brands fa-markdown", frozenset({"markdown", "md"})),
    ("fa-brands fa-docker", frozenset({"docker", "dockerfile"})),
    ("fa-brands fa-vuejs", frozenset({"vue"})),
    ("fa-solid fa-gem", frozenset({"rb", "ruby"})),
    (
        "fa-solid fa-database",
        frozenset(
            {"mysql", "plpgsql", "postgres", "postgresql", "sql", "sqlite3"}
        ),
    ),
    (
        "fa-solid fa-terminal",
        frozenset(
            {
                "bash",
                "bat",
                "batch",
                "console",
                "doscon",
                "fish",
                "powershell",
                "pwsh",
                "sh",
                "shell",
                "shell-session",
                "zsh",
            }
        ),
    ),
    (
        "fa-solid fa-brackets-curly",
        frozenset(
            {"c", "c++", "cpp", "cuda", "h", "hpp", "objc", "objective-c"}
        ),
    ),
)
# NOTE(xames3): `brackets-curly` is a Pro icon, so a site without a kit
# gets the Free `file-code` in its place.
PRO_ICONS: t.Final[dict[str, str]] = {
    "fa-solid fa-brackets-curly": "fa-solid fa-file-code",
}
OPTIONS: t.Final[tuple[str, ...]] = (
    "add_copy_to_headerlinks",
    "colour_mode",
    "fa_css",
    "fa_icons",
    "fa_kit",
    "fa_style",
    "favicons",
    "header_buttons",
    "license",
    "open_graph",
    "open_links_in_new_tab",
    "project",
    "show_404",
    "show_breadcrumbs",
    "show_colour_modes",
    "show_feedback",
    "show_kaamiki_theme",
    "show_last_updated_on",
    "show_more_after",
    "show_previous_next_pages",
    "show_scrolltop",
    "show_searchbox",
    "show_show_more",
    "show_sitemap",
    "show_toctree",
    "sidebar_buttons",
)
# NOTE(xames3): The settings Kaamiki adds on top of the ones above.
# The ones named in `PARSE_TIME` are read while the pages are read, so
# `reread` sends the pages back through when one of them changes.
DEFAULTS: t.Final[dict[str, t.Any]] = {
    "button_colours": {},
    "button_icon_position": "before",
    "button_scheme": "dark",
    "embed_css": [],
    "embed_iframe_hosts": [],
    "embed_js": [],
    "embed_js_loading": "defer",
    "feedback": {},
    "internal_hosts": [],
    "last_updated_on_fmt": "",
    "logo_size": None,
    "release_kinds": {},
    "release_version_fmt": "%Y.%m.%d",
    "role_colours": {},
    "sharpie_colour": "yellow",
    "thumbnail_grayscale": False,
    "toctree_includehidden": True,
    "toctree_maxdepth": 0,
    "toctree_titles_only": True,
    "underline_colour": "#FF9800",
    "underline_width": 2.5,
    "underline_wobble": 1.0,
    "words_per_minute": WORDS_PER_MINUTE,
    "youtube_allow": (
        "accelerometer; clipboard-write; encrypted-media; gyroscope;"
        " picture-in-picture; web-share"
    ),
    "youtube_privacy": False,
    "youtube_referrer_policy": "strict-origin-when-cross-origin",
}
PARSE_TIME: t.Final[tuple[str, ...]] = (
    "button_colours",
    "button_icon_position",
    "button_scheme",
    "embed_iframe_hosts",
    "internal_hosts",
    "open_links_in_new_tab",
    "release_kinds",
    "release_version_fmt",
    "role_colours",
    "sharpie_colour",
    "thumbnail_grayscale",
    "underline_colour",
    "underline_width",
    "underline_wobble",
    "walkthrough_budget",
    "walkthrough_cache",
    "walkthrough_comprehensions",
    "walkthrough_events",
    "walkthrough_limit",
    "walkthrough_memory",
    "walkthrough_output_limit",
    "walkthrough_python",
    "walkthrough_pythonpath",
    "walkthrough_timeout",
    "youtube_allow",
    "youtube_privacy",
    "youtube_referrer_policy",
)
TEMPLATED: t.Final[tuple[str, ...]] = ("toctree_titles_only",)
PAGE_SWITCHES: t.Final[tuple[str, ...]] = (
    "show_breadcrumbs",
    "show_colour_modes",
    "show_feedback",
    "show_kaamiki_theme",
    "show_last_updated_on",
    "show_previous_next_pages",
    "show_scrolltop",
    "show_searchbox",
    "show_show_more",
    "show_toctree",
)
FEEDBACK_KEYS: t.Final[frozenset[str]] = frozenset(
    {
        "button",
        "description",
        "icon",
        "mode",
        "subject",
        "url",
        "title",
        "type",
    }
)
SWITCHES: t.Final[dict[str, bool]] = {
    "show_breadcrumbs": True,
    "show_last_updated_on": True,
    "show_previous_next_pages": True,
    "show_searchbox": True,
    "show_toctree": True,
}
FA_STYLE: t.Final[str] = "solid"
FA_FREE: t.Final[str] = (
    "https://ka-f.fontawesome.com/releases/v7.3.1/css/free.min.css"
)
logger = logging.getLogger(__name__)


def setting(config: Config, key: str) -> t.Any:
    """Read one of Kaamiki's settings from `html_context`.

    :param config: The Sphinx configuration.
    :param key: The setting's name, as the site writes it.
    :return: What the site set or Kaamiki's own default.
    """
    value = config.html_context.get(key)
    return DEFAULTS[key] if value is None else value


def icon(value: str | None, fallback: str = "") -> str:
    """Spell out a Font Awesome icon in full.

    `video`, `fa-video` and `fa-solid fa-video` all work. A lone name
    gets the solid style, which every free icon has.

    :param value: The icon as written or `None` when unset.
    :param fallback: The icon to use when there isn't one.
    :return: The icon's classes or an empty string for no icon.
    """
    parts = (value or fallback).split()
    if len(parts) == 1:
        name = parts[0] if parts[0].startswith("fa-") else f"fa-{parts[0]}"
        parts = ["fa-solid", name]
    return " ".join(parts)


def language_icon(language: str | None, *, kit: bool = False) -> str:
    """Pick the Font Awesome icon a language is known by.

    :param language: The language a code block is written in.
    :param kit: Whether the site has a Font Awesome kit, which has the
        Pro icons.
    :return: The icon's classes or an empty string for a language
        with none.
    """
    name = (language or "").strip().lower()
    for classes, names in LANGUAGE_ICONS:
        if name in names:
            return classes if kit else PRO_ICONS.get(classes, classes)
    return ""


def toctree_args(config: Config) -> dict[str, t.Any]:
    """Read the settings the navigation trees are drawn with.

    :param config: The Sphinx configuration.
    :return: The arguments for Sphinx's `toctree()`, bar `titles_only`,
        which the header and the sidebar settle for themselves.
    """
    args: dict[str, t.Any] = {
        "includehidden": bool(setting(config, "toctree_includehidden"))
    }
    depth = setting(config, "toctree_maxdepth")
    try:
        if int(depth):
            args["maxdepth"] = int(depth)
    except TypeError, ValueError:
        logger.warning(
            "toctree_maxdepth needs a whole number, got %r",
            depth,
            type="kaamiki",
        )
    return args


def logo_size(config: Config) -> int | None:
    """Read `logo_size`, keeping it between the sizes a header holds.

    :param config: The Sphinx configuration.
    :return: The logo's height in pixels or `None` to leave it to the
        stylesheet.
    """
    value = setting(config, "logo_size")
    if value is None:
        return None
    low, high = LOGO_SIZES
    try:
        size = int(value)
    except TypeError, ValueError:
        size = 0
    if not low <= size <= high:
        logger.warning(
            "logo_size needs a whole number from %d to %d, got %r",
            low,
            high,
            value,
            type="kaamiki",
        )
        return min(max(size, low), high) if size else None
    return size


def reread(
    app: Sphinx,
    env: BuildEnvironment,
    added: set[str],
    changed: set[str],
    removed: set[str],
) -> list[str]:
    """Send every page back through reading when a parse-time setting
    changes.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param added: The pages Sphinx found new.
    :param changed: The pages Sphinx found changed.
    :param removed: The pages Sphinx found gone.
    :return: Every page when a setting in `PARSE_TIME` isn't what it
        was at the last build and none otherwise.
    """
    del added, changed, removed
    context = app.config.html_context
    seen = {key: context.get(key, DEFAULTS.get(key)) for key in PARSE_TIME}
    now = json.dumps(seen, sort_keys=True, default=str)
    before = getattr(env, "km_settings", None)
    env.km_settings = now  # type: ignore[attr-defined]
    return sorted(env.found_docs) if before != now else []
