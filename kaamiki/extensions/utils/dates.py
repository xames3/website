"""\
Date Utilities
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 09 October, 2026

The helpers that date a page, from its comments or from git.
"""

from __future__ import annotations

import re
import typing as t
from datetime import datetime as dt
from subprocess import DEVNULL
from subprocess import CalledProcessError
from subprocess import check_output as co

from sphinx.locale import _
from sphinx.util.i18n import format_date

from kaamiki.extensions.utils.settings import setting

if t.TYPE_CHECKING:
    from docutils import nodes
    from sphinx.application import Sphinx
    from sphinx.config import Config

HEADER_RE: re.Pattern[str] = re.compile(
    r"^\.\.\s+(Author|Created on|Last updated on):\s*(.+)$", re.IGNORECASE
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


def committed(app: Sphinx, docname: str, *, first: bool = False) -> dt | None:
    """Ask git when a page was last committed or first.

    :param app: The Sphinx application instance.
    :param docname: The document to ask about.
    :param first: Ask for the commit that brought the page in,
        following it through renames, rather than the latest one.
    :return: The commit's date or `None` outside a repository and for a
        page git has never seen.
    """
    src = str(app.env.doc2path(docname, base=True))
    order = ["--follow"] if first else ["-n1"]
    cmd = ["git", "log", *order, "--format=%cI", "--", src]
    try:
        on = co(cmd, cwd=app.confdir, stderr=DEVNULL).decode().split()  # noqa: S603
    except CalledProcessError, FileNotFoundError:
        return None
    return dt.fromisoformat(on[-1]) if on else None


def written(when: dt | None) -> str:
    """Write a date the way the header comments write it.

    :param when: The date or `None` for the day the site is built.
    :return: The date, as `29 September 2026`.
    """
    when = when or dt.now().astimezone()
    return f"{when.day} {when:%B} {when.year}"


def dated(when: dt, config: Config) -> str:
    """Write a date the way a reader wants it, in the site's language.

    Every date Kaamiki shows follows `html_last_updated_fmt` when the
    site sets it, then `last_updated_on_fmt`. With neither it's
    `05 October 2026` in English. `written` keeps the one form the
    header comments use, since Kaamiki reads that back.

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


def day(date: str) -> str:
    """Turn a date written like the header comments write it into ISO.

    The older `29 September, 2026` form is still read, so is
    `2026-09-29`.

    :param date: The date, as `29 September 2026`.
    :return: `2026-09-29` or an empty string when it doesn't read as a
        date.
    """
    for form in ("%d %B %Y", "%d %B, %Y", "%Y-%m-%d"):
        try:
            return dt.strptime(date, form).astimezone().date().isoformat()
        except ValueError:
            continue
    return ""


def provenance(app: Sphinx, docname: str, source: list[str]) -> None:
    """Work out who wrote a page and when it was created and updated.

    The page's `.. Author:`, `.. Created on:` and `.. Last updated on:`
    comments win. A missing date comes from git (first or latest
    commit), then the build day. A missing author comes from the
    `author` directive, then the project.

    :param app: The Sphinx application instance.
    :param docname: The document being read.
    :param source: The document's source, as docutils hands it over.
    """
    metadata = app.env.metadata.setdefault(docname, {})
    found = header(source[0] if source else "")
    if found.get("author"):
        metadata.setdefault("author", found["author"])
    if not metadata.get("created"):
        metadata["created"] = found.get("created on") or written(
            committed(app, docname, first=True)
        )
    if not metadata.get("last_updated"):
        metadata["last_updated"] = found.get("last updated on") or written(
            committed(app, docname)
        )
