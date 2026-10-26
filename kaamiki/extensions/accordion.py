"""\
Accordion Directive
===================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 23 October 2026
Last updated on: 25 October 2026

An `accordion` directive that folds its content away under a title::

    .. accordion:: How do you pronounce XAMES3 or XA?
       :subtitle: Asked on November 02, 2025
       :marker: down
       :marker-position: before
       :open:

       It's not "ex-ay-meez-three".
"""

import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import hollow
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils import titled
from kaamiki.extensions.utils.settings import CHOICES
from kaamiki.extensions.utils.settings import icon_style

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "accordion"
POSITIONS: t.Final[tuple[str, ...]] = CHOICES["accordion_marker_position"]
MARKERS: t.Final[tuple[str, ...]] = CHOICES["accordion_marker"]
# NOTE(xames3): A plus and a right chevron turn 45 degrees, a down chevron
# turns over like the header's dropdowns do. Nothing else moves.
GLYPHS: t.Final[dict[str, str]] = {
    "plus": "fa-plus",
    "down": "fa-chevron-down",
    "right": "fa-chevron-right",
}


class node(nodes.container):
    """The accordion and its content, waiting for `visit`."""


class summary(nodes.paragraph):
    """The title, parsed as rST, with the marker's icon and side."""


class subhead(nodes.inline):
    """The line under the title."""


class directive(rst.Directive):
    """The `accordion` directive.

    Options::

        - `open`: Start unfolded. Only one accordion of a `group` may.
        - `subtitle`: A dimmer line under the title.
        - `nested-subtitle`: Put the subtitle at the top of the
          content, so it shows once the accordion is open, instead of
          under the title. It needs `subtitle`.
        - `class-subtitle`: More classes for the subtitle, which has
          `km-text-subsection` without them. It needs `subtitle`.
        - `marker`: What shows an accordion opens, `plus`, a `down`
          chevron or a `right` one. A plus and a right chevron turn 45
          degrees as it opens, a down chevron turns over. It's the
          site's `accordion_marker` without one.
        - `marker-position`: The marker's side of the title, `before`
          it or `after` it.
        - `no-show-more`: Show a long body in full. One taller than
          the screen is folded behind a Show more button otherwise.
        - `group`: A name shared with other accordions on the page.
          Opening one folds the rest of its group.
        - `name`: A name to link to. A link to it, or to anything inside
          it, opens the accordion.
        - `class`: More classes for the accordion.
        - `class-title`: More classes for the title.
        - `class-body`: More classes for the content.

    An accordion needs some content, or the build stops. So does an
    option that's written wrong, out of range or at odds with another.

    The site's `accordion_marker` and `accordion_marker_position` settle
    the marker and its side for an accordion that doesn't say.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "open": rst.directives.flag,
        "subtitle": checks.text,
        "nested-subtitle": rst.directives.flag,
        "class-subtitle": checks.classes,
        "marker": checks.word(*MARKERS),
        "marker-position": checks.word(*POSITIONS),
        "no-show-more": rst.directives.flag,
        "group": checks.slug,
        "class-title": checks.classes,
        "class-body": checks.classes,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the title and the content and return the accordion.

        :return: The accordion's node, followed by whatever the title
            and the subtitle reported.
        """
        self.assert_has_content()
        config = self.state.document.settings.env.config
        options = self.options
        if "subtitle" not in options:
            for each in ("nested-subtitle", "class-subtitle"):
                if each in options:
                    raise self.error(f"accordion: :{each}: requires :subtitle:")
        if "group" in options and "open" in options:
            group = self.state.document.settings.env.temp_data.setdefault(
                "km_open_groups", set()
            )
            if options["group"] in group:
                raise self.error(
                    f"accordion: :open: is on another accordion of the group"
                    f" {options['group']!r} already"
                )
            group.add(options["group"])
        side = options.get("marker-position")
        if side is None:
            side = setting(config, "accordion_marker_position")
        shape = options.get("marker") or setting(config, "accordion_marker")
        element = node("", classes=list(options.get("class", [])))
        element["open"] = "open" in options
        element["group"] = options.get("group", "")
        element["body"] = list(options.get("class-body", []))
        element["marker"] = shape
        element["whole"] = "no-show-more" in options
        named(self, element)
        words = titled(self, self.arguments[0])
        title, messages = self.state.inline_text(words, self.lineno)
        head = summary(
            words,
            "",
            *title,
            classes=list(options.get("class-title", [])),
        )
        head["after"] = side == "after"
        under = None
        if "subtitle" in options:
            lead, more = self.state.inline_text(
                options["subtitle"], self.lineno
            )
            under = subhead(
                options["subtitle"],
                "",
                *lead,
                classes=list(options.get("class-subtitle", [])),
            )
            messages += more
        nested = "nested-subtitle" in options
        if under is not None and not nested:
            head += under
        element += head
        if under is not None and nested:
            element += under
        self.state.nested_parse(self.content, self.content_offset, element)
        if hollow(
            _ for _ in element.children if not isinstance(_, (summary, subhead))
        ):
            raise self.error("accordion: expected some content, got none")
        for para in element.findall(nodes.paragraph):
            if type(para) is nodes.paragraph:
                para["classes"].append("km-accordion__paragraph")
        return [element, *messages]


def visit(self: HTMLTranslator, node: node) -> None:
    """Open the accordion.

    :param self: The HTML translator, whose body this appends to.
    :param node: The accordion's node.
    """
    attributes: dict[str, t.Any] = {
        "CLASS": f"km-accordion km-accordion--{node['marker']}"
    }
    if node["open"]:
        attributes["open"] = "open"
    if node["group"]:
        attributes["data-km-group"] = node["group"]
    if node["whole"]:
        attributes["data-km-whole"] = "true"
    self.body.append(self.starttag(node, "details", "", **attributes))


def depart(self: HTMLTranslator, node: node) -> None:
    """Close the content and the accordion.

    :param self: The HTML translator, whose body this appends to.
    :param node: The accordion's node (unused).
    """
    del node
    self.body.append("</div></details>")


def visit_summary(self: HTMLTranslator, node: summary) -> None:
    """Open the title, with the marker ahead of the text if it goes
    there.

    :param self: The HTML translator, whose body this appends to.
    :param node: The title's node.
    """
    classes = " ".join(["km-accordion__title", *node["classes"]])
    self.body.append(f'<summary class="{self.attval(classes)}">')
    if not node["after"]:
        self.body.append(marker(self, node))
    self.body.append('<span class="km-accordion__text">')


def depart_summary(self: HTMLTranslator, node: summary) -> None:
    """Close the title and open the content.

    :param self: The HTML translator, whose body this appends to.
    :param node: The title's node.
    """
    self.body.append("</span>")
    if node["after"]:
        self.body.append(marker(self, node))
    classes = " ".join(["km-accordion__body", *node.parent["body"]])
    self.body.append(f'</summary><div class="{self.attval(classes)}">')


def visit_subhead(self: HTMLTranslator, node: subhead) -> None:
    """Open the line under the title.

    :param self: The HTML translator, whose body this appends to.
    :param node: The subtitle's node.
    """
    classes = " ".join(
        ["km-accordion__subtitle", "km-text-subsection", *node["classes"]]
    )
    self.body.append(f'<span class="{self.attval(classes)}">')


def depart_subhead(self: HTMLTranslator, node: subhead) -> None:
    """Close the line under the title.

    :param self: The HTML translator, whose body this appends to.
    :param node: The subtitle's node (unused).
    """
    del node
    self.body.append("</span>")


def marker(self: HTMLTranslator, node: summary) -> str:
    """Write the icon that shows an accordion is there to open.

    :param self: The HTML translator.
    :param node: The title's node.
    :return: The accordion's marker, in the site's `fa_style` when it
        has a Font Awesome kit and a solid one when it hasn't, as the
        styles the kit adds aren't free.
    """
    config = self.builder.config
    style = icon_style(config)
    glyph = GLYPHS[node.parent["marker"]]
    return (
        '<span class="km-accordion__marker">'
        f'<span class="fa-{style} {glyph} km-accordion__icon"'
        ' aria-hidden="true"></span></span>'
    )


def register(app: Sphinx) -> None:
    """Register the nodes only an accordion has.

    :param app: The Sphinx application instance.
    """
    app.add_node(summary, html=(visit_summary, depart_summary))
    app.add_node(subhead, html=(visit_subhead, depart_subhead))
