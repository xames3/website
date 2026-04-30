"""\
Theme Utilities
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February, 2025
Last updated on: 14 January, 2026

This module defines a collection of utility functions used for
customising this sphinx theme. These utilities focus on enhancing the
post-processing of the generated HTML output, as well as providing
additional support for interactive elements, theme options, and other
dynamic behaviours.

The functionality provided includes handling collapsible table of
contents (ToC), removal of unnecessary elements, and custom event
handling for theme-specific features.

The goal of this module is to ensure that this theme produces clean,
efficient, and interactive HTML documentation by leveraging Sphinx's
internal APIs and dynamic JavaScript bindings.

.. deprecated:: 19.10.2025

    Use of `website_options` in favour of `html_context`. This removes
    the need of `register_website_options` function.
"""

from __future__ import annotations

import re
import shlex
import typing as t
from datetime import datetime as dt
from pathlib import Path
from subprocess import CalledProcessError
from subprocess import check_output as co

import bs4
from docutils import nodes
from sphinx.util.display import status_iterator

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment

LAST_UPDATED_RE: re.Pattern[str] = re.compile(
    r"^\.\.\s+Last updated on:\s*(.+)$", re.IGNORECASE
)


def findall(
    node: nodes.Node,
    element: type[nodes.reference | nodes.bullet_list],
) -> t.Any:
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
    :return: An iterable containing all matching elements found within
        the given node.
    """
    findall = "findall" if hasattr(node, "findall") else "traverse"
    return getattr(node, findall)(element)


def make_toc_collapsible(tree: bs4.BeautifulSoup) -> None:
    """Enhance the left sidebar's ToC with collapsible branches.

    This attaches an adjacent toggle button after links that have a
    following ``ul``. The button uses theme CSS for a down chevron via a
    pseudo element. No Alpine attributes or inline SVGs are injected.

    :param tree: Parsed HTML tree to mutate.
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
        parent["class"] = list(
            set((parent.get("class") or []) + ["has-children"])
        )
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
    (those containing only whitespace or line breaks), and removes them
    to maintain a clean and optimised document structure.

    :param tree: Parsed HTML tree representing the document structure.
    """
    for div in tree.select("div.toctree-wrapper"):
        if len(div.contents) == 1 and not div.contents[0].strip():
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


def postprocess(html: str, app: Sphinx) -> None:
    """Perform post-processing on an HTML document after the Sphinx
    build.

    This function reads an HTML file, parses it into a BeautifulSoup
    tree, applies various transformations such as adding collapsible
    navigation, cleaning up empty elements, and removing comments, and
    finally writes the modified content back to the file.

    Post-processing ensures that the generated HTML is not only
    functional but also clean, optimised, and dynamic according to the
    user's configuration options.

    :param html: Path to the HTML file to be post-processed.
    :param app: The Sphinx application instance, used to access the
        current build's options and environment.
    """
    app = app or None  # Just to satisfy type checkers
    with open(html, encoding="utf-8") as f:
        tree = bs4.BeautifulSoup(f, "html.parser")
    open_links_in_new_tab(tree)
    add_copy_to_headerlinks(tree)
    make_toc_collapsible(tree)
    remove_empty_toctree_divs(tree)
    remove_comments(tree)
    with open(html, "w", encoding="utf-8") as f:
        f.write(str(tree))


def env_before_read_docs(
    app: Sphinx, _: BuildEnvironment, docnames: list[str]
) -> None:
    """Track the list of documents modified during the Sphinx build.

    This function captures the list of document names that have been
    added, updated, or deleted, and stores them in the Sphinx
    environment for later use. This ensures that post-processing only
    affects pages that have actually changed, optimising the build
    process by avoiding unnecessary rework.

    :param app: The Sphinx application instance.
    :param _: The current build environment (unused).
    :param docnames: A list of document names that were modified.
    """
    app.env.theme_htmls = docnames


def ensure_classes_on_nodes(
    app: Sphinx, doctree: BuildEnvironment, docnames: list[str]
) -> None:
    """Make sure classes are handled properly on node-tree.

    This patched function fixes the breaking code in sphinx's internal
    structure when the nodes with no classes are not handled properly.

    :param app: The Sphinx application instance (unused).
    :param doctree: The current build environment.
    :param docname: List of document names that are modified (unused).
    """
    app = app or docnames  # Just to satisfy type checkers
    for node in doctree.traverse(nodes.Element):
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
            shlex.quote(str(src)),
        ]
        on = co(cmd, cwd=app.confdir).decode().strip()  # noqa: S603
    except (CalledProcessError, FileNotFoundError):
        on = ""
    if not on:
        timestamp = src.stat().st_mtime
        try:
            tz = dt.now().astimezone().tzinfo or dt.timezone.utc
            on = dt.fromtimestamp(timestamp, tz=tz).strftime("%b %d, %Y")
        except FileNotFoundError:
            on = ""
    if on:
        metadata["last_updated"] = on


def build_finished(app: Sphinx, exc: Exception | None) -> None:
    """Post-processes HTML documents after the Sphinx build, applying
    final modifications to the output files.

    This function is triggered after the build process is completed. It
    checks if there are any errors, and if the builder is set to produce
    `HTML` or `dirhtml` output. It then applies final transformations
    to the list of modified documents stored in the environment, such as
    collapsible navigation, and comment removal.

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
    """
    if exc or app.builder.name not in {"html", "dirhtml"}:
        return
    htmls = [app.builder.get_outfilename(html) for html in app.env.theme_htmls]
    if not htmls:
        return
    for html in status_iterator(
        htmls,
        "Postprocessing... ",
        "darkgreen",
        len(htmls),
        app.verbosity,
    ):
        postprocess(html, app)
