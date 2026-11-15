"""\
Template Utilities
==================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 15 November 2026

The Jinja environment of Kaamiki and the helpers that read its
templates.
"""

from __future__ import annotations

import os.path as p
import typing as t

import jinja2

from kaamiki.extensions.utils.hooks import on
from kaamiki.extensions.utils.links import REL

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx

TEMPLATES: t.Final[str] = p.join(
    p.dirname(p.dirname(p.dirname(p.realpath(__file__)))), "theme", "templates"
)
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


def render(template: str, /, **context: object) -> str:
    """Render the template of a directive with a context.

    :param template: The file name of the template, relative to
        `theme/templates`.
    :param context: The values for the template. Each one gets a `km_`
        prefix in the template.
    :return: The rendered HTML.
    """
    values = {"km_rel": REL, **{f"km_{k}": v for k, v in context.items()}}
    return environment.get_template(template).render(**values)


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
