"""\
Kaamiki Sphinx Theme
====================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February, 2025
Last updated on: 30 September, 2026

The theme's entry point. `setup()` registers the theme itself, its
directives and roles and the handlers that fill in the page context
and tidy the written HTML.
"""

from __future__ import annotations

import filecmp
import inspect
import os.path as p
import re
import typing as t

import docutils.nodes as nodes
import lightningcss
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util import logging

from kaamiki.extensions import directives
from kaamiki.extensions import roles
from kaamiki.extensions import writer
from kaamiki.extensions.utils import bridge
from kaamiki.extensions.utils import build_finished
from kaamiki.extensions.utils import context_defaults
from kaamiki.extensions.utils import depart
from kaamiki.extensions.utils import design_assets
from kaamiki.extensions.utils import feedback
from kaamiki.extensions.utils import provenance
from kaamiki.extensions.utils import reading_length
from kaamiki.extensions.utils import skip
from kaamiki.extensions.utils import social_metadata
from kaamiki.extensions.utils import themed

if t.TYPE_CHECKING:
    import types

    from sphinx.application import Sphinx

version: str = "2026.10.5"
theme_name: t.Final[str] = "kaamiki"
theme_path = p.join(p.abspath(p.dirname(__file__)), "base", "templates")
static_path = p.join(p.abspath(p.dirname(__file__)), "base", "static")
supported_extensions: t.Sequence[str] = (
    "sphinx_copybutton",
    "sphinx_design",
)
# Explicit cascade order.
stylesheets: t.Sequence[tuple[str, int]] = (
    ("font.css", 400),
    ("code.css", 600),
    ("theme.css", 700),
    ("sphinx-design.css", 900),
)
scripts: t.Sequence[str] = ("theme.js",)
browsers: t.Sequence[str] = (
    "chrome >= 100",
    "edge >= 100",
    "firefox >= 100",
    "ios_saf >= 15",
    "opera >= 86",
    "safari >= 15",
    "samsung >= 16",
)
negated: re.Pattern[str] = re.compile(r"@media not \(")
logger = logging.getLogger(__name__)


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


def builder_inited(app: Sphinx) -> None:
    """Hand the theme's static files, stylesheets and scripts over.

    Only an HTML builder writing pages with this theme or with one
    built on it, gets them, so a site loading `kaamiki` for its
    directives under another theme keeps that theme's look.

    :param app: The Sphinx application instance.
    """
    if not isinstance(app.builder, StandaloneHTMLBuilder):
        return
    if not themed(app.builder):
        return
    app.add_static_dir(static_path)
    for stylesheet, priority in stylesheets:
        app.add_css_file(stylesheet, priority=priority)
    for script in scripts:
        app.add_js_file(script, loading_method="defer")


def flatten(app: Sphinx, exc: Exception | None) -> None:
    """Rewrite the theme's stylesheets for browsers a few years back.

    The stylesheets are written with nesting and range media queries,
    which Safari before 16.4 drops whole, leaving an older iPhone with
    no layout to speak of. `lightningcss` flattens the copies in
    `_static` for the `browsers` listed, prefixes what those need
    prefixing and minifies them and the sources stay as they are.

    It writes a negated media query as `not (min-width: ...)`, which
    only the newer grammar reads, so those become the older
    `not all and (min-width: ...)`, which means the same thing to both.

    A stylesheet a site put over one of the theme's through
    `html_static_path` is left alone.

    :param app: The Sphinx application instance.
    :param exc: Whatever went wrong during the build or `None`.
    """
    builder = app.builder
    if exc or not isinstance(builder, StandaloneHTMLBuilder):
        return
    if not themed(builder):
        return
    for stylesheet, _ in stylesheets:
        source = p.join(static_path, stylesheet)
        target = p.join(app.outdir, "_static", stylesheet)
        if not p.isfile(target) or not filecmp.cmp(source, target, False):
            continue
        with open(source, encoding="utf-8") as f:
            text = f.read()
        try:
            css = lightningcss.process_stylesheet(
                text,
                filename=stylesheet,
                browsers_list=list(browsers),
                minify=True,
            )
        except ValueError as error:
            logger.warning(
                "could not flatten %s: %s", stylesheet, error, type="kaamiki"
            )
            continue
        with open(target, "w", encoding="utf-8") as f:
            f.write(negated.sub("@media not all and (", css))


def setup(app: Sphinx) -> dict[str, str | bool | int]:
    """Set the theme up with Sphinx.

    Registers the theme and the extensions it relies on, its directives
    and roles and the handlers that fill in the page context and tidy
    the written HTML. `builder_inited` hands the stylesheets and scripts
    over once the builder is known.

    :param app: The Sphinx application instance.
    :return: The theme's version and that it is safe to read and write
        in parallel.
    """
    for extension in supported_extensions:
        app.setup_extension(extension)
    app.add_html_theme(theme_name, theme_path)
    for key, value in inspect.getmembers(roles, inspect.isfunction):
        if key.startswith("_") or value.__module__ != roles.__name__:
            continue
        app.add_role(key, value)
    app.add_node(roles.ink, html=(roles._visit, roles._depart))
    for directive in directives:
        if hasattr(directive, "node"):
            node = fix(directive)
            html = (directive.visit, getattr(directive, "depart", depart))
            if node.__bases__ == (nodes.Element,):
                away = (skip, None)
                app.add_node(
                    node,
                    html=html,
                    latex=away,
                    man=away,
                    texinfo=away,
                    text=away,
                )
            else:
                app.add_node(node, html=html)
        app.add_directive(directive.name, directive.directive)
        if hasattr(directive, "register"):
            directive.register(app)
        if hasattr(directive, "html_page_context"):
            app.connect("html-page-context", directive.html_page_context)
    app.connect("builder-inited", builder_inited)
    app.connect("builder-inited", context_defaults)
    app.connect("builder-inited", bridge)
    app.connect("builder-inited", writer.install)
    app.connect("html-page-context", social_metadata)
    app.connect("html-page-context", reading_length)
    app.connect("html-page-context", feedback)
    app.connect("html-page-context", design_assets)
    app.connect("source-read", provenance)
    app.connect("build-finished", build_finished)
    app.connect("build-finished", flatten)
    year, month, day = map(int, version.split("."))
    return {
        "version": version,
        "env_version": year * 10000 + month * 100 + day,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
