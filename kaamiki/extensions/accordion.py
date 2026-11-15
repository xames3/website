"""\
Accordion Directive
===================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 23 October 2026
Last updated on: 15 November 2026

An `accordion` directive that folds its content below a title::

    .. accordion:: What's an accordion?
       :subheader: A short answer
       :marker: down
       :marker-position: before
       :open:

       It's a box that folds its content below a title.

The build stops when an accordion has no content, or when an option is
wrong, out of range or in conflict with another option. When an
accordion does not set the marker or its side,
`kaamiki.conf.accordion.marker` and
`kaamiki.conf.accordion.marker_position` set them.
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import BEM
from kaamiki.extensions.utils import KaamikiDirective
from kaamiki.extensions.utils import Option
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils.aliases import ALIASES
from kaamiki.extensions.utils.icons import ACCORDION_MARKERS
from kaamiki.extensions.utils.icons import Icons

if t.TYPE_CHECKING:
    from sphinx.writers.html import HTMLTranslator

accordion: t.Final[BEM] = BEM("accordion")
text: t.Final[BEM] = BEM("text")


class Summary(nodes.paragraph):
    """The title, parsed as rST, with the icon of the marker."""


class Headline(nodes.TextElement):
    """A line above or below the title, as its `role` tells."""


class Accordion(KaamikiDirective, motion=True):
    """The `accordion` directive.

    Options::

        - `open`: Show the content at the start. Only one accordion
          in a `group` can have it.
        - `preheader`: A small line above the title.
        - `class-preheader`: More classes for the preheader. It
          always has `km-text--preheader`. It needs `preheader`.
        - `subheader`: A dimmer line below the title.
        - `nested-subheader`: Put the subheader at the top of the
          content, not below the title. Then it shows only when the
          accordion is open. It needs `subheader`.
        - `class-subheader`: More classes for the subheader. It
          always has `km-text--subheader`. It needs `subheader`.
        - `marker`: The icon that shows that the accordion opens,
          `plus`, a `down` chevron or a `right` chevron. When the
          accordion opens, a plus turns 45 degrees, a right chevron
          turns 90 degrees to point down and a down chevron turns
          over.
        - `marker-position`: The side of the title for the marker,
          `before` or `after`.
        - `hide-show-more`: Show all of a long body. Without it, a
          body that is taller than the screen folds behind a Show
          more button.
        - `group`: A name that other accordions on the page also
          use. When one of them opens, the others in the group
          close.
        - `class-title`: More classes for the title.
        - `class-body`: More classes for the content.
        - `speed`: The speed of its motion, relative to the site,
          one of `0.25`, `0.5`, `0.75`, `1`, `1.5`, `2`, `3` or
          `4`. `2` is two times as fast.
        - `no-motion`: Do not move it.
        - `name`: A name for links. A link to the accordion, or to
          a thing in it, opens the accordion.
        - `class`: More classes for the accordion.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    open = Option(rst.directives.flag)
    preheader = Option(checks.text)
    class_preheader = Option(checks.classes, needs="preheader", default=())
    subheader = Option(checks.text)
    nested_subheader = Option(rst.directives.flag, needs="subheader")
    class_subheader = Option(checks.classes, needs="subheader", default=())
    marker = Option(setting="accordion_marker")
    marker_position = Option(setting="accordion_marker_position")
    hide_show_more = Option(rst.directives.flag)
    group = Option(checks.slug, default="")
    class_title = Option(checks.classes, default=())
    class_body = Option(checks.classes, default=())

    class Node(nodes.container):
        """The accordion and its content."""

    def check(self) -> None:
        """Permit only one open accordion in each group on the page."""
        if not (self.group and self.open):
            return
        opened = t.cast(
            "set[str]", self.env.temp_data.setdefault("km_open_groups", set())
        )
        if self.group in opened:
            self.fail(
                ":open: expected on one accordion of the group"
                f" {self.group!r}, got it on another too"
            )
        opened.add(self.group)

    def build(self) -> list[nodes.Node]:
        """Make the accordion with its title, lines and content.

        :return: The node of the accordion and what the parser
            reported.
        """
        node = self.locate(self.Node("", classes=self.classes))
        node["open"] = self.open
        node["group"] = self.group
        node["body"] = [ALIASES.get(each, each) for each in self.class_body]
        node["marker"] = self.marker
        node["whole"] = self.hide_show_more
        self.add_name(node)
        words = self.title
        title, messages = self.text(words, "a title")
        lines: dict[str, Headline] = {}
        for role in ("preheader", "subheader"):
            if written := getattr(self, role):
                found, more = self.text(written, f"a {role}")
                classes = [*getattr(self, f"class_{role}")]
                lines[role] = self.locate(
                    Headline(written, "", *found, role=role, classes=classes)
                )
                messages += more
        above = [lines["preheader"]] if "preheader" in lines else []
        head = self.locate(
            Summary(words, "", *above, *title, classes=[*self.class_title])
        )
        head["after"] = self.marker_position == "after"
        below = lines.get("subheader")
        if below is not None and not self.nested_subheader:
            head += below
        node += head
        if below is not None and self.nested_subheader:
            node += below
        self.fill(node, besides=(Summary, Headline))
        for paragraph in node.children:
            if type(paragraph) is nodes.paragraph:
                paragraph["classes"].append(accordion.paragraph())
        return [node, *messages]


@html.opens(Accordion.Node)
def visit(self: HTMLTranslator, node: Accordion.Node) -> None:
    """Open the accordion.

    :param self: The HTML translator, whose body this appends to.
    :param node: The node of the accordion.
    """
    attributes: dict[str, t.Any] = {
        "CLASS": accordion(f"marker-{node['marker']}")
    }
    if node["open"]:
        attributes["open"] = "open"
    if node["group"]:
        attributes["data-km-group"] = node["group"]
    if node["whole"]:
        attributes["data-km-whole"] = "true"
    self.body.append(self.starttag(node, "details", "", **attributes))


html.closes(Accordion.Node, "</div></details>")


@html.opens(Summary)
def visit_summary(self: HTMLTranslator, node: Summary) -> None:
    """Open the title, with the marker first if it goes there.

    :param self: The HTML translator, whose body this appends to.
    :param node: The node of the title.
    """
    classes = accordion.title(more=node["classes"])
    self.body.append(f'<summary class="{self.attval(classes)}">')
    if not node["after"]:
        self.body.append(marker(self, node))
    self.body.append(f'<span class="{accordion.text()}">')


@html.closes(Summary)
def depart_summary(self: HTMLTranslator, node: Summary) -> None:
    """Close the title and open the content.

    :param self: The HTML translator, whose body this appends to.
    :param node: The node of the title.
    """
    self.body.append("</span>")
    if node["after"]:
        self.body.append(marker(self, node))
    classes = accordion.body(more=node.parent["body"])
    self.body.append(f'</summary><div class="{self.attval(classes)}">')


@html.opens(Headline)
def visit_headline(self: HTMLTranslator, node: Headline) -> None:
    """Open the line above or below the title.

    :param self: The HTML translator, whose body this appends to.
    :param node: The node of the line.
    """
    role = node["role"]
    classes = getattr(accordion, role)(more=[text[role], *node["classes"]])
    self.body.append(f'<span class="{self.attval(classes)}">')


html.closes(Headline, "</span>")


def marker(self: HTMLTranslator, node: Summary) -> str:
    """Write the icon that shows that the accordion opens.

    :param self: The HTML translator.
    :param node: The node of the title.
    :return: The HTML of the marker.
    """
    icons = Icons.of(self.builder.config)
    classes = icons.pair(ACCORDION_MARKERS[node.parent["marker"]])
    return (
        f'<span class="{accordion.marker()}">'
        f'<span class="{classes} {accordion.icon()}"'
        ' aria-hidden="true"></span></span>'
    )
