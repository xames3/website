"""\
Date Utilities
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 07 November 2026

The helpers that date a page, from its comments or from git.
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
from kaamiki.extensions.utils.settings import setting

if t.TYPE_CHECKING:
    from docutils import nodes
    from sphinx.application import Sphinx
    from sphinx.config import Config
    from sphinx.environment import BuildEnvironment

HEADER_RE: re.Pattern[str] = re.compile(
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
HISTORY: weakref.WeakKeyDictionary[Sphinx, dict[str, tuple[dt, dt]]] = (
    weakref.WeakKeyDictionary()
)


def updated_on(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Write the day a page was last updated in the site's language.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree or `None` for generated
        pages.
    """
    del pagename, templatename, doctree
    meta: dict[str, str] = context.get("meta") or {}
    shown = meta.get("last_updated", "")
    iso = day(shown)
    if iso:
        shown = dated(dt.fromisoformat(iso), app.config)
    context["km_updated_on"] = shown


def header(source: str) -> dict[str, str]:
    """Read the comments heading a page.

    Only comments before the first other line count, so a date quoted
    further down isn't taken for the page's own.

    .. note:: It's mostly for my edits and how I write my rST files.

    :param source: The page's source.
    :return: What they say, keyed `author`, `created on` and
        `last updated on`, for the ones the page has.
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
    """Ask git, once, when every file under a folder was first and last
    committed.

    One `git log` walks the history from the newest commit back, and a
    file that was renamed keeps the history it had under its old name.

    :param srcdir: The folder the sources are in, inside the repo.
    :return: Each file's path from `srcdir`, with the dates of the
        commit that brought it in and of the latest one. Empty outside
        a repository or without git.
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
        stamp, _, rest = commit.partition("\0")
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


def warm(app: Sphinx, env: BuildEnvironment, docnames: list[str]) -> None:
    """Ask git before the pages are read, so a parallel reader doesn't.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param docnames: The pages about to be read.
    """
    del env
    if docnames and app not in HISTORY:
        HISTORY[app] = read_history(str(app.srcdir))


def written(when: dt | None) -> str:
    """Write a date the way the header comments write it.

    The month is always the English name, whatever language the machine
    builds in, since `day` reads it back.

    :param when: The date or `None` for the day the site is built.
    :return: The date, as `04 May 2026`.
    """
    when = when or dt.now().astimezone()
    return f"{when:%d} {MONTHS[when.month - 1]} {when.year}"


def dated(when: dt, config: Config) -> str:
    """Write a date the way a reader wants it, in the site's language.

    Every date Kaamiki shows follows `html_last_updated_fmt` when the
    site sets it, then `kaamiki.conf.site.last_updated_fmt`. With
    neither it's `04 May 2026` in English. `written` keeps the one
    form the header comments use, since Kaamiki reads that back.

    :param when: The date.
    :param config: The Sphinx configuration.
    :return: The date, in the site's `language` (English when unset).
    """
    form = (
        config.html_last_updated_fmt
        or setting(config, "last_updated_on_fmt")
        or str(_("%d %B %Y"))
    )
    return format_date(form, date=when, language=config.language or "en")


def day(text: str) -> str:
    """Turn a date written like the header comments write it into ISO.

    The month is read by its English name, whatever language the
    machine builds in. `2026-09-29` is read too.

    :param text: The date, as `29 September 2026`.
    :return: `2026-09-29` or an empty string when it doesn't read as a
        date.
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
    """Say whether a day is from 2000 to a year ahead.

    :param iso: The day, as `2026-09-29`.
    :return: Whether it's one a page or a release could have.
    """
    return (
        date(2000, 1, 1)
        <= date.fromisoformat(iso)
        <= date.today() + timedelta(days=366)  # noqa: DTZ011
    )


def provenance(app: Sphinx, docname: str, source: list[str]) -> None:
    """Work out who wrote a page and when it was created and updated.

    The page's `.. Author:`, `.. Created on:` and `.. Last updated on:`
    comments win. A missing date comes from git (first or latest
    commit, read once for the whole build), then the build day. A
    missing author comes from the `byline` directive, then the project.

    :param app: The Sphinx application instance.
    :param docname: The document being read.
    :param source: The document's source, as docutils hands it over.
    :raises KaamikiError: For a date comment that isn't a date from
        2000 to a year ahead, or a page updated before it was created.
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
                    f"{key.capitalize()}: expected a date like 5 October"
                    f" 2026 or 2026-10-05, from 2000 to a year ahead, got"
                    f" {found[key]!r}",
                    where,
                )
    if (
        "created on" in found
        and "last updated on" in found
        and (day(found["last updated on"]) < day(found["created on"]))
    ):
        fail(
            "comment 'Last updated on' expected after 'Created on', got"
            " it before",
            where,
        )
    first, last = committed(app, docname)
    if not metadata.get("created"):
        metadata["created"] = found.get("created on") or written(first)
    if not metadata.get("last_updated"):
        metadata["last_updated"] = found.get("last updated on") or written(last)
