"""\
Context Utilities
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 15 November 2026

The utilities that fill the context of a page for the templates. The
templates can use only these names: the settings that
`context_defaults` copies with a `km_` prefix, and `km_fa_icons`,
`km_fa_kit`, `km_fa_css`, `km_fa_integrity`, `km_project`,
`km_license`, `km_header_buttons`, `km_sidebar_buttons`,
`km_toctree_args`, `km_credit`, `km_credit_new_tab`, `km_rel` and
`km_site`. The handlers for each page also set `km_author`,
`km_feedback`, `km_header_toctree`, `km_social` and `km_updated_on`. A
template of a site that reads a different setting must read it itself.
"""

from __future__ import annotations

import difflib
import functools
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
from kaamiki.extensions.utils.hooks import on
from kaamiki.extensions.utils.icons import Icons
from kaamiki.extensions.utils.links import REL
from kaamiki.extensions.utils.links import opens_new_tab
from kaamiki.extensions.utils.settings import BOUNDS
from kaamiki.extensions.utils.settings import CARDS
from kaamiki.extensions.utils.settings import CREDIT
from kaamiki.extensions.utils.settings import FA_FREE
from kaamiki.extensions.utils.settings import FA_FREE_INTEGRITY
from kaamiki.extensions.utils.settings import HEADER_LEAD_LENGTH
from kaamiki.extensions.utils.settings import HEADER_NO_SUBHEADER_FIELD
from kaamiki.extensions.utils.settings import HEADER_SUBHEADER_FIELD
from kaamiki.extensions.utils.settings import OG_LOCALE
from kaamiki.extensions.utils.settings import OG_TYPE
from kaamiki.extensions.utils.settings import PAGE_SWITCHES
from kaamiki.extensions.utils.settings import PROJECT
from kaamiki.extensions.utils.settings import kept
from kaamiki.extensions.utils.settings import site_values
from kaamiki.extensions.utils.settings import stored
from kaamiki.extensions.utils.settings import validate
from kaamiki.extensions.utils.settings import values
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
    """Find the folder of `conf.py` without the application.

    :param env: The build environment.
    :return: The folder, as the last build that started had it.
    """
    return str(stored(env, "confdir", ""))


TEMPLATE_KEYS: t.Final[tuple[str, ...]] = (
    "colour_mode",
    "copy_headerlinks",
    "embed_js_loading",
    "favicons",
    "logo_size",
    "logos",
    "media_enlarge",
    "motion_page_transitions",
    "motion_prefetch",
    "motion_speed",
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


@on("builder-inited")
def context_defaults(app: Sphinx) -> None:
    """Fill the `html_context` keys that the templates expect.

    :param app: The Sphinx application instance. On `builder-inited`,
        this checks each setting with `validate`, records the folder of
        `conf.py`, and copies each setting for the templates with a
        `km_` prefix, so that a missing setting gives its default.
        `km_show_feedback` comes from the email of the project and the
        feedback link when `show_feedback` is not set. Kaamiki has no
        general index, so `html_use_index` goes off. The credit of
        Sphinx is hidden unless the site sets `html_show_sphinx`.
    """
    validate(app)
    kept(app.env, "confdir", str(app.confdir))
    config = app.config
    context: dict[str, t.Any] = config.html_context
    for key in TEMPLATE_KEYS:
        context[f"km_{key}"] = values(config)[key]
    icons = Icons.of(config)
    context["km_fa_icons"] = icons.roles(values(config).icons.names)
    context["km_fa_kit"] = icons.kit
    author = config.author
    if author == config.values["author"].default:
        author = ""
    project = {**PROJECT, "author": author, **values(config).site.project}
    context["km_project"] = project
    if context["km_show_feedback"] is None:
        context["km_show_feedback"] = bool(
            project["email"] or values(config).site.feedback.get("url")
        )
    depth = values(config).toctree.maxdepth
    context["km_toctree_args"] = {
        "includehidden": values(config).toctree.includehidden,
        **({"maxdepth": depth} if depth else {}),
    }
    terms = values(config).site.license
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
            for text, button in values(config)[key].items()
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
            "html_use_index: expected False or nothing, got True; Kaamiki"
            " has no page for the general index, so it's left off. Leave"
            " html_use_index out of conf.py",
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
        "km-header-no-subheader",
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
RELATED_MOST: t.Final[int] = int(BOUNDS["show_previous_next_cards_count"][1])


def pages(argument: str) -> list[str]:
    """Read the pages that `:km-related-docs:` names.

    :param argument: The pages as written, as for a toctree.
    :return: The name of each page, trimmed.
    :raises ValueError: For a blank name (a comma at the end is one) or
        more than `RELATED_MOST` pages. `page_fields` refuses a page
        named two times, after it resolves the names.
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
    "km-header-subheader": functools.partial(checks.text, maximum=120),
    "km-page-backdrop": checks.picture,
    "km-page-card": checks.word(*CARDS),
    "km-page-description": functools.partial(checks.text, maximum=300),
    "km-page-image": checks.link,
    "km-page-image-alt": checks.text,
    "km-page-language": checks.language,
    "km-page-locale": OG_LOCALE,
    "km-page-next": checks.text,
    "km-page-prev": checks.text,
    "km-page-robots": lambda _: [
        checks.word(*ROBOTS)(each.strip()) for each in _.split(",")
    ],
    "km-page-title": functools.partial(checks.text, maximum=120),
    "km-page-type": OG_TYPE,
    "km-related-docs": pages,
    "km-related-header": functools.partial(checks.text, maximum=120),
}


@on("doctree-read", priority=300)
def field_lists(app: Sphinx, doctree: nodes.document) -> None:
    """Stop for a `:km-*:` field written two times or below the title.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read. This runs on `doctree-read` at
        priority 300, before the metadata collector of Sphinx at 500
        removes the field list, and it records where each field is for
        `page_fields`.
    :raises KaamikiError: For the first field of that kind.
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


@on("doctree-read", priority=200)
def page_title(app: Sphinx, doctree: nodes.document) -> None:
    """Stop for a page without a title that has words.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read.
    :raises KaamikiError: For a page without a title, or with only an
        icon. The title names the page in the tab, the navigation, the
        cards, the search and the link preview.
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


@on("doctree-read", priority=200)
def admonition_title(app: Sphinx, doctree: nodes.document) -> None:
    """Stop for a custom admonition whose title has no words.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read.
    :raises KaamikiError: For an `admonition` without a title that has
        words. Only `admonition` is named by its title. The admonitions
        of docutils, as `note` and `warning`, are named by their kind
        and can show only their icon.
    """
    del app
    for node in findall(doctree, nodes.admonition):
        if type(node) is not nodes.admonition:
            continue
        heading = node[0] if node.children else None
        if (
            not isinstance(heading, nodes.title)
            or not heading.astext().strip()
        ):
            fail(
                "admonition: expected a title with words, got only an icon"
                " or nothing",
                location(node),
            )


@on("doctree-read", priority=600)
def page_fields(app: Sphinx, doctree: nodes.document) -> None:  # noqa: ARG001
    """Check the `:km-*:` fields at the start of a page.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read. This runs on `doctree-read` at
        priority 600, after the metadata collector of Sphinx at 500
        fills `env.metadata`. A page with `noindex` or `none` in
        `:km-page-robots:` is also removed from the search of the site,
        through `nosearch`.
    :raises KaamikiError: For a `km-` field that Kaamiki does not read,
        a value that it does not take, or fields that do not go
        together.
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
        email = values(app.config).site.project.get("email")
        site = values(app.config).site.feedback.get("url")
        if not (email or site or found.get("km-feedback-url")):
            fail(
                "field :km-show-feedback: expected an email in"
                " kaamiki.conf.site.project, a url in"
                " kaamiki.conf.site.feedback or :km-feedback-url: on the page"
                " to send feedback to, got none",
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
            "field :km-related-docs: expected without"
            " :km-related-skip-page:, which gives the page no cards, got both",
            places.get("km-related-docs", where),
        )
    if "km-related-docs" in found:
        field = "km-show-previous-next-cards"
        if field in found and not toggle(found[field]):
            fail(
                "field :km-related-docs: expected without"
                f" :{field}: false, which turns the cards off, got both",
                places.get("km-related-docs", where),
            )
        if (
            field not in found
            and not values(app.config).show.previous_next_cards
        ):
            fail(
                "field :km-related-docs: expected"
                " kaamiki.conf.show.previous_next_cards to be True, got False",
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


@on("html-page-context")
def feedback(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Find what the feedback box of a page says and where it links.

    :param app: The Sphinx application instance. The fields
        `:km-feedback-*:` of the page come first, then
        `kaamiki.conf.site.feedback`, then the words of Kaamiki. The
        button sends an email to the address in
        `kaamiki.conf.site.project`, or links where the page or the
        setting tells. A site without an email and without a link has
        no box, but a page with its own link has one.
        `:km-feedback-split:` (or `split` in the setting) puts the
        title and the button next to each other.
    :param pagename: The page that is written.
    :param templatename: The template that writes it.
    :param context: The context of the page, changed in place.
    :param doctree: The resolved doctree, or `None` for a generated
        page.
    """
    del templatename, doctree
    options = app.config.html_context
    meta: dict[str, str] = context.get("meta") or {}
    site: dict[str, str] = values(app.config).site.feedback
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
            " there's no email or :km-feedback-url: for a button",
            str(app.env.doc2path(pagename)),
        )
    if url and values(app.config).show.feedback is None:
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
        or str(_("Tell us how this page can be improved.")),
        "button": tidy(meta.get("km-feedback-button", ""))
        or site.get("button")
        or str(_("Submit")),
        "icon": Icons.of(app.config).custom(chosen)
        or options["km_fa_icons"]["feedback"],
        "url": url,
    }


@on("html-page-context")
def page_switches(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Let a page switch a setting on or off for itself.

    :param app: The Sphinx application instance. The switches are the
        `show_*` settings, `toctree_in_header` and `media_enlarge`,
        each with the `:km-*:` field of the same name.
    :param pagename: The page that is written.
    :param templatename: The template that writes it.
    :param context: The context of the page, changed in place.
    :param doctree: The resolved doctree, or `None` for a generated
        page.
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
    """Hold the releases that link each article, and make the store.

    :param env: The build environment.
    :return: The articles that `release` links to, each with the pages
        of the releases that link it.
    """
    return stored(env, "articles", {})


def ensure_leads(env: BuildEnvironment) -> dict[str, str]:
    """Hold the lead of each page that has one.

    :param env: The build environment.
    :return: The lead of each page, by its document name.
    """
    return stored(env, "leads", {})


@on("doctree-read")
def note_lead(app: Sphinx, doctree: nodes.document) -> None:
    """Keep the lead of a page for the menus of the header.

    :param app: The Sphinx application instance.
    :param doctree: The doctree of the page.
    """
    lead = standfirst(doctree, HEADER_LEAD_LENGTH)
    if lead:
        ensure_leads(app.env)[app.env.docname] = lead


@on("env-purge-doc")
def forget_lead(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    """Forget the lead of a page when it is read again or removed.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param docname: The page that is read again.
    """
    del app
    ensure_leads(env).pop(docname, None)


@on("env-merge-info")
def merge_leads(
    app: Sphinx,
    env: BuildEnvironment,
    docnames: set[str],
    other: BuildEnvironment,
) -> None:
    """Take the leads that a parallel reader found.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param docnames: The pages that the reader read.
    :param other: The build environment of the reader.
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
    """Find the text below the title of each page in the header.

    :param builder: The HTML builder.
    :return: The text of each page as the `km-header__lead` span in its
        link, by document name. `:km-header-subheader:` comes first,
        then the lead, then `:km-page-description:`. A page without
        them is not included, as is a page with
        `:km-header-no-subheader:` and no subheader. This is done one
        time for the site and kept for the build.
    """
    env = builder.env
    found: dict[str, str] | None = builder.__dict__.get("km_header_leads")
    if found is None:
        found = {}
        for name in env.found_docs:
            fields = env.metadata.get(name, {})
            words = tidy(fields.get(HEADER_SUBHEADER_FIELD, ""))
            if not words and not (
                HEADER_NO_SUBHEADER_FIELD in fields
                and toggle(fields[HEADER_NO_SUBHEADER_FIELD])
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


@on("html-page-context")
def toctrees(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Give the page the navigations of the header and sidebar.

    :param app: The Sphinx application instance. The two use the
        toctree of the site, so it is drawn one time for each page. The
        copy for the header gets the lead of each page below its title,
        and the captions of the sidebar get a heading level.
    :param pagename: The page that is written.
    :param templatename: The template that writes it.
    :param context: The context of the page, changed in place.
    :param doctree: The resolved doctree, or `None` for a generated
        page.
    """
    del templatename, doctree
    builder = app.builder
    if not isinstance(builder, StandaloneHTMLBuilder):
        return
    drawn: dict[tuple[tuple[str, t.Any], ...], str] = {}

    def draw(**kwargs: t.Any) -> str:
        """Draw the toctree as the page asks for it, one time.

        :param kwargs: The arguments of `toctree` in the template.
        :return: The HTML of the toctree.
        """
        key = tuple(sorted(kwargs.items()))
        if key not in drawn:
            tree = global_toctree_for_doc(
                app.env, pagename, builder, tags=builder.tags, **kwargs
            )
            drawn[key] = builder.render_partial(tree)["fragment"]
        return drawn[key]

    def sidebar(**kwargs: t.Any) -> str:
        """Draw the navigation of the sidebar.

        :param kwargs: The arguments of `toctree` in the template.
        :return: The HTML of the navigation.
        """
        wanted = {"collapse": True, "includehidden": False, **kwargs}
        if wanted.get("maxdepth") == "":
            del wanted["maxdepth"]
        return levelled(draw(**wanted))

    def header(**kwargs: t.Any) -> str:
        """Draw the navigation of the header, with leads.

        :param kwargs: The arguments of `toctree` in the template.
        :return: The HTML of the navigation.
        """
        spans = header_leads(builder)
        by_link = {
            builder.get_relative_uri(pagename, name) or "#": span
            for name, span in spans.items()
        }

        def add(found: re.Match[str]) -> str:
            """Put the lead of the linked page in the link.

            :param found: The link, matched in the HTML.
            :return: The link with the lead in it.
            """
            span = by_link.get(unescape(found[2]), "")
            return f"{found[1]}{found[3]}{span}{found[4]}"

        return levelled(LINK.sub(add, draw(**kwargs)))

    context["toctree"] = sidebar
    context["km_header_toctree"] = header


@on("html-page-context")
def neighbours(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Let a page name its previous and next pages.

    :param app: The Sphinx application instance. Sphinx finds them from
        the toctree, so a page in no toctree gets none.
        `:km-page-prev:` and `:km-page-next:` take a document, as
        `:doc:` writes it, and have priority over the toctree. An
        article that a `release` links to, without a previous page,
        links back to the page of the release.
    :param pagename: The page that is written.
    :param templatename: The template that writes it.
    :param context: The context of the page, changed in place.
    :param doctree: The resolved doctree, or `None` for a generated
        page.
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
    """Find the pages that a page lists in `:km-related-docs:`.

    :param docname: The page that lists them.
    :param meta: The fields of the page.
    :return: Their document names, as `:doc:` writes them, or none when
        the field is missing or `pages` cannot read it.
    """
    try:
        names = pages(meta.get("km-related-docs") or "")
    except ValueError:
        return []
    return [docname_join(docname, _) for _ in names]


def skipped(env: BuildEnvironment, docname: str) -> bool:
    """Say whether a page keeps itself out of the cards of other pages.

    :param env: The build environment.
    :param docname: The page.
    :return: `True` when `:km-related-skip-page:` is on.
    """
    meta = env.metadata.get(docname, {})
    try:
        return "km-related-skip-page" in meta and toggle(
            meta["km-related-skip-page"]
        )
    except ValueError:
        return False


def reading_order(env: BuildEnvironment, docname: str) -> list[str]:
    """Find the pages that a reader goes to next.

    :param env: The build environment.
    :param docname: The page.
    :return: Their document names, or none for a page that no toctree
        holds. `:km-page-next:` and `:km-page-prev:` come first, then
        the toctree. The pages after the page come first, nearest
        first, then the pages before it, to a total of
        `kaamiki.conf.show.previous_next_cards_count`. The front page
        and a page with `:km-related-skip-page:` are not included.
    """
    relations = env.collect_relations()
    meta = env.metadata.get(docname, {})
    released = ensure_articles(env)
    most = values(env.config).show.previous_next_cards_count

    def first(key: str) -> str | None:
        """Give the neighbour of the page, from its fields first.

        :param key: `prev` or `next`.
        :return: The document name, or `None` when there is none.
        """
        target = (meta.get(f"km-page-{key}") or "").strip()
        if target:
            return docname_join(docname, target)
        found = relations.get(docname, (None, None, None))
        if key == "prev" and not found[1] and docname in released:
            return min(released[docname])
        return found[1 if key == "prev" else 2]

    def walk(key: str) -> list[str]:
        """Follow the toctree in one direction.

        :param key: `prev` or `next`.
        :return: The document names, nearest first.
        """
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
    """Read the captions of the toctrees of the front page.

    :param app: The Sphinx application instance.
    :return: Each page in a toctree of the front page that has a
        caption, with that caption. This is read one time for each
        build.
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
    """Name the part of the site that a page is in, as the header does.

    :param app: The Sphinx application instance.
    :param docname: The page.
    :return: The caption of the toctree of the front page that lists
        the page, or the nearest page above it. An empty string for the
        front page, a page in no toctree, and a toctree without a
        caption.
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
    """Split the rendered title of a page into its words and its icons.

    :param title: The title as the builder rendered it.
    :return: The parts in sequence, each with `text` or with the
        `glyph` classes of an icon. Only the words and the icons stay,
        as in the menus of the header. Other roles become plain text.
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


@on("html-page-context")
def related(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Give a page the cards that `:km-related-docs:` asks for.

    :param app: The Sphinx application instance. Without
        `:km-related-docs:`, the page gets the pages from
        `reading_order`, unless `kaamiki.conf.show.previous_next_cards`
        or its field is off, or the previous and next buttons are on. A
        page without cards gets no section. `km_related` holds the
        `header` of the section (`:km-related-header:`, or "More to
        read." in the language of the site) and a card for each page,
        with its `link`, `title`, `section`, `date` and `image`. The
        image is `:km-page-image:`, then `:km-page-backdrop:`, else an
        empty string, which the template draws as waves. The date is
        the `created` date of the page, or empty. A page with
        `:km-related-skip-page:` is not a card and gets none. A page
        with cards does not show the previous and next buttons.
    :param pagename: The page that is written.
    :param templatename: The template that writes it.
    :param context: The context of the page, changed in place.
    :param doctree: The resolved doctree, or `None` for a generated
        page.
    """
    del templatename, doctree
    builder = app.builder
    if not isinstance(builder, StandaloneHTMLBuilder):
        return
    env = app.env
    context["km_related"] = None
    if skipped(env, pagename):
        return
    meta: dict[str, str] = context.get("meta") or {}
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


@on("env-get-outdated")
def follow(
    app: Sphinx,
    env: BuildEnvironment,
    added: set[str],
    changed: set[str],
    removed: set[str],
) -> list[str]:
    """Read a page again when a page that it names changes.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param added: The pages that Sphinx found new.
    :param changed: The pages that Sphinx found changed.
    :param removed: The pages that Sphinx found removed.
    :return: The pages whose `:km-page-prev:`, `:km-page-next:` or
        `:km-related-docs:` names a page that changed, moved or was
        removed, and the articles whose release did. These pages have
        the title of the other page in them. `retitled` handles the
        neighbours in a toctree.
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


@on("env-updated")
def retitled(app: Sphinx, env: BuildEnvironment) -> list[str]:
    """Write pages again when the navigation changes.

    :param app: The Sphinx application instance.
    :param env: The build environment, with all pages read.
    :return: Each page when the title, lead, header subheader or
        description of a page changed since the last build, because the
        header of each page lists them. Else the pages whose previous
        or next page or related cards changed, the pages that no
        toctree holds now, and the pages that list a page whose part of
        the site changed. Nothing at the first build. Sphinx itself
        only writes again the pages whose source changed.
    """
    app.builder.__dict__.pop("km_captions", None)
    app.builder.__dict__.pop("km_header_leads", None)
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
                    HEADER_SUBHEADER_FIELD,
                    HEADER_NO_SUBHEADER_FIELD,
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
