"""\
Nesting Checks
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 30 October 2026
Last updated on: 16 November 2026

Stop a page that puts a directive where it cannot work, or a class
that works only on the page itself.
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
from kaamiki.extensions.utils.hooks import on

if t.TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Iterator

    from sphinx.application import Sphinx


def is_raw(node: nodes.Node) -> bool:
    """Say whether a node is a block of HTML from an author.

    :param node: The node to look at.
    :return: `True` for a `raw` block with text in it, which can hold
        anything.
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
CELLS: t.Final[tuple[str, ...]] = ("carousel", "columns", "tabs", "youtube")
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
    """Say whether a node holds a part of a directive.

    :param node: The node to look at.
    :return: `True` for the notes of a walkthrough, an attempt, or the
        body of a release. The message names them by what holds them.
    """
    if isinstance(node, PARTS):
        return True
    return type(node) is nodes.container and release.Release.made(node.parent)


def is_wrapper(node: nodes.Node) -> bool:
    """Say whether a node only wraps a node that is on the page.

    :param node: The node to look at.
    :return: `True` for a row of blocks, the box of a code block with a
        caption, and a link that holds only a picture. A class on what
        they hold is on the page.
    """
    if isinstance(node, block.Shelf):
        return True
    if isinstance(node, nodes.reference):
        return bool(node.children) and all(
            isinstance(_, nodes.image) for _ in node.children
        )
    return type(node) is nodes.container and bool(node.get("literal_block"))


def kind(node: nodes.Node) -> str:
    """Name the directive that wrote a node.

    :param node: The node to look at.
    :return: The name of the directive, or an empty string for another
        node.
    """
    for name, directive in KaamikiDirective.registry.items():
        if directive.made(node):
            return name
    return "raw" if is_raw(node) else ""


def open_to_page(node: nodes.Node) -> bool:
    """Say whether a node is part of the page itself.

    :param node: The node to look at.
    :return: `True` for the document, a section that is not a release,
        and an `only`. A plain `container` is not part of the page,
        because a wrapper from an author takes the width that a
        walkthrough needs.
    """
    if isinstance(node, (nodes.document, addnodes.only)):
        return True
    return isinstance(node, nodes.section) and not release.Release.made(node)


def article(name: str) -> str:
    """Put `a` or `an` before a name.

    :param name: The name.
    :return: The name with its article, as `an accordion`.
    """
    return f"an {name}" if name[0] in "aeiou" else f"a {name}"


def describe(node: nodes.Node) -> str:
    """Say what a node is, as a message names it.

    :param node: The node to look at.
    :return: Its name with an article, as `an accordion`. A directive
        gets its own name, and an admonition gets its kind, so a
        warning is not a note. A block gets its size when it is not
        large, and its link when it has one.
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

    :param node: The node to start from, which is not included.
    :return: Each node above it.
    """
    parent = node.parent
    while parent is not None:
        yield parent
        parent = parent.parent


def holder(node: nodes.Node) -> nodes.Node | None:
    """Find what holds a node, but not an `only`.

    :param node: The node to look at.
    :return: The nearest node above it that is not an `only`.
    """
    return next(
        (_ for _ in ancestors(node) if not isinstance(_, addnodes.only)),
        None,
    )


def narrow(host: nodes.Node) -> bool:
    """Say whether a host is narrower than the text of the page.

    :param host: One of the nodes above the columns.
    :return: `True` for a column that does not span its set, and for a
        block that is not large. Columns do not fit in it.
    """
    if isinstance(host, columns.Column.Node):
        whole = holder(host)
        count = (
            whole["columns"] if isinstance(whole, columns.Columns.Node) else 1
        )
        return host["span"] == "auto" or int(host["span"]) < count
    return isinstance(host, block.Block.Node) and host["size"] != "large"


class Rule(t.NamedTuple):
    """A place where some directives cannot be.

    :param names: The directives that cannot be there.
    :param place: The place, as a message names it.
    :param holds: Says whether a host is that place.
    """

    names: tuple[str, ...]
    place: str
    holds: Callable[[nodes.Node], bool]


RULES: t.Final[tuple[Rule, ...]] = (
    Rule(HEAVY, "a code-explain", lambda _: kind(_) == "code-explain"),
    Rule(HEAVY, "a code-version", lambda _: kind(_) == "code-version"),
    Rule(("block",), "a block", lambda _: kind(_) == "block"),
    Rule(
        CLICKABLE,
        "a block that links",
        lambda _: isinstance(_, block.Block.Node) and bool(_["link"]),
    ),
    Rule(
        ("carousel",),
        "a column",
        lambda _: isinstance(_, columns.Column.Node),
    ),
    Rule(("tabs",), "a tab", lambda _: isinstance(_, tabs.Tab.Node)),
    Rule(CELLS, "a table", lambda _: isinstance(_, nodes.entry)),
    Rule(("columns",), "a narrow column or block", narrow),
)


def refused(name: str, host: nodes.Node) -> bool:
    """Say whether a directive cannot be in a host.

    :param name: The name of the directive.
    :param host: One of the nodes above it.
    :return: `True` when it cannot be there.
    """
    return any(name in _.names and _.holds(host) for _ in RULES)


def places(name: str) -> str:
    """Name the places where a directive cannot be.

    :param name: The name of the directive.
    :return: The places, as `a column and a table`.
    """
    *first, last = [_.place for _ in RULES if name in _.names]
    return f"{', '.join(first)} and {last}" if first else last


def unplaced(node: nodes.Node) -> nodes.Element | None:
    """Find what keeps a node from the page itself.

    :param node: The node to look at.
    :return: The nearest node above it that is not part of the page, a
        wrapper, or a part of a directive, or `None` for a node on the
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


@on("doctree-read", priority=150)
def nested(app: Sphinx, doctree: nodes.document) -> None:
    """Stop the build for a directive in a place where it cannot be.

    :param app: The Sphinx application instance (unused).
    :param doctree: The page, just read.
    :raises KaamikiError: For the first directive or `km-wide` in the
        wrong place. `km-wide` goes on the page itself, because a block
        in a tab, a column or a list has no space to widen. It cannot
        go on an embed or a thumbnail, because their iframe and still
        keep their size.
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
                    f"{name}: expected outside {places(name)}, got it in"
                    f" {describe(host)}",
                    where,
                )
