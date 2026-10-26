"""\
Author Directive
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February 2025
Last updated on: 25 October 2026

An `author` directive that renders the byline under a page title::

    .. author:: Akshay Mestry
       :avatar: https://example.com/avatar.png
       :url: https://github.com/xames3
       :avatar-size: 24
"""

import os.path as p
import re
import typing as t
from urllib.parse import urlsplit

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import fields
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import opens_new_tab
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import reading_time
from kaamiki.extensions.utils import render
from kaamiki.extensions.utils import rooted
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils.settings import ALIGNMENTS
from kaamiki.extensions.utils.settings import BOUNDS

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "author"
template: t.Final[str] = "directives/author.html.jinja"
BACKGROUNDS: t.Final[int] = 8
KINDS: t.Final[dict[str, str]] = {".rst": "rst", ".md": "md"}
IMAGES: t.Final[re.Pattern[str]] = re.compile(
    r".+\.(?:jpe?g|png|webp|avif|gif|svg)", re.IGNORECASE
)


def backdrops(argument: str | None) -> str:
    """Check the pictures to fade through, one address each.

    :param argument: The addresses as written, spaces or new lines
        between them.
    :return: The addresses, a space between each.
    :raises ValueError: For one that isn't an address, one twice or
        more than `BACKGROUNDS`.
    """
    found = (argument or "").split()
    if not found or len(found) > BACKGROUNDS:
        raise ValueError(f"expected one to {BACKGROUNDS} addresses")
    for each in found:
        checks.link(each, schemes=("http", "https"))
        if not IMAGES.fullmatch(urlsplit(each).path):
            raise ValueError(
                f"expected a .jpg, .png, .webp, .avif, .gif or .svg "
                f"picture, got {each!r}"
            )
    if len(set(found)) != len(found):
        raise ValueError("expected addresses that are all different")
    return " ".join(found)


def source_url(self: HTMLTranslator) -> tuple[str, str]:
    """Link the page's plain-text source, the one Sphinx copies.

    :param self: The HTML translator, writing the page.
    :return: The address and what the source is, `rst` or `md`, or
        `""` for another kind. Both are empty strings with
        `html_copy_source` off.
    """
    builder = self.builder
    config = builder.config
    if not config.html_copy_source:
        return "", ""
    name = str(builder.env.doc2path(builder.current_docname, base=False))
    suffix = p.splitext(name)[1]
    if suffix != config.html_sourcelink_suffix:
        name += config.html_sourcelink_suffix
    url = rooted(self, f"_sources/{name.replace(p.sep, '/')}")
    return url, KINDS.get(suffix, "")


class node(nodes.Element):
    """The parsed directive, waiting for `visit` to write it out."""


class directive(rst.Directive):
    """The `author` directive.

    Options::

        - `avatar`: URL of the author's picture.
        - `url`: Where the name links to, a profile or a mailto.
        - `background`: One or more image URLs to fade through behind
          the title.
        - `avatar-size`: The picture's width and height in pixels, from
          16 to 64. Defaults to 20.
        - `interval`: Seconds each background stays, from 3 to 15. It
          needs two or more `background` pictures. Defaults to 7.
        - `align`: Where the byline sits, `left`, `center` or `right`.
          Defaults to `center`.
        - `hide-reading-time`: Hides the reading time, which is shown
          without it.
        - `hide-copy-url`: Hides the copy button, which is shown
          without it.
        - `hide-source`: Hides the link to the page's plain-text
          source, which is shown without it while `html_copy_source`
          is on.
        - `name`: A name to link to.
        - `class`: More classes for the byline.
    """

    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "avatar": checks.link,
        "url": checks.link,
        "background": backdrops,
        "avatar-size": checks.integer(*map(int, BOUNDS["avatar_size"])),
        "interval": checks.number(*BOUNDS["interval"]),
        "align": checks.word(*ALIGNMENTS),
        "hide-reading-time": rst.directives.flag,
        "hide-copy-url": rst.directives.flag,
        "hide-source": rst.directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        """Collect the options and return the node.

        Only what the page writes goes on the node, `visit` fills in
        the rest from `project`. The name also becomes the page's
        author, unless its `.. Author:` comment named one first, and
        the first background, when written, becomes a fallback for its
        social image.

        :return: The node, followed by the `raw` nodes `trail` returns
            for the link checker and anything the name reported.
        """
        text = self.arguments.pop().strip()
        env = self.state.document.settings.env
        if env.temp_data.get("km_author"):
            raise self.error("author: expected once on a page")
        env.temp_data["km_author"] = True
        options = self.options
        if (
            "interval" in options
            and len(options.get("background", "").split()) < 2
        ):
            raise self.error(
                "author: :interval: requires two or more :background: pictures"
            )
        if "avatar-size" in options and not (
            "avatar" in options or setting(env.config, "project").get("avatar")
        ):
            raise self.error("author: :avatar-size: requires an avatar")
        options.setdefault("align", "center")
        options["reading_time"] = "hide-reading-time" not in options
        options["copy_url"] = "hide-copy-url" not in options
        options["page_source"] = "hide-source" not in options
        options["classes"] = options.pop("class", [])
        if "avatar-size" in options:
            options["avatar_size"] = options["avatar-size"]
        metadata = env.metadata.setdefault(env.docname, {})
        metadata.setdefault("author", text)
        pictures = self.options.get("background", "").split()
        if pictures:
            metadata.setdefault("km-pg-background", pictures[0])
        words, messages = parse(self, text, "name")
        element = node("", words, **self.options)
        named(self, element)
        return [element, *trail(self.options), *messages]


def visit(self: HTMLTranslator, node: node) -> None:
    """Write the widget out when the HTML writer reaches the node.

    :param self: The HTML translator, whose body this appends to.
    :param node: The `author` node, its attributes and its name.
    :raises nodes.SkipNode: Always, since the name is written already.
    """
    config = self.builder.config
    context = config.html_context
    attributes = dict(node.attributes)
    attributes.update(fields(self, node))
    attributes["project"] = context["km_project"]
    url = attributes.get("url") or attributes["project"]["source"]
    attributes["new_tab"] = opens_new_tab(url, config)
    attributes["fa_icons"] = context["km_fa_icons"]
    attributes["minutes"] = max(1, reading_time(node.document, config))
    attributes["page_source"], attributes["source_kind"] = (
        source_url(self) if attributes["page_source"] else ("", "")
    )
    avatar = attributes.get("avatar") or attributes["project"]["avatar"]
    attributes["avatar"] = rooted(self, avatar)
    background = attributes.get("background", "").split()
    pictures = [rooted(self, _) for _ in background]
    attributes["data"] = {"data-km-background": " ".join(pictures) or None}
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
    context["km_author"] = (
        meta.get("author") or project.get("author") or app.config.author
    )
