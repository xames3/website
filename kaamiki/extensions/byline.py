"""\
Byline Directive
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February 2025
Last updated on: 15 November 2026

A `byline` directive that draws the byline under a page title::

    .. byline:: Akshay Mestry
       :avatar: https://example.com/avatar.png
       :target: https://github.com/xames3
       :avatar-size: 24
"""

from __future__ import annotations

import os.path as p
import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst
from babel import Locale
from babel import UnknownLocaleError

from kaamiki.extensions.utils import KaamikiDirective
from kaamiki.extensions.utils import Option
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import fields
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import opens_new_tab
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import phrase
from kaamiki.extensions.utils import reading_time
from kaamiki.extensions.utils import relative_to_page
from kaamiki.extensions.utils import render
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import unlinked
from kaamiki.extensions.utils import worded
from kaamiki.extensions.utils.settings import ALIGNMENTS
from kaamiki.extensions.utils.settings import BOUNDS

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

template: t.Final[str] = "directives/byline.html.jinja"
BACKDROPS: t.Final[int] = 8


def backdrops(argument: str | None) -> str:
    """Check the pictures to fade through, one address each.

    :param argument: The addresses as written, a comma between each.
    :return: The addresses, a space between each.
    :raises ValueError: For one that isn't an address, one twice or
        more than `BACKDROPS`.
    """
    found = [_.strip() for _ in (argument or "").split(",")]
    if not all(found) or len(found) > BACKDROPS:
        raise ValueError(
            f"expected one to {BACKDROPS} addresses split by commas, got"
            f" {argument!r}"
        )
    for each in found:
        checks.picture(each)
    if len(set(found)) != len(found):
        raise ValueError(
            f"expected addresses that are all different, got {argument!r}"
        )
    return " ".join(found)


def source_url(self: HTMLTranslator) -> str:
    """Link the page's plain-text source, the one Sphinx copies.

    :param self: The HTML translator, writing the page.
    :return: The address, or an empty string with `html_copy_source` or
        `html_show_sourcelink` off.
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
    """Spell a language in its own words, like `English` for `en`.

    :param code: The language code, like `en` or `pt-BR`.
    :return: The name, or the code itself for one babel doesn't know.
    """
    try:
        display = Locale.parse(code, sep="-").get_display_name()
    except ValueError, UnknownLocaleError:
        return code
    return display[:1].upper() + display[1:] if display else code


class Byline(KaamikiDirective, motion=True):
    """The `byline` directive.

    Put it on the page itself, one time. An `only` is part of the page.
    A container and the content of a different directive are not.

    Options::

        - `avatar`: The URL of the author's picture.
        - `target`: The link of the name, as a profile or a mailto. A
          path starts at the top of the site, as for `avatar` and
          `backdrop`.
        - `backdrop`: One or more image URLs, with a comma between each.
          They fade one into the next behind the title.
        - `avatar-size`: The width and height of the picture in pixels,
          from 16 to 64. The default is 20.
        - `interval`: The seconds that each backdrop shows, from 2 to 15.
          It needs two or more `backdrop` pictures. The default is 7.
        - `align`: Where the byline is, `left`, `center` or `right`. Only
          `left` puts the author, the reading time, the language and the
          copy button in one row. On a phone, that row shows only the
          author and the reading time. The default is `left`.
        - `hide-reading-time`: Do not show the reading time.
        - `hide-copy-url`: Do not show the copy button.
        - `hide-source`: Do not show the link to the plain-text source
          of the page. Without it, the link shows when `html_copy_source`
          and `html_show_sourcelink` are on.
        - `show-language`: Show the language of the page. It is the
          `:km-page-language:` field of the page, or the `language` of
          the Sphinx configuration when the page has no field.
        - `speed`: The speed of its motion, relative to the site, one
          of `0.25`, `0.5`, `0.75`, `1`, `1.5`, `2`, `3` or `4`. `2` is
          two times as fast.
        - `no-motion`: Do not move it.
        - `name`: A name for links.
        - `class`: More classes for the byline.
    """

    required_arguments = 1
    final_argument_whitespace = True
    avatar = Option(checks.link)
    target = Option(checks.link)
    backdrop = Option(backdrops, default="")
    avatar_size = Option(checks.integer(*map(int, BOUNDS["avatar_size"])))
    interval = Option(checks.number(*BOUNDS["interval"]))
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
        if self.interval is not None and len(self.backdrop.split()) < 2:
            self.fail(":interval: needs two or more :backdrop: pictures")
        project = setting(self.config, "project")
        if self.avatar_size is not None and not (
            self.avatar or project.get("avatar")
        ):
            self.fail(":avatar-size: needs an avatar")

    def build(self) -> list[nodes.Node]:
        """Keep what the page writes on the node and name the author.

        The `visit` function adds the rest from
        `kaamiki.conf.site.project`. The name also becomes the author of
        the page, if its `.. Author:` comment does not name one first.
        The first backdrop is a fallback for the social image of the
        page.

        :return: The node, the `raw` nodes from `trail` for the link
            checker and what the parser reported.
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
        if pictures := self.backdrop.split():
            metadata.setdefault("km-page-backdrop", pictures[0])
        node = self.locate(self.Node("", words, **options))
        self.add_name(node)
        return [node, *trail(self, options), *messages]

    @staticmethod
    def plain(node: Byline.Node) -> list[nodes.Node]:
        """Write a byline as words, for a builder that writes no HTML.

        :param node: The byline's node.
        :return: A paragraph with the author's name.
        """
        author = next(
            each for each in node.children if isinstance(each, phrase)
        )
        return [nodes.paragraph("", "", *author.children)]


@html.opens(Byline.Node)
def visit(self: HTMLTranslator, node: Byline.Node) -> None:
    """Write the widget out when the HTML writer reaches the node.

    :param self: The HTML translator, whose body this appends to.
    :param node: The `byline` node, its attributes and its name.
    :raises nodes.SkipNode: Always, since the name is written already.
    """
    config = self.builder.config
    context = config.html_context
    attributes = dict(node.attributes)
    attributes.update(fields(self, node))
    attributes["project"] = context["km_project"]
    target = attributes.get("target") or attributes["project"]["source"]
    attributes["new_tab"] = opens_new_tab(target, config)
    attributes["target"] = relative_to_page(self, target)
    attributes["fa_icons"] = context["km_fa_icons"]
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
    avatar = attributes.get("avatar") or attributes["project"]["avatar"]
    attributes["avatar"] = relative_to_page(self, avatar)
    backdrop = attributes.get("backdrop", "").split()
    pictures = [relative_to_page(self, _) for _ in backdrop]
    attributes["data"] = {"data-km-backdrop": " ".join(pictures) or None}
    if pictures and "interval" in attributes:
        attributes["data"]["data-km-interval"] = round(
            attributes["interval"] * 1000
        )
    self.body.append(render(template, **attributes))
    raise nodes.SkipNode


def html_page_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Name the page's author for the `<head>`.

    The `.. Author:` comment or the byline wins, then the project's
    author.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree or `None` for generated
        pages.
    """
    del pagename, templatename, doctree
    meta: dict[str, str] = context.get("meta") or {}
    project = app.config.html_context["km_project"]
    context["km_author"] = meta.get("author") or project.get("author")
