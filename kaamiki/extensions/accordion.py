"""\
Accordion Directive
===================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 23 October 2026
Last updated on: 15 November 2026

An `accordion` directive that folds its content away under a title::

    .. accordion:: What's an accordion?
       :subheader: A short answer
       :marker: down
       :marker-position: before
       :open:

       It's a box that folds its content away under a title.
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import MOTION
from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import Bem
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import hollow
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import located
from kaamiki.extensions.utils import moving
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
accordion: t.Final[Bem] = Bem("accordion")
text: t.Final[Bem] = Bem("text")


class Accordion(nodes.container):
    """The accordion and its content, waiting for `visit`."""


class summary(nodes.paragraph):
    """The title, parsed as rST, with the marker's icon and side."""


class headline(nodes.TextElement):
    """A line above or under the title, by its `role`."""


class directive(rst.Directive):
    """The `accordion` directive.

    Options::

        - `open`: Start unfolded. Only one accordion of a `group` may.
        - `preheader`: A small line above the title.
        - `class-preheader`: More classes for the preheader, which
          always has `km-text--preheader`. It needs `preheader`.
        - `subheader`: A dimmer line under the title.
        - `nested-subheader`: Put the subheader at the top of the
          content, so it shows once the accordion is open, instead of
          under the title. It needs `subheader`.
        - `class-subheader`: More classes for the subheader, which
          always has `km-text--subheader`. It needs `subheader`.
        - `marker`: What shows that an accordion opens, `plus`, a `down`
          chevron or a `right` one. A plus turns 45 degrees as it opens,
          a right chevron turns 90 degrees to point down and a down
          chevron turns over.
        - `marker-position`: The marker's side of the title, `before`
          it or `after` it.
        - `hide-show-more`: Show a long body in full. One taller than
          the screen is folded behind a Show more button otherwise.
        - `group`: A name shared with other accordions on the page.
          Opening one folds the rest of its group.
        - `class-title`: More classes for the title.
        - `class-body`: More classes for the content.
        - `speed`: How quick its motion is next to the site's, one
          of `0.25`, `0.5`, `0.75`, `1`, `1.5`, `2`, `3` or `4`.
          `2` is twice as quick.
        - `no-motion`: Keep it still.
        - `name`: A name to link to. A link to it, or to anything inside
          it, opens the accordion.
        - `class`: More classes for the accordion.

    An accordion needs some content, or the build stops. So does an
    option that's written wrong, out of range or at odds with another.

    The site's `kaamiki.conf.accordion.marker` and
    `kaamiki.conf.accordion.marker_position` settle the marker and its
    side for an accordion that doesn't say.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {  # noqa: RUF012
        **NATIVE,
        **MOTION,
        "open": rst.directives.flag,
        "preheader": checks.text,
        "class-preheader": checks.classes,
        "subheader": checks.text,
        "nested-subheader": rst.directives.flag,
        "class-subheader": checks.classes,
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
            and the lines around it reported.
        """
        config = self.state.document.settings.env.config
        options = self.options
        for need, each in (
            ("preheader", "class-preheader"),
            ("subheader", "nested-subheader"),
            ("subheader", "class-subheader"),
        ):
            if need not in options and each in options:
                raise self.error(f"accordion: :{each}: needs :{need}:")
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
            self,
            Accordion(
                "", classes=[*options.get("class", []), *moving(options)]
            ),
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
        lines: dict[str, headline] = {}
        for role in ("preheader", "subheader"):
            if role in options:
                lead, more = self.state.inline_text(options[role], self.lineno)
                unlinked(self, lead, f"a {role}")
                worded(self, lead, f"a {role}")
                lines[role] = located(
                    self,
                    headline(
                        options[role],
                        "",
                        *lead,
                        role=role,
                        classes=list(options.get(f"class-{role}", [])),
                    ),
                )
                messages += more
        head = located(
            self,
            summary(
                words,
                "",
                *([lines["preheader"]] if "preheader" in lines else []),
                *title,
                classes=list(options.get("class-title", [])),
            ),
        )
        head["after"] = side == "after"
        under = lines.get("subheader")
        nested = "nested-subheader" in options
        if under is not None and not nested:
            head += under
        element += head
        if under is not None and nested:
            element += under
        self.state.nested_parse(self.content, self.content_offset, element)
        if hollow(
            _
            for _ in element.children
            if not isinstance(_, (summary, headline))
        ):
            raise self.error("accordion: expected some content, got none")
        for para in element.children:
            if type(para) is nodes.paragraph:
                para["classes"].append("km-accordion__paragraph")
        return [element, *messages]


@html.opens(Accordion)
def visit(self: HTMLTranslator, node: Accordion) -> None:
    """Open the accordion.

    :param self: The HTML translator, whose body this appends to.
    :param node: The accordion's node.
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


html.closes(Accordion, "</div></details>")


@html.opens(summary)
def visit_summary(self: HTMLTranslator, node: summary) -> None:
    """Open the title. Put the marker first if it goes before the title.

    :param self: The HTML translator, whose body this appends to.
    :param node: The title's node.
    """
    classes = accordion.title(more=node["classes"])
    self.body.append(f'<summary class="{self.attval(classes)}">')
    if not node["after"]:
        self.body.append(marker(self, node))
    self.body.append(f'<span class="{accordion.text()}">')


@html.closes(summary)
def depart_summary(self: HTMLTranslator, node: summary) -> None:
    """Close the title and open the content.

    :param self: The HTML translator, whose body this appends to.
    :param node: The title's node.
    """
    self.body.append("</span>")
    if node["after"]:
        self.body.append(marker(self, node))
    classes = accordion.body(more=node.parent["body"])
    self.body.append(f'</summary><div class="{self.attval(classes)}">')


@html.opens(headline, elsewhere="inline")
def visit_headline(self: HTMLTranslator, node: headline) -> None:
    """Open the line above or below the title.

    :param self: The HTML translator, whose body this appends to.
    :param node: The line's node.
    """
    role = node["role"]
    classes = getattr(accordion, role)(more=[text[role], *node["classes"]])
    self.body.append(f'<span class="{self.attval(classes)}">')


html.closes(headline, "</span>")


def marker(self: HTMLTranslator, node: summary) -> str:
    """Write the icon that shows that the accordion opens.

    :param self: The HTML translator.
    :param node: The title's node.
    :return: The marker's HTML.
    """
    icons = Icons.of(self.builder.config)
    classes = icons.pair(ACCORDION_MARKERS[node.parent["marker"]])
    return (
        f'<span class="{accordion.marker()}">'
        f'<span class="{classes} {accordion.icon()}"'
        ' aria-hidden="true"></span></span>'
    )


node = Accordion
