"""\
HTML Writer
===========

Author: Akshay Mestry <xa@mes3.dev>
Created on: 27 September 2026
Last updated on: 07 November 2026

What Kaamiki changes in the HTML Sphinx writes, as it writes it.
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
from kaamiki.extensions.utils.icons import Icons
from kaamiki.extensions.utils.links import guarded
from kaamiki.extensions.utils.links import opens_new_tab
from kaamiki.extensions.utils.settings import setting
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
RELEASE_KINDS: t.Final[dict[str, str]] = {
    "added": "release_added",
    "changed": "release_changed",
    "fixed": "release_fixed",
    "removed": "release_removed",
    "deprecated": "release_removed",
}
NO_TICK: t.Final[frozenset[str]] = frozenset(
    {"km-release__body", "contents", "toctree-wrapper"}
)
PILCROW: t.Final[frozenset[str]] = frozenset({"", "\u00b6"})
LONG_LITERAL: t.Final[int] = 40
BACKREF: re.Pattern[str] = re.compile(
    r'</a><a class="headerlink" href="([^"]*)" title="([^"]*)">(.*)',
    re.DOTALL,
)


class translator(base):
    """What Kaamiki adds to the builder's own HTML translator.

    `install` puts it in front of the builder's translator, so one a
    site swapped in is kept.
    """

    def permalink(self, title: str) -> tuple[str, str]:
        """Work out a heading anchor's label and what it shows.

        :param title: The title Sphinx gives the anchor.
        :return: The label's attribute and the anchor's content.
            Sphinx's pilcrow is dropped, since a click anywhere on the
            heading follows the anchor. A site that
            set `html_permalinks_icon` of its own keeps it.
        """
        icon: str = self.config.html_permalinks_icon
        if icon.strip() in PILCROW:
            icon = ""
        if setting(self.config, "copy_headerlinks"):
            return f' aria-label="{html.escape(str(_("Copy link")))}"', icon
        return f' title="{title}"', icon

    @t.override
    def add_permalink_ref(self, node: nodes.Element, title: str) -> None:
        """Write the anchor a heading, caption or table links to.

        The page's own title, its first section, gets none. Every
        heading after it does, a second top-level one included.

        :param node: The element whose first id the anchor points at.
        :param title: The title Sphinx gives the anchor.
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
        """Open and close a section's heading, without a link back.

        :param node: The section's title.
        :return: The opening and the closing markup.
        """
        if not node.hasattr("refid") or not setting(
            self.config, "copy_headerlinks"
        ):
            return super().section_title_tags(node)
        refid = node["refid"]
        del node["refid"]
        tags = super().section_title_tags(node)
        node["refid"] = refid
        return tags

    def icon(self, key: str, *classes: str) -> str:
        """Write one of Kaamiki's own icons, the way the site draws it.

        :param key: The icon's name in `icons.ROLE_ICONS`.
        :param classes: Classes to put beside the icon's own.
        :return: The icon's markup or nothing for a site that set none.
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

        :param node: The admonition being opened.
        :param name: Its kind, `note` for a note.
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
        """Open a bullet's item with a tick in front of it.

        The lists of a table of contents, of the navigation and of a
        release's notes have no tick.

        :param node: The item being opened.
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
        """Open a quote's first paragraph with an opening quotation
        mark.

        :param node: The paragraph being opened.
        """
        super().visit_paragraph(node)
        if self.opens_quote(node):
            self.body.append("\u201c")

    @t.override
    def depart_paragraph(self, node: nodes.paragraph) -> None:
        """Close a quote's first paragraph with a closing quotation
        mark.

        :param node: The paragraph being closed.
        """
        if self.opens_quote(node):
            self.body.append("\u201d")
        super().depart_paragraph(node)

    @staticmethod
    def opens_quote(node: nodes.paragraph) -> bool:
        """Say whether a paragraph is the first one of a block
        quote.
        """
        parent = node.parent
        return isinstance(parent, nodes.block_quote) and parent.index(node) == 0

    @t.override
    def visit_term(self, node: nodes.Element) -> None:
        """Open a release's group with the icon of its kind.

        :param node: The term being opened.
        """
        super().visit_term(node)
        classes: list[str] = node.get("classes", [])
        if "km-release__kind" not in classes:
            return
        key = "release_other"
        for name, role in RELEASE_KINDS.items():
            if f"km-release__kind--{name}" in classes:
                key = role
        self.body.append(self.icon(key, "km-release__icon"))

    @t.override
    def visit_title(self, node: nodes.title) -> None:
        """Open a title, giving a table of contents' caption a level.

        :param node: The title being opened.
        """
        start = len(self.body)
        super().visit_title(node)
        self.body[start:] = [levelled(_) for _ in self.body[start:]]

    @t.override
    def depart_title(self, node: nodes.title) -> None:
        """Close a title and fix the anchor Sphinx writes by hand.

        A heading linked back to a table of contents gets its anchor
        written inline, not through `add_permalink_ref`.

        :param node: The title being closed.
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
        """Open a literal, and let a long one wrap.

        One longer than `LONG_LITERAL` characters can pass the width of
        a column, so it may wrap.

        :param node: The literal being opened.
        """
        if len(node.astext()) > LONG_LITERAL:
            node["classes"].append("km-literal--long")
        super().visit_literal(node)

    @t.override
    def visit_table(self, node: nodes.table) -> None:
        """Open a table inside a box that scrolls when it's too wide.

        :param node: The table being opened.
        """
        self.body.append('<div class="km-table">')
        super().visit_table(node)

    @t.override
    def depart_table(self, node: nodes.table) -> None:
        """Close a table and the box it's in.

        :param node: The table being closed.
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
        """Open a tag, with what Kaamiki changes in it.

        A link that leaves the site goes to a new tab. Every bullet and
        numbered list gets `km-list`, which the stylesheet counts with,
        and a numbered list that doesn't start at 1 gets a
        `counter-reset` for its `style`, so the count starts where the
        list does. The classes a tag is given come before the ones the
        page's author wrote with `:class:`.

        :param node: The node the tag belongs to.
        :param tagname: The tag's name.
        :param suffix: What follows the tag.
        :param empty: Whether the tag closes itself.
        :param attributes: The tag's attributes.
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
        """Open an image, loading it lazily unless told otherwise.

        :param node: The image being written.
        """
        default = getattr(self, "image_loading", "")
        if "loading" not in node and default == "link":
            node["loading"] = "lazy"
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
        """Open a topic as a `div`, since an `aside` inside the page's
        text is a landmark nested in another one.

        :param node: The topic being opened.
        """
        super().visit_topic(node)
        if getattr(node, "html5tagname", "") == "aside":
            setattr(node, "html5tagname", "div")  # noqa: B010
            self.body[-1] = self.body[-1].replace("<aside", "<div", 1)

    @t.override
    def visit_sidebar(self, node: nodes.sidebar) -> None:
        """Open a sidebar as a `div`, for the reason a topic is one.

        :param node: The sidebar being opened.
        """
        super().visit_sidebar(node)
        self.body[-1] = self.body[-1].replace("<aside", "<div", 1)

    @t.override
    def depart_sidebar(self, node: nodes.sidebar) -> None:
        """Close a sidebar's `div`.

        :param node: The sidebar being closed.
        """
        self.body.append("</div>\n")
        self.in_sidebar = False

    @t.override
    def visit_caption(self, node: nodes.caption) -> None:
        """Open a code block's caption with its language's icon in
        front.

        :param node: The caption being opened.
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
        """Open a compound, unless it's a hidden toctree's empty
        shell.

        :param node: The compound being opened.
        :raises nodes.SkipNode: For a `toctree-wrapper` with nothing
            left in it, which would paint nothing and leave a gap.
        """
        if "toctree-wrapper" in node["classes"] and not node.children:
            raise nodes.SkipNode
        super().visit_compound(node)


def install(app: Sphinx) -> None:
    """Put `translator` in front of the builder's HTML translator.

    Only HTML builders get it.

    :param app: The Sphinx application instance.
    """
    builder = app.builder
    if not isinstance(builder, StandaloneHTMLBuilder):
        return
    current = builder.get_translator_class()
    if issubclass(current, translator):
        return
    combined = type(current.__name__, (translator, current), {})
    app.set_translator(builder.name, combined, override=True)
