"""\
HTML Writer
===========

Author: Akshay Mestry <xa@mes3.dev>
Created on: 27 September, 2026
Last updated on: 30 September, 2026

What the theme changes in the HTML Sphinx writes, done as it writes it.

A heading's anchor shows the `permalink` icon and, with
`add_copy_to_headerlinks` on, is labelled for the copy it makes. An
external link that leaves the site opens in a new tab with `nofollow`
and `noopener` added to its `rel`, unless `open_links_in_new_tab` is
off. One to the site's own address or a `mailto:` stays in the tab.
An image loads lazily unless it asks otherwise. The empty wrapper a
hidden toctree leaves behind is never written.
"""

from __future__ import annotations

import html
import re
import typing as t

import docutils.nodes as nodes
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.locale import _

from kaamiki.extensions.utils import ICONS
from kaamiki.extensions.utils import elsewhere
from kaamiki.extensions.utils import themed

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html5 import HTML5Translator

    base = HTML5Translator
else:
    base = object

PILCROW: t.Final[frozenset[str]] = frozenset({"", "¶"})
BACKREF: re.Pattern[str] = re.compile(
    r'</a><a class="headerlink" href="([^"]*)" title="([^"]*)">(.*)',
    re.DOTALL,
)


class translator(base):
    """What the theme adds to the builder's own HTML translator.

    `install` puts it in front of whichever translator the builder was
    going to use, so a site or an extension that swapped in one of its
    own keeps it.
    """

    def permalink(self, title: str) -> tuple[str, str]:
        """Work out a heading anchor's label and what it shows.

        :param title: The title Sphinx gives the anchor.
        :return: The label's attribute and the icon's markup. The
            `permalink` icon replaces Sphinx's pilcrow, so a site that
            set `html_permalinks_icon` of its own keeps it.
        """
        options = self.config.html_context
        icon: str = self.config.html_permalinks_icon
        if icon.strip() in PILCROW:
            classes = (options.get("km_fa_icons") or ICONS).get("permalink", "")
            if classes:
                icon = (
                    f'<i class="{html.escape(classes)}" aria-hidden="true"></i>'
                )
        if options.get("km_add_copy_to_headerlinks", True):
            return f' aria-label="{html.escape(str(_("Copy link")))}"', icon
        return f' title="{title}"', icon

    @t.override
    def add_permalink_ref(self, node: nodes.Element, title: str) -> None:
        """Write the anchor a heading, a caption or a table links to.

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
    def depart_title(self, node: nodes.title) -> None:
        """Close a title and fix the anchor Sphinx writes by hand.

        A heading that links back to a table of contents gets its anchor
        written inline rather than through `add_permalink_ref`.

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
        """Open a tag, sending a link that leaves the site to a new tab.

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
            and elsewhere(href, self.config.html_baseurl)
            and self.config.html_context.get("km_open_links_in_new_tab", True)
        ):
            rel = str(attributes.get("rel") or "").split()
            wanted = [*rel, "nofollow", "noopener"]
            attributes["rel"] = " ".join(dict.fromkeys(wanted))
            attributes["target"] = "_blank"
        return super().starttag(node, tagname, suffix, empty, **attributes)

    @t.override
    def visit_image(self, node: nodes.image) -> None:
        """Open an image, loading it lazily unless told otherwise.

        docutils only writes `loading="lazy"` when an image asks for it
        with `:loading: lazy` or the site's docutils settings do, so
        every image loaded with the page, the ones far below the fold
        included. An image's own `:loading:` or an `image_loading`
        other than the default, still wins.

        :param node: The image being written.
        """
        default = getattr(self, "image_loading", "")
        if "loading" not in node and default == "link":
            node["loading"] = "lazy"
        super().visit_image(node)

    @t.override
    def visit_compound(self, node: nodes.compound) -> None:
        """Open a compound, unless it is a hidden toctree's empty shell.

        :param node: The compound being opened.
        :raises nodes.SkipNode: For a `toctree-wrapper` with nothing
            left in it, which would paint nothing and leave a gap.
        """
        if "toctree-wrapper" in node["classes"] and not node.children:
            raise nodes.SkipNode
        super().visit_compound(node)


def install(app: Sphinx) -> None:
    """Put `translator` in front of the builder's HTML translator.

    Only an HTML builder writing pages with this theme or with one
    built on it, gets it.

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
