.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 02 October 2026
.. Last updated on: 15 October 2026

:orphan:
:km-pg-title: Kaamiki Changelog
:km-pg-description: Evolution of Kaamiki Sphinx Theme since its inception
:km-pg-type: website
:km-pg-image: https://avatars.githubusercontent.com/u/90549089?v=4

.. _changelog:

===============================================================================
:far-icon:`list-ul` Changelog
===============================================================================

.. rst-class:: km-lead

    Updates, improvements and changes happening to Kaamiki.

.. author:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :url: https://github.com/xames3/website

.. release:: 2026.10.28
    :title: Loads through Sphinx alone
    :article: changelogs/october-2026

    The biggest release yet. Kaamiki loads through Sphinx natively.

    Added
        - A ``walkthrough`` directive, which scrolls a reader through a
          snippet a line at a time, with the values it held at each one
          written beside the code. |new|
        - An ``attempts`` directive, which shows the versions a piece of code
          went through on its way to what it is now, the lines on their way
          out going red and the new ones coming in green. |new|
        - A ``release`` directive, which writes a changelog entry like the
          ones on this page, with its date and version beside it. |new|
        - ``button`` takes ``:fa-icon-position: after`` to put its icon after
          the label, rather than before it.
        - A dropdown taller than the screen folds down to about a screenful,
          with a Show more button under it. While one is unfolded, Show less
          waits at the bottom of the screen, so folding it back never means
          scrolling all the way up.
        - The build writes ``sitemap.xml`` and a ``robots.txt`` pointing at
          it, unless ``show_sitemap`` is off.
        - A site without a ``fa_kit`` gets Font Awesome Free, so its icons
          still draw.
        - ``button`` takes a colour for its ``:scheme:``, ``red``,
          ``yellow``, ``blue`` or ``green``: the label and a faint outline in
          that colour, the outline filling in on hover.
        - A ``km-radius-normal-bg`` class sets a block on the code background,
          with rounded corners, the width of the text.
        - ``license`` names the content's licence in the footer, with a link
          when given one: ``{"name": "CC BY 4.0", "url": "https://..."}``.
        - ``show_kaamiki_theme`` adds a line naming the theme to the footer,
          the way ``html_show_sphinx`` names Sphinx.
        - ``button`` takes ``:new-tab:``, ``:no-new-tab:``, ``:rel:``,
          ``:title:``, ``:download:`` and ``:class:``. ``button_scheme`` and
          ``button_icon_position`` set the ones a button does not say and
          ``button_colours`` names colours for ``:scheme:``, like
          ``{"purple": "#7c3aed"}``.
        - ``author`` takes ``:avatar-size:``, ``:interval:``,
          ``:hide-reading-time:`` and ``:hide-copy-url:``, which hide what
          the byline shows without them.
        - ``release`` takes ``:date:``, ``:url:`` and ``:article-label:``.
          ``release_version_fmt`` says how a version spells its date and
          ``release_kinds`` gives a group of its own a colour.
        - ``video`` takes ``:sources:``, ``:poster:``, ``:preload:``,
          ``:loop:``, ``:muted:``, ``:hide-controls:`` and ``:track:``.
        - ``youtube`` takes ``:endat:``, ``:loop:``, ``:muted:``,
          ``:hide-controls:``, ``:privacy:``, ``:language:``, ``:ratio:`` and
          ``:click-to-load:``, which shows
          the video's picture and loads the player once it is clicked.
          ``youtube_privacy``, ``youtube_allow`` and
          ``youtube_referrer_policy`` set the rest for the site.
        - ``embed_iframe_hosts`` names the hosts an ``<iframe>`` may come
          from and ``embed_css``, ``embed_js`` and ``embed_js_loading`` load
          files on every page with an embed.
        - ``thumbnail`` takes ``:grayscale:``.
        - ``repository`` takes ``:hide-stars:`` and ``:hide-forks:``.
        - An option says what the author wants by being there. A bare
          ``:grayscale:`` or ``:new-tab:`` turns on what is off without it,
          and ``:hide-*:`` or ``:no-*:`` turns off what is on without it. No
          option takes ``true`` or ``false``.
        - ``show_page_last_updated`` puts the day a page was last updated in
          the feedback box. It is on once feedback is, and a page turns it
          off with ``:km-show-page-last-updated: false``.
        - A setting the theme cannot use stops the build with Python's own
          error, rather than being worked around. A few settings take only
          certain words or numbers (``fa_style``, ``embed_js_loading``,
          ``button_icon_position``, ``logo_size``, ``show_more_after`` and
          ``words_per_minute``), and the build says which. The warnings left
          are ``kaamiki.pages``, ``kaamiki.embed`` and
          ``kaamiki.walkthrough`` for ``suppress_warnings``.
        - The paths in ``author`` and ``video`` count from the top of the
          site, ``_static/cover.png`` or ``/_static/cover.png``, so they
          reach the same file from every page.
        - ``:km-fb-subject:`` sets the feedback mail's subject for a page.
        - ``sharpie_colour``, ``underline_colour``, ``underline_width``,
          ``underline_wobble`` and ``role_colours`` set what the ``sharpie``
          and ``underline`` roles draw, and ``underline`` takes its width
          and wobble after the colour, ``<red; width=3; wobble=0>``.
        - ``walkthrough_limit``, ``walkthrough_timeout``,
          ``walkthrough_memory``, ``walkthrough_output_limit``,
          ``walkthrough_budget``, ``walkthrough_python``,
          ``walkthrough_pythonpath``, ``walkthrough_events`` and
          ``walkthrough_comprehensions`` say what a snippet may run with. A
          snippet's own ``:limit:`` and ``:timeout:`` can lower them, never
          go past them.
        - ``walkthrough_cache`` keeps a trace next to the doctrees and uses
          it again while the snippet, its options, the interpreter and the
          installed packages stay the same.
        - ``last_updated_on_fmt`` spells every date the theme shows, after
          ``html_last_updated_fmt``. ``internal_hosts`` names hosts that count
          as the site, ``logo_size`` sizes the logo and ``words_per_minute``
          and the ``toctree_*`` settings replace what the templates had
          written in.
        - A page in no toctree, an orphan, names its own previous and next
          pages with ``:km-pg-prev:`` and ``:km-pg-next:``. Sphinx works those
          out from the toctree, so an orphan got no buttons at the bottom. An
          article a ``release`` links to goes back to the release's page on
          its own.
        - ``feedback`` sets the feedback box's defaults and a page turns
          any ``show_*`` setting on or off for itself with a field,
          ``:km-show-feedback: false``. The page's field wins.
        - Everything the theme writes reads in the site's ``language``. Its
          own words come in a catalogue that joins Sphinx's, so a site's own
          translation of one still wins and ``gettext`` now collects a
          directive's text, a release's title and a page's ``:km-pg-*:``
          and ``:km-fb-*:`` words.

    Changed
        - Every link that opens in a new tab says ``rel="noopener
          noreferrer"``, the footer's too, and the footer's Kaamiki link
          follows ``internal_hosts`` like the rest.
        - ``show_last_updated_on`` is ``show_page_last_updated`` and
          ``show_show_more`` is ``show_more``. The old names are no
          longer read.
        - The drawer lists what ``toctree_titles_only`` says, as the header
          does, rather than the reverse.
        - ``open_graph: {"enable": False}`` keeps the page's plain
          ``<meta name="description">``.
        - ``release_kinds`` names groups the theme does not colour itself,
          and says so when it is given ``added`` or another it does.
        - ``:km-fb-fa-icon:`` is ``:km-fb-icon:``, as ``feedback`` calls it.
        - ``embed_iframe_hosts`` lets ``about:blank`` through.
        - A feedback box with nowhere to send the reader is not drawn.
        - ``Copied!!`` is ``Copied!``. The walkthrough's ``returns:`` and
          ``error:`` marks, the repository's counts and an attempt's
          ``Broke`` or ``Worked`` are words a catalogue can translate.
        - ``header_buttons``, ``sidebar_buttons``, ``license`` and
          ``feedback`` take ``url`` where some of them took ``link``, so
          every setting that names an address names it the same way. Change
          yours, as the old name is no longer read.
        - ``mark`` is now ``sharpie``, as is its class and the
          ``--sharpie-color`` it draws with.
        - The thumbnail card is drawn in colour, unless ``:grayscale:`` asks
          for grey. It used to be grey until hovered.
        - sphinx-design's success colour is Kaamiki's green, with dark text
          on it, so a ``bdg-success`` badge keeps 4.5:1.
        - A setting that is read while pages are read, ``button_scheme`` and
          ``walkthrough_limit`` among them, sends every page back through
          reading when it changes. Sphinx only does that for settings it knows
          about, so the old buttons stayed in the saved pages until a build
          with ``-E``.
        - What a page writes in ``author`` wins over ``html_context``, which
          used to be poured over the options.
        - A date may be written ``2026-10-05`` as well as ``5 October 2026``.
        - A version that does not read as a date, ``v1.2.0`` say, no longer
          fails ``release``. It shows without a date, unless ``:date:`` gives
          one.
        - The theme loads through Sphinx alone. A site that runs builders
          other than HTML lists ``"kaamiki"`` in ``extensions``.
        - A page shows as soon as the document is ready, so a stalled Font
          Awesome kit, a slow image or a video cannot keep it blank.
        - Every class the theme owns starts with ``km-`` and a page's own
          fields are ``:km-pg-*:`` and ``:km-fb-*:``.
        - A click anywhere on a heading copies its link and brings the
          heading to the top, with the same "Copied!" the byline shows. The
          link icon is gone, so a heading on a phone no longer breaks onto
          another line for it.
        - With ``add_copy_to_headerlinks`` on, a heading under a ``contents``
          table no longer links back to it, so the click copies instead.
        - Numbered and bullet lists draw each marker in a ring, with a line
          running from one ring to the next. A list written in raw HTML keeps
          its own look.
        - Secondary buttons on a card or a ``km-radius-normal-bg`` block take
          the muted fill, so they still stand out in the dark.
        - The header is a little taller and its tint and blur fade out only
          below its links, so the page scrolls under it without a line and
          the links stay clear of it.
        - The footer keeps to the 800px column. Its lines wrap on a wide
          screen rather than squeezing up and stack on a phone.
        - Buttons fade between their colours on hover rather than switching
          at once.
        - Links within a page, Show less and the back to top button glide
          with the browser's own smooth scrolling and give way the moment you
          scroll.
        - The stylesheets go through ``lightningcss`` as the build finishes,
          so nesting reaches Safari 15 as rules it can read.
        - ``sphinx_design``'s stylesheet and tab script only go to pages that
          use them, which saves the rest about 50 KB.
        - Links in prose carry a faint underline, which darkens on hover.
        - Reloading a folded page finds it as it was left: opened if it had
          been and where it had been read to.
        - A site's ``templates_path`` can replace ``author.html.jinja`` and
          the rest, the way it replaces ``layout.html``.
        - The text in ``button``, ``video``, ``youtube``, ``thumbnail`` and
          ``author`` is read as rST, so a substitution or a role in a label
          or a caption shows the way it would in a paragraph.
        - Dates read in the site's ``language`` and the same way everywhere,
          ``05 October 2026`` in English, under a page and beside a release.
        - Dropdowns open and close smoothly however long they are and the
          plus turns back the moment one starts to close.
        - The header's menus and a newly picked tab fade in rather than
          popping up and Show more glides down with the page it unfolds.
        - Tab titles sit on one line in a rounded strip, which scrolls
          sideways on a phone rather than wrapping and the picked tab's
          fill slides across to it.
        - A card's link is a round button with an arrow. Its text is left
          for screen readers.
        - The 404 page is a plain one, a line and a button home. A
          ``404.html`` in the site's ``templates_path`` replaces it.
        - The title badge only shows when ``fa_icons`` names one.
        - A release's groups keep their colours when their headings are
          written in the site's ``language``.
        - A page fades in block by block a little more slowly, so each part
          can be seen arriving.
        - The stylesheets are 814 lines lighter: what was left of the
          Tailwind build they started as, rules for markup the theme no
          longer writes and declarations a later rule always overrode.
        - Borders are gone, except on the byline, the release timeline, the
          phone menu's edge, inline code, the header's menus, table rows and
          the strip of tab titles. Everything else stands apart by its fill,
          lighter in the dark, so nothing sinks into an OLED screen's black.
        - Text, code and tables sit in an 800px column, while pictures and
          videos keep the wider 861px.

    Fixed
        - In Firefox, a jump past a walkthrough lands where it was asked to.
        - Tabs work from the keyboard.
        - The copy buttons work on a plain HTTP address, where the clipboard
          API is missing.
        - A ``mailto:`` link no longer opens an empty tab.
        - A ``thumbnail`` with both ``:title:`` and ``:channel:`` keeps them,
          rather than having YouTube's written over them.
        - A heading's "Copied!" fades out where it showed, rather than
          jumping aside as it goes.
        - Back after a link within the page returns to where you clicked it.
        - Tabbing back up a page no longer leaves the focused link hidden
          under the header.
        - On a phone, tapping the page you are on in the menu closes the menu
          and goes to the top.
        - The back to top button jumps rather than glides when the system
          asks for less motion.
        - Admonition text keeps 4.5:1 against its box.
        - On a wide screen, the sidebar and a release's date stay clear of
          the header instead of slipping under it as the page scrolls.
        - A lexer error in a code block no longer gets a red box around it.
        - A code block's "Copied!" shows in green again. Kaamiki's grey had
          covered it.
        - A centred heading sits in the middle, not 2px to the left of it.
        - A hand-drawn underline comes out the same wherever the site is
          built. It used to depend on the folder the build ran in.

    Removed
        - Light mode. Kaamiki is dark only: ``colour_mode``,
          ``show_colour_modes``, the switch in the footer, its
          ``:km-show-colour-modes:`` field, the ``dark_mode`` and
          ``light_mode`` icons and the light colours are gone.
          ``dark_logo`` is ``logo`` now,
          ``light_logo`` is gone and a page prints as it shows.
        - ``thumbnail_grayscale``. Write ``:grayscale:`` on the thumbnails
          that need it.
        - ``:same-tab:``, ``:controls:``, ``:mute:`` and the ``false`` that
          ``:privacy:``, ``:comprehensions:``, ``:reading-time:`` and
          ``:copy-url:`` once took.
        - ``base.js``, a minified bundle of Alpine and clipboard.js with no
          source behind it. ``theme.js`` does its work now.
        - The ``picture`` directive, which no page used any more.
        - ``--km-scroll-min`` and ``--km-scroll-max``, which timed the script
          the browser's own scrolling replaced.
        - The frame and dashed rules around the content and the line under
          the header once a page has scrolled.
        - ``youtube``'s ``:modestbranding:`` and ``:playsinline:``, which did
          nothing and the ``modestbranding`` parameter YouTube stopped
          reading in 2023.
        - The undocumented ``km-no-zoom`` class. A picture zooms only when
          it asks to, with ``km-zoom``.
        - A colour picked under the September release is no longer read
          back. That release stored one for every visitor, chosen or not.
        - The footer's own "Content licensed under CC BY 4.0", which every
          site using the theme showed. ``license`` puts one back.
        - The ``permalink`` icon in ``fa_icons``, with the icon it named.
        - The cal.com loader. A site booking calls through cal.com loads
          its own script, through ``html_js_files``.

.. release:: 2026.9.10
    :title: Previews, folds and a 404 of its own

    Pages describe themselves to social sites, long pages fold up and the
    theme writes its own 404.

    Added
        - Open Graph and Twitter metadata, worked out from the page itself. A
          page's own fields win.
        - A page longer than ``show_more_after`` minutes folds down to one
          screenful, with a Show more button under it.
        - ``fa_kit`` names the Font Awesome kit. It used to be hardcoded, so
          every site using the theme loaded my kit off my quota.
        - The theme writes a ``404.html`` the site's host can serve, under
          ``show_404``.

    Changed
        - Every directive renders with escaping on, so a title carrying an
          ``&`` or a ``<`` no longer breaks the page.
        - The reading time is worked out as the page is built, rather than
          counted again in the browser.
        - The stylesheets load side by side in a stated order, rather than
          one ``@import`` after another.

    Removed
        - ``sphinxext-opengraph``, which pulled ``matplotlib`` in purely to
          draw social cards.
        - The "On this page" rail.

.. release:: 2026.8.31
    :title: ``iframe`` is now ``embed``

    Changed
        - The ``iframe`` directive is now ``embed``, since it covers inline
          content and HTML fragments as well as iframes. Its argument is
          ``iframe`` or the fragment's path, replacing ``:file:``.
        - An option's value may run over several indented lines.

.. release:: 2026.6.27
    :title: Backgrounds behind the byline

    Added
        - ``author`` takes ``:background:``, one or more pictures that fade
          through behind the page's title.

.. release:: 2026.4.24
    :title: A byline that links anywhere

    Changed
        - The byline's link is no longer tied to GitHub, so it can point at
          any profile.

.. release:: 2026.3.17
    :title: No more timestamps

    Removed
        - ``author``'s ``:timestamp:`` option, which nothing ever rendered.

.. release:: 2026.2.14
    :title: Kaamiki gets its name

    Changed
        - The theme has a name of its own, Kaamiki.

    Removed
        - Support for Algolia's DocSearch.

.. release:: 2026.1.15
    :title: A leaner byline

    Removed
        - The email, bio and LinkedIn details from ``author``.

.. release:: 2025.11.2
    :title: Templates in a folder of their own

    Changed
        - The theme registers from ``base/templates`` rather than ``base``,
          which keeps the templates apart from the styling.
        - The directives are called extensions inside the theme, which is
          the more accurate name for them.
        - Kaamiki's overriding stylesheets load at priority 800 rather
          than 900.

.. release:: 2025.10.19
    :title: Settings through ``html_context``

    Changed
        - Everything the templates read comes through ``html_context`` and
          Kaamiki's options are Sphinx's own ``html_theme_options``.
        - The byline's details are optional and fall back to the project's
          in ``conf.py``.

    Removed
        - The byline's custom subject header, in favour of the page title.

    Deprecated
        - ``website_options`` and ``register_website_options``, in favour of
          ``html_context``.
        - The ``tagged`` directive, which no page put to any real use.

.. release:: 2025.9.8
    :title: Thumbnails without scraping

    Changed
        - ``thumbnail`` reads a video's details from YouTube's oEmbed
          endpoint.

    Removed
        - Scraping YouTube with ``requests`` and BeautifulSoup, which broke
          whenever YouTube changed its markup and made builds very slow.

.. release:: 2025.8.27
    :title: Face tags

    Added
        - A ``tagged`` directive, which lays clickable face tags over an
          image.

    Changed
        - The "Last updated" date sits above the footer.

.. release:: 2025.3.2
    :title: A look for sphinx-design

    Added
        - Stylesheets that restyle ``sphinx_design``'s components to match
          the theme and ``sphinx_docsearch``'s too, until DocSearch went in
          February 2026.

.. release:: 2025.2.21
    :title: The first release

    Added
        - Support for ``sphinxext-opengraph``, out of the box.
