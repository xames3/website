"""\
Embed Directive
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 11 August, 2026
Last updated on: 29 September, 2026

An `embed` directive that drops a block of HTML into the page. Written
inline, the argument is `iframe` and the content is the markup::

    .. embed:: iframe
       :expected-count: 10

       <iframe
           src="https://example.com"
           width="100%"
           height="400px"
           data-expected-count="{{ expected-count }}">
       </iframe>

A larger embed is better kept in a file of its own, named as the
argument instead, relative to the document or, with a leading `/`, to
the source directory. Any CSS or JavaScript it needs is named in
`:css:` and `:js:`, comma-separated, as filenames under
`html_static_path`. They load in the order written, on the pages that
use the directive and on no others::

    .. embed:: ../assets/html/embed.html
       :css: embed.css
       :js: embed.js

Options become placeholders: `{{ expected-count }}` in the HTML is
replaced by the option's value, escaped for wherever it lands.
"""

from __future__ import annotations

import ast
import contextlib
import json
import re
import typing as t
from html import escape

import docutils.nodes as nodes
import docutils.parsers.rst as rst
from sphinx.util import logging

from kaamiki.extensions.utils import findall

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx

logger = logging.getLogger(__name__)

name: t.Final[str] = "embed"
pattern: t.Pattern[str] = re.compile(
    r"^[ \t]*:([\w-]+):[ \t]*(.*?)(?=^[ \t]*:[\w-]+:|\Z)",
    re.MULTILINE | re.DOTALL,
)
SCRIPTISH: t.Pattern[str] = re.compile(
    r"<(script|style)\b[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE
)
PLACEHOLDER: t.Pattern[str] = re.compile(r"\{\{\s*([\w-]+)\s*\}\}")
NOTE: t.Pattern[str] = re.compile(r"\{#.*?#\}[ \t]*\n?", re.DOTALL)
ESCAPES: dict[str, str] = {
    "<": "\\u003c",
    ">": "\\u003e",
    "&": "\\u0026",
    "\u2028": "\\u2028",
    "\u2029": "\\u2029",
}
STYLE_ESCAPES: frozenset[str] = frozenset("<>&\"'\\\n\r")
ASSETS: t.Final[frozenset[str]] = frozenset({"css", "js", "encoding"})


def encode(value: str, kind: str) -> str:
    """Write a placeholder's value for where it sits.

    A script gets the value read as a Python literal, so a number stays
    a number and a list becomes an array. Markup and CSS get it as it
    was written, less the quotes around a quoted string.

    :param value: The option's value, as written.
    :param kind: `script`, `style` or anything else for markup.
    :return: The value, escaped so it cannot break out of its place.
    """
    read = literal(value)
    if kind == "script":
        encoded = json.dumps(read, default=str)
        for char, point in ESCAPES.items():
            encoded = encoded.replace(char, point)
        return encoded
    text = read if isinstance(read, str) else value
    if kind == "style":
        return "".join(
            f"\\{ord(_):x} " if _ in STYLE_ESCAPES else _ for _ in text
        )
    return escape(text, quote=True)


def substitute(source: str, values: dict[str, str]) -> str:
    """Fill a fragment's placeholders, escaping each for where it sits.

    Markup, script and style want different things. A value in an
    attribute needs its quotes and brackets escaped or it closes the
    attribute early; the same treatment inside a `<script>` turns an
    array into `[&quot;a&quot;]` and JSON inside a `<style>` wraps a
    colour in quotes. The source is split on its script and style
    blocks and each gets what it needs.

    :param source: The fragment, placeholders and all.
    :param values: Directive options, keyed as they are written in the
        rST. A placeholder may spell them with underscores instead of
        hyphens.
    :return: The fragment with every known placeholder filled in.
        Anything unrecognised is left alone.
    """

    def swap(kind: str) -> t.Callable[[t.Match[str]], str]:
        def fill(match: t.Match[str]) -> str:
            key = match.group(1)
            if key not in values:
                key = key.replace("_", "-")
            if key not in values:
                return match.group(0)
            return encode(values[key], kind)

        return fill

    out: list[str] = []
    cursor = 0
    for block in SCRIPTISH.finditer(source):
        before = source[cursor : block.start()]
        out.append(PLACEHOLDER.sub(swap("html"), before))
        kind = block.group(1).lower()
        out.append(PLACEHOLDER.sub(swap(kind), block.group(0)))
        cursor = block.end()
    out.append(PLACEHOLDER.sub(swap("html"), source[cursor:]))
    return "".join(out)


def literal(value: str) -> t.Any:
    """Read an option's value as a Python literal where it is one.

    :param value: The value, as written.
    :return: A number, list or the like when it reads as one and the
        text otherwise.
    """
    with contextlib.suppress(ValueError, SyntaxError):
        return ast.literal_eval(value)
    return value


def files(value: str | None) -> list[str]:
    """Split a `:css:` or `:js:` option into its files, in order.

    :param value: The option's value or `None` when unset.
    :return: The files, in the order they were written.
    """
    return [_.strip() for _ in (value or "").split(",") if _.strip()]


class directive(rst.Directive):
    """The `embed` directive.

    The argument is either `iframe`, with the markup as content or the
    path to an HTML fragment. Every other option is a placeholder
    value, apart from `encoding`, `css` and `js`.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True

    def run(self) -> list[nodes.Node]:
        """Read the markup, fill its placeholders and return it.

        :return: A list holding the one `raw` node, which also carries
            the stylesheets and scripts the page is to load for it.
        """
        argument = self.arguments.pop().strip()
        file, _, options = argument.partition("\n")
        file = file.strip()
        for key, value in pattern.findall(options):
            self.options[key] = value.strip()
        if file == "iframe":
            if not self.content:
                raise self.error("embed requires inline HTML content")
            source = "\n".join(self.content)
        else:
            source = self.read(file)
        source = NOTE.sub("", source)
        values = {
            key: value
            for key, value in self.options.items()
            if key not in ASSETS
        }
        self.check(source, values)
        attributes: dict[str, t.Any] = {}
        attributes["text"] = substitute(source, values)
        attributes["format"] = "html"
        attributes["css"] = files(self.options.get("css"))
        attributes["js"] = files(self.options.get("js"))
        return [nodes.raw(**attributes)]

    def check(self, source: str, values: dict[str, str]) -> None:
        """Catch an option or a placeholder that has been misspelt.

        An option the fragment never asks for is an error, since its
        value would go nowhere. A placeholder no option fills is left in
        the page as written, which may be meant, so it only warns.

        :param source: The fragment, placeholders and all.
        :param values: The options that fill placeholders.
        """
        wanted = {_.replace("_", "-") for _ in PLACEHOLDER.findall(source)}
        unused = sorted(_ for _ in values if _.replace("_", "-") not in wanted)
        if unused:
            raise self.error(
                f"embed has {', '.join(f':{_}:' for _ in unused)}, which"
                " nothing in the fragment asks for"
            )
        given = {_.replace("_", "-") for _ in values}
        for key in sorted(wanted - given):
            env = self.state.document.settings.env
            logger.warning(
                "embed: {{ %s }} has no option to fill it",
                key,
                location=(env.docname, self.lineno),
                type="embed",
            )

    def read(self, file: str) -> str:
        """Read an HTML fragment off disk.

        The path follows Sphinx's rule: relative to the document or to
        the source directory when it starts with a `/`.

        :param file: The path, as written.
        :return: The fragment.
        """
        if self.content:
            raise self.error("embed can't use file and inline content")
        env = self.state.document.settings.env
        relative, path = env.relfn2path(file, env.docname)
        encoding = self.options.get("encoding", "utf-8")
        try:
            with open(path, encoding=encoding) as fd:
                source = fd.read()
        except OSError as exc:
            raise self.error(f"embed could not read {file!r}: {exc}") from exc
        env.note_dependency(relative)
        return source


def html_page_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Attach the page's embedded stylesheets and scripts to it.

    They go in the order the page names them, embed after embed, each
    file once. Only the pages carrying an `embed` that named assets get
    them, so the rest of the site is free of files it does not use.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context.
    :param doctree: The resolved doctree or `None` for generated
        pages.
    """
    if doctree is None:
        return
    css: dict[str, None] = {}
    js: dict[str, None] = {}
    for raw in findall(doctree, nodes.raw):
        css.update(dict.fromkeys(raw.get("css", ())))
        js.update(dict.fromkeys(raw.get("js", ())))
    for filename in css:
        app.add_css_file(filename)
    for filename in js:
        app.add_js_file(filename)
