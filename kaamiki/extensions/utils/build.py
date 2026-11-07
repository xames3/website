"""\
Build Utilities
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 07 November 2026

The utilities that write the 404 page and the sitemap after a build.
"""

from __future__ import annotations

import os
import os.path as p
import posixpath
import typing as t
from html import escape
from urllib.parse import quote
from urllib.parse import unquote
from urllib.parse import urlsplit

import bs4
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util import logging

from kaamiki.extensions.utils.dates import day
from kaamiki.extensions.utils.settings import setting

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx

logger = logging.getLogger(__name__)

NOT_FOUND: t.Final[str] = "404"
MARKER: t.Final[str] = "Written by Kaamiki, turn it off with"
ROOTED_ATTRIBUTES: t.Final[tuple[str, ...]] = (
    "action",
    "data-content_root",
    "href",
    "src",
)
ROOTED_SKIP: t.Final[tuple[str, ...]] = ("#", "/", "data:", "mailto:", "tel:")


def root_urls(tree: bs4.BeautifulSoup, base: str, root: str) -> None:
    """Rewrite a page's relative URLs to start at the site root.

    The 404 page is served for any address, so a relative URL would
    resolve against whatever was asked for.

    :param tree: Parsed HTML tree, edited in place.
    :param base: The directory the page was rendered as being in.
    :param root: The path the site is served under, with its slashes.
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
    """Write Kaamiki's 404 page to the top of the output.

    Hosts serve `404.html` from the root and `html_additional_pages`
    can't put it there under `dirhtml`.

    ..  note:: Set `kaamiki.conf.show.not_found` to `False` in
        `conf.py` to skip it. A site with a page of its own called
        `404` keeps it.

    :param app: The Sphinx application instance.
    :return: `True` when the page was written.
    """
    builder = app.builder
    if not isinstance(builder, StandaloneHTMLBuilder):
        return False
    if not setting(app.config, "show_404"):
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
    builder.handle_page(
        NOT_FOUND,
        {
            "pageurl": None,
            "km_show_breadcrumbs": False,
            "km_show_feedback": False,
            "km_show_more": False,
            "km_show_page_last_updated": False,
            "km_show_previous_next_cards": False,
            "km_show_previous_next_pages": False,
            "km_show_scrolltop": False,
        },
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
    """Say whether a page asks to be kept out of search engines' reach.

    :param robots: The page's `:km-page-robots:` field, as written.
    :return: `True` for `noindex` or `none`, which is `noindex` and
        `nofollow` together.
    """
    rules = {_.strip().lower() for _ in robots.split(",")}
    return bool(rules & {"noindex", "none"})


def sitemap(app: Sphinx) -> bool:
    """Write `sitemap.xml` and `robots.txt` at the top of the output.

    Pages marked `noindex` or `none` in `:km-page-robots:` are left
    out. Nothing is written without `html_baseurl` or with
    `kaamiki.conf.show.sitemap` off. A `robots.txt` in
    `html_extra_path` is kept.

    :param app: The Sphinx application instance.
    :return: `True` when the sitemap was written.
    """
    home = app.config.html_baseurl
    if not home or not setting(app.config, "show_sitemap"):
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
    """Remove the files an earlier build wrote that this one doesn't.

    Only a file with Kaamiki's marker in it goes, so a `404.html` or a
    `robots.txt` the site made itself stays. The log says once which
    went.

    :param app: The Sphinx application instance.
    :param kept: The files this build wrote.
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


def build_finished(app: Sphinx, exc: Exception | None) -> None:
    """Write Kaamiki's 404 page and the sitemap once the build has
    worked.

    :param app: The Sphinx application instance.
    :param exc: Whatever went wrong during the build or `None`.
    """
    builder = app.builder
    if exc or not isinstance(builder, StandaloneHTMLBuilder):
        return
    if builder.name in {"html", "dirhtml"}:
        kept: tuple[str, ...] = ()
        if not_found(app):
            kept += (f"{NOT_FOUND}.html",)
        if sitemap(app):
            kept += ("sitemap.xml", "robots.txt")
        forget(app, kept)
