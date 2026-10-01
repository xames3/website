"""\
Theme Utilities
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February, 2025
Last updated on: 30 September, 2026

The theme's shared helpers. They fall into four groups: rendering a
directive's template, reading things off the doctree (a lead, a
description, a reading time), filling in the page context and writing
the 404 page once the build is done.
"""

from __future__ import annotations

import functools
import os
import os.path as p
import posixpath
import re
import typing as t
from datetime import datetime as dt
from html import escape
from html import unescape
from math import ceil
from subprocess import DEVNULL
from subprocess import CalledProcessError
from subprocess import check_output as co
from urllib.parse import parse_qs
from urllib.parse import quote
from urllib.parse import urlsplit

import bs4
import jinja2
from docutils import nodes
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.locale import _

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

TEMPLATES: t.Final[str] = p.join(
    p.dirname(p.dirname(p.realpath(__file__))), "base", "templates"
)
HEADER_RE: re.Pattern[str] = re.compile(
    r"^\.\.\s+(Author|Created on|Last updated on):\s*(.+)$", re.IGNORECASE
)
TAG_RE: re.Pattern[str] = re.compile(r"</?[A-Za-z][^<>]*>")
FURNITURE: tuple[type, ...] = (
    nodes.Admonition,
    nodes.figure,
    nodes.literal_block,
    nodes.table,
    nodes.topic,
)
WORDS_PER_MINUTE: t.Final[int] = 225
SHOW_MORE_AFTER: t.Final[int] = 5
NOT_FOUND: t.Final[str] = "404"
ROOTED_ATTRIBUTES: t.Final[tuple[str, ...]] = (
    "action",
    "data-content_root",
    "href",
    "src",
)
ROOTED_SKIP: t.Final[tuple[str, ...]] = ("#", "/", "data:", "mailto:", "tel:")
PROJECT: t.Final[dict[str, str]] = {
    "author": "",
    "avatar": "",
    "email": "",
    "source": "#",
}
ICONS: t.Final[dict[str, str]] = {
    "breadcrumb_home": "fa-solid fa-house",
    "breadcrumb_separator_child": "fa-solid fa-angle-right",
    "breadcrumb_separator_parent": "fa-solid fa-angles-right",
    "copy_url": "fa-solid fa-link",
    "dark_mode": "fa-solid fa-moon",
    "external_link": "fa-solid fa-arrow-up-right-from-square",
    "feedback": "fa-solid fa-paper-plane",
    "light_mode": "fa-solid fa-sun",
    "menu": "fa-solid fa-bars",
    "next_button": "fa-solid fa-arrow-right",
    "permalink": "fa-solid fa-link",
    "previous_button": "fa-solid fa-arrow-left",
    "reading_time": "fa-regular fa-clock",
    "search": "fa-solid fa-magnifying-glass",
    "show_more": "fa-solid fa-chevron-down",
    "title_badge": "fa-solid fa-circle-check",
}
FEEDBACK: t.Final[dict[str, t.Any]] = {
    "title": _("Feedback"),
    "description": _("Let me know how this can be improved."),
    "button": _("Submit"),
}
SETTINGS: t.Final[tuple[str, ...]] = (
    "add_copy_to_headerlinks",
    "colour_mode",
    "fa_css",
    "fa_icons",
    "fa_kit",
    "fa_style",
    "favicons",
    "header_buttons",
    "open_graph",
    "open_links_in_new_tab",
    "project",
    "show_404",
    "show_breadcrumbs",
    "show_colour_modes",
    "show_feedback",
    "show_last_updated_on",
    "show_more_after",
    "show_previous_next_pages",
    "show_scrolltop",
    "show_searchbox",
    "show_show_more",
    "show_sitemap",
    "show_toctree",
    "sidebar_buttons",
)
SWITCHES: t.Final[dict[str, bool]] = {
    "show_breadcrumbs": True,
    "show_last_updated_on": True,
    "show_previous_next_pages": True,
    "show_searchbox": True,
    "show_toctree": True,
}
GENERATED: t.Final[dict[str, t.Any]] = {
    NOT_FOUND: _(
        "There is nothing at this address. It may have moved, or it may"
        " never have been here."
    ),
    "genindex": _("Every term indexed on this site, from A to Z."),
    "search": _("Search every page on this site."),
}
TITLES: t.Final[dict[str, t.Any]] = {
    NOT_FOUND: _("Page not found"),
    "genindex": _("Index"),
    "search": _("Search Results"),
}
FA_STYLE: t.Final[str] = "solid"
FA_FREE: t.Final[str] = (
    "https://ka-f.fontawesome.com/releases/v7.3.1/css/free.min.css"
)
YOUTUBE_ID: re.Pattern[str] = re.compile(r"^[\w-]{11}$")
YOUTUBE_HOSTS: t.Final[frozenset[str]] = frozenset(
    {"youtube.com", "youtube-nocookie.com", "music.youtube.com"}
)
YOUTUBE_PATHS: t.Final[frozenset[str]] = frozenset(
    {"embed", "live", "shorts", "v"}
)
LINKCHECK_OPTIONS: tuple[str, ...] = ("avatar", "background", "target")
DESIGN_ASSETS: t.Final[frozenset[str]] = frozenset(
    {"design-tabs.js", "sphinx-design.min.css"}
)
environment: jinja2.Environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES),
    autoescape=True,
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=False,
    extensions=["jinja2.ext.i18n"],
)
environment.install_null_translations(newstyle=True)  # type: ignore[attr-defined]


def render(template: str, /, **context: t.Any) -> str:
    """Render one of the theme's directive templates.

    Every directive shares this one environment, which has autoescaping
    on. `bridge` points its loader at the builder's own, so a template
    is looked up the way Sphinx looks up a page's.

    Every value reaches the template under a `km_` name, so a template
    tells the theme's own names from Sphinx's at a glance, while the
    options keep the names the rST writes them with.

    :param template: Template filename, relative to `base/templates`.
    :param context: Values made available to the template.
    :return: The rendered HTML.
    """
    values = {f"km_{key}": value for key, value in context.items()}
    return environment.get_template(template).render(**values)


def bridge(app: Sphinx) -> None:
    """Look directive templates up where Sphinx looks its own up.

    The builder's loader searches `templates_path` first, then the
    theme, then whatever theme it inherits from, so a site or a theme
    built on this one can replace `author.html.jinja` and the rest the
    way it would replace `layout.html`. The theme's own directory comes
    last, for a builder that uses another theme altogether. The
    environment stays the theme's, so escaping and whitespace handling
    are what they were. It takes the build's translations too, so `_()`
    in a directive template reads in the site's `language`.

    :param app: The Sphinx application instance.
    """
    environment.install_gettext_translations(app.translator, newstyle=True)  # type: ignore[attr-defined]
    theme = jinja2.FileSystemLoader(TEMPLATES)
    templates = getattr(app.builder, "templates", None)
    if not isinstance(templates, jinja2.BaseLoader):
        environment.loader = theme
        return
    environment.loader = jinja2.ChoiceLoader([templates, theme])
    sphinx = getattr(templates, "environment", None)
    for name, value in getattr(sphinx, "filters", {}).items():
        environment.filters.setdefault(name, value)


def depart(self: HTMLTranslator, node: nodes.Element) -> None:
    """Close a node that has nothing to close.

    `add_node` wants a visit/depart pair, but a directive that writes
    its whole widget during `visit` has nothing left to do. They share
    this instead of each carrying an empty function.

    :param self: The HTML translator instance.
    :param node: The node being departed.
    """


def skip(self: nodes.NodeVisitor, node: nodes.Element) -> None:
    """Leave a node out of a builder that has no use for it.

    A byline or a picture is HTML furniture. A PDF, a man page or plain
    text writes the prose around it and nothing for it.

    :param self: The translator.
    :param node: The node being skipped.
    :raises nodes.SkipNode: Always.
    """
    raise nodes.SkipNode


def findall[T: nodes.Element](
    node: nodes.Node,
    element: type[T],
) -> Iterator[T]:
    """Walk a doctree for every node of one type.

    :param node: Where to start looking.
    :param element: The node type to look for.
    :return: Every match, in document order.
    """
    return t.cast("Iterator[T]", node.findall(element))


def themed(builder: object) -> bool:
    """Say whether a builder writes its pages with this theme.

    A theme built on this one counts too, since its directories carry
    this one's templates.

    :param builder: The builder, of any kind.
    :return: `True` when this theme's templates are among its theme's.
    """
    theme = getattr(builder, "theme", None)
    if theme is None:
        return False
    return any(p.realpath(_) == TEMPLATES for _ in theme.get_theme_dirs())


def icon(value: str | None, fallback: str = "") -> str:
    """Spell out a Font Awesome icon in full.

    `video`, `fa-video` and `fa-solid fa-video` all work. A lone name
    is given the solid style, which is the one Font Awesome Free has
    for every icon.

    :param value: The icon as written, or `None` when unset.
    :param fallback: The icon to use when there is not one.
    :return: The icon's classes, or an empty string for no icon.
    """
    parts = (value or fallback).split()
    if len(parts) == 1:
        name = parts[0] if parts[0].startswith("fa-") else f"fa-{parts[0]}"
        parts = ["fa-solid", name]
    return " ".join(parts)


def youtube_id(url: str) -> str | None:
    """Find the video id in a YouTube link.

    Watch pages with the id anywhere in the query, `youtu.be` short
    links and the `embed`, `shorts`, `live` and `v` paths all work, as
    does the bare id.

    :param url: The link, as written.
    :return: The eleven character id, or `None` when there is not one.
    """
    parts = urlsplit(url.strip())
    host = parts.netloc.lower().removeprefix("www.").removeprefix("m.")
    segments = [_ for _ in parts.path.split("/") if _]
    found = ""
    if (not host and len(segments) == 1) or (host == "youtu.be" and segments):
        found = segments[0]
    elif host in YOUTUBE_HOSTS and segments[:1] == ["watch"]:
        found = parse_qs(parts.query).get("v", [""])[0]
    elif host in YOUTUBE_HOSTS and len(segments) > 1:
        found = segments[1] if segments[0] in YOUTUBE_PATHS else ""
    return found if YOUTUBE_ID.match(found) else None


def elsewhere(url: str, site: str) -> bool:
    """Say whether a link leaves the site.

    A link leaves when it names a host other than the one in
    `html_baseurl`, `www.` aside. A relative link, one to the site's own
    address and a `mailto:` all stay, so none of them opens a new tab.
    A link too malformed to read counts as leaving, which is what every
    external link did before.

    :param url: The link, as written.
    :param site: The site's own address, `html_baseurl`.
    :return: Whether the link goes to another site.
    """
    try:
        host = urlsplit(url).hostname
        home = urlsplit(site).hostname or ""
    except ValueError:
        return True
    if not host:
        return False
    return host.removeprefix("www.") != home.removeprefix("www.")


def trail(options: dict[str, t.Any]) -> list[nodes.Node]:
    """Give `linkcheck` the URLs a directive keeps in its options.

    Sphinx reads URIs off `reference`, `image` and `raw` nodes, the
    last through its `source` attribute. A directive returning an
    element of its own keeps its URLs in plain attributes, which the
    collector never looks at.

    An empty `raw` node per URL, returned beside the element, carries
    `source` for the collector and writes nothing to any output.

    :param options: The directive's options, as written in the rST.
    :return: One empty `raw` node per URL found, ready to sit beside
        the directive's own node.
    """
    found: list[nodes.Node] = []
    for option in LINKCHECK_OPTIONS:
        value = options.get(option)
        if not isinstance(value, str):
            continue
        found += [
            nodes.raw("", "", format="html", source=uri)
            for uri in value.split()
            if "://" in uri
        ]
    return found


def plain(text: str) -> str:
    """Flatten rendered HTML down to bare text.

    A page title reaches the context already rendered, so a heading
    carrying an icon role arrives as markup and that would put
    escaped `<span>` soup in a `<meta>` tag.

    Only things that look like a tag are stripped, so a description
    reading "when x < 5 and y > 0" keeps its middle.

    :param text: Rendered HTML, or plain text.
    :return: The text with tags removed, entities resolved and
        whitespace collapsed onto a single line.
    """
    return " ".join(unescape(TAG_RE.sub("", text)).split())


def clip(text: str, limit: int) -> str:
    """Cut a line down to length on a word boundary.

    :param text: The line to shorten.
    :param limit: Longest the result may be, ellipsis aside.
    :return: The text, trimmed and closed with an ellipsis when it
        had to be cut.
    """
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",;:.") + "\u2026"


def buried(paragraph: nodes.Element) -> bool:
    """Say whether a paragraph is sitting inside furniture.

    A line lifted out of a caption, an admonition, a table or a code
    block reads as a non-sequitur on its own, so those are passed over.

    :param paragraph: The paragraph to place.
    :return: `True` when it has one of those for an ancestor.
    """
    parent: nodes.Element | None = paragraph.parent
    while parent is not None and not isinstance(parent, FURNITURE):
        parent = parent.parent
    return parent is not None


def standfirst(doctree: nodes.document | None, limit: int) -> str:
    """Pull the page's lead, the line that sits under the title.

    It already answers "what is this page" in one line, which is what
    a social description wants.

    :param doctree: The resolved doctree, or `None` for generated
        pages.
    :param limit: Longest the result may be.
    :return: The lead, or an empty string when the page hasn't got
        one.
    """
    if doctree is None:
        return ""
    for paragraph in findall(doctree, nodes.paragraph):
        if "km-lead" not in (paragraph.get("classes") or []):
            continue
        if buried(paragraph):
            continue
        text = " ".join(paragraph.astext().split())
        if text:
            return clip(text, limit)
    return ""


def summarise(doctree: nodes.document | None, limit: int) -> str:
    """Fall back to a page's opening paragraph.

    Only reached when the page sets no description of its own, has no
    lead and the theme carries no default either.

    :param doctree: The resolved doctree, or `None` for generated
        pages.
    :param limit: Longest the result may be.
    :return: A single-line summary, or an empty string when the page
        has no usable prose.
    """
    if doctree is None:
        return ""
    for paragraph in findall(doctree, nodes.paragraph):
        if buried(paragraph):
            continue
        text = " ".join(paragraph.astext().split())
        if len(text) >= 40:
            return clip(text, limit)
    return ""


def social_metadata(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Work out the Open Graph and Twitter values for a page.

    Each one prefers the page's own `:km-pg-*:` field, then the default
    in `html_context`, then whatever can be salvaged from the page. The
    docinfo keys keep their `km-pg-` prefix, so they are looked up under
    that name and not the bare one. The default image's alt text only
    goes with the default image, since it describes that one and not a
    picture of the page's own. An article carries the days it was
    created and last updated, as `provenance` read them.

    The search, index and 404 pages have no title yet when this runs,
    so theirs come from `TITLES`, as their descriptions come from
    `GENERATED`. An image given as a path counts from the root of the
    site and goes out absolute, since a link preview ignores a relative
    one.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree, or `None` for generated
        pages.
    """
    options = app.config.html_context.get("km_open_graph") or {}
    if options.get("enable") is False:
        return
    meta: dict[str, str] = context.get("meta") or {}
    limit = int(options.get("description_length", 200))
    generated = doctree is None and pagename in GENERATED
    title = meta.get("km-pg-title") or plain(
        str(TITLES[pagename])
        if generated
        else context.get("title") or context.get("docstitle") or ""
    )
    description = (
        meta.get("km-pg-description")
        or standfirst(doctree, limit)
        or (str(GENERATED[pagename]) if generated else "")
        or options.get("description", "")
        or summarise(doctree, limit)
    )
    image = meta.get("km-pg-image") or options.get("image", "")
    alt = meta.get("km-pg-image-alt") or (
        options.get("image_alt", "") if image == options.get("image") else ""
    )
    context["km_social"] = {
        "title": plain(title),
        "description": plain(description),
        "image": absolute(image, app.config.html_baseurl),
        "image_alt": plain(alt),
        "published": day(meta.get("created", "")),
        "modified": day(meta.get("last_updated", "")),
        "site_name": options.get("site_name") or context.get("docstitle", ""),
        "type": meta.get("km-pg-type") or options.get("type", "website"),
        "locale": meta.get("km-pg-locale") or options.get("locale", ""),
        "card": meta.get("km-pg-card")
        or options.get("card", "summary_large_image"),
        "site": options.get("twitter_site", ""),
    }


def context_defaults(app: Sphinx) -> None:
    """Fill in the `html_context` keys the templates expect.

    A site writes its settings the way it always has, `fa_icons`,
    `fa_kit` and the rest. Each one in `SETTINGS` is copied under a
    `km_` name, which is the only one the theme reads, so its templates
    and code never take a name of Sphinx's or another extension's for
    one of their own. The site's keys are left as they were written.

    Templates read `km_fa_icons` and `km_project` straight off the
    context, so a site that sets neither would fail the build with an
    `UndefinedError`. The `default` filter does not help, since the
    attribute is looked up before the filter runs. Merging defaults
    here means a site names only what it wants changed.

    This runs on `builder-inited` rather than `config-inited`. A theme
    reached through `html_theme` alone is set up while the builder is
    being built, by which time `config-inited` has gone.

    :param app: The Sphinx application instance.
    """
    context: dict[str, t.Any] = app.config.html_context
    for key in SETTINGS:
        if key in context:
            context[f"km_{key}"] = context[key]
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
    context.setdefault("km_fa_style", FA_STYLE)
    context.setdefault("km_fa_css", FA_FREE)
    config = app.config
    if "html_show_sphinx" not in config._raw_config | config._overrides:
        context.setdefault("show_sphinx", False)


def wordcount(doctree: nodes.document | None) -> int:
    """Count the words in a page's prose.

    Paragraphs are counted. The ones inside code blocks, tables,
    figures and admonitions are skipped, which is the list `buried`
    already keeps out of a social description.

    :param doctree: The resolved doctree, or `None` for generated
        pages.
    :return: The number of words counted.
    """
    if doctree is None:
        return 0
    return sum(
        len(paragraph.astext().split())
        for paragraph in findall(doctree, nodes.paragraph)
        if not buried(paragraph)
    )


def reading_time(doctree: nodes.document | None) -> int:
    """Work out roughly how long a page takes to read.

    Code is left out of the count, so a page that is mostly listings
    comes out shorter than its length suggests.

    :param doctree: The resolved doctree, or `None` for generated
        pages.
    :return: Minutes, rounded up.
    """
    return ceil(wordcount(doctree) / WORDS_PER_MINUTE)


def reading_length(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Decide whether a page is long enough to fold up.

    `show_show_more` in `html_context` is the site-wide switch. The
    page's `km_show_show_more` is the answer for this page: true only
    when the page runs to `show_more_after` minutes or more and false
    everywhere when the switch is off.

    :param app: The Sphinx application instance.
    :param pagename: The name of the page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree, or `None` for generated
        pages.
    """
    options = app.config.html_context
    minutes = reading_time(doctree)
    after = int(options.get("km_show_more_after", SHOW_MORE_AFTER))
    context["km_reading_time"] = minutes
    context["km_show_show_more"] = (
        bool(options.get("km_show_show_more", True)) and minutes >= after
    )


def feedback(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Work out what a page's feedback box says and where it points.

    The page's own `:km-fb-*:` fields win and the theme's words fill in
    the rest. The box mails the address in `project`, with the page
    title as the subject, unless the page links somewhere instead. With
    neither, it has no button.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree, or `None` for generated
        pages.
    """
    options = app.config.html_context
    meta: dict[str, str] = context.get("meta") or {}
    email = (options.get("km_project") or {}).get("email", "")
    title = plain(context.get("title") or "")
    subject = quote(str(_("Feedback about %s")) % title)
    href: str | None = f"mailto:{email}?subject={subject}" if email else None
    if meta.get("km-fb-type") == "link":
        href = meta.get("km-fb-target") or href
    icons = options.get("km_fa_icons") or ICONS
    context["km_feedback"] = {
        "mode": meta.get("km-fb-mode", "default"),
        "title": meta.get("km-fb-title") or str(FEEDBACK["title"]),
        "description": meta.get("km-fb-description")
        or str(FEEDBACK["description"]),
        "button": meta.get("km-fb-button") or str(FEEDBACK["button"]),
        "icon": icon(meta.get("km-fb-fa-icon"), icons.get("feedback", "")),
        "href": href,
    }


def header(source: str) -> dict[str, str]:
    """Read the comments heading a page.

    Only the comments before its first line of anything else count, so
    a date quoted further down, in an example say, is not taken for the
    page's own. The address after an author's name is left off.

    :param source: The page's source.
    :return: What they say, keyed `author`, `created on` and
        `last updated on`, for the ones the page has.
    """
    found: dict[str, str] = {}
    for line in source.splitlines():
        if line.strip() and not line.startswith(".."):
            break
        match = HEADER_RE.match(line.strip())
        if match:
            found.setdefault(match.group(1).lower(), match.group(2).strip())
    if "author" in found:
        found["author"] = found["author"].split("<")[0].strip()
    return found


def committed(app: Sphinx, docname: str, *, first: bool = False) -> dt | None:
    """Ask git when a page was last committed, or first.

    :param app: The Sphinx application instance.
    :param docname: The document to ask about.
    :param first: Ask for the commit that brought the page in, following
        it through renames, rather than the latest one.
    :return: The commit's date, or `None` outside a repository and for a
        page git has never seen.
    """
    src = str(app.env.doc2path(docname, base=True))
    order = ["--follow"] if first else ["-n1"]
    cmd = ["git", "log", *order, "--format=%cI", "--", src]
    try:
        on = co(cmd, cwd=app.confdir, stderr=DEVNULL).decode().split()  # noqa: S603
    except CalledProcessError, FileNotFoundError:
        return None
    return dt.fromisoformat(on[-1]) if on else None


def written(when: dt | None) -> str:
    """Write a date the way a page's header comments write it.

    :param when: The date, or `None` for the day the site is built.
    :return: The date, as `29 September, 2026`.
    """
    when = when or dt.now().astimezone()
    return f"{when.day} {when:%B}, {when.year}"


def absolute(url: str, home: str) -> str:
    """Make an address absolute against the site's own.

    A path counts from the root of the site, with or without its
    leading slash, so `_static/cover.png` means the same picture on
    every page. A site without `html_baseurl` has nothing to resolve it
    against, so the path is left as written.

    :param url: The address, as written.
    :param home: The site's `html_baseurl`.
    :return: The address, absolute where it can be.
    """
    if not url or not home or urlsplit(url).scheme:
        return url
    if url.startswith("//"):
        return f"{urlsplit(home).scheme}:{url}"
    return home.rstrip("/") + "/" + quote(url.lstrip("/"), safe="/%?=&#:")


def day(date: str) -> str:
    """Turn a date written the way the header comments write it into ISO.

    :param date: The date, as `29 September, 2026`.
    :return: `2026-09-29`, or an empty string when it does not read as a
        date.
    """
    try:
        return dt.strptime(date, "%d %B, %Y").astimezone().date().isoformat()
    except ValueError:
        return ""


def provenance(app: Sphinx, docname: str, source: list[str]) -> None:
    """Work out who wrote a page and when it was created and updated.

    The page's own `.. Author:`, `.. Created on:` and `.. Last updated
    on:` comments win. A date the page leaves out is the one of its first
    commit or its latest and failing that, the day the site is built.
    An author it leaves out is the name its `author` directive gives,
    and failing that, the project's, which is settled as the page is
    written.

    :param app: The Sphinx application instance.
    :param docname: The document being read.
    :param source: The document's source, as docutils hands it over.
    """
    metadata = app.env.metadata.setdefault(docname, {})
    found = header(source[0] if source else "")
    if found.get("author"):
        metadata.setdefault("author", found["author"])
    if not metadata.get("created"):
        metadata["created"] = found.get("created on") or written(
            committed(app, docname, first=True)
        )
    if not metadata.get("last_updated"):
        metadata["last_updated"] = found.get("last updated on") or written(
            committed(app, docname)
        )


def root_urls(tree: bs4.BeautifulSoup, base: str, root: str) -> None:
    """Rewrite a page's relative URLs to start at the site root.

    A page served for somebody else's address cannot use relative URLs,
    since the browser resolves them against the address that was asked
    for. Each one is resolved against where the page would have lived,
    then written out from the root of the site.

    :param tree: Parsed HTML tree, edited in place.
    :param base: The directory the page was rendered as being in.
    :param root: The path the site is served under, with its slashes.
    """
    for tag in tree.find_all(True):
        for attribute in ROOTED_ATTRIBUTES:
            url = tag.get(attribute)
            if not isinstance(url, str) or not url:
                continue
            if url.startswith(ROOTED_SKIP) or "://" in url:
                continue
            url, _, fragment = url.partition("#")
            path = posixpath.normpath(posixpath.join("/", base, url))
            if url.endswith("/") and not path.endswith("/"):
                path += "/"
            path = root.rstrip("/") + path
            tag[attribute] = f"{path}#{fragment}" if fragment else path


def not_found(app: Sphinx) -> None:
    """Write the theme's 404 page to the top of the output tree.

    A host serves `404.html` for a path it cannot find, so the file has
    to sit at the root under that exact name. `html_additional_pages`
    cannot put it there, since `dirhtml` would write it as
    `404/index.html`, so the page is rendered here and its URLs rooted
    afterwards.

    `pageurl` is cleared, since the page stands in for whatever
    address was asked for and has no canonical URL of its own.

    Set `show_404` to `False` in `html_context` to skip it.

    :param app: The Sphinx application instance.
    """
    builder = app.builder
    if not isinstance(builder, StandaloneHTMLBuilder):
        return
    if not app.config.html_context.get("km_show_404", True):
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
            "km_show_last_updated_on": False,
            "km_show_previous_next_pages": False,
            "km_show_scrolltop": False,
            "km_show_show_more": False,
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


@functools.cache
def designed() -> frozenset[str]:
    """Name the theme's templates that draw a `sphinx_design` component.

    They are read once, the first time a page asks.

    :return: Their file names.
    """
    names: set[str] = set()
    for name in os.listdir(TEMPLATES):
        path = p.join(TEMPLATES, name)
        if not p.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            if "sd-" in f.read():
                names.add(name)
    return frozenset(names)


def design_assets(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Leave `sphinx_design`'s stylesheet and script off a page without it.

    `sphinx_design` hands every page its stylesheet and its tab script,
    about 50 KB between them, whether or not the page has a single card
    on it. A page keeps them when its body carries a class of theirs, or
    when its template draws one itself, the way the 404 page's button
    does. The theme's own `sphinx-design.css` stays on every page, since
    it styles icons outside the components too.

    The lists are trimmed in place, so a file added for the page after
    this runs, an `embed`'s stylesheet say, still makes it.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context.
    :param doctree: The resolved doctree.
    """
    if not themed(app.builder) or templatename in designed():
        return
    if "sd-" in str(context.get("body") or ""):
        return
    for key in ("css_files", "script_files"):
        files = context.get(key)
        if not isinstance(files, list):
            continue
        kept = []
        for item in files:
            filename = str(getattr(item, "filename", item) or "")
            if p.basename(filename) not in DESIGN_ASSETS:
                kept.append(item)
        files[:] = kept


def hidden(robots: str) -> bool:
    """Say whether a page's robots rules keep it out of search engines.

    :param robots: The page's `:km-pg-robots:` field, as written.
    :return: `True` for `noindex`, or `none`, which is `noindex` and
        `nofollow` together.
    """
    rules = {_.strip().lower() for _ in robots.split(",")}
    return bool(rules & {"noindex", "none"})


def sitemap(app: Sphinx) -> None:
    """Write `sitemap.xml` and `robots.txt` at the top of the output.

    The sitemap lists every page the site is built from, with the day
    it was last updated where that reads as a date and `robots.txt`
    points crawlers at it. A page asking search engines to leave it
    out, through `:km-pg-robots:`, is left out of the sitemap too, since
    listing it would ask them to index it. A sitemap holds whole
    addresses, so a site without `html_baseurl` gets neither and nor
    does one that turns `show_sitemap` off. A `robots.txt` the site
    keeps in `html_extra_path` is left as it is.

    :param app: The Sphinx application instance.
    """
    home = app.config.html_baseurl
    if not home or not app.config.html_context.get("km_show_sitemap", True):
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
    """Write the theme's 404 page and sitemap once the build has worked.

    :param app: The Sphinx application instance.
    :param exc: Whatever went wrong during the build, or `None`.
    """
    builder = app.builder
    if exc or not isinstance(builder, StandaloneHTMLBuilder):
        return
    if themed(builder) and builder.name in {"html", "dirhtml"}:
        not_found(app)
        sitemap(app)
