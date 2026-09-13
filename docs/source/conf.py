"""\
Akshay Mestry Configuration
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 February, 2025
Last updated on: 12 September, 2026

The Sphinx configuration for my website. Sphinx is a documentation
generator; I use it as a teaching and learning platform instead.

.. versionadded:: 22.2.2025

    [1] Algolia DocSearch in place of the standard Sphinx search,
        through the `sphinx_docsearch` extension.

.. versionadded:: 1.3.2025

    [1] A copy button, through `sphinx_copybutton`. The built-in one
        does not work.

.. versionchanged:: 5.3.2025

    [1] Custom CSS for the copy button, and a fix for a bug in its
        default element.

.. versionchanged:: 19.4.2025

    [1] PyTorch docs through InterSphinx.

.. deprecated:: 8.8.2025

    [1] The copy button's SVG icon, replaced with a Font Awesome one.
    [2] The `show_sphinx` and `last_updated` options.

.. versionchanged:: 8.8.2025

    [1] A shorter `copyright` line.

.. versionadded:: 22.8.2025

    [1] `sphinx-notfound-page`, for a better 404.

.. versionchanged:: 27.8.2025

    [1] `linkcheck` ignores localhost.
    [2] The last updated date sits above the footer, through the
        `last_updated_body` option.
    [3] The "Built with Sphinx" note is on, through `show_sphinx`.
    [4] A sponsor button in the sidebar.

.. versionchanged:: 19.10.2025

    [1] The theme uses Sphinx's own theme options rather than the
        custom `website_options`.
    [2] Everything passed to the templates goes through `html_context`.

.. versionadded:: 10.9.2026

    [1] The Open Graph and Twitter values come from the `open_graph`
        key in `html_context` and are written by the theme. A page's
        own `:og:*` fields win, and one with no `:og:description:`
        falls back to its lead before anything set here.
    [2] `fontawesome_kit` carries the kit URL, which used to be
        hardcoded in the theme's layout.
    [3] `show_show_more` folds a long page down to one screenful, with
        a Show more button under the fade. `show_more_after` is how
        many minutes a page has to run to before that happens, and
        code is left out of that count. Set `show_show_more` to
        `False` to fold nothing.
    [4] `fa_icons` gained `show_more` for that button and `copy_url`
        for the article's copy link, which the theme used to hardcode.
        The theme has defaults for both, so these two entries only pin
        the icons this site already used.
    [5] `show_404` writes a themed `404.html` at the top of the build,
        which is the file GitHub Pages serves for an address it cannot
        find. Set it to `False` to write nothing.

.. versionchanged:: 10.9.2026

    [1] The availability button wears a calendar icon rather than a
        video one, since it opens a scheduling page and not a call.
    [2] The cal.com button attributes had no space between `data-cal-
        link` and `data-cal-namespace`. It only ever looked right
        because BeautifulSoup re-normalised the markup on the way out.
    [3] `linkcheck_ignore` works. It held one pattern for an `https`
        localhost URL with a port, which could never match: the dev
        server speaks `http`, patterns are matched from the start of
        the URI so the trailing slash wanted a path after it, and
        nothing on the site links to localhost anyway. It covers either
        scheme on either host name now, with a port or without, and
        names the two hosts that answer Sphinx's user agent with a 403
        whatever it asks for: `medium.com` and `stackoverflow.com`.
    [4] `linkcheck_timeout` is back to the default 30 seconds. At 10 a
        couple of slow university hosts were failing on the clock
        rather than on being wrong, and a timeout counted as neither
        working nor broken, so the build went green with links nobody
        could open. `linkcheck_report_timeouts_as_broken` calls them
        what they are.
    [5] `linkcheck_workers` is up to 10. The video list alone is three
        hundred odd links.
    [6] `linkcheck_anchors_ignore_for_url` skips anchor checking on
        GitHub, which builds its heading anchors in the browser and so
        reports every one of them as missing.
    [7] `sphinx_copybutton` and `sphinx_design` are gone from
        `extensions`. The theme styles both and adds them to the
        config itself, so naming them here was writing out a
        dependency of the theme's. This file imports `kaamiki` for
        `version`, which is what puts the theme in a position to do
        that before Sphinx reads the list. The theme sets
        those up for the HTML builders, but Sphinx calls a theme's
        `setup()` only when a builder asks for the theme, so under
        `linkcheck` every `grid`, `card` and `fas` in the sources was
        an unknown directive whose content was dropped before the link
        checker saw it. The theme's own directives and roles come from
        importing `kaamiki`, which this file already does.
    [8] `exclude_patterns` names `_static`. An HTML builder excludes
        `html_static_path` itself, so `epilog.rst` was read as a
        document only by the builders that do not, which appended
        `rst_epilog` to the epilog and then complained about every
        substitution in it being defined twice.

.. deprecated:: 10.9.2026

    [1] Dropped the `sphinxext-opengraph` extension and its `ogp_*`
        settings. It pulled `matplotlib` in purely to render social
        cards, which is a heavy dependency for something the theme can
        derive from the doctree itself.
    [2] `secondary_toctree_title` is gone with the "On this page" rail
        it labelled.
    [3] `html_search` is gone. It is not a Sphinx option and nothing
        in the theme read it. `html_use_index` above it is real and
        stays.
    [4] `sphinx-notfound-page` is gone. The theme writes the 404 page
        itself, under `show_404`.
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
]

gettext_compact: bool = False
rst_epilog: str = ""
with open("_static/extra/epilog.rst") as f:
    rst_epilog += f.read()

nitpicky: bool = True
exclude_patterns: Sequence[str] = ["_build", "_static"]
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
        "copy_url": "fa-regular fa-link-simple",
        "dark_mode": "fa-solid fa-moon-star",
        "light_mode": "fa-solid fa-sun-bright",
        "next_button": "fa-solid fa-arrow-right",
        "previous_button": "fa-solid fa-arrow-left",
        "show_more": "fa-solid fa-chevron-down",
    },
    "fontawesome_kit": "https://kit.fontawesome.com/8bcdaaff4d.js",
    "favicons": {
        "manifest": "favicons/site.webmanifest",
        "size_96": "favicons/favicon-96x96.png",
        "size_180": "favicons/apple-touch-icon.png",
        "size_svg": "favicons/favicon.svg",
    },
    "header_buttons": {
        "Check my availability": {
            "link": "#",
            "icon": Markup('<i class="far fa-calendar"></i>'),
            "extras": Markup(
                'data-cal-link="xames3/quick-chat" '
                'data-cal-namespace="quick-chat" '
                'data-cal-config=\'{"layout":"month_view"}\''
            ),
        },
    },
    "open_graph": {
        "image": "https://avatars.githubusercontent.com/u/90549089?v=4",
        "image_alt": author,
        "site_name": author,
        "type": "website",
        "locale": "en_GB",
        "card": "summary",
    },
    "open_links_in_new_tab": True,
    "project": {
        "author": author,
        "source": source,
        "email": email,
    },
    "show_404": True,
    "show_breadcrumbs": True,
    "show_colour_modes": False,
    "show_feedback": True,
    "show_last_updated_on": True,
    "show_more_after": 5,
    "show_previous_next_pages": True,
    "show_scrolltop": False,
    "show_searchbox": True,
    "show_show_more": True,
    "show_sphinx": False,
    "show_toctree": True,
    "sidebar_buttons": {
        "Check my availability": {
            "link": "#",
            "icon": Markup('<i class="far fa-calendar"></i>'),
            "extras": Markup(
                'data-cal-link="xames3/quick-chat" '
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
html_use_index: bool = True
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

copybutton_exclude: str = ".linenos, .gp, .go"
copybutton_line_continuation_character: str = "\\"
copybutton_selector: str = "div:not(.no-copybutton) > div.highlight > pre"

linkcheck_ignore: list[str] = [
    r"https?://localhost(:\d+)?(/|$)",
    r"https?://127\.0\.0\.1(:\d+)?(/|$)",
    r"https://medium\.com/",
    r"https://stackoverflow\.com/",
]
linkcheck_timeout: int = 30
linkcheck_retries: int = 2
linkcheck_workers: int = 10
linkcheck_report_timeouts_as_broken: bool = True
linkcheck_anchors_ignore_for_url: list[str] = [r"https://github\.com/"]
