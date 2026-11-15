"""\
Theme Settings
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 15 November 2026

The settings of Kaamiki: their schema, their checks, and how a site
sets them on `kaamiki.conf` or with a `-D`. `WORDS_PER_MINUTE` is 238,
the average speed at which adults read non-fiction. `FA_FREE_INTEGRITY`
is the SHA-384 hash of `FA_FREE` for Subresource Integrity. When the
release changes, make it again with `openssl dgst -sha384 -binary
free.min.css | openssl base64 -A`.

https://doi.org/10.1016/j.jml.2019.104047

https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity
"""

from __future__ import annotations

import copy
import difflib
import json
import os
import os.path as p
import re
import sys
import typing as t
from datetime import datetime as dt
from types import MappingProxyType

from sphinx.locale import _
from sphinx.util import logging

from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import icons
from kaamiki.extensions.utils.checks import fail
from kaamiki.extensions.utils.hooks import on

if t.TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Mapping

    from sphinx.application import Sphinx
    from sphinx.builders import Builder
    from sphinx.config import Config
    from sphinx.environment import BuildEnvironment

type Rule = Callable[[t.Any], object]

logger = logging.getLogger(__name__)

NAME: t.Final[str] = "kaamiki"
PREFIX: t.Final[str] = f"{NAME}_"
WORDS_PER_MINUTE: t.Final[int] = 238
TONES: t.Final[tuple[str, ...]] = ("red", "yellow", "blue", "green")
PALETTE: t.Final[dict[str, str]] = {
    "red": "357.87 68.98% 57%",
    "yellow": "38.9 100% 57.06%",
    "blue": "205.88 100% 50%",
    "green": "131.25 41.03% 45.88%",
}
CREDIT: t.Final[str] = "https://github.com/xames3/website"
CONTACT: t.Final[str] = "xa@mes3.dev"
BOUNDS: t.Final[dict[str, tuple[float, float]]] = {
    "avatar_size": (16, 64),
    "cards": (1, 4),
    "description_length": (50, 300),
    "gap": (0, 4),
    "interval": (2, 15),
    "logo_size": (8, 64),
    "margin": (0, 8),
    "motion_speed": (0.25, 4),
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
HEADER_SUBHEADER_FIELD: t.Final[str] = "km-header-subheader"
HEADER_NO_SUBHEADER_FIELD: t.Final[str] = "km-header-no-subheader"
PROJECT: t.Final[dict[str, str]] = {
    "author": "",
    "avatar": "",
    "email": "",
    "source": "#",
}
FA_FREE: t.Final[str] = (
    "https://ka-f.fontawesome.com/releases/v7.3.1/css/free.min.css"
)
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
ALIGNMENTS: t.Final[tuple[str, ...]] = ("left", "center", "right")
SIZES: t.Final[tuple[str, ...]] = ("small", "medium", "large")


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
    "ico",
    "size_96",
    "size_180",
    "size_svg",
)
LOGOS: t.Final[tuple[str, ...]] = ("light", "dark")
SNAKE: t.Final[re.Pattern[str]] = re.compile(r"(?<!^)(?=[A-Z])")
TIME_DIRECTIVES: t.Final[re.Pattern[str]] = re.compile(r"%[aAbBdHIjmMpSyYZz%]")


def boolean(value: object) -> None:
    """Check a setting is `True` or `False` and nothing like them.

    :param value: What the site gave.
    :raises TypeError: For anything else.
    """
    if type(value) is not bool:
        raise TypeError(f"expected True or False, got {value!r}")


def whole(low: float, high: float) -> Rule:
    """Make a check for a whole number from `low` to `high`.

    :param low: The least it may be.
    :param high: The most it may be.
    :return: The check.
    """

    def rule(value: t.Any) -> None:
        """Check the whole number.

        :param value: The value to check.
        """
        if type(value) is not int:
            raise TypeError(f"expected a whole number, got {value!r}")
        if not low <= value <= high:
            raise ValueError(f"expected {low:g} to {high:g}, got {value}")

    return rule


def real(low: float, high: float) -> Rule:
    """Make a check for a number from `low` to `high`.

    :param low: The least it may be.
    :param high: The most it may be.
    :return: The check.
    """

    def rule(value: t.Any) -> None:
        """Check the number.

        :param value: The value to check.
        """
        if type(value) not in (int, float):
            raise TypeError(f"expected a number, got {value!r}")
        if not low <= value <= high:
            raise ValueError(f"expected {low:g} to {high:g}, got {value:g}")

    return rule


def string(read: Callable[[str], t.Any]) -> Rule:
    """Make a check for a string that `read` accepts.

    :param read: The check for the text.
    :return: The check.
    """

    def rule(value: t.Any) -> None:
        """Check the string and read it.

        :param value: The value to check.
        """
        if not isinstance(value, str):
            raise TypeError(f"expected a string, got {value!r}")
        read(value)

    return rule


def many(read: Callable[[str], t.Any]) -> Rule:
    """Make a check for a list of strings that `read` accepts.

    :param read: The check for each string.
    :return: The check.
    """

    def rule(value: t.Any) -> None:
        """Check each string in the list and that none repeats.

        :param value: The value to check.
        """
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
    """Make a check for a dict whose keys and values are readable.

    :param key: The check for each name.
    :param read: The check for each value.
    :return: The check.
    """

    def rule(value: t.Any) -> None:
        """Check each name and each value of the dict.

        :param value: The value to check.
        """
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
    """Make a check for a dict that has only the fields named.

    :param fields: The check for each field, by its name.
    :return: The check.
    """

    def rule(value: t.Any) -> None:
        """Check each field of the dict.

        :param value: The value to check.
        """
        if not isinstance(value, dict):
            raise TypeError(f"expected a dict, got {value!r}")
        for name, each in value.items():
            if name not in fields:
                raise ValueError(
                    f"expected one of {', '.join(sorted(fields))}, got"
                    f" {name!r}"
                )
            try:
                fields[name](each)
            except (TypeError, ValueError) as error:
                raise ValueError(f"{name!r}: {error}") from error

    return rule


def lower(read: Callable[[str | None], t.Any]) -> Callable[[str], t.Any]:
    """Make a check for a name that has to be written in lowercase.

    :param read: The check for the name.
    :return: The check.
    """

    def rule(value: str) -> t.Any:
        """Check the name is lowercase and read it.

        :param value: The name to check.
        """
        if value != value.lower():
            raise ValueError(
                f"expected a lowercase name like {value.lower()!r}, got"
                f" {value!r}"
            )
        return read(value)

    return rule


def moment(directives: re.Pattern[str]) -> Callable[[str], None]:
    """Make a check for a date format that only has known directives.

    :param directives: The directives the format may have.
    :return: The check.
    """

    def rule(value: str) -> None:
        """Check the format has only known date directives.

        :param value: The date format to check.
        """
        left = directives.sub("", value)
        if "%" in left:
            raise ValueError(
                f"expected a date format with %a %A %b %B %d %H %I %j %m %M"
                f" %p %S %y %Y %Z %z %%, got {value!r}"
            )

    return rule


def ending(suffix: str, read: Callable[[str], t.Any]) -> Callable[[str], str]:
    """Make a check for an address or a file name ending a certain way.

    :param suffix: What it ends with.
    :param read: The check for the address or the file name.
    :return: The check.
    """

    def check(value: str) -> str:
        """Check the value and what it ends with.

        :param value: The address or the file name to check.
        """
        read(value)
        if not value.endswith(suffix):
            raise ValueError(f"expected a name ending {suffix}, got {value!r}")
        return value

    return check


def listed_in(
    allowed: tuple[str, ...], separator: str
) -> Callable[[str], None]:
    """Make a check for a string of words joined by `separator`.

    :param allowed: The words it may have.
    :param separator: What joins them.
    :return: The check.
    """

    def read(value: str) -> None:
        """Check each word of the string.

        :param value: The string to check.
        """
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
    """Check one icon of a site, as a name or as a Pro and Free pair.

    :param value: The icon, or a dictionary with `pro` and `free`.
    :raises ValueError: When it is not an icon or a pair.
    :raises TypeError: For a value of a wrong type.
    """
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
    """Check the icons of a site.

    :param value: The icons, by name. Only `BLANK_ROLES` can be empty.
    :raises ValueError: For an unknown name, or a wrong icon.
    :raises TypeError: For a value of a wrong type.
    """
    if isinstance(value, dict):
        value = {
            key: each
            for key, each in value.items()
            if each != "" or key not in icons.BLANK_ROLES
        }
    table(checks.word(*icons.ROLE_ICONS), role_icon)(value)


def button(value: t.Any) -> None:
    """Check a header or sidebar button.

    :param value: The button, with its url, icon and extras.
    """
    if not isinstance(value, dict) or "url" not in value:
        raise ValueError("expected a dict with a url")
    shape(
        url=string(checks.link),
        icon=string(checks.icon),
        extras=string(lambda each: ATTRIBUTES(each.strip())),
    )(value)


class Value[T]:
    """A Kaamiki setting, read as an attribute of its group."""

    def __init__(
        self,
        default: T,
        rule: Rule | None = None,
        *,
        choices: tuple[str, ...] = (),
        number: type[int | float] | None = None,
        text: Callable[[str], t.Any] | None = None,
        key: str = "",
        reread: bool = False,
        page: bool = False,
    ) -> None:
        """Keep the default of the setting and how a value is checked.

        :param default: The value when a site does not set one.
        :param rule: The check for a value. `choices` and `number` make
            one when it is not given.
        :param choices: The words that the setting permits.
        :param number: `int` or `float`, for a number in the `BOUNDS`
            of the setting.
        :param text: The check for a string. It makes the rule, and it
            is how an option of a directive or a role reads the
            setting from rST.
        :param key: The name of the setting in Sphinx, without
            `kaamiki_`. The default is the group, `_` and the
            attribute.
        :param reread: Whether a change reads each page again, not only
            writes it again.
        :param page: Whether a page can switch it with a field.
        """
        self.default = default
        self.rule = string(text) if text else rule
        self.read: Callable[[str], t.Any] | None = text
        self.choices = choices
        self.number = number
        self.key = key
        self.reread = reread
        self.page = page
        self.attr = ""
        self.group = ""

    def __set_name__(self, owner: type, name: str) -> None:
        """Keep the name of the attribute.

        :param owner: The group.
        :param name: The attribute, as `marker`.
        """
        self.attr = name

    @t.overload
    def __get__(self, group: None, owner: type) -> Value[T]: ...

    @t.overload
    def __get__(self, group: Settings, owner: type) -> T: ...

    def __get__(self, group: Settings | None, owner: type) -> t.Any:
        """Read what the site set, or the default of the setting.

        :param group: The group, or `None` on its class.
        :param owner: The class of the group.
        :return: The value. A dictionary or a list default is copied
            into what the site set, so a change to it is kept.
        """
        if group is None:
            return self
        if self.key in group.given:
            return group.given[self.key]
        if isinstance(self.default, dict | list):
            return group.given.setdefault(
                self.key, copy.deepcopy(self.default)
            )
        return self.default

    def __set__(self, group: Settings, value: t.Any) -> None:
        """Check a value when the site sets it, then keep it.

        :param group: The group.
        :param value: The value from `conf.py`.
        """
        _check_value(self.key, value, "")
        group.given[self.key] = value


class Settings:
    """A group of the settings of Kaamiki, as `kaamiki.conf.show`."""

    schema: t.ClassVar[dict[str, Value[t.Any]]] = {}
    groups: t.ClassVar[dict[str, type[Settings]]] = {}
    name: t.ClassVar[str]
    given: dict[str, t.Any]

    def __init__(self, given: dict[str, t.Any]) -> None:
        """Make the group with the shared values.

        :param given: The values of the site, by key.
        """
        object.__setattr__(self, "given", given)

    def __init_subclass__(
        cls,
        *,
        name: str | None = None,
        prefix: str | None = None,
        **kwargs: t.Any,
    ) -> None:
        """Record the group and complete each of its settings.

        :param name: The name of the group in `kaamiki.conf`. The
            default is the name of the class in snake case.
        :param prefix: What the keys of the group start with. The
            default is the name of the group.
        :param kwargs: What the parent class takes.
        """
        super().__init_subclass__(**kwargs)
        cls.name = (
            SNAKE.sub("_", cls.__name__).lower() if name is None else name
        )
        start = cls.name if prefix is None else prefix
        for each in cls.values():
            each.key = each.key or "_".join(filter(None, (start, each.attr)))
            each.group = cls.name
            if each.choices:
                each.rule = each.read = checks.word(*each.choices)
            elif each.number is int:
                each.rule = whole(*BOUNDS[each.key])
                each.read = checks.integer(*map(int, BOUNDS[each.key]))
            elif each.number is float:
                each.rule = real(*BOUNDS[each.key])
                each.read = checks.number(*BOUNDS[each.key])
            Settings.schema[each.key] = each
        Settings.groups[cls.name] = cls

    @classmethod
    def values(cls) -> list[Value[t.Any]]:
        """List the settings of the group.

        :return: The settings, in the sequence of the class.
        """
        return [_ for _ in vars(cls).values() if isinstance(_, Value)]

    @classmethod
    def path(cls, attr: str = "") -> str:
        """Write how `conf.py` names the group or one of its settings.

        :param attr: The setting, or nothing for the group.
        :return: The name, as `kaamiki.conf.show.more`.
        """
        return ".".join(filter(None, (f"{NAME}.conf", cls.name, attr)))

    def __setattr__(self, attr: str, value: t.Any) -> None:
        """Refuse a name that is not a setting of the group.

        :param attr: The name that the site sets.
        :param value: The value.
        """
        if not isinstance(getattr(type(self), attr, None), Value):
            fail(
                f"{self.path(attr)}: expected a Kaamiki setting, got an"
                " unknown name"
            )
        object.__setattr__(self, attr, value)

    def __dir__(self) -> list[str]:
        """List the settings of the group.

        :return: The names of the settings.
        """
        return [each.attr for each in self.values()]

    def __repr__(self) -> str:
        """Show the settings of the group.

        :return: The name of the group and its settings.
        """
        return f"<{self.path()}: {', '.join(self.__dir__())}>"


class Icons(Settings):
    """The `kaamiki.conf.icons` settings."""

    style = Value(
        icons.DEFAULT_STYLE,
        choices=("solid", "regular", "light", "thin"),
        key="fa_style",
        reread=True,
    )
    kit = Value[str | None](None, text=checks.kit, key="fa_kit", reread=True)
    names = Value[dict[str, t.Any]]({}, site_icons, key="fa_icons")

    def update(
        self, names: Mapping[str, str] | None = None, /, **more: str
    ) -> None:
        """Add to the icon names of Kaamiki.

        :param names: The icon names and their icons.
        :param more: The same, as keywords.
        """
        self.names = {**self.names, **(names or {}), **more}


class Show(Settings):
    """The `kaamiki.conf.show` settings."""

    not_found = Value(True, boolean, key="show_404")
    breadcrumbs = Value(True, boolean, page=True)
    credit = Value(False, boolean, page=True)
    feedback = Value[bool | None](None, boolean, page=True)
    more = Value(True, boolean, page=True)
    more_after = Value(SHOW_MORE_AFTER, number=int)
    page_last_updated = Value(True, boolean, page=True)
    previous_next_cards = Value(True, boolean, page=True)
    previous_next_cards_count = Value(RELATED_PAGES, number=int)
    previous_next_pages = Value(False, boolean, page=True)
    scrolltop = Value(False, boolean, page=True)
    searchbox = Value(True, boolean, page=True)
    sitemap = Value(True, boolean)


class Media(Settings):
    """The `kaamiki.conf.media` settings."""

    enlarge = Value(True, boolean, page=True)


class Motion(Settings):
    """The `kaamiki.conf.motion` settings."""

    page_transitions = Value(False, boolean)
    prefetch = Value(True, boolean)
    speed = Value(0.625, number=float)


class Toctree(Settings):
    """The `kaamiki.conf.toctree` settings."""

    in_header = Value(True, boolean, page=True)
    includehidden = Value(True, boolean)
    maxdepth = Value(0, number=int)
    titles_only = Value(True, boolean)


class CodeExplain(Settings):
    """The `kaamiki.conf.code_explain` settings."""

    budget = Value(25, number=int, reread=True)
    cache = Value(True, boolean, reread=True)
    comprehensions = Value(False, boolean, reread=True)
    events = Value(
        "line, return", text=listed_in(TRACE_EVENTS, ", "), reread=True
    )
    limit = Value(100, number=int, reread=True)
    memory = Value(1024, number=int, reread=True)
    output_limit = Value(64, number=int, reread=True)
    python = Value[str | None](None, text=checks.text, reread=True)
    pythonpath = Value[list[str]]([], many(checks.text), reread=True)
    run = Value(False, boolean, reread=True)
    timeout = Value(10, number=int, reread=True)


class Youtube(Settings):
    """The `kaamiki.conf.youtube` settings."""

    allow = Value(
        "accelerometer; clipboard-write; encrypted-media; gyroscope;"
        " picture-in-picture; web-share",
        text=listed_in(PERMISSIONS, "; "),
        reread=True,
    )
    click_to_load = Value(True, boolean, reread=True)
    privacy = Value(True, boolean, reread=True)
    referrer_policy = Value(
        "strict-origin-when-cross-origin", checks.word(*REFERRERS), reread=True
    )


class Accordion(Settings):
    """The `kaamiki.conf.accordion` settings."""

    marker = Value("plus", choices=("plus", "down", "right"), reread=True)
    marker_position = Value("after", choices=("before", "after"), reread=True)


class Button(Settings):
    """The `kaamiki.conf.button` settings."""

    colours = Value[dict[str, str]](
        {}, table(lower(checks.slug), string(checks.colour)), reread=True
    )
    icon_position = Value("before", choices=("before", "after"), reread=True)
    scheme = Value("light", text=checks.text, reread=True)


class Tab(Settings):
    """The `kaamiki.conf.tab` settings."""

    icon_position = Value("before", choices=("before", "after"), reread=True)


class Embed(Settings):
    """The `kaamiki.conf.embed` settings."""

    css = Value[list[str]]([], many(ending(".css", STATIC_NAME)))
    iframe_hosts = Value[list[str]]([], many(checks.host), reread=True)
    js = Value[list[str]]([], many(ending(".js", STATIC_NAME)))
    js_loading = Value("defer", choices=("defer", "async", "normal"))


class Links(Settings):
    """The `kaamiki.conf.links` settings."""

    internal_hosts = Value[list[str]](
        [], many(checks.host), key="internal_hosts", reread=True
    )
    new_tab = Value(True, boolean, key="links_in_new_tab", reread=True)


class Roles(Settings, prefix=""):
    """The `kaamiki.conf.roles` settings."""

    colours = Value[dict[str, str]](
        {},
        table(lower(checks.slug), string(checks.colour)),
        key="role_colours",
        reread=True,
    )
    sharpie_colour = Value("yellow", text=checks.text, reread=True)
    underline_colour = Value("#FF9800", text=checks.text, reread=True)
    underline_width = Value(2.5, number=float, reread=True)
    underline_wobble = Value(1.0, number=float, reread=True)


class Release(Settings):
    """The `kaamiki.conf.release` settings."""

    kinds = Value[list[str]]([], many(lower(checks.slug)), reread=True)
    version_fmt = Value("%Y.%m.%d", text=moment(TIME_DIRECTIVES), reread=True)


class Site(Settings, prefix=""):
    """The `kaamiki.conf.site` settings."""

    project = Value[dict[str, t.Any]](
        {},
        shape(
            author=string(checks.text),
            avatar=string(checks.link),
            email=string(EMAIL_ONLY),
            source=string(
                lambda each: each if each == "#" else checks.web(each)
            ),
        ),
        reread=True,
    )
    license = Value[dict[str, t.Any]](
        {}, shape(name=string(checks.text), url=string(checks.web))
    )
    open_graph = Value[dict[str, t.Any]](
        {},
        shape(
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
    )
    favicons = Value[dict[str, str]](
        {}, shape(**dict.fromkeys(FAVICONS, string(STATIC_NAME)))
    )
    logo_size = Value[int | None](None, number=int)
    logos = Value[dict[str, str]](
        {}, shape(**dict.fromkeys(LOGOS, string(STATIC_NAME)))
    )
    feedback = Value[dict[str, t.Any]](
        {},
        shape(
            type=checks.word("mail", "link"),
            url=string(checks.link),
            subject=string(checks.text),
            title=string(checks.text),
            description=string(checks.text),
            button=string(checks.text),
            icon=string(checks.icon),
            split=boolean,
        ),
    )
    header_buttons = Value[dict[str, t.Any]]({}, table(checks.text, button))
    sidebar_buttons = Value[dict[str, t.Any]]({}, table(checks.text, button))
    last_updated_fmt = Value("", text=moment(TIME_DIRECTIVES))
    copy_headerlinks = Value(True, boolean)
    words_per_minute = Value(WORDS_PER_MINUTE, number=int)


class Root(Settings, name=""):
    """The settings of no group, directly on `kaamiki.conf`."""

    mode = Value(
        "dark", choices=("dark", "light", "system"), key="colour_mode"
    )

    icons: Icons
    show: Show
    media: Media
    motion: Motion
    toctree: Toctree
    code_explain: CodeExplain
    youtube: Youtube
    accordion: Accordion
    button: Button
    tab: Tab
    embed: Embed
    links: Links
    roles: Roles
    release: Release
    site: Site

    def __init__(self, given: dict[str, t.Any]) -> None:
        """Make `kaamiki.conf` with each group in it.

        :param given: What the site set, by key, shared by each group.
        """
        super().__init__(given)
        for name, group in Settings.groups.items():
            if name:
                object.__setattr__(self, name, group(given))

    def __setattr__(self, attr: str, value: t.Any) -> None:
        """Refuse a group, which cannot be set, and an unknown name.

        :param attr: The name that the site sets.
        :param value: The value.
        :raises AttributeError: For the name of a group.
        """
        if attr in Settings.groups:
            raise AttributeError(
                f"{self.path(attr)} is a group, set one of its settings"
            )
        super().__setattr__(attr, value)

    def __getitem__(self, key: str) -> t.Any:
        """Read a setting by its key, when the key is known only later.

        :param key: The key of the setting, as `show_more`.
        :return: The value, as the attribute of its group gives it.
        """
        value = Settings.schema[key]
        group = getattr(self, value.group) if value.group else self
        return getattr(group, value.attr)

    def __dir__(self) -> list[str]:
        """List the settings of no group, then the groups.

        :return: The names.
        """
        return [*super().__dir__(), *filter(None, Settings.groups)]


DEFAULTS: t.Final[dict[str, t.Any]] = {
    key: each.default for key, each in Settings.schema.items()
}
GROUPS: t.Final[dict[str, dict[str, str]]] = {
    name: {each.attr: each.key for each in group.values()}
    for name, group in Settings.groups.items()
    if name
}
ROOT: t.Final[dict[str, str]] = {each.attr: each.key for each in Root.values()}
PATHS: t.Final[dict[str, str]] = {
    **{
        key: f"{NAME}.conf.{group}.{attr}"
        for group, members in GROUPS.items()
        for attr, key in members.items()
    },
    **{key: f"{NAME}.conf.{attr}" for attr, key in ROOT.items()},
}
FLAT: t.Final[dict[str, str]] = {
    path.replace(".conf.", "_").replace(".", "_"): key
    for key, path in PATHS.items()
}
PARSE_TIME: t.Final[tuple[str, ...]] = tuple(
    key for key, each in Settings.schema.items() if each.reread
)
PAGE_SWITCHES: t.Final[tuple[str, ...]] = tuple(
    key for key, each in Settings.schema.items() if each.page
)
WHOLE_NUMBERS: t.Final[tuple[str, ...]] = tuple(
    key for key, each in Settings.schema.items() if each.number is int
)
REAL_NUMBERS: t.Final[tuple[str, ...]] = tuple(
    key for key, each in Settings.schema.items() if each.number is float
)
CHOICES: t.Final[dict[str, tuple[str, ...]]] = {
    key: each.choices for key, each in Settings.schema.items() if each.choices
}
RULES: t.Final[dict[str, Rule]] = {
    key: each.rule
    for key, each in Settings.schema.items()
    if each.rule is not None
}


def stored[V](env: BuildEnvironment, key: str, default: V) -> V:
    """Hold a value that Kaamiki keeps on the build environment.

    :param env: The build environment.
    :param key: The name of the value, without the `km_` prefix. The
        prefix keeps it apart from the values of Sphinx.
    :param default: The value to hold when there is none.
    :return: The value, which the caller can change. It is pickled with
        the environment, so it stays for the next build.
    """
    held: V = env.__dict__.setdefault(f"km_{key}", default)
    return held


def kept[V](env: BuildEnvironment, key: str, value: V) -> V | None:
    """Replace a value that Kaamiki keeps on the build environment.

    :param env: The build environment.
    :param key: The name of the value, without the prefix.
    :param value: The value to hold from now.
    :return: The value of the last build, or `None` at the first.
    """
    before = env.__dict__.get(f"km_{key}")
    env.__dict__[f"km_{key}"] = value
    return before


def option(key: str) -> str:
    """Write a setting as `conf.py` writes it.

    :param key: The name of the setting without the prefix, as
        `show_more`.
    :return: Its place on `kaamiki.conf`, as `kaamiki.conf.show.more`.
    """
    return PATHS[key]


def flat(key: str) -> str:
    """Write a setting as Sphinx and a `-D` know it.

    :param key: The name of the setting without the prefix, as
        `show_more`.
    :return: Its name in the configuration of Sphinx, with underscores
        between the parts, as `kaamiki_show_more`.
    """
    return PATHS[key].replace(".conf.", "_").replace(".", "_")


def register(app: Sphinx) -> None:
    """Make each setting a configuration value of Sphinx.

    :param app: The Sphinx application instance. Then Sphinx knows the
        name, gives Kaamiki the default, and reads or writes the pages
        again when the value changes. Kaamiki checks the values itself,
        so Sphinx does not check their types.
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
    """Collect what `conf.py` and `-D` of a site wrote.

    :param config: The Sphinx configuration. Sphinx has no public way
        to read what `conf.py` wrote, so this reads `_raw_config`. Each
        check of a setting starts from these names, as do the reads of
        `html_show_sphinx` and `html_use_index`.
    :return: The names and their values, with a `-D` over the value of
        `conf.py`.
    :raises KaamikiError: When this Sphinx has no `_raw_config`, so
        that no wrong setting gets through.
    """
    raw: dict[str, t.Any] | None = getattr(config, "_raw_config", None)
    if raw is None:
        fail(
            "this Sphinx has no Config._raw_config, which Kaamiki reads to"
            " check what conf.py wrote; use a Sphinx that Kaamiki supports"
            f" or report it to {CONTACT}"
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
    """Read a switch from a `-D`, `0` or `1`, as for Sphinx.

    :param argument: The value as written.
    :return: `True` when it is on.
    :raises ValueError: For other text.
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


@on("config-inited")
def overrides(app: Sphinx, config: Config) -> None:
    """Read the numbers and switches from a `-D`.

    :param app: The Sphinx application instance.
    :param config: The Sphinx configuration. Sphinx reads a `-D` by the
        type of the default, so a setting with a `None` default or a
        number with a point arrives as text. A number is read by
        `checks.integer` or `checks.number`, and a switch is `0` or
        `1`. Sphinx puts a `-D name.key=value` into the dictionary of
        the setting as text, so the switches and numbers of `ENTRIES`
        are read there and put back.
    :raises KaamikiError: For a value that the setting does not take.
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

    :param value: The default.
    :return: A function that returns it. Sphinx drops a `-D` with a
        warning for a plain float default, but a function lets the
        text through.
    """
    return lambda _: value


CONF: t.Final[Root] = Root({})


class Configured(dict[str, t.Any]):
    """What a site set, read from the Sphinx configuration."""

    def __init__(self, config: Config) -> None:
        """Read from a Sphinx configuration.

        :param config: The Sphinx configuration.
        """
        super().__init__()
        self.config = config

    def __contains__(self, key: object) -> bool:
        """Say that each Kaamiki setting has a value.

        :param key: The key of the setting.
        :return: `True` for a key in the schema.
        """
        return key in Settings.schema

    def __missing__(self, key: str) -> t.Any:
        """Read a setting, or its default when the site set none.

        :param key: The key of the setting.
        :return: A copy, so that no caller can change the setting.
        """
        value = self.config[flat(key)]
        return copy.deepcopy(DEFAULTS[key] if value is None else value)

    def __setitem__(self, key: str, value: t.Any) -> None:
        """Refuse a change, because the configuration is read only.

        :param key: The key of the setting.
        :param value: The value.
        :raises TypeError: Always.
        """
        raise TypeError(f"{PATHS[key]}: expected no change while building")


def values(config: Config) -> Root:
    """Read the settings of Kaamiki, by group.

    :param config: The Sphinx configuration.
    :return: The settings, as `values(config).show.more`.
    """
    return Root(Configured(config))


def frozen(value: t.Any) -> t.Any:
    """Make a value that no one can change.

    :param value: The value.
    :return: A dictionary as a read-only mapping and a list as a tuple,
        with each item made the same. Other values stay as they are.
    """
    if isinstance(value, MappingProxyType):
        return value
    if isinstance(value, dict):
        return MappingProxyType({k: frozen(v) for k, v in value.items()})
    if isinstance(value, list | tuple):
        return tuple(frozen(_) for _ in value)
    return value


class Kaamiki:
    """The values of Kaamiki for the templates, as `kaamiki.show`."""

    __slots__ = ("_page", "_path", "_values")
    _page: bool
    _path: str
    _values: dict[str, t.Any]

    def __init__(
        self, path: str, values: Mapping[str, t.Any], *, page: bool = False
    ) -> None:
        """Keep the values of a group.

        :param path: The name of the group, as `kaamiki.show`.
        :param values: The values of the group, by name.
        :param page: Whether this is the copy of one page, which the
            handlers of the page can change.
        """
        object.__setattr__(self, "_page", page)
        object.__setattr__(self, "_path", path)
        object.__setattr__(
            self, "_values", {k: frozen(v) for k, v in values.items()}
        )

    @classmethod
    def of(cls, builder: Builder) -> Kaamiki:
        """Read the values that Kaamiki made for the build.

        :param builder: The builder, which holds the values. They are
            not pickled.
        :return: The values, as `Kaamiki.of(builder).show.breadcrumbs`.
        """
        found: Kaamiki = builder.__dict__["km_kaamiki"]
        return found

    def __getattr__(self, name: str) -> t.Any:
        """Read a value, or stop for a name that is not one.

        :param name: The name, as `breadcrumbs`.
        :return: The value.
        :raises AttributeError: For a name that starts with `_`, which
            Python and Jinja ask for.
        :raises KaamikiError: For another name that is not a value,
            with the nearest name.
        """
        if name.startswith("_"):
            raise AttributeError(name)
        if name not in self._values:
            near = difflib.get_close_matches(name, self._values, n=1)
            fail(
                f"{self._path}.{name}: expected a Kaamiki value, got an"
                " unknown name"
                + (f"; did you mean {self._path}.{near[0]}?" if near else "")
            )
        return self._values[name]

    def __setattr__(self, name: str, value: t.Any) -> None:
        """Refuse a change.

        :param name: The name.
        :param value: The value.
        :raises TypeError: Always.
        """
        raise TypeError(f"{self._path}.{name}: expected no change")

    def __setitem__(self, path: str, value: t.Any) -> None:
        """Change a value for one page.

        :param path: The value, as `show.breadcrumbs`.
        :param value: The value for the page.
        :raises TypeError: For the values of the site.
        """
        group, _, name = path.rpartition(".")
        if not self._page:
            raise TypeError(f"{self._path}.{path}: expected no change")
        found = getattr(self, group) if group else self
        found._values[name] = frozen(value)

    def __copy__(self) -> Kaamiki:
        """Copy the groups for one page.

        :return: The copy, whose values the handlers of the page can
            change. The values themselves are not copied.
        """
        return Kaamiki(
            self._path,
            {
                k: copy.copy(v) if isinstance(v, Kaamiki) else v
                for k, v in self._values.items()
            },
            page=True,
        )

    def __dir__(self) -> list[str]:
        """List the names of the group.

        :return: The names.
        """
        return list(self._values)

    def __repr__(self) -> str:
        """Show the group and its names.

        :return: The name of the group and its names.
        """
        return f"<{self._path}: {', '.join(self._values)}>"


@on("config-inited")
def apply(app: Sphinx, config: Config) -> None:
    """Give Sphinx what `conf.py` set on `kaamiki.conf`.

    :param app: The Sphinx application instance.
    :param config: The Sphinx configuration. A `-D` on the command line
        has priority over `conf.py`, as for the settings of Sphinx. A
        `-D name.key=value` has priority entry by entry over the
        dictionary from `conf.py`.
    """
    del app
    for key, value in CONF.given.items():
        name = flat(key)
        if name in config.overrides:
            continue
        value = copy.deepcopy(value)
        entries = config[name]
        if isinstance(value, dict) and isinstance(entries, dict):
            value = {**value, **entries}
        config[name] = value


def validate(app: Sphinx) -> None:
    """Check each setting that a site gave Kaamiki.

    :param app: The Sphinx application instance.
    :raises KaamikiError: For the first problem. `_read` refuses a
        plain `kaamiki_` name in `conf.py` (a dictionary below one is a
        `-D name.key=value`), a `-D` for a name that is not of Kaamiki,
        and a value that is `None` or of a wrong type, spelling or
        range. The other `_check_` helpers refuse an icon or a colour
        that Kaamiki cannot draw, a wrong `html_baseurl` or
        `html_last_updated_fmt`, the `KAAMIKI_FA_KIT` environment
        variable, settings that contradict each other, a file that is
        not in `html_static_path`, a missing folder or Python, a date
        format that cannot be read again, and a theme option that the
        sidebar does not read.
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
    """Read the settings of a site, and refuse the wrong ones.

    :param config: The Sphinx configuration. A site sets a setting on
        `kaamiki.conf`, which `apply` gave to Sphinx, or with a `-D`. A
        plain `kaamiki_` name in `conf.py` is neither. A dictionary
        below one comes from a `-D name.key=value`, so it is read and
        checked as the others.
    :param conf: The path of `conf.py`, for the messages.
    :return: The settings that the site gave, by key.
    """
    given: dict[str, t.Any] = {}
    for name, value in site_values(config).items():
        if not name.startswith(PREFIX) or name in config.overrides:
            continue
        key = FLAT.get(name)
        if key is None:
            fail(
                f"{name}: expected a Kaamiki setting, got an unknown name",
                conf,
            )
        if isinstance(DEFAULTS[key], dict) and isinstance(value, dict):
            given[key] = config[name]
            continue
        fail(
            f"{name}: expected {option(key)}, got a plain name in conf.py",
            conf,
        )
    for key in CONF.given:
        if flat(key) not in config.overrides:
            given[key] = config[flat(key)]
    for name in sorted(config.overrides):
        if not name.startswith(PREFIX):
            continue
        if name not in FLAT:
            fail(
                f"{name}: expected a Kaamiki setting, got an unknown name",
                conf,
            )
        given[FLAT[name]] = config[name]
    for key, value in given.items():
        _check_value(key, value, conf)
    return given


def _check_value(key: str, value: t.Any, conf: str) -> None:
    """Check one setting against its rule.

    :param key: The name of the setting without the prefix.
    :param value: The value that it got.
    :param conf: The path of `conf.py`, for the messages.
    """
    if value is None:
        if DEFAULTS[key] is not None:
            fail(
                f"{option(key)}: expected a value, got None; leave it out for"
                " the default",
                conf,
            )
        return
    try:
        RULES[key](value)
    except (TypeError, ValueError) as error:
        fail(f"{option(key)}: {error}", conf)


def _check_kit(given: dict[str, t.Any], conf: str) -> None:
    """Check the Font Awesome kit an environment variable names.

    :param given: The settings given.
    :param conf: The path of `conf.py`, for the messages.
    """
    kit = os.environ.get(icons.KIT_VARIABLE)
    if kit and not given.get("fa_kit"):
        try:
            string(checks.kit)(kit)
        except (TypeError, ValueError) as error:
            fail(f"environment variable {icons.KIT_VARIABLE}: {error}", conf)


def _check_icons(config: Config, given: dict[str, t.Any], conf: str) -> None:
    """Check every icon a setting names.

    :param config: The Sphinx configuration.
    :param given: The settings given.
    :param conf: The path of `conf.py`, for the messages.
    """
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
    """Check the colours a role is drawn in.

    :param given: The settings given.
    :param conf: The path of `conf.py`, for the messages.
    """
    colours = {**given.get("role_colours", {})}
    for key in ("sharpie_colour", "underline_colour"):
        if key in given:
            try:
                checks.colour(given[key], (*TONES, *colours))
            except (TypeError, ValueError) as error:
                fail(f"{option(key)}: {error}", conf)


def _check_site(config: Config, conf: str) -> None:
    """Check the address and the date of Sphinx.

    :param config: The Sphinx configuration.
    :param conf: The path of `conf.py`, for the messages.
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
    """Check the button scheme and the colours a site adds.

    :param given: The settings given.
    :param conf: The path of `conf.py`, for the messages.
    """
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
    """Check the settings that only make sense together.

    :param config: The Sphinx configuration.
    :param given: The settings given.
    :param conf: The path of `conf.py`, for the messages.
    """
    feedback = given.get("feedback", {})
    if feedback and given.get("show_feedback") is False:
        fail(
            "kaamiki.conf.show.feedback: expected True or nothing as"
            " kaamiki.conf.site.feedback is set, got False",
            conf,
        )
    if given.get("show_feedback") is True and not (
        given.get("project", {}).get("email") or feedback.get("url")
    ):
        fail(
            "kaamiki.conf.show.feedback: expected an email in"
            " kaamiki.conf.site.project or a url in kaamiki.conf.site.feedback"
            " to send feedback to, got neither",
            conf,
        )
    if feedback.get("split") and not (
        given.get("project", {}).get("email") or feedback.get("url")
    ):
        fail(
            "kaamiki.conf.site.feedback: split expected an email in"
            " kaamiki.conf.site.project or a url for its button, got neither",
            conf,
        )
    if "show_more_after" in given and given.get("show_more") is False:
        fail(
            "kaamiki.conf.show.more: expected True or nothing as"
            " kaamiki.conf.show.more_after is set, got False",
            conf,
        )
    if (
        "show_previous_next_cards_count" in given
        and given.get("show_previous_next_cards") is False
    ):
        fail(
            "kaamiki.conf.show.previous_next_cards: expected True or nothing"
            " as kaamiki.conf.show.previous_next_cards_count is set, got"
            " False",
            conf,
        )
    if "show_previous_next_cards_count" in given and given.get(
        "show_previous_next_pages"
    ):
        fail(
            "kaamiki.conf.show.previous_next_pages: expected False or nothing"
            " as kaamiki.conf.show.previous_next_cards_count is set, got"
            " True, which shows the buttons and no cards",
            conf,
        )
    if given.get("show_previous_next_cards") is False and not given.get(
        "show_previous_next_pages"
    ):
        fail(
            "kaamiki.conf.show.previous_next_pages: expected True with"
            " kaamiki.conf.show.previous_next_cards off, got False; a page"
            " needs one of them to lead on",
            conf,
        )
    if feedback.get("type") == "link" and "url" not in feedback:
        fail(
            "kaamiki.conf.site.feedback: type 'link' expected a url, got none",
            conf,
        )
    if "url" in feedback and feedback.get("type") != "link":
        fail(
            "kaamiki.conf.site.feedback: url expected type 'link', got"
            f" {feedback.get('type')!r}",
            conf,
        )
    terms = given.get("license", {})
    if "url" in terms and "name" not in terms:
        fail("kaamiki.conf.site.license: url expected a name, got none", conf)
    style = given.get("fa_style")
    if style in ("light", "thin") and not icons.Icons.of(config).kit:
        fail(
            f"kaamiki.conf.icons.style: {style!r} needs a Font Awesome Pro"
            f" kit, set kaamiki.conf.icons.kit or {icons.KIT_VARIABLE}",
            conf,
        )
    logos = given.get("logos", {})
    if logos and set(logos) != set(LOGOS):
        fail(
            "kaamiki.conf.site.logos: expected both light and dark, got"
            f" {', '.join(sorted(logos))}",
            conf,
        )
    if logos and (config.html_theme_options.get("logo") or config.html_logo):
        fail(
            "kaamiki.conf.site.logos: expected html_logo and"
            " html_theme_options['logo'] unset, got one of them set",
            conf,
        )
    drawn = logos or config.html_theme_options.get("logo") or config.html_logo
    if given.get("logo_size") is not None and not drawn:
        fail(
            "kaamiki.conf.site.logo_size: expected a site with a logo, got"
            " none; set html_theme_options['logo'] or html_logo",
            conf,
        )


def _check_static(app: Sphinx, given: dict[str, t.Any], conf: str) -> None:
    """Check the files a site names are in `html_static_path`.

    :param app: The Sphinx application instance.
    :param given: The settings given.
    :param conf: The path to `conf.py`, for the messages.
    """
    statics = [
        p.join(app.confdir, each) for each in app.config.html_static_path
    ]

    def present(name: str) -> bool:
        """Say whether a static folder has the file.

        :param name: The name of the file.
        """
        return any(p.isfile(p.join(each, name)) for each in statics)

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
                "html_theme_options['logo']: expected a file in"
                f" html_static_path, got {logo!r}",
                conf,
            )
    for key, found in (
        ("embed_css", given.get("embed_css", [])),
        ("embed_js", given.get("embed_js", [])),
        ("favicons", given.get("favicons", {}).values()),
        ("logos", given.get("logos", {}).values()),
    ):
        for name in found:
            if not present(name):
                fail(
                    f"{option(key)}: expected a file in html_static_path, got"
                    f" {name!r}",
                    conf,
                )


def _check_theme(config: Config, conf: str) -> None:
    """Check that the sidebar of Kaamiki reads each theme option.

    :param config: The Sphinx configuration.
    :param conf: The path of `conf.py`, for the messages.
    """
    for name in UNREAD_OPTIONS:
        if name in config.html_theme_options:
            fail(
                f"html_theme_options[{name!r}]: expected nothing, got"
                f" {config.html_theme_options[name]!r}; Kaamiki's sidebar is"
                " fixed, so this changes nothing, and the navigation is set"
                " with the kaamiki.conf.toctree settings",
                conf,
            )


def _check_code_explain(
    app: Sphinx, given: dict[str, t.Any], conf: str
) -> None:
    """Check the folders and Python a `code-explain` is run with.

    :param app: The Sphinx application instance.
    :param given: The settings given.
    :param conf: The path to `conf.py`, for the messages.
    """
    for entry in given.get("code_explain_pythonpath", []):
        if not p.isdir(p.join(app.srcdir, entry)):
            fail(
                "kaamiki.conf.code_explain.pythonpath: expected a directory,"
                f" got {entry!r}",
                conf,
            )
    python = given.get("code_explain_python")
    if python is not None and not given.get("code_explain_run"):
        fail(
            "kaamiki.conf.code_explain.run: expected True as"
            " kaamiki.conf.code_explain.python is set, got False, so nothing"
            " runs with it",
            conf,
        )
    if python is not None and not p.isfile(python):
        fail(
            "kaamiki.conf.code_explain.python: expected a file, got"
            f" {python!r}",
            conf,
        )
    if given.get("code_explain_run") and os.name != "posix":
        fail(
            "kaamiki.conf.code_explain.run: expected a POSIX system like"
            f" Linux or macOS to run python on, got {sys.platform!r}",
            conf,
        )


def _check_dates(given: dict[str, t.Any], conf: str) -> None:
    """Check the date formats a site wrote.

    :param given: The settings given.
    :param conf: The path to `conf.py`, for the messages.
    """
    for key in ("release_version_fmt", "last_updated_fmt"):
        if given.get(key) and "%" not in given[key]:
            fail(
                f"{option(key)}: expected a date format with a directive like"
                f" %Y, got {given[key]!r}",
                conf,
            )
    if given.get("release_version_fmt"):
        sample = dt.fromisoformat("2026-01-02").strftime(
            given["release_version_fmt"]
        )
        try:
            dt.strptime(sample, given["release_version_fmt"])  # noqa: DTZ007
        except ValueError, re.error:
            fail(
                "kaamiki.conf.release.version_fmt: expected a format that"
                " reads back what it writes, got one that doesn't",
                conf,
            )


def _check_translation(
    app: Sphinx, given: dict[str, t.Any], conf: str
) -> None:
    """Check the date format that the catalogue of a language gives.

    :param app: The Sphinx application instance.
    :param given: The settings that the site gave. The check counts
        only when the site sets no format.
    :param conf: The path of `conf.py`, for the messages.
    """
    if app.config.html_last_updated_fmt or given.get("last_updated_fmt"):
        return
    try:
        moment(TIME_DIRECTIVES)(str(_("%d %B %Y")))
    except (TypeError, ValueError) as error:
        fail(
            f"the translation of '%d %B %Y' into {app.config.language}:"
            f" {error}",
            conf,
        )


@on("env-get-outdated")
def reread(
    app: Sphinx,
    env: BuildEnvironment,
    added: set[str],
    changed: set[str],
    removed: set[str],
) -> list[str]:
    """Read each page again when the kit or the address changes.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param added: The pages that Sphinx found new.
    :param changed: The pages that Sphinx found changed.
    :param removed: The pages that Sphinx found removed.
    :return: Each page when the kit or the address is not the same as
        at the last build, else none, and none at the first build.
        Sphinx reads each page again for a change in `PARSE_TIME`, but
        it cannot see the kit from `KAAMIKI_FA_KIT` or `html_baseurl`,
        which Sphinx records only for the HTML builders.
    """
    del added, changed, removed
    now = json.dumps([icons.Icons.of(app.config).kit, app.config.html_baseurl])
    before = kept(env, "settings", now)
    return sorted(env.found_docs) if before not in (None, now) else []
