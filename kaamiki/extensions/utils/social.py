"""\
Social Metadata
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 09 October 2026

The handler that works out a page's Open Graph and Twitter values.
"""

from __future__ import annotations

import typing as t

from sphinx.locale import _

from kaamiki.extensions.utils.build import NOT_FOUND
from kaamiki.extensions.utils.dates import day
from kaamiki.extensions.utils.doctree import standfirst
from kaamiki.extensions.utils.doctree import summarise
from kaamiki.extensions.utils.links import absolute
from kaamiki.extensions.utils.text import plain
from kaamiki.extensions.utils.text import tidy

if t.TYPE_CHECKING:
    from docutils import nodes
    from sphinx.application import Sphinx


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
                "There is nothing at this address. It may have moved or it"
                " may never have been here."
            ),
        ),
        "genindex": (
            _("Index"),
            _("Every term indexed on this site, from A to Z."),
        ),
        "search": (_("Search Results"), _("Search every page on this site.")),
    }
    found = pages.get(pagename)
    return (str(found[0]), str(found[1])) if found else None


def social_metadata(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Work out the Open Graph and Twitter values for a page.

    Each prefers the page's own `:km-pg-*:` field, then the
    `html_context` default, then whatever the page offers. Only the
    title arrives as rendered HTML, so only it's stripped of tags.

    The image goes the page's `:km-pg-image:` field first, then the
    first `:background:` of its `author` directive and last the site's
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
    options = app.config.html_context.get("km_open_graph") or {}
    if options.get("enable") is False:
        return
    meta: dict[str, str] = context.get("meta") or {}
    limit = int(options.get("description_length", 200))
    made = generated(pagename) if doctree is None else None
    title = tidy(meta.get("km-pg-title", "")) or plain(
        made[0]
        if made
        else context.get("title") or context.get("docstitle") or ""
    )
    description = (
        meta.get("km-pg-description")
        or standfirst(doctree, limit)
        or (made[1] if made else "")
        or options.get("description", "")
        or summarise(doctree, limit)
    )
    image = (
        meta.get("km-pg-image")
        or meta.get("km-pg-background")
        or options.get("image", "")
    )
    alt = meta.get("km-pg-image-alt") or (
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
        "type": meta.get("km-pg-type") or options.get("type", "website"),
        "locale": meta.get("km-pg-locale") or options.get("locale", ""),
        "card": meta.get("km-pg-card")
        or options.get("card", "summary_large_image"),
        "site": options.get("twitter_site", ""),
    }
