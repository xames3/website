"""\
Carousel Directive
==================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 04 November 2026
Last updated on: 07 November 2026

A `carousel` directive that lays blocks, pictures, repositories,
thumbnails and buttons out in a row a reader swipes through::

    .. carousel:: What to do next.
       :header: :fa-icon:regular:`comments` Keep it stupid simple
       :gap: medium
       :auto-run:
       :direction: left

       .. thumbnail:: https://www.youtube.com/watch?v=dQw4w9WgXcQ

       .. thumbnail:: https://www.youtube.com/watch?v=9bZkp7q19f0
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst
from sphinx.locale import _

from kaamiki.extensions import block
from kaamiki.extensions import button
from kaamiki.extensions import repository
from kaamiki.extensions import thumbnail
from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import fields
from kaamiki.extensions.utils import hollow
from kaamiki.extensions.utils import located
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import phrase
from kaamiki.extensions.utils import skip
from kaamiki.extensions.utils import through
from kaamiki.extensions.utils import titled
from kaamiki.extensions.utils import what
from kaamiki.extensions.utils import worded
from kaamiki.extensions.utils.checks import fail
from kaamiki.extensions.utils.checks import location
from kaamiki.extensions.utils.settings import BOUNDS
from kaamiki.extensions.utils.settings import GAPS
from kaamiki.extensions.utils.settings import SIZES
from kaamiki.extensions.utils.templates import render

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "carousel"
template: t.Final[str] = "directives/carousel.html.jinja"
DIRECTIONS: t.Final[tuple[str, ...]] = ("right", "left")
ITEMS: t.Final[tuple[type[nodes.Node], ...]] = (
    block.Block,
    button.Button,
    nodes.figure,
    nodes.image,
    repository.Repository,
    thumbnail.Thumbnail,
)
SKIPPED: t.Final[tuple[type[nodes.Node], ...]] = (
    nodes.comment,
    nodes.pending,
    nodes.target,
    nodes.system_message,
)


class Carousel(nodes.container):
    """The carousel and what is in it, waiting for `visit`."""


class carouseltext(phrase):
    """A line of the carousel's heading, parsed and waiting for
    `visit`.
    """


def is_trail(found: nodes.Node) -> bool:
    """Say whether a node is the empty `raw` a directive leaves for the
    link checker.

    :param found: The node to look at.
    :return: `True` for a `raw` node with nothing in it.
    """
    return isinstance(found, nodes.raw) and not found.astext().strip()


def is_pending(found: nodes.Node) -> bool:
    """Say whether a node is a `pending` instruction, which is what
    `rst-class` leaves for the element after it.

    :param found: The node to look at.
    :return: `True` for a `pending` node.
    """
    return isinstance(found, nodes.pending)


def is_item(found: nodes.Node) -> bool:
    """Say whether a node is something a carousel holds.

    :param found: The node to look at.
    :return: `True` for a block, a button, a figure, a picture, a
        repository or a thumbnail, and for a picture that links.
    """
    if isinstance(found, ITEMS):
        return True
    return (
        isinstance(found, nodes.reference)
        and len(found.children) == 1
        and isinstance(found.children[0], nodes.image)
    )


class directive(rst.Directive):
    """The `carousel` directive.

    Options::

        - `header`: A small line above the title, set the way a
          section's pre-section text is, with roles like
          `:fa-icon:regular:`heart` Love`. It needs a title.
        - `subsection`: A dimmer line under the title, set the way a
          section's is. It needs a title.
        - `gap`: The space between items. `small`, the default,
          `medium` or `large`, or a length in `rem` that replaces them,
          up to 4rem, like `1.5rem`. Two lengths, as `columns` takes,
          use the second.
        - `hide-arrows`: Leave out the arrows. A reader still swipes or
          scrolls.
        - `auto-run`: Move on by itself, pausing while a reader hovers,
          touches or focuses it. It stays still for a reader who asks
          their device for less motion.
        - `interval`: Seconds between moves, from 2 to 15. Defaults to
          4. It needs `auto-run`.
        - `direction`: Which way `auto-run` moves, `right`, the
          default or `left`. It needs `auto-run`.
        - `name`: A name to link to.
        - `class`: More classes for the carousel.

    The argument is the title, which is optional and is set the way a
    section's is. It is read as reStructuredText, so roles work in it,
    and so they do in `header` and `subsection`. The arrows sit on the
    title's line when it and they fit on one and below the items when
    they don't, and always below on a phone.

    A `block`, a `button`, a `figure`, an `image`, a `repository` and a
    `thumbnail` go inside, an item each.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "header": checks.text,
        "subsection": checks.text,
        "gap": checks.spacing(SIZES, GAPS),
        "hide-arrows": rst.directives.flag,
        "auto-run": rst.directives.flag,
        "interval": checks.number(*BOUNDS["interval"]),
        "direction": checks.word(*DIRECTIONS),
    }

    def run(self) -> list[nodes.Node]:
        """Parse the items and return the carousel.

        :return: The carousel's node.
        """
        options = self.options
        for option in ("header", "subsection"):
            if option in options and not self.arguments:
                raise self.error(f"carousel: :{option}: needs a title")
        if "auto-run" not in options:
            for option in ("interval", "direction"):
                if option in options:
                    raise self.error(f"carousel: :{option}: needs :auto-run:")
        element = located(
            self, Carousel("", classes=list(options.get("class", [])))
        )
        element["titled"] = bool(self.arguments)
        element["gap"] = options.get("gap", "small")
        element["arrows"] = "hide-arrows" not in options
        element["auto"] = "auto-run" in options
        element["interval"] = options.get("interval", 4)
        element["direction"] = options.get("direction", "right")
        named(self, element)
        self.state.nested_parse(self.content, self.content_offset, element)
        for row in list(element.findall(block.shelf)):
            row.replace_self(list(row.children))
        found = list(through(element.children))
        if any(
            isinstance(_, nodes.system_message) and _["level"] >= 3
            for _ in found
        ):
            return [element]
        for each in found:
            if not (
                isinstance(each, SKIPPED) or is_trail(each) or is_item(each)
            ):
                raise self.error(
                    "carousel: expected blocks, buttons, figures, images,"
                    f" repositories and thumbnails, got {what(each)}"
                )
        if hollow(_ for _ in found if not is_trail(_) and not is_pending(_)):
            raise self.error("carousel: expected at least 1 item, got none")
        messages: list[nodes.system_message] = []
        if self.arguments:
            pieces: list[tuple[str, str]] = [
                ("title", titled(self, self.arguments[0]))
            ]
            if "header" in options:
                pieces.insert(0, ("header", options["header"]))
            if "subsection" in options:
                pieces.append(("subsection", options["subsection"]))
            for place, (field, text) in enumerate(pieces):
                words, found_messages = parse(self, text, field)
                worded(self, words, f"a {field}")
                messages += found_messages
                element.insert(
                    place,
                    located(
                        self,
                        carouseltext(text, "", *words.children, field=field),
                    ),
                )
        return [element, *messages]


def visit(self: HTMLTranslator, node: Carousel) -> None:
    """Open the carousel and the track its items scroll along.

    :param self: The HTML translator, whose body this appends to.
    :param node: The carousel's node.
    """
    classes = ["km-carousel"]
    if node["titled"]:
        classes.append("km-carousel--titled")
    styles: list[str] = []
    if node["gap"] in SIZES:
        if node["gap"] != "small":
            classes.append(f"km-carousel--gap-{node['gap']}")
    else:
        styles.append(f"--km-carousel-gap: {checks.lengths(node['gap'])[1]}")
    attributes: dict[str, t.Any] = {
        "CLASS": " ".join(classes),
        "role": "group",
        "aria-roledescription": "carousel",
        "data-km-carousel": "",
    }
    if styles:
        attributes["style"] = "; ".join(styles)
    if node["titled"]:
        serial = self.__dict__.get("km_carousel_titles", 0)
        self.__dict__["km_carousel_titles"] = serial + 1
        ident = f"km-carousel-title-{serial}"
        attributes["aria-labelledby"] = ident
    else:
        attributes["aria-label"] = _("Carousel")
    if node["auto"]:
        attributes["data-km-carousel-interval"] = f"{node['interval']:g}"
        attributes["data-km-carousel-direction"] = node["direction"]
    self.body.append(self.starttag(node, "div", "", **attributes))
    if node["titled"]:
        lines = fields(self, node)
        for field in ("header", "title", "subsection"):
            if field in lines:
                label = f' id="{ident}"' if field == "title" else ""
                more = " km-text--pre-section" if field == "header" else ""
                self.body.append(
                    f'<p class="km-carousel__{field}{more}"{label}>'
                    f"{lines[field]}</p>"
                )
    self.body.append('<div class="km-carousel__track">')


def depart(self: HTMLTranslator, node: Carousel) -> None:
    """Close the track, write the arrows and close the carousel.

    :param self: The HTML translator, whose body this appends to.
    :param node: The carousel's node.
    """
    self.body.append("</div>")
    if node["arrows"]:
        self.body.append(render(template))
    self.body.append("</div>")


def emptied(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Stop the build for a carousel with nothing left to show.

    A carousel whose items are all in an `only` for another builder
    passes the directive's check and has nothing in it once the page is
    resolved.

    :param app: The Sphinx application instance.
    :param doctree: The page, about to be written.
    :param docname: The page's name (unused).
    :raises KaamikiError: For the first carousel without an item.
    """
    del docname
    if app.builder.format != "html":
        return
    for found in doctree.findall(Carousel):
        if not any(is_item(_) for _ in through(found.children)):
            fail(
                "carousel: expected at least 1 item, got none", location(found)
            )


def plain(node: Carousel) -> list[nodes.Node]:
    """Write a carousel as words, for a builder that draws no HTML.

    :param node: The carousel's node.
    :return: A paragraph for each line of its heading, if it has one,
        then its items.
    """
    words = [
        nodes.paragraph("", "", *_.children)
        for _ in node.children
        if isinstance(_, carouseltext)
    ]
    return [
        *words,
        *(_ for _ in node.children if not isinstance(_, carouseltext)),
    ]


def register(app: Sphinx) -> None:
    """Register the heading's node and check each carousel again once its
    page is resolved.

    :param app: The Sphinx application instance.
    """
    app.add_node(carouseltext, html=(skip, None))
    app.connect("doctree-resolved", emptied)


node = Carousel
