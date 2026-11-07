"""\
Directive Utilities
===================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 07 November 2026

The helpers Kaamiki's directives are built from.
"""

from __future__ import annotations

import os.path as p
import typing as t
from urllib.parse import urlsplit

from docutils import nodes
from markupsafe import Markup
from sphinx import addnodes
from sphinx.util import docname_join

from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils.templates import render

if t.TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Iterable
    from collections.abc import Iterator
    from collections.abc import Sequence

    from docutils.parsers.rst import Directive
    from sphinx.writers.html import HTMLTranslator

LINKCHECK_OPTIONS: tuple[str, ...] = ("avatar", "backdrop", "target")
LINKS: t.Final[tuple[type[nodes.Node], ...]] = (
    nodes.reference,
    nodes.footnote_reference,
    nodes.citation_reference,
    addnodes.pending_xref,
)
# NOTE(xames3): The two options docutils gives its own directives, so a
# Kaamiki directive reads `:class:` and `:name:` the same way.
# https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options
NATIVE: t.Final[dict[str, Callable[[str | None], t.Any]]] = {
    "class": checks.classes,
    "name": checks.reference_name,
}


def toggle(argument: str | None) -> bool:
    """Read a directive option or a page field as a switch.

    A bare one is on and `false` turns it off.

    :param argument: The value written in the rST or `None` when bare.
    :return: Whether it's on.
    :raises ValueError: For anything but nothing, `true` and `false`.
    """
    if argument in (None, "", "true"):
        return True
    if argument == "false":
        return False
    raise ValueError(f"expected true or false, got {argument!r}")


def hollow(found: Iterable[nodes.Node]) -> bool:
    """Say whether some parsed nodes hold nothing a reader would see.

    :param found: The nodes.
    :return: `True` when all there is are comments and link targets.
    """
    skipped = (nodes.comment, nodes.target)
    return all(isinstance(_, skipped) for _ in found)


def through(found: Iterable[nodes.Node]) -> Iterator[nodes.Node]:
    """Walk some nodes, looking through each `only` to what it holds.

    :param found: The nodes.
    :return: Each node that isn't an `only`, in the order written.
    """
    for each in found:
        if isinstance(each, addnodes.only):
            yield from through(each.children)
        else:
            yield each


def unlinked(
    directive: Directive,
    found: Iterable[nodes.Node] | nodes.Node,
    part: str,
) -> None:
    """Refuse a link in a text that is a link already or a control.

    :param directive: The directive that has the text.
    :param found: The parsed text or the nodes it came to.
    :param part: What the text is, `a label` for one.
    :raises rst.DirectiveError: When the text holds a link.
    """
    for each in [found] if isinstance(found, nodes.Node) else found:
        if any(isinstance(_, LINKS) for _ in each.findall()):
            raise directive.error(
                f"{directive.name}: expected {part} without a link, got one"
            )


def worded(
    directive: Directive,
    found: Iterable[nodes.Node] | nodes.Node,
    part: str,
) -> None:
    """Refuse a text that has no words, only an icon or nothing.

    An icon adds to a text and never stands for it, so a screen reader
    and a reader with the icons switched off still get the meaning.

    :param directive: The directive that has the text.
    :param found: The parsed text or the nodes it came to.
    :param part: What the text is, `a title` for one.
    :raises rst.DirectiveError: When the text reads as nothing.
    """
    each = [found] if isinstance(found, nodes.Node) else found
    if not "".join(_.astext() for _ in each).strip():
        raise directive.error(
            f"{directive.name}: expected {part} with words, got only an"
            " icon or nothing"
        )


def titled(directive: Directive, argument: str) -> str:
    """Read the title a directive is given as its argument.

    :param directive: The directive that has the title.
    :param argument: The title as written.
    :return: The title, trimmed.
    :raises rst.DirectiveError: When it is blank or too long.
    """
    try:
        return checks.text(argument)
    except ValueError as error:
        raise directive.error(f"{directive.name}: title {error}") from error


def document(directive: Directive, name: str, option: str) -> str:
    """Find the document an option names, as `:doc:` would write it.

    :param directive: The directive that has the option.
    :param name: The document, relative to the page or from the top
        with a leading `/`.
    :param option: The option it was written in.
    :return: The document's name.
    :raises rst.DirectiveError: When the site has no such document.
    """
    env = directive.state.document.settings.env
    found = docname_join(env.docname, name.strip())
    if found not in env.found_docs:
        raise directive.error(
            f"{directive.name}: :{option}: expected a document of this site,"
            f" got {name!r}"
        )
    return found


def shipped(directive: Directive, value: str, where: str) -> str:
    """Check that a path from the top of the site is a file the build
    puts there.

    A full address or a `#` fragment is left alone. A path under
    `_static` has to be in one of `html_static_path` and any other path
    in `html_extra_path`, and it can't climb out of that folder. The
    file is noted as one the page depends on, so the page is read again
    when it changes or goes.

    :param directive: The directive that has the option.
    :param value: The path or address, as written.
    :param where: What it was written as, `:poster:` or `the address`.
    :return: The value, as written.
    :raises rst.DirectiveError: When no such file ships with the site.
    """
    from kaamiki.extensions.utils.context import confdir

    parts = urlsplit(value)
    if parts.scheme or value.startswith("#"):
        return value
    env = directive.state.document.settings.env
    name = parts.path.lstrip("/")
    config = env.config
    if name.startswith("_static/"):
        name = name.removeprefix("_static/")
        roots = config.html_static_path
    else:
        roots = config.html_extra_path
    for root in (p.normpath(p.join(confdir(env), _)) for _ in roots):
        if p.isfile(root) and p.basename(root) == name:
            found = root
        else:
            found = p.normpath(p.join(root, name))
            if p.commonpath([root, found]) != root:
                continue
        if p.isfile(found):
            env.note_dependency(found)
            return value
    raise directive.error(
        f"{directive.name}: {where} expected a file in html_static_path or"
        f" html_extra_path, got {value!r}"
    )


def named(directive: Directive, node: nodes.Element) -> None:
    """Give a node the name its `:name:` option asks for, once.

    :param directive: The directive that has the option.
    :param node: The node to name.
    :raises rst.DirectiveError: When the page already has the name.
    """
    if "name" not in directive.options:
        return
    page = directive.state.document
    name = nodes.fully_normalize_name(directive.options["name"])
    if name in page.nameids:
        raise directive.error(
            f"{directive.name}: :name: {name!r} is on the page already"
        )
    directive.add_name(node)


def depart(self: HTMLTranslator, node: nodes.Element) -> None:
    """Close a node that has nothing to close.

    :param self: The HTML translator instance.
    :param node: The node being departed.
    """


def close(self: HTMLTranslator, node: nodes.Element) -> None:
    """Close the `<div>` a node's visitor opened.

    :param self: The HTML translator instance.
    :param node: The node being departed (unused).
    """
    del node
    self.body.append("</div>")


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


class phrase(nodes.TextElement):
    """A directive's text, parsed and waiting for its template."""


def located[N: nodes.Node](directive: Directive, node: N) -> N:
    """Give a node the place in the source it was written, which
    `gettext` needs to collect the text.

    :param directive: The directive the node's text belongs to.
    :param node: The node.
    :return: The same node.
    """
    node.source, node.line = directive.state_machine.get_source_and_line(
        directive.lineno
    )
    return node


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
    return located(directive, phrase(text, "", *words, field=field)), messages


BLOCKS: t.Final[tuple[tuple[type[nodes.Node], str], ...]] = (
    (nodes.bullet_list, "a list"),
    (nodes.enumerated_list, "a list"),
    (nodes.definition_list, "a definition list"),
    (nodes.block_quote, "a block quote"),
    (nodes.literal_block, "a code block"),
    (nodes.table, "a table"),
    (nodes.comment, "a comment"),
)


def paragraph(
    directive: Directive, text: str, field: str
) -> tuple[phrase, list[nodes.system_message]]:
    """Parse a directive's content, which is one paragraph of text.

    It reads the content as a page does, so a list, a second paragraph
    or a directive in it is found and not written out as text.

    :param directive: The directive the content belongs to.
    :param text: The content, as written in the rST.
    :param field: The name the directive's template knows it by.
    :return: The parsed text, held under its name, and whatever the
        parsing reported.
    :raises rst.DirectiveError: When the content isn't one paragraph.
    """
    if not text.strip():
        return parse(directive, text, field)
    holder = nodes.Element()
    directive.state.nested_parse(
        directive.content, directive.content_offset, holder
    )
    found = [
        _ for _ in holder.children if not isinstance(_, nodes.system_message)
    ]
    messages = [
        _ for _ in holder.children if isinstance(_, nodes.system_message)
    ]
    if len(found) != 1 or type(found[0]) is not nodes.paragraph:
        what = "more than one block"
        if found and all(type(_) is nodes.paragraph for _ in found):
            what = "more than one paragraph"
        if len(found) == 1:
            what = next(
                (name for kind, name in BLOCKS if isinstance(found[0], kind)),
                "a directive",
            )
        raise directive.error(
            f"{directive.name}: expected one paragraph of text, got {what}"
        )
    return (
        located(directive, phrase(text, "", *found[0].children, field=field)),
        messages,
    )


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
        attributes, it returns what the template is given. It's where
        a directive turns the paths it was handed into addresses.
    :return: The visitor, which raises `nodes.SkipNode` once written.
    """

    def visit(self: HTMLTranslator, node: nodes.Element) -> None:
        icons = self.builder.config.html_context["km_fa_icons"]
        attributes = dict(node.attributes)
        if prepare is not None:
            attributes = prepare(self, attributes)
        self.body.append(
            render(template, fa_icons=icons, **attributes, **fields(self, node))
        )
        raise nodes.SkipNode

    return visit


def what(found: nodes.Node) -> str:
    """Say what a node is, the way a message names what author wrote.

    :param found: The node.
    :return: Its name with an article, `a paragraph` or `an accordion`.
    """
    from kaamiki.extensions import nesting

    return nesting.describe(found)


def listed(value: str) -> list[str]:
    """Split a comma-separated option into its trimmed, non-empty
    parts.

    :param value: The option's value.
    :return: The parts, in the order written.
    """
    return [_.strip() for _ in value.split(",") if _.strip()]
