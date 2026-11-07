"""\
Doctree Utilities
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 07 November 2026

The helpers that walk a doctree and pick prose out of it.
"""

from __future__ import annotations

import re
import typing as t
from uuid import uuid4

from docutils import nodes
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound
from sphinx import addnodes
from sphinx.builders.gettext import MessageCatalogBuilder

from kaamiki.extensions.utils.icons import FILE_ICON
from kaamiki.extensions.utils.icons import KEY_ICONS
from kaamiki.extensions.utils.icons import Icons
from kaamiki.extensions.utils.text import clip
from kaamiki.extensions.utils.text import tidy

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from sphinx.application import Sphinx


class annotated(nodes.container):
    """A snippet with notes beside it, the base of `code-explain`."""


class alternatives(nodes.container):
    """Panels a reader sees one at a time, the base of `tabs`."""


class glyph(nodes.inline):
    """A Font Awesome icon, an empty span the stylesheet draws into."""


KEYS: t.Final[dict[str, str]] = {
    "cmd": "cmd",
    "command": "cmd",
    "shift": "shift",
    "control": "control",
    "option": "option",
    "tab": "tab",
    "esc": "esc",
    "caps lock": "caps",
    "enter": "enter",
    "return": "enter",
    "backspace": "backspace",
    "delete": "delete",
    "left": "left",
    "right": "right",
    "up": "up",
    "down": "down",
    "fn": "globe",
    "globe": "globe",
    "super": "super",
}
PC_KEYS: t.Final[frozenset[str]] = frozenset(
    {
        "shift",
        "caps",
        "tab",
        "esc",
        "enter",
        "backspace",
        "delete",
        "globe",
    }
)
ARROWS: t.Final[frozenset[str]] = frozenset({"left", "right", "up", "down"})
WORD: t.Final[re.Pattern[str]] = re.compile(r"\w")
SEPARATORS: t.Final[frozenset[str]] = frozenset({"-", "+", "^"})
SYSTEM_KEYS: t.Final[frozenset[str]] = frozenset(
    {"km-key--windows", "km-key--linux"}
)


PAGE: t.Final[tuple[type, ...]] = (
    nodes.document,
    nodes.section,
    addnodes.only,
)
TRANSLATED: t.Final[frozenset[str]] = frozenset(
    {
        "km-feedback-button",
        "km-feedback-description",
        "km-feedback-title",
        "km-page-description",
        "km-header-subtitle",
        "km-page-image-alt",
        "km-page-title",
        "km-related-header",
    }
)


def findall[T: nodes.Element](
    node: nodes.Node,
    element: type[T],
) -> Iterator[T]:
    """Walk a doctree for every node of one type.

    :param node: Where to start looking.
    :param element: The node type to look for.
    :return: Every match, in document order.
    """
    return t.cast("Iterator[T]", node.findall(element))


def caption_icon(
    caption: nodes.Element,
    language: str | None,
    *,
    icons: Icons,
) -> str:
    """Pick the icon a code block's caption wears.

    The language has the first say. A language with no icon of its own,
    like a diff's, hands over to the caption's file name and a name no
    icon knows gets a plain file.

    :param caption: The caption.
    :param language: The language of the code under it.
    :param icons: The icons the site draws.
    :return: The icon's classes or an empty string when the caption
        opens with an icon of its own.
    """
    first = caption.children[0] if caption.children else None
    if isinstance(first, glyph):
        return ""
    if icon := icons.language(language):
        return icon
    try:
        lexer = get_lexer_for_filename(caption.astext().strip())
    except ClassNotFound:
        return icons.pair(FILE_ICON)
    for alias in lexer.aliases:
        if icon := icons.language(alias):
            return icon
    return icons.pair(FILE_ICON)


def buried(paragraph: nodes.Element) -> bool:
    """Say whether a paragraph sits anywhere but directly in a section.

    Lifted out of a note, a table, a fold, a tab, a card, a footnote or
    a quote, a line reads as a non-sequitur, and a page's description
    shouldn't come from one a reader can't see when the page opens.

    :param paragraph: The paragraph to place.
    :return: `True` when something other than a section, an `only` or
        the page itself is above it.
    """
    parent: nodes.Element | None = paragraph.parent
    while parent is not None:
        if not isinstance(parent, PAGE):
            return True
        parent = parent.parent
    return False


def standfirst(doctree: nodes.document | None, limit: int) -> str:
    """Pull the page's lead, the line right under the title.

    :param doctree: The resolved doctree or `None` for generated
        pages.
    :param limit: Longest the result may be.
    :return: The lead or an empty string when the page hasn't got
        one.
    """
    if doctree is None:
        return ""
    for paragraph in findall(doctree, nodes.paragraph):
        if "km-text--lead" not in (paragraph.get("classes") or []):
            continue
        if buried(paragraph):
            continue
        text = tidy(paragraph.astext())
        if text:
            return clip(text, limit)
    return ""


def summarise(doctree: nodes.document | None, limit: int) -> str:
    """Fall back to a page's first usable paragraph.

    :param doctree: The resolved doctree or `None` for generated
        pages.
    :param limit: Longest the result may be.
    :return: A single-line summary or an empty string when the page
        has no usable prose.
    """
    if doctree is None:
        return ""
    for paragraph in findall(doctree, nodes.paragraph):
        if buried(paragraph):
            continue
        text = tidy(paragraph.astext())
        if len(text) >= 40:
            return clip(text, limit)
    return ""


def offer(app: Sphinx, doctree: nodes.document) -> None:
    """Hand the words in a page's own fields to `gettext`.

    Sphinx lifts these fields out of the page before `gettext` sees
    them, so a copy of each is left in a container only a `gettext`
    build gets. This runs ahead of Sphinx's metadata collector.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read.
    """
    if not isinstance(app.builder, MessageCatalogBuilder):
        return
    info = next(findall(doctree, nodes.docinfo), None)
    if info is None:
        return
    box = nodes.container()
    for field in findall(info, nodes.field):
        if field[0].astext() not in TRANSLATED:
            continue
        for paragraph in findall(field[1], nodes.paragraph):
            copy = paragraph.deepcopy()
            copy.uid = uuid4().hex  # type: ignore[attr-defined]
            box += copy
    if len(box):
        doctree += box


def is_key(node: nodes.Node) -> t.TypeGuard[nodes.literal]:
    """Say whether a node is a key, a `kbd` literal.

    :param node: The node to look at.
    :return: `True` when it's a key.
    """
    return isinstance(node, nodes.literal) and "kbd" in node["classes"]


def dress(key: nodes.literal, *, icons: Icons) -> None:
    """Give a key the classes and the icon that draw it.

    The arrows, the globe and, written for Windows or Linux, Super wear
    a Font Awesome icon. A Mac has no Super key, so there it stays a
    word, as it does in a plain `kbd`.

    The `kbd:windows` and `kbd:linux` roles mark their keys with
    `SYSTEM_KEYS`, which this reads and takes off again, since nothing
    in the stylesheet or the scripts does.

    :param key: The key.
    :param icons: The icons the site draws.
    """
    classes = key["classes"]
    pc = bool(SYSTEM_KEYS & set(classes))
    text = tidy(key.astext().lower())
    name = KEYS.get(text)
    icon = ""
    if text in ("space", "space bar"):
        classes.extend(["km-key", "km-key--space"])
    elif name:
        classes.append("km-key")
        if name not in ARROWS:
            classes.append(f"km-key--{name}")
        if pc and name in PC_KEYS:
            classes.append("km-key--pc")
    elif pc and len(text) > 1:
        classes.extend(["km-key", "km-key--text"])
    if name in ARROWS:
        icon = icons.pair(KEY_ICONS[f"{'chevron' if pc else 'caret'}-{name}"])
    elif name == "globe" and not pc:
        icon = icons.pair(KEY_ICONS["globe"])
    elif name == "super" and pc:
        logo = "ubuntu" if "km-key--linux" in classes else "microsoft"
        icon = icons.pair(KEY_ICONS[logo])
    classes[:] = [_ for _ in classes if _ not in SYSTEM_KEYS]
    if icon:
        key += glyph("", "", classes=[*icon.split(), "km-key__icon"])


def combos(children: list[nodes.Node], *, icons: Icons) -> list[nodes.Node]:
    """Dress the keys among some siblings and bind each combo.

    A combo is two or more keys joined by `-`, `+` or `^`. It gets a
    span of its own, which keeps it on one line when it fits.

    :param children: The siblings, some of which are keys.
    :param icons: The icons the site draws.
    :return: The siblings, with every combo in a span.
    """
    result: list[nodes.Node] = []
    combo: list[nodes.Node] = []

    def close() -> None:
        if len(combo) > 1:
            result.append(nodes.inline("", "", *combo, classes=["km-combo"]))
        else:
            result.extend(combo)
        combo.clear()

    index = 0
    while index < len(children):
        node = children[index]
        index += 1
        after = children[index : index + 2]
        if is_key(node):
            if (
                node.astext().lower() == "space"
                and len(after) == 2
                and isinstance(after[0], nodes.Text)
                and after[0].astext().isspace()
                and is_key(after[1])
                and after[1].astext().lower() == "bar"
            ):
                node[:] = [nodes.Text(f"{node.astext()} {after[1].astext()}")]
                index += 2
            dress(node, icons=icons)
            combo.append(node)
        elif (
            combo
            and isinstance(node, nodes.Text)
            and node.astext() in SEPARATORS
            and after
            and is_key(after[0])
        ):
            mark = node.astext()
            combo.append(
                nodes.inline(mark, mark, classes=["km-combo__separator"])
            )
        else:
            close()
            result.append(node)
    close()
    return result


def keycaps(app: Sphinx, doctree: nodes.document) -> None:
    """Dress `kbd` keys as keycaps.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read.
    """
    icons = Icons.of(app.config)
    for parent in list(findall(doctree, nodes.Element)):
        if any(is_key(node) for node in parent.children):
            parent[:] = combos(parent.children, icons=icons)


def _spaced(line: nodes.Element, icons: set[int]) -> None:
    """Mark the icons in a line that start or end it and trim the space
    beside them.

    The line is walked once. Each icon's words before and after it come
    from running flags, and the whitespace goes in two passes, so the
    work grows with the line and not with its icons.

    :param line: The nearest node above the icons that isn't inline.
    :param icons: The `id` of each icon in it that wants spacing.
    """
    order = [
        _ for _ in line.findall() if isinstance(_, nodes.Text) or id(_) in icons
    ]
    present = [
        isinstance(_, nodes.Text) and WORD.search(_.astext()) is not None
        for _ in order
    ]
    behind, seen = [], False
    for found in present:
        behind.append(seen)
        seen = seen or found
    ahead, seen = [], False
    for found in reversed(present):
        ahead.append(seen)
        seen = seen or found
    ahead.reverse()
    prefix = [a and not b for a, b in zip(ahead, behind, strict=True)]
    suffix = [b and not a for a, b in zip(ahead, behind, strict=True)]
    dropped: set[int] = set()
    kept: dict[int, str] = {}
    trimming = False
    for index, node in enumerate(order):
        if not isinstance(node, nodes.Text):
            icon = t.cast("nodes.Element", node)
            if prefix[index]:
                icon["classes"].append("km-glyph--prefix")
                trimming = True
            elif suffix[index]:
                icon["classes"].append("km-glyph--suffix")
            continue
        if trimming:
            text = node.astext().lstrip()
            if not text:
                dropped.add(id(node))
                continue
            if text != node.astext():
                kept[id(node)] = text
            trimming = False
    trimming = False
    for index in range(len(order) - 1, -1, -1):
        node = order[index]
        if not isinstance(node, nodes.Text):
            trimming = trimming or suffix[index]
            continue
        if trimming and id(node) not in dropped:
            written = kept.get(id(node), node.astext())
            text = written.rstrip()
            if not text:
                dropped.add(id(node))
                kept.pop(id(node), None)
                continue
            if text != written:
                kept[id(node)] = text
            trimming = False
    touched = kept.keys() | dropped
    parents = {
        id(_.parent): _.parent
        for _ in order
        if isinstance(_, nodes.Text) and id(_) in touched
    }
    for parent in parents.values():
        parent[:] = [
            nodes.Text(kept[id(_)]) if id(_) in kept else _
            for _ in parent.children
            if id(_) not in dropped
        ]


def glyph_edges(app: Sphinx, doctree: nodes.document) -> None:
    """Mark the icons that start or end a line.

    :param app: The Sphinx application instance (unused).
    :param doctree: The page, just read.
    """
    del app
    lines: dict[int, tuple[nodes.Element, set[int]]] = {}
    for icon in findall(doctree, glyph):
        if "km-glyph" not in icon["classes"]:
            continue
        line: nodes.Element | None = icon.parent
        while line is not None and isinstance(line, nodes.Inline):
            line = line.parent
        found = t.cast("nodes.Element", line)
        lines.setdefault(id(found), (found, set()))[1].add(id(icon))
    for line, icons in lines.values():
        _spaced(line, icons)
