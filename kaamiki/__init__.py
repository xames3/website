"""\
Kaamiki Sphinx Theme
====================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February 2025
Last updated on: 09 October, 2026

Kaamiki's entry point.
"""

from __future__ import annotations

import filecmp
import inspect
import os.path as p
import re
import typing as t

import docutils.nodes as nodes
import lightningcss
from sphinx import locale
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util import logging

from kaamiki.extensions import directives
from kaamiki.extensions import roles
from kaamiki.extensions.utils import bridge
from kaamiki.extensions.utils import build_finished
from kaamiki.extensions.utils import context_defaults
from kaamiki.extensions.utils import depart
from kaamiki.extensions.utils import design_assets
from kaamiki.extensions.utils import feedback
from kaamiki.extensions.utils import offer
from kaamiki.extensions.utils import page_switches
from kaamiki.extensions.utils import provenance
from kaamiki.extensions.utils import reading_length
from kaamiki.extensions.utils import reread
from kaamiki.extensions.utils import skip
from kaamiki.extensions.utils import social_metadata
from kaamiki.extensions.utils import themed
from kaamiki.extensions.utils import updated_on
from kaamiki.extensions.utils import writer

if t.TYPE_CHECKING:
    import types

    from sphinx.application import Sphinx

version: str = "2026.10.8"
theme_name: t.Final[str] = "kaamiki"
theme_path = p.join(p.abspath(p.dirname(__file__)), "base", "templates")
static_path = p.join(p.abspath(p.dirname(__file__)), "base", "static")
locale_path = p.join(p.abspath(p.dirname(__file__)), "locale")
supported_extensions: t.Sequence[str] = (
    "sphinx_copybutton",
    "sphinx_design",
)
# NOTE(xames3): This is an explicit cascade order and needs to be
# respected in order to ensure the theme loads its UI elements in an
# expected manner.
stylesheets: t.Sequence[tuple[str, int]] = (
    ("font.css", 400),
    ("code.css", 600),
    ("theme.css", 700),
    ("sphinx-design.css", 900),
)
scripts: t.Sequence[str] = ("theme.js",)
# Proper list available here:
# https://web-platform-dx.github.io/supported-browsers/
browsers: t.Sequence[str] = (
    "chrome >= 100",
    "edge >= 100",
    "firefox >= 100",
    "ios_saf >= 15",
    "opera >= 86",
    "safari >= 15",
    "samsung >= 16",
)
# NOTE(xames3): `not (...)` is the newer Media Queries 4 grammar,
# older browsers only read `not all and (...)`.
# https://www.w3.org/TR/mediaqueries-4/#mq-not
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


def add_theme_assets(app: Sphinx) -> None:
    """Add Kaamiki's static files, stylesheets and scripts to HTML
    builders using this theme.

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
    """Rewrite Kaamiki's stylesheets for older browsers.

    The stylesheets are written with nesting and range media queries,
    which older Safari dropped, leaving an older iPhone (which I had)
    with no layout to speak of.

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
    """Set Kaamiki up with Sphinx.

    Registers Kaamiki, its extensions, directives, roles and the
    handlers that fill in the page context. Kaamiki's own words join
    Sphinx's catalogue, the way pydata-sphinx-theme's do, so a site's
    translation of one still wins.

    If Sphinx has no catalogue for the language, the builder's
    translator is pointed at Kaamiki's.

    :param app: The Sphinx application instance.
    :return: Kaamiki's version and that it is safe to read and write
        in parallel.
    """
    for extension in supported_extensions:
        app.setup_extension(extension)
    app.add_html_theme(theme_name, theme_path)
    app.add_message_catalog("sphinx", locale_path)
    app.translator = locale.get_translator()
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
    app.connect("builder-inited", add_theme_assets)
    app.connect("builder-inited", context_defaults)
    app.connect("builder-inited", bridge)
    app.connect("builder-inited", writer.install)
    app.connect("html-page-context", social_metadata)
    app.connect("html-page-context", reading_length)
    app.connect("html-page-context", feedback)
    app.connect("html-page-context", updated_on)
    app.connect("html-page-context", page_switches)
    app.connect("html-page-context", design_assets)
    app.connect("source-read", provenance)
    app.connect("env-get-outdated", reread)
    app.connect("doctree-read", offer, priority=400)
    app.connect("build-finished", build_finished)
    app.connect("build-finished", flatten)
    year, month, day = map(int, version.split("."))
    return {
        "version": version,
        "env_version": year * 10000 + month * 100 + day,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
