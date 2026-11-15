"""\
Kaamiki Sphinx Theme
====================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February 2025
Last updated on: 15 November 2026

Kaamiki's entry point.
"""

from __future__ import annotations

import contextlib
import filecmp
import os
import os.path as p
import re
import shutil
import tempfile
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
from kaamiki.extensions.utils import feedback
from kaamiki.extensions.utils import field_lists
from kaamiki.extensions.utils import follow
from kaamiki.extensions.utils import forget_lead
from kaamiki.extensions.utils import glyph_edges
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import keycaps
from kaamiki.extensions.utils import linkcheck
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
bundles_dir = p.join(p.abspath(p.dirname(__file__)), "theme", "bundles")
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
bundles: Sequence[str] = (
    "styles/theme.css",
    "scripts/core.js",
    "scripts/animations.js",
    "scripts/theme.js",
    "scripts/explainer.js",
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

    Each of the first four numbers in it moves up two digits for the
    next, so `2026.11.8` is `20261108` and `2026.11.8.1` is
    `2026110801`. Only digits count.

    :param version: Kaamiki's version.
    :return: The number, which changes with every release.
    """
    number = 0
    for each in re.findall(r"[0-9]+", version)[:4]:
        number = number * 100 + int(each)
    return number


def themed(app: Sphinx) -> bool:
    """Tell if the build's pages are written with Kaamiki's theme.

    Only the HTML builders that do get Kaamiki's files, which leaves out
    `epub` and the help builders.

    :param app: The Sphinx application instance.
    :return: `True` for those builders, `False` for any other.
    """
    if not isinstance(app.builder, StandaloneHTMLBuilder):
        return False
    theme = getattr(app.builder, "theme", None)
    return theme is not None and TEMPLATES in map(
        p.realpath, theme.get_theme_dirs()
    )


def add_theme_assets(app: Sphinx) -> None:
    """Add Kaamiki's static files, stylesheets and scripts to a build.

    :param app: The Sphinx application instance.
    """
    if not themed(app):
        return
    app.add_static_dir(static_dir)
    for stylesheet, priority in stylesheets:
        app.add_css_file(stylesheet, priority=priority)
    for script in scripts:
        app.add_js_file(script, loading_method="defer")


def generated(app: Sphinx) -> str:
    """Name the folder where a build keeps the bundles it joined.

    :param app: The Sphinx application instance.
    :return: The build's own folder, or nothing before `join_parts` made it.
    """
    return str(app.builder.__dict__.get("km_bundles", ""))


def join_parts(app: Sphinx) -> None:
    """Join the parts of every bundle into the file the pages link to.

    Sphinx fingerprints a stylesheet or a script from the file in `_static`
    while it writes the first page, so the joined file has to be there by then,
    not at the end of the build. It's written as a static folder, which
    Sphinx copies first. A part's name is its place, so `10-reset.css`
    comes before `20-base.css`.

    The folder is the build's own, in the system's temporary one. Its name
    can't be guessed and nobody but the build can write in it, so no other
    build, and no other user, can change what's copied. Sphinx copies a
    folder's permissions onto `_static`, so it's opened up for reading.

    :param app: The Sphinx application instance.
    :raises KaamikiError: For a bundle with no parts, a part that isn't
        UTF-8 text and a folder Kaamiki can't write to.
    """
    if not themed(app):
        return
    texts: dict[str, str] = {}
    for bundle in bundles:
        stem, suffix = p.splitext(bundle)
        folder = p.join(bundles_dir, stem)
        names = sorted(
            _
            for _ in (os.listdir(folder) if p.isdir(folder) else ())
            if _.endswith(suffix) and not _.startswith(".")
        )
        if not names:
            checks.fail(
                f"expected the parts of {bundle!r} in {folder!r}, got none,"
                " so the install is incomplete",
                "bundles",
            )
        texts[bundle] = ""
        for name in names:
            try:
                with open(
                    p.join(folder, name), encoding="utf-8-sig", newline=""
                ) as f:
                    texts[bundle] += f.read()
            except (OSError, UnicodeDecodeError) as error:
                checks.fail(
                    f"expected {name!r} to be UTF-8 text, got {error}",
                    "bundles",
                )
    joined = ""
    try:
        joined = tempfile.mkdtemp(prefix="kaamiki-")
        os.chmod(joined, 0o755)  # noqa: S103
        for bundle, text in texts.items():
            target = p.join(joined, bundle)
            os.makedirs(p.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8", newline="") as f:
                f.write(text)
    except OSError as error:
        shutil.rmtree(joined, ignore_errors=True)
        checks.fail(
            f"expected a temporary folder Kaamiki can write to, got {error}",
            "bundles",
        )
    app.builder.__dict__["km_bundles"] = joined
    app.add_static_dir(joined)


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
        source = p.join(
            generated(app) if stylesheet in bundles else static_dir, stylesheet
        )
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
        os.chmod(target, 0o644)
        with open(target, "w", encoding="utf-8") as f:
            f.write(notices + css)


def forget(app: Sphinx, exc: Exception | None) -> None:
    """Remove the folder a build kept its joined bundles in.

    :param app: The Sphinx application instance.
    :param exc: Whatever went wrong during the build or `None`.
    """
    del exc
    if joined := app.builder.__dict__.pop("km_bundles", ""):
        shutil.rmtree(joined, ignore_errors=True)


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


def simplify(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Swap Kaamiki's nodes for ordinary ones where there's no HTML.

    The text, LaTeX, man and texinfo builders can't write Kaamiki's
    nodes, so a directive that has a `plain` function gets its node
    swapped for what that returns. They then write words and links.

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
    """Register Kaamiki's roles, their domains and the `phrase` node.

    :param app: The Sphinx application instance.
    """
    for key in roles.ROLES:
        app.add_role(key, getattr(roles, key))
    app.add_directive("role", roles.role, override=True)
    app.add_role("fa-icon", roles.icon)
    app.add_domain(roles.fa_icon)
    app.add_domain(roles.kbd)
    app.add_node(phrase)


def add_directives(app: Sphinx) -> None:
    """Register Kaamiki's directives and each node in the `html` record.

    :param app: The Sphinx application instance.
    """
    for directive in directives:
        app.add_directive(directive.name, directive.directive)
        if hasattr(directive, "register"):
            directive.register(app)
        if hasattr(directive, "html_page_context"):
            app.connect("html-page-context", directive.html_page_context)
    html.register(app)


def connect_hooks(app: Sphinx) -> None:
    """Connect the handlers that read and write Kaamiki's pages.

    :param app: The Sphinx application instance.
    """
    app.connect("builder-inited", checks.hush)
    app.connect("builder-inited", add_theme_assets)
    app.connect("builder-inited", join_parts)
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
    app.connect("build-finished", forget)


def setup(app: Sphinx) -> dict[str, str | bool | int]:
    """Set Kaamiki up with Sphinx.

    Registers Kaamiki, its extensions, directives, roles, the link
    checker and the handlers that fill in the page context.

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
    app.add_builder(linkcheck, override=True)
    connect_hooks(app)
    return {
        "version": __version__,
        "env_version": env_version(__version__),
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
