"""\
Input Checks
============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 23 October 2026
Last updated on: 07 November 2026

Kaamiki takes what it's given or stops the build. Nothing is clamped,
guessed or quietly dropped. Every option, role, page field and setting
is read by one of the checks here and a wrong one raises
`KaamikiError`.
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
from sphinx.errors import SphinxError
from sphinx.errors import SphinxParallelError

if t.TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Collection
    from collections.abc import Sequence

    from sphinx.application import Sphinx

TEXT_LENGTH: t.Final[int] = 300
URL_LENGTH: t.Final[int] = 2048
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
STYLES: t.Final[frozenset[str]] = frozenset(
    {
        "fa-solid",
        "fa-regular",
        "fa-light",
        "fa-thin",
        "fa-brands",
        "fas",
        "far",
        "fal",
        "fat",
        "fab",
    }
)
FAMILIES: t.Final[frozenset[str]] = frozenset(
    {"fa-duotone", "fa-sharp", "fa-sharp-duotone", "fad", "fass", "fasds"}
)
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
    """What a site gave Kaamiki is wrong, so the build stops.

    The message is `where: what`, the way `report` reads it back when
    the error comes from a parallel reader as text.
    """

    category = "KaamikiError"
    __module__ = "kaamiki"


def fail(message: str, where: str = "") -> t.NoReturn:
    """Stop the build.

    :param message: What's wrong and what's accepted.
    :param where: `source:line` the mistake is at, if there's one.
    :raises KaamikiError: Always.
    """
    raise KaamikiError(f"{where}: {message}" if where else message)


def text(argument: str | None, maximum: int = TEXT_LENGTH) -> str:
    """Read a line of text that must say something.

    :param argument: The value as written.
    :param maximum: The most characters it may have.
    :return: The text with the spaces around it trimmed.
    :raises ValueError: When it's blank, has control characters (a
        `newline` is fine, for an option written over several lines) or
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
    """Read a name made of letters, digits, `-` and `_`.

    :param argument: The value as written.
    :return: The name.
    :raises ValueError: For anything else.
    """
    value = (argument or "").strip()
    if not SLUG.fullmatch(value):
        raise ValueError(
            "expected a name of letters, digits, - and _ up to 64 long,"
            f" got {argument!r}"
        )
    return value


def reference_name(argument: str | None) -> str:
    """Read a `:name:` the way docutils does and check it is a name.

    Any text is a name, as with docutils' own directives: spaces and
    capitals are fine and docutils makes the id (`My Note` is the id
    `my-note`). The checks are for what docutils would let through
    that no link could use. A name in any script will do, and docutils
    makes an id of its own (`id1`) for one it can't spell in ASCII.

    :param argument: The value as written.
    :return: The name, its spaces collapsed to one each.
    :raises ValueError: For none, one that is empty, has a control
        character, has no letter in it or is longer than `NAME_LENGTH`.
    :raises TypeError: For a value that isn't text.
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
    """Read class names the way docutils does and check each is one.

    Names are split on spaces and made into ids as docutils' own
    `:class:` option does, so `Foo_Bar` is `foo-bar`. A comma followed
    by a space does no harm, but one with no space after it joins two
    names into one class: `big,red` is `big-red`. Kaamiki's checks are
    on top: a name has to make an id, none may be more than
    `NAME_LENGTH` long and there are `CLASS_COUNT` at most.

    :param argument: The names as written.
    :return: The names, in the order written and each once.
    :raises ValueError: For none, a name that can't be made into a
        class, one that is too long or too many.
    :raises TypeError: For a value that isn't text.
    """
    if argument is None or (isinstance(argument, str) and not argument.strip()):
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
    """Read a text encoding Python knows.

    :param argument: The name as written, like `utf-8`.
    :return: The name, trimmed.
    :raises ValueError: For none, an empty one or one Python doesn't
        have.
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
    """Make a check for text written a certain way.

    :param expression: What the text has to match, all of it.
    :param hint: How to say what's expected, for the message.
    :return: The check, which takes the text as it is, spaces and all.
    """
    regex = re.compile(expression)

    def read(argument: str | None) -> str:
        """Read the text, which has to match."""
        value = argument or ""
        if not regex.fullmatch(value):
            raise ValueError(f"expected {hint}, got {argument!r}")
        return value

    return read


def word(*choices: str) -> Callable[[str | None], str]:
    """Make a check for an option that takes one of a few words.

    :param choices: The words it takes, written as they must be.
    :return: The check.
    """

    def read(argument: str | None) -> str:
        """Read the word, which has to be one of the choices."""
        if argument not in choices:
            raise ValueError(
                f"expected one of {', '.join(map(repr, choices))}, got "
                f"{argument!r}"
            )
        return argument

    return read


def integer(low: int, high: int) -> Callable[[str | None], int]:
    """Make a check for a whole number in a range.

    :param low: The least it may be.
    :param high: The most it may be.
    :return: The check, which takes digits only: no sign, no `_`, no
        spaces, no other scripts and no leading zeros.
    """

    def read(argument: str | None) -> int:
        """Read the digits as a number in the range."""
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
    """Make a check for a number, decimals allowed, in a range.

    :param low: The least it may be.
    :param high: The most it may be.
    :return: The check, which takes digits and a point only.
    """

    def read(argument: str | None) -> float:
        """Read the number, in the range."""
        value = (argument or "").strip()
        if not DECIMAL.fullmatch(value):
            raise ValueError(f"expected a number, got {argument!r}")
        amount = float(value)
        if not low <= amount <= high:
            raise ValueError(f"expected {low:g} to {high:g}, got {argument!r}")
        return amount

    return read


def spacing(presets: Sequence[str], high: float) -> Callable[[str | None], str]:
    """Make a check for a space, a preset or one or two lengths in rem.

    :param presets: The words that stand for a space.
    :param high: The longest length, in rem.
    :return: The check, which hands back the preset or the lengths
        with a bare `0` given its unit, which `calc()` needs.
    """

    def read(argument: str | None) -> str:
        """Read the space, a preset or the lengths."""
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
    """Split a space `spacing` handed back into its first and last
    length.

    :param value: One or two lengths, as `spacing` returns them.
    :return: The first and the last, the same one for a single length.
        What a vertical and a horizontal gap are made of, or an edge
        above and one below.
    """
    words = value.split()
    return words[0], words[-1]


def icon(argument: str | None) -> str:
    """Read a Font Awesome icon the way an option or a role writes it.

    It is `plus`, `fa-plus` or a style and a name, `far fa-plus`, with
    a family ahead of the style for Pro, `fa-sharp fa-solid fa-plus`.
    Font Awesome's sizes and animations, like `fa-lg` and `fa-spin`
    and Kaamiki's `km-tone--red`, `km-tone--yellow`, `km-tone--blue`
    and `km-tone--green` may follow, but only after a style or a
    family: `far fa-plus fa-spin` is read and `fa-plus fa-spin` is not.
    An icon has `ICON_WORDS` words at most.

    :param argument: The icon as written.
    :return: The icon, as written.
    :raises ValueError: When it isn't written like one. Whether the
        name is one Font Awesome has can't be known here.
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
        if parts[0] in FAMILIES and rest and rest[0] in STYLES:
            rest = rest[1:]
        if not rest or not rest[0].startswith("fa-"):
            raise ValueError(
                f"expected a name like fa-plus after the style, got "
                f"{argument!r}"
            )
    else:
        raise ValueError(
            f"expected a style, {', '.join(sorted(STYLES | FAMILIES))}, before"
            f" the name, got {argument!r}"
        )
    if not ICON_NAME.fullmatch(rest[0]) or rest[0] in STYLES | FAMILIES:
        raise ValueError(f"expected an icon name like fa-plus, got {rest[0]!r}")
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
    """Read an address: a full one, a path on the site or a fragment.

    :param argument: The address as written.
    :param schemes: The schemes it may start with. A path and a `#`
        fragment are always fine.
    :return: The address, as written.
    :raises ValueError: For whitespace, a backslash (a browser reads it
        as a slash, which can turn a path into `//host`), a scheme that
        isn't in `schemes`, a full address with no host, one that
        starts with `//` or one longer than `URL_LENGTH`.
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
    :raises ValueError: For anything else.
    """
    value = link(argument, schemes=("http", "https"))
    if not urlsplit(value).scheme:
        raise ValueError(f"expected an http or https address, got {argument!r}")
    return value


def kit(argument: str | None) -> str:
    """Read the address of a Font Awesome kit,
    `https://kit.fontawesome.com/` and the kit's name, ending in `.js`.

    :param argument: The address as written.
    :return: The address.
    :raises ValueError: For anything else.
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
    """Read the address of a site, an `http` or `https` one with a host
    and no query, fragment or login.

    :param argument: The address as written.
    :return: The address.
    :raises ValueError: For anything else.
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
    """Read the address of a picture, an `http` or `https` one or a
    path on the site, ending in an image's extension.

    :param argument: The address as written.
    :return: The address, as written.
    :raises ValueError: For anything `link` refuses, a scheme that
        isn't `http` or `https` and an address that isn't a picture.
    """
    value = link(argument, schemes=("http", "https"))
    if not IMAGES.fullmatch(urlsplit(value).path):
        raise ValueError(
            f"expected a .jpg, .png, .webp, .avif, .gif or .svg picture, got "
            f"{argument!r}"
        )
    return value


def colour(argument: str | None, names: Collection[str] = ()) -> str:
    """Read a colour: one of the names given, `#abc`, `#aabbcc` or the
    three numbers of `hsl`, as `262 83% 58%`.

    :param argument: The colour as written.
    :param names: The colour names that are known.
    :return: The colour, as written.
    :raises ValueError: For anything else, or for hsl numbers that
        aren't a hue to 360 and two percentages to 100.
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
    raise ValueError(
        f"expected {', '.join(sorted(names)) + ', ' if names else ''}a "
        f"hex colour"
        f" like #7c3aed or hsl numbers like 262 83% 58%, got {argument!r}"
    )


def language(argument: str | None) -> str:
    """Read a language code Babel knows, like `en`, `hi` or `pt-BR`.

    :param argument: The code as written, with a `-` or an `_` between
        the language and its region.
    :return: The code, as written.
    :raises ValueError: For text that isn't a language code or one
        Babel doesn't have.
    """
    code = (argument or "").strip()
    try:
        Locale.parse(code, sep="-" if "-" in code else "_")
    except (ValueError, UnknownLocaleError) as error:
        raise ValueError(
            f"expected a language code like en, hi or pt-BR, got {argument!r}"
        ) from error
    return code


def host(argument: str) -> str:
    """Read a host name, as `example.com`.

    A host stands for itself. There are no wildcards, so a site lists
    each subdomain it means.

    :param argument: The host as written.
    :return: The host, in lowercase.
    :raises ValueError: For anything else, `*.example.com` included.
    """
    value = argument.strip().lower()
    if not HOST.fullmatch(value) or len(value) > 253:
        raise ValueError(
            f"expected a host name like example.com, got {argument!r}"
        )
    return value


def location(node: nodes.Element) -> str:
    """Say where in the source a node is.

    :param node: The node.
    :return: `source:line` or whatever of it is known.
    """
    source = node.get("source") or node.source or ""
    line = node.get("line") or node.line
    return f"{source}:{line}" if line else str(source)


def restate(why: str) -> str:
    """Put an error docutils worded as prose in Kaamiki's own words.

    :param why: What docutils said, on one line.
    :return: The same in the form `expected X, got Y`, or the words
        docutils used, lower-cased at the start, when it isn't one of
        the few Kaamiki knows.
    """
    for pattern, form in COUNTS:
        if found := pattern.fullmatch(why):
            noun = "argument" if found[1] == "1" else "arguments"
            return form.format(*found.groups(), noun=noun)
    return why[:1].lower() + why[1:]


def pythonic(message: str) -> str:
    """Say what docutils reported the way Python would.

    docutils words an error as a block of prose. This gives the same
    error as one line, `name: what`, with the value `repr`'d.

    :param message: The message docutils gave.
    :return: The message as one line.
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
    """Keep what each error says as it was written.

    Sphinx's smart quotes run on the text of an error too, turning `--`
    into an en dash and `...` into an ellipsis, so the value an author
    typed wouldn't be found in the file by the one Kaamiki quotes. This
    runs just ahead of them.
    """

    default_priority = 700

    def apply(self, **kwargs: t.Any) -> None:
        """Note the text of every error on the page.

        :param kwargs: What docutils hands its transforms.
        """
        del kwargs
        for message in self.document.findall(nodes.system_message):
            if message["level"] >= ERROR_LEVEL and message.children:
                message["km-plain"] = message.children[0].astext()


class Promoted(logging.Filter):
    """Keep the error `promote` stops the build on from being printed
    twice.

    docutils logs an error the moment it finds it and Sphinx prints it
    once the pages are read, by which time `promote` has stopped the
    build with the same error in one line. From then on the errors
    docutils logged aren't printed.
    """

    def __init__(self) -> None:
        """Start with the build going."""
        super().__init__()
        self.stopped = False

    def filter(self, record: logging.LogRecord) -> bool:
        """Drop an error from docutils once `promote` has stopped the
        build.

        :param record: The log record.
        :return: `False` for an error from docutils after that and
            `True` for anything else.
        """
        return not (
            self.stopped
            and getattr(record, "type", "") == "docutils"
            and record.levelno >= logging.ERROR
        )


def hush(app: Sphinx) -> None:
    """Stop Sphinx printing the errors `promote` reports.

    :param app: The Sphinx application instance.
    """
    del app
    PROMOTED.stopped = False
    for handler in logging.getLogger("sphinx").handlers:
        handler.addFilter(PROMOTED)


PROMOTED: t.Final[Promoted] = Promoted()
ERROR_LEVEL: t.Final[int] = 3


def promote(app: Sphinx, doctree: nodes.document) -> None:
    """Make an error docutils reported while reading a page stop the
    build.

    docutils writes a mistake in a directive, a role or the markup as
    a message in the page and carries on. Kaamiki stops at the first,
    whichever directive or extension it came from, with or
    without `-W`.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read.
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
    """Split a message into the file, the line and what's wrong.

    The message is `file:line: what` or `file: what`. The file is the
    start of it that is a file that exists, so a folder with a space in
    its name, or a drive letter, doesn't get in the way.

    :param message: What `fail` was given, with its `where` in front.
    :return: The file, the line (empty when there isn't one) and what's
        wrong, or `None` when the message doesn't start with a file.
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
    """Print a Kaamiki error the way Python prints a `SyntaxError`.

    Sphinx ends every uncaught exception with a note asking for it to
    be reported to Sphinx. A `KaamikiError` is about what a site gave
    Kaamiki, so it's printed on its own: the file and line, the line
    itself and the error. With `-T` the traceback follows, and Sphinx
    still ends the build with its own exit status.

    :param exception: What stopped the build.
    :param stderr: Where to write.
    :param print_traceback: Whether Sphinx was asked for the traceback.
    :param rest: What else Sphinx hands its handler, for the handler
        this one stands in front of.
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
    """Put `report` in front of Sphinx's handler for uncaught errors.

    Sphinx keeps that handler in a private module, so Kaamiki leaves
    Sphinx's own error output alone when a Sphinx has moved it. The
    swap holds for the whole process, and `report` hands every error
    that isn't Kaamiki's to the handler it replaced.
    """
    global original
    try:
        from sphinx._cli.util import errors

        if errors.handle_exception is not report:
            original = errors.handle_exception
            errors.handle_exception = report  # type: ignore[assignment]
    except ImportError, AttributeError:
        return


original: t.Any = None
