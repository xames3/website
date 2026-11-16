"""\
Kaamiki Sphinx Theme
====================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February 2025
Last updated on: 16 November 2026

The entry point of Kaamiki. Sphinx adds the stylesheets by priority, so
`font.css` loads first, and `theme.css` loads last and has priority.

https://www.sphinx-doc.org/en/master/extdev/appapi.html
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

import lightningcss
from sphinx import locale
from sphinx.util import logging

from kaamiki.extensions import roles
from kaamiki.extensions.utils import CONF
from kaamiki.extensions.utils import TEMPLATES
from kaamiki.extensions.utils import KaamikiDirective
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import linkcheck
from kaamiki.extensions.utils import on
from kaamiki.extensions.utils import pair
from kaamiki.extensions.utils import phrase
from kaamiki.extensions.utils import register
from kaamiki.extensions.utils.build import writes_pages
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
logger = logging.getLogger(__name__)


def env_version(version: str) -> int:
    """Change a version into the number for the cache.

    :param version: The version of Kaamiki.
    :return: The number, which changes with each release. Each of the
        first four numbers moves two digits for the next, so
        `2026.11.8` is `20261108` and `2026.11.8.1` is `2026110801`.
        Only digits count.
    """
    number = 0
    for each in re.findall(r"[0-9]+", version)[:4]:
        number = number * 100 + int(each)
    return number


@on("builder-inited")
def add_theme_assets(app: Sphinx) -> None:
    """Add the static files of Kaamiki to a build.

    :param app: The Sphinx application instance.
    """
    if not writes_pages(app):
        return
    app.add_static_dir(static_dir)
    for stylesheet, priority in stylesheets:
        app.add_css_file(stylesheet, priority=priority)
    for script in scripts:
        app.add_js_file(script, loading_method="defer")


def generated(app: Sphinx) -> str:
    """Name the folder where a build keeps its joined bundles.

    :param app: The Sphinx application instance.
    :return: The own folder of the build, or nothing before
        `join_parts` made it.
    """
    return str(app.builder.__dict__.get("km_bundles", ""))


@on("builder-inited")
def join_parts(app: Sphinx) -> None:
    """Join the parts of each bundle into the file that the pages link.

    :param app: The Sphinx application instance. Sphinx makes the
        fingerprint of a stylesheet or a script from the file in
        `_static` while it writes the first page, so the joined file
        must be there then. It is written as a static folder, which
        Sphinx copies first. The name of a part is its place, so
        `10-reset.css` comes before `20-base.css`. The folder is in the
        temporary folder of the system. Its name cannot be guessed, and
        only the build can write in it, so no other build or user can
        change what is copied. Sphinx copies the permissions of a
        folder onto `_static`, so the folder is opened for reading.
    :raises KaamikiError: For a bundle without parts, a part that is
        not UTF-8 text, or a folder that Kaamiki cannot write to.
    """
    if not writes_pages(app):
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


@on("build-finished")
def flatten(app: Sphinx, exc: Exception | None) -> None:
    """Write the stylesheets of Kaamiki again for its browsers.

    :param app: The Sphinx application instance.
    :param exc: What went wrong in the build, or `None`.
    """
    if exc or not writes_pages(app):
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


@on("build-finished")
def forget(app: Sphinx, exc: Exception | None) -> None:
    """Remove the folder a build kept its joined bundles in.

    :param app: The Sphinx application instance.
    :param exc: Whatever went wrong during the build or `None`.
    """
    del exc
    if joined := app.builder.__dict__.pop("km_bundles", ""):
        shutil.rmtree(joined, ignore_errors=True)


@on("build-finished")
def cleanup(app: Sphinx, exc: Exception | None) -> None:
    """Remove the unused files of the basic theme.

    :param app: The Sphinx application instance.
    :param exc: What went wrong in the build, or `None`.
    """
    if exc or not writes_pages(app):
        return
    for name in basic_files:
        with contextlib.suppress(FileNotFoundError):
            os.remove(p.join(app.outdir, "_static", name))


def add_roles(app: Sphinx) -> None:
    """Register the roles, their domains and `phrase`.

    :param app: The Sphinx application instance.
    """
    for name, role in roles.KaamikiRole.registry.items():
        app.add_role(name, role)
    app.add_directive("role", roles.CustomRole, override=True)
    app.add_domain(roles.FaIcon)
    app.add_domain(roles.Kbd)
    app.add_node(phrase)


def add_directives(app: Sphinx) -> None:
    """Register the directives of Kaamiki and each node of `html`.

    :param app: The Sphinx application instance.
    """
    for name, directive in KaamikiDirective.registry.items():
        app.add_directive(name, directive)
    html.register(app)


def setup(app: Sphinx) -> dict[str, str | bool | int]:
    """Set up Kaamiki with Sphinx.

    :param app: The Sphinx application instance. This registers
        Kaamiki, its extensions, directives and roles, the link
        checker, and the handlers that fill the context of a page.
    :return: The version of Kaamiki, and an `env_version` that changes
        with each release, so Sphinx reads each page again. Parallel
        reading and writing are safe.
    :raises KaamikiError: For `kaamiki` in `extensions` with a
        different `html_theme`, and for `html_theme = "kaamiki"`
        without `kaamiki` in `extensions`.
    """
    checks.install_reporter()
    pair(app)
    for extension in supported_extensions:
        app.setup_extension(extension)
    app.add_html_theme(NAME, TEMPLATES)
    app.add_message_catalog("sphinx", locale_dir)
    register(app)
    app.add_transform(checks.Plain)
    app.translator = locale.get_translator()
    add_roles(app)
    add_directives(app)
    app.add_builder(linkcheck, override=True)
    on.connect(app)
    return {
        "version": __version__,
        "env_version": env_version(__version__),
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
