"""\
Block Directive
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 23 October 2026
Last updated on: 25 October 2026

A `block` directive that frames a title and some content, which
can link somewhere::

    .. block:: Why write xsNumPy?
       :subtitle: A story from January 2025
       :url: xsnumpy
       :type: doc

       An experimental re-implementation of a few of the core NumPy
       features in pure Python.
"""

import re
import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions import columns
from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import document
from kaamiki.extensions.utils import hollow
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import opens_new_tab
from kaamiki.extensions.utils import titled
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils.checks import fail
from kaamiki.extensions.utils.checks import location
from kaamiki.extensions.utils.links import REL

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "block"
SPANS: t.Final[tuple[str, ...]] = ("small", "medium", "large")
TYPES: t.Final[tuple[str, ...]] = ("doc", "ref", "url")
LABEL: t.Final[re.Pattern[str]] = re.compile(r"[\w.-]+")


class node(nodes.container):
    """The block and what's in it, waiting for `visit`."""


class shelf(nodes.container):
    """A run of same-sized blocks, written one after another, in a row."""


class part(nodes.container):
    """A part of a block that holds other nodes, like its body."""


class blocktext(nodes.paragraph):
    """A part of a block that holds text, like its title."""


class directive(rst.Directive):
    """The `block` directive.

    Options::

        - `subtitle`: A smaller line under the title.
        - `header`: Text above the title, with roles like
          `:fa-icon:regular:`heart` Love`.
        - `footer`: Text at the bottom, written like `header`.
        - `url`: Where the block goes. The whole block links there.
        - `type`: What `url` is, `doc` for a document, `ref` for a label
          or `url` for an address, the default.
        - `span`: How wide it is when blocks sit side by side, `small`
          for three in a line, `medium` for two or `large`, the
          default, for one.
        - `name`: A name to link to.
        - `class`: More classes for the block.

    The argument is the title and everything below is the content.
    Blocks of the same `span` written one after another form rows,
    unless they are inside `rows`, which decide where they go. A
    `large` block is a row of its own and a block of another span starts
    a new row.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "subtitle": checks.text,
        "header": checks.text,
        "footer": checks.text,
        "url": checks.text,
        "type": checks.word(*TYPES),
        "span": checks.word(*SPANS),
    }

    def inline(
        self, role: str, text: str
    ) -> tuple[blocktext, list[nodes.system_message]]:
        """Parse a line of text the way a paragraph is parsed.

        :param role: The part of the block it is, as its class knows it.
        :param text: The text, as written.
        :return: The parsed text and whatever the parsing reported.
        """
        words, messages = self.state.inline_text(text, self.lineno)
        return blocktext(text, "", *words, role=role), messages

    def run(self) -> list[nodes.Node]:
        """Parse the parts and return the block.

        :return: The block, or the row of blocks it starts, followed by
            whatever the parsing reported. A block that joins the row
            before it returns only what the parsing reported.
        """
        options = self.options
        url = options.get("url", "")
        kind = options.get("type", "url")
        if "type" in options and not url:
            raise self.error("block: :type: requires :url:")
        if url and kind == "url":
            try:
                checks.link(url)
            except ValueError as error:
                raise self.error(f"block: :url: {error}") from error
        elif kind == "doc":
            url = document(self, url, "url")
        elif url and not LABEL.fullmatch(url):
            raise self.error(f"block: :url: expected a ref name, got {url!r}")
        element = node("", classes=list(options.get("class", [])))
        element.source, element.line = self.state_machine.get_source_and_line(
            self.lineno
        )
        element["span"] = options.get("span", "large")
        element["url"] = url
        element["kind"] = kind
        named(self, element)
        messages: list[nodes.system_message] = []
        if "header" in options:
            header, found = self.inline("header", options["header"])
            element += header
            messages += found
        content = part("", role="body")
        title, found = self.inline("title", titled(self, self.arguments[0]))
        element["label"] = title.astext()
        content += title
        messages += found
        subtitle_node = None
        if "subtitle" in options:
            subtitle_node, found = self.inline("subtitle", options["subtitle"])
            content += subtitle_node
            messages += found
        self.state.nested_parse(self.content, self.content_offset, content)
        if hollow(
            c
            for c in content.children
            if c is not title and c is not subtitle_node
        ):
            raise self.error("block: expected some content, got none")
        element += content
        if "footer" in options:
            footer, found = self.inline("footer", options["footer"])
            element += footer
            messages += found
        if kind == "url":
            for reference in trail({"url": url}, ("url",)):
                element += reference
        parent = self.state.parent
        if isinstance(parent, columns.item):
            return [element, *messages]
        previous = parent.children[-1] if parent.children else None
        if (
            isinstance(previous, shelf)
            and element["span"] != "large"
            and previous["last"] == element["span"]
        ):
            previous += element
            previous["last"] = element["span"]
            return [*messages]
        row = shelf("", last=element["span"])
        row += element
        return [row, *messages]


def address(self: HTMLTranslator, node: node) -> tuple[str, bool]:
    """Work out where a block goes.

    :param self: The HTML translator.
    :param node: The block's node.
    :return: The address, as it reads from this page, and whether it
        opens in a new tab. An address that leads nowhere is `#`.
    """
    builder = self.builder
    here = builder.current_docname
    url, kind = node["url"], node["kind"]
    if kind == "url":
        return url, opens_new_tab(url, builder.config)
    if kind == "doc":
        return builder.get_relative_uri(here, url), False
    labels = builder.env.domains.standard_domain.labels
    target = labels.get(url.lower())
    if target is None:
        fail(f"block: :url: {url!r} is not a label", location(node))
    page = target[0]
    base = "" if page == here else builder.get_relative_uri(here, page)
    return f"{base}#{target[1]}", False


def link(self: HTMLTranslator, node: node) -> str:
    """Write a block's link.

    :param self: The HTML translator.
    :param node: The block's node.
    :return: The link, which covers the whole block.
    """
    href, new_tab = address(self, node)
    attributes = [
        'class="km-block__link"',
        f'href="{self.attval(href)}"',
        f'aria-label="{self.attval(node["label"])}"',
    ]
    if new_tab:
        attributes += ['target="_blank"', f'rel="{REL}"']
    return f"<a {' '.join(attributes)}></a>"


def visit(self: HTMLTranslator, node: node) -> None:
    """Open the block.

    :param self: The HTML translator, whose body this appends to.
    :param node: The block's node.
    """
    classes = ["km-block", f"km-block--{node['span']}"]
    if node["url"]:
        classes.append("km-block--link")
    self.body.append(self.starttag(node, "div", "", CLASS=" ".join(classes)))


def depart(self: HTMLTranslator, node: node) -> None:
    """Close the block, with its link as the last thing in it.

    :param self: The HTML translator, whose body this appends to.
    :param node: The block's node.
    """
    if node["url"]:
        self.body.append(link(self, node))
    self.body.append("</div>")


def visit_shelf(self: HTMLTranslator, node: shelf) -> None:
    """Open a row of blocks.

    :param self: The HTML translator, whose body this appends to.
    :param node: The row's node.
    """
    self.body.append(self.starttag(node, "div", "", CLASS="km-blocks"))


def depart_shelf(self: HTMLTranslator, node: shelf) -> None:
    """Close a row of blocks.

    :param self: The HTML translator, whose body this appends to.
    :param node: The row's node (unused).
    """
    del node
    self.body.append("</div>")


def visit_part(self: HTMLTranslator, node: part) -> None:
    """Open a part of a block.

    :param self: The HTML translator, whose body this appends to.
    :param node: The part's node.
    """
    self.body.append(
        self.starttag(node, "div", "", CLASS=f"km-block__{node['role']}")
    )


def depart_part(self: HTMLTranslator, node: part) -> None:
    """Close a part of a block.

    :param self: The HTML translator, whose body this appends to.
    :param node: The part's node (unused).
    """
    del node
    self.body.append("</div>")


def visit_blocktext(self: HTMLTranslator, node: blocktext) -> None:
    """Open a line of a block's text.

    :param self: The HTML translator, whose body this appends to.
    :param node: The line's node.
    """
    self.body.append(
        self.starttag(node, "div", "", CLASS=f"km-block__{node['role']}")
    )


def depart_blocktext(self: HTMLTranslator, node: blocktext) -> None:
    """Close a line of a block's text.

    :param self: The HTML translator, whose body this appends to.
    :param node: The line's node (unused).
    """
    del node
    self.body.append("</div>")


def register(app: Sphinx) -> None:
    """Register the nodes only a block has.

    :param app: The Sphinx application instance.
    """
    app.add_node(shelf, html=(visit_shelf, depart_shelf))
    app.add_node(part, html=(visit_part, depart_part))
    app.add_node(blocktext, html=(visit_blocktext, depart_blocktext))
