"""\
Tabs Directive
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 23 October 2026
Last updated on: 25 October 2026

A `tabs` directive that holds `tab` directives and shows one at a time::

    .. tabs::
       :group: install

       .. tab:: pip
          :fa-icon: fa-brands fa-python
          :selected:

          ``pip install kaamiki``

       .. tab:: uv

          ``uv add kaamiki``
"""

import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import hollow
from kaamiki.extensions.utils import icon
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils import titled
from kaamiki.extensions.utils.settings import ALIGNMENTS
from kaamiki.extensions.utils.settings import CHOICES

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "tabs"
POSITIONS: t.Final[tuple[str, ...]] = CHOICES["tab_icon_position"]


class node(nodes.container):
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

        - `group`: A name shared with other tab sets on the page. Picking
          a tab picks the tab with the same key in each of them, which
          is its title unless it has a `key`, and the browser remembers
          the choice. A set can't have a key twice.
        - `align`: Where the row of titles sits, `left`, `center` or
          `right`. Defaults to `center`.
        - `no-slide`: Switch tabs without the pill sliding across.
        - `name`: A name to link to.
        - `class`: More classes for the tab set.
        - `class-bar`: More classes for the row of titles.

    A `tab` goes inside, one for each title. A set needs at least two,
    as one tab has nothing to switch to.
    """

    has_content = True
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "group": checks.slug,
        "align": checks.word(*ALIGNMENTS),
        "no-slide": rst.directives.flag,
        "class-bar": checks.classes,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the tabs and return the tab set.

        :return: The tab set's node.
        """
        env = self.state.document.settings.env
        options = self.options
        element = node("", classes=list(options.get("class", [])))
        element["index"] = env.temp_data.get("km_tabs", 0)
        env.temp_data["km_tabs"] = element["index"] + 1
        element["group"] = options.get("group", "")
        element["align"] = options.get("align", "center")
        element["still"] = "no-slide" in options
        element["bar"] = list(options.get("class-bar", []))
        named(self, element)
        self.state.nested_parse(self.content, self.content_offset, element)
        if any(
            isinstance(_, nodes.system_message) and _["level"] >= 3
            for _ in element.children
        ):
            return [element]
        skipped = (pane, nodes.comment, nodes.target, nodes.system_message)
        if any(not isinstance(_, skipped) for _ in element.children):
            raise self.error("tabs: expected tab directives and nothing else")
        panes = [_ for _ in element.children if isinstance(_, pane)]
        if len(panes) < 2:
            raise self.error(
                f"tabs: expected at least 2 tabs, got {len(panes)}"
            )
        keys = [_["key"] for _ in panes]
        for key in keys:
            if keys.count(key) > 1:
                raise self.error(f"tabs: key {key!r} is used more than once")
        picked = [_ for _ in panes if _["selected"]]
        if len(picked) > 1:
            raise self.error("tabs: :selected: is on more than one tab")
        for at, each in enumerate(panes):
            each["index"] = at
            each["checked"] = each in picked or (not picked and at == 0)
        return [element]


class tab(rst.Directive):
    """The `tab` directive.

    Options::

        - `fa-icon`: A Font Awesome icon for the title, as `code`,
          `fa-code` or `fa-regular fa-code`. One without a style is
          drawn solid.
        - `fa-icon-position`: `before` the title, the default or
          `after` it.
        - `selected`: Show this tab first. The first one is shown
          without it.
        - `key`: What a `group` matches this tab by, for tabs that
          mean the same under different titles. It's the title
          without it.
        - `name`: A name to link to. A link to it, or to anything
          inside it, shows the tab.
        - `class-title`: More classes for the title.
        - `class-body`: More classes for the content.

    The site's `tab_icon_position` settles the icon's side for a tab
    that doesn't say.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {  # noqa: RUF012
        "fa-icon": checks.icon,
        "fa-icon-position": checks.word(*POSITIONS),
        "selected": rst.directives.flag,
        "key": checks.slug,
        "name": NATIVE["name"],
        "class-title": checks.classes,
        "class-body": checks.classes,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the title and the content and return the tab.

        :return: The tab's node, followed by whatever the title
            reported.
        """
        if not isinstance(self.state.parent, node):
            raise self.error("tab: expected to be inside tabs")
        config = self.state.document.settings.env.config
        options = self.options
        side = options.get("fa-icon-position")
        if side is None:
            side = setting(config, "tab_icon_position")
        element = pane("")
        element["selected"] = "selected" in options
        element["body"] = list(options.get("class-body", []))
        named(self, element)
        label = titled(self, self.arguments[0])
        words, messages = self.state.inline_text(label, self.lineno)
        title = tablabel(
            label,
            "",
            *words,
            classes=list(options.get("class-title", [])),
        )
        title["icon"] = icon(
            options.get("fa-icon"), kit=bool(setting(config, "fa_kit"))
        )
        title["after"] = side == "after"
        element["key"] = nodes.fully_normalize_name(
            options.get("key") or title.astext()
        )
        element += title
        self.state.nested_parse(self.content, self.content_offset, element)
        if hollow(_ for _ in element.children if _ is not title):
            raise self.error("tab: expected some content, got none")
        return [element, *messages]


def visit(self: HTMLTranslator, node: node) -> None:
    """Open the tab set.

    :param self: The HTML translator, whose body this appends to.
    :param node: The tab set's node.
    """
    attributes: dict[str, t.Any] = {
        "CLASS": f"km-tabs km-tabs--{node['align']}"
    }
    if node["still"]:
        attributes["CLASS"] += " km-tabs--still"
    if node["group"]:
        attributes["data-km-group"] = node["group"]
    if node["bar"]:
        attributes["data-km-bar"] = " ".join(node["bar"])
    self.body.append(self.starttag(node, "div", "", **attributes))


def depart(self: HTMLTranslator, node: node) -> None:
    """Close the tab set.

    :param self: The HTML translator, whose body this appends to.
    :param node: The tab set's node (unused).
    """
    del node
    self.body.append("</div>")


def ident(node: nodes.Element) -> str:
    """Name the radio button that shows a tab.

    :param node: The tab's node.
    :return: Its id, which is unique on the page.
    """
    return f"km-tab-{node.parent['index']}-{node['index']}"


def visit_pane(self: HTMLTranslator, node: pane) -> None:
    """Write the radio button that shows a tab.

    :param self: The HTML translator, whose body this appends to.
    :param node: The tab's node.
    """
    attributes = [
        'class="km-tabs__input"',
        'type="radio"',
        f'id="{ident(node)}"',
        f'name="km-tabs-{node.parent["index"]}"',
        f'data-km-key="{self.attval(node["key"])}"',
    ]
    if node["checked"]:
        attributes.append('checked="checked"')
    self.body.append(f"<input {' '.join(attributes)}>")


def depart_pane(self: HTMLTranslator, node: pane) -> None:
    """Close the tab's content.

    :param self: The HTML translator, whose body this appends to.
    :param node: The tab's node (unused).
    """
    del node
    self.body.append("</div>")


def glyph(self: HTMLTranslator, node: tablabel) -> str:
    """Write a tab's icon.

    :param self: The HTML translator.
    :param node: The title's node.
    :return: The icon, or nothing for a tab without one.
    """
    if not node["icon"]:
        return ""
    after = " km-tabs__glyph--after" if node["after"] else ""
    return (
        f'<span aria-hidden="true" class="{self.attval(node["icon"])}'
        f' km-glyph{after}"></span>'
    )


def visit_tablabel(self: HTMLTranslator, node: tablabel) -> None:
    """Open a tab's title, with the icon ahead of the text if it goes
    there.

    :param self: The HTML translator, whose body this appends to.
    :param node: The title's node.
    """
    classes = " ".join(["km-tabs__label", *node["classes"]])
    self.body.append(
        f'<label class="{self.attval(classes)}" for="{ident(node.parent)}">'
    )
    if not node["after"]:
        self.body.append(glyph(self, node))
        if node["icon"]:
            self.body.append(" ")


def depart_tablabel(self: HTMLTranslator, node: tablabel) -> None:
    """Close the title and open the tab's content.

    :param self: The HTML translator, whose body this appends to.
    :param node: The title's node.
    """
    if node["after"]:
        self.body.append(" " + glyph(self, node))
    pane = node.parent
    classes = " ".join(["km-tabs__panel", *pane["body"]])
    ids = pane["ids"]
    anchor = f' id="{self.attval(ids[0])}"' if ids else ""
    self.body.append(
        f'</label><div class="{self.attval(classes)}"{anchor}'
        f' data-km-tab="{ident(pane)}">'
    )


def register(app: Sphinx) -> None:
    """Register the `tab` directive and the nodes only tabs have.

    :param app: The Sphinx application instance.
    """
    app.add_directive("tab", tab)
    app.add_node(pane, html=(visit_pane, depart_pane))
    app.add_node(tablabel, html=(visit_tablabel, depart_tablabel))
