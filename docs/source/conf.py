"""\
Akshay Mestry Configuration
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February 2025
Last updated on: 02 November 2026

The Sphinx configuration for my website. Sphinx is a documentation
generator; I use it as a teaching and learning platform instead.
"""

import os
import typing as t
from datetime import UTC
from datetime import datetime as dt

import kaamiki

if t.TYPE_CHECKING:
    from collections.abc import Sequence

project: t.Final[str] = "Akshay Mestry"
author: t.Final[str] = "Akshay Mestry"
# NOTE(xames3): `SOURCE_DATE_EPOCH` keeps the copyright year of a rebuild
# the same, whatever year it happens in.
# https://reproducible-builds.org/specs/source-date-epoch/
epoch: t.Final[str | None] = os.environ.get("SOURCE_DATE_EPOCH")
year: t.Final[int] = (
    dt.fromtimestamp(int(epoch), UTC) if epoch else dt.now()
).year
project_copyright: str = f"© 2025-{year} {author}."
source: t.Final[str] = "https://github.com/xames3/website"
email: t.Final[str] = "xa@mes3.dev"

extensions: list[str] = [
    "kaamiki",
    "sphinx.ext.intersphinx",
]

with open("prolog.rst", encoding="utf-8") as f:
    rst_prolog: str = f.read()

nitpicky: bool = True
smartquotes: bool = False
exclude_patterns: Sequence[str] = ["_static", "prolog.rst"]

html_theme: t.Final[str] = "kaamiki"
html_title: str = "AM"
html_baseurl: t.Final[str] = "https://xa.mes3.dev/"

kaamiki.conf.code_explain.run = True
kaamiki.conf.icons.update(
    {
        "search": "fa-regular fa-magnifying-glass",
        "title_badge": "fa-solid fa-badge-check",
    }
)
kaamiki.conf.icons.style = "regular"
kaamiki.conf.icons.kit = "https://kit.fontawesome.com/8bcdaaff4d.js"
kaamiki.conf.site.favicons = {
    "manifest": "favicons/site.webmanifest",
    "size_96": "favicons/favicon-96x96.png",
    "size_180": "favicons/apple-touch-icon.png",
    "size_svg": "favicons/favicon.svg",
}
kaamiki.conf.site.license = {
    "name": "CC BY 4.0",
    "url": "https://creativecommons.org/licenses/by/4.0/",
}
kaamiki.conf.site.open_graph = {
    "image": "https://avatars.githubusercontent.com/u/90549089?v=4",
    "image_alt": author,
    "site_name": author,
    "locale": "en_GB",
    "card": "summary",
}
kaamiki.conf.site.project = {
    "source": source,
    "email": email,
}
kaamiki.conf.site.sidebar_buttons = {
    "Sponsor on GitHub": {
        "url": "https://github.com/sponsors/xames3",
        "icon": "fa-solid fa-heart km-tone--red",
    },
}
html_favicon: t.Final[str] = "_static/favicons/favicon.ico"
html_static_path: list[str] = ["_static"]
html_css_files: list[str] = ["site.css"]
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

copybutton_exclude: str = ".linenos, .gp, .go"
copybutton_line_continuation_character: str = "\\"
copybutton_selector: str = "div > div.highlight > pre"

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
