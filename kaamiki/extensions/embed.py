"""\
Embed Directive
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 11 August, 2026
Last updated on: 12 September, 2026

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
argument instead. Any CSS or JavaScript it needs is named in `:css:`
and `:js:`, comma-separated, as filenames under `html_static_path`.
They are attached to the pages that use the directive and to no
others::

    .. embed:: ../assets/html/embed.html
       :css: embed.css
       :js: embed.js

Options become placeholders: `{{ expected-count }}` in the HTML is
replaced by the option's value, escaped for wherever it lands.

.. versionchanged:: 31.8.2026

    [1] Renamed from `iframe`, since the directive covers inline
        content and external fragments and not just iframes.
    [2] The `:file:` option is gone. The argument is either `iframe` or
        the fragment's path.
    [3] An option's value may span several indented lines.

.. versionadded:: 10.9.2026

    `substitute` escapes each placeholder for where it sits: quotes and
    brackets for an attribute, JSON for a `<script>`. It was a plain
    string replace before, so a fragment was only ever as safe as the
    options handed to it.

.. deprecated:: 10.9.2026

    Dropped the `node` class and the `visit`/`depart` pair. This
    directive hands back a `nodes.raw` and never reaches a translator,
    so all three only existed to keep the registration loop happy.
"""

from __future__ import annotations

import ast
import contextlib
import json
import os.path as p
import re
import typing as t
from html import escape

import docutils.nodes as nodes
import docutils.parsers.rst as rst

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx

name: t.Final[str] = "embed"
pattern: t.Pattern[str] = re.compile(
    r"^[ \t]*:([\w-]+):[ \t]*(.*?)(?=^[ \t]*:[\w-]+:|\Z)",
    re.MULTILINE | re.DOTALL,
)


SCRIPTISH: t.Pattern[str] = re.compile(
    r"<(script|style)\b[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE
)
PLACEHOLDER: t.Pattern[str] = re.compile(r"\{\{\s*([\w-]+)\s*\}\}")
ESCAPES: dict[str, str] = {
    "<": "\\u003c",
    ">": "\\u003e",
    "&": "\\u0026",
    "\u2028": "\\u2028",
    "\u2029": "\\u2029",
}


def substitute(source: str, values: dict[str, t.Any]) -> str:
    """Fill a fragment's placeholders, escaping each for where it sits.

    Markup and script want opposite things. A value in an attribute
    needs its quotes and brackets escaped or it closes the attribute
    early; the same treatment inside a `<script>` turns an array into
    `[&quot;a&quot;]` and breaks the page. The source is split on its
    script and style blocks, and each side gets what it needs.

    :param source: The fragment, placeholders and all.
    :param values: Directive options, keyed as they are written in the
        rST. A placeholder may spell them with underscores instead of
        hyphens.
    :return: The fragment with every known placeholder filled in.
        Anything unrecognised is left alone.

    .. versionadded:: 10.9.2026
    """

    def swap(*, scripting: bool) -> t.Callable[[t.Match[str]], str]:
        def fill(match: t.Match[str]) -> str:
            key = match.group(1)
            if key not in values:
                key = key.replace("_", "-")
            if key not in values:
                return match.group(0)
            value = values[key]
            if scripting:
                encoded = json.dumps(value, default=str)
                for char, point in ESCAPES.items():
                    encoded = encoded.replace(char, point)
                return encoded
            return escape(str(value), quote=True)

        return fill

    out: list[str] = []
    cursor = 0
    for block in SCRIPTISH.finditer(source):
        out.append(
            PLACEHOLDER.sub(
                swap(scripting=False), source[cursor : block.start()]
            )
        )
        out.append(PLACEHOLDER.sub(swap(scripting=True), block.group(0)))
        cursor = block.end()
    out.append(PLACEHOLDER.sub(swap(scripting=False), source[cursor:]))
    return "".join(out)


class directive(rst.Directive):
    """The `embed` directive.

    The argument is either `iframe`, with the markup as content, or the
    path to an HTML fragment. Every other option is a placeholder
    value, apart from `encoding`, `css` and `js`.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True

    def run(self) -> list[nodes.Node]:
        """Read the markup, fill its placeholders and return it.

        :return: A list holding the one `raw` node.

        .. versionchanged:: 31.8.2026

            The argument is either `iframe` or the fragment's path,
            replacing the old `:file:` option. Options are read out of
            that same argument, so a value may span several indented
            lines.
        """
        argument = self.arguments.pop().strip()
        file, _, options = argument.partition("\n")
        file = file.strip()
        for key, value in pattern.findall(options):
            value = value.strip()
            with contextlib.suppress(ValueError, SyntaxError):
                value = ast.literal_eval(value)
            self.options[key] = value
        if file == "iframe":
            if not self.content:
                raise self.error("embed requires inline HTML content")
            source = "\n".join(self.content)
        else:
            if self.content:
                raise self.error("embed can't use file and inline content")
            if not p.isabs(file):
                here = p.dirname(str(self.state.document.current_source))
                file = p.abspath(p.join(here, file))
            if not p.isfile(file):
                raise FileNotFoundError(f"{file!r} not found")
            dependencies = self.state.document.settings.record_dependencies
            if dependencies is not None:
                dependencies.add(p.abspath(str(file)))
            encoding = self.options.get("encoding", "utf-8")
            with open(file, encoding=encoding) as fd:
                source = fd.read()
        values = {
            key: value
            for key, value in self.options.items()
            if key not in {"encoding", "css", "js"}
        }
        rendered = substitute(source, values)
        env = self.state.document.settings.env
        docname = env.docname
        assets = env.embed_assets = getattr(env, "embed_assets", {})
        css_files, js_files = assets.setdefault(docname, (set(), set()))
        css_files.update(
            _.strip()
            for _ in self.options.get("css", "").split(",")
            if _.strip()
        )
        js_files.update(
            _.strip()
            for _ in self.options.get("js", "").split(",")
            if _.strip()
        )
        attributes: dict[str, str] = {}
        attributes["text"] = rendered
        attributes["format"] = "html"
        return [nodes.raw(**attributes)]


def html_page_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Attach an embed's `:css:` and `:js:` files to its page.

    Only the pages carrying an `embed` that named assets get them, so
    the rest of the site is free of stylesheets and scripts it does not
    use.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered.
    :param templatename: The template rendering it (unused).
    :param context: The page's rendering context (unused).
    :param doctree: The resolved doctree, or `None` for generated
        pages (unused).

    .. versionchanged:: 31.8.2026

        The unused parameters are named rather than OR'd into `app`,
        which corrupted `app`'s type for the uses right below.
    """
    assets = getattr(app.env, "embed_assets", {})
    css_files, js_files = assets.get(pagename, ((), ()))
    for css in css_files:
        app.add_css_file(css)
    for js in js_files:
        app.add_js_file(js)
