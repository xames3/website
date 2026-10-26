"""\
Template Utilities
==================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 23 October 2026

Kaamiki's Jinja environment and the helpers that read its templates.
"""

import os.path as p
import typing as t

import jinja2

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
environment.install_null_translations(newstyle=True)  # type: ignore[attr-defined]


def render(template: str, /, **context: t.Any) -> str:
    """Render a theme directive template with the given context.

    Context values are exposed to the template with a `km_` prefix.

    :param template: Template filename, relative to `theme/templates`.
    :param context: Values made available to the template.
    :return: The rendered HTML.
    """
    values = {"km_rel": REL, **{f"km_{k}": v for k, v in context.items()}}
    return environment.get_template(template).render(**values)


def bridge(app: Sphinx) -> None:
    """Bridge Kaamiki's directive templates with Sphinx's template
    loader.

    Directive templates can be overridden by the site or a child theme,
    while keeping Kaamiki's Jinja environment, translations and
    filters.

    :param app: The Sphinx application instance.
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


def themed(builder: object) -> bool:
    """Say whether a builder writes its pages with this theme.

    :param builder: The builder, of any kind.
    :return: `True` when this theme's templates are among its theme's.
    """
    theme = getattr(builder, "theme", None)
    if theme is None:
        return False
    return any(p.realpath(_) == TEMPLATES for _ in theme.get_theme_dirs())
