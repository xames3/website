"""\
Context Utilities
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 25 October 2026

The utilities that fill a page's context for the templates.
"""

import difflib
import typing as t
from urllib.parse import quote

from docutils import nodes
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.environment.adapters.toctree import global_toctree_for_doc
from sphinx.locale import _
from sphinx.util import docname_join

from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils.checks import fail
from kaamiki.extensions.utils.checks import location
from kaamiki.extensions.utils.directives import toggle
from kaamiki.extensions.utils.doctree import findall
from kaamiki.extensions.utils.doctree import standfirst
from kaamiki.extensions.utils.links import REL
from kaamiki.extensions.utils.links import opens_new_tab
from kaamiki.extensions.utils.settings import CARDS
from kaamiki.extensions.utils.settings import CREDIT
from kaamiki.extensions.utils.settings import DEFAULTS
from kaamiki.extensions.utils.settings import HEADER_LEAD_LENGTH
from kaamiki.extensions.utils.settings import HEADER_NO_SUBTITLE_FIELD
from kaamiki.extensions.utils.settings import HEADER_SUBTITLE_FIELD
from kaamiki.extensions.utils.settings import ICONS
from kaamiki.extensions.utils.settings import PAGE_SWITCHES
from kaamiki.extensions.utils.settings import PROJECT
from kaamiki.extensions.utils.settings import RENAMED
from kaamiki.extensions.utils.settings import icon
from kaamiki.extensions.utils.settings import icon_style
from kaamiki.extensions.utils.settings import pro
from kaamiki.extensions.utils.settings import setting
from kaamiki.extensions.utils.settings import validate
from kaamiki.extensions.utils.text import clip
from kaamiki.extensions.utils.text import plain
from kaamiki.extensions.utils.text import tidy

if t.TYPE_CHECKING:
    from collections.abc import Callable

    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment


def context_defaults(app: Sphinx) -> None:
    """Fill in the `html_context` keys the templates expect.

    Every setting in `DEFAULTS` is copied with a `km_` prefix, which is
    the only one the templates read, so one that's missing is its
    default and not an `UndefinedError`. The ones that need more than a
    copy are worked out after.

    This runs on `builder-inited` and not `config-inited`, which has
    gone by the time a theme picked through `html_theme` alone is set
    up.

    :param app: The Sphinx application instance.
    """
    validate(app)
    config = app.config
    context: dict[str, t.Any] = config.html_context
    for key in DEFAULTS:
        context[f"km_{key}"] = setting(config, key)
    icons: dict[str, str] = context["km_fa_icons"]
    if not setting(config, "fa_kit"):
        icons = {key: _ for key, _ in icons.items() if not pro(_)}
    context["km_fa_icons"] = {
        **ICONS,
        **{key: icon(_) for key, _ in icons.items()},
    }
    context["km_fa_style"] = icon_style(config)
    project = {**PROJECT, "author": config.author, **context["km_project"]}
    context["km_project"] = project
    if context["km_show_feedback"] is None:
        context["km_show_feedback"] = bool(
            project["email"] or context["km_feedback"].get("url")
        )
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
    # NOTE(xames3): Kaamiki has no page for the general index. The builder
    # read the setting before this runs, so it is told as well.
    config.html_use_index = False
    if isinstance(app.builder, StandaloneHTMLBuilder):
        app.builder.use_index = False
    if "html_show_sphinx" not in config._raw_config | config._overrides:
        context.setdefault("show_sphinx", False)


SWITCHES: t.Final[frozenset[str]] = frozenset(
    {
        "km-fb-split",
        "km-header-no-subtitle",
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
FIELDS: t.Final[dict[str, Callable[[str], t.Any]]] = {
    "km-fb-button": checks.text,
    "km-fb-description": checks.text,
    "km-fb-icon": checks.icon,
    "km-fb-subject": checks.text,
    "km-fb-title": checks.text,
    "km-fb-type": checks.word("mail", "link"),
    "km-fb-url": checks.link,
    "km-header-subtitle": lambda _: checks.text(_, 120),
    "km-pg-card": checks.word(*CARDS),
    "km-pg-description": lambda _: checks.text(_, 300),
    "km-pg-image": checks.link,
    "km-pg-image-alt": checks.text,
    "km-pg-locale": checks.pattern(
        r"[a-z]{2,3}_[A-Z]{2}", "a locale like en_GB"
    ),
    "km-pg-next": checks.text,
    "km-pg-prev": checks.text,
    "km-pg-robots": lambda _: [
        checks.word(*ROBOTS)(each.strip()) for each in _.split(",")
    ],
    "km-pg-title": lambda _: checks.text(_, 120),
    "km-pg-type": checks.pattern(
        r"[a-z]+(?:\.[a-z_]+)?", "an Open Graph type like article"
    ),
}


def field_lists(app: Sphinx, doctree: nodes.document) -> None:
    """Stop for a `:km-*:` field that is written twice or isn't one of
    the fields a page opens with.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read.
    :raises KaamikiError: For the first such field.
    """
    del app
    info = next(findall(doctree, nodes.docinfo), None)
    seen: set[str] = set()
    for field in findall(doctree, nodes.field):
        name = field[0].astext()
        if not name.startswith("km-"):
            continue
        if info is None or field.parent is not info:
            fail(
                f"field :{name}: belongs above the page title, with the "
                "page's other fields",
                location(field),
            )
        if name in seen:
            fail(f"field :{name}: is written twice", location(field))
        seen.add(name)


def page_fields(app: Sphinx, doctree: nodes.document) -> None:  # noqa: ARG001
    """Check the `:km-*:` fields a page opens with.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read.
    :raises KaamikiError: For a `km-` field Kaamiki doesn't read, a
        value it doesn't take or fields that don't go together.
    """
    docname = app.env.docname
    found = app.env.metadata.get(docname, {})
    where = str(app.env.doc2path(docname))
    for key, value in found.items():
        if not key.startswith("km-") or key == "km-pg-background":
            continue
        try:
            if key in SWITCHES:
                toggle(value)
            elif key in FIELDS:
                FIELDS[key](value)
            elif key.removeprefix("km-") in {
                _.replace("_", "-") for _ in RENAMED
            }:
                fail(f"field :{key}: was renamed :km-toctree-in-header:", where)
            else:
                known = sorted([*FIELDS, *SWITCHES])
                near = difflib.get_close_matches(key, known, n=1, cutoff=0.7)
                fail(
                    f"field :{key}: is not one Kaamiki reads"
                    + (f", did you mean :{near[0]}:" if near else ""),
                    where,
                )
        except ValueError as error:
            fail(f"field :{key}: {error}", where)
    kind = found.get("km-fb-type")
    if ("km-fb-url" in found) != (kind == "link"):
        fail(
            "field :km-fb-url: requires :km-fb-type: link and the reverse",
            where,
        )
    for key in ("km-pg-prev", "km-pg-next"):
        if key in found:
            target = docname_join(docname, found[key].strip())
            if target == docname or target not in app.env.found_docs:
                fail(
                    f"field :{key}: expected another page, got {found[key]!r}",
                    where,
                )


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
            meta.get("km-fb-icon") or site.get("icon"),
            icons["feedback"],
            kit=bool(setting(app.config, "fa_kit")),
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
