"""\
Social Metadata
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 15 November 2026

The handler that finds the Open Graph and Twitter values of a page.
"""

from __future__ import annotations

import html
import re
import typing as t

from sphinx.locale import _

from kaamiki.extensions.utils.build import NOT_FOUND
from kaamiki.extensions.utils.dates import day
from kaamiki.extensions.utils.doctree import standfirst
from kaamiki.extensions.utils.doctree import summarise
from kaamiki.extensions.utils.hooks import on
from kaamiki.extensions.utils.links import absolute
from kaamiki.extensions.utils.settings import DESCRIPTION_LENGTH
from kaamiki.extensions.utils.settings import NAME
from kaamiki.extensions.utils.settings import values
from kaamiki.extensions.utils.text import plain
from kaamiki.extensions.utils.text import tidy

if t.TYPE_CHECKING:
    from docutils import nodes
    from sphinx.application import Sphinx

META: t.Final[re.Pattern[str]] = re.compile(r"<meta\s[^>]*>")
ATTRIBUTE: t.Final[re.Pattern[str]] = re.compile(r'([\w:-]+)="([^"]*)"')


def generated(pagename: str) -> tuple[str, str] | None:
    """Name and describe a page that Sphinx writes without a source.

    :param pagename: The page that is written.
    :return: Its title and description, or `None` for a page with its
        own source. The words are found on each call, because the words
        of Kaamiki join the catalogue of Sphinx only after setup.
    """
    pages = {
        NOT_FOUND: (
            _("Page not found"),
            _(
                "There's nothing at this address. It may've moved or it"
                " may never have been here."
            ),
        ),
        "search": (_("Search results"), _("Search every page on this site.")),
    }
    found = pages.get(pagename)
    return (str(found[0]), str(found[1])) if found else None


def written(context: dict[str, t.Any]) -> str:
    """Find the description in the `.. meta::` of the page.

    :param context: The context of the page, whose `metatags` hold the
        tags of `.. meta::` as HTML.
    :return: The description, or an empty string when there is none.
    """
    for tag in META.findall(context.get("metatags") or ""):
        found = dict(ATTRIBUTE.findall(tag))
        if found.get("name") == "description":
            return tidy(html.unescape(found.get("content", "")))
    return ""


@on("html-page-context")
def social_metadata(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Find the Open Graph and Twitter values of a page.

    :param app: The Sphinx application instance. The title is
        `:km-page-title:`, else the title of the page. The description
        is the `.. meta::` of the page, then `:km-page-description:`,
        the lead, the words of a generated page, the `description` of
        the site, and the first paragraph. Only the title arrives as
        HTML, so only it loses its tags. The image is
        `:km-page-image:`, then `:km-page-backdrop:` (from the first
        `:backdrop:` of a `byline`), then the `image` of the site. A
        relative image path becomes absolute, because link previews
        ignore relative paths.
    :param pagename: The page that is written.
    :param templatename: The template that writes it.
    :param context: The context of the page, changed in place.
    :param doctree: The resolved doctree, or `None` for a generated
        page.
    """
    del templatename
    options = values(app.config).site.open_graph
    meta: dict[str, str] = context.get("meta") or {}
    limit = int(options.get("description_length", DESCRIPTION_LENGTH))
    made = generated(pagename) if doctree is None else None
    title = tidy(meta.get("km-page-title", "")) or plain(
        made[0]
        if made
        else context.get("title") or context.get("docstitle") or ""
    )
    description = (
        written(context)
        or meta.get("km-page-description")
        or standfirst(doctree, limit)
        or (made[1] if made else "")
        or options.get("description", "")
        or summarise(doctree, limit)
    )
    image = (
        meta.get("km-page-image")
        or meta.get("km-page-backdrop")
        or options.get("image", "")
    )
    alt = meta.get("km-page-image-alt") or (
        options.get("image_alt", "") if image == options.get("image") else ""
    )
    context[NAME]["site.open_graph"] = {
        "title": title,
        "description": tidy(description),
        "image": absolute(image, app.config.html_baseurl),
        "image_alt": tidy(alt),
        "published": day(meta.get("created", "")),
        "modified": day(meta.get("last_updated", "")),
        "site_name": options.get("site_name")
        or context.get("docstitle")
        or context.get("title", ""),
        "type": meta.get("km-page-type") or options.get("type", "website"),
        "locale": meta.get("km-page-locale") or options.get("locale", ""),
        "card": meta.get("km-page-card")
        or options.get("card", "summary_large_image"),
        "site": options.get("twitter_site", ""),
        "enable": options.get("enable") is not False,
    }
