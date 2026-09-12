"""\
Kaamiki Sphinx Theme
====================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February, 2025
Last updated on: 11 September, 2026

This module serves as the primary entry point for the Kaamiki Sphinx
Theme. It is responsible for initialising the theme, configuring its
extensions and integrating with Sphinx's build process.

This module connects the theme's internal utilities and configurations
with the Sphinx application lifecycle, ensuring seamless interaction
between theme components and the final HTML output.

This theme  is registered through the `setup()` function, which
configures the theme, maps user-configurable options and binds event
hooks for post-processing and dynamic content handling.

.. versionadded:: 21.2.2025

    [1] Added native support for `sphinx.ext-opengraph` extension.

.. versionadded:: 2.3.2025

    [1] Override styles for `sphinx_design` extension by using a custom
        CSS.
    [2] Override styles for `sphinx_docsearch` extension by using a
        custom CSS (deprecated, removed in February 2026).

.. versionchanged:: 27.8.2025

    [1] Added support for `tagged` directive to overlay clickable face
        tags on images.
    [2] Added native support for injecting `last_updated` date just
        above the footer.

.. deprecated:: 19.10.2025

    [1] Use of `website_options` in favour of `html_context`. This
        removes the need of `register_website_options` function.
    [2] Custom website options are now replaced by default Sphinx's
        `html_theme_options`.

.. versionchanged:: 2.11.2025

    [1] Internals are now called Extensions, which is way more accurate
        and appropriate name for them.
    [2] The theme now registers from the `base/templates` directory
        instead of `base`, like before. This allows to make the
        development simple and easy to follow by keeping the templates
        (html/jinja2 templates) separate then the styling components.

.. versionchanged:: 14.2.2026

    [1] This theme now has a name, `Kaamiki`.
    [2] Officially dropped support for `DocSearch`.

.. versionchanged:: 31.8.2026

    [1] Replaced the `iframe` directive with a more general `embed`
        directive, capable of inline content or an external HTML
        fragment, selected by its argument rather than a `:file:`
        option.
    [2] `mypy` now runs fully strict across the theme, with the
        underlying type errors it surfaced fixed rather than silenced.

.. versionadded:: 10.9.2026

    [1] Open Graph and Twitter metadata is worked out from the doctree
        by `social_metadata` and emitted by the layout template. A
        page's own `:og:title:`, `:og:description:`, `:og:type:` and
        `:og:image:` fields win, then the defaults in `html_context`,
        then the page's opening paragraph.
    [2] The `picture` directive emits the image's real `width` and
        `height`, read off the file header, so the page stops shuffling
        about as images land.
    [3] A `show_secondary_toctree` gate, so the secondary toctree is a
        choice rather than something that turns up whenever a page
        happens to have one.

.. versionchanged:: 10.9.2026

    [1] Stylesheets are registered here in an explicit cascade order
        instead of being `@import`-ed from `theme.css`, so the browser
        fetches them in parallel rather than walking a waterfall.
        `theme.toml` no longer declares one of its own.
    [2] Every directive renders through `utils.render`, one shared Jinja
        environment with autoescaping on. Each one used to open its own
        template at import time and build a bare `jinja2.Template` with
        escaping off, so any caption, title or label carrying an `&`, a
        `<` or a stray quote quietly emitted broken markup.
    [3] Roles are registered by skipping anything whose name starts with
        an underscore, rather than handing docutils every function in
        the module.
    [4] Renamed `geist.css` to `font.css`. It has always carried both
        Geist Sans and Geist Mono, so naming it after one typeface was
        never quite right.
    [5] The logo markup lives in a `logo.html.jinja` macro shared by the
        header and the left sidebar instead of being written out twice.
        It still honours `html_logo` first and falls back to the
        `dark_logo`/`light_logo` theme options, both of which stay unset
        on my own site.

.. deprecated:: 10.9.2026

    [1] Dropped `sphinxext-opengraph`, which dragged `matplotlib` in
        purely to draw social cards.
    [2] Only the directives that emit a real node get a translator pair
        now. The rest hand back a `nodes.raw` and never reach
        `visit`/`depart`, so their placeholders were deleted rather than
        registered and never called.
    [3] The dark blocks in `code.css` were re-stating fifteen tokens
        with values identical to their light counterparts. They are
        gone; only the five that genuinely differ remain.
"""

from __future__ import annotations

import inspect
import os.path as p
import typing as t
from pathlib import Path

import docutils.parsers.rst as rst
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.fileutil import copy_asset
from sphinx.util.matching import DOTFILES

from kaamiki.extensions import directives
from kaamiki.extensions import roles
from kaamiki.extensions.utils import build_finished
from kaamiki.extensions.utils import depart
from kaamiki.extensions.utils import ensure_classes_on_nodes
from kaamiki.extensions.utils import env_before_read_docs
from kaamiki.extensions.utils import last_updated_date
from kaamiki.extensions.utils import social_metadata

if t.TYPE_CHECKING:
    import types

    import docutils.nodes as nodes
    from sphinx.application import Sphinx

logger = logging.getLogger(__name__)

version: str = "10.09.2026"
theme_name: t.Final[str] = "kaamiki"
theme_path = p.join(p.abspath(p.dirname(__file__)), "base", "templates")
supported_extensions: t.Sequence[str] = (
    "sphinx_carousel.carousel",
    "sphinx_design",
)

# Explicit cascade order. Sphinx gives `pygments.css` and any theme.toml
# stylesheet priority 200, so registering these here - rather than
# `@import`-ing them from theme.css - keeps the layering deliberate and
# lets the browser fetch them in parallel instead of in a waterfall.
stylesheets: t.Sequence[tuple[str, int]] = (
    ("font.css", 400),
    ("base.css", 500),
    ("code.css", 600),
    ("theme.css", 700),
    ("sphinx-design.css", 900),
)

unmodified = StandaloneHTMLBuilder.copy_theme_static_files


def copy_theme_static_files(
    self: StandaloneHTMLBuilder,
    context: dict[str, t.Any],
) -> None:
    """Monkey-patch `HTMLBuilder` method to add relative directory.

    .. versionadded:: 2.11.2025

        Add "relative" static (styling) directory to the theme path.
    """
    unmodified(self, context)

    def onerror(filename: str, error: Exception) -> None:
        """Display warning on file transfer."""
        msg = __("Failed to copy file in theme's 'static' directory: %s: %r")
        logger.warning(msg, filename, error)

    copy_asset(
        Path(self.theme.get_theme_dirs()[0], "../static"),
        self._static_dir,
        excluded=DOTFILES,
        context=context,
        renderer=self.templates,
        onerror=onerror,
        force=True,
    )


StandaloneHTMLBuilder.copy_theme_static_files = (  # type: ignore[method-assign]
    copy_theme_static_files
)


def fix(module: types.ModuleType) -> type[nodes.Element]:
    """Correct the `__name__` attribute of a directive's node class.

    This function updates the `__name__` attribute of a node class
    defined within a directive's module. The `__name__` attribute is
    adjusted by converting hyphenated module names into PascalCase for
    consistency with the node's class naming conventions.

    This is particularly useful when dynamically registering nodes,
    ensuring their names match Sphinx's internal expectations.

    :param module: The module containing the node class.
    :return: The node class with an updated `__name__` attribute.
    """
    node: type[nodes.Element] = module.node
    node.__name__ = "".join(_.capitalize() for _ in module.name.split("-"))
    return node


def setup(app: Sphinx) -> dict[str, str | bool]:
    """Initialise and configure the sphinx theme.

    This function serves as the main entry point for integrating the
    theme with the Sphinx application. It performs the following tasks::

        [1] Registers the theme's supported extensions.
        [2] Registers the stylesheets in an explicit cascade order,
            plus the theme's scripts.
        [3] Registers every public function in `roles` as a role,
            skipping the underscore-prefixed helpers.
        [4] Registers each directive, giving a translator pair only to
            the ones that emit a real node and letting a directive
            hook in extra nodes of its own through `register`.
        [5] Binds the event hooks for social metadata, last-updated
            stamps and the post-build HTML pass.

    :param app: The Sphinx application instance.
    :return: A dictionary indicating the theme's version and its
        compatibility with parallel read and write processes.

    .. deprecated:: 19.10.2025

        Custom website options are now replaced by default Sphinx's
        `html_theme_options`.

    .. versionchanged:: 2.11.2025

        Overridding CSS files now have slightly higher priority than
        before. It was 900 earlier, now it's 800.

    .. versionchanged:: 10.9.2026

        [1] Stylesheets come from the `stylesheets` table rather than a
            lone `add_css_file` call, so their order is stated once and
            `theme.toml` declares none of its own.
        [2] Roles are filtered by name instead of being registered
            wholesale, which had been exporting a drawing helper as a
            role.
        [3] A directive only gets `add_node` when it defines one, and a
            directive with nothing to write on the way out borrows the
            shared no-op `depart` from `utils` rather than carrying an
            empty one of its own.
        [4] A directive may expose a `register` hook to add nodes the
            loop knows nothing about.
        [5] Connects `social_metadata`, which replaces the dropped
            `sphinxext-opengraph`.
    """
    for extension in supported_extensions:
        app.setup_extension(extension)
    app.add_html_theme(theme_name, theme_path)
    for stylesheet, priority in stylesheets:
        app.add_css_file(stylesheet, priority=priority)
    app.add_js_file("base.js", loading_method="defer")
    app.add_js_file("theme.js", loading_method="defer")
    for key, value in inspect.getmembers(roles, inspect.isfunction):
        if not key.startswith("_"):
            rst.roles.register_local_role(key, value)
    for directive in directives:
        if hasattr(directive, "node"):
            node = fix(directive)
            leave = getattr(directive, "depart", depart)
            app.add_node(node, html=(directive.visit, leave))
        app.add_directive(directive.name, directive.directive)
        if hasattr(directive, "register"):
            directive.register(app)
        if hasattr(directive, "html_page_context"):
            app.connect("html-page-context", directive.html_page_context)
    app.connect("env-before-read-docs", env_before_read_docs)
    app.connect("html-page-context", social_metadata)
    app.connect("source-read", last_updated_date)
    app.connect("doctree-resolved", ensure_classes_on_nodes)
    app.connect("build-finished", build_finished)
    return {
        "version": version,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
