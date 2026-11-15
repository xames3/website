"""\
Input Checks
============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 23 October 2026
Last updated on: 15 November 2026

Kaamiki takes a correct value or stops the build. It does not change,
guess or ignore a value. A check in this file reads each option, role,
page field and setting, and a wrong value raises `KaamikiError`.
`install_reporter` puts `report` before the handler of Sphinx for
uncaught errors, for all of the process. Sphinx keeps that handler in
a private module, so Kaamiki does not change it when a version of
Sphinx moves it. `report` gives each error that is not a
`KaamikiError` to the handler that it replaced.
"""

from __future__ import annotations

import logging
import os.path as p
import re
import sys
import traceback
import typing as t
from urllib.parse import urlsplit

from babel import Locale
from babel import UnknownLocaleError
from docutils import nodes
from docutils.transforms import Transform
from docutils.utils import Reporter
from sphinx.errors import SphinxError
from sphinx.errors import SphinxParallelError

from kaamiki.extensions.utils.hooks import on

if t.TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Collection
    from collections.abc import Sequence

    from sphinx.application import Sphinx

ERROR_LEVEL: t.Final[int] = Reporter.ERROR_LEVEL
TEXT_LENGTH: t.Final[int] = 300
URL_LENGTH: t.Final[int] = 2048
HOST_LENGTH: t.Final[int] = 253
SLUG: t.Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}")
NAME_LENGTH: t.Final[int] = 64
CLASS_COUNT: t.Final[int] = 8
DIGITS: t.Final[re.Pattern[str]] = re.compile(r"[0-9]+")
ICON_WORDS: t.Final[int] = 6
DECIMAL: t.Final[re.Pattern[str]] = re.compile(
    r"(?:0|[1-9][0-9]{0,5})(?:\.[0-9]{1,6})?"
)
LENGTH: t.Final[re.Pattern[str]] = re.compile(
    r"(?:(?:0|[1-9][0-9]{0,2})(?:\.[0-9]{1,3})?rem|0)"
)
FAMILY_STYLES: t.Final[dict[str, dict[str, str]]] = {
    "classic": {
        "solid": "fas",
        "regular": "far",
        "light": "fal",
        "thin": "fat",
    },
    "duotone": {
        "solid": "fad",
        "regular": "fadr",
        "light": "fadl",
        "thin": "fadt",
    },
    "sharp": {
        "solid": "fass",
        "regular": "fasr",
        "light": "fasl",
        "thin": "fast",
    },
    "sharp-duotone": {
        "solid": "fasds",
        "regular": "fasdr",
        "light": "fasdl",
        "thin": "fasdt",
    },
    "chisel": {"regular": "facr"},
    "etch": {"solid": "faes"},
    "graphite": {"thin": "fagt"},
    "jelly": {"regular": "fajr"},
    "jelly-fill": {"regular": "fajfr"},
    "jelly-duo": {"regular": "fajdr"},
    "mosaic": {"solid": "fams"},
    "notdog": {"solid": "fans"},
    "notdog-duo": {"solid": "fands"},
    "pixel": {"regular": "fapr"},
    "slab": {"regular": "faslr"},
    "slab-press": {"regular": "faslpr"},
    "slab-duo": {"regular": "fasldr"},
    "slab-press-duo": {"regular": "faslpdr"},
    "thumbprint": {"light": "fatl"},
    "utility": {"semibold": "fausb"},
    "utility-fill": {"semibold": "faufsb"},
    "utility-duo": {"semibold": "faudsb"},
    "vellum": {"solid": "favs"},
    "whiteboard": {"semibold": "fawsb"},
}
STYLE_NAMES: t.Final[dict[str, str]] = {
    "fa-brands": "brands",
    "fab": "brands",
    **{
        f"fa-{style}": style
        for styles in FAMILY_STYLES.values()
        for style in styles
    },
    **{short: style for style, short in FAMILY_STYLES["classic"].items()},
}
FAMILY_NAMES: t.Final[dict[str, tuple[str, str | None]]] = {
    **{f"fa-{family}": (family, None) for family in FAMILY_STYLES},
    **{
        short: (family, style)
        for family, styles in FAMILY_STYLES.items()
        if family != "classic"
        for style, short in styles.items()
    },
}
STYLES: t.Final[frozenset[str]] = frozenset(STYLE_NAMES)
FAMILIES: t.Final[frozenset[str]] = frozenset(FAMILY_NAMES)
MODIFIERS: t.Final[re.Pattern[str]] = re.compile(
    r"fa-(?:fw|spin|pulse|beat|fade|beat-fade|bounce|shake|spin-pulse"
    r"|spin-reverse|flip-horizontal|flip-vertical|flip-both"
    r"|rotate-(?:90|180|270)|2xs|xs|sm|lg|xl|2xl|[1-9]x|10x)"
    r"|km-tone--(?:red|yellow|blue|green)"
)
ICON_NAME: t.Final[re.Pattern[str]] = re.compile(
    r"(?:fa-)?[a-z0-9]+(?:-[a-z0-9]+)*"
)
HOST: t.Final[re.Pattern[str]] = re.compile(
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
    r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)*"
)
FILE: t.Final[re.Pattern[str]] = re.compile(
    r"(?!(?:.*/)?\.\.(?:/|$))[\w.+-][\w./+-]*"
)
EMAIL: t.Final[re.Pattern[str]] = re.compile(
    r"[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9-]{1,63}(?:\.[A-Za-z0-9-]{1,63})+"
)
HEX: t.Final[re.Pattern[str]] = re.compile(
    r"#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})"
)
HSL: t.Final[re.Pattern[str]] = re.compile(
    r"([0-9]{1,3}(?:\.[0-9]+)?) ([0-9]{1,3}(?:\.[0-9]+)?)%"
    r" ([0-9]{1,3}(?:\.[0-9]+)?)%"
)
IMAGES: t.Final[re.Pattern[str]] = re.compile(
    r".+\.(?:jpe?g|png|webp|avif|gif|svg)", re.IGNORECASE
)
LOCALE: t.Final[re.Pattern[str]] = re.compile(
    r"[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*"
)
DIRECTIVE_OPTION: t.Final[re.Pattern[str]] = re.compile(
    r'Error in "(?P<name>[\w-]+)" directive:\s*invalid option value: '
    r'\(option: "(?P<option>[\w-]+)"; value: '
    r"(?P<value>'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"|.*?)\)\s*(?P<why>.*)",
    re.DOTALL,
)
UNKNOWN: t.Final[re.Pattern[str]] = re.compile(
    r'Error in "(?P<name>[\w-]+)" directive:\s*'
    r'unknown option: "(?P<option>[^"]+)"'
)
ARGUMENTS: t.Final[re.Pattern[str]] = re.compile(
    r'Error in "(?P<name>[\w-]+)" directive:\s*(?P<why>.*)', re.DOTALL
)
COUNTS: t.Final[tuple[tuple[re.Pattern[str], str], ...]] = (
    (
        re.compile(r"(\d+) argument\(s\) required, (\d+) supplied"),
        "expected {0} {noun}, got {1}",
    ),
    (
        re.compile(r"maximum (\d+) argument\(s\) allowed, (\d+) supplied"),
        "expected at most {0} {noun}, got {1}",
    ),
    (
        re.compile(r'invalid option data: duplicate option "([\w-]+)"'),
        ":{0}: expected once, got twice",
    ),
    (re.compile(r"no content permitted"), "expected no content, got some"),
)


class KaamikiError(SphinxError):
    """A value from a site is wrong, so the build stops."""

    category = "KaamikiError"
    __module__ = "kaamiki"


def fail(message: str, where: str = "") -> t.NoReturn:
    """Stop the build.

    :param message: What is wrong and what is correct.
    :param where: The `source:line` of the mistake, if known. The
        message is `where: what`, as `report` reads it again from a
        parallel reader.
    :raises KaamikiError: Always.
    """
    raise KaamikiError(f"{where}: {message}" if where else message)


def text(argument: str | None, maximum: int = TEXT_LENGTH) -> str:
    """Read a line of text that must not be empty.

    :param argument: The value as written.
    :param maximum: The maximum number of characters.
    :return: The text without the spaces around it.
    :raises ValueError: When it is blank, has control characters (a
        newline is permitted, for an option on more than one line) or
        is longer than `maximum`.
    """
    value = (argument or "").strip()
    if not value:
        raise ValueError("expected some text, got none")
    if len(value) > maximum:
        raise ValueError(
            f"expected at most {maximum} characters, got {len(value)}"
        )
    if any(_ != "\n" and (ord(_) < 32 or 127 <= ord(_) <= 159) for _ in value):
        raise ValueError(
            f"expected text without control characters, got {argument!r}"
        )
    return value


def slug(argument: str | None) -> str:
    """Read a name of letters, digits, `-` and `_`.

    :param argument: The value as written.
    :return: The name.
    :raises ValueError: For other text.
    """
    value = (argument or "").strip()
    if not SLUG.fullmatch(value):
        raise ValueError(
            "expected a name of letters, digits, - and _ up to 64 long,"
            f" got {argument!r}"
        )
    return value


def reference_name(argument: str | None) -> str:
    """Read a `:name:` as docutils does, and check that it is a name.

    :param argument: The value as written. Any text is a name, as for
        the directives of docutils, also with spaces, capitals and
        other scripts. docutils makes the id, as `my-note` for `My
        Note`, or `id1` when it cannot write it in ASCII.
    :return: The name, with each run of spaces as one space.
    :raises ValueError: For no name, an empty name, a control
        character, no letter, or more than `NAME_LENGTH` characters.
    :raises TypeError: For a value that is not text.
    """
    if argument is None:
        raise ValueError("expected a name, got none")
    if not isinstance(argument, str):
        raise TypeError(f"expected a name, got {argument!r}")
    value = " ".join(argument.split())
    if not value:
        raise ValueError("expected a name, got none")
    if any(ord(_) < 32 or ord(_) == 127 for _ in argument if _ != "\n"):
        raise ValueError(
            f"expected a name without control characters, got {argument!r}"
        )
    if len(value) > NAME_LENGTH:
        raise ValueError(
            f"expected a name up to {NAME_LENGTH} long, got {len(value)}"
        )
    if not any(_.isalpha() for _ in value):
        raise ValueError(
            f"expected a name with a letter in it, got {argument!r}"
        )
    return value


def classes(argument: str | None) -> list[str]:
    """Read class names as docutils does, and check each one.

    :param argument: The names as written. They are split at spaces and
        made into ids, as the `:class:` option of docutils does, so
        `Foo_Bar` is `foo-bar`. A comma with no space after it joins
        two names, so `big,red` is `big-red`.
    :return: The names, in the sequence written, each one time.
    :raises ValueError: For no names, a name that cannot make a class,
        a name longer than `NAME_LENGTH`, or more than `CLASS_COUNT`
        names.
    :raises TypeError: For a value that is not text.
    """
    if argument is None or (
        isinstance(argument, str) and not argument.strip()
    ):
        raise ValueError("expected one or more class names, got none")
    if not isinstance(argument, str):
        raise TypeError(f"expected class names, got {argument!r}")
    found: list[str] = []
    for each in argument.split():
        name = nodes.make_id(each)
        if not name:
            raise ValueError(
                f"expected class names with a letter in them, got {each!r}"
            )
        if len(name) > NAME_LENGTH:
            raise ValueError(
                f"expected class names up to {NAME_LENGTH} long, got {each!r}"
            )
        if name not in found:
            found.append(name)
    if len(found) > CLASS_COUNT:
        raise ValueError(
            f"expected up to {CLASS_COUNT} class names, got {len(found)}"
        )
    return found


def encoding(argument: str | None) -> str:
    """Read a text encoding that Python knows.

    :param argument: The name as written, as `utf-8`.
    :return: The name, trimmed.
    :raises ValueError: For no name, an empty name, or a name that
        Python does not have.
    """
    value = (argument or "").strip()
    try:
        "".encode(value)
    except (LookupError, ValueError) as error:
        raise ValueError(
            f"expected a text encoding like utf-8, got {argument!r}"
        ) from error
    return value


def pattern(
    expression: str | re.Pattern[str], hint: str
) -> Callable[[str | None], str]:
    """Make a check for text in a specified form.

    :param expression: The pattern that all of the text must match.
    :param hint: What the message says is expected.
    :return: The check, which takes the text as it is, with its spaces.
    """
    regex = re.compile(expression)

    def read(argument: str | None) -> str:
        """Read the text, which must match.

        :param argument: The value as written.
        :return: The text.
        :raises ValueError: When it does not match.
        """
        value = argument or ""
        if not regex.fullmatch(value):
            raise ValueError(f"expected {hint}, got {argument!r}")
        return value

    return read


def word(*choices: str) -> Callable[[str | None], str]:
    """Make a check for an option that takes one of some words.

    :param choices: The words that it takes, as they must be written.
    :return: The check.
    """

    def read(argument: str | None) -> str:
        """Read the word, which must be one of the choices.

        :param argument: The value as written.
        :return: The word.
        :raises ValueError: For a different word.
        """
        if argument not in choices:
            raise ValueError(
                f"expected one of {', '.join(map(repr, choices))}, got "
                f"{argument!r}"
            )
        return argument

    return read


def integer(low: int, high: int) -> Callable[[str | None], int]:
    """Make a check for a whole number in a range.

    :param low: The minimum.
    :param high: The maximum.
    :return: The check, which takes only digits: no sign, no `_`, no
        other scripts and no leading zeros. It removes the spaces
        around them.
    """

    def read(argument: str | None) -> int:
        """Read the digits as a number in the range.

        :param argument: The value as written.
        :return: The number.
        :raises ValueError: For other text, or a number out of range.
        """
        value = (argument or "").strip()
        if not DIGITS.fullmatch(value):
            raise ValueError(f"expected a whole number, got {argument!r}")
        if len(value) > 1 and value.startswith("0"):
            raise ValueError(
                f"expected a whole number with no leading zero, got "
                f"{argument!r}"
            )
        if len(value) > len(str(high)):
            raise ValueError(f"expected {low} to {high}, got {argument!r}")
        amount = int(value)
        if not low <= amount <= high:
            raise ValueError(f"expected {low} to {high}, got {argument!r}")
        return amount

    return read


def number(low: float, high: float) -> Callable[[str | None], float]:
    """Make a check for a number with decimals in a range.

    :param low: The minimum.
    :param high: The maximum.
    :return: The check, which takes only digits and a point.
    """

    def read(argument: str | None) -> float:
        """Read the number in the range.

        :param argument: The value as written.
        :return: The number.
        :raises ValueError: For other text, or a number out of range.
        """
        value = (argument or "").strip()
        if not DECIMAL.fullmatch(value):
            raise ValueError(f"expected a number, got {argument!r}")
        amount = float(value)
        if not low <= amount <= high:
            raise ValueError(f"expected {low:g} to {high:g}, got {argument!r}")
        return amount

    return read


def spacing(
    presets: Sequence[str], high: float
) -> Callable[[str | None], str]:
    """Make a check for a preset space or lengths in rem.

    :param presets: The words that are spaces.
    :param high: The maximum length, in rem.
    :return: The check, which gives the preset or the lengths. A bare
        `0` gets its unit, because `calc()` needs it.
    """

    def read(argument: str | None) -> str:
        """Read the space, as a preset or as lengths.

        :param argument: The value as written.
        :return: The preset or the lengths.
        :raises ValueError: For other text, or a length out of range.
        """
        value = " ".join((argument or "").split())
        if value in presets:
            return value
        words = value.split(" ")
        if len(words) <= 2 and all(LENGTH.fullmatch(_) for _ in words):
            if all(float(_.removesuffix("rem")) <= high for _ in words):
                return " ".join("0rem" if _ == "0" else _ for _ in words)
            raise ValueError(
                f"expected lengths up to {high:g}rem, got {value!r}"
            )
        raise ValueError(
            f"expected {', '.join(presets)} or one or two lengths from 0 to"
            f" {high:g}rem like 1.5rem or 1rem 2rem, got {argument!r}"
        )

    return read


def lengths(value: str) -> tuple[str, str]:
    """Split a space from `spacing` into two lengths.

    :param value: One or two lengths, as `spacing` gives them.
    :return: The first and the last length, the same for one length.
        They are a vertical and a horizontal gap, or an edge above and
        below.
    """
    words = value.split()
    return words[0], words[-1]


def icon(argument: str | None) -> str:
    """Read a Font Awesome icon, as an option or a role writes it.

    :param argument: The icon as written: `plus`, `fa-plus`, or a style
        and a name, `far fa-plus`, with a family of `FAMILY_STYLES`
        before the style, `fa-sharp fa-solid fa-plus` or
        `fa-jelly fa-plus`. A family takes only its own styles. After a
        style or a family, sizes
        and animations can follow, as `fa-lg` and `fa-spin`, and the
        Kaamiki tones `km-tone--red`, `km-tone--yellow`,
        `km-tone--blue` and `km-tone--green`. The maximum is
        `ICON_WORDS` words.
    :return: The icon, as written.
    :raises ValueError: When it is not written as an icon. This cannot
        know whether Font Awesome has the name.
    """
    parts = (argument or "").split()
    if not parts:
        raise ValueError(f"expected an icon like fa-plus, got {argument!r}")
    if len(parts) > ICON_WORDS:
        raise ValueError(
            f"expected an icon of {ICON_WORDS} words at most, got {argument!r}"
        )
    if len(parts) == 1:
        rest = parts
    elif parts[0] in STYLES or parts[0] in FAMILIES:
        rest = parts[1:]
        style = STYLE_NAMES.get(parts[0], "brands")
        if style != "brands" and style not in FAMILY_STYLES["classic"]:
            owner = next(_ for _, s in FAMILY_STYLES.items() if style in s)
            raise ValueError(
                f"expected a family with {parts[0]} before it, as"
                f" fa-{owner}, got {argument!r}"
            )
        if parts[0] in FAMILIES and rest and rest[0] in STYLES:
            family, fixed = FAMILY_NAMES[parts[0]]
            allowed = [fixed] if fixed else [*FAMILY_STYLES[family]]
            if STYLE_NAMES[rest[0]] not in allowed:
                raise ValueError(
                    f"expected {parts[0]} with"
                    f" {' or '.join(f'fa-{_}' for _ in allowed)}, got"
                    f" {rest[0]!r}"
                )
            rest = rest[1:]
        if not rest or not rest[0].startswith("fa-"):
            raise ValueError(
                f"expected a name like fa-plus after the style, got "
                f"{argument!r}"
            )
    else:
        raise ValueError(
            "expected a style or a family, as fa-solid or fa-jelly, before"
            f" the name, got {argument!r}"
        )
    if (
        not ICON_NAME.fullmatch(rest[0])
        or rest[0] in STYLES | FAMILIES
        or MODIFIERS.fullmatch(rest[0])
    ):
        raise ValueError(
            f"expected an icon name like fa-plus, got {rest[0]!r}"
        )
    for each in rest[1:]:
        if not MODIFIERS.fullmatch(each):
            raise ValueError(
                f"expected a Font Awesome size or animation, got {each!r}"
            )
    return " ".join(parts)


def link(
    argument: str | None,
    *,
    schemes: Collection[str] = ("http", "https", "mailto"),
) -> str:
    """Read a full address, a path on the site, or a fragment.

    :param argument: The address as written.
    :param schemes: The schemes that it can start with. A path and a
        `#` fragment are always correct.
    :return: The address, as written.
    :raises ValueError: For whitespace, a backslash (a browser reads it
        as a slash, which can change a path into `//host`), a scheme
        that is not in `schemes`, a full address without a host, an
        address that starts with `//`, or one longer than `URL_LENGTH`.
    """
    value = (argument or "").strip()
    if not value:
        raise ValueError("expected an address, got none")
    if "\\" in value:
        raise ValueError(
            f"expected an address without a backslash, got {argument!r}"
        )
    if value.startswith("//"):
        raise ValueError(
            f"expected an address with its scheme, https://, got {argument!r}"
        )
    if len(value) > URL_LENGTH:
        raise ValueError(
            f"expected an address of {URL_LENGTH} characters at most, got "
            f"{len(value)}"
        )
    if re.search(r"\s", value):
        raise ValueError(
            f"expected an address with no spaces, got {argument!r}"
        )
    parts = urlsplit(value)
    if parts.scheme:
        if parts.scheme not in schemes:
            starts = ", ".join(f"{_}:" for _ in schemes)
            raise ValueError(
                f"expected an address starting {starts} or a path,"
                f" got {argument!r}"
            )
        if parts.scheme != "mailto" and not parts.hostname:
            raise ValueError(
                f"expected an address with a host, got {argument!r}"
            )
        if parts.scheme == "mailto" and not EMAIL.fullmatch(parts.path):
            raise ValueError(
                f"expected mailto: and an email address, got {argument!r}"
            )
    return value


def web(argument: str | None) -> str:
    """Read an `http` or `https` address.

    :param argument: The address as written.
    :return: The address.
    :raises ValueError: For other text.
    """
    value = link(argument, schemes=("http", "https"))
    if not urlsplit(value).scheme:
        raise ValueError(
            f"expected an http or https address, got {argument!r}"
        )
    return value


def kit(argument: str | None) -> str:
    """Read the address of a Font Awesome kit.

    :param argument: The address as written, as
        `https://kit.fontawesome.com/` and the name of the kit, with
        `.js` at the end.
    :return: The address.
    :raises ValueError: For other text.
    """
    value = web(argument)
    found = urlsplit(value)
    if (
        found.scheme != "https"
        or found.netloc != "kit.fontawesome.com"
        or found.query
        or found.fragment
        or not re.fullmatch(r"/[A-Za-z0-9]+\.js", found.path)
    ):
        raise ValueError(
            "expected a kit address like https://kit.fontawesome.com/"
            f"abc123.js, got {argument!r}"
        )
    return value


def site(argument: str | None) -> str:
    """Read the address of a site.

    :param argument: The address as written, as `http` or `https` with
        a host, and without a query, a fragment or a login.
    :return: The address.
    :raises ValueError: For other text.
    """
    value = web(argument)
    found = urlsplit(value)
    if (
        not found.hostname
        or found.query
        or found.fragment
        or found.username
        or found.password
    ):
        raise ValueError(
            "expected an address with a host and a path only, like"
            f" https://example.com/docs/, got {argument!r}"
        )
    return value


def picture(argument: str | None) -> str:
    """Read the address of a picture.

    :param argument: The address as written, as `http` or `https` or a
        path on the site, with the extension of an image.
    :return: The address, as written.
    :raises ValueError: For what `link` refuses, a scheme that is not
        `http` or `https`, or an address that is not a picture.
    """
    value = link(argument, schemes=("http", "https"))
    if not IMAGES.fullmatch(urlsplit(value).path):
        raise ValueError(
            "expected a .jpg, .jpeg, .png, .webp, .avif, .gif or .svg picture,"
            f" got {argument!r}"
        )
    return value


def colour(argument: str | None, names: Collection[str] = ()) -> str:
    """Read a colour.

    :param argument: The colour as written: one of `names`, `#abc`,
        `#aabbcc`, or the three numbers of `hsl`, as `262 83% 58%`.
    :param names: The known colour names.
    :return: The colour, as written.
    :raises ValueError: For other text, or `hsl` numbers that are not a
        hue to 360 and two percentages to 100.
    """
    value = " ".join((argument or "").split())
    if value in names or HEX.fullmatch(value):
        return value
    found = HSL.fullmatch(value)
    if (
        found
        and float(found[1]) <= 360
        and float(found[2]) <= 100
        and float(found[3]) <= 100
    ):
        return value
    known = "".join(f"{_}, " for _ in sorted(names))
    raise ValueError(
        f"expected {known}a hex colour like #7c3aed or hsl numbers like"
        f" 262 83% 58%, got {argument!r}"
    )


def language(argument: str | None) -> str:
    """Read a language code that Babel knows, as `en`, `hi` or `pt-BR`.

    :param argument: The code as written, with a `-` or an `_` between
        the language and its region.
    :return: The code, as written.
    :raises ValueError: For text that is not a language code, or a code
        that Babel does not have.
    """
    code = (argument or "").strip()
    try:
        Locale.parse(code, sep="-" if "-" in code else "_")
    except (ValueError, UnknownLocaleError) as error:
        raise ValueError(
            f"expected a language code like en, hi or pt-BR, got {argument!r}"
        ) from error
    return code


def host(argument: str | None) -> str:
    """Read a host name, as `example.com`.

    :param argument: The host as written. A host is only itself,
        without wildcards, so a site lists each subdomain.
    :return: The host, in lower case.
    :raises ValueError: For other text, also `*.example.com`.
    """
    value = (argument or "").strip().lower()
    if not HOST.fullmatch(value) or len(value) > HOST_LENGTH:
        raise ValueError(
            f"expected a host name like example.com, got {argument!r}"
        )
    return value


def location(node: nodes.Element) -> str:
    """Say where a node is in the source.

    :param node: The node.
    :return: `source:line`, or the part of it that is known.
    """
    source = node.get("source") or node.source or ""
    line = node.get("line") or node.line
    return f"{source}:{line}" if line else str(source)


def restate(why: str) -> str:
    """Write an error from docutils in the words of Kaamiki.

    :param why: What docutils said, on one line.
    :return: The same as `expected X, got Y`, or the words of docutils
        with a lower-case start, when Kaamiki does not know the error.
    """
    for pattern, form in COUNTS:
        if found := pattern.fullmatch(why):
            noun = "argument" if found[1] == "1" else "arguments"
            return form.format(*found.groups(), noun=noun)
    return why[:1].lower() + why[1:]


def pythonic(message: str) -> str:
    """Write a message from docutils as one line, as Python does.

    :param message: The message, which docutils writes as a block of
        prose.
    :return: The message as one line, `name: what`, with the value as
        its `repr`.
    """
    flat = " ".join(message.split())
    if found := DIRECTIVE_OPTION.fullmatch(message.strip()):
        why = " ".join(found["why"].split()).rstrip(".")
        head = f"{found['name']}: :{found['option']}:"
        if "no argument is allowed" in why:
            return f"{head} expected no value, got {found['value'].strip()}"
        if "argument required" in why:
            return f"{head} expected a value, got none"
        return f"{head} {why}"
    if found := UNKNOWN.search(message):
        return (
            f"{found['name']}: expected an option it takes,"
            f" got :{found['option']}:"
        )
    if found := ARGUMENTS.fullmatch(message.strip()):
        why = " ".join(found["why"].split()).rstrip(".")
        return f"{found['name']}: {restate(why)}"
    return flat[:1].lower() + flat[1:] if flat else flat


class Plain(Transform):
    """Keep the text of each error before the smart quotes."""

    default_priority = 700

    def apply(self, **kwargs: t.Any) -> None:
        """Record the text of each error on the page.

        :param kwargs: What docutils gives its transforms. This runs
            before the smart quotes of Sphinx, which change `--` to an
            en dash and `...` to an ellipsis. Then the value that
            Kaamiki quotes is the same as the text in the file.
        """
        del kwargs
        for message in self.document.findall(nodes.system_message):
            if message["level"] >= ERROR_LEVEL and message.children:
                message["km-plain"] = message.children[0].astext()


class Promoted(logging.Filter):
    """Stop the error from `promote` printing two times."""

    def __init__(self) -> None:
        """Start with the build in progress."""
        super().__init__()
        self.stopped = False

    def filter(self, record: logging.LogRecord) -> bool:
        """Remove an error after `promote` stops the build.

        :param record: The log record.
        :return: `False` for an error from docutils after that, and
            `True` for other records.
        """
        return not (
            self.stopped
            and getattr(record, "type", "") == "docutils"
            and record.levelno >= logging.ERROR
        )


@on("builder-inited")
def hush(app: Sphinx) -> None:
    """Stop Sphinx printing the errors that `promote` reports.

    :param app: The Sphinx application instance.
    """
    del app
    PROMOTED.stopped = False
    for handler in logging.getLogger("sphinx").handlers:
        handler.addFilter(PROMOTED)


PROMOTED: t.Final[Promoted] = Promoted()


@on("doctree-read", priority=100)
def promote(app: Sphinx, doctree: nodes.document) -> None:
    """Stop the build for an error that docutils reports.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read. docutils writes a mistake in a
        directive, a role or the markup as a message in the page and
        continues. Kaamiki stops at the first one, from each directive
        or extension, with or without `-W`.
    :raises KaamikiError: For the first error on the page.
    """
    del app
    for message in doctree.findall(nodes.system_message):
        if message["level"] >= ERROR_LEVEL:
            PROMOTED.stopped = True
            first = message.get("km-plain") or (
                message.children[0].astext() if message.children else ""
            )
            fail(pythonic(first), location(message))


def locate(message: str) -> tuple[str, str, str] | None:
    """Split a message into the file, the line and the error.

    :param message: What `fail` got, with its `where` first, as
        `file:line: what` or `file: what`. The file is the first part
        that is a file that exists, so a folder with a space or a drive
        letter does not cause a problem.
    :return: The file, the line (empty when there is none) and the
        error, or `None` when the message does not start with a file.
    """
    end = message.find(": ")
    while end != -1:
        file, _, line = message[:end].rpartition(":")
        if not (file and DIGITS.fullmatch(line)):
            file, line = message[:end], ""
        if p.isfile(file):
            return file, line, message[end + 2 :]
        end = message.find(": ", end + 2)
    return None


def report(
    exception: BaseException,
    /,
    *,
    stderr: t.TextIO = sys.stderr,
    print_traceback: bool = False,
    **rest: object,
) -> None:
    """Print a Kaamiki error as Python prints a `SyntaxError`.

    :param exception: What stopped the build. A `KaamikiError` is about
        a value from the site, so it prints alone: the file and the
        line, the line itself and the error. Sphinx does not add its
        note that asks to report the problem to Sphinx.
    :param stderr: Where to write.
    :param print_traceback: Whether Sphinx must show the traceback, as
        with `-T`. Sphinx still ends the build with its own exit
        status.
    :param rest: The other values that Sphinx gives its handler, for
        the handler that this one replaces.
    """
    message = str(exception) if isinstance(exception, KaamikiError) else ""
    if isinstance(exception, SphinxParallelError):
        last = exception.traceback.rstrip().splitlines()[-1:]
        found = re.search(r"KaamikiError: (.*)", last[0]) if last else None
        message = found[1] if found else ""
    if not message:
        original(
            exception, stderr=stderr, print_traceback=print_traceback, **rest
        )
        return
    lines: list[str] = []
    if place := locate(message):
        file, line, message = place
        lines.append(
            f'  File "{p.relpath(file)}"' + (f", line {line}" if line else "")
        )
        if line:
            try:
                with open(file, encoding="utf-8") as fd:
                    source = fd.read().splitlines()[int(line) - 1]
            except OSError, IndexError:
                source = ""
            if source.strip():
                shown = source.strip()
                lines.append(f"    {shown}")
                lines.append(f"    {'^' * len(shown)}")
    print(*lines, f"kaamiki.KaamikiError: {message}", sep="\n", file=stderr)
    if print_traceback:
        if isinstance(exception, SphinxParallelError):
            print(exception.traceback, file=stderr)
        else:
            traceback.print_exception(exception, file=stderr)


def install_reporter() -> None:
    """Put `report` before the Sphinx handler for uncaught errors."""
    global original
    try:
        from sphinx._cli.util import errors

        if errors.handle_exception is not report:
            original = errors.handle_exception
            errors.handle_exception = report  # type: ignore[assignment]
    except ImportError, AttributeError:
        return


original: t.Any = None
