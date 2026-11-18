"""\
Template Utilities
==================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 18 November 2026

The Jinja environment of Kaamiki and the helpers that read its
templates and the parts of its bundles.
"""

from __future__ import annotations

import os
import os.path as p
import typing as t

import jinja2

from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils.hooks import on
from kaamiki.extensions.utils.settings import NAME
from kaamiki.extensions.utils.settings import Kaamiki

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx

THEME: t.Final[str] = p.join(
    p.dirname(p.dirname(p.dirname(p.realpath(__file__)))), "theme"
)
TEMPLATES: t.Final[str] = p.join(THEME, "templates")
BUNDLES: t.Final[str] = p.join(THEME, "bundles")
environment: jinja2.Environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES),
    autoescape=True,
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=False,
    extensions=["jinja2.ext.i18n"],
)
environment.install_null_translations(  # type: ignore[attr-defined]
    newstyle=True
)


def parts(bundle: str) -> dict[str, str]:
    """Read the parts of a bundle, in sequence.

    :param bundle: The bundle, relative to `theme/bundles`, as
        `scripts/theme.js`. Its parts are in the folder of the same
        name, and the name of a part is its place, so `10-reset.css`
        comes before `20-base.css`.
    :return: The text of each part, by its file name.
    :raises KaamikiError: For a bundle without parts, or a part that
        is not UTF-8 text.
    """
    stem, suffix = p.splitext(bundle)
    folder = p.join(BUNDLES, stem)
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
    found: dict[str, str] = {}
    for name in names:
        try:
            with open(
                p.join(folder, name), encoding="utf-8-sig", newline=""
            ) as f:
                found[name] = f.read()
        except (OSError, UnicodeDecodeError) as error:
            checks.fail(
                f"expected {name!r} to be UTF-8 text, got {error}",
                "bundles",
            )
    return found


def render(
    template: str,
    /,
    *,
    optional: frozenset[str] = frozenset(),
    **context: object,
) -> str:
    """Render the template of a directive with a context.

    :param template: The file name of the template, relative to
        `theme/templates`.
    :param optional: The options of the directive, which the page can
        leave out.
    :param context: The values for the template, which reads them as
        `kaamiki.directive.url`, next to the values of the site.
    :return: The rendered HTML.
    """
    found = t.cast("Kaamiki", environment.globals[NAME]) | {
        "directive": Kaamiki(f"{NAME}.directive", context, optional=optional)
    }
    return environment.get_template(template).render({NAME: found})


@on("builder-inited")
def bridge(app: Sphinx) -> None:
    """Join the directive templates of Kaamiki to the loader of Sphinx.

    :param app: The Sphinx application instance. Then a site can
        replace a directive template, and the template keeps the Jinja
        environment, the translations and the filters of Kaamiki.
    """
    environment.install_gettext_translations(  # type: ignore[attr-defined]
        app.translator,
        newstyle=True,
    )
    theme = jinja2.FileSystemLoader(TEMPLATES)
    templates = getattr(app.builder, "templates", None)
    if not isinstance(templates, jinja2.BaseLoader):
        environment.loader = theme
        return
    environment.loader = jinja2.ChoiceLoader([templates, theme])
    sphinx = getattr(templates, "environment", None)
    for name, value in getattr(sphinx, "filters", {}).items():
        environment.filters.setdefault(name, value)
