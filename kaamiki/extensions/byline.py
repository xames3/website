"""\
Byline Directive
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February 2025
Last updated on: 07 November 2026

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

from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import fields
from kaamiki.extensions.utils import located
from kaamiki.extensions.utils import named
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

name: t.Final[str] = "byline"
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


class Byline(nodes.Element):
    """The parsed directive, waiting for `visit` to write it out."""


class directive(rst.Directive):
    """The `byline` directive.

    It goes on the page itself, once. An `only` counts as the page, a
    container and the content of another directive don't.

    Options::

        - `avatar`: URL of the author's picture.
        - `target`: Where the name links to, a profile or a mailto. A
          path counts from the top of the site, like `avatar` and
          `backdrop`.
        - `backdrop`: One or more image URLs, a comma between each, to
          fade through behind the title.
        - `avatar-size`: The picture's width and height in pixels, from
          16 to 64. Defaults to 20.
        - `interval`: Seconds each backdrop stays, from 2 to 15. It
          needs two or more `backdrop` pictures. Defaults to 7.
        - `align`: Where the byline sits, `left`, `center` or `right`.
          Only `left` puts the author, the reading time, the language
          and the copy button in one row, which phones cut to the
          author and the reading time. Defaults to `left`.
        - `hide-reading-time`: Hides the reading time, which is shown
          without it.
        - `hide-copy-url`: Hides the copy button, which is shown
          without it.
        - `hide-source`: Hides the link to the page's plain-text
          source, which is shown without it while `html_copy_source`
          and `html_show_sourcelink` are on.
        - `show-language`: Shows the page's language, which is hidden
          without it: the page's `:km-page-language:` field, or the
          `language` in Sphinx's configuration when it has none.
        - `name`: A name to link to.
        - `class`: More classes for the byline.
    """

    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "avatar": checks.link,
        "target": checks.link,
        "backdrop": backdrops,
        "avatar-size": checks.integer(*map(int, BOUNDS["avatar_size"])),
        "interval": checks.number(*BOUNDS["interval"]),
        "align": checks.word(*ALIGNMENTS),
        "hide-reading-time": rst.directives.flag,
        "hide-copy-url": rst.directives.flag,
        "hide-source": rst.directives.flag,
        "show-language": rst.directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        """Collect the options and return the node.

        Only what the page writes goes on the node, `visit` fills in
        the rest from `kaamiki.conf.site.project`. The name also
        becomes the page's author, unless its `.. Author:` comment
        named one first, and the first backdrop, when written, becomes
        a fallback for its social image.

        :return: The node, followed by the `raw` nodes `trail` returns
            for the link checker and anything the name reported.
        """
        text = self.arguments.pop().strip()
        env = self.state.document.settings.env
        if env.temp_data.get("km_byline"):
            raise self.error("byline: expected once on a page, got it twice")
        env.temp_data["km_byline"] = True
        options = self.options
        if (
            "interval" in options
            and len(options.get("backdrop", "").split()) < 2
        ):
            raise self.error(
                "byline: :interval: needs two or more :backdrop: pictures"
            )
        if "avatar-size" in options and not (
            "avatar" in options or setting(env.config, "project").get("avatar")
        ):
            raise self.error("byline: :avatar-size: needs an avatar")
        options.setdefault("align", "left")
        options["reading_time"] = "hide-reading-time" not in options
        options["copy_url"] = "hide-copy-url" not in options
        options["page_source"] = "hide-source" not in options
        options["language"] = "show-language" in options
        options["classes"] = options.pop("class", [])
        if "avatar-size" in options:
            options["avatar_size"] = options["avatar-size"]
        words, messages = parse(self, text, "name")
        unlinked(self, words, "a name")
        worded(self, words, "a name")
        metadata = env.metadata.setdefault(env.docname, {})
        metadata.setdefault("author", words.astext().strip() or text)
        pictures = self.options.get("backdrop", "").split()
        if pictures:
            metadata.setdefault("km-page-backdrop", pictures[0])
        element = located(self, Byline("", words, **self.options))
        named(self, element)
        return [element, *trail(self.options), *messages]


def plain(node: Byline) -> list[nodes.Node]:
    """Write a byline as words, for a builder that draws no HTML.

    :param node: The byline's node.
    :return: A paragraph with the author's name.
    """
    name = next(_ for _ in node.children if isinstance(_, phrase))
    return [nodes.paragraph("", "", *name.children)]


def visit(self: HTMLTranslator, node: Byline) -> None:
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


node = Byline
