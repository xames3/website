"""\
Context Utilities
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 15 October 2026

The utilities that fill a page's context for the templates.
"""

import typing as t
from urllib.parse import quote

from docutils import nodes
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.environment.adapters.toctree import global_toctree_for_doc
from sphinx.errors import ConfigError
from sphinx.locale import _
from sphinx.util import docname_join
from sphinx.util import logging

from kaamiki.extensions.utils.directives import toggle
from kaamiki.extensions.utils.doctree import standfirst
from kaamiki.extensions.utils.links import REL
from kaamiki.extensions.utils.links import opens_new_tab
from kaamiki.extensions.utils.settings import CREDIT
from kaamiki.extensions.utils.settings import DEFAULTS
from kaamiki.extensions.utils.settings import HEADER_LEAD_LENGTH
from kaamiki.extensions.utils.settings import HEADER_NO_SUBTITLE_FIELD
from kaamiki.extensions.utils.settings import HEADER_SUBTITLE_FIELD
from kaamiki.extensions.utils.settings import ICONS
from kaamiki.extensions.utils.settings import LOGO_SIZES
from kaamiki.extensions.utils.settings import PAGE_SWITCHES
from kaamiki.extensions.utils.settings import PROJECT
from kaamiki.extensions.utils.settings import icon
from kaamiki.extensions.utils.settings import setting
from kaamiki.extensions.utils.text import clip
from kaamiki.extensions.utils.text import plain
from kaamiki.extensions.utils.text import tidy

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment

logger = logging.getLogger(__name__)


def context_defaults(app: Sphinx) -> None:
    """Fill in the `html_context` keys the templates expect.

    Every setting in `DEFAULTS` is copied with a `km_` prefix, which is
    the only one the templates read, so one that is missing is its
    default and not an `UndefinedError`. The ones that need more than a
    copy are worked out after.

    This runs on `builder-inited` and not `config-inited`, which has
    gone by the time a theme picked through `html_theme` alone is set
    up.

    :param app: The Sphinx application instance.
    """
    config = app.config
    context: dict[str, t.Any] = config.html_context
    for key in DEFAULTS:
        context[f"km_{key}"] = setting(config, key)
    if unknown := context["km_fa_icons"].keys() - ICONS.keys():
        raise KeyError(
            f"fa_icons has {', '.join(sorted(unknown))};"
            f" it takes {', '.join(ICONS)}"
        )
    context["km_fa_icons"] = {**ICONS, **context["km_fa_icons"]}
    project = {**PROJECT, "author": config.author, **context["km_project"]}
    context["km_project"] = project
    if context["km_show_feedback"] is None:
        context["km_show_feedback"] = bool(
            project["email"] or context["km_feedback"].get("url")
        )
    if context["km_show_more_after"] < 1:
        raise ConfigError("show_more_after takes a number above zero")
    size = context["km_logo_size"]
    low, high = LOGO_SIZES
    if size is not None and not low <= size <= high:
        raise ConfigError(f"logo_size takes {low} to {high}, got {size}")
    depth = context["km_toctree_maxdepth"]
    context["km_toctree_args"] = {
        "includehidden": bool(context["km_toctree_includehidden"]),
        **({"maxdepth": depth} if depth else {}),
    }
    licence: dict[str, t.Any] = dict(context["km_license"])
    licence["new_tab"] = opens_new_tab(licence.get("url") or "", config)
    context["km_license"] = licence
    for key in ("header_buttons", "sidebar_buttons"):
        context[f"km_{key}"] = {
            text: {**button, "new_tab": opens_new_tab(button["url"], config)}
            for text, button in context[f"km_{key}"].items()
        }
    context["km_credit"] = CREDIT
    context["km_credit_new_tab"] = opens_new_tab(CREDIT, config)
    context["km_rel"] = REL
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

    `:km-fb-split:` (or `split` in the setting) puts the title and the
    button side by side.

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
    site: dict[str, str] = options["km_feedback"]
    email = options["km_project"]["email"]
    title = plain(context.get("title") or "")
    if meta.get("km-fb-subject") or site.get("subject"):
        said = str(meta.get("km-fb-subject") or site["subject"])
        said = said.replace("%s", title)
    else:
        said = str(_("Feedback about %s")) % title
    url: str | None = None
    if email:
        url = f"mailto:{email}?subject={quote(said)}"
    if (meta.get("km-fb-type") or site.get("type")) == "link":
        url = meta.get("km-fb-url") or site.get("url") or url
    icons = options["km_fa_icons"]
    context["km_feedback"] = {
        "split": toggle(meta["km-fb-split"])
        if "km-fb-split" in meta
        else bool(site.get("split")),
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
            meta.get("km-fb-icon") or site.get("icon"), icons["feedback"]
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
    del app, pagename, templatename, doctree
    meta: dict[str, str] = context.get("meta") or {}
    for key in PAGE_SWITCHES:
        field = "km-" + key.replace("_", "-")
        if field not in meta:
            continue
        context[f"km_{key}"] = toggle(meta[field])


def articles(env: BuildEnvironment) -> dict[str, str]:
    """Hold the release each article was linked from.

    :param env: The build environment.
    :return: The articles `release` links to, each with the page the
        release is written on.
    """
    found: dict[str, str] = env.__dict__.setdefault("km_articles", {})
    return found


def leads(env: BuildEnvironment) -> dict[str, str]:
    """Hold the lead of each page that has one.

    :param env: The build environment.
    :return: Each page's lead, keyed by its document name.
    """
    found: dict[str, str] = env.__dict__.setdefault("km_leads", {})
    return found


def note_lead(app: Sphinx, doctree: nodes.document) -> None:
    """Keep a page's lead as it's read, for the header's dropdowns.

    :param app: The Sphinx application instance.
    :param doctree: The page's doctree.
    """
    lead = standfirst(doctree, HEADER_LEAD_LENGTH)
    if lead:
        leads(app.env)[app.env.docname] = lead


def forget_lead(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    """Forget a page's lead, as it's read again or removed.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param docname: The page about to be read again.
    """
    del app
    leads(env).pop(docname, None)


def merge_leads(
    app: Sphinx,
    env: BuildEnvironment,
    docnames: set[str],
    other: BuildEnvironment,
) -> None:
    """Take in the leads a parallel reader found.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param docnames: The pages the reader read.
    :param other: The reader's build environment.
    """
    del app
    leads(env).update(
        {name: lead for name, lead in leads(other).items() if name in docnames}
    )


def header_leads(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Give the header a `toctree()` that adds each page's lead.

    The leads go into the links as `km-header__lead` spans, which the
    header's dropdowns show under the titles. A page's own
    `:km-header-subtitle:` wins over everything, then its lead and last
    its `:km-pg-description:`. A page with none of them is left as it
    is, as is one with `:km-header-no-subtitle:` and no subtitle.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree or `None` for generated
        pages.
    """
    del templatename, doctree
    builder = app.builder
    if not isinstance(builder, StandaloneHTMLBuilder):
        return

    def toctree(**kwargs: t.Any) -> str:
        tree = global_toctree_for_doc(
            app.env, pagename, builder, tags=builder.tags, **kwargs
        )
        if tree is None:
            return ""
        found: dict[str, str] = {}
        for name in app.env.found_docs:
            fields = app.env.metadata.get(name, {})
            text = tidy(fields.get(HEADER_SUBTITLE_FIELD, ""))
            if not text and not (
                HEADER_NO_SUBTITLE_FIELD in fields
                and toggle(fields[HEADER_NO_SUBTITLE_FIELD])
            ):
                text = clip(
                    leads(app.env).get(name)
                    or tidy(fields.get("km-pg-description", "")),
                    HEADER_LEAD_LENGTH,
                )
            if text:
                found[builder.get_relative_uri(pagename, name)] = text
        for reference in tree.findall(nodes.reference):
            lead = found.get(reference.get("refuri"))
            if lead:
                reference.append(
                    nodes.inline("", lead, classes=["km-header__lead"])
                )
        return builder.render_partial(tree)["fragment"]

    context["km_header_toctree"] = toctree


def neighbours(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Let a page name its own previous and next pages.

    Sphinx works those out from the toctree, so a page in none of them,
    an orphan, gets neither. `:km-pg-prev:` and `:km-pg-next:` take a
    document as `:doc:` would write it and win over the toctree's. An
    article a `release` links to, and that has no previous page, goes
    back to the page the release is on.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree or `None` for generated
        pages.
    """
    del templatename, doctree
    builder = app.builder
    if not isinstance(builder, StandaloneHTMLBuilder):
        return
    meta: dict[str, str] = context.get("meta") or {}
    released = articles(app.env)
    for key in ("prev", "next"):
        target = (meta.get(f"km-pg-{key}") or "").strip()
        if target:
            docname = docname_join(pagename, target)
            if docname not in app.env.found_docs:
                logger.warning(
                    ":km-pg-%s: names %r, which is not a document. As with"
                    " :doc:, a name not starting with / is relative to this"
                    " page",
                    key,
                    target,
                    location=pagename,
                    type="kaamiki",
                    subtype="pages",
                )
                continue
        elif key == "prev" and not context.get(key) and pagename in released:
            docname = released[pagename]
        else:
            continue
        title = builder.render_partial(app.env.titles[docname])["title"]
        context[key] = {
            "link": builder.get_relative_uri(pagename, docname),
            "title": title,
        }


def follow(
    app: Sphinx,
    env: BuildEnvironment,
    added: set[str],
    changed: set[str],
    removed: set[str],
) -> list[str]:
    """Send a page back through reading when a neighbour of it changes.

    The neighbour's title is written into the page, so the page is
    stale once the neighbour is retitled, moved or gone.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param added: The pages Sphinx found new.
    :param changed: The pages Sphinx found changed.
    :param removed: The pages Sphinx found gone.
    :return: The pages whose `:km-pg-prev:` or `:km-pg-next:` names a
        page that moved on, or whose release did.
    """
    del app
    moved = added | changed | removed
    stale: set[str] = set()
    for docname, meta in env.metadata.items():
        for key in ("km-pg-prev", "km-pg-next"):
            target = (meta.get(key) or "").strip()
            if target and docname_join(docname, target) in moved:
                stale.add(docname)
    for article, release in articles(env).items():
        if release in moved:
            stale.add(article)
    return sorted(stale - moved)
