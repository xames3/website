"""\
Kaamiki Sphinx Theme
====================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February 2025
Last updated on: 07 November 2026

Kaamiki's entry point.
"""

from __future__ import annotations

import contextlib
import filecmp
import os
import os.path as p
import re
import typing as t

import docutils.nodes as nodes
from sphinx import locale
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util import logging

from kaamiki.extensions import directives
from kaamiki.extensions import nesting
from kaamiki.extensions import roles
from kaamiki.extensions.utils import CONF
from kaamiki.extensions.utils import TEMPLATES
from kaamiki.extensions.utils import admonition_title
from kaamiki.extensions.utils import apply
from kaamiki.extensions.utils import bridge
from kaamiki.extensions.utils import build_finished
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import context_defaults
from kaamiki.extensions.utils import depart
from kaamiki.extensions.utils import feedback
from kaamiki.extensions.utils import field_lists
from kaamiki.extensions.utils import follow
from kaamiki.extensions.utils import forget_lead
from kaamiki.extensions.utils import glyph
from kaamiki.extensions.utils import glyph_edges
from kaamiki.extensions.utils import keycaps
from kaamiki.extensions.utils import merge_leads
from kaamiki.extensions.utils import neighbours
from kaamiki.extensions.utils import note_lead
from kaamiki.extensions.utils import offer
from kaamiki.extensions.utils import overrides
from kaamiki.extensions.utils import page_fields
from kaamiki.extensions.utils import page_switches
from kaamiki.extensions.utils import page_title
from kaamiki.extensions.utils import pair
from kaamiki.extensions.utils import phrase
from kaamiki.extensions.utils import provenance
from kaamiki.extensions.utils import register
from kaamiki.extensions.utils import related
from kaamiki.extensions.utils import reread
from kaamiki.extensions.utils import retitled
from kaamiki.extensions.utils import show_more
from kaamiki.extensions.utils import skip
from kaamiki.extensions.utils import social_metadata
from kaamiki.extensions.utils import spell
from kaamiki.extensions.utils import toctrees
from kaamiki.extensions.utils import updated_on
from kaamiki.extensions.utils import warm
from kaamiki.extensions.utils import writer
from kaamiki.extensions.utils.settings import NAME

if t.TYPE_CHECKING:
    from collections.abc import Sequence

    from sphinx.application import Sphinx

__version__: str = "2026.11.8"
conf = CONF
static_dir = p.join(p.abspath(p.dirname(__file__)), "theme", "static")
locale_dir = p.join(p.abspath(p.dirname(__file__)), "locale")
supported_extensions: Sequence[str] = ("sphinx_copybutton",)
# NOTE(xames3): Sphinx adds stylesheets by priority, so font.css loads
# first and theme.css last and wins.
# https://www.sphinx-doc.org/en/master/extdev/appapi.html
stylesheets: Sequence[tuple[str, int]] = (
    ("styles/font.css", 400),
    ("styles/code.css", 600),
    ("styles/theme.css", 700),
)
scripts: Sequence[str] = (
    "scripts/core.js",
    "scripts/animations.js",
    "scripts/theme.js",
    "scripts/explainer.js",
)
browsers: Sequence[str] = (
    "chrome >= 120",
    "edge >= 120",
    "firefox >= 121",
    "ios_saf >= 17",
    "opera >= 106",
    "safari >= 17",
    "samsung >= 25",
)
basic_files: Sequence[str] = ("basic.css", "file.png", "minus.png", "plus.png")
formats: Sequence[str] = ("latex", "man", "texinfo", "text")
logger = logging.getLogger(__name__)


def env_version(version: str) -> int:
    """Turn a version into the number Sphinx compares the cache with.

    The first four numbers in it, two digits each, so `2026.11.8` is
    `20261108` and a same day fix (`2026.11.8.1`) or a pre-release
    (`2026.11.8rc1`) is another.

    :param version: Kaamiki's version.
    :return: The number, which changes with every release.
    """
    number = 0
    for each in re.findall(r"[0-9]+", version)[:4]:
        number = number * 100 + int(each)
    return number


def add_theme_assets(app: Sphinx) -> None:
    """Add Kaamiki's static files, stylesheets and scripts to the HTML
    builders that write their pages with Kaamiki's theme, which leaves
    out `epub` and the help builders.

    :param app: The Sphinx application instance.
    """
    if not isinstance(app.builder, StandaloneHTMLBuilder):
        return
    theme = getattr(app.builder, "theme", None)
    if theme is None or TEMPLATES not in map(
        p.realpath, theme.get_theme_dirs()
    ):
        return
    app.add_static_dir(static_dir)
    for stylesheet, priority in stylesheets:
        app.add_css_file(stylesheet, priority=priority)
    for script in scripts:
        app.add_js_file(script, loading_method="defer")


def flatten(app: Sphinx, exc: Exception | None) -> None:
    """Rewrite Kaamiki's stylesheets for the browsers it supports.

    :param app: The Sphinx application instance.
    :param exc: Whatever went wrong during the build or `None`.
    """
    builder = app.builder
    if exc or not isinstance(builder, StandaloneHTMLBuilder):
        return
    try:
        import lightningcss
    except ImportError as error:
        logger.warning(
            "lightningcss isn't installed, so the stylesheets stay as they"
            " were copied: %s",
            error,
            type="kaamiki",
            subtype="css",
        )
        return
    for stylesheet, _ in stylesheets:
        source = p.join(static_dir, stylesheet)
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
                "%s stays as it was copied: %s",
                stylesheet,
                error,
                type="kaamiki",
                subtype="css",
            )
            continue
        notices = "".join(
            f"{_}\n"
            for _ in re.findall(r"/\*!.*?\*/", text, re.DOTALL)
            if _ not in css
        )
        with open(target, "w", encoding="utf-8") as f:
            f.write(notices + css)


def cleanup(app: Sphinx, exc: Exception | None) -> None:
    """Remove the files of Sphinx's basic theme that no page loads.

    :param app: The Sphinx application instance.
    :param exc: Whatever went wrong during the build or `None`.
    """
    if exc or not isinstance(app.builder, StandaloneHTMLBuilder):
        return
    for name in basic_files:
        with contextlib.suppress(FileNotFoundError):
            os.remove(p.join(app.outdir, "_static", name))


away = (skip, None)


def simplify(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Swap Kaamiki's nodes for ordinary ones where there is no HTML.

    The text, LaTeX, man and texinfo builders can't write Kaamiki's
    nodes, so a directive that has a `plain` function gets its node
    swapped for what that returns, and they write words and links.

    :param app: The Sphinx application instance.
    :param doctree: The page, about to be written.
    :param docname: The page's name.
    """
    del docname
    if app.builder.format not in formats:
        return
    for directive in directives:
        plain = getattr(directive, "plain", None)
        if plain is None:
            continue
        for found in [*doctree.findall(directive.node)]:
            found.replace_self(plain(found))


def add_roles(app: Sphinx) -> None:
    """Register Kaamiki's roles and the nodes they write.

    :param app: The Sphinx application instance.
    """
    for key in roles.ROLES:
        app.add_role(key, getattr(roles, key))
    app.add_directive("role", roles.role, override=True)
    app.add_role("fa-icon", roles.icon)
    app.add_domain(roles.fa_icon)
    app.add_domain(roles.kbd)
    app.add_node(roles.ink, html=(roles._visit, roles._depart))
    app.add_node(roles.rotor, html=(roles._visit_rotor, roles._depart_rotor))
    app.add_node(
        glyph,
        html=(roles._visit_glyph, roles._depart),
        latex=away,
        man=away,
        texinfo=away,
        text=away,
    )
    app.add_node(phrase)


def add_directives(app: Sphinx) -> None:
    """Register Kaamiki's directives and the nodes they write.

    :param app: The Sphinx application instance.
    """
    for directive in directives:
        if hasattr(directive, "node"):
            node = directive.node
            html = (directive.visit, getattr(directive, "depart", depart))
            if node.__bases__ == (nodes.Element,) and not hasattr(
                directive, "plain"
            ):
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


def connect_hooks(app: Sphinx) -> None:
    """Connect the handlers that read and write Kaamiki's pages.

    :param app: The Sphinx application instance.
    """
    app.connect("builder-inited", checks.hush)
    app.connect("builder-inited", add_theme_assets)
    app.connect("builder-inited", context_defaults)
    app.connect("builder-inited", bridge)
    app.connect("builder-inited", writer.install)
    app.connect("html-page-context", social_metadata)
    app.connect("html-page-context", show_more)
    app.connect("html-page-context", feedback)
    app.connect("html-page-context", updated_on)
    app.connect("html-page-context", page_switches)
    app.connect("html-page-context", neighbours)
    app.connect("html-page-context", related)
    app.connect("html-page-context", toctrees)
    app.connect("source-read", provenance)
    app.connect("env-before-read-docs", warm)
    app.connect("env-get-outdated", reread)
    app.connect("env-get-outdated", follow)
    app.connect("env-updated", retitled)
    app.connect("doctree-read", spell, priority=50)
    app.connect("doctree-read", checks.promote, priority=100)
    app.connect("doctree-read", nesting.nested, priority=150)
    app.connect("doctree-read", field_lists, priority=300)
    app.connect("doctree-read", offer, priority=400)
    app.connect("doctree-read", page_title, priority=200)
    app.connect("doctree-read", admonition_title, priority=200)
    app.connect("doctree-read", page_fields, priority=600)
    app.connect("doctree-read", note_lead)
    app.connect("doctree-read", roles.subjects)
    app.connect("doctree-read", keycaps)
    app.connect("doctree-read", glyph_edges, priority=700)
    app.connect("env-purge-doc", forget_lead)
    app.connect("env-merge-info", merge_leads)
    app.connect("doctree-resolved", simplify)
    app.connect("build-finished", build_finished)
    app.connect("build-finished", flatten)
    app.connect("build-finished", cleanup)


def setup(app: Sphinx) -> dict[str, str | bool | int]:
    """Set Kaamiki up with Sphinx.

    Registers Kaamiki, its extensions, directives, roles and the
    handlers that fill in the page context.

    :param app: The Sphinx application instance.
    :return: Kaamiki's version and an `env_version` that changes with
        each release, so Sphinx reads every page again. Reading and
        writing in parallel is safe.
    :raises KaamikiError: For `kaamiki` in `extensions` with another
        `html_theme` and for `html_theme = "kaamiki"` without `kaamiki`
        in `extensions`.
    """
    checks.install_reporter()
    pair(app)
    for extension in supported_extensions:
        app.setup_extension(extension)
    app.add_html_theme(NAME, TEMPLATES)
    app.add_message_catalog("sphinx", locale_dir)
    register(app)
    app.connect("config-inited", apply)
    app.connect("config-inited", overrides)
    app.add_transform(checks.Plain)
    app.translator = locale.get_translator()
    add_roles(app)
    add_directives(app)
    connect_hooks(app)
    return {
        "version": __version__,
        "env_version": env_version(__version__),
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
