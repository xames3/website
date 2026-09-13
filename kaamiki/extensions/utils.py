"""\
Theme Utilities
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February, 2025
Last updated on: 12 September, 2026

The theme's shared helpers. They fall into four groups: rendering a
directive's template, reading things off the doctree (a lead, a
description, a reading time), filling in the page context, and the
post-build pass over the written HTML.

.. deprecated:: 19.10.2025

    `website_options` in favour of `html_context`, which removes the
    need for `register_website_options`.

.. versionchanged:: 31.8.2026

    [1] `ensure_classes_on_nodes` was annotated and connected for the
        wrong event; it matches `doctree-resolved` now and uses
        `findall()` rather than the removed `.traverse()`.
    [2] Fixed a `dt.timezone.utc` typo in `last_updated_date`. `dt` is
        the class, not the module.

.. versionadded:: 10.9.2026

    [1] `render` gives every directive one shared Jinja environment
        with autoescaping on. Each one used to build a bare
        `jinja2.Template` at import time, which left escaping off.
    [2] `measure` reads an image's size off the file header, for PNG,
        GIF, WEBP and JPEG, so the theme can write `width`/`height`
        without an imaging dependency.
    [3] `social_metadata` works the Open Graph and Twitter values out
        of the doctree and `html_context`, replacing
        `sphinxext-opengraph` and the `matplotlib` it dragged in. A
        page's own `:og:*` fields win.
    [4] `plain` flattens rendered HTML to bare text, so a title
        carrying an icon role does not leak `<span>` soup into a
        `<meta>` tag.
    [5] `depart` is the shared no-op for a directive that writes its
        whole widget during `visit`.
    [6] `standfirst` pulls the page's lead, which `social_metadata`
        prefers to anything guessed from the prose below it.
    [7] `buried` and `clip` are the bits `standfirst` and `summarise`
        both wanted, pulled out rather than written twice.
    [8] `wordcount` and `reading_time` put a number of minutes on a
        page. Paragraphs count towards it; code, tables, figures and
        admonitions do not. `reading_length` passes that to the
        template with the answer to whether the page folds up.
    [9] `context_defaults` merges the theme's icons and project
        details into `html_context`, so a site that sets neither gets
        defaults rather than a failed build.
    [10] `trail` hands the link checker the URLs a directive keeps in
         its options. Sphinx reads URIs off `reference`, `image` and
         `raw` nodes alone, so an avatar or background went unchecked.
    [11] `not_found` writes the theme's 404 page to the top of the
         output tree, under `show_404`. `root_urls` rewrites its URLs
         to start at the site root, since the page is served under
         whatever address was asked for and not under its own.

.. versionchanged:: 10.9.2026

    [1] `last_updated_date` no longer wraps the path in `shlex.quote`
        for `git log`. The command runs as an argument list, not
        through a shell, so the quoting only corrupted paths with a
        space in them.
    [2] `findall` is generic over the element type rather than
        returning `t.Any`, which had been switching type checking off
        at the one place the doctree is walked.
    [3] `build_finished` post-processes every HTML file in the output
        directory, not only the documents Sphinx re-read. A template
        or stylesheet change rewrites pages without re-reading them, so
        that list came back empty and an incremental build shipped
        pages with none of the transforms applied.
    [5] The description falls back in a stated order: the page's own
        `:og:description:`, then its lead, then the default in
        `html_context`, then its opening paragraph.
    [6] `SOCIAL_SKIP` is now `FURNITURE`, since the reading-time count
        uses the same list.

.. deprecated:: 10.9.2026

    `env_before_read_docs` and the `theme_htmls` list it kept are gone.
    They narrowed post-processing to re-read documents, which is what
    made an incremental build differ from a fresh one.
"""

from __future__ import annotations

import posixpath
import re
import struct
import typing as t
from datetime import UTC
from datetime import datetime as dt
from html import unescape
from math import ceil
from pathlib import Path
from subprocess import CalledProcessError
from subprocess import check_output as co
from urllib.parse import urlsplit

import bs4
import jinja2
from bs4.element import NavigableString
from docutils import nodes
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util.display import status_iterator

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

TEMPLATES: Path = Path(__file__).resolve().parent.parent / "base" / "templates"
LAST_UPDATED_RE: re.Pattern[str] = re.compile(
    r"^\.\.\s+Last updated on:\s*(.+)$", re.IGNORECASE
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
    "email": "",
    "source": "#",
}
ICONS: t.Final[dict[str, str]] = {
    "breadcrumb_home": "fa-solid fa-house",
    "breadcrumb_separator_child": "fa-solid fa-angle-right",
    "breadcrumb_separator_parent": "fa-solid fa-angles-right",
    "copy_url": "fa-solid fa-link",
    "dark_mode": "fa-solid fa-moon",
    "light_mode": "fa-solid fa-sun",
    "next_button": "fa-solid fa-arrow-right",
    "previous_button": "fa-solid fa-arrow-left",
    "reading_time": "fa-regular fa-clock",
    "show_more": "fa-solid fa-chevron-down",
}
LINKCHECK_OPTIONS: tuple[str, ...] = ("avatar", "background", "target")
JPEG_SIZE_MARKERS: frozenset[int] = frozenset(
    {
        0xC0,
        0xC1,
        0xC2,
        0xC3,
        0xC5,
        0xC6,
        0xC7,
        0xC9,
        0xCA,
        0xCB,
        0xCD,
        0xCE,
        0xCF,
    }
)

environment: jinja2.Environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES),
    autoescape=True,
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=False,
)


def render(template: str, /, **context: t.Any) -> str:
    """Render one of the theme's directive templates.

    Every directive shares this one environment, which has autoescaping
    on and a loader rooted at the theme's template directory.

    :param template: Template filename, relative to `base/templates`.
    :param context: Values made available to the template.
    :return: The rendered HTML.

    .. versionadded:: 10.9.2026
    """
    return environment.get_template(template).render(**context)


def depart(self: HTMLTranslator, node: nodes.Element) -> None:
    """Close a node that has nothing to close.

    `add_node` wants a visit/depart pair, but a directive that writes
    its whole widget during `visit` has nothing left to do. They share
    this instead of each carrying an empty function.

    :param self: The HTML translator instance (unused).
    :param node: The node being departed (unused).

    .. versionadded:: 10.9.2026
    """


def measure(path: str) -> tuple[int, int] | None:
    """Read an image's size from its header.

    Only the leading bytes are read, so this is cheap and needs no
    imaging dependency. Writing `width`/`height` out lets the browser
    hold the space open before the image lands.

    :param path: Filesystem path to the image.
    :return: A `(width, height)` pair, or `None` when the format is not
        recognised or the header is unreadable.

    .. versionadded:: 10.9.2026
    """
    try:
        with open(path, "rb") as fd:
            head = fd.read(32)
            if head[:8] == b"\x89PNG\r\n\x1a\n" and head[12:16] == b"IHDR":
                w, h = struct.unpack(">II", head[16:24])
                return int(w), int(h)
            if head[:6] in {b"GIF87a", b"GIF89a"}:
                w, h = struct.unpack("<HH", head[6:10])
                return int(w), int(h)
            if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
                fd.seek(0)
                blob = fd.read(30)
                if blob[12:16] == b"VP8X":
                    w = int.from_bytes(blob[24:27], "little") + 1
                    h = int.from_bytes(blob[27:30], "little") + 1
                    return w, h
                return None
            if head[:2] == b"\xff\xd8":
                fd.seek(2)
                while True:
                    marker = fd.read(2)
                    if len(marker) < 2 or marker[0] != 0xFF:
                        return None
                    if marker[1] in JPEG_SIZE_MARKERS:
                        fd.read(3)
                        h, w = struct.unpack(">HH", fd.read(4))
                        return int(w), int(h)
                    size = struct.unpack(">H", fd.read(2))[0]
                    fd.seek(size - 2, 1)
    except (OSError, struct.error):
        return None
    return None


def findall[T: nodes.Element](
    node: nodes.Node,
    element: type[T],
) -> Iterator[T]:
    """Walk a doctree for every node of one type.

    Older docutils spells this `traverse`, so the method is looked up
    by name rather than called directly.

    :param node: Where to start looking.
    :param element: The node type to look for.
    :return: Every match, in document order.

    .. versionchanged:: 31.8.2026

        Takes any `nodes.Element`, not just references and bullet
        lists.

    .. versionchanged:: 10.9.2026

        Generic over the element type rather than returning `t.Any`,
        which had been switching type checking off for the whole loop.
        `docutils` is untyped, so the cast marks that boundary.
    """
    method = "findall" if hasattr(node, "findall") else "traverse"
    return t.cast("Iterator[T]", getattr(node, method)(element))


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

    .. versionadded:: 10.9.2026
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


def remove_empty_toctree_divs(tree: bs4.BeautifulSoup) -> None:
    """Drop the wrapper a hidden toctree leaves behind.

    Sphinx writes a `toctree-wrapper` div even for a `:hidden:`
    toctree, which paints nothing and leaves a gap.

    :param tree: Parsed HTML tree, edited in place.

    .. versionchanged:: 31.8.2026

        Only calls `.strip()` on the div's sole child when it is a
        `NavigableString`, instead of assuming it always is one.
    """
    for div in tree.select("div.toctree-wrapper"):
        if len(div.contents) != 1:
            continue
        content = div.contents[0]
        if isinstance(content, NavigableString) and not content.strip():
            div.decompose()


def remove_comments(tree: bs4.BeautifulSoup) -> None:
    """Strip the HTML comments out of a page.

    The templates carry header comments the reader has no use for.

    :param tree: Parsed HTML tree, edited in place.
    """
    for comment in tree.find_all(string=lambda c: isinstance(c, bs4.Comment)):
        comment.extract()


def add_copy_to_headerlinks(tree: bs4.BeautifulSoup) -> None:
    """Make a heading's anchor copy its own URL when clicked.

    :param tree: Parsed HTML tree, edited in place.
    """
    for link in tree.select("a.headerlink"):
        link["@click.prevent"] = (
            "window.navigator.clipboard.writeText($el.href);"
        )
        del link["title"]
        link["aria-label"] = "Copy link"


def open_links_in_new_tab(tree: bs4.BeautifulSoup) -> None:
    """Open external links in a new tab.

    `rel="nofollow noopener"` goes on with the target, so the new tab
    cannot reach back at the page that opened it.

    :param tree: Parsed HTML tree, edited in place.
    """
    for link in tree("a", class_="reference external"):
        link["rel"] = "nofollow noopener"
        link["target"] = "_blank"


def postprocess(html: str) -> None:
    """Run every transform over one written page.

    :param html: Path to the HTML file, rewritten in place.

    .. versionchanged:: 31.8.2026

        Dropped the unused `app` parameter rather than reassigning it
        to itself to appease the linter.
    """
    with open(html, encoding="utf-8") as f:
        tree = bs4.BeautifulSoup(f, "html.parser")
    open_links_in_new_tab(tree)
    add_copy_to_headerlinks(tree)
    remove_empty_toctree_divs(tree)
    remove_comments(tree)
    with open(html, "w", encoding="utf-8") as f:
        f.write(str(tree))


def plain(text: str) -> str:
    """Flatten rendered HTML down to bare text.

    A page title reaches the context already rendered, so a heading
    carrying an icon role arrives as markup, and that would put
    escaped `<span>` soup in a `<meta>` tag.

    Only things that look like a tag are stripped, so a description
    reading "when x < 5 and y > 0" keeps its middle.

    :param text: Rendered HTML, or plain text.
    :return: The text with tags removed, entities resolved and
        whitespace collapsed onto a single line.

    .. versionadded:: 10.9.2026
    """
    return " ".join(unescape(TAG_RE.sub("", text)).split())


def clip(text: str, limit: int) -> str:
    """Cut a line down to length on a word boundary.

    :param text: The line to shorten.
    :param limit: Longest the result may be, ellipsis aside.
    :return: The text, trimmed and closed with an ellipsis when it
        had to be cut.

    .. versionadded:: 10.9.2026
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

    .. versionadded:: 10.9.2026
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

    .. versionadded:: 10.9.2026
    """
    if doctree is None:
        return ""
    for paragraph in findall(doctree, nodes.paragraph):
        if "lead" not in (paragraph.get("classes") or []):
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
    lead, and the theme carries no default either.

    :param doctree: The resolved doctree, or `None` for generated
        pages.
    :param limit: Longest the result may be.
    :return: A single-line summary, or an empty string when the page
        has no usable prose.

    .. versionchanged:: 10.9.2026

        Only returns the opening paragraph now. The lead moved out to
        `standfirst` so the theme-wide default can sit between the two.
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

    Each one prefers the page's own `:og:*` field, then the default in
    `html_context`, then whatever can be salvaged from the page. The
    docinfo keys keep their `og:` prefix, so they are looked up under
    that name and not the bare one.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered (unused).
    :param templatename: The template rendering it (unused).
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree, or `None` for generated
        pages.

    .. versionadded:: 10.9.2026
    """
    options = app.config.html_context.get("open_graph") or {}
    if options.get("enable") is False:
        return
    meta: dict[str, str] = context.get("meta") or {}
    limit = int(options.get("description_length", 200))
    title = meta.get("og:title") or plain(
        context.get("title") or context.get("docstitle") or ""
    )
    description = (
        meta.get("og:description")
        or standfirst(doctree, limit)
        or options.get("description", "")
        or summarise(doctree, limit)
    )
    image = meta.get("og:image") or options.get("image", "")
    context["social"] = {
        "title": plain(title),
        "description": plain(description),
        "image": image,
        "image_alt": meta.get("og:image:alt") or options.get("image_alt", ""),
        "site_name": options.get("site_name") or context.get("docstitle", ""),
        "type": meta.get("og:type") or options.get("type", "website"),
        "locale": meta.get("og:locale") or options.get("locale", ""),
        "card": meta.get("og:card")
        or options.get("card", "summary_large_image"),
        "site": options.get("twitter_site", ""),
    }


def context_defaults(app: Sphinx) -> None:
    """Fill in the `html_context` keys the templates expect.

    Templates read `fa_icons` and `project` straight off the context,
    so a site that sets neither fails the build with an
    `UndefinedError`. The `default` filter does not help, since the
    attribute is looked up before the filter runs. Merging defaults
    here means a site names only what it wants changed.

    This runs on `builder-inited` rather than `config-inited`. A theme
    reached through `html_theme` alone is set up while the builder is
    being built, by which time `config-inited` has gone.

    :param app: The Sphinx application instance.

    .. versionadded:: 10.9.2026
    """
    context: dict[str, t.Any] = app.config.html_context
    icons: dict[str, str] = dict(ICONS)
    icons.update(context.get("fa_icons") or {})
    context["fa_icons"] = icons
    project: dict[str, str] = dict(PROJECT)
    project["author"] = app.config.author
    project.update(context.get("project") or {})
    context["project"] = project


def wordcount(doctree: nodes.document | None) -> int:
    """Count the words in a page's prose.

    Paragraphs are counted. The ones inside code blocks, tables,
    figures and admonitions are skipped, which is the list `buried`
    already keeps out of a social description.

    :param doctree: The resolved doctree, or `None` for generated
        pages.
    :return: The number of words counted.

    .. versionadded:: 10.9.2026
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

    .. versionadded:: 10.9.2026
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

    `show_show_more` in `html_context` is the site-wide switch. This
    replaces it in the page context with the answer for this page:
    true only when the page runs to `show_more_after` minutes or more,
    and false everywhere when the switch is off.

    :param app: The Sphinx application instance.
    :param pagename: The name of the page being rendered (unused).
    :param templatename: The template rendering it (unused).
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree, or `None` for generated
        pages.

    .. versionadded:: 10.9.2026
    """
    options = app.config.html_context
    minutes = reading_time(doctree)
    after = int(options.get("show_more_after", SHOW_MORE_AFTER))
    context["reading_time"] = minutes
    context["show_show_more"] = (
        bool(options.get("show_show_more", True)) and minutes >= after
    )


def ensure_classes_on_nodes(
    app: Sphinx, doctree: nodes.document, docname: str
) -> None:
    """Give every node a `classes` list.

    Parts of Sphinx assume the attribute is there and fall over on a
    node that never got one.

    :param app: The Sphinx application instance (unused).
    :param doctree: The resolved doctree, edited in place.
    :param docname: The document's name (unused).

    .. versionchanged:: 31.8.2026

        Was annotated and connected for a different event. It matches
        `doctree-resolved` now and uses `findall()` rather than the
        removed `.traverse()`.
    """
    for node in findall(doctree, nodes.Element):
        node.setdefault("classes", [])


def last_updated_date(app: Sphinx, docname: str, source: list[str]) -> None:
    """Work out when a page was last updated.

    A `.. Last updated on:` comment in the source wins. Failing that,
    the date of the file's last commit, and failing that, the file's
    own timestamp.

    :param app: The Sphinx application instance.
    :param docname: The document being read.
    :param source: The document's source, as docutils hands it over.

    .. versionchanged:: 31.8.2026

        Fixed a `dt.timezone.utc` typo. `dt` is the class, not the
        module, so this uses `datetime.UTC` directly.
    """
    metadata = app.env.metadata.setdefault(docname, {})
    if metadata.get("last_updated"):
        return
    on = None
    if source:
        for line in source[0].splitlines():
            match = LAST_UPDATED_RE.match(line.strip())
            if match:
                on = match.group(1).strip()
                break
    if on:
        metadata["last_updated"] = on
        return
    src = Path(app.env.doc2path(docname, base=True))
    if not src.is_file():
        return
    on = ""
    try:
        cmd = [
            "git",
            "log",
            "--pretty=format:%cd",
            "--date=format:%B %d, %Y",
            "-n1",
            "--",
            str(src),
        ]
        on = co(cmd, cwd=app.confdir).decode().strip()  # noqa: S603
    except (CalledProcessError, FileNotFoundError):
        on = ""
    if not on:
        timestamp = src.stat().st_mtime
        try:
            tz = dt.now().astimezone().tzinfo or UTC
            on = dt.fromtimestamp(timestamp, tz=tz).strftime("%b %d, %Y")
        except FileNotFoundError:
            on = ""
    if on:
        metadata["last_updated"] = on


def root_urls(tree: bs4.BeautifulSoup, base: str, root: str) -> None:
    """Rewrite a page's relative URLs to start at the site root.

    A page served for somebody else's address cannot use relative URLs,
    since the browser resolves them against the address that was asked
    for. Each one is resolved against where the page would have lived,
    then written out from the root of the site.

    :param tree: Parsed HTML tree, edited in place.
    :param base: The directory the page was rendered as being in.
    :param root: The path the site is served under, with its slashes.

    .. versionadded:: 10.9.2026
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

    .. versionadded:: 10.9.2026
    """
    builder = app.builder
    if not isinstance(builder, StandaloneHTMLBuilder):
        return
    if not app.config.html_context.get("show_404", True):
        return
    if getattr(builder, "globalcontext", None) is None:
        return
    page = Path(app.outdir, f"{NOT_FOUND}.html")
    builder.handle_page(
        NOT_FOUND,
        {
            "pageurl": None,
            "show_breadcrumbs": False,
            "show_feedback": False,
            "show_last_updated_on": False,
            "show_previous_next_pages": False,
            "show_scrolltop": False,
            "show_show_more": False,
        },
        f"{NOT_FOUND}.html",
        outfilename=page,
    )
    base = posixpath.dirname(builder.get_target_uri(NOT_FOUND))
    root = urlsplit(app.config.html_baseurl).path or "/"
    with open(page, encoding="utf-8") as f:
        tree = bs4.BeautifulSoup(f, "html.parser")
    root_urls(tree, base, root)
    page.write_text(str(tree), encoding="utf-8")


def build_finished(app: Sphinx, exc: Exception | None) -> None:
    """Write the 404 page and post-process every page.

    Only for the HTML builders, and only when the build worked. The 404
    page goes out first so it is post-processed along with the rest.

    :param app: The Sphinx application instance.
    :param exc: Whatever went wrong during the build, or `None`.

    .. versionchanged:: 10.9.2026

        Writes the theme's 404 page through `not_found` before the
        post-processing pass.
    """
    if exc or app.builder.name not in {"html", "dirhtml"}:
        return
    not_found(app)
    htmls = sorted(str(_) for _ in Path(app.outdir).rglob("*.html"))
    if not htmls:
        return
    for html in status_iterator(
        htmls,
        "Postprocessing... ",
        "darkgreen",
        len(htmls),
        app.verbosity,
    ):
        postprocess(html)
