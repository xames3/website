"""\
Theme Utilities
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February, 2025
Last updated on: 11 September, 2026

This module defines a collection of utility functions used for
customising this sphinx theme. These utilities focus on enhancing the
post-processing of the generated HTML output, as well as providing
additional support for interactive elements, theme options and other
dynamic behaviours.

The functionality provided includes handling collapsible table of
contents (ToC), removal of unnecessary elements and custom event
handling for theme-specific features.

The goal of this module is to ensure that this theme produces clean,
efficient and interactive HTML documentation by leveraging Sphinx's
internal APIs and dynamic JavaScript bindings.

.. deprecated:: 19.10.2025

    Use of `website_options` in favour of `html_context`. This removes
    the need of `register_website_options` function.

.. versionchanged:: 31.8.2026

    [1] `ensure_classes_on_nodes` was annotated and called for the wrong
        Sphinx event; fixed to match `doctree-resolved`'s actual
        signature and to use `findall()` instead of the removed
        `.traverse()` call.
    [2] Fixed a `datetime.timezone.utc` typo (`dt` is the `datetime`
        class, not the module) in `last_updated_date`.
    [3] `make_toc_collapsible` and `remove_empty_toctree_divs` no longer
        assume a tag's `class` attribute or a div's sole child are
        always list/text types.

.. versionadded:: 10.9.2026

    [1] `render` gives every directive one shared, autoescaping Jinja
        environment rooted at the theme's template directory. Each
        directive previously opened its own template at import time
        and built a bare `jinja2.Template`, which left autoescaping
        off entirely.
    [2] `measure` reads an image's intrinsic size straight from the
        file header (PNG, GIF, WEBP and JPEG), so the theme can emit
        `width`/`height` without pulling in an imaging dependency.
    [3] `summarise` and `social_metadata` work out the Open Graph and
        Twitter card values from the doctree and `html_context`.
        Between them they replace `sphinxext-opengraph`, which
        dragged `matplotlib` in purely to draw social cards. A page's
        own `:og:title:`, `:og:description:`, `:og:type:` and
        `:og:image:` are read straight off the docinfo, keys and all,
        since that is how docutils hands them over. Anything a page
        leaves unset falls back to `html_context`, then to the page's
        own opening paragraph.
    [4] `plain` flattens rendered HTML down to bare text, so a page
        title carrying an icon role doesn't leak escaped `<span>`
        soup into a `<meta>` tag.
    [5] `depart` is the shared no-op that any directive writing its
        whole widget during `visit` can borrow, instead of each one
        carrying an empty function to satisfy `add_node`.

.. versionchanged:: 10.9.2026

    [1] `last_updated_date` no longer wraps the source path in
        `shlex.quote` before handing it to `git log`. The command is run
        as an argument list rather than through a shell, so the quoting
        only corrupted paths that contained a space.
    [2] `findall` is generic over the element type instead of returning
        `t.Any`, which had been switching type checking off at the one
        place the doctree is walked. Tightening it turned up `summarise`
        walking a parent chain the stubs believed could never end.
"""

from __future__ import annotations

import re
import struct
import typing as t
from datetime import UTC
from datetime import datetime as dt
from html import unescape
from pathlib import Path
from subprocess import CalledProcessError
from subprocess import check_output as co

import bs4
import jinja2
from bs4.element import AttributeValueList
from bs4.element import NavigableString
from docutils import nodes
from sphinx.util.display import status_iterator

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from sphinx.application import Sphinx
    from sphinx.builders.html import StandaloneHTMLBuilder
    from sphinx.environment import BuildEnvironment
    from sphinx.writers.html import HTMLTranslator

TEMPLATES: Path = Path(__file__).resolve().parent.parent / "base" / "templates"
LAST_UPDATED_RE: re.Pattern[str] = re.compile(
    r"^\.\.\s+Last updated on:\s*(.+)$", re.IGNORECASE
)
TAG_RE: re.Pattern[str] = re.compile(r"</?[A-Za-z][^<>]*>")
SOCIAL_SKIP: tuple[type, ...] = (
    nodes.Admonition,
    nodes.figure,
    nodes.literal_block,
    nodes.table,
    nodes.topic,
)
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

    Directives previously each opened their own template file at import
    time and built a bare `jinja2.Template`, which left autoescaping
    off - so a caption or title containing `&`, `<` or a quote emitted
    broken markup. They now share one autoescaping environment with a
    loader rooted at the theme's template directory.

    :param template: Template filename, relative to `base/templates`.
    :param context: Values made available to the template.
    :return: The rendered HTML.

    .. versionadded:: 10.9.2026
    """
    return environment.get_template(template).render(**context)


def depart(self: HTMLTranslator, node: nodes.Element) -> None:
    """Close a node that has nothing to close.

    `add_node` insists on a visit/depart pair, but a directive that
    writes its whole widget in one go during `visit` has nothing left
    to do on the way out. Every one of those used to carry its own
    empty function purely to satisfy the signature; they share this
    one now.

    :param self: The HTML translator instance (unused).
    :param node: The node being departed (unused).

    .. versionadded:: 10.9.2026
    """


def measure(path: str) -> tuple[int, int] | None:
    """Read an image's intrinsic pixel size from its header.

    Only the leading bytes are read, so this stays cheap and avoids
    pulling in an imaging dependency. Supplying `width`/`height` lets
    the browser reserve space before the image arrives, which is what
    stops the page reflowing as images load.

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
    """Recursively search through the given docutils node to find all
    instances of a specified element type.

    This function abstracts the traversal method, ensuring
    compatibility across different versions of docutils. Depending on
    the version, it will either use the `findall` method or the older
    `traverse` method.

    :param node: The starting node from which the search will be
        performed.
    :param element: The type of node element to find, such as references
        or bullet lists.
    :return: An iterator over every matching element found within the
        given node.

    .. versionchanged:: 31.8.2026

        Broadened `element` from `reference | bullet_list` to
        `nodes.Element`, so callers can search for any node type.

    .. versionchanged:: 10.9.2026

        Generic over the element type rather than returning `t.Any`, so
        a caller walking for `nodes.paragraph` gets paragraphs back
        instead of switching type checking off for the whole loop.
        `docutils` is untyped, so the cast marks that boundary.
    """
    method = "findall" if hasattr(node, "findall") else "traverse"
    return t.cast("Iterator[T]", getattr(node, method)(element))


def make_toc_collapsible(tree: bs4.BeautifulSoup) -> None:
    """Enhance the left sidebar's ToC with collapsible branches.

    This attaches an adjacent toggle button after links that have a
    following ``ul``. The button uses theme CSS for a down chevron via a
    pseudo element. No Alpine attributes or inline SVGs are injected.

    :param tree: Parsed HTML tree to mutate.

    .. versionchanged:: 31.8.2026

        No longer assumes an existing `class` attribute is a list; a
        plain string (a valid bs4 representation) is now handled too.
    """
    for link in tree.select("#left-sidebar a"):
        children = link.find_next_sibling("ul")
        if not children:
            continue
        parent = link.parent
        if not parent or parent.name != "li":
            continue
        if not children.get("id"):
            children["id"] = f"nav-branch-{abs(hash(str(children))) % (10**8)}"
        current = (
            "current" in (parent.get("class") or [])
            or "current" in (link.get("class") or [])
            or bool(children.select(".current"))
        )
        raw: str | AttributeValueList | list[str] = parent.get("class") or []
        classes: list[str] = raw.split() if isinstance(raw, str) else list(raw)
        parent["class"] = AttributeValueList({*classes, "has-children"})
        if current:
            parent["aria-expanded"] = "true"
        else:
            parent["aria-expanded"] = "false"
        button = tree.new_tag("button", type="button")
        button["class"] = "nav-toggle"
        button["aria-controls"] = children["id"]
        sr = tree.new_tag("span", attrs={"class": "sr-only"})
        sr.string = "Toggle section"
        button.append(sr)
        link.insert_after(button)


def remove_empty_toctree_divs(tree: bs4.BeautifulSoup) -> None:
    """Remove empty `toctree-wrapper` divs from the HTML tree.

    In Sphinx, `toctree-wrapper` divs may be generated even when no
    visible content is present, such as when a toctree is marked as
    `:hidden:`. These empty containers result in unnecessary whitespace
    and redundant elements in the final HTML output.

    This function scans the HTML tree, identifies empty toctree divs
    (those containing only whitespace or line breaks) and removes them
    to maintain a clean and optimised document structure.

    :param tree: Parsed HTML tree representing the document structure.

    .. versionchanged:: 31.8.2026

        Only calls `.strip()` on the div's sole child when it's a
        `NavigableString`, instead of assuming it always is one.
    """
    for div in tree.select("div.toctree-wrapper"):
        if len(div.contents) != 1:
            continue
        content = div.contents[0]
        if isinstance(content, NavigableString) and not content.strip():
            div.decompose()


def remove_comments(tree: bs4.BeautifulSoup) -> None:
    """Strip all HTML comments from the parsed HTML tree.

    HTML comments (enclosed in `<!-- -->`) are often used during
    development for debugging or documentation purposes but are not
    needed in the final output. This function iterates through the HTML
    tree and removes all comment nodes, resulting in a cleaner, more
    efficient HTML file.

    :param tree: Parsed HTML tree representing the document structure.
    """
    for comment in tree.find_all(string=lambda c: isinstance(c, bs4.Comment)):
        comment.extract()


def add_copy_to_headerlinks(tree: bs4.BeautifulSoup) -> None:
    """Add "copy to clipboard" functionality to header links.

    This function enhances all anchor tags with the `headerlink` class
    by binding a JavaScript event handler that copies the link's URL to
    the clipboard when clicked.

    :param tree: Parsed HTML tree representing the document structure.
    """
    for link in tree.select("a.headerlink"):
        link["@click.prevent"] = (
            "window.navigator.clipboard.writeText($el.href);"
        )
        del link["title"]
        link["aria-label"] = "Copy link"


def open_links_in_new_tab(tree: bs4.BeautifulSoup) -> None:
    """Ensure external links open in a new tab with proper security
    attributes.

    This function modifies all anchor tags marked with the class
    `reference external`, adding `rel="nofollow noopener"` attributes.
    These attributes prevent potential security risks such as reverse
    tabnabbing by ensuring that new tabs cannot manipulate the referring
    page.

    :param tree: Parsed HTML tree representing the document structure.
    """
    for link in tree("a", class_="reference external"):
        link["rel"] = "nofollow noopener"
        link["target"] = "_blank"


def postprocess(html: str) -> None:
    """Perform post-processing on an HTML document after the Sphinx
    build.

    This function reads an HTML file, parses it into a BeautifulSoup
    tree, applies various transformations such as adding collapsible
    navigation, cleaning up empty elements and removing comments and
    finally writes the modified content back to the file.

    Post-processing ensures that the generated HTML is not only
    functional but also clean, optimised and dynamic according to the
    user's configuration options.

    :param html: Path to the HTML file to be post-processed.

    .. versionchanged:: 31.8.2026

        Dropped the unused `app` parameter, instead of keeping it and
        reassigning it to itself just to appease the linter.
    """
    with open(html, encoding="utf-8") as f:
        tree = bs4.BeautifulSoup(f, "html.parser")
    open_links_in_new_tab(tree)
    add_copy_to_headerlinks(tree)
    make_toc_collapsible(tree)
    remove_empty_toctree_divs(tree)
    remove_comments(tree)
    with open(html, "w", encoding="utf-8") as f:
        f.write(str(tree))


def plain(text: str) -> str:
    """Flatten a snippet of rendered HTML down to bare text.

    A page title reaches the context already rendered, so a heading
    carrying an icon role arrives as markup. Shoving that straight
    into a `<meta>` tag leaks escaped `<span>` soup into every
    scraper's preview, which is not a great look.

    Only things that actually look like a tag are stripped, so a
    description reading "when x < 5 and y > 0" keeps its middle
    rather than having it swallowed whole.

    :param text: Rendered HTML, or plain text.
    :return: The text with tags removed, entities resolved and
        whitespace collapsed onto a single line.

    .. versionadded:: 10.9.2026
    """
    return " ".join(unescape(TAG_RE.sub("", text)).split())


def summarise(doctree: nodes.document | None, limit: int) -> str:
    """Build a plain-text summary from a document's first paragraph.

    Walks the resolved doctree for the first body paragraph that is not
    part of a figure, admonition, table or code block, flattens it to
    text and truncates it on a word boundary.

    :param doctree: The resolved doctree, or `None` for generated pages.
    :param limit: Maximum length of the returned summary.
    :return: A single-line summary, or an empty string when the page has
        no usable prose.
    """
    if doctree is None:
        return ""
    for paragraph in findall(doctree, nodes.paragraph):
        parent: nodes.Element | None = paragraph.parent
        while parent is not None and not isinstance(parent, SOCIAL_SKIP):
            parent = parent.parent
        if parent is not None:
            continue
        text = " ".join(paragraph.astext().split())
        if len(text) < 40:
            continue
        if len(text) <= limit:
            return text
        return text[:limit].rsplit(" ", 1)[0].rstrip(",;:.") + "\u2026"
    return ""


def social_metadata(
    app: Sphinx,
    _pagename: str,
    _templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Expose Open Graph and Twitter card values to the page context.

    Replaces `sphinxext-opengraph`, which pulled in `matplotlib` purely
    to render social cards. Everything here is derived from the doctree
    and `html_context`, so the build stays dependency-free.

    Each value prefers the page's own `:og:*` field, then the
    theme-wide default in `html_context`, then whatever can be
    salvaged from the page itself. The docinfo keys keep their `og:`
    prefix, so they are looked up under that name and not the bare
    one.

    :param app: The Sphinx application instance.
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree, or `None` for generated pages.

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


def env_before_read_docs(
    app: Sphinx, _: BuildEnvironment, docnames: list[str]
) -> None:
    """Track the list of documents modified during the Sphinx build.

    This function captures the list of document names that have been
    added, updated, or deleted and stores them in the Sphinx
    environment for later use. This ensures that post-processing only
    affects pages that have actually changed, optimising the build
    process by avoiding unnecessary rework.

    :param app: The Sphinx application instance.
    :param _: The current build environment (unused).
    :param docnames: A list of document names that were modified.

    .. versionchanged:: 31.8.2026

        Stores `theme_htmls` via `setattr()` rather than a direct
        attribute assignment, since `BuildEnvironment` doesn't declare
        it statically.
    """
    setattr(app.env, "theme_htmls", docnames)  # noqa: B010


def ensure_classes_on_nodes(
    _app: Sphinx, doctree: nodes.document, _docname: str
) -> None:
    """Make sure classes are handled properly on node-tree.

    This patched function fixes the breaking code in sphinx's internal
    structure when the nodes with no classes are not handled properly.

    :param _app: The Sphinx application instance (unused).
    :param doctree: The resolved doctree for the document.
    :param _docname: The name of the document (unused).

    .. versionchanged:: 31.8.2026

        Was annotated and called for a different Sphinx event; fixed to
        match `doctree-resolved`'s actual `(app, doctree, docname)`
        signature and to use `findall()` instead of the removed
        `.traverse()` call.
    """
    for node in findall(doctree, nodes.Element):
        node.setdefault("classes", [])


def last_updated_date(app: Sphinx, docname: str, source: list[str]) -> None:
    """Inject the last updated date into the document's metadata.

    This function checks if the `last_updated` metadata is already set
    for the given document. If not, it attempts to extract the last
    updated date from a special comment in the document source. If no
    such comment is found, it falls back to using the last commit date
    from Git. If the document is not tracked by Git, it uses the file's
    last modified timestamp.

    :param app: The Sphinx application instance.
    :param docname: The name of the document being processed.
    :param source: The source content of the document as a list of
        strings.

    .. versionchanged:: 31.8.2026

        Fixed a `dt.timezone.utc` typo: `dt` is the `datetime` class
        (aliased from `datetime.datetime`), which has no `timezone`
        attribute; now uses `datetime.UTC` directly.
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


def build_finished(app: Sphinx, exc: Exception | None) -> None:
    """Post-processes HTML documents after the Sphinx build, applying
    final modifications to the output files.

    This function is triggered after the build process is completed. It
    checks if there are any errors and if the builder is set to produce
    `HTML` or `dirhtml` output. It then applies final transformations
    to the list of modified documents stored in the environment, such as
    collapsible navigation and comment removal.

    :param app: Sphinx application object.
    :param exc: Any exception raised during the build process, or None
        if no exceptions occurred.

    Execute post-processing steps after the Sphinx build is complete.

    Once the Sphinx build process concludes — and if no errors occurred
    — this function processes each modified HTML file by applying the
    necessary transformations (collapsible ToCs, link adjustments,
    etc.). Only HTML or directory-style HTML (`dirhtml`) builds are
    considered.

    If an exception occurs during the build, post-processing is skipped
    to avoid further complications.

    :param app: The Sphinx application instance.
    :param exc: An exception raised during the build process, or `None`
        if the build was successful.

    .. versionchanged:: 31.8.2026

        Reads `theme_htmls` via `getattr()` and narrows `app.builder` to
        `StandaloneHTMLBuilder` with `t.cast()`, since neither is
        declared on the general `BuildEnvironment`/`Builder` types.
    """
    if exc or app.builder.name not in {"html", "dirhtml"}:
        return
    builder = t.cast("StandaloneHTMLBuilder", app.builder)
    htmls = getattr(app.env, "theme_htmls", [])
    htmls = [str(builder.get_outfilename(html)) for html in htmls]
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
