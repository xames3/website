"""\
Kaamiki Sphinx Theme
====================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February, 2025
Last updated on: 12 September, 2026

The theme's entry point. `setup()` registers the theme itself, its
stylesheets and scripts, its directives and roles, and the handlers
that fill in the page context and tidy the written HTML. `register()`
puts the directives and roles into docutils as this package is
imported, so they exist for builders that never ask for a theme.

A site needs nothing but `html_theme = "kaamiki"` in its `conf.py`.

.. versionadded:: 21.2.2025

    [1] Native support for the `sphinx.ext-opengraph` extension.

.. versionadded:: 2.3.2025

    [1] Custom CSS overriding the `sphinx_design` styles.
    [2] Custom CSS overriding the `sphinx_docsearch` styles
        (deprecated, removed in February 2026).

.. versionchanged:: 27.8.2025

    [1] A `tagged` directive, overlaying clickable face tags on images.
    [2] The `last_updated` date is injected above the footer.

.. deprecated:: 19.10.2025

    [1] `website_options` in favour of `html_context`, which removes
        the need for `register_website_options`.
    [2] The custom website options, in favour of Sphinx's own
        `html_theme_options`.

.. versionchanged:: 2.11.2025

    [1] The internals are called extensions, which is the more
        accurate name for them.
    [2] The theme registers from `base/templates` rather than `base`,
        which keeps the templates apart from the styling.

.. versionchanged:: 14.2.2026

    [1] The theme has a name, `Kaamiki`.
    [2] Dropped support for `DocSearch`.

.. versionchanged:: 31.8.2026

    [1] The `iframe` directive is now `embed`, which covers inline
        content and external HTML fragments and not just iframes.
    [2] `mypy` runs fully strict across the theme, with the type errors
        it surfaced fixed rather than silenced.

.. versionadded:: 10.9.2026

    [1] Open Graph and Twitter metadata is worked out from the doctree
        by `social_metadata` and written by the layout template. A
        page's own `:og:*` fields win. Without a description of its own
        a page falls back to its lead, then to the default in
        `html_context`, then to its opening paragraph.
    [2] The `picture` directive writes the image's real `width` and
        `height`, read off the file header, so the page stops shuffling
        about as images land.
    [3] A `fontawesome_kit` key. The kit URL was hardcoded in the
        layout, so every site using this theme loaded my kit off my
        quota. Leave it unset and no kit script is written.
    [4] A page longer than `show_more_after` minutes is folded down to
        one screenful, faded off at the cut, with a Show more button
        under it and a Show less to put it back. `reading_length`
        measures the page from the doctree, so the fold is in the
        markup before the browser paints. Code, tables, figures and
        admonitions are left out of the count.
        `show_show_more: False` in `html_context` turns it off, and a
        browser with scripting off never sees a fold.
    [5] Font Awesome classes and the project details have theme
        defaults, merged into `html_context` as the builder starts.
        Templates read `fa_icons` and `project` directly, so a site
        that set neither used to fail the build.

.. versionchanged:: 10.9.2026

    [1] Stylesheets are registered here in a stated cascade order
        instead of being `@import`-ed from `theme.css`, so the browser
        fetches them in parallel rather than walking a waterfall.
    [2] Every directive renders through `utils.render`, one shared
        Jinja environment with autoescaping on. Each one used to build
        a bare `jinja2.Template` at import time with escaping off, so
        any caption or title carrying an `&`, a `<` or a stray quote
        emitted broken markup.
    [3] Roles are registered by skipping anything whose name starts
        with an underscore, rather than handing docutils every
        function in the module.
    [4] Renamed `geist.css` to `font.css`. It has always carried both
        Geist Sans and Geist Mono.
    [5] The logo markup lives in a `logo.html.jinja` macro shared by
        the header and the sidebar instead of being written out twice.
        It still honours `html_logo` first and falls back to the
        `dark_logo`/`light_logo` theme options.
    [6] The stylesheets carry no explanatory comments any more, only
        the device-view markers, and reference the `--km-color-*`
        tokens directly rather than repeating a fallback triplet at
        every use.
    [7] The cal.com embed initialises whatever namespaces it finds on
        the page instead of one hardcoded name, so a site with no
        booking buttons never pulls the embed script.
    [8] The `preconnect` to jsdelivr is gone. MathJax was the only
        thing using it, and it only loads on pages carrying maths.
    [9] `left_sidebar.html.jinja` is now `sidebar.html.jinja`, its
        block is `sidebar` and the element it renders is `#sidebar`.
        There is one rail left, and on a phone it arrives as a drawer,
        so naming it after a side was wrong at every width.
    [10] The sidebar renders only when `html_sidebars` leaves
         something to render, which is the condition the menu toggle
         and the backdrop already went by. Emptying it used to leave a
         drawer nothing could open and a column reserved for it.
    [11] The reading time is written out by the `author` directive
         rather than counted in the browser. Two counts of the same
         page did not always agree.
    [12] `SOCIAL_SKIP` in `utils` is now `FURNITURE`, since the
         reading-time count uses the same list.
    [13] `supported_extensions` names `sphinx_copybutton` alongside
         `sphinx_design`. The theme styles `button.copybtn` and
         `.o-tooltip--left`, neither of which exists without it, so it
         was a dependency the theme had without declaring.
         `sphinx_carousel` went the other way, out with the last page
         that used it.
    [14] `config_init` adds those to `config.extensions` as the
         configuration is built, so a site using the theme never names
         them. `setup()` still asks for them too, which covers a
         `conf.py` that does not import `kaamiki` at all: the HTML
         builders get them either way.
    [15] The directives and roles are registered as this package is
         imported, not only when an HTML builder asks for the theme.
         Sphinx calls a theme's `setup()` only for the builders that
         want a theme, so under `linkcheck` every `thumbnail`,
         `author` and `picture` in the sources was an unknown
         directive whose content was dropped before the link checker
         saw it.
    [16] The theme writes a 404 page to the top of the output tree,
         which is the file a static host serves for an address it
         cannot find. It is a normal theme template, so it carries the
         header, the footer and the colour modes. Set `show_404` to
         `False` in `html_context` to write nothing.

.. deprecated:: 10.9.2026

    [1] Dropped `sphinxext-opengraph`, which dragged `matplotlib` in
        purely to draw social cards.
    [2] Only the directives that emit a real node get a translator
        pair. The rest hand back a `nodes.raw` and never reach
        `visit`/`depart`, so their placeholders were deleted rather
        than registered and never called.
    [3] The dark blocks in `code.css` were re-stating fifteen tokens
        with values identical to their light counterparts. Only the
        five that genuinely differ remain.
    [4] Three rules in `theme.css` were sitting there four times over,
        byte for byte. Kept one of each.
    [5] `env-before-read-docs` is no longer connected, since the
        post-processing no longer works off the re-read list.
    [6] The "On this page" secondary toctree is gone entirely, along
        with `right_sidebar.html.jinja`, the scrollspy that lit up its
        links, the `.toc-active` styling and the
        `secondary_toctree_title` option. It reserved a grid column and
        painted nothing, on every width, and nothing had ever rendered
        it in the first place. `layout.html` keeps an empty `aside`
        block so `genindex` can still hang its "Jump to letter" rail
        there, which is what the remaining `.site-sidebar--alpha`
        styling is for.
"""

from __future__ import annotations

import inspect
import os.path as p
import typing as t
from pathlib import Path

import docutils.parsers.rst as rst
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.config import Config
from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.fileutil import copy_asset
from sphinx.util.matching import DOTFILES

from kaamiki.extensions import directives
from kaamiki.extensions import roles
from kaamiki.extensions.utils import build_finished
from kaamiki.extensions.utils import context_defaults
from kaamiki.extensions.utils import depart
from kaamiki.extensions.utils import ensure_classes_on_nodes
from kaamiki.extensions.utils import last_updated_date
from kaamiki.extensions.utils import reading_length
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
    "sphinx_copybutton",
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

unmodified_config = Config.__init__


def config_init(
    self: Config,
    config: dict[str, t.Any] | None = None,
    overrides: dict[str, t.Any] | None = None,
) -> None:
    """Add the theme's own extensions to the ones the site asked for.

    Sphinx loads `config.extensions` for every builder, but calls a
    theme's `setup()` only for the builders that want a theme. Naming
    `sphinx_design` in `conf.py` is therefore the only way a
    `linkcheck` or `gettext` build sees a `grid` or a `:fas:`, and
    that is the site writing out a dependency of the theme's.

    `Config` is built from the `conf.py` namespace once that file has
    run, so a `conf.py` that imports `kaamiki` has this patch in place
    before Sphinx reads the list.

    :param self: The configuration being built.
    :param config: The `conf.py` namespace.
    :param overrides: Values given on the command line.

    .. versionadded:: 10.9.2026
    """
    unmodified_config(self, config, overrides)
    for extension in supported_extensions:
        if extension not in self.extensions:
            self.extensions.append(extension)


Config.__init__ = config_init  # type: ignore[method-assign]

unmodified = StandaloneHTMLBuilder.copy_theme_static_files


def copy_theme_static_files(
    self: StandaloneHTMLBuilder,
    context: dict[str, t.Any],
) -> None:
    """Copy the theme's `static` directory as well as its own.

    The templates live in `base/templates`, so Sphinx copies the static
    files from there. The stylesheets and scripts sit beside it in
    `base/static`, which this fetches too.

    :param self: The HTML builder, as this replaces one of its methods.
    :param context: The values the static files are rendered with.

    .. versionadded:: 2.11.2025
    """
    unmodified(self, context)

    def onerror(filename: str, error: Exception) -> None:
        """Warn about a file that would not copy.

        :param filename: The file that failed.
        :param error: Why it failed.
        """
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
    """Name a directive's node class after the directive.

    Every module calls its node class `node`, which is no use to Sphinx
    when it comes to register them. This renames the class to the
    directive's own name in PascalCase.

    :param module: The directive's module.
    :return: Its node class, renamed.
    """
    node: type[nodes.Element] = module.node
    node.__name__ = "".join(_.capitalize() for _ in module.name.split("-"))
    return node


def register() -> None:
    """Register the theme's directives and roles with docutils.

    Sphinx calls a theme's `setup()` only when a builder asks for the
    theme by name, and none but the HTML builders do. Under `linkcheck`
    the directives did not exist at all, so every use of one was an
    unknown directive whose content was dropped.

    Only functions written in `roles` are registered. Filtering on the
    leading underscore alone let the module's own imports through, so
    `escape`, `findall` and `quote` were roles too, each of which would
    have raised on the first use.

    This runs as the package is imported, which covers every builder.
    `setup()` registers them again through the application so Sphinx
    keeps its own record.
    """
    for key, value in inspect.getmembers(roles, inspect.isfunction):
        if key.startswith("_") or value.__module__ != roles.__name__:
            continue
        rst.roles.register_local_role(key, value)
    for directive in directives:
        rst.directives.register_directive(directive.name, directive.directive)


def setup(app: Sphinx) -> dict[str, str | bool]:
    """Set the theme up with Sphinx.

    Registers the theme and the extensions it relies on, its
    stylesheets in a stated cascade order, its scripts, its directives
    and roles, and the handlers that fill in the page context and tidy
    the written HTML.

    :param app: The Sphinx application instance.
    :return: The theme's version, and that it is safe to read and write
        in parallel.

    .. deprecated:: 19.10.2025

        The custom website options, in favour of Sphinx's own
        `html_theme_options`.

    .. versionchanged:: 2.11.2025

        The overriding CSS files sit at priority 800 rather than 900.

    .. versionchanged:: 10.9.2026

        [1] Stylesheets come from the `stylesheets` table rather than a
            lone `add_css_file` call, so their order is stated once and
            `theme.toml` declares none of its own.
        [2] Roles are filtered by name instead of being registered
            wholesale, which had been exporting a drawing helper as a
            role.
        [3] A directive only gets `add_node` when it defines one, and
            one with nothing to write on the way out borrows the shared
            no-op `depart` from `utils`.
        [4] A directive may expose a `register` hook to add nodes the
            loop knows nothing about.
        [5] Connects `social_metadata`, which replaces the dropped
            `sphinxext-opengraph`.
        [6] Connects `reading_length`, which works out how long a page
            takes to read and whether it should be folded up.
        [7] Connects `context_defaults`, so the templates always have
            a `fa_icons` and a `project` to read.
        [8] Calls `register()`, which has already run on import, so
            Sphinx keeps its own record of the directives too.
    """
    for extension in supported_extensions:
        app.setup_extension(extension)
    app.add_html_theme(theme_name, theme_path)
    for stylesheet, priority in stylesheets:
        app.add_css_file(stylesheet, priority=priority)
    app.add_js_file("base.js", loading_method="defer")
    app.add_js_file("theme.js", loading_method="defer")
    register()
    for directive in directives:
        if hasattr(directive, "node"):
            node = fix(directive)
            leave = getattr(directive, "depart", depart)
            app.add_node(node, html=(directive.visit, leave))
        app.add_directive(directive.name, directive.directive, override=True)
        if hasattr(directive, "register"):
            directive.register(app)
        if hasattr(directive, "html_page_context"):
            app.connect("html-page-context", directive.html_page_context)
    app.connect("builder-inited", context_defaults)
    app.connect("html-page-context", social_metadata)
    app.connect("html-page-context", reading_length)
    app.connect("source-read", last_updated_date)
    app.connect("doctree-resolved", ensure_classes_on_nodes)
    app.connect("build-finished", build_finished)
    return {
        "version": version,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


register()
