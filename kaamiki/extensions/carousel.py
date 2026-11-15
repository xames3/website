"""\
Carousel Directive
==================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 04 November 2026
Last updated on: 15 November 2026

A `carousel` directive that lays blocks, buttons, figures, pictures,
repositories and thumbnails out in a row a reader swipes through::

    .. carousel:: What to read next
       :preheader: :fa-icon:regular:`comments` Guides
       :gap: medium
       :auto-run:
       :direction: left

       .. block:: Getting started
          :target: https://example.com/start

          A short guide to set things up.

       .. thumbnail:: https://www.youtube.com/watch?v=jNQXAC9IVRw
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
from kaamiki.extensions.utils import BEM
from kaamiki.extensions.utils import KaamikiDirective
from kaamiki.extensions.utils import Option
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import fields
from kaamiki.extensions.utils import hollow
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import phrase
from kaamiki.extensions.utils import through
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

carousel: t.Final[BEM] = BEM("carousel")
text: t.Final[BEM] = BEM("text")
template: t.Final[str] = "directives/carousel.html.jinja"
DIRECTIONS: t.Final[tuple[str, ...]] = ("right", "left")
CARDS: t.Final[int] = 2
ITEMS: t.Final[tuple[type[nodes.Node], ...]] = (
    block.Block.Node,
    button.Button,
    nodes.figure,
    nodes.image,
    repository.Repository.Node,
    thumbnail.Thumbnail.Node,
)
SKIPPED: t.Final[tuple[type[nodes.Node], ...]] = (
    nodes.comment,
    nodes.pending,
    nodes.target,
    nodes.system_message,
)


class CarouselText(phrase):
    """A line of the carousel's heading, which `visit` writes."""


html.skips(CarouselText)


def is_trail(found: nodes.Node) -> bool:
    """Say whether a node is the empty `raw` a directive leaves behind.

    The link checker reads that node.

    :param found: The node to look at.
    :return: `True` for a `raw` node with nothing in it.
    """
    return isinstance(found, nodes.raw) and not found.astext().strip()


def is_pending(found: nodes.Node) -> bool:
    """Say whether a node is a `pending` instruction.

    That's what `rst-class` leaves for the element after it.

    :param found: The node to look at.
    :return: `True` for a `pending` node.
    """
    return isinstance(found, nodes.pending)


def is_item(found: nodes.Node) -> bool:
    """Say whether a node is something a carousel holds.

    :param found: The node to look at.
    :return: `True` for a block, a button, a figure, a picture, a
        repository or a thumbnail. A picture that links counts too.
    """
    if isinstance(found, ITEMS):
        return True
    return (
        isinstance(found, nodes.reference)
        and len(found.children) == 1
        and isinstance(found.children[0], nodes.image)
    )


def few(cards: int, count: int) -> str:
    """Word the message for a carousel with fewer items than `cards`.

    :param cards: How many cards the carousel was asked to show.
    :param count: How many items it has.
    :return: The message, which names the option.
    """
    return f":cards: {cards} needs at least {cards} items, got {count}"


class Carousel(KaamikiDirective, motion=True):
    """The `carousel` directive.

    Options::

        - `preheader`: A small line above the title, as the preheader of
          a section. It can have roles, as `:fa-icon:regular:`heart`
          Love`. It needs a title.
        - `subheader`: A dimmer line below the title, as the subheader of
          a section. It needs a title.
        - `gap`: The space between items, `small`, `medium` or `large`.
          The default is `small`. A length in `rem`, up to 4rem, can
          replace them, as `1.5rem`. With two lengths, as for `columns`,
          it uses the second.
        - `cards`: How many items show fully, from 1 to 4. A quarter of
          the next item shows next to them. The default is 2. The
          carousel needs a minimum of that number of items. A phone
          always shows approximately one item and a part of the next.
        - `hide-arrows`: Remove the arrows. A reader can still swipe or
          scroll.
        - `dots`: Show a dot for each item below the row, not the
          arrows, with a pill that moves from one dot to the next. You
          cannot use it with `hide-arrows`.
        - `auto-run`: Move to the next item automatically. It stops
          while a reader hovers on it, touches it or puts the focus on
          it. It does not move for a reader whose device asks for less
          motion.
        - `interval`: The seconds between moves, from 2 to 15. The
          default is 4. It needs `auto-run`.
        - `direction`: The direction of `auto-run`, `right` or `left`.
          The default is `right`. It needs `auto-run`.
        - `speed`: The speed of its motion, relative to the site, one
          of `0.25`, `0.5`, `0.75`, `1`, `1.5`, `2`, `3` or `4`. `2` is
          two times as fast.
        - `no-motion`: Do not move it.
        - `name`: A name for links.
        - `class`: More classes for the carousel.

    The argument is the title. It is optional, and it looks like the
    title of a section. It is reStructuredText, so roles work in it and
    in `preheader` and `subheader`. The arrows are on the line of the
    title when the two fit on one line. If not, they are below the
    items. Below 768px wide, they are always below the items.

    Put a `block`, a `button`, a `figure`, an `image`, a `repository`
    or a `thumbnail` in it for each item.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    preheader = Option(checks.text)
    subheader = Option(checks.text)
    gap = Option(checks.spacing(SIZES, GAPS), default="small")
    cards = Option(checks.integer(*map(int, BOUNDS["cards"])))
    hide_arrows = Option(rst.directives.flag)
    dots = Option(rst.directives.flag)
    auto_run = Option(rst.directives.flag)
    interval = Option(
        checks.number(*BOUNDS["interval"]), needs="auto-run", default=4
    )
    direction = Option(
        checks.word(*DIRECTIONS), needs="auto-run", default="right"
    )

    class Node(nodes.container):
        """The carousel and its items."""

    def check(self) -> None:
        """Refuse lines without a title, and dots without arrows."""
        for option in ("preheader", "subheader"):
            if option in self.options and not self.arguments:
                self.fail(f":{option}: needs a title")
        if self.dots and self.hide_arrows:
            self.fail(
                ":dots: replaces the arrows, so :hide-arrows: has nothing"
                " to hide"
            )

    def build(self) -> list[nodes.Node]:
        """Make the carousel with its items and its heading.

        :return: The carousel's node and what the parser reported.
        """
        node = self.locate(self.Node("", classes=self.classes))
        node["titled"] = bool(self.arguments)
        node["gap"] = self.gap
        node["cards"] = self.cards
        node["arrows"] = not (self.hide_arrows or self.dots)
        node["dots"] = self.dots
        node["auto"] = self.auto_run
        node["interval"] = self.interval
        node["direction"] = self.direction
        self.add_name(node)
        self.state.nested_parse(self.content, self.content_offset, node)
        for shelf in list(node.findall(block.Shelf)):
            shelf.replace_self(list(shelf.children))
        found = list(through(node.children))
        if any(
            isinstance(each, nodes.system_message) and each["level"] >= 3
            for each in found
        ):
            return [node]
        for each in found:
            if not (
                isinstance(each, SKIPPED) or is_trail(each) or is_item(each)
            ):
                self.fail(
                    "expected blocks, buttons, figures, images, repositories"
                    f" and thumbnails, got {what(each)}"
                )
        if hollow(
            each
            for each in found
            if not is_trail(each) and not is_pending(each)
        ):
            self.fail("expected at least 1 item, got none")
        count = sum(map(is_item, found))
        if node["cards"] and count < node["cards"]:
            self.fail(few(node["cards"], count))
        messages: list[nodes.system_message] = []
        if self.arguments:
            pieces = [("title", self.title)]
            if self.preheader:
                pieces.insert(0, ("preheader", self.preheader))
            if self.subheader:
                pieces.append(("subheader", self.subheader))
            for place, (field, written) in enumerate(pieces):
                words, more = parse(self, written, field)
                worded(self, words, f"a {field}")
                messages += more
                node.insert(
                    place,
                    self.locate(
                        CarouselText(written, "", *words.children, field=field)
                    ),
                )
        return [node, *messages]

    @staticmethod
    def plain(node: Carousel.Node) -> list[nodes.Node]:
        """Write a carousel as words, for a builder that writes no HTML.

        :param node: The carousel's node.
        :return: A paragraph for each line of its heading, then its
            items.
        """
        heading = [
            nodes.paragraph("", "", *each.children)
            for each in node.children
            if isinstance(each, CarouselText)
        ]
        return [
            *heading,
            *(
                each
                for each in node.children
                if not isinstance(each, CarouselText)
            ),
        ]


@html.opens(Carousel.Node)
def visit(self: HTMLTranslator, node: Carousel.Node) -> None:
    """Open the carousel and the track its items scroll along.

    :param self: The HTML translator, whose body this appends to.
    :param node: The carousel's node.
    """
    modifiers = ["titled"] if node["titled"] else []
    styles: list[str] = []
    if node["gap"] in SIZES:
        if node["gap"] != "small":
            modifiers.append(f"gap-{node['gap']}")
    else:
        styles.append(f"--km-carousel-gap: {checks.lengths(node['gap'])[1]}")
    if node["cards"] not in (None, CARDS):
        modifiers.append(f"cards-{node['cards']}")
    attributes: dict[str, t.Any] = {
        "CLASS": carousel(*modifiers),
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
        for field in ("preheader", "title", "subheader"):
            if field in lines:
                label = f' id="{ident}"' if field == "title" else ""
                more = [text["preheader"]] if field == "preheader" else []
                classes = getattr(carousel, field)(more=more)
                self.body.append(
                    f'<p class="{classes}"{label}>{lines[field]}</p>'
                )
    self.body.append(f'<div class="{carousel.track()}">')


@html.closes(Carousel.Node)
def depart(self: HTMLTranslator, node: Carousel.Node) -> None:
    """Close the track, write the arrows or the dots and close the carousel.

    :param self: The HTML translator, whose body this appends to.
    :param node: The carousel's node.
    """
    self.body.append("</div>")
    if node["arrows"]:
        self.body.append(render(template))
    if node["dots"]:
        self.body.append(f'<div class="{carousel.dots()}" aria-hidden="true">')
        self.body.append("</div>")
    self.body.append("</div>")


def emptied(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Stop the build for a carousel with too few items left to show.

    A carousel whose items are all in an `only` for another builder
    passes the directive's checks and has nothing in it once the page is
    resolved. One that has some of them there can fall short of its
    `cards` the same way.

    :param app: The Sphinx application instance.
    :param doctree: The page, about to be written.
    :param docname: The page's name (unused).
    :raises KaamikiError: For the first carousel without an item or
        with fewer than its `cards`.
    """
    del docname
    if app.builder.format != "html":
        return
    for found in doctree.findall(Carousel.Node):
        count = sum(map(is_item, through(found.children)))
        if not count:
            fail(
                "carousel: expected at least 1 item, got none", location(found)
            )
        if found["cards"] and count < found["cards"]:
            fail(f"carousel: {few(found['cards'], count)}", location(found))


def register(app: Sphinx) -> None:
    """Register the check on each carousel.

    :param app: The Sphinx application instance.
    """
    app.connect("doctree-resolved", emptied)
