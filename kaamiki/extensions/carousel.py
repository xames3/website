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
from kaamiki.extensions.utils import MOTION
from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import fields
from kaamiki.extensions.utils import hollow
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import located
from kaamiki.extensions.utils import moving
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import phrase
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
carousel: t.Final[BEM] = BEM("carousel")
text: t.Final[BEM] = BEM("text")
template: t.Final[str] = "directives/carousel.html.jinja"
DIRECTIONS: t.Final[tuple[str, ...]] = ("right", "left")
CARDS: t.Final[int] = 2
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
    """The carousel and what's in it, waiting for `visit`."""


class carouseltext(phrase):
    """A line of the carousel's heading, waiting for `visit`."""


html.skips(carouseltext)


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
    return (
        f"carousel: :cards: {cards} needs at least {cards} items, got {count}"
    )


class directive(rst.Directive):
    """The `carousel` directive.

    Options::

        - `preheader`: A small line above the title, set the way a
          section's preheader text is, with roles like
          `:fa-icon:regular:`heart` Love`. It needs a title.
        - `subheader`: A dimmer line under the title, set the way a
          section's is. It needs a title.
        - `gap`: The space between items, `small`, `medium` or
          `large`. Defaults to `small`. A length in `rem` replaces
          them, up to 4rem, like `1.5rem`. Two lengths, as `columns`
          takes, use the second.
        - `cards`: How many items show in full, from 1 to 4, with a
          quarter of the next one beside them. Defaults to 2. It needs
          at least that many items. A phone shows about one and a bit
          whatever it says.
        - `hide-arrows`: Leave out the arrows. A reader still swipes or
          scrolls.
        - `dots`: Put a dot for each item under the row in place of the
          arrows, with a pill that stretches from one dot to the next.
          It can't go with `hide-arrows`.
        - `auto-run`: Move on by itself, pausing while a reader hovers,
          touches or focuses it. It stays still for a reader who asks
          their device for less motion.
        - `interval`: Seconds between moves, from 2 to 15. Defaults to
          4. It needs `auto-run`.
        - `direction`: Which way `auto-run` moves, `right` or `left`.
          Defaults to `right`. It needs `auto-run`.
        - `speed`: How quick its motion is next to the site's, one
          of `0.25`, `0.5`, `0.75`, `1`, `1.5`, `2`, `3` or `4`.
          `2` is twice as quick.
        - `no-motion`: Keep it still.
        - `name`: A name to link to.
        - `class`: More classes for the carousel.

    The argument is the title, which is optional and is set the way a
    section's is. It's read as reStructuredText, so roles work in it,
    and so they do in `preheader` and `subheader`. The arrows sit on the
    title's line when it and they fit on one and below the items when
    they don't, and always below under 768px wide.

    A `block`, a `button`, a `figure`, an `image`, a `repository` and a
    `thumbnail` go inside, an item each.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {  # noqa: RUF012
        **NATIVE,
        **MOTION,
        "preheader": checks.text,
        "subheader": checks.text,
        "gap": checks.spacing(SIZES, GAPS),
        "cards": checks.integer(*map(int, BOUNDS["cards"])),
        "hide-arrows": rst.directives.flag,
        "dots": rst.directives.flag,
        "auto-run": rst.directives.flag,
        "interval": checks.number(*BOUNDS["interval"]),
        "direction": checks.word(*DIRECTIONS),
    }

    def run(self) -> list[nodes.Node]:
        """Parse the items and return the carousel.

        :return: The carousel's node.
        """
        options = self.options
        for option in ("preheader", "subheader"):
            if option in options and not self.arguments:
                raise self.error(f"carousel: :{option}: needs a title")
        if "dots" in options and "hide-arrows" in options:
            raise self.error(
                "carousel: :dots: replaces the arrows, so :hide-arrows: has"
                " nothing to hide"
            )
        if "auto-run" not in options:
            for option in ("interval", "direction"):
                if option in options:
                    raise self.error(f"carousel: :{option}: needs :auto-run:")
        element = located(
            self,
            Carousel("", classes=[*options.get("class", []), *moving(options)]),
        )
        element["titled"] = bool(self.arguments)
        element["gap"] = options.get("gap", "small")
        element["cards"] = options.get("cards")
        element["arrows"] = not ({"hide-arrows", "dots"} & set(options))
        element["dots"] = "dots" in options
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
        count = sum(map(is_item, found))
        if element["cards"] and count < element["cards"]:
            raise self.error(few(element["cards"], count))
        messages: list[nodes.system_message] = []
        if self.arguments:
            pieces: list[tuple[str, str]] = [
                ("title", titled(self, self.arguments[0]))
            ]
            if "preheader" in options:
                pieces.insert(0, ("preheader", options["preheader"]))
            if "subheader" in options:
                pieces.append(("subheader", options["subheader"]))
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


@html.opens(Carousel)
def visit(self: HTMLTranslator, node: Carousel) -> None:
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


@html.closes(Carousel)
def depart(self: HTMLTranslator, node: Carousel) -> None:
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
    for found in doctree.findall(Carousel):
        count = sum(map(is_item, through(found.children)))
        if not count:
            fail(
                "carousel: expected at least 1 item, got none", location(found)
            )
        if found["cards"] and count < found["cards"]:
            fail(few(found["cards"], count), location(found))


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
    """Register the check on each carousel.

    :param app: The Sphinx application instance.
    """
    app.connect("doctree-resolved", emptied)


node = Carousel
