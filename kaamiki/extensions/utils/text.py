"""\
Text Utilities
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 18 November 2026

The helpers that flatten, tidy and shorten text, give a level to the
captions of a table of contents and write the groups of the header
navigation.
"""

import dataclasses
import re
import typing as t
from html import unescape
from html.parser import HTMLParser

CAPTION: t.Final[re.Pattern[str]] = re.compile(
    r'(<p class="caption") role="heading">'
)
TAG_RE: t.Final[re.Pattern[str]] = re.compile(r"</?[A-Za-z][^<>]*>")
CLASS: t.Final[re.Pattern[str]] = re.compile(r'class="([^"]*)"')


def tidy(text: str) -> str:
    """Make each run of whitespace in plain text one space.

    :param text: The text.
    :return: The text with each run of whitespace as one space.
    """
    return " ".join(text.split())


def plain(text: str) -> str:
    """Change rendered HTML to plain text.

    :param text: The HTML.
    :return: Its text, tidied.
    """
    return tidy(unescape(TAG_RE.sub("", text)))


def clip(text: str, limit: int) -> str:
    """Cut a line to a length, with `...` at the end.

    :param text: The line.
    :param limit: The maximum number of characters, with `...`.
    :return: The line. A longer line is cut at the last space that
        fits, or in a word when the first word is too long.
    :raises ValueError: For a limit less than 4.
    """
    if limit < 4:
        raise ValueError(f"expected a limit of 4 or more, got {limit}")
    if len(text) <= limit:
        return text
    room = limit - 3
    cut = text[:room]
    if text[room : room + 1] != " ":
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(",;:.") + "..."


def levelled(fragment: str) -> str:
    """Give each caption in a table of contents a heading level.

    :param fragment: The table of contents as HTML.
    :return: The table of contents with each caption at level 2. Sphinx
        writes a caption as `role="heading"` without a level, and a
        screen reader needs the level.
    """
    return CAPTION.sub(r'\1 role="heading" aria-level="2">', fragment)


def classed(tag: str, name: str) -> str:
    """Add a class to a start tag.

    :param tag: The start tag as HTML.
    :param name: The class to add.
    :return: The start tag with the class.
    """
    if CLASS.search(tag):
        return CLASS.sub(rf'class="\1 {name}"', tag, count=1)
    return f'{tag[:-1]} class="{name}">'


def given(tag: str, **attributes: str) -> str:
    """Add attributes to a start tag.

    :param tag: The start tag as HTML.
    :param attributes: The attributes, with `_` for `-` in names.
    :return: The start tag with the attributes.
    """
    added = "".join(
        f' {name.replace("_", "-")}="{value}"'
        for name, value in attributes.items()
    )
    return f"{tag[:-1]}{added}>"


@dataclasses.dataclass
class Opened:
    """A list of the header navigation that is open in the parser.

    :param at: The place of its start tag in the output.
    :param kind: `group` below a caption, `links` for the top links,
        `item` below a top link, or empty.
    :param name: The id of a dropdown.
    :param items: The number of its items.
    """

    at: int
    kind: str = ""
    name: str = ""
    items: int = 0


class HeaderNav(HTMLParser):
    """The header navigation, as the header shows it."""

    def __init__(self, fragment: str, arrow: str, rows: int) -> None:
        """Write the groups and the dropdowns of the navigation.

        :param fragment: The table of contents as HTML, with levels.
        :param arrow: The arrow of a dropdown as HTML.
        :param rows: The most rows of a dropdown.
        """
        super().__init__(convert_charrefs=False)
        self.arrow = arrow
        self.rows = rows
        self.out: list[str] = []
        self.lists: list[Opened] = []
        self.dropdowns = 0
        self.caption = ""
        self.button = False
        self.link: list[int] = []
        self.feed(fragment)
        self.close()

    @property
    def html(self) -> str:
        """The navigation as HTML."""
        return "".join(self.out)

    def number(self) -> str:
        """Number the next dropdown.

        :return: Its id.
        """
        self.dropdowns += 1
        return f"km-nav-group-{self.dropdowns}"

    @property
    def top(self) -> bool:
        """Whether the parser is in an item of the top links."""
        return len(self.lists) == 1 and self.lists[0].kind == "links"

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        """Copy a start tag, as a dropdown needs it.

        :param tag: The name of the tag.
        :param attrs: Its attributes.
        """
        raw = self.get_starttag_text() or ""
        names = (dict(attrs).get("class") or "").split()
        if tag == "p" and "caption" in names and not self.lists:
            self.caption = self.number()
            self.button = True
            raw = (
                '<div class="km-header__nav-group">'
                '<button type="button" class="caption"'
                f' aria-controls="{self.caption}" aria-expanded="false">'
            )
        elif tag == "ul":
            raw = self.open(raw)
        elif tag == "li" and self.lists:
            self.lists[-1].items += 1
            if self.top:
                self.link = [len(self.out)]
        elif tag == "a" and self.top and len(self.link) == 1:
            self.link.append(len(self.out))
        self.out.append(raw)

    def handle_endtag(self, tag: str) -> None:
        """Copy an end tag, as a dropdown needs it.

        :param tag: The name of the tag.
        """
        raw = f"</{tag}>"
        if tag == "span" and self.button:
            raw = self.arrow + raw
        elif tag == "p" and self.button:
            self.button = False
            raw = "</button>"
        elif tag == "a" and self.top and len(self.link) == 2:
            self.link.append(len(self.out))
        elif tag == "ul":
            raw = self.shut()
        self.out.append(raw)

    def open(self, raw: str) -> str:
        """Open a list and mark it as the header uses it.

        :param raw: The start tag of the list.
        :return: The start tag, with the top links marked.
        """
        opened = Opened(len(self.out))
        if not self.lists and self.caption:
            opened.kind, opened.name = "group", self.caption
            self.caption = ""
        elif not self.lists:
            opened.kind = "links"
            raw = classed(raw, "km-header__nav-links")
        elif self.top and len(self.link) == 3:
            opened.kind, opened.name = "item", self.number()
            item, link, end = self.link
            self.out[item] = classed(self.out[item], "km-header__nav-group")
            self.out[link] = given(
                self.out[link],
                aria_controls=opened.name,
                aria_expanded="false",
            )
            self.out[end] = self.arrow + self.out[end]
        self.lists.append(opened)
        return raw

    def shut(self) -> str:
        """Close a list and size it if it's a dropdown.

        :return: The end tag, and the end of a group.
        """
        opened = self.lists.pop()
        if not opened.kind or opened.kind == "links":
            return "</ul>"
        rows = max(1, min(self.rows, opened.items))
        columns = max(1, -(-opened.items // self.rows))
        self.out[opened.at] = given(
            self.out[opened.at],
            id=opened.name,
            style=(
                f"--km-dropdown-rows: {rows};"
                f" --km-dropdown-columns: {columns};"
            ),
        )
        return "</ul></div>" if opened.kind == "group" else "</ul>"

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        """Copy an empty tag.

        :param tag: The name of the tag.
        :param attrs: Its attributes.
        """
        del tag, attrs
        self.out.append(self.get_starttag_text() or "")

    def handle_data(self, data: str) -> None:
        """Copy text.

        :param data: The text.
        """
        self.out.append(data)

    def handle_entityref(self, name: str) -> None:
        """Copy a named character.

        :param name: The name.
        """
        self.out.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        """Copy a numbered character.

        :param name: The number.
        """
        self.out.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        """Copy a comment.

        :param data: The text of the comment.
        """
        self.out.append(f"<!--{data}-->")
