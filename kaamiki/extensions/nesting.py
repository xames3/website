"""\
Nesting Checks
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 30 October 2026
Last updated on: 07 November 2026

Stops a page that puts a directive where it makes no sense.
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
from sphinx import addnodes

from kaamiki.extensions import accordion
from kaamiki.extensions import block
from kaamiki.extensions import byline
from kaamiki.extensions import carousel
from kaamiki.extensions import columns
from kaamiki.extensions import release
from kaamiki.extensions import repository
from kaamiki.extensions import tabs
from kaamiki.extensions import thumbnail
from kaamiki.extensions import video
from kaamiki.extensions import youtube
from kaamiki.extensions.code import explain
from kaamiki.extensions.code import version
from kaamiki.extensions.utils import checks

if t.TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Iterator

    from sphinx.application import Sphinx


def is_release(node: nodes.Node | None) -> bool:
    """Say whether a node is a release, which is a section underneath.

    A release holds the node that carries its version and date, which
    no section an author writes does, whatever classes it has.

    :param node: The node to look at.
    :return: `True` for a release.
    """
    return isinstance(node, nodes.section) and any(
        isinstance(_, release.node) for _ in node.children
    )


def is_embed(node: nodes.Node) -> bool:
    """Say whether a node is an embed, which is a container underneath.

    An embed holds the `raw` node that carries its styles and scripts,
    which no container an author writes does, whatever classes it has.

    :param node: The node to look at.
    :return: `True` for an embed.
    """
    return type(node) is nodes.container and any(
        isinstance(_, nodes.raw) and "css" in _ for _ in node.children
    )


def is_raw(node: nodes.Node) -> bool:
    """Say whether a node is a block of HTML an author wrote, which can
    hold anything.

    :param node: The node to look at.
    :return: `True` for a `raw` block with something in it.
    """
    return (
        isinstance(node, nodes.raw)
        and bool(node.astext().strip())
        and not isinstance(node.parent, nodes.TextElement)
    )


KINDS: t.Final[dict[str, Callable[[nodes.Node], bool]]] = {
    "accordion": lambda _: isinstance(_, accordion.node),
    "block": lambda _: isinstance(_, block.node),
    "byline": lambda _: isinstance(_, byline.node),
    "carousel": lambda _: isinstance(_, carousel.node),
    "code-explain": lambda _: (
        isinstance(_, explain.node) and not isinstance(_, version.node)
    ),
    "code-version": lambda _: isinstance(_, version.node),
    "columns": lambda _: isinstance(_, columns.node),
    "embed": is_embed,
    "raw": is_raw,
    "release": is_release,
    "repository": lambda _: isinstance(_, repository.node),
    "tabs": lambda _: isinstance(_, tabs.node),
    "thumbnail": lambda _: isinstance(_, thumbnail.node),
    "video": lambda _: isinstance(_, video.node),
    "youtube": lambda _: isinstance(_, youtube.node),
}
PLURAL: t.Final[frozenset[str]] = frozenset({"columns", "tabs"})
PAGE: t.Final[dict[str, str]] = {
    "byline": "on the page itself",
    "code-explain": "on the page itself",
    "code-version": "on the page itself",
    "release": "directly in a section",
}
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
    (tabs.pane, tabs.node, "tab", "tabs"),
    (columns.item, columns.node, "column", "columns"),
)
PARTS: t.Final[tuple[type[nodes.Element], ...]] = (
    explain.explanations,
    explain.explanation,
    version.attempt,
    version.draft,
)
HOSTS: t.Final[tuple[tuple[type, str], ...]] = (
    (tabs.pane, "a tab"),
    (columns.item, "a column"),
    (block.part, "a block"),
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
    return type(node) is nodes.container and is_release(node.parent)


def kind(node: nodes.Node) -> str:
    """Name the directive a node was written by.

    :param node: The node to look at.
    :return: The directive's name or an empty string for any other
        node.
    """
    return next((_ for _, is_it in KINDS.items() if is_it(node)), "")


def open_to_page(node: nodes.Node) -> bool:
    """Say whether a node is part of the page itself, where the page's
    own directives go.

    :param node: The node to look at.
    :return: `True` for the document, a section that isn't a release
        and an `only`. A plain `container` isn't, since an author's
        wrapper takes the width a walkthrough needs.
    """
    if isinstance(node, (nodes.document, addnodes.only)):
        return True
    return isinstance(node, nodes.section) and not is_release(node)


def article(name: str) -> str:
    """Put `a` or `an` in front of a name.

    :param name: The name.
    :return: The name with its article, `an accordion`.
    """
    return f"an {name}" if name[0] in "aeiou" else f"a {name}"


def describe(node: nodes.Node) -> str:
    """Say what a node is, the way a message names it.

    A directive is named after itself, an admonition after its kind, so
    a warning isn't a note, and a block after its size when it isn't
    large, and after its link when it has one.

    :param node: The node to look at.
    :return: Its name with an article, `an accordion`.
    """
    if isinstance(node, block.node):
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
    """Say whether a host is narrower than the page's text, so a set of
    columns has no room in it.

    :param host: One of the nodes above the columns.
    :return: `True` for a column that doesn't span its set and for a
        block that isn't large.
    """
    if isinstance(host, columns.item):
        whole = holder(host)
        count = whole["columns"] if isinstance(whole, columns.node) else 1
        return host["span"] == "auto" or int(host["span"]) < count
    return isinstance(host, block.node) and host["size"] != "large"


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
    if isinstance(host, block.node) and host["link"] and name in CLICKABLE:
        return True
    return name == "columns" and narrow(host)


def nested(app: Sphinx, doctree: nodes.document) -> None:
    """Stop the build for a directive that sits where it can't.

    :param app: The Sphinx application instance (unused).
    :param doctree: The page, just read.
    :raises KaamikiError: For the first directive in the wrong place.
    """
    del app
    for node in doctree.findall(nodes.Element):
        where = checks.location(node)
        for part, whole, one, many in SETS:
            if isinstance(node, part) and not isinstance(holder(node), whole):
                checks.fail(
                    f"{one}: expected inside {many}, got it on its own", where
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
