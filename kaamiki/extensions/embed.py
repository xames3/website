"""\
Embed Directive
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 11 August 2026
Last updated on: 09 October, 2026

An `embed` directive that drops a block of HTML into the page.

    .. embed:: iframe
       :expected-count: 10

       <iframe
           src="https://example.com"
           width="100%"
           height="400px"
           data-expected-count="{{ expected-count }}">
       </iframe>

Every other option is a placeholder, so `{{ expected-count }}` is
replaced by the option's value, escaped for where it lands.

A larger embed can live in a file of its own, named as the argument,
relative to the document or to the source directory with a leading `/`.
The `:css:` and `:js:` options are for the files under
`html_static_path`, which load in order on the pages that use the
directive::

    .. embed:: ../assets/html/embed.html
       :css: embed.css
       :js: embed.js
"""

from __future__ import annotations

import ast
import contextlib
import json
import re
import typing as t
from html import escape
from html import unescape
from urllib.parse import urlsplit

import docutils.nodes as nodes
import docutils.parsers.rst as rst
from sphinx.util import logging

from kaamiki.extensions.utils import findall
from kaamiki.extensions.utils import hostnames
from kaamiki.extensions.utils import listed
from kaamiki.extensions.utils import setting

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
# NOTE(xames3): Keeps a value from closing its `<script>` early and
# U+2028/2029 from ending a JavaScript string line.
# https://html.spec.whatwg.org/multipage/scripting.html#restrictions-for-contents-of-script-elements
# https://github.com/tc39/proposal-json-superset
ESCAPES: dict[str, str] = {
    "<": "\\u003c",
    ">": "\\u003e",
    "&": "\\u0026",
    "\u2028": "\\u2028",
    "\u2029": "\\u2029",
}
STYLE_ESCAPES: frozenset[str] = frozenset("<>&\"'\\\n\r{};")
ASSETS: t.Final[frozenset[str]] = frozenset({"css", "js", "encoding"})
LOADING: t.Final[tuple[str, ...]] = ("defer", "async", "normal")
IFRAME: t.Pattern[str] = re.compile(
    r"<iframe\b[^>]*?\bsrc\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))",
    re.IGNORECASE,
)


def encode(value: str, kind: str) -> str:
    """Write a placeholder's value for where it sits.

    :param value: The option's value, as written.
    :param kind: `script`, `style` or anything else for markup.
    :return: The value, escaped so it can't break out of its place.
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

    Markup, `<script>` and `<style>` want different escaping, so the
    source is split on its script and style blocks and each part gets
    its own.

    :param source: The fragment, placeholders and all.
    :param values: Directive options, keyed as they're written in the
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


class directive(rst.Directive):
    """The `embed` directive.

    The argument is `iframe`, with the markup as content or the path to
    an HTML fragment. Every option but `encoding`, `css` and `js` is a
    placeholder value.
    """

    has_content = True
    required_arguments = 1
    # HACK(xames3): No `option_spec` is declared, so docutils hands the
    # options over inside the argument and `run` reads them back out.
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
        self.guard(attributes["text"])
        attributes["format"] = "html"
        attributes["css"] = listed(self.options.get("css"))
        attributes["js"] = listed(self.options.get("js"))
        return [nodes.raw(**attributes)]

    def check(self, source: str, values: dict[str, str]) -> None:
        """Catch an option or a placeholder that has been misspelt.

        An option the fragment never asks for is an error. A
        placeholder no option fills only warns, since it may be meant.

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

    def guard(self, markup: str) -> None:
        """Keep an `<iframe>` to the hosts the site allows.

        Nothing is checked without `embed_iframe_hosts`. With it, a
        source on a relative path is allowed and one from another host
        has to be on the list, or on a subdomain of a host that is.

        :param markup: The embedded HTML, placeholders filled in.
        :raises rst.DirectiveError: When an iframe comes from a host
            that isn't allowed.
        """
        config = self.state.document.settings.env.config
        allowed = hostnames(setting(config, "embed_iframe_hosts"), www=True)
        if not allowed:
            return
        for match in IFRAME.finditer(markup):
            src = unescape(next(_ for _ in match.groups() if _ is not None))
            try:
                parts = urlsplit(src.strip())
                host = parts.hostname or ""
            except ValueError:
                parts, host = urlsplit(""), "?"
            if parts.scheme.lower() in {"", "http", "https"}:
                if not parts.netloc and host != "?":
                    continue
                if any(host == _ or host.endswith(f".{_}") for _ in allowed):
                    continue
            raise self.error(
                f"embed has an iframe from {src!r}, which embed_iframe_hosts"
                f" does not allow; it allows {', '.join(sorted(allowed))}"
            )

    def read(self, file: str) -> str:
        """Read an HTML fragment off disk.

        The path is relative to the document or to the source directory
        when it starts with a `/`.

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

    The site's `embed_css` and `embed_js` come first, then the page's
    own in the order it names them, each once. Pages without an `embed`
    don't get any.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context.
    :param doctree: The resolved doctree or `None` for generated
        pages.
    """
    del pagename, templatename, context
    if doctree is None:
        return
    embeds = [_ for _ in findall(doctree, nodes.raw) if "css" in _]
    if not embeds:
        return
    css = dict.fromkeys(listed(setting(app.config, "embed_css")))
    js = dict.fromkeys(listed(setting(app.config, "embed_js")))
    for raw in embeds:
        css.update(dict.fromkeys(raw.get("css", ())))
        js.update(dict.fromkeys(raw.get("js", ())))
    loading = setting(app.config, "embed_js_loading")
    if loading not in LOADING:
        logger.warning(
            "embed_js_loading takes %s, got %r; using defer",
            ", ".join(LOADING),
            loading,
            type="embed",
        )
        loading = "defer"
    for filename in css:
        app.add_css_file(filename)
    for filename in js:
        app.add_js_file(
            filename, loading_method=None if loading == "normal" else loading
        )
