"""\
Directive Utilities
===================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 25 October 2026

The helpers Kaamiki's directives are built from.
"""

import os.path as p
import typing as t
from urllib.parse import urlsplit

from docutils import nodes
from markupsafe import Markup
from sphinx.util import docname_join

from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils.settings import ICONS
from kaamiki.extensions.utils.templates import render

if t.TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Iterable
    from collections.abc import Sequence

    from docutils.parsers.rst import Directive
    from sphinx.writers.html import HTMLTranslator

LINKCHECK_OPTIONS: tuple[str, ...] = ("avatar", "background", "url")
# NOTE(xames3): The two options docutils gives its own directives, so a
# Kaamiki directive reads `:class:` and `:name:` the same way.
NATIVE: t.Final[dict[str, Callable[[str | None], t.Any]]] = {
    "class": checks.classes,
    "name": checks.slug,
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
    :return: `True` when all there is are comments.
    """
    skipped = (nodes.comment, nodes.target)
    return all(isinstance(_, skipped) for _ in found)


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
    :param name: The document, relative to the page or from the top with
        a leading `/`.
    :param option: The option it was written in.
    :return: The document's name.
    :raises rst.DirectiveError: When the site has no such document.
    """
    env = directive.state.document.settings.env
    found = docname_join(env.docname, name.strip())
    if found not in env.found_docs:
        raise directive.error(
            f"{directive.name}: :{option}: {name!r} is not a document"
        )
    return found


def shipped(directive: Directive, value: str, where: str) -> str:
    """Check that a path from the top of the site is a file the build puts
    there.

    A full address or a `#` fragment is left alone. A path under
    `_static` has to be in one of `html_static_path` and any other path
    in `html_extra_path`.

    :param directive: The directive that has the option.
    :param value: The path or address, as written.
    :param where: What it was written as, `:poster:` or `the address`.
    :return: The value, as written.
    :raises rst.DirectiveError: When no such file ships with the site.
    """
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
    for root in (p.join(env.app.confdir, _) for _ in roots):
        if p.isfile(p.join(root, name)) or (
            p.isfile(root) and p.basename(root) == name
        ):
            return value
    raise directive.error(
        f"{directive.name}: {where} {value!r} is not in html_static_path or"
        " html_extra_path"
    )


def named(directive: Directive, node: nodes.Element) -> None:
    """Give a node the name its `:name:` option asks for, once.

    :param directive: The directive that has the option.
    :param node: The node to name.
    :raises rst.DirectiveError: When the page already has the name.
    """
    if "name" not in directive.options:
        return
    document = directive.state.document
    name = nodes.fully_normalize_name(directive.options["name"])
    if name in document.nameids:
        raise directive.error(f":name: {name!r} is on the page already")
    directive.add_name(node)


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
        attributes, it returns what the template is given. It's where
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
