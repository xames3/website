"""\
Input Checks
============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 23 October 2026
Last updated on: 25 October 2026

Kaamiki takes what it's given or stops the build. Nothing is clamped,
guessed or quietly dropped. Every option, role, page field and setting
is read by one of the checks here and a wrong one raises
`KaamikiError`.
"""

import os.path as p
import re
import sys
import typing as t
from urllib.parse import urlsplit

from docutils import nodes
from sphinx.errors import SphinxError
from sphinx.errors import SphinxParallelError

if t.TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Collection
    from collections.abc import Iterable
    from collections.abc import Sequence

    from sphinx.application import Sphinx

TEXT_LENGTH: t.Final[int] = 300
URL_LENGTH: t.Final[int] = 2048
SLUG: t.Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}")
CLASS: t.Final[re.Pattern[str]] = re.compile(r"[A-Za-z_][A-Za-z0-9_-]{0,63}")
WHOLE: t.Final[re.Pattern[str]] = re.compile(r"0|[1-9][0-9]{0,14}")
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
# NOTE(xames3): Font Awesome 7 Pro draws a style in a family of its own,
# `fa-sharp fa-solid fa-plus` or `fa-duotone fa-plus`.
FAMILIES: t.Final[frozenset[str]] = frozenset(
    {"fa-duotone", "fa-sharp", "fa-sharp-duotone", "fad", "fass", "fasds"}
)
# NOTE(xames3): The sizes, animations and turns Font Awesome documents,
# plus the colour classes Kaamiki's own stylesheet knows.
MODIFIERS: t.Final[re.Pattern[str]] = re.compile(
    r"fa-(?:fw|spin|pulse|beat|fade|beat-fade|bounce|shake|spin-pulse"
    r"|spin-reverse|flip-horizontal|flip-vertical|flip-both"
    r"|rotate-(?:90|180|270)|2xs|xs|sm|lg|xl|2xl|[1-9]x|10x)"
    r"|km-(?:red|yellow|blue|green|margin-inline)"
)
ICON_NAME: t.Final[re.Pattern[str]] = re.compile(
    r"(?:fa-)?[a-z0-9]+(?:-[a-z0-9]+)*"
)
HOST: t.Final[re.Pattern[str]] = re.compile(
    r"(?:\*\.)?(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)"
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
LOCALE: t.Final[re.Pattern[str]] = re.compile(
    r"[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*"
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
    :raises ValueError: When it's blank, has control characters or is
        longer than `maximum`.
    """
    value = (argument or "").strip()
    if not value:
        raise ValueError("expected some text, it is empty")
    if len(value) > maximum:
        raise ValueError(f"expected at most {maximum} characters")
    if any(ord(_) < 32 and _ != "\n" for _ in value):
        raise ValueError("expected text without control characters")
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


def classes(argument: str | None) -> list[str]:
    """Read class names, each one a letter or `_` and then letters,
    digits, `-` and `_`.

    :param argument: The names as written.
    :return: The names, in the order written.
    :raises ValueError: For a name docutils would have rewritten.
    """
    found = (argument or "").split()
    if not found or len(found) > 8:
        raise ValueError("expected one to eight class names")
    for each in found:
        if not CLASS.fullmatch(each):
            raise ValueError(
                f"expected class names of letters, digits, - and _, got "
                f"{each!r}"
            )
    return found


def pattern(expression: str, hint: str) -> Callable[[str | None], str]:
    """Make a check for text written a certain way.

    :param expression: What the text has to match, all of it.
    :param hint: How to say what's expected, for the message.
    :return: The check.
    """
    regex = re.compile(expression)

    def read(argument: str | None) -> str:
        value = (argument or "").strip()
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
        value = (argument or "").strip()
        if not WHOLE.fullmatch(value):
            raise ValueError(f"expected a whole number, got {argument!r}")
        number = int(value)
        if not low <= number <= high:
            raise ValueError(f"expected {low} to {high}, got {number}")
        return number

    return read


def number(low: float, high: float) -> Callable[[str | None], float]:
    """Make a check for a number, decimals allowed, in a range.

    :param low: The least it may be.
    :param high: The most it may be.
    :return: The check.
    """

    def read(argument: str | None) -> float:
        value = (argument or "").strip()
        if not DECIMAL.fullmatch(value):
            raise ValueError(f"expected a number, got {argument!r}")
        amount = float(value)
        if not low <= amount <= high:
            raise ValueError(f"expected {low:g} to {high:g}, got {amount:g}")
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
            f"expected {', '.join(presets)}, or one or two lengths from 0 to"
            f" {high:g}rem like 1.5rem or 1rem 2rem, got {argument!r}"
        )

    return read


def icon(argument: str | None) -> str:
    """Read a Font Awesome icon the way an option or a role writes it.

    It is `plus`, `fa-plus` or a style and a name, `far fa-plus`, with a
    family ahead of the style for Pro, `fa-sharp fa-solid fa-plus`. Font
    Awesome's own sizes and animations may follow.

    :param argument: The icon as written.
    :return: The icon, as written.
    :raises ValueError: When it isn't written like one. Whether the
        name is one Font Awesome has can't be known here.
    """
    parts = (argument or "").split()
    if not parts or len(parts) > 6:
        raise ValueError(f"expected an icon like fa-plus, got {argument!r}")
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
    :raises ValueError: For whitespace, a scheme that isn't in
        `schemes`, a full address with no host, one that starts with `//`
        or one too long.
    """
    value = (argument or "").strip()
    if not value:
        raise ValueError("expected an address, it is empty")
    if value.startswith("//"):
        raise ValueError(
            f"expected an address with its scheme, https://, got {argument!r}"
        )
    if len(value) > URL_LENGTH or re.search(r"\s", value):
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


def host(argument: str) -> str:
    """Read a host name, as `example.com` or `*.example.com`.

    :param argument: The host as written.
    :return: The host, in lowercase.
    :raises ValueError: For anything else.
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


OPTION: t.Final[re.Pattern[str]] = re.compile(
    r'Error in "(?P<name>[\w-]+)" directive:\s*invalid option value: '
    r'\(option: "(?P<option>[\w-]+)"; value: (?P<value>.*?)\)\s*(?P<why>.*)',
    re.DOTALL,
)
UNKNOWN: t.Final[re.Pattern[str]] = re.compile(
    r'Error in "(?P<name>[\w-]+)" directive:\s*'
    r'unknown option: "(?P<option>[^"]+)"'
)
ARGUMENTS: t.Final[re.Pattern[str]] = re.compile(
    r'Error in "(?P<name>[\w-]+)" directive:\s*(?P<why>.*)', re.DOTALL
)


def pythonic(text: str) -> str:
    """Say what docutils reported the way Python would.

    docutils words an error as a block of prose. This gives the same
    error as one line, `name: what`, with the value `repr`'d.

    :param text: The message docutils gave.
    :return: The message as one line.
    """
    flat = " ".join(text.split())
    if found := OPTION.fullmatch(text.strip()):
        why = " ".join(found["why"].split()).rstrip(".")
        head = f"{found['name']}: option {found['option']!r}"
        if "no argument is allowed" in why:
            return f"{head} takes no value, got {found['value'].strip()}"
        if "argument required" in why:
            return f"{head} needs a value"
        return f"{head}: {why}"
    if found := UNKNOWN.search(text):
        return f"{found['name']}: unexpected option {found['option']!r}"
    if found := ARGUMENTS.fullmatch(text.strip()):
        why = " ".join(found["why"].split()).rstrip(".")
        return f"{found['name']}: {why[:1].lower() + why[1:]}"
    return flat[:1].lower() + flat[1:] if flat else flat


def promote(app: Sphinx, doctree: nodes.document) -> None:
    """Make an error docutils reported while reading a page stop the
    build.

    docutils writes a mistake in a directive, a role or the markup as
    a message in the page and carries on. Kaamiki stops at the first.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read.
    :raises KaamikiError: For the first error on the page.
    """
    del app
    for message in doctree.findall(nodes.system_message):
        if message["level"] >= 3:
            first = message.children[0].astext() if message.children else ""
            fail(pythonic(first), location(message))


WHERE: t.Final[re.Pattern[str]] = re.compile(
    r"(?P<file>[^\s:]*[/.][^\s:]*?)(?::(?P<line>\d+))?: (?P<what>.*)",
    re.DOTALL,
)


def report(
    exception: BaseException,
    /,
    *,
    stderr: t.TextIO = sys.stderr,
    print_traceback: bool = False,
    **rest: t.Any,
) -> None:
    """Print a Kaamiki error the way Python prints a `SyntaxError`.

    Sphinx ends every uncaught exception with a note asking for it to
    be reported to Sphinx. A `KaamikiError` is about what a site gave
    Kaamiki, so it's printed on its own: the file and line, the line
    itself and the error.

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
    if found := WHERE.fullmatch(message):
        message = found["what"]
        path = p.relpath(found["file"])
        place = f'  File "{path}"'
        if found["line"]:
            place += f", line {found['line']}"
            try:
                with open(found["file"], encoding="utf-8") as fd:
                    source = fd.read().splitlines()[int(found["line"]) - 1]
            except OSError, IndexError:
                source = ""
            lines.append(place)
            if source.strip():
                shown = source.strip()
                lines.append(f"    {shown}")
                lines.append(f"    {'^' * len(shown)}")
        else:
            lines.append(place)
    print(*lines, f"kaamiki.KaamikiError: {message}", sep="\n", file=stderr)
    if print_traceback:
        raise exception


def install() -> None:
    """Put `report` in front of Sphinx's handler for uncaught errors."""
    global original
    from sphinx._cli.util import errors

    if errors.handle_exception is not report:
        original = errors.handle_exception
        errors.handle_exception = report  # type: ignore[assignment]


def sound(
    parts: Iterable[str], allowed: Collection[str], where: str
) -> list[str]:
    """Check every word of a list is one that's allowed.

    :param parts: The words as written.
    :param allowed: The words that are allowed.
    :param where: What is being checked, for the message.
    :return: The words.
    :raises KaamikiError: For a word that isn't allowed.
    """
    found = list(parts)
    for each in found:
        if each not in allowed:
            fail(
                f"{where} expected one of "
                f"{', '.join(map(repr, sorted(allowed)))}, got {each!r}"
            )
    return found


original: t.Any = None
