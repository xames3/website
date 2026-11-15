"""\
Block Directive
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 23 October 2026
Last updated on: 15 November 2026

A `block` directive that frames a title and some content, which
can link somewhere::

    .. block:: Getting started
       :subheader: A short guide
       :target: https://example.com/guide

       Everything you need to set up and start writing.
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes

from kaamiki.extensions import columns
from kaamiki.extensions.utils import BEM
from kaamiki.extensions.utils import KaamikiDirective
from kaamiki.extensions.utils import Option
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import document
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import opens_new_tab
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import unlinked
from kaamiki.extensions.utils import worded
from kaamiki.extensions.utils.checks import fail
from kaamiki.extensions.utils.checks import location
from kaamiki.extensions.utils.links import REL
from kaamiki.extensions.utils.settings import SIZES

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

block: t.Final[BEM] = BEM("block")
row: t.Final[BEM] = BEM("block-row")
LINKS: t.Final[tuple[str, ...]] = ("target", "doc", "ref")


class Shelf(nodes.container):
    """A row of blocks of the same size."""


class Part(nodes.container):
    """A part of a block that holds other nodes, as its body."""


class BlockText(nodes.paragraph):
    """A part of a block that holds text, as its title."""


class Block(KaamikiDirective):
    """The `block` directive.

    Options::

        - `preheader`: A small line above the title. It can have roles,
          as `:fa-icon:regular:`heart` Love`.
        - `subheader`: A smaller line below the title.
        - `footer`: Text at the bottom, written as `preheader`.
        - `target`: An address. The full block is a link to it.
        - `doc`: A document, named as `:doc:` names it. The full block
          is a link to it.
        - `ref`: A label, named as `:ref:` names it. Capitals and
          spaces do not change the label. The full block is a link to
          it.
        - `size`: The width when blocks are side by side, `small` for
          three in a row, `medium` for two or `large` for one. The
          default is `large`.
        - `name`: A name for links.
        - `class`: More classes for the block.

    The argument is the title, and the lines below it are the content.
    A block can have only one of `target`, `doc` and `ref`. Then the
    full block is one link, so the build stops when it holds an
    `accordion`, `carousel`, `embed`, `tabs`, `video` or `youtube`. A
    block cannot hold a block, and a block that is not `large` cannot
    hold columns. Blocks of the same `size`, one after the other, make
    a row. Blocks in a column, at all depths, do not make rows. Each
    block is as wide as the column. A `large` block is a row by itself,
    and a block of a different size starts a new row.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    preheader = Option(checks.text)
    subheader = Option(checks.text)
    footer = Option(checks.text)
    target = Option(checks.link)
    doc = Option(checks.text)
    ref = Option(checks.text)
    size = Option(checks.word(*SIZES), default="large")

    class Node(nodes.container):
        """The block and its content."""

    @property
    def links(self) -> list[str]:
        """The options that make the full block a link."""
        return [each for each in LINKS if each in self.options]

    @property
    def kind(self) -> str:
        """The option that makes the full block a link, or nothing."""
        return next(iter(self.links), "")

    def check(self) -> None:
        """Permit only one of `target`, `doc` and `ref`."""
        if len(self.links) > 1:
            first, second = self.links[:2]
            self.fail(f":{first}: not allowed with :{second}:")

    def line(
        self, role: str, written: str
    ) -> tuple[BlockText, list[nodes.system_message]]:
        """Parse a line of text as a paragraph is parsed.

        :param role: The part of the block, as `title` or `footer`.
        :param written: The text, as written in the rST.
        :return: The parsed text and what the parser reported.
        """
        words, messages = self.state.inline_text(written, self.lineno)
        worded(self, words, f"a {role}")
        if self.kind:
            unlinked(self, words, f"a {role}")
        return self.locate(BlockText(written, "", *words, role=role)), messages

    def build(self) -> list[nodes.Node]:
        """Make the block, or the row of blocks that it starts.

        :return: The block or its row, then what the parser reported. A
            block that joins the row before it gives only what the
            parser reported. A row in a column comes apart when the page
            is read, see `unrow`.
        """
        kind = self.kind
        link = getattr(self, kind) if kind else ""
        if kind == "doc":
            link = document(self, link, "doc")
        node = self.locate(self.Node("", classes=self.classes))
        node["size"] = self.size
        node["link"] = link
        node["kind"] = kind
        self.add_name(node)
        messages: list[nodes.system_message] = []
        if self.preheader:
            preheader, found = self.line("preheader", self.preheader)
            node += preheader
            messages += found
        content = Part("", role="body")
        title, found = self.line("title", self.title)
        node["label"] = title.astext()
        content += title
        messages += found
        if self.subheader:
            subheader, found = self.line("subheader", self.subheader)
            content += subheader
            messages += found
        self.fill(content, besides=(BlockText,))
        node += content
        if self.footer:
            footer, found = self.line("footer", self.footer)
            node += footer
            messages += found
        if kind == "target":
            for reference in trail(self, {"target": link}, ("target",)):
                node += reference
        parent = self.state.parent
        previous = parent.children[-1] if parent.children else None
        if (
            isinstance(previous, Shelf)
            and node["size"] != "large"
            and previous["last"] == node["size"]
        ):
            previous += node
            previous["last"] = node["size"]
            return [*messages]
        shelf = Shelf("", last=node["size"])
        shelf += node
        return [shelf, *messages]


def address(
    self: HTMLTranslator, caller: str, kind: str, link: str, where: str
) -> tuple[str, bool]:
    """Work out where a block or a button goes.

    :param self: The HTML translator.
    :param caller: The directive, for the message.
    :param kind: `target` for an address, `doc` for a document or `ref`
        for a label.
    :param link: The address, the document or the label.
    :param where: `source:line` the directive is at.
    :return: The address, as it reads from this page, and whether it
        opens in a new tab.
    :raises KaamikiError: For a `:ref:` that names no label, as the
        build stops instead of linking to nowhere.
    """
    builder = self.builder
    here = builder.current_docname
    if kind == "target":
        return link, opens_new_tab(link, builder.config)
    if kind == "doc":
        return builder.get_relative_uri(here, link), False
    labels = builder.env.domains.standard_domain.labels
    label = labels.get(nodes.fully_normalize_name(link))
    if label is None:
        fail(f"{caller}: :ref: expected a label, got {link!r}", where)
    page = label[0]
    base = "" if page == here else builder.get_relative_uri(here, page)
    return f"{base}#{label[1]}", False


def anchor(self: HTMLTranslator, node: Block.Node) -> str:
    """Write a block's link.

    :param self: The HTML translator.
    :param node: The block's node.
    :return: The link, which covers the whole block.
    """
    href, new_tab = address(
        self, "block", node["kind"], node["link"], location(node)
    )
    attributes = [
        f'class="{block.link()}"',
        f'href="{self.attval(href)}"',
        f'aria-label="{self.attval(node["label"])}"',
    ]
    if new_tab:
        attributes += ['target="_blank"', f'rel="{REL}"']
    return f"<a {' '.join(attributes)}></a>"


@html.opens(Block.Node)
def visit(self: HTMLTranslator, node: Block.Node) -> None:
    """Open the block.

    :param self: The HTML translator, whose body this appends to.
    :param node: The block's node.
    """
    modifiers = [] if node["size"] == "large" else [f"size-{node['size']}"]
    if node["link"]:
        modifiers.append("link")
    self.body.append(self.starttag(node, "div", "", CLASS=block(*modifiers)))


@html.closes(Block.Node)
def depart(self: HTMLTranslator, node: Block.Node) -> None:
    """Close the block, with its link as the last thing in it.

    :param self: The HTML translator, whose body this appends to.
    :param node: The block's node.
    """
    if node["link"]:
        self.body.append(anchor(self, node))
    self.body.append("</div>")


@html.opens(Shelf)
def visit_shelf(self: HTMLTranslator, node: Shelf) -> None:
    """Open a row of blocks.

    :param self: The HTML translator, whose body this appends to.
    :param node: The row's node.
    """
    self.body.append(self.starttag(node, "div", "", CLASS=row()))


@html.opens(Part)
@html.opens(BlockText)
def visit_piece(self: HTMLTranslator, node: Part | BlockText) -> None:
    """Open a part of a block, or a line of its text.

    :param self: The HTML translator, whose body this appends to.
    :param node: The part's or the line's node.
    """
    classes = getattr(block, node["role"])()
    self.body.append(self.starttag(node, "div", "", CLASS=classes))


html.closes(Shelf, "</div>")
html.closes(Part, "</div>")
html.closes(BlockText, "</div>")


def unrow(app: Sphinx, doctree: nodes.document) -> None:
    """Take the blocks out of the rows that sit in a column.

    A column lays out its blocks, however deep they are in it.

    :param app: The Sphinx application instance (unused).
    :param doctree: The page, just read.
    """
    del app
    for found in list(doctree.findall(Shelf)):
        host = found.parent
        while host is not None and not isinstance(host, columns.Column.Node):
            host = host.parent
        if host is not None:
            found.replace_self(list(found.children))


def register(app: Sphinx) -> None:
    """Register the check on the rows of blocks.

    :param app: The Sphinx application instance.
    """
    app.connect("doctree-read", unrow)
