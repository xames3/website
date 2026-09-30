"""\
Akshay Mestry Configuration
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February, 2025
Last updated on: 29 September, 2026

The Sphinx configuration for my website. Sphinx is a documentation
generator; I use it as a teaching and learning platform instead.
"""

from __future__ import annotations

import typing as t
from datetime import datetime as dt

from markupsafe import Markup

if t.TYPE_CHECKING:
    from collections.abc import Sequence

project: t.Final[str] = "Akshay Mestry"
author: t.Final[str] = "Akshay Mestry"
project_copyright: str = f"© 2025-{dt.now().year} {author}."
source: t.Final[str] = "https://github.com/xames3/website"
email: t.Final[str] = "xa@mes3.dev"

extensions: list[str] = [
    "kaamiki",
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

gettext_compact: bool = False
rst_prolog: str = ""
with open("prolog.rst") as f:
    rst_prolog += f.read()

nitpicky: bool = True
exclude_patterns: Sequence[str] = ["_build", "_static", "prolog.rst"]
smartquotes: bool = False

html_theme: t.Final[str] = "kaamiki"
html_title: str = "amestry"
html_baseurl: t.Final[str] = "https://xa.mes3.dev/"

availability: t.Final[dict[str, str]] = {
    "link": "#",
    "icon": Markup('<i class="far fa-calendar"></i>'),
    "extras": Markup(
        'data-cal-link="xames3/quick-chat" '
        'data-cal-namespace="quick-chat" '
        'data-cal-config=\'{"layout":"month_view"}\''
    ),
}

html_context: dict[str, t.Any] = {
    "fa_icons": {
        "breadcrumb_home": "fa-regular fa-house",
        "copy_url": "fa-regular fa-link-simple",
        "dark_mode": "fa-solid fa-moon-star",
        "light_mode": "fa-solid fa-sun-bright",
        "menu": "fa-regular fa-arrow-left-to-line",
        "permalink": "fa-regular fa-link-simple",
        "search": "fa-regular fa-magnifying-glass",
        "title_badge": "fa-solid fa-badge-check",
    },
    "fa_style": "regular",
    "fa_kit": "https://kit.fontawesome.com/8bcdaaff4d.js",
    "favicons": {
        "manifest": "favicons/site.webmanifest",
        "size_96": "favicons/favicon-96x96.png",
        "size_180": "favicons/apple-touch-icon.png",
        "size_svg": "favicons/favicon.svg",
    },
    "header_buttons": {
        "Check my availability": availability,
    },
    "open_graph": {
        "image": "https://avatars.githubusercontent.com/u/90549089?v=4",
        "image_alt": author,
        "site_name": author,
        "locale": "en_GB",
        "card": "summary",
    },
    "project": {
        "source": source,
        "email": email,
    },
    "sidebar_buttons": {
        "Check my availability": availability,
        "Sponsor on GitHub": {
            "link": "https://github.com/sponsors/xames3",
            "icon": Markup('<i class="far fa-heart"></i>'),
        },
    },
}
html_favicon: t.Final[str] = "_static/favicons/favicon.ico"
html_static_path: list[str] = ["_static"]
html_use_index: bool = False

inventories: t.Final[dict[str, str]] = {
    "numpy": "https://numpy.org/doc/stable/",
    "python": "https://docs.python.org/3/",
    "sphinx": "https://www.sphinx-doc.org/en/master/",
    "torch": "https://docs.pytorch.org/docs/2.11/",
}
intersphinx_mapping: dict[str, tuple[str, tuple[str | None, str]]] = {
    name: (url, (None, f"../.cache/intersphinx/{name}.inv"))
    for name, url in inventories.items()
}
suppress_warnings: list[str] = ["design.fa-build"]
extlinks: dict[str, tuple[str, str | None]] = {
    "c-ref": ("https://en.cppreference.com/w/c/language/%s", "%s"),
}

copybutton_exclude: str = ".linenos, .gp, .go"
copybutton_line_continuation_character: str = "\\"
copybutton_selector: str = "div:not(.no-copybutton) > div.highlight > pre"

linkcheck_ignore: list[str] = [
    r"https?://localhost(:\d+)?(/|$)",
    r"https?://127\.0\.0\.1(:\d+)?(/|$)",
    r"https://medium\.com/",
    r"https://stackoverflow\.com/",
]
linkcheck_retries: int = 2
linkcheck_workers: int = 10
linkcheck_report_timeouts_as_broken: bool = True
linkcheck_anchors_ignore_for_url: list[str] = [r"https://github\.com/"]
