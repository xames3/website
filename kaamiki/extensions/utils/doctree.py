"""\
Doctree Utilities
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 26 October 2026

The helpers that walk a doctree and pick prose out of it.
"""

import typing as t
from uuid import uuid4

from docutils import nodes
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound
from sphinx.builders.gettext import MessageCatalogBuilder

from kaamiki.extensions.utils.settings import FILE_ICON
from kaamiki.extensions.utils.settings import free
from kaamiki.extensions.utils.settings import language_icon
from kaamiki.extensions.utils.settings import setting
from kaamiki.extensions.utils.text import clip

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from sphinx.application import Sphinx


class annotated(nodes.container):
    """A snippet with notes beside it, the base of `code-explain`."""


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
SEPARATORS: t.Final[frozenset[str]] = frozenset({"-", "+", "^"})


FURNITURE: tuple[type, ...] = (
    annotated,
    nodes.Admonition,
    nodes.figure,
    nodes.literal_block,
    nodes.table,
    nodes.topic,
)
TRANSLATED: t.Final[frozenset[str]] = frozenset(
    {
        "km-fb-button",
        "km-fb-description",
        "km-fb-title",
        "km-pg-description",
        "km-header-subtitle",
        "km-pg-image-alt",
        "km-pg-title",
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


def badged(
    caption: nodes.Element,
    language: str | None,
    *,
    kit: bool = False,
) -> str:
    """Pick the icon a code block's caption wears.

    The language has the first say. A language with no icon of its own,
    like a diff's, hands over to the caption's file name and a name no
    icon knows gets a plain file.

    :param caption: The caption.
    :param language: The language of the code under it.
    :param kit: Whether the site has a Font Awesome kit.
    :return: The icon's classes or an empty string when the caption
        opens with an icon of its own.
    """
    first = caption.children[0] if caption.children else None
    if isinstance(first, glyph):
        return ""
    if icon := language_icon(language, kit=kit):
        return icon
    try:
        lexer = get_lexer_for_filename(caption.astext().strip())
    except ClassNotFound:
        return FILE_ICON
    for alias in lexer.aliases:
        if icon := language_icon(alias, kit=kit):
            return icon
    return FILE_ICON


def buried(paragraph: nodes.Element) -> bool:
    """Say whether a paragraph sits inside an admonition, table or code
    block.

    Figures, topics and the notes of a walkthrough count too. Lifted
    out of those, a line reads as a non-sequitur.

    :param paragraph: The paragraph to place.
    :return: `True` when it has one of those for an ancestor.
    """
    parent: nodes.Element | None = paragraph.parent
    while parent is not None and not isinstance(parent, FURNITURE):
        parent = parent.parent
    return parent is not None


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
        if "km-lead" not in (paragraph.get("classes") or []):
            continue
        if buried(paragraph):
            continue
        text = " ".join(paragraph.astext().split())
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
        text = " ".join(paragraph.astext().split())
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


def dress(key: nodes.literal, *, kit: bool) -> None:
    """Give a key the classes and the icon that draw it.

    The arrows, the globe and Super wear a Font Awesome icon. The globe
    is a solid one when the site has no kit.

    :param key: The key.
    :param kit: Whether the site has a Font Awesome kit.
    """
    classes = key["classes"]
    pc = bool({"km-windows", "km-linux"} & set(classes))
    text = " ".join(key.astext().lower().split())
    name = KEYS.get(text)
    icon = ""
    if text in ("space", "space bar"):
        classes.append("km-space")
    elif name:
        classes.append("km-key")
        if name not in ARROWS:
            classes.append(f"km-key-{name}")
        if pc and name in PC_KEYS:
            classes.append("km-pc")
    elif pc and len(text) > 1:
        classes.append("km-key-text")
    if name in ARROWS:
        icon = f"fa-solid fa-{'chevron' if pc else 'caret'}-{name}"
    elif name == "globe" and not pc:
        icon = "fa-light fa-globe"
    elif name == "super":
        logo = "ubuntu" if "km-linux" in classes else "microsoft"
        icon = f"fa-brands fa-{logo}"
    if icon:
        if not kit:
            icon = free(icon)
        key += glyph("", "", classes=[*icon.split(), "km-key-icon"])


def combos(children: list[nodes.Node], *, kit: bool) -> list[nodes.Node]:
    """Dress the keys among some siblings and bind each combo.

    A combo is two or more keys joined by `-`, `+` or `^`. It gets a
    span of its own, which keeps it on one line when it fits.

    :param children: The siblings, some of which are keys.
    :param kit: Whether the site has a Font Awesome kit.
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
            dress(node, kit=kit)
            combo.append(node)
        elif (
            combo
            and isinstance(node, nodes.Text)
            and node.astext() in SEPARATORS
            and after
            and is_key(after[0])
        ):
            mark = node.astext()
            combo.append(nodes.inline(mark, mark, classes=["km-kbd-sep"]))
        else:
            close()
            result.append(node)
    close()
    return result


def keycaps(app: Sphinx, doctree: nodes.document) -> None:
    """Dress `kbd` keys as keycaps.

    Each key named in `KEYS` gets `km-key` and, but for the arrows, a
    `km-key-*` class, which the stylesheet draws as it's printed on a
    Mac keyboard. The text stays, so search and screen readers still see
    "Cmd". "Space bar" is one key, a wide one without text.

    Written with `kbd:windows` or `kbd:linux`, the keys in `PC_KEYS` get
    `km-pc` and are drawn as a PC prints them. Any other key named by a
    word, like Alt or Home, gets `km-key-text`, which sets it a little
    smaller.

    Keys joined by `-`, `+` or `^` are one combo, wrapped in `km-combo`
    so it stays on one line when it fits. The separators are wrapped in
    `km-kbd-sep`, which the stylesheet hides.

    :param app: The Sphinx application instance.
    :param doctree: The page, just read.
    """
    kit = bool(setting(app.config, "fa_kit"))
    for parent in list(findall(doctree, nodes.Element)):
        if any(is_key(node) for node in parent.children):
            parent[:] = combos(parent.children, kit=kit)
