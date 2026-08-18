"""\
iFrame Directive
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 11 August, 2026
Last updated on: 18 August, 2026

This module defines a custom `iframe` directive for the Kaamiki Sphinx
Theme. The directive allows adding an (optionally) customisable iframe
directly within the document.

The `iframe` directive can be used in reStructuredText documents as
follows::

    .. code-block:: rst

        .. iframe::
            :expected-count: 10

            <iframe
                src="https://example.com"
                width="100%"
                height="400px"
                data-expected-count="{{ expected-count }}">
            </iframe>

To keep large embeds out of the page's own reST source, the directive
also accepts a `:file:` option pointing at an external HTML fragment.
That fragment may in turn need its own CSS and/or JavaScript. Rather
than inlining `<style>`/`<script>` tags in the fragment, list the
static filenames (relative to `html_static_path`) via `:css:` and
`:js:`, comma-separated. They are only attached to pages that actually
use the directive, via Sphinx's `html-page-context` event::

    .. code-block:: rst

        .. iframe::
            :file: ../assets/html/widget.html
            :css: widget.css
            :js: widget.js
"""

from __future__ import annotations

import os.path as p
import typing as t
from pathlib import Path

import docutils.nodes as nodes
import docutils.parsers.rst as rst

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "iframe"


class _option_spec(dict[str, t.Callable[[str], t.Any]]):
    """Custom option specs that allow arbitrary option names while
    still giving special parsing for `:file:` and `:encoding:`.
    """

    def __contains__(self, key: object) -> bool:
        """Returns `True` if the key is in the specs, else `False`."""
        return isinstance(key, str)

    def __bool__(self) -> bool:
        """Force option parsing to stay enabled."""
        return True

    def __getitem__(self, key: str) -> t.Callable[[str], t.Any]:
        """Return appropriate directive type."""
        if key == "file":
            return rst.directives.path
        if key == "encoding":
            return rst.directives.encoding
        return rst.directives.unchanged


class node(nodes.Element):
    """Class to represent a custom node in the document tree.

    This class extends the `nodes.Element` from `docutils`, serving as
    the container for the parsed information. The node will ultimately
    be transformed into HTML or other output formats by the relevant
    Sphinx translators.
    """


class directive(rst.Directive):
    """Custom `iframe` directive for reStructuredText.

    This class defines the behaviour of the `iframe` directive,
    including
    how it processes options and content and how it generates nodes to
    be inserted into the document tree.
    """

    has_content = True
    required_arguments = 0
    option_spec = _option_spec()

    def run(self) -> list[nodes.Node]:
        """Parse directive options and create an `iframe` node.

        This method gathers all options provided by the user (if any)
        in the `iframe` directive, constructs a new `node` instance and
        returns it wrapped in a list.

        The returned node is then placed into the document tree at the
        directive's location. Further processing will convert the node
        into HTML or other formats.

        :return: A list containing a single `node` self.
        """
        file = "file" in self.options
        inline = bool(self.content)
        if file and inline:
            raise self.error("iframe can't use both file and inline content")
        if not file and not inline:
            raise self.error("iframe requires an inline HTML content or file")
        source = "\n".join(self.content)
        if file:
            path = Path(self.options["file"])
            if not path.is_absolute():
                here = Path(self.state.document.current_source).parent
                path = (here / path).resolve()
            if not path.is_file():
                raise self.error(f"iframe error, file not found: {path!r}")
            dependencies = self.state.document.settings.record_dependencies
            if dependencies is not None:
                dependencies.add(p.abspath(str(path)))
            encoding = self.options.get("encoding", "utf-8")
            source = path.read_text(encoding=encoding)
        values: dict[str, str] = {}
        for key, value in self.options.items():
            if key in {"file", "encoding", "css", "js"}:
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
        page_assets = env.iframe_page_assets = getattr(
            env, "iframe_page_assets", {}
        )
        css_files, js_files = page_assets.setdefault(docname, (set(), set()))
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
    """Handle the entry processing of the `iframe` node during HTML
    generation.

    This method is called when the HTML translator encounters the
    `iframe` node in the document tree. It retrieves the relevant
    attributes from the node (if any) and uses Jinja2 templating to
    produce the final HTML output. Since the `iframe` node does not
    require any actions, the method currently acts as a placeholder.

    :param self: The HTML translator instance.
    :param node: The `iframe` node being processed.
    """


def depart(self: HTMLTranslator, node: node) -> None:
    """Handle the exit processing of the `iframe` node during HTML
    generation.

    This method is invoked after the node's HTML representation has been
    fully processed and added to the output. Since the `iframe` node
    does not require any closing actions, the method currently acts as a
    placeholder.

    :param self: The HTML translator instance.
    :param node: The `iframe` node being processed.
    """


def html_page_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Attach an `iframe` embed's `:css:`/`:js:` assets to its page.

    Only pages containing an `iframe` directive that declared static
    assets get them attached, keeping unrelated pages free of unused
    stylesheets and scripts.

    :param app: The Sphinx application instance.
    :param pagename: The name of the page currently being rendered.
    :param templatename: The template used for the page (unused).
    :param context: The Jinja2 rendering context (unused).
    :param doctree: The doctree for the page, or `None` for pages
        without one (unused).
    """
    app = app or templatename or context or doctree
    page_assets = getattr(app.env, "iframe_page_assets", {})
    css_files, js_files = page_assets.get(pagename, ((), ()))
    for css in css_files:
        app.add_css_file(css)
    for js in js_files:
        app.add_js_file(js)
