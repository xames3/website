"""\
Date Utilities
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 15 November 2026

The helpers that give a page its dates, from its comments or from git.
"""

from __future__ import annotations

import re
import typing as t
import weakref
from datetime import date
from datetime import datetime as dt
from datetime import timedelta
from pathlib import PurePath
from subprocess import DEVNULL
from subprocess import CalledProcessError
from subprocess import check_output as co

from sphinx.locale import _
from sphinx.util.i18n import format_date

from kaamiki.extensions.utils.checks import fail
from kaamiki.extensions.utils.hooks import on
from kaamiki.extensions.utils.settings import values

if t.TYPE_CHECKING:
    from docutils import nodes
    from sphinx.application import Sphinx
    from sphinx.config import Config
    from sphinx.environment import BuildEnvironment

HEADER_RE: t.Final[re.Pattern[str]] = re.compile(
    r"^\.\.\s+(Author|Created on|Last updated on):\s*(.+)$", re.IGNORECASE
)
MONTHS: t.Final[tuple[str, ...]] = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
NUMBERS: t.Final[dict[str, int]] = {
    name.lower(): number for number, name in enumerate(MONTHS, 1)
}
WRITTEN: t.Final[re.Pattern[str]] = re.compile(
    r"([0-9]{1,2})\s+([A-Za-z]+)\s+([0-9]{4})"
)
ISO: t.Final[re.Pattern[str]] = re.compile(
    r"([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})"
)
HISTORY: t.Final[
    weakref.WeakKeyDictionary[Sphinx, dict[str, tuple[dt, dt]]]
] = weakref.WeakKeyDictionary()


@on("html-page-context")
def updated_on(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Write the last update of a page in its language.

    :param app: The Sphinx application instance.
    :param pagename: The page that is written.
    :param templatename: The template that writes it.
    :param context: The context of the page, changed in place.
    :param doctree: The resolved doctree, or `None` for a generated
        page.
    """
    del pagename, templatename, doctree
    meta: dict[str, str] = context.get("meta") or {}
    shown = meta.get("last_updated", "")
    iso = day(shown)
    if iso:
        shown = dated(dt.fromisoformat(iso), app.config)
    context["km_updated_on"] = shown


def header(source: str) -> dict[str, str]:
    """Read the comments at the top of a page.

    :param source: The source of the page. It starts with `.. Author:`,
        `.. Created on:` and `.. Last updated on:` comments. Only
        comments before the first other line count, so a date lower in
        the page is not taken.
    :return: What they say, as `author`, `created on` and `last updated
        on`, for the comments that the page has.
    """
    found: dict[str, str] = {}
    for line in source.splitlines():
        if line.strip() and not line.startswith(".."):
            break
        match = HEADER_RE.match(line.strip())
        if match:
            found.setdefault(match.group(1).lower(), match.group(2).strip())
    if "author" in found:
        found["author"] = found["author"].split("<")[0].strip()
    return found


def read_history(srcdir: str) -> dict[str, tuple[dt, dt]]:
    """Ask git for the first and last commit of each file.

    :param srcdir: The folder of the sources, in the repository.
    :return: The path of each file from `srcdir`, with the dates of its
        first and its latest commit, or empty outside a repository or
        without git. One `git log` walks the history from the newest
        commit, and a renamed file keeps its history.
    """
    cmd = [
        "git",
        "-c",
        "core.quotepath=false",
        "log",
        "--format=%x01%cI",
        "--name-status",
        "-M",
        "--relative",
        "-z",
        "--",
        ".",
    ]
    try:
        raw = co(cmd, cwd=srcdir, stderr=DEVNULL)  # noqa: S603
    except CalledProcessError, OSError:
        return {}
    out = raw.decode("utf-8", "replace")
    named: dict[str, str | None] = {}
    found: dict[str, tuple[dt, dt]] = {}
    for commit in out.split("\x01")[1:]:
        stamp, _gap, rest = commit.partition("\0")
        when = dt.fromisoformat(stamp)
        entries = iter(filter(None, rest.lstrip("\n").split("\0")))
        for status in entries:
            old = next(entries)
            new = next(entries) if status.startswith("R") else old
            if status.startswith("D"):
                continue
            now = named.get(new, new)
            if now is not None:
                found[now] = (when, found[now][1] if now in found else when)
            if old != new:
                named[old] = now
            if status.startswith(("A", "R")):
                named[new] = None
    return found


def committed(app: Sphinx, docname: str) -> tuple[dt, dt] | tuple[None, None]:
    """Look up when git first saw a page and when it last changed it.

    :param app: The Sphinx application instance.
    :param docname: The document to ask about.
    :return: The dates of the commit that brought the page in and of
        the latest one, or `None` twice outside a repository and for a
        page git has never seen.
    """
    if app not in HISTORY:
        HISTORY[app] = read_history(str(app.srcdir))
    path = PurePath(str(app.env.doc2path(docname, base=False))).as_posix()
    return HISTORY[app].get(path, (None, None))


@on("env-before-read-docs")
def warm(app: Sphinx, env: BuildEnvironment, docnames: list[str]) -> None:
    """Ask git before the pages are read.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param docnames: The pages that are read.
    """
    del env
    if docnames and app not in HISTORY:
        HISTORY[app] = read_history(str(app.srcdir))


def written(when: dt | None) -> str:
    """Write a date as the header comments write it.

    :param when: The date, or `None` for the day of the build.
    :return: The date, as `04 May 2026`. The month is always in
        English, in each language of the machine, because `day` reads
        it again.
    """
    when = when or dt.now().astimezone()
    return f"{when:%d} {MONTHS[when.month - 1]} {when.year}"


def dated(when: dt, config: Config) -> str:
    """Write a date for a reader, in the language of the site.

    :param when: The date.
    :param config: The Sphinx configuration.
    :return: The date in the `language` of the site, or in English when
        it is not set. Each date follows `html_last_updated_fmt` when
        set, then `kaamiki.conf.site.last_updated_fmt`, else it is `04
        May 2026`. `written` keeps the form of the header comments,
        because Kaamiki reads that again.
    """
    form = (
        config.html_last_updated_fmt
        or values(config).site.last_updated_fmt
        or str(_("%d %B %Y"))
    )
    return format_date(form, date=when, language=config.language or "en")


def day(text: str) -> str:
    """Change a date from the header comments into ISO.

    :param text: The date, as `29 September 2026` or `2026-09-29`. The
        month is read by its English name, in each language of the
        machine.
    :return: `2026-09-29`, or an empty string when it is not a date.
    """
    if found := WRITTEN.fullmatch(text):
        month = NUMBERS.get(found[2].lower(), 0)
        parts = (int(found[3]), month, int(found[1]))
    elif found := ISO.fullmatch(text):
        parts = (int(found[1]), int(found[2]), int(found[3]))
    else:
        return ""
    try:
        return date(*parts).isoformat()
    except ValueError:
        return ""


def within(iso: str) -> bool:
    """Say whether a day is from 2000 to one year later.

    :param iso: The day, as `2026-09-29`.
    :return: `True` when a page or a release can have it.
    """
    return (
        date(2000, 1, 1)
        <= date.fromisoformat(iso)
        <= date.today() + timedelta(days=366)  # noqa: DTZ011
    )


@on("source-read")
def provenance(app: Sphinx, docname: str, source: list[str]) -> None:
    """Find who wrote a page, and when.

    :param app: The Sphinx application instance.
    :param docname: The document that is read.
    :param source: The source of the document, from docutils. The `..
        Author:`, `.. Created on:` and `.. Last updated on:` comments
        come first. A missing date comes from git (the first or the
        latest commit, read one time for the build), then the day of
        the build. A missing author comes from the `byline` directive,
        then the project.
    :raises KaamikiError: For a date comment that is not a date from
        2000 to one year later, or a page updated before it was
        created.
    """
    metadata = app.env.metadata.setdefault(docname, {})
    found = header(source[0] if source else "")
    where = str(app.env.doc2path(docname))
    if found.get("author"):
        metadata.setdefault("author", found["author"])
    for key in ("created on", "last updated on"):
        if key in found:
            iso = day(found[key])
            if not iso or not within(iso):
                fail(
                    f"comment {key.capitalize()!r}: expected a date like 5"
                    " October 2026 or 2026-10-05, from 2000 to a year ahead,"
                    f" got {found[key]!r}",
                    where,
                )
    if (
        "created on" in found
        and "last updated on" in found
        and (day(found["last updated on"]) < day(found["created on"]))
    ):
        fail(
            "comment 'Last updated on': expected after 'Created on', got it"
            " before",
            where,
        )
    first, last = committed(app, docname)
    if not metadata.get("created"):
        metadata["created"] = found.get("created on") or written(first)
    if not metadata.get("last_updated"):
        metadata["last_updated"] = found.get("last updated on") or written(last)
