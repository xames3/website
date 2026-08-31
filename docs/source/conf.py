"""\
Akshay Mestry Configuration
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February, 2025
Last updated on: 30 August, 2026

This file contains the configuration settings for building my static
website using Sphinx, a popular Python documentation tool. Sphinx is a
powerful documentation generator that makes it easy to create high
quality technical documentation for technical projects. I, however will
be using it as teaching and learning platform.

.. versionadded:: 22.2.2025

    [1] Added support for Algolia DocSearch instead of using standard
        Sphinx search. This support is added through the
        `sphinx_docsearch` extension.

.. versionadded:: 1.3.2025

    [1] Added support for copy button. For some reason, the default copy
        button doesn't seem to work. Hence, relying on external sphinx
        extension. This support is added through the `sphinx_copybutton`
        extension.

.. versionchanged:: 5.3.2025

    [1] Customised the CSS of the copy button extension and fixed a bug
        caused by default copy button element.

.. versionchanged:: 19.4.2025

    [1] Added support for PyTorch docs via InterSphinx mappings.

.. deprecated:: 8.8.2025

    [1] Copybutton SVG icon has been replaced with `FontAwesome` icon.
    [2] The `show_sphinx` and `last_updated` options are disabled now.

.. versionchanged:: 8.8.2025

    [1] The website `copyright` is updated to enforce minimalism.

.. versionadded:: 22.8.2025

    [1] Added support for `sphinx-notfound-page` extension to handle the
        404 pages. This extension is used to provide a better user
        experience when a page is not found.

.. versionchanged:: 27.8.2025

    [1] Configured `linkcheck` builder to ignore localhost links.
    [2] Added support for showing the last updated date just above the
        footer. This is done using the `website_options` configuration
        option `last_updated_body`.
    [3] Show the "Built with Sphinx" footer note by enabling the
        `show_sphinx` option in `website_options`.
    [4] Added support for `sponsor` button in the right sidebar.

.. versionchanged:: 19.10.2025

    [1] The theme will now support and use the native sphinx theme
        options instead of custom `website_options`.
    [2] The theme now heavily relies on using `html_context` for passing
        elements through it making them accessible for all pages.
"""

from __future__ import annotations

import typing as t
from datetime import datetime as dt

from markupsafe import Markup

from kaamiki import version as theme_version

if t.TYPE_CHECKING:
    from collections.abc import Sequence

project: t.Final[str] = "Akshay Mestry"
author: t.Final[str] = "Akshay Mestry"
project_copyright: str = f"© 2025-{dt.now().year} {author}."
source: t.Final[str] = "https://github.com/xames3/website"
email: t.Final[str] = "xa@mes3.dev"
version: str = theme_version

extensions: list[str] = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
]

gettext_compact: bool = False
rst_epilog = ""
with open("_static/extra/epilog.rst") as f:
    rst_epilog += f.read()

nitpicky: bool = True
exclude_patterns: Sequence[str] = ["_build"]
smartquotes: bool = False

html_theme: t.Final[str] = "kaamiki"
html_title: str = "amestry"
html_baseurl: t.Final[str] = "https://xa.mes3.dev/"
html_context: dict[str, t.Any] = {
    "add_copy_to_headerlinks": True,
    "fa_icons": {
        "breadcrumb_home": "fa-regular fa-house",
        "breadcrumb_separator_child": "fa-solid fa-angle-right",
        "breadcrumb_separator_parent": "fa-solid fa-angles-right",
        "dark_mode": "fa-solid fa-moon-star",
        "light_mode": "fa-solid fa-sun-bright",
        "next_button": "fa-solid fa-arrow-right",
        "previous_button": "fa-solid fa-arrow-left",
    },
    "favicons": {
        "manifest": "favicons/site.webmanifest",
        "size_96": "favicons/favicon-96x96.png",
        "size_180": "favicons/apple-touch-icon.png",
        "size_svg": "favicons/favicon.svg",
    },
    "header_buttons": {
        "Check my availability": {
            "link": "#",
            "icon": Markup('<i class="far fa-video"></i>'),
            "extras": Markup(
                'data-cal-link="xames3/quick-chat"'
                'data-cal-namespace="quick-chat" '
                'data-cal-config=\'{"layout":"month_view"}\''
            ),
        },
    },
    "open_links_in_new_tab": True,
    "project": {
        "author": author,
        "source": source,
        "email": email,
    },
    "secondary_toctree_title": "On this page",
    "show_breadcrumbs": True,
    "show_colour_modes": False,
    "show_feedback": True,
    "show_last_updated_on": True,
    "show_previous_next_pages": True,
    "show_scrolltop": False,
    "show_searchbox": True,
    "show_sphinx": False,
    "show_toctree": True,
    "sidebar_buttons": {
        "Check my availability": {
            "link": "#",
            "icon": Markup('<i class="far fa-video"></i>'),
            "extras": Markup(
                'data-cal-link="xames3/quick-chat"'
                'data-cal-namespace="quick-chat" '
                'data-cal-config=\'{"layout":"month_view"}\''
            ),
        },
        "Sponsor on GitHub": {
            "link": "https://github.com/sponsors/xames3",
            "icon": Markup('<i class="far fa-heart"></i>'),
        },
    },
}
html_favicon: t.Final[str] = "_static/favicons/favicon.ico"
html_static_path: list[str] = ["_static"]
html_extra_path: list[str] = ["docutils.conf"]
html_permalinks_icon: t.Final[str] = ""
html_use_index = True
html_search = True
templates_path: list[str] = ["_templates"]

intersphinx_mapping: dict[str, tuple[str, None]] = {
    "numpy": ("https://numpy.org/doc/stable/", None),
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    "torch": ("https://docs.pytorch.org/docs/2.11/", None),
}
extlinks: dict[str, tuple[str, str | None]] = {
    "c-ref": ("https://en.cppreference.com/w/c/language/%s", "%s"),
}

ogp_site_name: str = project
ogp_site_url: t.Final[str] = html_baseurl
ogp_social_cards: dict[str, str | bool] = {
    "site_url": html_baseurl,
    "enable": True,
}
ogp_type: t.Final[str] = "website"
ogp_enable_meta_description: bool = True

copybutton_exclude: str = ".linenos, .gp, .go"
copybutton_line_continuation_character: str = "\\"
copybutton_selector: str = "div:not(.no-copybutton) > div.highlight > pre"

linkcheck_ignore: list[str] = [r"https://localhost:\d+/"]
linkcheck_timeout: int = 10
linkcheck_retries: int = 2
