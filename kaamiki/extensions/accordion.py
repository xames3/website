"""\
Accordion Directive
===================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 23 October 2026
Last updated on: 07 November 2026

An `accordion` directive that folds its content away under a title::

    .. accordion:: How do you pronounce XAMES3 or XA?
       :subsection: Asked on 02 November 2025
       :marker: down
       :marker-position: before
       :open:

       It's not "ex-ay-meez-three".
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst
from sphinx.writers.latex import LaTeXTranslator
from sphinx.writers.manpage import ManualPageTranslator
from sphinx.writers.texinfo import TexinfoTranslator
from sphinx.writers.text import TextTranslator

from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import hollow
from kaamiki.extensions.utils import located
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils import titled
from kaamiki.extensions.utils import unlinked
from kaamiki.extensions.utils import worded
from kaamiki.extensions.utils.aliases import ALIASES
from kaamiki.extensions.utils.icons import ACCORDION_MARKERS
from kaamiki.extensions.utils.icons import Icons
from kaamiki.extensions.utils.settings import CHOICES

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "accordion"
MARKER_POSITIONS: t.Final[tuple[str, ...]] = CHOICES[
    "accordion_marker_position"
]
MARKERS: t.Final[tuple[str, ...]] = CHOICES["accordion_marker"]


class Accordion(nodes.container):
    """The accordion and its content, waiting for `visit`."""


class summary(nodes.paragraph):
    """The title, parsed as rST, with the marker's icon and side."""


class subhead(nodes.TextElement):
    """The line under the title."""


class directive(rst.Directive):
    """The `accordion` directive.

    Options::

        - `open`: Start unfolded. Only one accordion of a `group` may.
        - `subsection`: A dimmer line under the title.
        - `nested-subsection`: Put the subsection at the top of the
          content, so it shows once the accordion is open, instead of
          under the title. It needs `subsection`.
        - `class-subsection`: More classes for the subsection, which
          always has `km-text--subsection`. It needs `subsection`.
        - `marker`: What shows that an accordion opens, `plus`, a `down`
          chevron or a `right` one. A plus turns 45 degrees as it opens,
          a right chevron turns 90 degrees to point down and a down
          chevron turns over. It's the site's `kaamiki.conf.accordion.marker`
          without one.
        - `marker-position`: The marker's side of the title, `before`
          it or `after` it.
        - `hide-show-more`: Show a long body in full. One taller than
          the screen is folded behind a Show more button otherwise.
        - `group`: A name shared with other accordions on the page.
          Opening one folds the rest of its group.
        - `class-title`: More classes for the title.
        - `class-body`: More classes for the content.
        - `name`: A name to link to. A link to it, or to anything inside
          it, opens the accordion.
        - `class`: More classes for the accordion.

    An accordion needs some content, or the build stops. So does an
    option that's written wrong, out of range or at odds with another.

    The site's `kaamiki.conf.accordion.marker` and
    `kaamiki.conf.accordion.marker_position` settle the marker and its side for
    an accordion that doesn't say.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "open": rst.directives.flag,
        "subsection": checks.text,
        "nested-subsection": rst.directives.flag,
        "class-subsection": checks.classes,
        "marker": checks.word(*MARKERS),
        "marker-position": checks.word(*MARKER_POSITIONS),
        "hide-show-more": rst.directives.flag,
        "group": checks.slug,
        "class-title": checks.classes,
        "class-body": checks.classes,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the title and the content and return the accordion.

        :return: The accordion's node, followed by whatever the title
            and the subsection reported.
        """
        config = self.state.document.settings.env.config
        options = self.options
        if "subsection" not in options:
            for each in ("nested-subsection", "class-subsection"):
                if each in options:
                    raise self.error(f"accordion: :{each}: needs :subsection:")
        if "group" in options and "open" in options:
            group = self.state.document.settings.env.temp_data.setdefault(
                "km_open_groups", set()
            )
            if options["group"] in group:
                raise self.error(
                    f"accordion: :open: expected on one accordion of the"
                    f" group {options['group']!r}, got it on another too"
                )
            group.add(options["group"])
        side = options.get("marker-position")
        if side is None:
            side = setting(config, "accordion_marker_position")
        shape = options.get("marker") or setting(config, "accordion_marker")
        element = located(
            self, Accordion("", classes=list(options.get("class", [])))
        )
        element["open"] = "open" in options
        element["group"] = options.get("group", "")
        element["body"] = [
            ALIASES.get(_, _) for _ in options.get("class-body", [])
        ]
        element["marker"] = shape
        element["whole"] = "hide-show-more" in options
        named(self, element)
        words = titled(self, self.arguments[0])
        title, messages = self.state.inline_text(words, self.lineno)
        unlinked(self, title, "a title")
        worded(self, title, "a title")
        head = located(
            self,
            summary(
                words,
                "",
                *title,
                classes=list(options.get("class-title", [])),
            ),
        )
        head["after"] = side == "after"
        under = None
        if "subsection" in options:
            lead, more = self.state.inline_text(
                options["subsection"], self.lineno
            )
            unlinked(self, lead, "a subsection")
            worded(self, lead, "a subsection")
            under = located(
                self,
                subhead(
                    options["subsection"],
                    "",
                    *lead,
                    classes=list(options.get("class-subsection", [])),
                ),
            )
            messages += more
        nested = "nested-subsection" in options
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
        for para in element.children:
            if type(para) is nodes.paragraph:
                para["classes"].append("km-accordion__paragraph")
        return [element, *messages]


def visit(self: HTMLTranslator, node: Accordion) -> None:
    """Open the accordion.

    :param self: The HTML translator, whose body this appends to.
    :param node: The accordion's node.
    """
    attributes: dict[str, t.Any] = {
        "CLASS": f"km-accordion km-accordion--marker-{node['marker']}"
    }
    if node["open"]:
        attributes["open"] = "open"
    if node["group"]:
        attributes["data-km-group"] = node["group"]
    if node["whole"]:
        attributes["data-km-whole"] = "true"
    self.body.append(self.starttag(node, "details", "", **attributes))


def depart(self: HTMLTranslator, node: Accordion) -> None:
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
    :param node: The subsection's node.
    """
    classes = " ".join(
        ["km-accordion__subsection", "km-text--subsection", *node["classes"]]
    )
    self.body.append(f'<span class="{self.attval(classes)}">')


def depart_subhead(self: HTMLTranslator, node: subhead) -> None:
    """Close the line under the title.

    :param self: The HTML translator, whose body this appends to.
    :param node: The subsection's node (unused).
    """
    del node
    self.body.append("</span>")


def marker(self: HTMLTranslator, node: summary) -> str:
    """Write the icon that shows an accordion is there to open.

    :param self: The HTML translator.
    :param node: The title's node.
    :return: The accordion's marker. A plus turns 45 degrees, a right
        chevron turns 90 degrees and a down chevron turns over like the
        header's dropdowns do. Nothing else moves.
    """
    icons = Icons.of(self.builder.config)
    classes = icons.pair(ACCORDION_MARKERS[node.parent["marker"]])
    return (
        '<span class="km-accordion__marker">'
        f'<span class="{classes} km-accordion__icon"'
        ' aria-hidden="true"></span></span>'
    )


def register(app: Sphinx) -> None:
    """Register the nodes only an accordion has.

    :param app: The Sphinx application instance.
    """
    app.add_node(summary, html=(visit_summary, depart_summary))
    app.add_node(
        subhead,
        html=(visit_subhead, depart_subhead),
        latex=(LaTeXTranslator.visit_inline, LaTeXTranslator.depart_inline),
        man=(
            ManualPageTranslator.visit_inline,
            ManualPageTranslator.depart_inline,
        ),
        texinfo=(
            TexinfoTranslator.visit_inline,
            TexinfoTranslator.depart_inline,
        ),
        text=(TextTranslator.visit_inline, TextTranslator.depart_inline),
    )


node = Accordion
