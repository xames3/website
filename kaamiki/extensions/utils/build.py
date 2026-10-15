"""\
Build Utilities
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 15 October 2026

The utilities that write the 404 page and the sitemap after a build.
"""

import os.path as p
import posixpath
import typing as t
from html import escape
from urllib.parse import quote
from urllib.parse import urlsplit

import bs4
from sphinx.builders.html import StandaloneHTMLBuilder

from kaamiki.extensions.utils.dates import day
from kaamiki.extensions.utils.settings import setting
from kaamiki.extensions.utils.templates import themed

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx

NOT_FOUND: t.Final[str] = "404"
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


def not_found(app: Sphinx) -> None:
    """Write Kaamiki's 404 page to the top of the output.

    Hosts serve `404.html` from the root and `html_additional_pages`
    can't put it there under `dirhtml`.

    ..  note:: Set `show_404` to `False` in `html_context` to skip it.

    :param app: The Sphinx application instance.
    """
    builder = app.builder
    if not isinstance(builder, StandaloneHTMLBuilder):
        return
    if not setting(app.config, "show_404"):
        return
    if getattr(builder, "globalcontext", None) is None:
        return
    page = p.join(app.outdir, f"{NOT_FOUND}.html")
    builder.handle_page(
        NOT_FOUND,
        {
            "pageurl": None,
            "km_show_breadcrumbs": False,
            "km_show_feedback": False,
            "km_show_more": False,
            "km_show_page_last_updated": False,
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
    with open(page, "w", encoding="utf-8") as f:
        f.write(str(tree))


def hidden(robots: str) -> bool:
    """Keep pages out of search engines' reach.

    :param robots: The page's `:km-pg-robots:` field, as written.
    :return: `True` for `noindex` or `none`, which is `noindex` and
        `nofollow` together.
    """
    rules = {_.strip().lower() for _ in robots.split(",")}
    return bool(rules & {"noindex", "none"})


def sitemap(app: Sphinx) -> None:
    """Write `sitemap.xml` and `robots.txt` at the top of the output.

    Pages marked `noindex` or `none` in `:km-pg-robots:` are left out.
    Nothing is written without `html_baseurl` or with `show_sitemap`
    off. A `robots.txt` in `html_extra_path` is kept.

    :param app: The Sphinx application instance.
    """
    home = app.config.html_baseurl
    if not home or not setting(app.config, "show_sitemap"):
        return
    home = home.rstrip("/") + "/"
    urls: list[str] = []
    for docname in sorted(app.env.found_docs):
        metadata = app.env.metadata.get(docname, {})
        if hidden(metadata.get("km-pg-robots", "")):
            continue
        loc = escape(home + quote(app.builder.get_target_uri(docname)))
        updated = day(metadata.get("last_updated", ""))
        lastmod = f"<lastmod>{updated}</lastmod>" if updated else ""
        urls.append(f"  <url><loc>{loc}</loc>{lastmod}</url>")
    text = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
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
        return
    with open(p.join(app.outdir, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nDisallow:\n\nSitemap: {home}sitemap.xml\n")


def build_finished(app: Sphinx, exc: Exception | None) -> None:
    """Write Kaamiki's 404 page and the sitemap once the build has
    worked.

    :param app: The Sphinx application instance.
    :param exc: Whatever went wrong during the build or `None`.
    """
    builder = app.builder
    if exc or not isinstance(builder, StandaloneHTMLBuilder):
        return
    if themed(builder) and builder.name in {"html", "dirhtml"}:
        not_found(app)
        sitemap(app)
