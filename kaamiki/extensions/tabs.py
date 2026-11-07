"""\
Tabs Directive
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 23 October 2026
Last updated on: 07 November 2026

A `tabs` directive that holds `tab` directives and shows one at a
time::

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
from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import close
from kaamiki.extensions.utils import hollow
from kaamiki.extensions.utils import located
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils import through
from kaamiki.extensions.utils import titled
from kaamiki.extensions.utils import unlinked
from kaamiki.extensions.utils import what
from kaamiki.extensions.utils import worded
from kaamiki.extensions.utils.aliases import ALIASES
from kaamiki.extensions.utils.doctree import alternatives
from kaamiki.extensions.utils.icons import Icons
from kaamiki.extensions.utils.settings import ALIGNMENTS
from kaamiki.extensions.utils.settings import CHOICES

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "tabs"
depart = close
ICON_POSITIONS: t.Final[tuple[str, ...]] = CHOICES["tab_icon_position"]


class Tabs(alternatives):
    """The tab set and its tabs, waiting for `visit`."""


class pane(nodes.container):
    """One tab, its title and its content."""


class tablabel(nodes.paragraph):
    """A tab's title, parsed as rST, with its icon and the icon's
    side.
    """


class directive(rst.Directive):
    """The `tabs` directive.

    Options::

        - `group`: A name shared with other tab sets on the page.
          Picking a tab picks the tab with the same key in each of
          them, which is its title unless it has a `key` and the
          browser remembers the choice. A set can't have a key twice.
        - `align`: Where the row of titles sits, `left`, `center` or
          `right`. Defaults to `center`.
        - `class-bar`: More classes for the row of titles.
        - `name`: A name to link to.
        - `class`: More classes for the tab set.

    A `tab` goes inside, one for each title, and can sit in an `only`.
    A set needs at least two written, as one tab has nothing to switch
    to. A builder an `only` leaves a tab out of shows the tabs that are
    left, and the first of them if the checked one went.
    """

    has_content = True
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "group": checks.slug,
        "align": checks.word(*ALIGNMENTS),
        "class-bar": checks.classes,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the tabs and return the tab set.

        :return: The tab set's node.
        """
        options = self.options
        element = located(
            self, Tabs("", classes=list(options.get("class", [])))
        )
        element["group"] = options.get("group", "")
        element["align"] = options.get("align", "center")
        element["bar"] = [
            ALIASES.get(_, _) for _ in options.get("class-bar", [])
        ]
        named(self, element)
        self.state.nested_parse(self.content, self.content_offset, element)
        found = list(through(element.children))
        if any(
            isinstance(_, nodes.system_message) and _["level"] >= 3
            for _ in found
        ):
            return [element]
        skipped = (pane, nodes.comment, nodes.target, nodes.system_message)
        if stray := next(
            (_ for _ in found if not isinstance(_, skipped)), None
        ):
            raise self.error(
                "tabs: expected tab directives and nothing else, got"
                f" {what(stray)}"
            )
        panes = [_ for _ in found if isinstance(_, pane)]
        if len(panes) < 2:
            raise self.error(
                f"tabs: expected at least 2 tabs, got {len(panes)}"
            )
        keys = [_["key"] for _ in panes]
        for key in keys:
            if keys.count(key) > 1:
                raise self.error(
                    f"tabs: expected each key once, got {key!r} more than once"
                )
        picked = [_ for _ in panes if _["selected"]]
        if len(picked) > 1:
            raise self.error(
                "tabs: :selected: expected on one tab, got it on more than one"
            )
        for at, each in enumerate(panes):
            each["index"] = at
            each["checked"] = each in picked or (not picked and at == 0)
        return [element]


class tab(rst.Directive):
    """The `tab` directive.

    Options::

        - `fa-icon`: A Font Awesome icon for the title, as `code`,
          `fa-code` or `fa-regular fa-code`. One without a style is
          drawn in the site's `kaamiki.conf.icons.style`, `regular`
          unless it says otherwise, and `solid` where Font Awesome Free
          has no icon of that name in that style.
        - `icon-position`: `before` the title, the default or
          `after` it.
        - `selected`: Show this tab first. The first one is shown
          without it.
        - `key`: What a `group` matches this tab by, for tabs that
          mean the same under different titles. It's the title
          without it.
        - `class-title`: More classes for the title.
        - `class-body`: More classes for the content.
        - `name`: A name to link to. A link to it, or to anything
          inside it, shows the tab.
        - `class`: More classes for the title and the content.

    The site's `kaamiki.conf.tab.icon_position` settles the icon's side
    for a tab that doesn't say.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {  # noqa: RUF012
        "fa-icon": checks.icon,
        "icon-position": checks.word(*ICON_POSITIONS),
        "selected": rst.directives.flag,
        "key": checks.slug,
        **NATIVE,
        "class-title": checks.classes,
        "class-body": checks.classes,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the title and the content and return the tab.

        :return: The tab's node, followed by whatever the title
            reported.
        """
        if not isinstance(self.state.parent, (Tabs, addnodes.only)):
            raise self.error("tab: expected inside tabs, got it on its own")
        config = self.state.document.settings.env.config
        options = self.options
        if "icon-position" in options and "fa-icon" not in options:
            raise self.error("tab: :icon-position: needs :fa-icon:")
        side = options.get("icon-position")
        if side is None:
            side = setting(config, "tab_icon_position")
        element = located(self, pane(""))
        element["selected"] = "selected" in options
        element["classes"] = list(options.get("class", []))
        element["body"] = [
            ALIASES.get(_, _) for _ in options.get("class-body", [])
        ]
        named(self, element)
        label = titled(self, self.arguments[0])
        words, messages = self.state.inline_text(label, self.lineno)
        unlinked(self, words, "a title")
        worded(self, words, "a title")
        steady(self, words, "a title", "which moves the tabs")
        title = located(
            self,
            tablabel(
                label,
                "",
                *words,
                classes=list(options.get("class-title", [])),
            ),
        )
        try:
            title["icon"] = Icons.of(config).custom(options.get("fa-icon"))
        except ValueError as error:
            raise self.error(f"tab: :fa-icon: {error}") from error
        title["after"] = side == "after"
        text = title.astext().strip()
        element["said"] = True
        element["key"] = nodes.fully_normalize_name(options.get("key") or text)
        element += title
        self.state.nested_parse(self.content, self.content_offset, element)
        if hollow(_ for _ in element.children if _ is not title):
            raise self.error("tab: expected some content, got none")
        return [element, *messages]


def visit(self: HTMLTranslator, node: Tabs) -> None:
    """Open the tab set, numbering it among the sets on the page.

    A page being written is every page at once for `singlehtml`, so the
    number comes from the sets this translator has opened and not from
    the source file, or two files would give the same ids.

    :param self: The HTML translator, whose body this appends to.
    :param node: The tab set's node.
    """
    node["serial"] = self.__dict__.get("km_tab_sets", 0)
    self.__dict__["km_tab_sets"] = node["serial"] + 1
    panes = [_ for _ in node.children if isinstance(_, pane)]
    if panes and not any(_["checked"] for _ in panes):
        panes[0]["checked"] = True
    classes = ["km-tabs"]
    if node["align"] != "center":
        classes.append(f"km-tabs--align-{node['align']}")
    attributes: dict[str, t.Any] = {"CLASS": " ".join(classes)}
    if node["group"]:
        attributes["data-km-group"] = node["group"]
    if node["bar"]:
        attributes["data-km-bar"] = " ".join(node["bar"])
    self.body.append(self.starttag(node, "div", "", **attributes))


def ident(node: nodes.Element) -> str:
    """Name the radio button that shows a tab.

    :param node: The tab's node.
    :return: Its id, which is unique on the page.
    """
    return f"km-tab-{node.parent['serial']}-{node['index']}"


def visit_pane(self: HTMLTranslator, node: pane) -> None:
    """Write the radio button that shows a tab.

    :param self: The HTML translator, whose body this appends to.
    :param node: The tab's node.
    """
    attributes = [
        'class="km-tabs__input"',
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


def tab_icon(self: HTMLTranslator, node: tablabel) -> str:
    """Write a tab's icon.

    :param self: The HTML translator.
    :param node: The title's node.
    :return: The icon, or nothing for a tab without one.
    """
    if not node["icon"]:
        return ""
    after = " km-tabs__glyph--icon-position-after" if node["after"] else ""
    return (
        f'<span aria-hidden="true" class="{self.attval(node["icon"])}'
        f' km-glyph km-tabs__glyph{after}"></span>'
    )


def visit_tablabel(self: HTMLTranslator, node: tablabel) -> None:
    """Open a tab's title, with the icon ahead of the text if it goes
    there.

    :param self: The HTML translator, whose body this appends to.
    :param node: The title's node.
    """
    classes = " ".join(
        ["km-tabs__label", *node.parent["classes"], *node["classes"]]
    )
    self.body.append(
        f'<label class="{self.attval(classes)}" for="{ident(node.parent)}">'
    )
    if not node["after"]:
        self.body.append(tab_icon(self, node))


def depart_tablabel(self: HTMLTranslator, node: tablabel) -> None:
    """Close the title and open the tab's content.

    :param self: The HTML translator, whose body this appends to.
    :param node: The title's node.
    """
    if node["after"]:
        self.body.append(tab_icon(self, node))
    panel = node.parent
    classes = " ".join(["km-tabs__panel", *panel["classes"], *panel["body"]])
    ids = panel["ids"]
    anchor = f' id="{self.attval(ids[0])}"' if ids else ""
    spans = "".join(f'<span id="{self.attval(_)}"></span>' for _ in ids[1:])
    text = self.attval(node.astext().strip() or panel["key"])
    self.body.append(
        f'</label><div class="{self.attval(classes)}"{anchor}'
        f' data-km-tab="{ident(panel)}" data-km-label="{text}">{spans}'
    )


def register(app: Sphinx) -> None:
    """Register the `tab` directive and the nodes only tabs have.

    :param app: The Sphinx application instance.
    """
    app.add_directive("tab", tab)
    app.add_node(pane, html=(visit_pane, close))
    app.add_node(tablabel, html=(visit_tablabel, depart_tablabel))


node = Tabs
