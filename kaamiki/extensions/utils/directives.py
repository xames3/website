"""\
Directive Utilities
===================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 15 October 2026

The helpers Kaamiki's directives are built from.
"""

import typing as t
from math import isfinite

from docutils import nodes
from markupsafe import Markup

from kaamiki.extensions.utils.settings import ICONS
from kaamiki.extensions.utils.templates import render

if t.TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Sequence

    from docutils.parsers.rst import Directive
    from sphinx.writers.html import HTMLTranslator

LINKCHECK_OPTIONS: tuple[str, ...] = ("avatar", "background", "url")


def toggle(argument: str | None) -> bool:
    """Read a directive option as a switch.

    A bare option is on and `false` turns it off.

    :param argument: The value written in the rST or `None` when bare.
    :return: Whether the option is on.
    :raises ValueError: For anything else.
    """
    value = (argument or "").strip().lower()
    if value in {"", "true"}:
        return True
    if value == "false":
        return False
    raise ValueError(f"expected true or false, got {argument!r}")


def seconds(argument: str | None) -> float:
    """Read a directive option as a number of seconds above zero.

    :param argument: The value written in the rST.
    :return: The seconds.
    :raises ValueError: When it isn't a number above zero.
    """
    if argument is None:
        raise ValueError("argument required but none supplied")
    value = float(argument)
    if not isfinite(value) or value <= 0:
        raise ValueError("expected a number of seconds above zero")
    return value


def depart(self: HTMLTranslator, node: nodes.Element) -> None:
    """Close a node that has nothing to close.

    :param self: The HTML translator instance.
    :param node: The node being departed.
    """


def skip(self: nodes.NodeVisitor, node: nodes.Element) -> None:
    """Leave a node out of a builder that has no use for it.

    :param self: The translator.
    :param node: The node being skipped.
    :raises nodes.SkipNode: Always.
    """
    del self, node
    raise nodes.SkipNode


def trail(
    options: dict[str, t.Any],
    keys: Sequence[str] = LINKCHECK_OPTIONS,
) -> list[nodes.Node]:
    """Give `linkcheck` the URLs a directive keeps in its options.

    Sphinx only reads URLs off `reference`, `image` and `raw` nodes, so
    each one is returned as an empty `raw` node to sit beside the
    directive's own.

    :param options: The directive's options, as written in the rST.
    :param keys: The options holding URLs, the byline's by default.
    :return: One empty `raw` node per URL found, ready to sit beside
        the directive's own node.
    """
    found: list[nodes.Node] = []
    for option in keys:
        found += [
            nodes.raw("", "", format="html", source=uri)
            for uri in options.get(option, "").split()
            if "://" in uri
        ]
    return found


# NOTE(xames3): A `TextElement` and not an `inline`, which Sphinx unwraps
# when it translates a page.
class phrase(nodes.TextElement):
    """A directive's text, parsed and waiting for its template."""


def parse(
    directive: Directive, text: str, field: str
) -> tuple[phrase, list[nodes.system_message]]:
    """Parse a directive's text the way a paragraph is parsed.

    The text keeps its place in the source, so `gettext` can collect
    it.

    :param directive: The directive the text belongs to.
    :param text: The text, as written in the rST.
    :param field: The name the directive's template knows it by.
    :return: The parsed text, held under its name and whatever the
        parsing reported.
    """
    words, messages = directive.state.inline_text(text, directive.lineno)
    found = phrase(text, "", *words, field=field)
    found.source, found.line = directive.state_machine.get_source_and_line(
        directive.lineno
    )
    return found, messages


def fields(self: HTMLTranslator, node: nodes.Element) -> dict[str, Markup]:
    """Write out the text `parse` made, one piece of HTML per field.

    The page's own translator writes each one, so it reads as a
    paragraph would.

    :param self: The HTML translator.
    :param node: The directive's node, holding what `parse` made.
    :return: Each field's HTML under its name, ready for a template.
    """
    found: dict[str, Markup] = {}
    body = self.body
    for child in node.children:
        if not isinstance(child, phrase) or "field" not in child:
            continue
        self.body = []
        for part in child.children:
            part.walkabout(self)
        found[child["field"]] = Markup("".join(self.body))  # noqa: S704
    self.body = body
    return found


def visitor(
    template: str,
    prepare: Callable[[HTMLTranslator, dict[str, t.Any]], dict[str, t.Any]]
    | None = None,
) -> Callable[[HTMLTranslator, nodes.Element], None]:
    """Make the visitor that writes a directive's node out in one go.

    One template draws the whole node, so the writer has nothing left
    to walk into.

    :param template: The directive's template, relative to
        `theme/templates`.
    :param prepare: Called with the translator and a copy of the node's
        attributes, it returns what the template is given. It is where
        a directive turns the paths it was handed into addresses.
    :return: The visitor, which raises `nodes.SkipNode` once written.
    """

    def visit(self: HTMLTranslator, node: nodes.Element) -> None:
        icons = self.builder.config.html_context.get("km_fa_icons", ICONS)
        attributes = dict(node.attributes)
        if prepare is not None:
            attributes = prepare(self, attributes)
        self.body.append(
            render(template, fa_icons=icons, **attributes, **fields(self, node))
        )
        raise nodes.SkipNode

    return visit


def listed(value: str) -> list[str]:
    """Split a comma-separated option into its trimmed, non-empty
    parts.

    :param value: The option's value.
    :return: The parts, in the order written.
    """
    return [_.strip() for _ in value.split(",") if _.strip()]
