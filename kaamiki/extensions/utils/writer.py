"""\
HTML Writer
===========

Author: Akshay Mestry <xa@mes3.dev>
Created on: 27 September 2026
Last updated on: 15 November 2026

What Kaamiki changes in the HTML that Sphinx writes, while it writes
it.
"""

from __future__ import annotations

import html
import os
import re
import typing as t

import docutils.nodes as nodes
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.locale import _
from sphinx.util.images import get_image_size

from kaamiki.extensions.utils.doctree import caption_icon
from kaamiki.extensions.utils.hooks import on
from kaamiki.extensions.utils.icons import Icons
from kaamiki.extensions.utils.links import guarded
from kaamiki.extensions.utils.links import opens_new_tab
from kaamiki.extensions.utils.settings import values
from kaamiki.extensions.utils.text import levelled

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html5 import HTML5Translator

    base = HTML5Translator
else:
    base = object

ADMONITIONS: t.Final[dict[str, str]] = {
    "note": "note",
    "seealso": "seealso",
    "tip": "tip",
    "hint": "hint",
    "important": "important",
    "danger": "danger",
    "error": "error",
    "warning": "warning",
    "caution": "warning",
    "attention": "warning",
}
NO_TICK: t.Final[frozenset[str]] = frozenset(
    {"km-release__body", "contents", "toctree-wrapper"}
)
PILCROW: t.Final[frozenset[str]] = frozenset({"", "\u00b6"})
LONG_LITERAL: t.Final[int] = 40
BACKREF: t.Final[re.Pattern[str]] = re.compile(
    r'</a><a class="headerlink" href="([^"]*)" title="([^"]*)">(.*)',
    re.DOTALL,
)


class translator(base):
    """What Kaamiki adds to the HTML translator of the builder."""

    def permalink(self, title: str) -> tuple[str, str]:
        """Find the label of a heading anchor and what it shows.

        :param title: The title that Sphinx gives the anchor.
        :return: The label attribute and the content of the anchor. The
            pilcrow of Sphinx goes, because a click on the heading
            follows the anchor. A site with its own
            `html_permalinks_icon` keeps it.
        """
        icon: str = self.config.html_permalinks_icon
        if icon.strip() in PILCROW:
            icon = ""
        if values(self.config).site.copy_headerlinks:
            return f' aria-label="{html.escape(str(_("Copy link")))}"', icon
        return f' title="{title}"', icon

    @t.override
    def add_permalink_ref(self, node: nodes.Element, title: str) -> None:
        """Write the anchor of a heading, a caption or a table.

        :param node: The element whose first id the anchor points at.
            The title of the page, its first section, gets none. Each
            heading after it gets one, also a second top-level heading.
        :param title: The title that Sphinx gives the anchor.
        """
        if not node["ids"] or not self.config.html_permalinks:
            return
        if isinstance(node.parent, nodes.document) and node is next(
            node.parent.findall(nodes.section), None
        ):
            return
        if not self.builder.add_permalinks:
            return
        label, icon = self.permalink(title)
        self.body.append(
            f'<a class="headerlink" href="#{node["ids"][0]}"{label}>{icon}</a>'
        )

    @t.override
    def section_title_tags(self, node: nodes.Element) -> tuple[str, str]:
        """Open and close a section heading, with no back link.

        :param node: The title of the section.
        :return: The markup that opens it and the markup that closes
            it.
        """
        if (
            not node.hasattr("refid")
            or not values(self.config).site.copy_headerlinks
        ):
            return super().section_title_tags(node)
        refid = node["refid"]
        del node["refid"]
        tags = super().section_title_tags(node)
        node["refid"] = refid
        return tags

    def icon(self, key: str, *classes: str) -> str:
        """Write one of the icons of Kaamiki, as the site draws it.

        :param key: The name of the icon in `icons.ROLE_ICONS`.
        :param classes: The classes to put next to those of the icon.
        :return: The markup of the icon, or nothing when the site set
            none.
        """
        found = self.builder.config.html_context["km_fa_icons"][key]
        if not found:
            return ""
        return (
            f'<i class="{" ".join([found, *classes])}" aria-hidden="true"></i>'
        )

    @t.override
    def visit_admonition(self, node: nodes.Element, name: str = "") -> None:
        """Open an admonition with the icon of its kind.

        :param node: The admonition.
        :param name: Its kind, as `note` for a note.
        """
        super().visit_admonition(node, name)
        if name in ADMONITIONS:
            self.body.append(
                self.icon(
                    f"admonition_{ADMONITIONS[name]}", "km-admonition__icon"
                )
            )

    @t.override
    def visit_list_item(self, node: nodes.list_item) -> None:
        """Open the item of a bullet list with a tick before it.

        :param node: The item. The lists of a table of contents, of the
            navigation and of the notes of a release get no tick.
        """
        super().visit_list_item(node)
        if not isinstance(node.parent, nodes.bullet_list):
            return
        if str(self.document.get("source", "")).startswith("<"):
            return
        parent: nodes.Element | None = node.parent
        while parent is not None:
            if NO_TICK.intersection(parent.get("classes", [])):
                return
            parent = parent.parent
        self.body.append(self.icon("list_tick", "km-list__tick"))

    @t.override
    def visit_paragraph(self, node: nodes.paragraph) -> None:
        """Open the first paragraph of a quote with an opening mark.

        :param node: The paragraph.
        """
        super().visit_paragraph(node)
        if self.opens_quote(node):
            self.body.append("\u201c")

    @t.override
    def depart_paragraph(self, node: nodes.paragraph) -> None:
        """Close the first paragraph of a quote with a closing mark.

        :param node: The paragraph.
        """
        if self.opens_quote(node):
            self.body.append("\u201d")
        super().depart_paragraph(node)

    @staticmethod
    def opens_quote(node: nodes.paragraph) -> bool:
        """Say whether a paragraph is the first in a block quote.

        :param node: The paragraph.
        :return: `True` when it is the first in a block quote.
        """
        parent = node.parent
        return isinstance(parent, nodes.block_quote) and parent.index(node) == 0

    @t.override
    def visit_title(self, node: nodes.title) -> None:
        """Open a title, and give a toctree caption a level.

        :param node: The title.
        """
        start = len(self.body)
        super().visit_title(node)
        self.body[start:] = [levelled(_) for _ in self.body[start:]]

    @t.override
    def depart_title(self, node: nodes.title) -> None:
        """Close a title, and correct the anchor of Sphinx.

        :param node: The title. A heading with a back link to a table
            of contents gets its anchor inline, not through
            `add_permalink_ref`.
        """
        start = len(self.body)
        super().depart_title(node)
        for index in range(start, len(self.body)):
            match = BACKREF.fullmatch(self.body[index])
            if match is None:
                continue
            label, icon = self.permalink(match[2])
            self.body[index] = (
                f'</a><a class="headerlink" href="{match[1]}"{label}>{icon}'
            )

    @t.override
    def visit_literal(self, node: nodes.Element) -> None:
        """Open a literal, and let a long literal wrap.

        :param node: The literal. A literal longer than `LONG_LITERAL`
            characters can be wider than a column, so it can wrap.
        """
        if len(node.astext()) > LONG_LITERAL:
            node["classes"].append("km-literal--long")
        super().visit_literal(node)

    @t.override
    def visit_table(self, node: nodes.table) -> None:
        """Open a table in a box that scrolls when it is wide.

        :param node: The table. The box takes `km-wide` from the table,
            because the page gives its width to the box.
        """
        wide = " km-wide" if "km-wide" in node["classes"] else ""
        self.body.append(f'<div class="km-table{wide}">')
        super().visit_table(node)

    @t.override
    def depart_table(self, node: nodes.table) -> None:
        """Close a table and its box.

        :param node: The table.
        """
        super().depart_table(node)
        self.body.append("</div>")

    @t.override
    def starttag(
        self,
        node: nodes.Element,
        tagname: str,
        suffix: str = "\n",
        empty: bool = False,
        **attributes: t.Any,
    ) -> str:
        """Open a tag, with the changes of Kaamiki.

        :param node: The node of the tag. A link to a different site
            opens in a new tab. Each bullet and numbered list gets
            `km-list`, for the counts of the stylesheet. A numbered
            list that does not start at 1 gets a `counter-reset` in its
            `style`. The classes of a tag come before the `:class:` of
            the author.
        :param tagname: The name of the tag.
        :param suffix: What follows the tag.
        :param empty: Whether the tag closes itself.
        :param attributes: The attributes of the tag.
        :return: The opening tag.
        """
        classes = str(attributes.get("class") or attributes.get("CLASS") or "")
        href = str(attributes.get("href") or "")
        if (
            tagname == "a"
            and "external" in classes.split()
            and opens_new_tab(href, self.config)
        ):
            attributes["rel"] = guarded(str(attributes.get("rel") or ""))
            attributes["target"] = "_blank"
        if isinstance(node, (nodes.bullet_list, nodes.enumerated_list)):
            key = "CLASS" if "CLASS" in attributes else "class"
            attributes[key] = f"{attributes.get(key) or ''} km-list".strip()
        if tagname == "ol" and "start" in attributes:
            attributes["style"] = (
                f"counter-reset: km-list {int(attributes['start']) - 1}"
            )
        own = f"{attributes.pop('CLASS', '')} {attributes.pop('class', '')}"
        if own.strip():
            attributes["classes"] = [
                *attributes.get("classes", []),
                *own.split(),
            ]
        return super().starttag(node, tagname, suffix, empty, **attributes)

    @t.override
    def visit_image(self, node: nodes.image) -> None:
        """Open an image, and load it lazily unless told otherwise.

        :param node: The image. Each image from an author, alone or in
            a figure, gets `km-image`, so that the script of the page
            can find it among the pictures of Kaamiki. An image with a
            size also gets `km-image--sized`.
        """
        default = getattr(self, "image_loading", "")
        if "loading" not in node and default == "link":
            node["loading"] = "lazy"
        node["classes"].append("km-image")
        sized = any(_ in node for _ in ("width", "height", "scale"))
        if sized:
            node["classes"].append("km-image--sized")
        source = str(node["uri"])
        super().visit_image(node)
        if (
            "height" in node
            or "scale" in node
            or "://" in source
            or source.startswith("data:")
        ):
            return
        size = get_image_size(os.path.join(self.builder.srcdir, source))
        if size and self.body[-1].startswith("<img "):
            self.body[-1] = self.body[-1].replace(
                "<img ", f'<img width="{size[0]}" height="{size[1]}" ', 1
            )

    @t.override
    def visit_topic(self, node: nodes.topic) -> None:
        """Open a topic as a `div`.

        :param node: The topic. An `aside` in the text of the page
            would be a landmark in a landmark.
        """
        super().visit_topic(node)
        if getattr(node, "html5tagname", "") == "aside":
            setattr(node, "html5tagname", "div")  # noqa: B010
            self.body[-1] = self.body[-1].replace("<aside", "<div", 1)

    @t.override
    def visit_sidebar(self, node: nodes.sidebar) -> None:
        """Open a sidebar as a `div`, as for a topic.

        :param node: The sidebar.
        """
        super().visit_sidebar(node)
        self.body[-1] = self.body[-1].replace("<aside", "<div", 1)

    @t.override
    def depart_sidebar(self, node: nodes.sidebar) -> None:
        """Close the `div` of a sidebar.

        :param node: The sidebar.
        """
        self.body.append("</div>\n")
        self.in_sidebar = False

    @t.override
    def visit_caption(self, node: nodes.caption) -> None:
        """Open a code block caption, with its language icon.

        :param node: The caption.
        """
        super().visit_caption(node)
        parent = node.parent
        if not isinstance(parent, nodes.container):
            return
        if not parent.get("literal_block"):
            return
        block = next(
            (_ for _ in parent.children if isinstance(_, nodes.literal_block)),
            None,
        )
        if block is None:
            return
        icon = caption_icon(
            node, block.get("language"), icons=Icons.of(self.config)
        )
        if icon:
            self.body.append(
                f'<span class="km-lang-icon {icon}" aria-hidden="true"></span>'
            )

    @t.override
    def visit_compound(self, node: nodes.compound) -> None:
        """Open a compound, unless it is an empty toctree wrapper.

        :param node: The compound.
        :raises nodes.SkipNode: For a `toctree-wrapper` that holds
            nothing, which would show only a gap.
        """
        if "toctree-wrapper" in node["classes"] and not node.children:
            raise nodes.SkipNode
        super().visit_compound(node)


@on("builder-inited")
def install(app: Sphinx) -> None:
    """Put `translator` before the HTML translator of the builder.

    :param app: The Sphinx application instance. Only HTML builders get
        it, and a translator that a site set is kept below it.
    """
    builder = app.builder
    if not isinstance(builder, StandaloneHTMLBuilder):
        return
    current = builder.get_translator_class()
    if issubclass(current, translator):
        return
    combined = type(current.__name__, (translator, current), {})
    app.set_translator(builder.name, combined, override=True)
