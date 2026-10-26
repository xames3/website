"""\
Columns Directive
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 23 October 2026
Last updated on: 25 October 2026

A `columns` directive that sets `rows` directives side by side::

    .. columns:: 3
       :gap: medium

       .. rows::

          First.

       .. rows::
          :span: 2

          Second, as wide as two.
"""

import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import hollow
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils.settings import GAPS
from kaamiki.extensions.utils.settings import MARGINS

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "columns"
COLUMNS: t.Final[int] = 6
SIZES: t.Final[tuple[str, ...]] = ("small", "medium", "large")
VALIGNS: t.Final[tuple[str, ...]] = ("top", "center", "bottom")
STACKS: t.Final[tuple[str, ...]] = ("start", "center")


class node(nodes.container):
    """The columns and their rows, waiting for `visit`."""


class item(nodes.container):
    """One row and its content."""


count = checks.integer(1, COLUMNS)


def span(argument: str | None) -> str:
    """Check how many columns a row takes.

    :param argument: The number as written or `auto`.
    :return: The number of columns, as written, or `auto`.
    :raises ValueError: If it's neither.
    """
    if argument == "auto":
        return argument
    try:
        return str(checks.integer(1, COLUMNS)(argument))
    except ValueError as error:
        raise ValueError(
            f"expected auto or a whole number from 1 to {COLUMNS}, got "
            f"{argument!r}"
        ) from error


class directive(rst.Directive):
    """The `columns` directive.

    Options::

        - `gap`: The space between rows. `small`, the default,
          `medium` or `large`, or lengths in `rem` that replace them:
          one for both directions, like `1.5rem`, or two as the row gap
          then the column gap, like `1rem 2rem`.
        - `valign`: Where rows of different heights line up, `top`,
          `center`, the default or `bottom`.
        - `flush`: Take off the space above the first thing in each row
          and below the last, so the gap and the margin decide the
          spacing. A row with a `padding`, `border` or `background`
          already does.
        - `padding`: The space inside each row. `small`, `medium` or
          `large`, or lengths in `rem` like `gap`, as the space above
          and below then at the sides when there are two. A row with a
          `border` or a `background` has `1rem` without it.
        - `border`: Draw a border and rounded corners around each row.
        - `background`: Fill each row, with rounded corners.
        - `margin`: The space above and below the columns. `small`,
          `medium`, the default, or `large`, or lengths in `rem`: one
          for both, or two as above then below, like `5rem 2rem`.
        - `stack-align`: How the text in the rows lines up when they
          stack on a phone, `start`, the default, or `center`.
        - `name`: A name to link to.
        - `class`: More classes for the columns.
        - `class-row`: More classes for every row in them.

    The argument is the number of columns, from 1 to 6. A `rows` goes
    inside for each piece. On a phone every row takes the full width.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "gap": checks.spacing(SIZES, GAPS),
        "valign": checks.word(*VALIGNS),
        "flush": rst.directives.flag,
        "padding": checks.spacing(SIZES, GAPS),
        "border": rst.directives.flag,
        "background": rst.directives.flag,
        "margin": checks.spacing(SIZES, MARGINS),
        "stack-align": checks.word(*STACKS),
        "class-row": checks.classes,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the rows and return the columns.

        :return: The columns' node.
        """
        options = self.options
        try:
            number = count(self.arguments[0])
        except ValueError as error:
            raise self.error(f"columns: {error}") from error
        element = node("", classes=list(options.get("class", [])))
        element["columns"] = number
        element["gap"] = options.get("gap", "small")
        element["valign"] = options.get("valign", "center")
        element["flush"] = "flush" in options
        element["padding"] = options.get("padding", "")
        element["margin"] = options.get("margin", "")
        element["stack"] = options.get("stack-align", "start")
        element["border"] = "border" in options
        element["background"] = "background" in options
        element["rows"] = list(options.get("class-row", []))
        named(self, element)
        self.state.nested_parse(self.content, self.content_offset, element)
        if any(
            isinstance(_, nodes.system_message) and _["level"] >= 3
            for _ in element.children
        ):
            return [element]
        skipped = (item, nodes.comment, nodes.target, nodes.system_message)
        if any(not isinstance(_, skipped) for _ in element.children):
            raise self.error(
                "columns: expected rows directives and nothing else"
            )
        reported = (item, nodes.system_message)
        if not any(isinstance(_, reported) for _ in element.children):
            raise self.error("columns: expected at least 1 rows, got none")
        padded = ("padding", "border", "background")
        if "flush" in options and any(_ in options for _ in padded):
            raise self.error(
                "columns: :flush: not allowed with :padding:, :border: or"
                " :background:, which flush each row already"
            )

        return [element]


class rows(rst.Directive):
    """The `rows` directive.

    Options::

        - `span`: How many columns the row takes, or `auto` to be as
          wide as its content. One column without it.
        - `name`: A name to link to.
        - `class`: More classes for the row.
    """

    has_content = True
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "span": span,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the content and return the row.

        :return: The row's node.
        """
        parent = self.state.parent
        if not isinstance(parent, node):
            raise self.error("rows: expected to be inside columns")
        options = self.options
        size = options.get("span", "1")
        if size != "auto" and int(size) > parent["columns"]:
            raise self.error(
                f"rows: :span: {size} is more than the {parent['columns']} "
                "columns"
            )
        classes = [*parent["rows"], *options.get("class", [])]
        element = item("", classes=classes)
        element["span"] = size
        named(self, element)
        self.state.nested_parse(self.content, self.content_offset, element)
        if hollow(element.children):
            raise self.error("rows: expected some content, got none")
        return [element]


def visit(self: HTMLTranslator, node: node) -> None:
    """Open the columns.

    :param self: The HTML translator, whose body this appends to.
    :param node: The columns' node.
    """
    styles = []
    gap, padding = node["gap"], node["padding"]
    classes = [
        "km-columns",
        f"km-columns--{node['columns']}",
        f"km-columns--valign-{node['valign']}",
    ]
    if gap in SIZES:
        classes.append(f"km-columns--gap-{gap}")
    else:
        rows, columns = gap.split()[0], gap.split()[-1]
        styles += [
            f"--km-columns-gap-y: {rows}",
            f"--km-columns-gap-x: {columns}",
        ]
    if padding in SIZES:
        classes.append(f"km-columns--padding-{padding}")
    elif padding:
        styles.append(f"--km-columns-padding: {padding}")
    margin = node["margin"]
    if margin in SIZES:
        classes.append(f"km-columns--margin-{margin}")
    elif margin:
        above, below = margin.split()[0], margin.split()[-1]
        styles += [
            f"--km-columns-margin-top: {above}",
            f"--km-columns-margin-bottom: {below}",
        ]
    if node["stack"] == "center":
        classes.append("km-columns--stack-center")
    if node["border"]:
        classes.append("km-columns--border")
    if node["background"]:
        classes.append("km-columns--background")
    if padding or node["border"] or node["background"]:
        classes.append("km-columns--padded")
    if node["flush"] or padding or node["border"] or node["background"]:
        classes.append("km-columns--flush")
    attributes: dict[str, t.Any] = {"CLASS": " ".join(classes)}
    if styles:
        attributes["style"] = "; ".join(styles)
    self.body.append(self.starttag(node, "div", "", **attributes))


def depart(self: HTMLTranslator, node: node) -> None:
    """Close the columns.

    :param self: The HTML translator, whose body this appends to.
    :param node: The columns' node (unused).
    """
    del node
    self.body.append("</div>")


def visit_item(self: HTMLTranslator, node: item) -> None:
    """Open a row.

    :param self: The HTML translator, whose body this appends to.
    :param node: The row's node.
    """
    classes = f"km-columns__row km-columns__row--span-{node['span']}"
    self.body.append(self.starttag(node, "div", "", CLASS=classes))


def depart_item(self: HTMLTranslator, node: item) -> None:
    """Close a row.

    :param self: The HTML translator, whose body this appends to.
    :param node: The row's node (unused).
    """
    del node
    self.body.append("</div>")


def register(app: Sphinx) -> None:
    """Register the `rows` directive and the node only columns have.

    :param app: The Sphinx application instance.
    """
    app.add_directive("rows", rows)
    app.add_node(item, html=(visit_item, depart_item))
