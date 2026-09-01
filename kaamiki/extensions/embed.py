"""\
Embed Directive
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 11 August, 2026
Last updated on: 31 August, 2026

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
"""

from __future__ import annotations

import ast
import contextlib
import os.path as p
import re
import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "embed"
pattern: t.Pattern[str] = re.compile(
    r"^[ \t]*:([\w-]+):[ \t]*(.*?)(?=^[ \t]*:[\w-]+:|\Z)",
    re.MULTILINE | re.DOTALL,
)


class node(nodes.Element):
    """Class to represent a custom node in the document tree.

    This class extends the `nodes.Element` from `docutils`, serving as
    the container for the parsed information. The node will ultimately
    be transformed into HTML or other output formats by the relevant
    Sphinx translators.
    """


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
        values: dict[str, str] = {}
        for key, value in self.options.items():
            if key in {"encoding", "css", "js"}:
                continue
            values[key] = str(value)
        rendered = source
        for key, value in values.items():
            rendered = rendered.replace(f"{{{{ {key} }}}}", value)
            rendered = rendered.replace(f"{{{{{key}}}}}", value)
            normalised = key.replace("-", "_")
            if normalised != key:
                rendered = rendered.replace(f"{{{{ {normalised} }}}}", value)
                rendered = rendered.replace(f"{{{{{normalised}}}}}", value)
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


def visit(self: HTMLTranslator, node: node) -> None:
    """Handle the entry processing of the `embed` node during HTML
    generation.

    This method is called when the HTML translator encounters the
    `embed` node in the document tree. It retrieves the relevant
    attributes from the node (if any) and uses Jinja2 templating to
    produce the final HTML output. Since the `embed` node does not
    require any actions, the method currently acts as a placeholder.

    :param self: The HTML translator instance.
    :param node: The `embed` node being processed.
    """


def depart(self: HTMLTranslator, node: node) -> None:
    """Handle the exit processing of the `embed` node during HTML
    generation.

    This method is invoked after the node's HTML representation has been
    fully processed and added to the output. Since the `embed` node
    does not require any closing actions, the method currently acts as a
    placeholder.

    :param self: The HTML translator instance.
    :param node: The `embed` node being processed.
    """


def html_page_context(
    app: Sphinx,
    pagename: str,
    _templatename: str,
    _context: dict[str, t.Any],
    _doctree: nodes.document | None,
) -> None:
    """Attach an `embed` embed's `:css:`/`:js:` assets to its page.

    Only pages containing an `embed` directive that declared static
    assets get them attached, keeping unrelated pages free of unused
    stylesheets and scripts.

    :param app: The Sphinx application instance.
    :param pagename: The name of the page currently being rendered.
    :param _templatename: The template used for the page (unused).
    :param _context: The Jinja2 rendering context (unused).
    :param _doctree: The doctree for the page, or `None` for pages
        without one (unused).

    .. versionchanged:: 31.8.2026

        The unused parameters are now prefixed with `_` instead of
        being OR'd into `app`, which corrupted `app`'s type for the
        `app.env`/`app.add_css_file()` uses right below.
    """
    assets = getattr(app.env, "embed_assets", {})
    css_files, js_files = assets.get(pagename, ((), ()))
    for css in css_files:
        app.add_css_file(css)
    for js in js_files:
        app.add_js_file(js)
