"""\
Social Metadata
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 27 October 2026

The handler that works out a page's Open Graph and Twitter values.
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
from kaamiki.extensions.utils.links import absolute
from kaamiki.extensions.utils.settings import DESCRIPTION_LENGTH
from kaamiki.extensions.utils.settings import setting
from kaamiki.extensions.utils.text import plain
from kaamiki.extensions.utils.text import tidy

if t.TYPE_CHECKING:
    from docutils import nodes
    from sphinx.application import Sphinx

META: re.Pattern[str] = re.compile(r"<meta\s[^>]*>")
ATTRIBUTE: re.Pattern[str] = re.compile(r'([\w:-]+)="([^"]*)"')


def generated(pagename: str) -> tuple[str, str] | None:
    """Name and describe a page Sphinx writes without a source file.

    The words are looked up on every call, since Kaamiki's own words
    only join Sphinx's catalogue once it's set up.

    :param pagename: The page being rendered.
    :return: Its title and description or `None` for a page with a
        source of its own.
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
    """Find the description the page's own `.. meta::` gives.

    :param context: The page's rendering context, whose `metatags` hold
        the tags `.. meta::` wrote, as HTML.
    :return: The description, or an empty string when there isn't one.
    """
    for tag in META.findall(context.get("metatags") or ""):
        found = dict(ATTRIBUTE.findall(tag))
        if found.get("name") == "description":
            return tidy(html.unescape(found.get("content", "")))
    return ""


def social_metadata(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Work out the Open Graph and Twitter values for a page.

    The title is the page's `:km-page-title:` field, or else its own
    title. The description is the one the page's own `.. meta::` gives,
    then the `:km-page-description:` field, the page's lead, the words
    of a generated page, the site's `description` and last the page's
    first paragraph. Only the title arrives as rendered HTML, so only
    it's stripped of tags.

    The image goes the page's `:km-page-image:` field first, then the
    first `:backdrop:` of its `byline` directive and last the site's
    `image`.

    Relative image paths are made absolute, since link previews ignore
    them.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree or `None` for generated
        pages.
    """
    del templatename
    options = setting(app.config, "open_graph")
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
    context["km_social"] = {
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
