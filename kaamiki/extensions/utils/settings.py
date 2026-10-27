"""\
Theme Settings
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 26 October 2026

Kaamiki's settings, their defaults and the helpers that read them.
"""

import copy
import difflib
import json
import os.path as p
import re
import typing as t
from datetime import datetime as dt

from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils.checks import fail

if t.TYPE_CHECKING:
    from collections.abc import Callable

    from sphinx.application import Sphinx
    from sphinx.config import Config
    from sphinx.environment import BuildEnvironment

# NOTE(xames3): A rough average, adults read non-fiction at about
# 238 words a minute: https://doi.org/10.1016/j.jml.2019.104047
WORDS_PER_MINUTE: t.Final[int] = 230
TONES: t.Final[tuple[str, ...]] = ("red", "yellow", "blue", "green")
# NOTE(xames3): The hue, saturation and lightness behind each tone in
# `theme.css`, which a data URI can't read through `var()`.
PALETTE: t.Final[dict[str, str]] = {
    "red": "357.87 68.98% 57%",
    "yellow": "38.9 100% 57.06%",
    "blue": "205.88 100% 50%",
    "green": "131.25 41.03% 45.88%",
}
CREDIT: t.Final[str] = "https://github.com/xames3/website"
# NOTE(xames3): The most and the least a number may be, for every number
# a site, a page or a directive gives Kaamiki. Anything outside is an
# error and never clamped.
BOUNDS: t.Final[dict[str, tuple[float, float]]] = {
    "avatar_size": (16, 64),
    "interval": (3, 15),
    "logo_size": (8, 64),
    "pace": (24, 240),
    "show_more_after": (3, 8),
    "startfrom": (1, 10800),
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
GAPS: t.Final[float] = 4.0
MARGINS: t.Final[float] = 8.0
SHOW_MORE_AFTER: t.Final[int] = 5
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
ICONS: t.Final[dict[str, str]] = {
    "breadcrumb_home": "fa-solid fa-house",
    "breadcrumb_separator_child": "fa-solid fa-angle-right",
    "breadcrumb_separator_parent": "fa-solid fa-angles-right",
    "copy_url": "fa-solid fa-link",
    "external_link": "fa-solid fa-arrow-up-right-from-square",
    "feedback": "fa-solid fa-paper-plane",
    "menu": "fa-solid fa-bars",
    "page_source": "fa-regular fa-file-lines",
    "play": "fa-solid fa-play",
    "reading_time": "fa-regular fa-clock",
    "release_notes": "fa-solid fa-tag",
    "scrolltop": "fa-solid fa-arrow-up",
    "search": "fa-solid fa-magnifying-glass",
    "show_more": "fa-solid fa-chevron-down",
    "title_badge": "",
}
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
            {
                "c",
                "c++",
                "cpp",
                "cuda",
                "h",
                "hpp",
                "json",
                "json-object",
                "objc",
                "objective-c",
            }
        ),
    ),
    ("fa-regular fa-file-lines", frozenset({"rest", "restructuredtext", "rst", "text", "txt"})),
    ("fa-solid fa-file-xml", frozenset({"xml"})),
    (
        "fa-solid fa-list",
        frozenset({"cfg", "dosini", "ini", "toml", "yaml", "yml"}),
    ),
    ("fa-brands fa-android", frozenset({"kotlin"})),
)
PRO_STYLES: t.Final[tuple[str, ...]] = (
    "fa-light",
    "fa-thin",
    "fal",
    "fat",
    *sorted(checks.FAMILIES),
)
BLANK_ICONS: t.Final[tuple[str, ...]] = ("release_notes", "title_badge")
PRO_ICONS: t.Final[dict[str, str]] = {
    "fa-light fa-globe": "fa-solid fa-globe",
    "fa-solid fa-brackets-curly": "fa-solid fa-code",
    "fa-solid fa-file-xml": "fa-solid fa-code",
}
FA_FREE: t.Final[str] = (
    "https://ka-f.fontawesome.com/releases/v7.3.1/css/free.min.css"
)
DEFAULTS: t.Final[dict[str, t.Any]] = {
    "accordion_marker": "plus",
    "accordion_marker_position": "after",
    "add_copy_to_headerlinks": True,
    "block_ai": False,
    "button_colours": {},
    "button_icon_position": "before",
    "button_scheme": "light",
    "embed_css": [],
    "embed_iframe_hosts": [],
    "embed_js": [],
    "embed_js_loading": "defer",
    "fa_css": FA_FREE,
    "fa_icons": {},
    "fa_kit": None,
    "fa_style": "solid",
    "favicons": {},
    "feedback": {},
    "header_buttons": {},
    "internal_hosts": [],
    "last_updated_on_fmt": "",
    "license": {},
    "logo_size": None,
    "open_graph": {},
    "open_links_in_new_tab": True,
    "project": {},
    "release_kinds": {},
    "release_version_fmt": "%Y.%m.%d",
    "role_colours": {},
    "sharpie_colour": "yellow",
    "show_404": True,
    "show_breadcrumbs": True,
    "show_feedback": None,
    "show_kaamiki_theme": False,
    "show_more": True,
    "show_more_after": SHOW_MORE_AFTER,
    "show_page_last_updated": True,
    "show_previous_next_pages": True,
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
    "code_explain_timeout": 10,
    "words_per_minute": WORDS_PER_MINUTE,
    "youtube_allow": (
        "accelerometer; clipboard-write; encrypted-media; gyroscope;"
        " picture-in-picture; web-share"
    ),
    "youtube_privacy": False,
    "youtube_referrer_policy": "strict-origin-when-cross-origin",
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
    "open_links_in_new_tab",
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
    "code_explain_timeout",
    "youtube_allow",
    "youtube_privacy",
    "youtube_referrer_policy",
)
# NOTE(xames3): Settings that moved, so a site that still has the old name is
# told instead of left with a setting that does nothing.
RENAMED: t.Final[dict[str, str]] = {
    "accordion_icon_position": "accordion_marker_position",
    "show_toctree": "toctree_in_header",
}
PAGE_SWITCHES: t.Final[tuple[str, ...]] = (
    "show_breadcrumbs",
    "show_feedback",
    "show_kaamiki_theme",
    "show_more",
    "show_page_last_updated",
    "show_previous_next_pages",
    "show_scrolltop",
    "show_searchbox",
    "toctree_in_header",
)
ALIGNMENTS: t.Final[tuple[str, ...]] = ("left", "center", "right")
CHOICES: t.Final[dict[str, tuple[str, ...]]] = {
    "accordion_marker": ("plus", "down", "right"),
    "accordion_marker_position": ("before", "after"),
    "button_icon_position": ("before", "after"),
    "embed_js_loading": ("defer", "async", "normal"),
    "fa_style": ("solid", "regular", "light", "thin"),
    "tab_icon_position": ("before", "after"),
}


EVENTS: t.Final[tuple[str, ...]] = ("call", "line", "return")
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
CARDS: t.Final[tuple[str, ...]] = ("summary", "summary_large_image")
FAVICONS: t.Final[tuple[str, ...]] = (
    "manifest",
    "size_96",
    "size_180",
    "size_svg",
)
TIME_DIRECTIVES: t.Final[re.Pattern[str]] = re.compile(r"%[aAbBdHIjmMpSyYZz%]")


def boolean(value: t.Any) -> None:
    """Check a setting is `True` or `False` and nothing like them."""
    if type(value) is not bool:
        raise TypeError(f"expected True or False, got {value!r}")


def whole(low: float, high: float) -> Callable[[t.Any], None]:
    """Make a check for a whole number from `low` to `high`."""

    def rule(value: t.Any) -> None:
        if type(value) is not int:
            raise TypeError(f"expected a whole number, got {value!r}")
        if not low <= value <= high:
            raise ValueError(f"expected {low:g} to {high:g}, got {value}")

    return rule


def real(low: float, high: float) -> Callable[[t.Any], None]:
    """Make a check for a number from `low` to `high`."""

    def rule(value: t.Any) -> None:
        if type(value) not in (int, float):
            raise TypeError(f"expected a number, got {value!r}")
        if not low <= value <= high:
            raise ValueError(f"expected {low:g} to {high:g}, got {value:g}")

    return rule


def string(read: Callable[[str], t.Any]) -> Callable[[t.Any], None]:
    """Make a check for a string that `read` accepts."""

    def rule(value: t.Any) -> None:
        if not isinstance(value, str):
            raise TypeError(f"expected a string, got {value!r}")
        read(value)

    return rule


def words(allowed: tuple[str, ...]) -> Callable[[t.Any], None]:
    """Make a check for one of a few words."""

    def rule(value: t.Any) -> None:
        if value not in allowed:
            raise ValueError(
                f"expected one of {', '.join(map(repr, allowed))}, got "
                f"{value!r}"
            )

    return rule


def many(read: Callable[[str], t.Any]) -> Callable[[t.Any], None]:
    """Make a check for a list of strings that `read` accepts."""

    def rule(value: t.Any) -> None:
        if not isinstance(value, (list, tuple)):
            raise TypeError(f"expected a list, got {value!r}")
        for each in value:
            if not isinstance(each, str):
                raise TypeError(f"expected a list of strings, got {each!r}")
            read(each)
        if len(set(value)) != len(value):
            raise ValueError("expected a list with nothing twice")

    return rule


def table(
    key: Callable[[str], t.Any], read: Callable[[t.Any], None]
) -> Callable[[t.Any], None]:
    """Make a check for a dict whose keys `key` and values `read`
    accept.
    """

    def rule(value: t.Any) -> None:
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


def shape(**fields: Callable[[t.Any], None]) -> Callable[[t.Any], None]:
    """Make a check for a dict that has only the fields named."""

    def rule(value: t.Any) -> None:
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
        if value != value.lower():
            raise ValueError(f"expected {value.lower()!r}, names are lowercase")
        return read(value)

    return rule


def moment(directives: re.Pattern[str]) -> Callable[[str], None]:
    """Make a check for a date format that only has known directives."""

    def rule(value: str) -> None:
        left = directives.sub("", value)
        if "%" in left:
            raise ValueError(
                f"expected a date format with %a %A %b %B %d %H %I %j %m %M"
                f" %p %S %y %Y %Z %z, got {value!r}"
            )

    return rule


def pattern(regex: re.Pattern[str], hint: str) -> Callable[[str], str]:
    """Make a check for a string written a certain way."""

    def read(value: str) -> str:
        if not regex.fullmatch(value):
            raise ValueError(f"expected {hint}, got {value!r}")
        return value

    return read


def ending(suffix: str, read: Callable[[str], t.Any]) -> Callable[[str], str]:
    """Make a check for an address or a file name ending a certain way."""

    def check(value: str) -> str:
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
        for each in value.split(separator):
            words(allowed)(each)

    return read


EMAIL_ONLY: t.Final = pattern(checks.EMAIL, "an email address")
STATIC_NAME: t.Final = pattern(checks.FILE, "a file name")
ATTRIBUTES: t.Final = pattern(
    re.compile(
        r"(?:(?:data|aria)-[a-z][\w:-]*=(?:\"[^\"<>]*\"|'[^'<>]*')\s*)+"
    ),
    'data or aria attributes like data-x="y"',
)


def icons(value: t.Any) -> None:
    """Check the icons a site sets, which only `BLANK_ICONS` may leave empty."""
    if isinstance(value, dict):
        value = {
            key: each
            for key, each in value.items()
            if each != "" or key not in BLANK_ICONS
        }
    table(words(tuple(ICONS)), string(checks.icon))(value)


def button(value: t.Any) -> None:
    """Check a header or sidebar button."""
    if not isinstance(value, dict) or "url" not in value:
        raise ValueError("expected a dict with a url")
    shape(
        url=string(checks.link),
        icon=string(checks.text),
        extras=string(lambda _: ATTRIBUTES(_.strip())),
    )(value)


RULES: t.Final[dict[str, Callable[[t.Any], None]]] = {
    "accordion_marker": words(CHOICES["accordion_marker"]),
    "accordion_marker_position": words(CHOICES["accordion_marker_position"]),
    "add_copy_to_headerlinks": boolean,
    "block_ai": boolean,
    "button_icon_position": words(CHOICES["button_icon_position"]),
    "embed_js_loading": words(CHOICES["embed_js_loading"]),
    "fa_style": words(CHOICES["fa_style"]),
    "tab_icon_position": words(CHOICES["tab_icon_position"]),
    "open_links_in_new_tab": boolean,
    "show_404": boolean,
    "show_breadcrumbs": boolean,
    "show_kaamiki_theme": boolean,
    "show_more": boolean,
    "show_page_last_updated": boolean,
    "show_previous_next_pages": boolean,
    "show_scrolltop": boolean,
    "show_searchbox": boolean,
    "show_sitemap": boolean,
    "toctree_in_header": boolean,
    "toctree_includehidden": boolean,
    "toctree_titles_only": boolean,
    "code_explain_cache": boolean,
    "code_explain_comprehensions": boolean,
    "youtube_privacy": boolean,
    "show_feedback": boolean,
    "show_more_after": whole(*BOUNDS["show_more_after"]),
    "words_per_minute": whole(*BOUNDS["words_per_minute"]),
    "logo_size": whole(*BOUNDS["logo_size"]),
    "toctree_maxdepth": whole(*BOUNDS["toctree_maxdepth"]),
    "underline_width": real(*BOUNDS["underline_width"]),
    "underline_wobble": real(*BOUNDS["underline_wobble"]),
    "code_explain_budget": whole(*BOUNDS["code_explain_budget"]),
    "code_explain_limit": whole(*BOUNDS["code_explain_limit"]),
    "code_explain_memory": whole(*BOUNDS["code_explain_memory"]),
    "code_explain_output_limit": whole(*BOUNDS["code_explain_output_limit"]),
    "code_explain_timeout": whole(*BOUNDS["code_explain_timeout"]),
    "fa_kit": string(ending(".js", checks.web)),
    "fa_css": string(ending(".css", checks.web)),
    "last_updated_on_fmt": string(moment(TIME_DIRECTIVES)),
    "release_version_fmt": string(moment(TIME_DIRECTIVES)),
    "code_explain_events": string(listed_in(EVENTS, ", ")),
    "youtube_allow": string(listed_in(PERMISSIONS, "; ")),
    "youtube_referrer_policy": words(REFERRERS),
    "internal_hosts": many(checks.host),
    "embed_iframe_hosts": many(checks.host),
    "embed_css": many(ending(".css", STATIC_NAME)),
    "embed_js": many(ending(".js", STATIC_NAME)),
    "code_explain_pythonpath": many(checks.text),
    "code_explain_python": string(checks.text),
    "button_colours": table(lower(checks.slug), string(checks.colour)),
    "role_colours": table(lower(checks.slug), string(checks.colour)),
    "release_kinds": table(lower(checks.slug), words(TONES)),
    "fa_icons": icons,
    "favicons": shape(**dict.fromkeys(FAVICONS, string(STATIC_NAME))),
    "header_buttons": table(checks.text, button),
    "sidebar_buttons": table(checks.text, button),
    "license": shape(name=string(checks.text), url=string(checks.web)),
    "feedback": shape(
        type=words(("mail", "link")),
        url=string(checks.link),
        subject=string(checks.text),
        title=string(checks.text),
        description=string(checks.text),
        button=string(checks.text),
        icon=string(checks.icon),
        split=boolean,
    ),
    "open_graph": shape(
        card=words(CARDS),
        description=string(checks.text),
        description_length=whole(50, 300),
        enable=boolean,
        image=string(checks.link),
        image_alt=string(checks.text),
        locale=string(
            pattern(re.compile(r"[a-z]{2,3}_[A-Z]{2}"), "a locale like en_GB")
        ),
        site_name=string(checks.text),
        twitter_site=string(
            pattern(re.compile(r"@[A-Za-z0-9_]{1,15}"), "a handle like @xames3")
        ),
        type=string(
            pattern(
                re.compile(r"[a-z]+(?:\.[a-z_]+)?"),
                "an Open Graph type like website",
            )
        ),
    ),
    "project": shape(
        author=string(checks.text),
        avatar=string(checks.link),
        email=string(EMAIL_ONLY),
        source=string(lambda _: _ if _ == "#" else checks.web(_)),
    ),
}


def validate(app: Sphinx) -> None:
    """Check every setting a site gave Kaamiki.

    :param app: The Sphinx application instance.
    :raises KaamikiError: For the first setting that is the wrong
        type, isn't written the way it takes or is out of range, and
        for a name that's a misspelling of one of Kaamiki's.
    """
    given = app.config.html_context
    conf = p.join(app.confdir, "conf.py")

    def refuse(message: str) -> t.NoReturn:
        fail(message, conf)

    for key, value in given.items():
        if key.startswith("km_"):
            continue
        if key in RENAMED:
            refuse(f"html_context[{key!r}] was renamed {RENAMED[key]!r}")
        if key not in DEFAULTS:
            near = difflib.get_close_matches(key, DEFAULTS, n=1, cutoff=0.8)
            if near:
                refuse(
                    f"html_context[{key!r}] is not a setting, did you mean "
                    f"{near[0]!r}"
                )
            continue
        if value is None:
            if DEFAULTS[key] is not None and key != "show_feedback":
                refuse(
                    f"html_context[{key!r}] is None, leave it out for the "
                    f"default"
                )
            continue
        try:
            RULES[key](value)
        except KeyError:
            pass
        except (TypeError, ValueError) as error:
            refuse(f"html_context[{key!r}]: {error}")
    colours = {**given.get("role_colours", {})}
    for key in ("sharpie_colour", "underline_colour"):
        if key in given:
            if not isinstance(given[key], str):
                refuse(
                    f"html_context[{key!r}]: expected a colour, got "
                    f"{given[key]!r}"
                )
            try:
                checks.colour(given[key], (*TONES, *colours))
            except (TypeError, ValueError) as error:
                refuse(f"html_context[{key!r}]: {error}")
    base = app.config.html_baseurl
    if base:
        try:
            if not checks.web(base).endswith("/"):
                raise ValueError("expected an address ending in /")
        except (TypeError, ValueError) as error:
            refuse(f"html_baseurl: {error}")
    stamp = app.config.html_last_updated_fmt
    if stamp:
        try:
            moment(TIME_DIRECTIVES)(stamp)
        except (TypeError, ValueError) as error:
            refuse(f"html_last_updated_fmt: {error}")
    scheme = given.get("button_scheme")
    if scheme is not None and scheme not in (
        *SCHEMES,
        *given.get("button_colours", {}),
    ):
        refuse(
            f"html_context['button_scheme']: expected {', '.join(SCHEMES)}"
            f" or a name in button_colours, got {scheme!r}"
        )
    for key, own in (("button_colours", SCHEMES), ("role_colours", TONES)):
        for name in given.get(key, {}):
            if name in own:
                refuse(
                    f"html_context[{key!r}]: {name!r} is one of Kaamiki's "
                    f"own colours"
                )
    if given.get("feedback") and given.get("show_feedback") is False:
        refuse("html_context['feedback'] is set but show_feedback is False")
    if "show_more_after" in given and given.get("show_more") is False:
        refuse("html_context['show_more_after'] is set but show_more is False")
    feedback = given.get("feedback", {})
    if feedback.get("type") == "link" and "url" not in feedback:
        refuse("html_context['feedback']: type 'link' needs a url")
    if "url" in feedback and feedback.get("type") != "link":
        refuse("html_context['feedback']: a url needs type 'link'")
    licence = given.get("license", {})
    if "url" in licence and "name" not in licence:
        refuse("html_context['license']: a url needs a name")
    statics = [p.join(app.confdir, _) for _ in app.config.html_static_path]

    def present(name: str) -> bool:
        return any(p.isfile(p.join(_, name)) for _ in statics)

    logo = app.config.html_theme_options.get("logo")
    if logo is not None and not (isinstance(logo, str) and not logo):
        try:
            STATIC_NAME(logo)
        except (TypeError, ValueError) as error:
            refuse(f"html_theme_options['logo']: {error}")
        if not present(logo):
            refuse(
                f"html_theme_options['logo']: {logo!r} is not in"
                " html_static_path"
            )
    for key, found in (
        ("embed_css", given.get("embed_css", [])),
        ("embed_js", given.get("embed_js", [])),
        ("favicons", given.get("favicons", {}).values()),
    ):
        for name in found:
            if not present(name):
                refuse(
                    f"html_context[{key!r}]: {name!r} is not in"
                    " html_static_path"
                )
    for entry in given.get("code_explain_pythonpath", []):
        if not p.isdir(p.join(app.srcdir, entry)):
            refuse(
                f"html_context['code_explain_pythonpath']: {entry!r} is not "
                f"a directory"
            )
    python = given.get("code_explain_python")
    if python is not None and not p.isfile(python):
        refuse(f"html_context['code_explain_python']: {python!r} is not a file")
    for key in ("release_version_fmt", "last_updated_on_fmt"):
        if given.get(key) and "%" not in given[key]:
            refuse(
                f"html_context[{key!r}]: {given[key]!r} has no date directive"
            )
    if given.get("release_version_fmt"):
        sample = dt.fromisoformat("2026-01-02").strftime(
            given["release_version_fmt"]
        )
        try:
            dt.strptime(sample, given["release_version_fmt"])  # noqa: DTZ007
        except ValueError:
            refuse(
                "html_context['release_version_fmt']: cannot read back "
                "what it writes"
            )


def setting(config: Config, key: str) -> t.Any:
    """Read one of Kaamiki's settings from `html_context`.

    :param config: The Sphinx configuration.
    :param key: The setting's name, as the site writes it.
    :return: What the site set or Kaamiki's own default, which is a copy
        for a list or a dict so no caller can change the default.
    """
    value = config.html_context.get(key)
    if value is None:
        return copy.deepcopy(DEFAULTS[key])
    return value


def icon(value: str | None, fallback: str = "", *, kit: bool = True) -> str:
    """Spell out a Font Awesome icon in full.

    `video`, `fa-video` and `fa-solid fa-video` all work. A lone name
    gets the solid style, which every free icon has.

    :param value: The icon as written or `None` when unset.
    :param fallback: The icon to use when there isn't one.
    :param kit: Whether the site has a Font Awesome kit. Without one a
        Pro icon is swapped for its Free stand-in.
    :return: The icon's classes or an empty string for no icon.
    """
    parts = (value or fallback).split()
    if len(parts) == 1:
        name = parts[0] if parts[0].startswith("fa-") else f"fa-{parts[0]}"
        parts = ["fa-solid", name]
    return free(" ".join(parts)) if parts and not kit else " ".join(parts)


def icon_style(config: Config) -> str:
    """Pick the style icons are drawn in.

    :param config: The Sphinx configuration.
    :return: The site's `fa_style` with a Font Awesome kit, which has
        every style, and `solid` without one, as that's the style the
        free icons all have.
    """
    return setting(config, "fa_style") if setting(config, "fa_kit") else "solid"


def pro(classes: str) -> bool:
    """Say whether an icon needs a Font Awesome kit.

    :param classes: The icon's classes, as `fa-light fa-globe`.
    :return: Whether it's one of the Pro icons Kaamiki knows a Free
        stand-in for or in a Pro style.
    """
    return classes in PRO_ICONS or classes.partition(" ")[0] in PRO_STYLES


def free(classes: str) -> str:
    """Swap a Pro icon for the Free one that stands in for it.

    :param classes: The icon's classes, as `fa-light fa-globe`.
    :return: The stand-in Kaamiki names, or the same name in the solid
        style for a Pro style, or the classes as they were.
    """
    if classes in PRO_ICONS:
        return PRO_ICONS[classes]
    parts = classes.split()
    skip = 0
    while skip < len(parts) and parts[skip] in PRO_STYLES:
        skip += 1
    if not skip:
        return classes
    if skip < len(parts) and parts[skip] in ("fa-solid", "fa-regular"):
        skip += 1
    return " ".join(["fa-solid", *parts[skip:]])


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
            return classes if kit else free(classes)
    return ""


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
