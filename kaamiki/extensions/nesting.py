"""\
Nesting Checks
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 30 October 2026
Last updated on: 15 November 2026

Stops a page that puts a directive where it makes no sense, or a class
that only works on the page itself.
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
from sphinx import addnodes

from kaamiki.extensions import block
from kaamiki.extensions import columns
from kaamiki.extensions import release
from kaamiki.extensions import tabs
from kaamiki.extensions.code import explain
from kaamiki.extensions.code import version
from kaamiki.extensions.utils import KaamikiDirective
from kaamiki.extensions.utils import checks

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from sphinx.application import Sphinx


def is_raw(node: nodes.Node) -> bool:
    """Say whether a node is a block of HTML an author wrote.

    Such a block can hold anything.

    :param node: The node to look at.
    :return: `True` for a `raw` block with something in it.
    """
    return (
        isinstance(node, nodes.raw)
        and bool(node.astext().strip())
        and not isinstance(node.parent, nodes.TextElement)
    )


PLURAL: t.Final[frozenset[str]] = frozenset({"columns", "tabs"})
PAGE: t.Final[dict[str, str]] = {
    "byline": "on the page itself",
    "code-explain": "on the page itself",
    "code-version": "on the page itself",
    "release": "directly in a section",
}
WIDE: t.Final[str] = "km-wide"
FIXED: t.Final[tuple[str, ...]] = ("embed", "thumbnail")
EXPLAINERS: t.Final[tuple[str, ...]] = ("code-explain", "code-version")
CLICKABLE: t.Final[tuple[str, ...]] = (
    "accordion",
    "carousel",
    "embed",
    "tabs",
    "video",
    "youtube",
)
HEAVY: t.Final[tuple[str, ...]] = (
    "accordion",
    "block",
    "carousel",
    "columns",
    "embed",
    "raw",
    "repository",
    "tabs",
    "thumbnail",
    "video",
    "youtube",
)
SETS: t.Final[tuple[tuple[type, type, str, str], ...]] = (
    (tabs.Tab.Node, tabs.Tabs.Node, "tab", "tabs"),
    (columns.Column.Node, columns.Columns.Node, "column", "columns"),
)
PARTS: t.Final[tuple[type[nodes.Element], ...]] = (
    explain.Explanations,
    explain.Explanation,
    version.Attempt,
    version.Draft,
)
HOSTS: t.Final[tuple[tuple[type, str], ...]] = (
    (tabs.Tab.Node, "a tab"),
    (columns.Column.Node, "a column"),
    (block.Part, "a block"),
    (nodes.list_item, "a list"),
    (nodes.entry, "a table"),
    (nodes.definition, "a definition list"),
    (nodes.block_quote, "a block quote"),
    (nodes.topic, "a topic"),
    (nodes.sidebar, "a sidebar"),
    (nodes.footnote, "a footnote"),
    (nodes.field_body, "a field list"),
    (nodes.legend, "a figure"),
    (nodes.compound, "a compound"),
)


def is_part(node: nodes.Node) -> bool:
    """Say whether a node only holds a piece of a directive's content.

    :param node: The node to look at.
    :return: `True` for the notes of a walkthrough, an attempt or a
        release's body, which the message names by what they are in.
    """
    if isinstance(node, PARTS):
        return True
    return type(node) is nodes.container and release.Release.made(node.parent)


def is_wrapper(node: nodes.Node) -> bool:
    """Say whether a node only wraps something that sits on the page.

    A block comes in a row of blocks, a code block with a caption in a
    box of its own and a picture that links in its link, so the class
    that's on what's inside is on the page.

    :param node: The node to look at.
    :return: `True` for a row of blocks, a captioned code block's box
        and a link that holds nothing but a picture.
    """
    if isinstance(node, block.Shelf):
        return True
    if isinstance(node, nodes.reference):
        return bool(node.children) and all(
            isinstance(_, nodes.image) for _ in node.children
        )
    return type(node) is nodes.container and bool(node.get("literal_block"))


def kind(node: nodes.Node) -> str:
    """Name the directive a node was written by.

    :param node: The node to look at.
    :return: The directive's name or an empty string for any other
        node.
    """
    for name, directive in KaamikiDirective.registry.items():
        if directive.made(node):
            return name
    return "raw" if is_raw(node) else ""


def open_to_page(node: nodes.Node) -> bool:
    """Say whether a node is part of the page itself.

    That's where the page's own directives go.

    :param node: The node to look at.
    :return: `True` for the document, a section that isn't a release
        and an `only`. A plain `container` isn't, since an author's
        wrapper takes the width a walkthrough needs.
    """
    if isinstance(node, (nodes.document, addnodes.only)):
        return True
    return isinstance(node, nodes.section) and not release.Release.made(node)


def article(name: str) -> str:
    """Put `a` or `an` in front of a name.

    :param name: The name.
    :return: The name with its article, `an accordion`.
    """
    return f"an {name}" if name[0] in "aeiou" else f"a {name}"


def describe(node: nodes.Node) -> str:
    """Say what a node is, the way a message names it.

    A directive is named after itself and an admonition after its kind,
    so a warning isn't a note. A block is named after its size when it
    isn't large and after its link when it has one.

    :param node: The node to look at.
    :return: Its name with an article, `an accordion`.
    """
    if isinstance(node, block.Block.Node):
        size = "" if node["size"] == "large" else f"{node['size']} "
        links = " that links" if node["link"] else ""
        return f"{article(f'{size}block')}{links}"
    name = kind(node)
    if name in PLURAL:
        return name
    if name:
        return article(name)
    if isinstance(node, addnodes.versionmodified):
        return article(node["type"])
    if isinstance(node, nodes.Admonition):
        return article(type(node).__name__.lower())
    for host, text in HOSTS:
        if isinstance(node, host):
            return text
    return article(type(node).__name__.replace("_", " "))


def ancestors(node: nodes.Node) -> Iterator[nodes.Node]:
    """Walk up from a node, nearest first.

    :param node: Where to start, which isn't given.
    :return: Each node above it.
    """
    parent = node.parent
    while parent is not None:
        yield parent
        parent = parent.parent


def holder(node: nodes.Node) -> nodes.Node | None:
    """Find what holds a node, an `only` aside.

    :param node: The node to look at.
    :return: The nearest node above it that isn't an `only`.
    """
    return next(
        (_ for _ in ancestors(node) if not isinstance(_, addnodes.only)),
        None,
    )


def narrow(host: nodes.Node) -> bool:
    """Say whether a host is narrower than the page's text.

    A set of columns has no room in a host like that.

    :param host: One of the nodes above the columns.
    :return: `True` for a column that doesn't span its set and for a
        block that isn't large.
    """
    if isinstance(host, columns.Column.Node):
        whole = holder(host)
        count = (
            whole["columns"] if isinstance(whole, columns.Columns.Node) else 1
        )
        return host["span"] == "auto" or int(host["span"]) < count
    return isinstance(host, block.Block.Node) and host["size"] != "large"


def refused(name: str, host: nodes.Node) -> bool:
    """Say whether a directive can't sit in a host.

    :param name: The directive's name.
    :param host: One of the nodes above it.
    :return: `True` when it can't.
    """
    if kind(host) in EXPLAINERS:
        return name in HEAVY
    if name == "block" and kind(host) == "block":
        return True
    if (
        isinstance(host, block.Block.Node)
        and host["link"]
        and name in CLICKABLE
    ):
        return True
    if name == "carousel" and isinstance(host, columns.Column.Node):
        return True
    return name == "columns" and narrow(host)


def unplaced(node: nodes.Node) -> nodes.Element | None:
    """Find what keeps a node from being part of the page itself.

    :param node: The node to look at.
    :return: The nearest node above it that isn't part of the page, a
        wrapper or a part of a directive, or `None` for a node on the
        page.
    """
    return next(
        (
            _
            for _ in ancestors(node)
            if isinstance(_, nodes.Element)
            and not (open_to_page(_) or is_part(_) or is_wrapper(_))
        ),
        None,
    )


def nested(app: Sphinx, doctree: nodes.document) -> None:
    """Stop the build for a directive that sits where it can't.

    A `km-wide` goes on the page itself, since a block in a tab, a column
    or a list has no room to widen into. It doesn't go on an embed or a
    thumbnail either, as their iframe and still keep the size they have.

    :param app: The Sphinx application instance (unused).
    :param doctree: The page, just read.
    :raises KaamikiError: For the first directive or `km-wide` in the
        wrong place.
    """
    del app
    for node in doctree.findall(nodes.Element):
        where = checks.location(node)
        for part, whole, one, many in SETS:
            if isinstance(node, part) and not isinstance(holder(node), whole):
                checks.fail(
                    f"{one}: expected inside {many}, got it on its own", where
                )
        if WIDE in node["classes"]:
            outside = unplaced(node)
            if outside is not None:
                advice = (
                    ", use :figclass: instead"
                    if isinstance(outside, nodes.figure)
                    and isinstance(node, nodes.image)
                    else ""
                )
                checks.fail(
                    f"{WIDE}: expected directly on the page, got it in"
                    f" {describe(outside)}{advice}",
                    where if node.line else checks.location(outside),
                )
            if kind(node) in FIXED:
                checks.fail(
                    f"{WIDE}: expected something it can widen, got"
                    f" {describe(node)}",
                    where,
                )
        name = kind(node)
        if not name:
            continue
        if name in PAGE:
            host = next(
                (
                    _
                    for _ in ancestors(node)
                    if not open_to_page(_) and not is_part(_)
                ),
                None,
            )
            if host is not None:
                checks.fail(
                    f"{name}: expected {PAGE[name]}, got it in"
                    f" {describe(host)}",
                    where,
                )
        for host in ancestors(node):
            if refused(name, host):
                checks.fail(
                    f"{name}: expected somewhere else, got it in"
                    f" {describe(host)}",
                    where,
                )
