"""\
Block Directive
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 23 October 2026
Last updated on: 07 November 2026

A `block` directive that frames a title and some content, which
can link somewhere::

    .. block:: Why write xsNumPy?
       :subsection: A story from January 2025
       :doc: xsnumpy

       An experimental re-implementation of a few of the core NumPy
       features in pure Python.
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions import columns
from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import close
from kaamiki.extensions.utils import document
from kaamiki.extensions.utils import hollow
from kaamiki.extensions.utils import located
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import opens_new_tab
from kaamiki.extensions.utils import titled
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

name: t.Final[str] = "block"
LINKS: t.Final[tuple[str, ...]] = ("target", "doc", "ref")


class Block(nodes.container):
    """The block and what's in it, waiting for `visit`."""


class shelf(nodes.container):
    """A run of same-sized blocks, written one after another, in a
    row.
    """


class part(nodes.container):
    """A part of a block that holds other nodes, like its body."""


class blocktext(nodes.paragraph):
    """A part of a block that holds text, like its title."""


class directive(rst.Directive):
    """The `block` directive.

    Options::

        - `subsection`: A smaller line under the title.
        - `header`: Text above the title, with roles like
          `:fa-icon:regular:`heart` Love`.
        - `footer`: Text at the bottom, written like `header`.
        - `target`: An address the whole block links to.
        - `doc`: A document the whole block links to, as `:doc:` names
          it.
        - `ref`: A label the whole block links to, as `:ref:` names it,
          capitals and spaces aside.
        - `size`: How wide it is when blocks sit side by side, `small`
          for three in a line, `medium` for two or `large`, the
          default, for one.
        - `name`: A name to link to.
        - `class`: More classes for the block.

    The argument is the title and everything below is the content. A
    block takes one of `target`, `doc` and `ref`, and is one link as a
    whole, so an accordion, tabs, a video, a player, an embed or a
    walkthrough in it stops the build. A block holds no other block and
    one that isn't `large` holds no columns. Blocks of the same `size`
    written one after another form rows. Blocks inside a column, at any
    depth, form no rows, each is as wide as the column. A `large` block
    is a row of its own and a block of another size starts a new row.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "subsection": checks.text,
        "header": checks.text,
        "footer": checks.text,
        "target": checks.link,
        "doc": checks.text,
        "ref": checks.text,
        "size": checks.word(*SIZES),
    }

    def inline(
        self, role: str, text: str, *, linked: bool
    ) -> tuple[blocktext, list[nodes.system_message]]:
        """Parse a line of text the way a paragraph is parsed.

        :param role: The part of the block it is as its class knows it.
        :param text: The text, as written.
        :param linked: Whether the whole block is a link, which the
            text can't hold another of.
        :return: The parsed text and whatever the parsing reported.
        :raises rst.DirectiveError: For a link in a block that is one.
        """
        words, messages = self.state.inline_text(text, self.lineno)
        worded(self, words, f"a {role}")
        if linked:
            unlinked(self, words, f"a {role}")
        return located(self, blocktext(text, "", *words, role=role)), messages

    def run(self) -> list[nodes.Node]:
        """Parse the parts and return the block.

        :return: The block, or the row of blocks it starts, followed by
            whatever the parsing reported. A block that joins the row
            before it returns only what the parsing reported. A row in
            a column is taken apart once the page is read, see `unrow`.
        """
        options = self.options
        given = [_ for _ in LINKS if _ in options]
        if len(given) > 1:
            raise self.error(
                f"block: :{given[0]}: not allowed with :{given[1]}:"
            )
        kind = given[0] if given else ""
        link = options.get(kind, "")
        if kind == "doc":
            link = document(self, link, "doc")
        element = located(
            self, Block("", classes=list(options.get("class", [])))
        )
        element["size"] = options.get("size", "large")
        element["link"] = link
        element["kind"] = kind
        named(self, element)
        messages: list[nodes.system_message] = []
        if "header" in options:
            header, found = self.inline(
                "header", options["header"], linked=bool(kind)
            )
            element += header
            messages += found
        content = part("", role="body")
        title, found = self.inline(
            "title", titled(self, self.arguments[0]), linked=bool(kind)
        )
        element["label"] = title.astext()
        content += title
        messages += found
        subsection_node = None
        if "subsection" in options:
            subsection_node, found = self.inline(
                "subsection", options["subsection"], linked=bool(kind)
            )
            content += subsection_node
            messages += found
        self.state.nested_parse(self.content, self.content_offset, content)
        if hollow(
            c
            for c in content.children
            if c is not title and c is not subsection_node
        ):
            raise self.error("block: expected some content, got none")
        element += content
        if "footer" in options:
            footer, found = self.inline(
                "footer", options["footer"], linked=bool(kind)
            )
            element += footer
            messages += found
        if kind == "target":
            for reference in trail({"target": link}, ("target",)):
                element += reference
        parent = self.state.parent
        previous = parent.children[-1] if parent.children else None
        if (
            isinstance(previous, shelf)
            and element["size"] != "large"
            and previous["last"] == element["size"]
        ):
            previous += element
            previous["last"] = element["size"]
            return [*messages]
        row = shelf("", last=element["size"])
        row += element
        return [row, *messages]


def address(
    self: HTMLTranslator, name: str, kind: str, link: str, where: str
) -> tuple[str, bool]:
    """Work out where a block or a button goes.

    :param self: The HTML translator.
    :param name: The directive, for the message.
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
        fail(f"{name}: :ref: expected a label, got {link!r}", where)
    page = label[0]
    base = "" if page == here else builder.get_relative_uri(here, page)
    return f"{base}#{label[1]}", False


def anchor(self: HTMLTranslator, node: Block) -> str:
    """Write a block's link.

    :param self: The HTML translator.
    :param node: The block's node.
    :return: The link, which covers the whole block.
    """
    href, new_tab = address(
        self, "block", node["kind"], node["link"], location(node)
    )
    attributes = [
        'class="km-block__link"',
        f'href="{self.attval(href)}"',
        f'aria-label="{self.attval(node["label"])}"',
    ]
    if new_tab:
        attributes += ['target="_blank"', f'rel="{REL}"']
    return f"<a {' '.join(attributes)}></a>"


def visit(self: HTMLTranslator, node: Block) -> None:
    """Open the block.

    :param self: The HTML translator, whose body this appends to.
    :param node: The block's node.
    """
    classes = ["km-block"]
    if node["size"] != "large":
        classes.append(f"km-block--size-{node['size']}")
    if node["link"]:
        classes.append("km-block--link")
    self.body.append(self.starttag(node, "div", "", CLASS=" ".join(classes)))


def depart(self: HTMLTranslator, node: Block) -> None:
    """Close the block, with its link as the last thing in it.

    :param self: The HTML translator, whose body this appends to.
    :param node: The block's node.
    """
    if node["link"]:
        self.body.append(anchor(self, node))
    self.body.append("</div>")


def visit_shelf(self: HTMLTranslator, node: shelf) -> None:
    """Open a row of blocks.

    :param self: The HTML translator, whose body this appends to.
    :param node: The row's node.
    """
    self.body.append(self.starttag(node, "div", "", CLASS="km-block-row"))


def visit_piece(self: HTMLTranslator, node: part | blocktext) -> None:
    """Open a part of a block, or a line of its text.

    :param self: The HTML translator, whose body this appends to.
    :param node: The part's or the line's node.
    """
    self.body.append(
        self.starttag(node, "div", "", CLASS=f"km-block__{node['role']}")
    )


def unrow(app: Sphinx, doctree: nodes.document) -> None:
    """Take the blocks out of the rows that sit in a column.

    A column decides where its blocks go, however deep they are in it,
    so they are not put side by side. A row is made as the blocks are
    parsed, when what they are in isn't known yet.

    :param app: The Sphinx application instance (unused).
    :param doctree: The page, just read.
    """
    del app
    for row in list(doctree.findall(shelf)):
        host = row.parent
        while host is not None and not isinstance(host, columns.item):
            host = host.parent
        if host is not None:
            row.replace_self(list(row.children))


def register(app: Sphinx) -> None:
    """Register the nodes only a block has and the check on their rows.

    :param app: The Sphinx application instance.
    """
    app.connect("doctree-read", unrow)
    app.add_node(shelf, html=(visit_shelf, close))
    app.add_node(part, html=(visit_piece, close))
    app.add_node(blocktext, html=(visit_piece, close))


node = Block
