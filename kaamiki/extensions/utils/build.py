"""\
Build Utilities
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 15 November 2026

The utilities that write the 404 page and the sitemap after a build,
and the link checker that names a missing video.
"""

from __future__ import annotations

import os
import os.path as p
import posixpath
import re
import typing as t
from html import escape
from urllib.parse import quote
from urllib.parse import unquote
from urllib.parse import urlsplit

import bs4
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.builders.linkcheck import CheckExternalLinksBuilder
from sphinx.util import logging

from kaamiki.extensions.utils.dates import day
from kaamiki.extensions.utils.hooks import on
from kaamiki.extensions.utils.links import youtube_still_id
from kaamiki.extensions.utils.settings import values

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.builders.linkcheck import CheckResult

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
GONE: t.Final[re.Pattern[str]] = re.compile(r"(?:404|410) Client Error")
GONE_MESSAGE: t.Final[str] = "the video is deleted or private"


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
    builder = app.builder
    if not isinstance(builder, StandaloneHTMLBuilder):
        return False
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


class linkcheck(CheckExternalLinksBuilder):
    """The link checker, which names a video, not its picture."""

    def process_result(self, result: CheckResult) -> None:
        """Report a result, with the video for its picture.

        :param result: What the checker found for one link. `thumbnail`
            and `youtube` give the checker the picture, because YouTube
            serves the page of a removed video. A missing picture is
            reported as the link of the video, with the reason. Sphinx
            keeps no code for a broken link, so a 404 or a 410 is read
            from the start of its message. The other results are those
            of Sphinx.
        """
        vid = youtube_still_id(result.uri)
        if vid is not None:
            result = result._replace(
                uri=f"https://www.youtube.com/watch?v={vid}"
            )
            if result.status == "broken" and GONE.match(result.message):
                result = result._replace(message=GONE_MESSAGE)
        super().process_result(result)
