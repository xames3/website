"""\
Columns Directive
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 23 October 2026
Last updated on: 07 November 2026

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

from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import close
from kaamiki.extensions.utils import hollow
from kaamiki.extensions.utils import located
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import through
from kaamiki.extensions.utils import what
from kaamiki.extensions.utils.checks import fail
from kaamiki.extensions.utils.checks import location
from kaamiki.extensions.utils.settings import GAPS
from kaamiki.extensions.utils.settings import MARGINS
from kaamiki.extensions.utils.settings import SIZES

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "columns"
depart = close
COLUMNS: t.Final[int] = 6
VALIGNS: t.Final[tuple[str, ...]] = ("top", "middle", "bottom")
STACKS: t.Final[tuple[str, ...]] = ("left", "center")


class Columns(nodes.container):
    """The columns and what is in them, waiting for `visit`."""


class item(nodes.container):
    """One column and its content."""


count = checks.integer(1, COLUMNS)


def span(argument: str | None) -> str:
    """Check how many columns a column takes.

    :param argument: The number as written or `auto`.
    :return: The number of columns, as written, or `auto`.
    :raises ValueError: If it's neither.
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


class directive(rst.Directive):
    """The `columns` directive.

    Options::

        - `gap`: The space between columns. `small`, the default,
          `medium` or `large`, or lengths in `rem` that replace them,
          up to 4rem: one for both directions, like `1.5rem`, or two as
          the row gap then the column gap, like `1rem 2rem`.
        - `valign`: Where columns of different heights line up, `top`,
          `middle`, the default or `bottom`.
        - `flush`: Take off the space above the first thing in each
          column and below the last, so the gap and the margin decide
          the spacing. A column with a `padding`, `border` or
          `background` already does.
        - `padding`: The space inside each column. `small`, `medium` or
          `large`, or lengths in `rem` like `gap`, as the space above
          and below then at the sides when there are two. A column with
          a `border` or a `background` has `1rem` without it.
        - `border`: Draw a 1px border and rounded corners around each
          column.
        - `background`: Fill each column, with rounded corners.
        - `margin`: The space above and below the columns. `small`,
          `medium`, the default, or `large`, or lengths in `rem` up to
          8rem: one for both, or two as above then below, like
          `5rem 2rem`.
        - `stack-align`: How the text in the columns lines up when they
          stack on a phone, `left`, the default, or `center`.
        - `class-column`: More classes for every column in them.
        - `name`: A name to link to.
        - `class`: More classes for the columns.

    The argument is the number of columns, from 1 to 6. A `column` goes
    inside for each piece. On a phone every column takes the full
    width, except one with `:span: auto`, which keeps its own width and
    is centred.

    A set of columns goes in nothing narrower than the page's text, so
    not in a column that doesn't span its set, nor in a block that
    isn't `large`.
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
        "class-column": checks.classes,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the columns and return the set.

        :return: The set's node.
        """
        options = self.options
        try:
            number = count(self.arguments[0])
        except ValueError as error:
            raise self.error(f"columns: {error}") from error
        element = located(
            self, Columns("", classes=list(options.get("class", [])))
        )
        element["columns"] = number
        element["gap"] = options.get("gap", "small")
        element["valign"] = options.get("valign", "middle")
        element["flush"] = "flush" in options
        element["padding"] = options.get("padding", "")
        element["margin"] = options.get("margin", "")
        element["stack"] = options.get("stack-align", "left")
        element["border"] = "border" in options
        element["background"] = "background" in options
        element["column_classes"] = list(options.get("class-column", []))
        named(self, element)
        self.state.nested_parse(self.content, self.content_offset, element)
        found = list(through(element.children))
        if any(
            isinstance(_, nodes.system_message) and _["level"] >= 3
            for _ in found
        ):
            return [element]
        skipped = (item, nodes.comment, nodes.target, nodes.system_message)
        if stray := next(
            (_ for _ in found if not isinstance(_, skipped)), None
        ):
            raise self.error(
                "columns: expected column directives and nothing else, got"
                f" {what(stray)}"
            )
        reported = (item, nodes.system_message)
        if not any(isinstance(_, reported) for _ in found):
            raise self.error("columns: expected at least 1 column, got none")
        for each in found:
            if not isinstance(each, item):
                continue
            if each["span"] != "auto" and int(each["span"]) > number:
                fail(
                    f"column: :span: expected 1 to {number}, got"
                    f" {each['span']!r}",
                    location(each),
                )
            each["classes"] = [*element["column_classes"], *each["classes"]]
        padded = ("padding", "border", "background")
        if "flush" in options and any(_ in options for _ in padded):
            raise self.error(
                "columns: :flush: not allowed with :padding:, :border: or"
                " :background:, which flush each column already"
            )

        return [element]


class column(rst.Directive):
    """The `column` directive.

    Options::

        - `span`: How many of the columns it takes, or `auto` to be as
          wide as its content. A column without it takes one.
        - `name`: A name to link to.
        - `class`: More classes for the column.
    """

    has_content = True
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "span": span,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the content and return the column.

        :return: The column's node.
        """
        if not isinstance(self.state.parent, (Columns, addnodes.only)):
            raise self.error(
                "column: expected inside columns, got it on its own"
            )
        options = self.options
        element = located(
            self, item("", classes=list(options.get("class", [])))
        )
        element["span"] = options.get("span", "1")
        named(self, element)
        self.state.nested_parse(self.content, self.content_offset, element)
        if hollow(element.children):
            raise self.error("column: expected some content, got none")
        return [element]


def visit(self: HTMLTranslator, node: Columns) -> None:
    """Open the columns.

    :param self: The HTML translator, whose body this appends to.
    :param node: The columns' node.
    """
    styles = []
    gap, padding = node["gap"], node["padding"]
    classes = ["km-columns", f"km-columns--count-{node['columns']}"]
    if node["valign"] != "middle":
        classes.append(f"km-columns--valign-{node['valign']}")
    if gap in SIZES:
        if gap != "small":
            classes.append(f"km-columns--gap-{gap}")
    else:
        vertical, horizontal = checks.lengths(gap)
        styles += [
            f"--km-columns-gap-y: {vertical}",
            f"--km-columns-gap-x: {horizontal}",
        ]
    if padding in SIZES:
        classes.append(f"km-columns--padding-{padding}")
    elif padding:
        styles.append(f"--km-columns-padding: {padding}")
    margin = node["margin"]
    if margin in SIZES:
        classes.append(f"km-columns--margin-{margin}")
    elif margin:
        above, below = checks.lengths(margin)
        styles += [
            f"--km-columns-margin-top: {above}",
            f"--km-columns-margin-bottom: {below}",
        ]
    if node["stack"] == "center":
        classes.append("km-columns--stack-align-center")
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


def visit_item(self: HTMLTranslator, node: item) -> None:
    """Open a column.

    :param self: The HTML translator, whose body this appends to.
    :param node: The column's node.
    """
    classes = f"km-columns__column km-columns__column--span-{node['span']}"
    self.body.append(self.starttag(node, "div", "", CLASS=classes))


def register(app: Sphinx) -> None:
    """Register the `column` directive and the node only columns have.

    :param app: The Sphinx application instance.
    """
    app.add_directive("column", column)
    app.add_node(item, html=(visit_item, close))


node = Columns
