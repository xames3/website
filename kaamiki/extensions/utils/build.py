"""\
Build Utilities
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 16 November 2026

The utilities that write the 404 page and the sitemap after a build,
the link checker that names a missing video and the one check of the
builder. Kaamiki writes web pages only, so a builder that is not in
`BUILDERS` stops the build.
"""

from __future__ import annotations

import copy
import os
import os.path as p
import posixpath
import typing as t
from html import escape
from urllib.parse import quote
from urllib.parse import unquote
from urllib.parse import urlsplit

import bs4
from sphinx.util import logging

from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils.dates import day
from kaamiki.extensions.utils.hooks import on
from kaamiki.extensions.utils.settings import NAME
from kaamiki.extensions.utils.settings import Kaamiki
from kaamiki.extensions.utils.settings import values

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.builders.html import StandaloneHTMLBuilder

logger = logging.getLogger(__name__)

PAGES: t.Final[tuple[str, ...]] = ("html", "dirhtml")
BUILDERS: t.Final[tuple[str, ...]] = (*PAGES, "linkcheck")
NOT_FOUND: t.Final[str] = "404"
MARKER: t.Final[str] = "Written by Kaamiki, turn it off with"
HIDDEN_ON_NOT_FOUND: t.Final[tuple[str, ...]] = (
    "breadcrumbs",
    "feedback",
    "more",
    "page_last_updated",
    "previous_next_cards",
    "previous_next_pages",
    "scrolltop",
)
ROOTED_ATTRIBUTES: t.Final[tuple[str, ...]] = (
    "action",
    "data-content_root",
    "href",
    "src",
)
ROOTED_SKIP: t.Final[tuple[str, ...]] = ("#", "/", "data:", "mailto:", "tel:")


@on("builder-inited", priority=100)
def refuse_builder(app: Sphinx) -> None:
    """Stop the build for a builder that is not in `BUILDERS`.

    :param app: The Sphinx application instance.
    :raises KaamikiError: For a builder that is not in `BUILDERS`.
    """
    name = app.builder.name
    if name not in BUILDERS:
        checks.fail(
            f"expected the {', '.join(BUILDERS[:-1])} or {BUILDERS[-1]}"
            f" builder, got {name!r}; Kaamiki writes web pages only",
            "builder",
        )


def writes_pages(app: Sphinx) -> bool:
    """Say whether the build writes the web pages.

    :param app: The Sphinx application instance.
    :return: `True` for a builder in `PAGES`, `False` for `linkcheck`.
    """
    return app.builder.name in PAGES


def root_urls(tree: bs4.BeautifulSoup, base: str, root: str) -> None:
    """Change the relative URLs of a page to the root.

    :param tree: The parsed HTML tree, changed in place. The 404 page
        is served for each address, so a relative URL would resolve
        against the requested address.
    :param base: The directory of the rendered page.
    :param root: The path of the site, with its slashes.
    """
    for tag in tree.find_all(True):
        for attribute in ROOTED_ATTRIBUTES:
            url = str(tag.get(attribute) or "")
            if not url or url.startswith(ROOTED_SKIP) or "://" in url:
                continue
            url, _, fragment = url.partition("#")
            path = posixpath.normpath(posixpath.join("/", base, url))
            if url.endswith("/") and not path.endswith("/"):
                path += "/"
            path = root.rstrip("/") + path
            tag[attribute] = f"{path}#{fragment}" if fragment else path


def not_found(app: Sphinx) -> bool:
    """Write the 404 page at the top of the output.

    :param app: The Sphinx application instance. Hosts serve `404.html`
        from the root, and `html_additional_pages` cannot put it there
        with `dirhtml`. Set `kaamiki.conf.show.not_found` to `False` to
        skip it. A site with its own page `404` keeps it.
    :return: `True` when the page was written.
    """
    builder = t.cast("StandaloneHTMLBuilder", app.builder)
    if not values(app.config).show.not_found:
        return False
    if NOT_FOUND in app.env.found_docs:
        logger.info(
            "the site has a page called %s, so Kaamiki's 404 page isn't"
            " written",
            NOT_FOUND,
        )
        return False
    if getattr(builder, "globalcontext", None) is None:
        return False
    page = p.join(app.outdir, f"{NOT_FOUND}.html")
    found = copy.copy(Kaamiki.of(builder))
    for name in HIDDEN_ON_NOT_FOUND:
        found[f"show.{name}"] = False
    builder.handle_page(
        NOT_FOUND,
        {"pageurl": None, NAME: found},
        f"{NOT_FOUND}.html",
        outfilename=page,  # type: ignore[arg-type]
    )
    base = posixpath.dirname(builder.get_target_uri(NOT_FOUND))
    root = urlsplit(app.config.html_baseurl).path or "/"
    with open(page, encoding="utf-8") as f:
        tree = bs4.BeautifulSoup(f, "html.parser")
    root_urls(tree, base, root)
    if tree.html:
        tree.html.insert(
            0, bs4.Comment(f" {MARKER} kaamiki.conf.show.not_found. ")
        )
    with open(page, "w", encoding="utf-8") as f:
        f.write(str(tree))
    return True


def is_noindex(robots: str) -> bool:
    """Say whether a page asks to stay out of search engines.

    :param robots: The `:km-page-robots:` field of the page, as
        written.
    :return: `True` for `noindex` or `none`, which is `noindex` and
        `nofollow` together.
    """
    rules = {_.strip().lower() for _ in robots.split(",")}
    return bool(rules & {"noindex", "none"})


def sitemap(app: Sphinx) -> bool:
    """Write `sitemap.xml` and `robots.txt`.

    :param app: The Sphinx application instance. Pages with `noindex`
        or `none` in `:km-page-robots:` are not included. Nothing is
        written without `html_baseurl`, or with
        `kaamiki.conf.show.sitemap` off. A `robots.txt` in
        `html_extra_path` is kept.
    :return: `True` when the sitemap was written.
    """
    home = app.config.html_baseurl
    if not home or not values(app.config).show.sitemap:
        return False
    home = home.rstrip("/") + "/"
    urls: list[str] = []
    for docname in sorted(app.env.found_docs):
        metadata = app.env.metadata.get(docname, {})
        if is_noindex(metadata.get("km-page-robots", "")):
            continue
        uri = app.builder.get_target_uri(docname)
        loc = escape(home + quote(unquote(uri), safe="/#"))
        updated = day(metadata.get("last_updated", ""))
        lastmod = f"<lastmod>{updated}</lastmod>" if updated else ""
        urls.append(f"  <url><loc>{loc}</loc>{lastmod}</url>")
    text = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f"<!-- {MARKER} kaamiki.conf.show.sitemap. -->",
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            *urls,
            "</urlset>",
            "",
        ]
    )
    with open(p.join(app.outdir, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(text)
    extra = [p.join(app.confdir, _) for _ in app.config.html_extra_path]
    if any(
        (p.basename(_) == "robots.txt" and p.isfile(_))
        or p.isfile(p.join(_, "robots.txt"))
        for _ in extra
    ):
        return True
    with open(p.join(app.outdir, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(
            f"# {MARKER} kaamiki.conf.show.sitemap.\n"
            f"User-agent: *\nDisallow:\n\nSitemap: {home}sitemap.xml\n"
        )
    return True


def forget(app: Sphinx, kept: tuple[str, ...]) -> None:
    """Remove the files of an earlier build.

    :param app: The Sphinx application instance.
    :param kept: The files that this build wrote. Only a file with the
        marker of Kaamiki goes, so a `404.html` or a `robots.txt` from
        the site stays. The log tells one time which files went.
    """
    gone: list[str] = []
    for name in (f"{NOT_FOUND}.html", "sitemap.xml", "robots.txt"):
        target = p.join(app.outdir, name)
        if name in kept or not p.isfile(target):
            continue
        with open(target, encoding="utf-8", errors="replace") as f:
            if MARKER in f.read(2048):
                os.remove(target)
                gone.append(name)
    if gone:
        logger.info(
            "removed %s, which an earlier build wrote and this one doesn't",
            ", ".join(gone),
        )


@on("build-finished")
def build_finished(app: Sphinx, exc: Exception | None) -> None:
    """Write the 404 page and the sitemap.

    :param app: The Sphinx application instance.
    :param exc: What went wrong in the build, or `None`.
    """
    if exc or not writes_pages(app):
        return
    kept: tuple[str, ...] = ()
    if not_found(app):
        kept += (f"{NOT_FOUND}.html",)
    if sitemap(app):
        kept += ("sitemap.xml", "robots.txt")
    forget(app, kept)
