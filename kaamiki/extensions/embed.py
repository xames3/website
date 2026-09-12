"""\
Embed Directive
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 11 August, 2026
Last updated on: 12 September, 2026

This module defines a custom `embed` directive for the Kaamiki Sphinx
Theme. The directive allows including/embedding an HTML page (embed) or
an iframe directly within the document.

The `embed` directive can be used in reStructuredText documents as
follows::

    .. code-block:: rst

        .. embed:: iframe
            :expected-count: 10

            <iframe
                src="https://example.com"
                width="100%"
                height="400px"
                data-expected-count="{{ expected-count }}">
            </iframe>

To keep large embeds out of the page's own rST source, the directive
also accepts an external HTML fragment as an (optional) input. That
fragment may in turn need its own CSS and/or JavaScript. Rather than
inlining `<style>`/`<script>` tags in the fragment, list the static
filenames (relative to `html_static_path`) via `:css:` and `:js:`,
comma-separated. They are only attached to pages that actually use the
directive, via Sphinx's `html-page-context` event::

    .. code-block:: rst

        .. embed:: ../assets/html/embed.html
            :css: embed.css
            :js: embed.js

.. versionchanged:: 31.8.2026

    [1] Renamed from `iframe` to `embed`, since the directive covers
        inline content and external HTML fragments, not just iframes.
    [2] The `:file:` option is gone; the directive's argument is now
        either `iframe` (inline content) or the fragment's path.
    [3] Options may now span multiple lines, so a single `:option:`
        value (an array, a long string) can be written across several
        indented lines instead of one.

.. versionadded:: 10.9.2026

    `substitute` fills a fragment's placeholders with escaping picked
    for where each one sits. A value going into an attribute gets its
    quotes and brackets escaped; one going into a `<script>` is JSON-
    encoded, with `<`, `>` and `&` written as escape sequences so a
    value can't close the block it lives in. Before this the
    substitution was a plain string replace, which meant a fragment was
    only ever as safe as the options handed to it.

.. deprecated:: 10.9.2026

    Dropped the `node` class and the `visit`/`depart` pair. This
    directive hands back a `nodes.raw` and never goes anywhere near a
    translator, so all three were dead weight that only existed to keep
    the registration loop happy.
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
    """Fill a fragment's placeholders, escaping for where each sits.

    A fragment mixes markup and script, and the two want opposite
    things. A value dropped into an attribute has to have its quotes
    and angle brackets escaped or it closes the attribute early; the
    same treatment inside a `<script>` turns a perfectly good array
    into `[&quot;a&quot;]` and breaks the page. So the source is split
    on its script and style blocks and each side gets what it needs,
    HTML escaping out here, JSON in there.

    :param source: The fragment, placeholders and all.
    :param values: Directive options, keyed as they are written in the
        rST. A placeholder may spell them with underscores instead of
        hyphens.
    :return: The fragment with every known placeholder filled in.
        Anything unrecognised is left alone.

    .. versionadded:: 12.9.2026
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
    """Custom `embed` directive for reStructuredText.

    This class defines the behaviour of the `embed` directive,
    including
    how it processes options and content and how it generates nodes to
    be inserted into the document tree.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True

    def run(self) -> list[nodes.Node]:
        """Parse directive options and create an `embed` node.

        This method gathers all options provided by the user (if any)
        in the `embed` directive, constructs a new `node` instance and
        returns it wrapped in a list.

        The returned node is then placed into the document tree at the
        directive's location. Further processing will convert the node
        into HTML or other formats.

        :return: A list containing a single `node` self.

        .. versionchanged:: 31.8.2026

            Replaces the old `:file:` option: the directive's single
            argument is now either `iframe` (inline content) or the
            fragment's path. Options are parsed from that same argument
            with a regex, so a value (an array, say) may now span
            multiple indented lines instead of just one.
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
    """Attach an `embed` embed's `:css:`/`:js:` assets to its page.

    Only pages containing an `embed` directive that declared static
    assets get them attached, keeping unrelated pages free of unused
    stylesheets and scripts.

    :param app: The Sphinx application instance.
    :param pagename: The name of the page currently being rendered.
    :param templatename: The template used for the page (unused).
    :param context: The Jinja2 rendering context (unused).
    :param doctree: The doctree for the page, or `None` for pages
        without one (unused).

    .. versionchanged:: 31.8.2026

        The unused parameters are now prefixed with `_` instead of being
        OR'd into `app`, which corrupted `app`'s type for the
        `app.env`/`app.add_css_file()` uses right below.
    """
    assets = getattr(app.env, "embed_assets", {})
    css_files, js_files = assets.get(pagename, ((), ()))
    for css in css_files:
        app.add_css_file(css)
    for js in js_files:
        app.add_js_file(js)
