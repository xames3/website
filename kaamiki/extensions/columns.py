"""\
Columns Directive
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 23 October 2026
Last updated on: 15 November 2026

A `columns` directive that sets `column` directives side by side::

    .. columns:: 3
       :gap: medium

       .. column::

          First.

       .. column::
          :span: 2

          Second, as wide as two.
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst
from sphinx import addnodes

from kaamiki.extensions.utils import BEM
from kaamiki.extensions.utils import KaamikiDirective
from kaamiki.extensions.utils import Option
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import through
from kaamiki.extensions.utils import what
from kaamiki.extensions.utils.checks import fail
from kaamiki.extensions.utils.checks import location
from kaamiki.extensions.utils.settings import GAPS
from kaamiki.extensions.utils.settings import MARGINS
from kaamiki.extensions.utils.settings import SIZES

if t.TYPE_CHECKING:
    from sphinx.writers.html import HTMLTranslator

columns: t.Final[BEM] = BEM("columns")
COLUMNS: t.Final[int] = 6
VALIGNS: t.Final[tuple[str, ...]] = ("top", "middle", "bottom")
STACKS: t.Final[tuple[str, ...]] = ("left", "center")
count = checks.integer(1, COLUMNS)


def span_count(argument: str | None) -> str:
    """Check how many columns a column takes.

    :param argument: The number as written, or `auto`.
    :return: The number of columns as written, or `auto`.
    :raises ValueError: When it is not a number or `auto`.
    """
    if argument == "auto":
        return argument
    try:
        return str(count(argument))
    except ValueError as error:
        raise ValueError(
            f"expected auto or a whole number from 1 to {COLUMNS}, got "
            f"{argument!r}"
        ) from error


class Columns(KaamikiDirective):
    """The `columns` directive.

    Options::

        - `gap`: The space between columns, `small`, `medium` or
          `large`. The default is `small`. A length in `rem`, up to
          4rem, can replace them. Write one length for the two
          directions, as `1.5rem`, or two lengths for the row gap and
          the column gap, as `1rem 2rem`.
        - `valign`: Where columns of different heights align, `top`,
          `middle` or `bottom`. The default is `middle`.
        - `flush`: Remove the space above the first item in each column
          and below the last item. Then the gap and the margin set the
          spacing. A column with a `padding`, `border` or `background`
          is flush already.
        - `padding`: The space in each column, `small`, `medium` or
          `large`. Lengths in `rem`, as for `gap`, can replace them: the
          space above and below, then the space at the sides. A column
          with a `border` or a `background` has `1rem` without it.
        - `border`: Put a 1px border with round corners around each
          column.
        - `background`: Fill each column, with round corners.
        - `margin`: The space above and below the columns, `small`,
          `medium` or `large`. The default is `medium`. A length in
          `rem`, up to 8rem, can replace them. Write one length for the
          two, or two lengths for above and below, as `5rem 2rem`.
        - `stack-align`: How the text in the columns aligns when they
          stack on a phone, `left` or `center`. The default is `left`.
        - `class-column`: More classes for each column.
        - `name`: A name for links.
        - `class`: More classes for the columns.

    The argument is the number of columns, from 1 to 6. Put one `column`
    in it for each item. On a phone, each column takes the full width.
    A column with `:span: auto` keeps its width and goes in the center.

    Columns cannot go in a container that is narrower than the text of
    the page. Thus they cannot go in a column that does not span its
    set, or in a block that is not `large`.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = False
    gap = Option(checks.spacing(SIZES, GAPS), default="small")
    valign = Option(checks.word(*VALIGNS), default="middle")
    flush = Option(rst.directives.flag)
    padding = Option(checks.spacing(SIZES, GAPS), default="")
    border = Option(rst.directives.flag)
    background = Option(rst.directives.flag)
    margin = Option(checks.spacing(SIZES, MARGINS), default="")
    stack_align = Option(checks.word(*STACKS), default="left")
    class_column = Option(checks.classes, default=())

    class Node(nodes.container):
        """The columns and their content."""

    def check(self) -> None:
        """Refuse `flush` with an option that makes a column flush."""
        if self.flush and (self.padding or self.border or self.background):
            self.fail(
                ":flush: not allowed with :padding:, :border: or"
                " :background:, since a column with one is flush already"
            )

    def build(self) -> list[nodes.Node]:
        """Make the columns and give each column its classes.

        :return: The node of the columns.
        """
        try:
            number = count(self.arguments[0])
        except ValueError as error:
            self.fail(str(error))
        node = self.locate(self.Node("", classes=self.classes))
        node["columns"] = number
        node["gap"] = self.gap
        node["valign"] = self.valign
        node["flush"] = self.flush
        node["padding"] = self.padding
        node["margin"] = self.margin
        node["stack"] = self.stack_align
        node["border"] = self.border
        node["background"] = self.background
        node["column_classes"] = [*self.class_column]
        self.add_name(node)
        self.state.nested_parse(self.content, self.content_offset, node)
        found = list(through(node.children))
        if any(
            isinstance(each, nodes.system_message) and each["level"] >= 3
            for each in found
        ):
            return [node]
        skipped = (
            Column.Node,
            nodes.comment,
            nodes.target,
            nodes.system_message,
        )
        if stray := next(
            (each for each in found if not isinstance(each, skipped)), None
        ):
            self.fail(
                "expected column directives and nothing else, got"
                f" {what(stray)}"
            )
        reported = (Column.Node, nodes.system_message)
        if not any(isinstance(each, reported) for each in found):
            self.fail("expected at least 1 column, got none")
        for each in found:
            if not isinstance(each, Column.Node):
                continue
            if each["span"] != "auto" and int(each["span"]) > number:
                fail(
                    f"column: :span: expected 1 to {number}, got"
                    f" {each['span']!r}",
                    location(each),
                )
            each["classes"] = [*node["column_classes"], *each["classes"]]
        return [node]


class Column(KaamikiDirective):
    """The `column` directive.

    Options::

        - `span`: How many columns it takes, or `auto` to make it as
          wide as its content. Without it, a column takes one.
        - `name`: A name for links.
        - `class`: More classes for the column.
    """

    has_content = True
    span = Option(span_count, default="1")

    class Node(nodes.container):
        """One column and its content."""

    def check(self) -> None:
        """Permit a column only in columns."""
        if not isinstance(self.state.parent, (Columns.Node, addnodes.only)):
            self.fail("expected inside columns, got it on its own")

    def build(self) -> list[nodes.Node]:
        """Make the column with its content.

        :return: The column's node.
        """
        node = self.locate(self.Node("", classes=self.classes))
        node["span"] = self.span
        self.add_name(node)
        self.fill(node)
        return [node]


@html.opens(Columns.Node)
def visit(self: HTMLTranslator, node: Columns.Node) -> None:
    """Open the columns.

    :param self: The HTML translator, whose body this appends to.
    :param node: The columns' node.
    """
    styles: list[str] = []
    gap, padding = node["gap"], node["padding"]
    modifiers = [f"count-{node['columns']}"]
    if node["valign"] != "middle":
        modifiers.append(f"valign-{node['valign']}")
    if gap in SIZES:
        if gap != "small":
            modifiers.append(f"gap-{gap}")
    else:
        vertical, horizontal = checks.lengths(gap)
        styles += [
            f"--km-columns-gap-y: {vertical}",
            f"--km-columns-gap-x: {horizontal}",
        ]
    if padding in SIZES:
        modifiers.append(f"padding-{padding}")
    elif padding:
        styles.append(f"--km-columns-padding: {padding}")
    margin = node["margin"]
    if margin in SIZES:
        modifiers.append(f"margin-{margin}")
    elif margin:
        above, below = checks.lengths(margin)
        styles += [
            f"--km-columns-margin-top: {above}",
            f"--km-columns-margin-bottom: {below}",
        ]
    if node["stack"] == "center":
        modifiers.append("stack-align-center")
    if node["border"]:
        modifiers.append("border")
    if node["background"]:
        modifiers.append("background")
    if padding or node["border"] or node["background"]:
        modifiers.append("padded")
    if node["flush"] or padding or node["border"] or node["background"]:
        modifiers.append("flush")
    attributes: dict[str, t.Any] = {"CLASS": columns(*modifiers)}
    if styles:
        attributes["style"] = "; ".join(styles)
    self.body.append(self.starttag(node, "div", "", **attributes))


html.closes(Columns.Node, "</div>")


@html.opens(Column.Node)
def visit_column(self: HTMLTranslator, node: Column.Node) -> None:
    """Open a column.

    :param self: The HTML translator, whose body this appends to.
    :param node: The column's node.
    """
    classes = columns.column(f"span-{node['span']}")
    self.body.append(self.starttag(node, "div", "", CLASS=classes))


html.closes(Column.Node, "</div>")
