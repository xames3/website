"""\
HTML Writer
===========

Author: Akshay Mestry <xa@mes3.dev>
Created on: 27 September 2026
Last updated on: 15 October 2026

What Kaamiki changes in the HTML Sphinx writes, as it writes it.
"""

import html
import re
import typing as t

import docutils.nodes as nodes
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.locale import _

from kaamiki.extensions.utils.doctree import badged
from kaamiki.extensions.utils.links import REL
from kaamiki.extensions.utils.links import opens_new_tab
from kaamiki.extensions.utils.settings import setting
from kaamiki.extensions.utils.templates import themed

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html5 import HTML5Translator

    base = HTML5Translator
else:
    base = object

PILCROW: t.Final[frozenset[str]] = frozenset({"", "\u00b6"})
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
        if setting(self.config, "add_copy_to_headerlinks"):
            return f' aria-label="{html.escape(str(_("Copy link")))}"', icon
        return f' title="{title}"', icon

    @t.override
    def add_permalink_ref(self, node: nodes.Element, title: str) -> None:
        """Write the anchor a heading, caption or table links to.

        :param node: The element whose first id the anchor points at.
        :param title: The title Sphinx gives the anchor.
        """
        if not node["ids"] or not self.config.html_permalinks:
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

        Under a `contents` table docutils links a heading back to its
        entry. With `add_copy_to_headerlinks` on, a click copies the
        heading's own link instead, so the link back is dropped.

        :param node: The section's title.
        :return: The opening and the closing markup.
        """
        if not node.hasattr("refid") or not setting(
            self.config, "add_copy_to_headerlinks"
        ):
            return super().section_title_tags(node)
        refid = node["refid"]
        del node["refid"]
        tags = super().section_title_tags(node)
        node["refid"] = refid
        return tags

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
    def starttag(
        self,
        node: nodes.Element,
        tagname: str,
        suffix: str = "\n",
        empty: bool = False,
        **attributes: t.Any,
    ) -> str:
        """Open a tag, sending a link that leaves the site to a new
        tab.

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
            rel = str(attributes.get("rel") or "").split()
            wanted = [*rel, *REL.split()]
            attributes["rel"] = " ".join(dict.fromkeys(wanted))
            attributes["target"] = "_blank"
        if isinstance(node, (nodes.bullet_list, nodes.enumerated_list)):
            key = "CLASS" if "CLASS" in attributes else "class"
            attributes[key] = f"{attributes.get(key) or ''} km-list".strip()
        if tagname == "ol" and "start" in attributes:
            attributes["style"] = (
                f"counter-reset: km-list {int(attributes['start']) - 1}"
            )
        return super().starttag(node, tagname, suffix, empty, **attributes)

    @t.override
    def visit_image(self, node: nodes.image) -> None:
        """Open an image, loading it lazily unless told otherwise.

        :param node: The image being written.
        """
        default = getattr(self, "image_loading", "")
        if "loading" not in node and default == "link":
            node["loading"] = "lazy"
        super().visit_image(node)

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
        kit = bool(setting(self.config, "fa_kit"))
        icon = badged(node, block.get("language"), kit=kit)
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

    Only HTML builders writing pages with this theme get it.

    :param app: The Sphinx application instance.
    """
    builder = app.builder
    if not isinstance(builder, StandaloneHTMLBuilder) or not themed(builder):
        return
    current = builder.get_translator_class()
    if issubclass(current, translator):
        return
    combined = type(current.__name__, (translator, current), {})
    app.set_translator(builder.name, combined, override=True)
