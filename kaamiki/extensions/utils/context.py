"""\
Context Utilities
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 09 October 2026

The utilities that fill a page's context for the templates.
"""

from __future__ import annotations

import typing as t
from urllib.parse import quote

from sphinx.locale import _
from sphinx.util import logging

from kaamiki.extensions.utils.directives import toggle
from kaamiki.extensions.utils.links import opens_new_tab
from kaamiki.extensions.utils.settings import FA_FREE
from kaamiki.extensions.utils.settings import FA_STYLE
from kaamiki.extensions.utils.settings import FEEDBACK_KEYS
from kaamiki.extensions.utils.settings import ICONS
from kaamiki.extensions.utils.settings import OPTIONS
from kaamiki.extensions.utils.settings import PAGE_SWITCHES
from kaamiki.extensions.utils.settings import PROJECT
from kaamiki.extensions.utils.settings import SWITCHES
from kaamiki.extensions.utils.settings import TEMPLATED
from kaamiki.extensions.utils.settings import icon
from kaamiki.extensions.utils.settings import logo_size
from kaamiki.extensions.utils.settings import setting
from kaamiki.extensions.utils.settings import toctree_args
from kaamiki.extensions.utils.text import plain

if t.TYPE_CHECKING:
    from docutils import nodes
    from sphinx.application import Sphinx

logger = logging.getLogger(__name__)


def context_defaults(app: Sphinx) -> None:
    """Fill in the `html_context` keys the templates expect.

    Every setting in `OPTIONS` is copied with a `km_` prefix, which is
    the only one Kaamiki reads. Missing ones get defaults, since a
    template fails with an `UndefinedError` on an attribute that isn't
    there.

    This runs on `builder-inited` and not `config-inited`, which has
    gone by the time a theme picked through `html_theme` alone is set
    up.

    :param app: The Sphinx application instance.
    """
    context: dict[str, t.Any] = app.config.html_context
    for option in OPTIONS:
        if option in context:
            context[f"km_{option}"] = context[option]
    icons: dict[str, str] = dict(ICONS)
    icons.update(context.get("fa_icons") or {})
    context["km_fa_icons"] = icons
    project: dict[str, str] = dict(PROJECT)
    project["author"] = app.config.author
    project.update(context.get("project") or {})
    context["km_project"] = project
    for key, value in SWITCHES.items():
        context.setdefault(f"km_{key}", value)
    context.setdefault("km_show_feedback", bool(project["email"]))
    unknown = sorted(set(context.get("feedback") or {}) - FEEDBACK_KEYS)
    if unknown:
        logger.warning(
            "feedback has %s, which it does not take; it takes %s",
            ", ".join(unknown),
            ", ".join(sorted(FEEDBACK_KEYS)),
            type="kaamiki",
        )
    for key in TEMPLATED:
        context[f"km_{key}"] = setting(app.config, key)
    context["km_toctree_args"] = toctree_args(app.config)
    context["km_logo_size"] = logo_size(app.config)
    context.setdefault("km_fa_style", FA_STYLE)
    context.setdefault("km_fa_css", FA_FREE)
    licence: dict[str, t.Any] = dict(context.get("license") or {})
    licence["new_tab"] = opens_new_tab(licence.get("url") or "", app.config)
    context["km_license"] = licence
    for key in ("header_buttons", "sidebar_buttons"):
        buttons: dict[str, t.Any] = {}
        for text, button in (context.get(key) or {}).items():
            if isinstance(button, dict):
                url = str(button.get("url") or "")
                button = {**button, "new_tab": opens_new_tab(url, app.config)}
            buttons[text] = button
        context[f"km_{key}"] = buttons
    config = app.config
    if "html_show_sphinx" not in config._raw_config | config._overrides:
        context.setdefault("show_sphinx", False)


def feedback(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Work out what a page's feedback box says and where it points.

    The page's `:km-fb-*:` fields are considered first, then
    the `feedback` setting, then Kaamiki's own words. The button mails
    the address in `project` or links where the page or the setting
    says.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree or `None` for generated
        pages.
    """
    del pagename, templatename, doctree
    options = app.config.html_context
    meta: dict[str, str] = context.get("meta") or {}
    site: dict[str, str] = setting(app.config, "feedback")
    email = options["km_project"]["email"]
    title = plain(context.get("title") or "")
    if site.get("subject"):
        said = str(site["subject"]).replace("%s", title)
    else:
        said = str(_("Feedback about %s")) % title
    url: str | None = None
    if email:
        url = f"mailto:{email}?subject={quote(said)}"
    if (meta.get("km-fb-type") or site.get("type")) == "link":
        url = meta.get("km-fb-url") or site.get("url") or url
    icons = options["km_fa_icons"]
    context["km_feedback"] = {
        "mode": meta.get("km-fb-mode") or site.get("mode") or "default",
        "title": meta.get("km-fb-title")
        or site.get("title")
        or str(_("Feedback")),
        "description": meta.get("km-fb-description")
        or site.get("description")
        or str(_("Let me know how this can be improved.")),
        "button": meta.get("km-fb-button")
        or site.get("button")
        or str(_("Submit")),
        "icon": icon(
            meta.get("km-fb-fa-icon") or site.get("icon"), icons["feedback"]
        ),
        "url": url,
    }


def page_switches(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Let a page turn a `show_*` setting on or off for itself.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree or `None` for generated
        pages.
    """
    del app, templatename, doctree
    meta: dict[str, str] = context.get("meta") or {}
    for key in PAGE_SWITCHES:
        field = "km-" + key.replace("_", "-")
        if field not in meta:
            continue
        try:
            context[f"km_{key}"] = toggle(meta[field])
        except ValueError:
            logger.warning(
                ":%s: takes true or false, got %r",
                field,
                meta[field],
                location=pagename,
                type="kaamiki",
            )
