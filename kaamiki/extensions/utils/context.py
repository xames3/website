"""\
Context Utilities
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 07 November 2026

The utilities that fill a page's context for the templates.
"""

from __future__ import annotations

import difflib
import json
import re
import typing as t
from datetime import datetime
from html import unescape
from urllib.parse import quote

from docutils import nodes
from sphinx import addnodes
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.environment.adapters.toctree import global_toctree_for_doc
from sphinx.locale import _
from sphinx.util import docname_join
from sphinx.util import logging

from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils.build import is_noindex
from kaamiki.extensions.utils.checks import fail
from kaamiki.extensions.utils.checks import location
from kaamiki.extensions.utils.dates import dated
from kaamiki.extensions.utils.dates import day
from kaamiki.extensions.utils.directives import toggle
from kaamiki.extensions.utils.doctree import findall
from kaamiki.extensions.utils.doctree import standfirst
from kaamiki.extensions.utils.icons import Icons
from kaamiki.extensions.utils.links import REL
from kaamiki.extensions.utils.links import opens_new_tab
from kaamiki.extensions.utils.settings import CARDS
from kaamiki.extensions.utils.settings import CREDIT
from kaamiki.extensions.utils.settings import FA_FREE
from kaamiki.extensions.utils.settings import FA_FREE_INTEGRITY
from kaamiki.extensions.utils.settings import HEADER_LEAD_LENGTH
from kaamiki.extensions.utils.settings import HEADER_NO_SUBTITLE_FIELD
from kaamiki.extensions.utils.settings import HEADER_SUBTITLE_FIELD
from kaamiki.extensions.utils.settings import OG_LOCALE
from kaamiki.extensions.utils.settings import OG_TYPE
from kaamiki.extensions.utils.settings import PAGE_SWITCHES
from kaamiki.extensions.utils.settings import PROJECT
from kaamiki.extensions.utils.settings import kept
from kaamiki.extensions.utils.settings import setting
from kaamiki.extensions.utils.settings import site_values
from kaamiki.extensions.utils.settings import stored
from kaamiki.extensions.utils.settings import validate
from kaamiki.extensions.utils.text import clip
from kaamiki.extensions.utils.text import levelled
from kaamiki.extensions.utils.text import plain
from kaamiki.extensions.utils.text import tidy

if t.TYPE_CHECKING:
    from collections.abc import Callable

    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment

logger = logging.getLogger(__name__)


def confdir(env: BuildEnvironment) -> str:
    """Find the folder `conf.py` is in without asking the application.

    :param env: The build environment.
    :return: The folder, as the build that last began had it.
    """
    return str(stored(env, "confdir", ""))


TEMPLATE_KEYS: t.Final[tuple[str, ...]] = (
    "copy_headerlinks",
    "embed_js_loading",
    "favicons",
    "logo_size",
    "show_breadcrumbs",
    "show_credit",
    "show_feedback",
    "show_more",
    "show_more_after",
    "show_page_last_updated",
    "show_previous_next_cards",
    "show_previous_next_cards_count",
    "show_previous_next_pages",
    "show_scrolltop",
    "show_searchbox",
    "toctree_in_header",
    "toctree_titles_only",
)


def context_defaults(app: Sphinx) -> None:
    """Fill in the `html_context` keys the templates expect.

    The settings the templates read are copied with a `km_` prefix, so
    one that's missing is its default and not an `UndefinedError`.
    `show_more_after` is there for `show_more`. The ones that need
    more than a copy are worked out after: `km_fa_icons`, `km_fa_kit`,
    `km_fa_style`, `km_fa_integrity`, `km_project`, `km_license`,
    `km_header_buttons`, `km_sidebar_buttons`, `km_toctree_args`,
    `km_credit`, `km_credit_new_tab`, `km_rel` and `km_site`. Those and
    the ones a handler sets for each page (`km_author`, `km_feedback`,
    `km_header_toctree`, `km_social` and `km_updated_on`) are the only
    names the templates are promised, a site's own templates that read
    another setting have to read it themselves.

    Kaamiki has no page for the general index, so `html_use_index` is
    turned off, and a site that turned it on is told. Sphinx's credit is
    hidden unless the site sets `html_show_sphinx`, since
    `kaamiki.conf.show.credit` has Kaamiki's own.

    This runs on `builder-inited`, once the builder has read the
    configuration.

    :param app: The Sphinx application instance.
    """
    validate(app)
    kept(app.env, "confdir", str(app.confdir))
    config = app.config
    context: dict[str, t.Any] = config.html_context
    for key in TEMPLATE_KEYS:
        context[f"km_{key}"] = setting(config, key)
    icons = Icons.of(config)
    context["km_fa_icons"] = icons.roles(setting(config, "fa_icons"))
    context["km_fa_kit"] = icons.kit
    context["km_fa_style"] = icons.font_style
    project = {**PROJECT, "author": config.author, **setting(config, "project")}
    context["km_project"] = project
    if context["km_show_feedback"] is None:
        context["km_show_feedback"] = bool(
            project["email"] or setting(config, "feedback").get("url")
        )
    depth = setting(config, "toctree_maxdepth")
    context["km_toctree_args"] = {
        "includehidden": bool(setting(config, "toctree_includehidden")),
        **({"maxdepth": depth} if depth else {}),
    }
    terms = setting(config, "license")
    context["km_license"] = {
        **terms,
        "new_tab": opens_new_tab(terms.get("url") or "", config),
    }
    for key in ("header_buttons", "sidebar_buttons"):
        context[f"km_{key}"] = {
            text: {
                **button,
                "icon": icons.custom(button.get("icon")),
                "new_tab": opens_new_tab(button["url"], config),
            }
            for text, button in setting(config, key).items()
        }
    context["km_credit"] = CREDIT
    context["km_credit_new_tab"] = opens_new_tab(CREDIT, config)
    context["km_fa_css"] = FA_FREE
    context["km_fa_integrity"] = FA_FREE_INTEGRITY
    context["km_rel"] = REL
    named = site_values(config)
    context["km_site"] = str(named.get("html_title") or config.project)
    if "html_use_index" in named and config.html_use_index:
        logger.warning(
            "html_use_index is True, but Kaamiki has no page for the"
            " general index, so it is left off. Leave html_use_index out of"
            " conf.py",
            type="kaamiki",
            subtype="settings",
        )
    config.html_use_index = False
    if isinstance(app.builder, StandaloneHTMLBuilder):
        app.builder.use_index = False
    if "html_show_sphinx" not in named:
        context.setdefault("show_sphinx", False)


SWITCHES: t.Final[frozenset[str]] = frozenset(
    {
        "km-feedback-split",
        "km-header-no-subtitle",
        "km-related-skip-page",
        *("km-" + _.replace("_", "-") for _ in PAGE_SWITCHES),
    }
)
ROBOTS: t.Final[frozenset[str]] = frozenset(
    {
        "all",
        "index",
        "follow",
        "noarchive",
        "nofollow",
        "noindex",
        "none",
        "nosnippet",
    }
)
RELATED_MOST: t.Final[int] = 7


def pages(argument: str) -> list[str]:
    """Read the pages `:km-related-docs:` names, split by commas.

    :param argument: The pages as written, like a toctree's.
    :return: Each page's name, with the spaces around it trimmed.
    :raises ValueError: For a blank name (a comma at the end is one) or
        more than `RELATED_MOST` pages. A page named twice is refused
        by `page_fields`, once the names are resolved.
    """
    names = [_.strip() for _ in argument.split(",")]
    if not argument.strip() or "" in names:
        raise ValueError(f"expected pages split by commas, got {argument!r}")
    if len(names) > RELATED_MOST:
        raise ValueError(
            f"expected at most {RELATED_MOST} pages, got {len(names)}"
        )
    return names


FIELDS: t.Final[dict[str, Callable[[str], t.Any]]] = {
    "km-feedback-button": checks.text,
    "km-feedback-description": checks.text,
    "km-feedback-icon": checks.icon,
    "km-feedback-subject": checks.text,
    "km-feedback-title": checks.text,
    "km-feedback-type": checks.word("mail", "link"),
    "km-feedback-url": checks.link,
    "km-header-subtitle": lambda _: checks.text(_, 120),
    "km-page-backdrop": checks.picture,
    "km-page-card": checks.word(*CARDS),
    "km-page-description": lambda _: checks.text(_, 300),
    "km-page-image": checks.link,
    "km-page-image-alt": checks.text,
    "km-page-language": checks.language,
    "km-page-locale": OG_LOCALE,
    "km-page-next": checks.text,
    "km-page-prev": checks.text,
    "km-page-robots": lambda _: [
        checks.word(*ROBOTS)(each.strip()) for each in _.split(",")
    ],
    "km-page-title": lambda _: checks.text(_, 120),
    "km-page-type": OG_TYPE,
    "km-related-docs": pages,
    "km-related-header": lambda _: checks.text(_, 120),
}


def field_lists(app: Sphinx, doctree: nodes.document) -> None:
    """Stop for a `:km-*:` field that is written twice or isn't one of
    the fields a page opens with.

    It runs on `doctree-read` at priority 300, ahead of Sphinx's metadata
    collector at 500, which takes the field list out of the page.
    Moved after it, there would be no field list left to look at and
    nothing would be refused. It keeps where each field is, for
    `page_fields` to quote.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read.
    :raises KaamikiError: For the first such field.
    """
    info = next(findall(doctree, nodes.docinfo), None)
    seen: set[str] = set()
    places = t.cast(
        "dict[str, str]", app.env.temp_data.setdefault("km_fields", {})
    )
    for field in findall(doctree, nodes.field):
        name = field[0].astext()
        if not name.startswith("km-"):
            continue
        if info is None or field.parent is not info:
            fail(
                f"field :{name}: expected above the page title, with the"
                " page's other fields, got it below",
                location(field),
            )
        if name in seen:
            fail(f"field :{name}: expected once, got twice", location(field))
        seen.add(name)
        places[name] = location(field)


def page_title(app: Sphinx, doctree: nodes.document) -> None:
    """Stop for a page that has no title with words in it.

    A page's title names it in the tab, the navigation, the cards, the
    search and the link preview, so one that is missing, or is only an
    icon, leaves each of them with nothing to say.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read.
    :raises KaamikiError: For a page with no title or only an icon.
    """
    where = str(app.env.doc2path(app.env.docname))
    section = next(
        (_ for _ in doctree.children if isinstance(_, nodes.section)), None
    )
    heading = section[0] if section is not None else None
    if not isinstance(heading, nodes.title):
        fail("page: expected a title, got none", where)
    elif not heading.astext().strip():
        fail(
            "page: expected a title with words, got only an icon",
            location(heading),
        )


def admonition_title(app: Sphinx, doctree: nodes.document) -> None:
    """Stop for a custom admonition whose title has no words.

    The `admonition` directive is the one admonition that is named by its
    title, so an icon alone is no name. The ones docutils draws for
    themselves (`note`, `tip`, `warning` and the others) are named by
    their kind and may show only their icon.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read.
    :raises KaamikiError: For an `admonition` with no title with words.
    """
    del app
    for node in findall(doctree, nodes.admonition):
        if type(node) is not nodes.admonition:
            continue
        heading = node[0] if node.children else None
        if not isinstance(heading, nodes.title) or not heading.astext().strip():
            fail(
                "admonition: expected a title with words, got only an icon"
                " or nothing",
                location(node),
            )


def page_fields(app: Sphinx, doctree: nodes.document) -> None:  # noqa: ARG001
    """Check the `:km-*:` fields a page opens with.

    It runs on `doctree-read` at priority 600, after Sphinx's metadata
    collector at 500 has filled `env.metadata`, which is where it reads
    the fields. Moved ahead of the collector, there would be nothing to
    read and nothing would be refused.

    A page marked `noindex` or `none` in `:km-page-robots:` is kept out
    of the site's own search too, through Sphinx's `nosearch`.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read.
    :raises KaamikiError: For a `km-` field Kaamiki doesn't read, a
        value it doesn't take or fields that don't go together.
    """
    docname = app.env.docname
    found = app.env.metadata.get(docname, {})
    where = str(app.env.doc2path(docname))
    places = t.cast("dict[str, str]", app.env.temp_data.get("km_fields", {}))
    for key, value in found.items():
        if not key.startswith("km-"):
            continue
        at = places.get(key, where)
        try:
            if key in SWITCHES:
                toggle(value)
            elif key in FIELDS:
                FIELDS[key](value)
            else:
                known = sorted([*FIELDS, *SWITCHES])
                near = difflib.get_close_matches(key, known, n=1, cutoff=0.7)
                fail(
                    f"field :{key}: expected a field Kaamiki reads, got it"
                    + (f"; did you mean :{near[0]}:?" if near else ""),
                    at,
                )
        except ValueError as error:
            fail(f"field :{key}: {error}", at)
    if "km-feedback-icon" in found:
        try:
            Icons.of(app.config).custom(found["km-feedback-icon"])
        except ValueError as error:
            fail(
                f"field :km-feedback-icon: {error}",
                places.get("km-feedback-icon", where),
            )
    if "km-show-feedback" in found and toggle(found["km-show-feedback"]):
        email = setting(app.config, "project").get("email")
        site = setting(app.config, "feedback").get("url")
        if not (email or site or found.get("km-feedback-url")):
            fail(
                "field :km-show-feedback: is on but there is nowhere to send"
                " feedback: set an email in kaamiki.conf.site.project, a url in"
                " kaamiki.conf.site.feedback or :km-feedback-url: on the page",
                places.get("km-show-feedback", where),
            )
    kind = found.get("km-feedback-type")
    if ("km-feedback-url" in found) != (kind == "link"):
        fail(
            "field :km-feedback-url: expected with :km-feedback-type: link"
            " and only then",
            where,
        )
    for key in ("km-page-prev", "km-page-next"):
        if key in found:
            target = docname_join(docname, found[key].strip())
            if target == docname or target not in app.env.found_docs:
                fail(
                    f"field :{key}: expected another page, got {found[key]!r}",
                    places.get(key, where),
                )
    if "km-related-header" in found and "km-related-docs" not in found:
        fail(
            "field :km-related-header: expected with :km-related-docs: and"
            " only then",
            places.get("km-related-header", where),
        )
    if "km-related-docs" in found and skipped(app.env, docname):
        fail(
            "field :km-related-docs: not allowed with :km-related-skip-page:,"
            " which gives the page no cards",
            places.get("km-related-docs", where),
        )
    if "km-related-docs" in found:
        field = "km-show-previous-next-cards"
        if field in found and not toggle(found[field]):
            fail(
                "field :km-related-docs: not allowed with"
                f" :{field}: false, which turns the cards off",
                places.get("km-related-docs", where),
            )
        if field not in found and not setting(
            app.config, "show_previous_next_cards"
        ):
            fail(
                "field :km-related-docs: needs"
                " kaamiki.conf.show.previous_next_cards, which is False",
                places.get("km-related-docs", where),
            )
    listed: set[str] = set()
    for target in related_docs(docname, found):
        at = places.get("km-related-docs", where)
        if target == docname:
            fail(
                "field :km-related-docs: expected pages other than this one,"
                f" got {target!r}",
                at,
            )
        if target not in app.env.found_docs:
            fail(
                f"field :km-related-docs: expected pages that exist, got "
                f"{target!r}",
                at,
            )
        if target in listed:
            fail(
                f"field :km-related-docs: expected each page once, got "
                f"{target!r} again",
                at,
            )
        listed.add(target)
    if is_noindex(found.get("km-page-robots", "")):
        found["nosearch"] = ""


def feedback(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Work out what a page's feedback box says and where it points.

    The page's `:km-feedback-*:` fields are considered first, then
    the `kaamiki.conf.site.feedback` setting, then Kaamiki's own words. The
    button mails the address in `kaamiki.conf.site.project` or links where the
    page or the setting says. A box has a button, so a site with no email and
    no link has no box, except on a page that gives a link of its own.

    `:km-feedback-split:` (or `split` in the setting) puts the title and the
    button side by side.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree or `None` for generated
        pages.
    """
    del templatename, doctree
    options = app.config.html_context
    meta: dict[str, str] = context.get("meta") or {}
    site: dict[str, str] = setting(app.config, "feedback")
    email = options["km_project"]["email"]
    title = plain(context.get("title") or "")
    if meta.get("km-feedback-subject") or site.get("subject"):
        said = tidy(str(meta.get("km-feedback-subject") or site["subject"]))
        said = said.replace("%s", title)
    else:
        said = str(_("Feedback about %s")) % title
    url: str | None = None
    if email:
        url = f"mailto:{email}?subject={quote(said)}"
    if (meta.get("km-feedback-type") or site.get("type")) == "link":
        url = meta.get("km-feedback-url") or site.get("url") or url
    chosen = meta.get("km-feedback-icon") or site.get("icon")
    if "km-feedback-split" in meta and not url:
        fail(
            "field :km-feedback-split: needs somewhere to send feedback,"
            " there is no email or :km-feedback-url: for a button",
            str(app.env.doc2path(pagename)),
        )
    if url and setting(app.config, "show_feedback") is None:
        context["km_show_feedback"] = True
    context["km_feedback"] = {
        "split": toggle(meta["km-feedback-split"])
        if "km-feedback-split" in meta
        else bool(site.get("split")),
        "title": tidy(meta.get("km-feedback-title", ""))
        or site.get("title")
        or str(_("Feedback")),
        "description": tidy(meta.get("km-feedback-description", ""))
        or site.get("description")
        or str(_("Let me know how this can be improved.")),
        "button": tidy(meta.get("km-feedback-button", ""))
        or site.get("button")
        or str(_("Submit")),
        "icon": Icons.of(app.config).custom(chosen)
        or options["km_fa_icons"]["feedback"],
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
        if key == "show_more":
            continue
        field = "km-" + key.replace("_", "-")
        if field not in meta:
            continue
        context[f"km_{key}"] = toggle(meta[field])


def ensure_articles(env: BuildEnvironment) -> dict[str, set[str]]:
    """Hold the releases each article was linked from, making the store.

    :param env: The build environment.
    :return: The articles `release` links to, each with every page a
        release linking it is written on.
    """
    return stored(env, "articles", {})


def ensure_leads(env: BuildEnvironment) -> dict[str, str]:
    """Hold the lead of each page that has one, making the store.

    :param env: The build environment.
    :return: Each page's lead, keyed by its document name.
    """
    return stored(env, "leads", {})


def note_lead(app: Sphinx, doctree: nodes.document) -> None:
    """Keep a page's lead as it's read, for the header's dropdowns.

    :param app: The Sphinx application instance.
    :param doctree: The page's doctree.
    """
    lead = standfirst(doctree, HEADER_LEAD_LENGTH)
    if lead:
        ensure_leads(app.env)[app.env.docname] = lead


def forget_lead(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    """Forget a page's lead, as it's read again or removed.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param docname: The page about to be read again.
    """
    del app
    ensure_leads(env).pop(docname, None)


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
    ensure_leads(env).update(
        {
            name: lead
            for name, lead in ensure_leads(other).items()
            if name in docnames
        }
    )


LINK: t.Final[re.Pattern[str]] = re.compile(
    r'(<a [^>]*?href="([^"]*)"[^>]*>)(.*?)(</a>)', re.DOTALL
)


def header_leads(builder: StandaloneHTMLBuilder) -> dict[str, str]:
    """Work out what each page says under its title in the header.

    A page's own `:km-header-subtitle:` wins over everything, then its
    lead and last its `:km-page-description:`. A page with none of them is
    left out, as is one with `:km-header-no-subtitle:` and no subtitle.
    It is done once for the whole site and kept for the build.

    :param builder: The HTML builder.
    :return: Each page's words as the `km-header__lead` span that goes in
        its link, keyed by its document name.
    """
    env = builder.env
    found: dict[str, str] | None = builder.__dict__.get("km_header_leads")
    if found is None:
        found = {}
        for name in env.found_docs:
            fields = env.metadata.get(name, {})
            words = tidy(fields.get(HEADER_SUBTITLE_FIELD, ""))
            if not words and not (
                HEADER_NO_SUBTITLE_FIELD in fields
                and toggle(fields[HEADER_NO_SUBTITLE_FIELD])
            ):
                words = clip(
                    ensure_leads(env).get(name)
                    or tidy(fields.get("km-page-description", "")),
                    HEADER_LEAD_LENGTH,
                )
            if words:
                span = nodes.inline("", words, classes=["km-header__lead"])
                found[name] = builder.render_partial(span)["fragment"].strip()
        builder.__dict__["km_header_leads"] = found
    return found


def toctrees(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Give the page its two navigations, the header's and the sidebar's.

    Both are the site's toctree, so it is worked out and drawn once for
    the page and the header's copy gets each page's lead, as a
    `km-header__lead` span, under its title. The captions of the sidebar
    are given a heading level.

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
    drawn: dict[tuple[tuple[str, t.Any], ...], str] = {}

    def draw(**kwargs: t.Any) -> str:
        """Draw the toctree the way the page asked for it, once."""
        key = tuple(sorted(kwargs.items()))
        if key not in drawn:
            tree = global_toctree_for_doc(
                app.env, pagename, builder, tags=builder.tags, **kwargs
            )
            drawn[key] = builder.render_partial(tree)["fragment"]
        return drawn[key]

    def sidebar(**kwargs: t.Any) -> str:
        """Draw the sidebar's navigation, with Sphinx's defaults."""
        wanted = {"collapse": True, "includehidden": False, **kwargs}
        if wanted.get("maxdepth") == "":
            del wanted["maxdepth"]
        return levelled(draw(**wanted))

    def header(**kwargs: t.Any) -> str:
        """Draw the header's navigation with each page's lead."""
        spans = header_leads(builder)
        by_link = {
            builder.get_relative_uri(pagename, name) or "#": span
            for name, span in spans.items()
        }

        def add(found: re.Match[str]) -> str:
            """Put the lead of the page a link goes to inside the link."""
            span = by_link.get(unescape(found[2]), "")
            return f"{found[1]}{found[3]}{span}{found[4]}"

        return levelled(LINK.sub(add, draw(**kwargs)))

    context["toctree"] = sidebar
    context["km_header_toctree"] = header


def neighbours(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Let a page name its own previous and next pages.

    Sphinx works those out from the toctree, so a page in none of them,
    an orphan, gets neither. `:km-page-prev:` and `:km-page-next:` take a
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
    released = ensure_articles(app.env)
    for key in ("prev", "next"):
        target = (meta.get(f"km-page-{key}") or "").strip()
        if target:
            docname = docname_join(pagename, target)
        elif key == "prev" and not context.get(key) and pagename in released:
            docname = min(released[pagename])
        else:
            continue
        title = builder.render_partial(app.env.titles[docname])["title"]
        context[key] = {
            "link": builder.get_relative_uri(pagename, docname),
            "title": title,
        }


def related_docs(docname: str, meta: dict[str, str]) -> list[str]:
    """Work out the pages a page lists in `:km-related-docs:`.

    :param docname: The page that lists them.
    :param meta: The page's fields.
    :return: Their document names, as `:doc:` would write them, or none
        when the field is missing or is not one `pages` reads.
    """
    try:
        names = pages(meta.get("km-related-docs") or "")
    except ValueError:
        return []
    return [docname_join(docname, _) for _ in names]


def skipped(env: BuildEnvironment, docname: str) -> bool:
    """Say whether a page keeps itself out of other pages' cards.

    :param env: The build environment.
    :param docname: The page.
    :return: Whether it has `:km-related-skip-page:` on.
    """
    meta = env.metadata.get(docname, {})
    try:
        return "km-related-skip-page" in meta and toggle(
            meta["km-related-skip-page"]
        )
    except ValueError:
        return False


def reading_order(env: BuildEnvironment, docname: str) -> list[str]:
    """Work out the pages a reader meets next, as the next buttons would.

    The page's own `:km-page-next:` and `:km-page-prev:` come first, as
    they do for the buttons, then the toctree. The pages after it come
    first, nearest first, then the pages before it, nearest first, up to
    `kaamiki.conf.show.previous_next_cards_count` in all. So a page with
    none after it gets the five before it, and a small site gets the pages
    it has. The front page is never one of them, nor is a page with
    `:km-related-skip-page:`.

    :param env: The build environment.
    :param docname: The page.
    :return: Their document names, none for a page no toctree holds.
    """
    relations = env.collect_relations()
    meta = env.metadata.get(docname, {})
    released = ensure_articles(env)
    most = setting(env.config, "show_previous_next_cards_count")

    def first(key: str) -> str | None:
        """Give the page's own neighbour, its fields first."""
        target = (meta.get(f"km-page-{key}") or "").strip()
        if target:
            return docname_join(docname, target)
        found = relations.get(docname, (None, None, None))
        if key == "prev" and not found[1] and docname in released:
            return min(released[docname])
        return found[1 if key == "prev" else 2]

    def walk(key: str) -> list[str]:
        """Follow the toctree one way from the page's own neighbour."""
        found: list[str] = []
        seen: set[str] = set()
        here = first(key)
        while (
            here in env.found_docs
            and here != docname
            and here not in seen
            and len(found) < most
        ):
            seen.add(here)
            if here != env.config.root_doc and not skipped(env, here):
                found.append(here)
            here = relations.get(here, (None, None, None))[
                1 if key == "prev" else 2
            ]
        return found

    ahead = walk("next")
    return (ahead + [_ for _ in walk("prev") if _ not in ahead])[:most]


def captions(app: Sphinx) -> dict[str, str]:
    """Read the captions the front page's toctrees give their pages.

    :param app: The Sphinx application instance.
    :return: Each page a captioned toctree of the front page lists, with
        that caption. It is read once for a build.
    """
    found: dict[str, str] | None = app.builder.__dict__.get("km_captions")
    if found is None:
        found = {}
        tree = app.env.get_doctree(app.config.root_doc)
        for each in findall(tree, addnodes.toctree):
            for _title, name in each["entries"]:
                if each.get("caption") and name in app.env.found_docs:
                    found.setdefault(name, tidy(each["caption"]))
        app.builder.__dict__["km_captions"] = found
    return found


def section_of(app: Sphinx, docname: str) -> str:
    """Name the part of the site a page is in, the way the header does.

    That is the caption of the front page's toctree that lists the page
    or the nearest page above it that one lists.

    :param app: The Sphinx application instance.
    :param docname: The page.
    :return: The caption, or an empty string for the front page, a page
        no toctree holds and a toctree with no caption.
    """
    relations = app.env.collect_relations()
    home = app.config.root_doc
    here = docname
    while here != home:
        parent = relations.get(here, (None,))[0]
        if parent is None:
            return ""
        if parent == home:
            return captions(app).get(here, "")
        here = parent
    return ""


GLYPH: t.Final[re.Pattern[str]] = re.compile(
    r'<span aria-hidden="true" class="([^"]*km-glyph[^"]*)"></span>'
)
TAGS: t.Final[re.Pattern[str]] = re.compile(r"</?[A-Za-z][^<>]*>")


def title_parts(title: str) -> list[dict[str, str]]:
    """Split a page's rendered title into its words and its icons.

    A title is shown the way the header's menus show it: words only, with
    an icon where the title has one and every other role as plain text.

    :param title: The title as the builder rendered it.
    :return: The pieces in order, each with `text` or the `glyph` classes
        of an icon.
    """
    parts: list[dict[str, str]] = []
    here = 0
    for found in [*GLYPH.finditer(title), None]:
        end = found.start() if found else len(title)
        text = " ".join(unescape(TAGS.sub("", title[here:end])).split("\n"))
        text = re.sub(r"\s+", " ", text)
        if text.strip():
            parts.append({"text": text})
        if found:
            parts.append({"glyph": found.group(1)})
            here = found.end()
    if parts and "text" in parts[0]:
        parts[0]["text"] = parts[0]["text"].lstrip()
    if parts and "text" in parts[-1]:
        parts[-1]["text"] = parts[-1]["text"].rstrip()
    return parts


def related(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Give a page the cards `:km-related-docs:` asks for.

    A page with no `:km-related-docs:` gets the pages a reader meets
    next, as `reading_order` works them out, unless
    `kaamiki.conf.show.previous_next_cards` or its field is off or the
    previous and next buttons are on. A page with none to show gets no
    section.

    `km_related` holds the section's `header` (`:km-related-header:`, or
    the words "More to read." in the site's language) and a card for each
    page: its `link`, `title`, `section`, `date`
    and `image`. A card's image is the page's `:km-page-image:`, then
    its `:km-page-backdrop:`, else an empty string, which the template
    draws as waves. The date is the page's `created` date, written as
    every other date is, and is empty when the page has none. A page
    with `:km-related-skip-page:` is no card and has none. A page with
    cards leaves out the previous and next buttons.

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
    env = app.env
    if skipped(env, pagename):
        context["km_related"] = None
        return
    meta: dict[str, str] = context.get("meta") or {}
    context["km_related"] = None
    cards: list[dict[str, t.Any]] = []
    names = related_docs(pagename, meta)
    if (
        not names
        and context.get("km_show_previous_next_cards")
        and not context.get("km_show_previous_next_pages")
    ):
        names = reading_order(env, pagename)
    for docname in names:
        if skipped(env, docname):
            fail(
                f"field :km-related-docs: expected pages that can be listed,"
                f" got {docname!r}, which has :km-related-skip-page:",
                str(env.doc2path(pagename)),
            )
        other = env.metadata.get(docname, {})
        title = other.get("km-page-title") or builder.render_partial(
            env.titles[docname]
        ).get("title", "")
        image = (
            other.get("km-page-image") or other.get("km-page-backdrop") or ""
        )
        if image:
            image = context["pathto"](image.lstrip("/"), 1)
        iso = day(other.get("created", ""))
        cards.append(
            {
                "link": builder.get_relative_uri(pagename, docname),
                "title": plain(title),
                "parts": title_parts(title),
                "section": section_of(app, docname),
                "date": dated(datetime.fromisoformat(iso), app.config)
                if iso
                else "",
                "image": image,
            }
        )
    if cards:
        context["km_related"] = {
            "header": meta.get("km-related-header") or str(_("More to read.")),
            "cards": cards,
        }


def follow(
    app: Sphinx,
    env: BuildEnvironment,
    added: set[str],
    changed: set[str],
    removed: set[str],
) -> list[str]:
    """Send a page back through reading when a page it names changes.

    A page that names another with `:km-page-prev:`, `:km-page-next:` or
    `:km-related-docs:`, or is the article of a release, has that page's
    title written into it,
    so it is stale once the other is changed, moved or gone. Neighbours
    in a toctree are `retitled`.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param added: The pages Sphinx found new.
    :param changed: The pages Sphinx found changed.
    :param removed: The pages Sphinx found gone.
    :return: The pages whose `:km-page-prev:`, `:km-page-next:` or
        `:km-related-docs:` names a page that moved on, or whose release
        did.
    """
    del app
    moved = added | changed | removed
    stale: set[str] = set()
    for docname, meta in env.metadata.items():
        for key in ("km-page-prev", "km-page-next"):
            target = (meta.get(key) or "").strip()
            if target and docname_join(docname, target) in moved:
                stale.add(docname)
        if moved.intersection(related_docs(docname, meta)):
            stale.add(docname)
    for article, pages in ensure_articles(env).items():
        if pages & moved:
            stale.add(article)
    return sorted(stale - moved)


def retitled(app: Sphinx, env: BuildEnvironment) -> list[str]:
    """Send pages back to be written when what the navigation says
    changes.

    Every page's header lists every page with its title, its lead and its
    subtitle, and the previous and the next page's titles are written
    into a page, so a page is stale once any of them is changed, moved or
    gone. A page's related cards, the ones it lists and the ones it gets
    from the pages around it, show each page's title, picture and date
    and say which part of the site it is in, so it is stale once any of
    them changes. Sphinx only rewrites the
    pages whose own source changed.

    :param app: The Sphinx application instance.
    :param env: The build environment, whose pages are all read.
    :return: Every page when a page's title, lead, header subtitle or
        description isn't what it was at the last build, otherwise the
        pages whose previous or next page, or whose related cards,
        aren't what they were, the pages no toctree holds any more and
        the pages that list a page whose part of the site changed. None
        at the first build.
    """
    app.builder.__dict__.pop("km_captions", None)
    seen: dict[str, tuple[t.Any, ...]] = {}
    for docname, (_parent, before, after) in env.collect_relations().items():
        seen[docname] = tuple(
            (name, env.titles[name].astext()) if name in env.titles else None
            for name in (before, after)
        ) + tuple(
            (
                name,
                env.titles[name].astext() if name in env.titles else None,
                env.metadata.get(name, {}).get("km-page-title"),
                env.metadata.get(name, {}).get("km-page-image"),
                env.metadata.get(name, {}).get("km-page-backdrop"),
                env.metadata.get(name, {}).get("created"),
                section_of(app, name),
            )
            for name in reading_order(env, docname)
        )
    before_now = kept(env, "neighbours", seen) or {}
    listed = {
        name: (
            env.titles[name].astext() if name in env.titles else None,
            ensure_leads(env).get(name),
            *(
                env.metadata.get(name, {}).get(key)
                for key in (
                    HEADER_SUBTITLE_FIELD,
                    HEADER_NO_SUBTITLE_FIELD,
                    "km-page-description",
                )
            ),
        )
        for name in env.found_docs
    }
    navigation = json.dumps(listed, sort_keys=True)
    earlier = kept(env, "navigation", navigation)
    parts = {
        name: section_of(app, name)
        for docname, meta in env.metadata.items()
        for name in related_docs(docname, meta)
    }
    before_parts = kept(env, "sections", parts) or {}
    if earlier not in (None, navigation):
        return sorted(env.found_docs)
    moved = {
        _ for _, part in parts.items() if before_parts.get(_, part) != part
    }
    return sorted(
        {
            docname
            for docname, links in seen.items()
            if before_now.get(docname, links) != links
        }
        | {_ for _ in before_now if _ not in seen and _ in env.found_docs}
        | {
            docname
            for docname, meta in env.metadata.items()
            if moved.intersection(related_docs(docname, meta))
        }
    )
