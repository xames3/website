"""\
Tabs Directive
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 23 October 2026
Last updated on: 15 November 2026

A `tabs` directive that holds `tab` directives and shows one of them at
a time::

    .. tabs::
       :group: install

       .. tab:: pip
          :fa-icon: fa-brands fa-python
          :selected:

          ``pip install kaamiki-sphinx-theme``

       .. tab:: uv

          ``uv add kaamiki-sphinx-theme``
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst
from sphinx import addnodes

from kaamiki.extensions.roles import steady
from kaamiki.extensions.utils import BEM
from kaamiki.extensions.utils import KaamikiDirective
from kaamiki.extensions.utils import Option
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import through
from kaamiki.extensions.utils import what
from kaamiki.extensions.utils.aliases import ALIASES
from kaamiki.extensions.utils.doctree import alternatives
from kaamiki.extensions.utils.icons import Icons
from kaamiki.extensions.utils.settings import ALIGNMENTS
from kaamiki.extensions.utils.settings import CHOICES

if t.TYPE_CHECKING:
    from sphinx.writers.html import HTMLTranslator

tabs: t.Final[BEM] = BEM("tabs")
glyph: t.Final[BEM] = BEM("glyph")
ICON_POSITIONS: t.Final[tuple[str, ...]] = CHOICES["tab_icon_position"]


class TabLabel(nodes.paragraph):
    """A tab's title, parsed as rST, with its icon and the icon's side."""


class Tabs(KaamikiDirective, motion=True):
    """The `tabs` directive.

    Options::

        - `group`: A name that other tab sets on the page also use. When
          you pick a tab, each set in the group picks the tab with the
          same key, and the browser keeps the choice. The key is the
          title, or the tab's `key`. A set cannot have a key two times.
        - `align`: Where the row of titles is, `left`, `center` or
          `right`. The default is `center`.
        - `class-bar`: More classes for the row of titles.
        - `speed`: The speed of its motion, relative to the site, one
          of `0.25`, `0.5`, `0.75`, `1`, `1.5`, `2`, `3` or `4`. `2` is
          two times as fast.
        - `no-motion`: Do not move it.
        - `name`: A name for links.
        - `class`: More classes for the tab set.

    Put one `tab` in the set for each title. A tab can be in an `only`.
    A set needs a minimum of two tabs, because one tab has nothing to
    change to. When an `only` removes a tab for a builder, the other
    tabs show. If the removed tab was the selected one, the first tab
    becomes selected.
    """

    has_content = True
    group = Option(checks.slug, default="")
    align = Option(checks.word(*ALIGNMENTS), default="center")
    class_bar = Option(checks.classes, default=())

    class Node(alternatives):
        """The tab set and its tabs."""

    def build(self) -> list[nodes.Node]:
        """Make the tab set and number its tabs.

        :return: The tab set's node.
        """
        node = self.locate(self.Node("", classes=self.classes))
        node["group"] = self.group
        node["align"] = self.align
        node["bar"] = [ALIASES.get(each, each) for each in self.class_bar]
        self.add_name(node)
        self.state.nested_parse(self.content, self.content_offset, node)
        found = list(through(node.children))
        if any(
            isinstance(each, nodes.system_message) and each["level"] >= 3
            for each in found
        ):
            return [node]
        skipped = (Tab.Node, nodes.comment, nodes.target, nodes.system_message)
        if stray := next(
            (each for each in found if not isinstance(each, skipped)), None
        ):
            self.fail(
                f"expected tab directives and nothing else, got {what(stray)}"
            )
        panes = [each for each in found if isinstance(each, Tab.Node)]
        if len(panes) < 2:
            self.fail(f"expected at least 2 tabs, got {len(panes)}")
        keys = [each["key"] for each in panes]
        for key in keys:
            if keys.count(key) > 1:
                self.fail(f"expected each key once, got {key!r} more than once")
        picked = [each for each in panes if each["selected"]]
        if len(picked) > 1:
            self.fail(":selected: expected on one tab, got it on more than one")
        for at, each in enumerate(panes):
            each["index"] = at
            each["checked"] = each in picked or (not picked and at == 0)
        return [node]


class Tab(KaamikiDirective):
    """The `tab` directive.

    Options::

        - `fa-icon`: A Font Awesome icon for the title, as `code`,
          `fa-code` or `fa-regular fa-code`. An icon without a style
          uses the site's `kaamiki.conf.icons.style`, which is
          `regular` by default. When Font Awesome Free has no icon of
          that name in that style, it uses `solid`.
        - `icon-position`: The side of the title for the icon, `before`
          or `after`. The default is `before`. It needs `fa-icon`.
        - `selected`: Show this tab first. Without it, the first tab
          shows.
        - `key`: The name that a `group` uses to find this tab. Use it
          when tabs have different titles but the same meaning. The
          default is the title.
        - `class-title`: More classes for the title.
        - `class-body`: More classes for the content.
        - `name`: A name for links. A link to the tab, or to a thing in
          it, shows the tab.
        - `class`: More classes for the title and the content.

    When a tab does not set the side of its icon,
    `kaamiki.conf.tab.icon_position` sets it.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    fa_icon = Option(checks.icon)
    icon_position = Option(
        checks.word(*ICON_POSITIONS),
        needs="fa-icon",
        setting="tab_icon_position",
    )
    selected = Option(rst.directives.flag)
    key = Option(checks.slug)
    class_title = Option(checks.classes, default=())
    class_body = Option(checks.classes, default=())

    class Node(nodes.container):
        """One tab, its title and its content."""

    def check(self) -> None:
        """Permit a tab only in a tab set."""
        if not isinstance(self.state.parent, (Tabs.Node, addnodes.only)):
            self.fail("expected inside tabs, got it on its own")

    def build(self) -> list[nodes.Node]:
        """Make the tab with its title and its content.

        :return: The tab's node and what the parser reported.
        """
        node = self.locate(self.Node(""))
        node["selected"] = self.selected
        node["classes"] = self.classes
        node["body"] = [ALIASES.get(each, each) for each in self.class_body]
        self.add_name(node)
        label = self.title
        words, messages = self.text(label, "a title")
        steady(self, words, "a title", "which moves the tabs")
        title = self.locate(
            TabLabel(label, "", *words, classes=[*self.class_title])
        )
        try:
            title["icon"] = Icons.of(self.config).custom(self.fa_icon)
        except ValueError as error:
            self.fail(f":fa-icon: {error}")
        title["after"] = self.icon_position == "after"
        node["said"] = True
        node["key"] = nodes.fully_normalize_name(
            self.key or title.astext().strip()
        )
        node += title
        self.fill(node, besides=(TabLabel,))
        return [node, *messages]


@html.opens(Tabs.Node)
def visit(self: HTMLTranslator, node: Tabs.Node) -> None:
    """Open the tab set, numbering it among the sets on the page.

    :param self: The HTML translator, whose body this appends to.
    :param node: The tab set's node.
    """
    node["serial"] = self.__dict__.get("km_tab_sets", 0)
    self.__dict__["km_tab_sets"] = node["serial"] + 1
    panes = [each for each in node.children if isinstance(each, Tab.Node)]
    if panes and not any(each["checked"] for each in panes):
        panes[0]["checked"] = True
    align = [] if node["align"] == "center" else [f"align-{node['align']}"]
    attributes: dict[str, t.Any] = {"CLASS": tabs(*align)}
    if node["group"]:
        attributes["data-km-group"] = node["group"]
    if node["bar"]:
        attributes["data-km-bar"] = " ".join(node["bar"])
    self.body.append(self.starttag(node, "div", "", **attributes))


html.closes(Tabs.Node, "</div>")


def ident(node: nodes.Element) -> str:
    """Name the radio button that shows a tab.

    :param node: The tab's node.
    :return: Its id, which is unique on the page.
    """
    return f"km-tab-{node.parent['serial']}-{node['index']}"


@html.opens(Tab.Node)
def visit_tab(self: HTMLTranslator, node: Tab.Node) -> None:
    """Write the radio button that shows a tab.

    :param self: The HTML translator, whose body this appends to.
    :param node: The tab's node.
    """
    attributes = [
        f'class="{tabs.input()}"',
        'type="radio"',
        f'id="{ident(node)}"',
        f'name="km-tabs-{node.parent["serial"]}"',
        f'data-km-key="{self.attval(node["key"])}"',
    ]
    if not node["said"]:
        attributes.append(f'aria-label="{self.attval(node["key"])}"')
    if node["checked"]:
        attributes.append('checked="checked"')
    self.body.append(f"<input {' '.join(attributes)}>")


html.closes(Tab.Node, "</div>")


def tab_icon(self: HTMLTranslator, node: TabLabel) -> str:
    """Write a tab's icon.

    :param self: The HTML translator.
    :param node: The title's node.
    :return: The icon, or nothing for a tab without one.
    """
    if not node["icon"]:
        return ""
    after = ["icon-position-after"] if node["after"] else []
    return (
        f'<span aria-hidden="true" class="{self.attval(node["icon"])}'
        f' {glyph} {tabs.glyph(*after)}"></span>'
    )


@html.opens(TabLabel)
def visit_label(self: HTMLTranslator, node: TabLabel) -> None:
    """Open a tab's title and put the icon first if it goes there.

    :param self: The HTML translator, whose body this appends to.
    :param node: The title's node.
    """
    classes = tabs.label(more=[*node.parent["classes"], *node["classes"]])
    self.body.append(
        f'<label class="{self.attval(classes)}" for="{ident(node.parent)}">'
    )
    if not node["after"]:
        self.body.append(tab_icon(self, node))


@html.closes(TabLabel)
def depart_label(self: HTMLTranslator, node: TabLabel) -> None:
    """Close the title and open the tab's content.

    :param self: The HTML translator, whose body this appends to.
    :param node: The title's node.
    """
    if node["after"]:
        self.body.append(tab_icon(self, node))
    panel = node.parent
    classes = tabs.panel(more=[*panel["classes"], *panel["body"]])
    ids = panel["ids"]
    anchor = f' id="{self.attval(ids[0])}"' if ids else ""
    spans = "".join(f'<span id="{self.attval(_)}"></span>' for _ in ids[1:])
    text = self.attval(node.astext().strip() or panel["key"])
    self.body.append(
        f'</label><div class="{self.attval(classes)}"{anchor}'
        f' data-km-tab="{ident(panel)}" data-km-label="{text}">{spans}'
    )
