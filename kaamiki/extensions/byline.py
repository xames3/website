"""\
Byline Directive
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February 2025
Last updated on: 28 November 2026

A `byline` directive that draws the byline below the title of a page::

    .. byline:: Akshay Mestry
       :avatar: https://example.com/avatar.png
       :target: https://github.com/xames3
       :avatar-size: 24
       :shade: orange
       :swirl: 2

Put it on the page itself, one time. An `only` is part of the page. A
container and the content of a different directive are not.
"""

from __future__ import annotations

import os.path as p
import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst
from babel import Locale
from babel import UnknownLocaleError

from kaamiki.extensions.utils import Kaamiki
from kaamiki.extensions.utils import KaamikiDirective
from kaamiki.extensions.utils import Option
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import fields
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import on
from kaamiki.extensions.utils import opens_new_tab
from kaamiki.extensions.utils import optional
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import reading_time
from kaamiki.extensions.utils import relative_to_page
from kaamiki.extensions.utils import render
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import unlinked
from kaamiki.extensions.utils import values
from kaamiki.extensions.utils import worded
from kaamiki.extensions.utils.banner import SHADE
from kaamiki.extensions.utils.banner import SHADES
from kaamiki.extensions.utils.banner import SWIRLS
from kaamiki.extensions.utils.banner import Banner
from kaamiki.extensions.utils.banner import banners
from kaamiki.extensions.utils.banner import source
from kaamiki.extensions.utils.banner import swirl
from kaamiki.extensions.utils.icons import Icons
from kaamiki.extensions.utils.settings import ALIGNMENTS
from kaamiki.extensions.utils.settings import BOUNDS
from kaamiki.extensions.utils.settings import NAME

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

template: t.Final[str] = "directives/byline.html.jinja"


def source_url(self: HTMLTranslator) -> str:
    """Link the plain-text source of the page that Sphinx copies.

    :param self: The HTML translator that writes the page.
    :return: The address, or an empty string when `html_copy_source` or
        `html_show_sourcelink` is off.
    """
    builder = self.builder
    config = builder.config
    if not (config.html_copy_source and config.html_show_sourcelink):
        return ""
    path = str(builder.env.doc2path(builder.current_docname, base=False))
    suffix = p.splitext(path)[1]
    if suffix != config.html_sourcelink_suffix:
        path += config.html_sourcelink_suffix
    return relative_to_page(self, f"_sources/{path.replace(p.sep, '/')}")


def native(code: str) -> str:
    """Write a language in its own words, as `English` for `en`.

    :param code: The language code, as `en` or `pt-BR`.
    :return: The name, or the code when Babel does not know it.
    """
    try:
        display = Locale.parse(code, sep="-").get_display_name()
    except ValueError, UnknownLocaleError:
        return code
    return display[:1].upper() + display[1:] if display else code


class Byline(KaamikiDirective, motion=True):
    """The `byline` directive.

    Options::

        - `avatar`: The URL of the picture of the author.
        - `target`: The link of the name, as a profile or a mailto.
          A path starts at the top of the site, as for `avatar`.
        - `avatar-size`: The width and height of the picture in
          pixels, from 16 to 64. The default is 20.
        - `banner`: A picture for the cards that link to the page:
          a URL, or a file relative to the page, or to the source
          directory when it starts with a `/`. Without it, the
          banner is a swirl in `shade` with the icon.
        - `shade`: The colour of the swirl, one of `blue`,
          `indigo`, `purple`, `red`, `orange`, `yellow`, `green`,
          `teal` or `graphite`. The default is `blue`.
        - `swirl`: The shape of the swirl, from `1` to `4`. The
          default comes from the name of the page, the same in each
          build.
        - `fa-icon`: A Font Awesome icon for the swirl, as on a
          button. The default is the first icon of the title, else
          no icon.
        - `align`: Where the byline is, `left`, `center` or
          `right`. Only `left` puts the author, the reading time,
          the language and the copy button in one row. On a phone,
          that row shows only the author and the reading time. The
          default is `left`.
        - `hide-reading-time`: Do not show the reading time.
        - `hide-copy-url`: Do not show the copy button.
        - `hide-source`: Do not show the link to the plain-text
          source of the page. Without it, the link shows when
          `html_copy_source` and `html_show_sourcelink` are on.
        - `show-language`: Show the language of the page. It is the
          `:km-page-language:` field of the page, or the `language`
          of the Sphinx configuration when the page has no field.
        - `speed`: The speed of its motion, relative to the site,
          one of `0.25`, `0.5`, `0.75`, `1`, `1.5`, `2`, `3` or
          `4`. `2` is two times as fast.
        - `no-motion`: Do not move it.
        - `name`: A name for links.
        - `class`: More classes for the byline.
    """

    required_arguments = 1
    final_argument_whitespace = True
    avatar = Option(checks.link)
    target = Option(checks.link)
    avatar_size = Option(checks.integer(*map(int, BOUNDS["avatar_size"])))
    banner = Option(checks.picture)
    shade = Option(checks.word(*SHADES), default=SHADE)
    swirl = Option(checks.word(*SWIRLS))
    fa_icon = Option(checks.icon)
    align = Option(checks.word(*ALIGNMENTS), default="left")
    hide_reading_time = Option(rst.directives.flag)
    hide_copy_url = Option(rst.directives.flag)
    hide_source = Option(rst.directives.flag)
    show_language = Option(rst.directives.flag)

    class Node(nodes.Element):
        """The byline, which `visit` writes with its template."""

    def check(self) -> None:
        """Permit one byline on a page, and the options it can use."""
        if self.env.temp_data.get("km_byline"):
            self.fail("expected once on a page, got it twice")
        self.env.temp_data["km_byline"] = True
        project = values(self.config).site.project
        if self.avatar_size is not None and not (
            self.avatar or project.get("avatar")
        ):
            self.fail(":avatar-size: needs an avatar")
        given = [
            _
            for _ in ("banner", "shade", "swirl", "fa-icon")
            if _ in self.options
        ]
        if self.banner and len(given) > 1:
            self.fail(f":{given[1]}: not allowed with :banner:")

    def build(self) -> list[nodes.Node]:
        """Keep the values on the node, and name the author.

        :return: The node, the `raw` nodes from `trail` for the link
            checker, and what the parser reported. `visit` adds the
            rest from `kaamiki.conf.site.project`. The name also
            becomes the author of the page, if its `.. Author:` comment
            names none. The banner is kept for the page.
        """
        written = self.arguments.pop().strip()
        options = self.options
        options["align"] = self.align
        options["reading_time"] = not self.hide_reading_time
        options["copy_url"] = not self.hide_copy_url
        options["page_source"] = not self.hide_source
        options["language"] = self.show_language
        options["classes"] = self.classes
        options.pop("class", None)
        if self.avatar_size is not None:
            options["avatar_size"] = self.avatar_size
        words, messages = parse(self, written, "name")
        unlinked(self, words, "a name")
        worded(self, words, "a name")
        metadata = self.env.metadata.setdefault(self.env.docname, {})
        metadata.setdefault("author", words.astext().strip() or written)
        try:
            icon = Icons.of(self.config).custom(self.fa_icon)
        except ValueError as error:
            self.fail(f":fa-icon: {error}")
        picture = self.banner or ""
        if picture and "://" not in picture:
            try:
                picture = source(self.env, picture)
            except ValueError as error:
                self.fail(f":banner: {error}")
        docname = self.env.docname
        banners(self.env)[docname] = Banner(
            self.shade,
            icon,
            picture,
            self.swirl or swirl(docname),
        )
        node = self.locate(self.Node("", words, **options))
        self.add_name(node)
        return [node, *trail(self, options), *messages]


@html.opens(Byline.Node)
def visit(self: HTMLTranslator, node: Byline.Node) -> None:
    """Write the widget out when the HTML writer reaches the node.

    :param self: The HTML translator, whose body this appends to.
    :param node: The `byline` node, its attributes and its name.
    :raises nodes.SkipNode: Always, since the name is written already.
    """
    config = self.builder.config
    found = Kaamiki.of(self.builder)
    attributes = dict(node.attributes)
    attributes.update(fields(self, node))
    project = found.site.project
    target = attributes.get("target") or project["source"]
    attributes["new_tab"] = opens_new_tab(target, config)
    attributes["target"] = relative_to_page(self, target)
    attributes["minutes"] = max(1, reading_time(node.document, config))
    attributes["page_source"] = (
        source_url(self) if attributes["page_source"] else ""
    )
    meta = self.builder.env.metadata.get(self.builder.current_docname, {})
    code = (meta.get("km-page-language") or config.language or "en").replace(
        "_", "-"
    )
    attributes["language"] = (
        {"code": code, "name": native(code)} if attributes["language"] else {}
    )
    avatar = attributes.get("avatar") or project["avatar"]
    attributes["avatar"] = relative_to_page(self, avatar)
    self.body.append(render(template, optional=optional(node), **attributes))
    raise nodes.SkipNode


@on("html-page-context")
def html_page_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Name the author of the page.

    :param app: The Sphinx application instance. The `.. Author:`
        comment or the byline comes first, then the author of the
        project.
    :param pagename: The page that is written.
    :param templatename: The template that writes it.
    :param context: The context of the page, changed in place.
    :param doctree: The resolved doctree, or `None` for a generated
        page.
    """
    del app, pagename, templatename, doctree
    meta: dict[str, str] = context.get("meta") or {}
    found = context[NAME]
    found["page.author"] = meta.get("author") or found.site.project.get(
        "author"
    )
