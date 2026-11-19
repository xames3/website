.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 02 October 2026
.. Last updated on: 19 November 2026

:km-page-title: Changelog
:km-page-description: Every Kaamiki release, newest first.
:km-page-type: article
:km-feedback-title: Have you tried Kaamiki yet?
:km-feedback-description: I know it's a long list of changes and updates, but
    if you've any feature in mind or noticed any bugs...
:km-feedback-button: Let me know

.. _changelog:

===============================================================================
:fa-icon:`list-ul` Changelog
===============================================================================

.. rst-class:: km-text-lead

    Every Kaamiki release, newest first.

.. byline:: @xames3
    :avatar: https://i.imgur.com/hUhxigb.jpeg
    :target: https://github.com/xames3

.. release:: Kaamiki stops borrowing now!
    :version: v2026.11.8
    :article: changelogs/november-2026

    The first release on PyPI. Two directives that show code instead of
    describing it, building blocks of my own, a carousel, cards that lead a
    reader on and a theme that loads the way Sphinx expects.

    Added
        - ``code-explain``, which scrolls a reader through a snippet a line at
          a time with the values it held written beside it. Python is run at
          build time, within limits on time, memory and the files it
          writes. |new|
        - ``code-version``, which shows the versions a piece of code went
          through, the lines on their way out going red and the new ones
          green. |new|
        - ``carousel``, a scrolling row of blocks, figures, repositories,
          thumbnails and buttons, with arrows and an optional auto-run. |new|
        - ``accordion``, ``tabs``, ``columns`` and ``block``, which are
          Kaamiki's own. |new|
        - ``release``, which writes an entry like this one, with its date and
          a link to the story behind it. |new|
        - ``:roll:``, a role that rolls a word into the next one while it's on
          screen, at its own pace with ``:interval:``, ``:duration:`` and
          ``:stagger:``. |new|
        - ``:typewrite:``, a role that types its words one key at a time,
          slips now and then and deletes them again. A reader without scripts
          gets them as a list. |new|
        - A picture that's shown smaller than it is opens when you press it,
          flying out from where it sits and back to where it is when it's
          closed. ``kaamiki.conf.media.enlarge`` turns it off for a site,
          ``:km-media-enlarge:`` for a page and ``km-no-enlarge`` for one
          picture. |new|
        - Cards at the end of every page for the pages around it, in place of
          the previous and next buttons. A page names its own with
          ``:km-related-docs:`` and ``:km-related-header:``. |new|
        - A page loads in order: the title block first and then each section,
          once. |new|
        - ``kaamiki.conf`` settings for ``conf.py``, with fields that switch
          the page-level ones for a single page. |new|
        - An option says what you want by being there, so ``:new-tab:`` opens
          a link in a new tab and ``:same-tab:`` keeps it in this one. |new|
        - Roles of your own, built on Kaamiki's: ``.. role:: warn(sharpie)``.
          |new|
        - Icons that draw from Font Awesome Pro with a kit and from Free
          without one. |new|
        - ``sitemap.xml``, ``robots.txt`` and a ``404.html``, written by the
          build. |new|
        - Install it from PyPI as ``kaamiki-sphinx-theme`` on Python 3.14 or
          newer. |new|

    Changed
        - Kaamiki loads the way Sphinx expects: name ``kaamiki`` in
          ``extensions`` and in ``html_theme``. One without the other stops
          the build with an error that says what to change.
        - Kaamiki is dark by default, with a light side and the device's own
          setting, and set in Inter, with fills instead of borders.
        - The title, the lead and the byline are left aligned, the byline in
          one row, with the page's language only when you ask with
          ``:show-language:`` and a faint glow behind the title of a page
          without a ``:backdrop:``.
        - Breadcrumbs show only on a page inside another: the pages above it
          and then its own name, with no home link, since the logo goes home.
        - A page shows as soon as its fonts are ready and never waits more than
          two seconds.
        - A YouTube player shows the video's picture with a play button and
          loads on a click, from ``youtube-nocookie.com``.
        - A directive in the wrong place stops the build, and so does a link
          inside a link or ``:roll:`` inside one. Options and settings
          outside their bounds stop it too, naming the line.
        - The header's menus and a phone's menu list the branch you're in, so
          a site of hundreds of pages builds quickly and its pages stay light.
        - No page scrolls sideways. A table wider than the page scrolls inside
          its own box and long inline code wraps.
        - Pictures, figures, videos and the YouTube player stop at the text's
          675px and sit in the middle of it. Only ``code-explain`` and
          ``code-version`` are wider.
        - The site's search leaves out the byline.
        - The copy buttons on code blocks are Kaamiki's own and show their
          tick the same way as a snippet's.
        - A reader without JavaScript gets the icons and a phone's menu, and
          no buttons that need a script.

    Removed
        - The dependency on ``sphinx-design``, whose ``dropdown``, ``grid``,
          ``card`` and ``tab-set`` are replaced by ``accordion``,
          ``columns``, ``block`` and ``tabs``.
        - The dependency on ``sphinx-copybutton``, whose buttons Kaamiki now
          draws itself.

.. release:: Previews, folds and a 404 of its own
    :version: v2026.9.10

    Pages describe themselves to social sites, long pages fold up and the
    theme writes its own 404.

    Added
        - Open Graph and Twitter metadata, worked out from the page itself. A
          page's own fields win.
        - A page longer than ``kaamiki.conf.show.more_after`` minutes folds
          down to one screenful, with a Show more button under it.
        - ``kaamiki.conf.icons.kit`` names the Font Awesome kit. It used to be
          hardcoded, so every site using the theme loaded the same kit.
        - The theme writes a ``404.html`` the site's host can serve, under
          ``kaamiki.conf.show.not_found``.

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

.. release:: ``iframe`` is now ``embed``
    :version: v2026.8.31

    Changed
        - The ``iframe`` directive is now ``embed``, since it covers inline
          content and HTML fragments as well as iframes. Its argument is
          ``iframe`` or the fragment's path, replacing ``:file:``.
        - An option's value may run over several indented lines.

.. release:: Backgrounds behind the byline
    :version: v2026.6.27

    Added
        - ``byline`` takes ``:backdrop:``, one or more pictures that fade
          through behind the page's title.

.. release:: A byline that links anywhere
    :version: v2026.4.24

    Changed
        - The byline's link is no longer tied to GitHub, so it can point at
          any profile.

.. release:: No more timestamps
    :version: v2026.3.17

    Removed
        - ``byline``'s ``:timestamp:`` option, which nothing ever rendered.

.. release:: Kaamiki gets its name
    :version: v2026.2.14

    Changed
        - The theme has a name of its own, Kaamiki.

    Removed
        - Support for Algolia's DocSearch.

.. release:: A leaner byline
    :version: v2026.1.15

    Removed
        - The email, bio and LinkedIn details from ``byline``.

.. release:: Templates in a folder of their own
    :version: v2025.11.2

    Changed
        - The theme registers from ``base/templates`` rather than ``base``,
          which keeps the templates apart from the styling.
        - The directives are called extensions inside the theme, which is
          the more accurate name for them.
        - Kaamiki's overriding stylesheets load at priority 800 rather
          than 900.

.. release:: Settings through ``html_context``
    :version: v2025.10.19

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

.. release:: Thumbnails without scraping
    :version: v2025.9.8

    Changed
        - ``thumbnail`` reads a video's details from YouTube's oEmbed
          endpoint.

    Removed
        - Scraping YouTube with ``requests`` and BeautifulSoup, which broke
          whenever YouTube changed its markup and made builds very slow.

.. release:: Face tags?!
    :version: v2025.8.27

    Added
        - A ``tagged`` directive, which lays clickable face tags over an
          image.

    Changed
        - The "Last updated" date sits above the footer.

.. release:: A look for ``sphinx-design``
    :version: v2025.3.2

    Added
        - Stylesheets that restyle ``sphinx_design``'s components to match
          the theme and ``sphinx_docsearch``'s too, until DocSearch went in
          February 2026.

.. release:: The very first release!
    :version: v2025.2.21

    Added
        - Support for ``sphinxext-opengraph``, out of the box.
