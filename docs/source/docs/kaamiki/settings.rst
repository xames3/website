.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 19 October 2026
.. Last updated on: 22 November 2026

:km-page-title: Kaamiki settings
:km-page-description: Every setting Kaamiki reads, grouped by what you want to
    change, with what it falls back to and how a page can override it.
:km-page-type: article
:km-header-subheader: Every setting, set in conf.py
:km-feedback-title: Is a setting missing?
:km-feedback-description: Tell me what you'd want to change from conf.py.
:km-feedback-button: Tell me

.. _kaamiki-settings:

===============================================================================
:fa-icon:regular:`sliders` Settings
===============================================================================

.. rst-class:: km-text-lead

    Every setting, in one place.

Kaamiki's settings live on one object, ``kaamiki.conf``, in groups such as
``icons``, ``show`` and ``youtube``. Each one is written as the group and then
the name in the tables further down, and you can set it in three places.
Anything you leave out takes the default listed on this page, so you only write
what you want to change:

.. tabs::
    :group: setting-place

    .. tab:: conf.py

        .. code-block:: python

            import kaamiki

            kaamiki.conf.show.scrolltop = True

    .. tab:: Command line

        .. code-block:: console

            sphinx-build -D kaamiki_show_scrolltop=1 ...

    .. tab:: One page

        .. code-block:: rst

            :km-show-scrolltop:

Settings are read when ``"kaamiki"`` is in your ``extensions``, which it is
next to ``html_theme = "kaamiki"``, as :doc:`installation` shows. The two go
together, so a value you set on ``kaamiki.conf`` always counts.

.. _kaamiki-where-do-you-want-to-start:

-------------------------------------------------------------------------------
Where do you want to start?
-------------------------------------------------------------------------------

.. block:: Your site
    :size: small
    :ref: kaamiki-settings-site

    Who you are, your licence and your link previews.

.. block:: Page furniture
    :size: small
    :ref: kaamiki-settings-chrome

    Breadcrumbs, feedback, show more and the back-to-top button.

.. block:: Navigation
    :size: small
    :ref: kaamiki-settings-nav

    The menus, and the buttons in the header.

.. block:: Links
    :size: small
    :ref: kaamiki-settings-links

    Which links open in a new tab.

.. block:: The feedback box
    :size: small
    :ref: kaamiki-settings-feedback

    Its words, its button and where it sends readers.

.. block:: Buttons and roles
    :size: small
    :ref: kaamiki-settings-colours

    Colours for buttons, sharpies and underlines.

.. block:: Icons
    :size: small
    :ref: kaamiki-settings-icons

    A Font Awesome kit, a style and the icons the theme draws.

.. block:: Pictures
    :size: small
    :ref: kaamiki-settings-media

    Whether a click opens a picture bigger.

.. block:: Motion
    :size: small
    :ref: kaamiki-settings-motion

    How quickly everything moves, all at once.

.. block:: Embeds and videos
    :size: small
    :ref: kaamiki-settings-embeds

    Where an iframe may come from, and YouTube's privacy.

.. block:: code-explain
    :size: small
    :ref: kaamiki-settings-code-explain

    What a snippet may run with.

.. _kaamiki-settings-start:

-------------------------------------------------------------------------------
Settings most sites set.
-------------------------------------------------------------------------------

Everything works without any of these, but this is what I'd set first:

.. code-block:: python

    # Turns on the feedback box, which emails you.
    kaamiki.conf.site.project = {"email": "you@example.com"}
    # Adds a licence line to the footer.
    kaamiki.conf.site.license = {
        "name": "CC BY 4.0",
        "url": "https://creativecommons.org/licenses/by/4.0/",
    }
    # The picture shown when someone shares a link to your site.
    kaamiki.conf.site.open_graph = {"image": "_static/cover.png"}
    # Dark by default. "light" and "system" are the other two.
    kaamiki.conf.mode = "dark"

The sections after this one list every setting by area. Each has its table of
settings folded away first, and examples after it.

.. _kaamiki-settings-precedence:

-------------------------------------------------------------------------------
Which value wins.
-------------------------------------------------------------------------------

A setting can come from three places. The closest one wins:

1. A field at the top of a page, like ``:km-toctree-in-header: false``, changes
   the setting for that page alone.
2. Your ``conf.py`` is the setting for the whole site.
3. Kaamiki's default is what you get when neither of the above says anything.

Take the back-to-top button. Kaamiki's default is off, so no page has one. Set
``kaamiki.conf.show.scrolltop`` to ``True`` in ``conf.py`` and every page does.
Put ``:km-show-scrolltop: false`` on one page and that page goes back to having
none. It works the other way round too, so a page can turn something on that
the site has off.

This is easiest to see on a real page. :doc:`examples/overrides` turns several
switches on and off for itself, and this site's own ``conf.py`` doesn't set any
of them.

A few settings can only be set for the whole site, since a page can't choose
them. They're marked *site-wide* in the tables.

Every setting is checked before the first page is read, and one Kaamiki can't
accept stops the build with a message naming it and what it takes. Nothing in
``conf.py`` is coerced, so ``"false"`` isn't ``False``, ``1`` isn't ``True``
and a string isn't a list. A number that's valid but outside its range is an
error and never clamped. A name that isn't a setting, like
``kaamiki.conf.show.breadcrumb``, fails on the line of ``conf.py`` that wrote
it with "expected a Kaamiki setting, got an unknown name", and so does a wrong
value. A flat name like ``kaamiki_show_scrolltop = True`` in ``conf.py`` is no
setting either. It stops the build with "expected kaamiki.conf.show.scrolltop,
got a plain name in conf.py", and a ``kaamiki_`` name that Kaamiki doesn't have
stops it with the same unknown-name message. Settings that shape the content of
pages, like the button, code-explain, YouTube and icon ones, also send every
page back through reading when you change them, so you don't need ``-E`` to see
the change.

.. _kaamiki-settings-command-line:

-------------------------------------------------------------------------------
On the command line.
-------------------------------------------------------------------------------

A ``-D`` reaches every setting and wins over ``conf.py``. Its name is
``kaamiki_``, the group and the name, joined by underscores:

.. code-block:: console

    sphinx-build -D kaamiki_show_scrolltop=1 -D kaamiki_icons_style=solid ...

A switch is written ``0`` or ``1``. A number is written as itself, a list has
commas between its items and one entry of a dictionary setting is written
``-D kaamiki_site_feedback.title=Hi``, which the setting takes the way it
takes ``kaamiki.conf.site.feedback = {"title": "Hi"}``. An entry wins over the
same entry in ``conf.py`` and leaves the other entries of the dictionary as
``conf.py`` wrote them. The entries that are switches or numbers are read the
way the setting reads them:

.. code-block:: console

    sphinx-build -D kaamiki_site_feedback.split=1 ...
    sphinx-build -D kaamiki_site_open_graph.enable=0 ...
    sphinx-build -D kaamiki_site_open_graph.description_length=120 ...

Here ``split`` and ``enable`` take ``0`` or ``1`` and ``description_length``
takes a whole number from 50 to 300. A value that isn't one the setting takes
stops the build, as it does in ``conf.py``, and so does a name that isn't a
Kaamiki setting:

.. code-block:: text

    -D kaamiki_site_feedback.split=2: expected 0 or 1, got '2'

.. _kaamiki-settings-ranges:

-------------------------------------------------------------------------------
What a setting accepts.
-------------------------------------------------------------------------------

The ranges below are the same ones a directive's options check. A bound is
included.

.. accordion:: What each setting accepts

    .. list-table::
        :header-rows: 1
        :widths: 36 64

        * - Setting
          - Accepts
        * - ``kaamiki.conf.show.*``, ``kaamiki.conf.site.copy_headerlinks``,
            ``kaamiki.conf.links.new_tab``, ``kaamiki.conf.toctree.in_header``,
            ``kaamiki.conf.toctree.includehidden``,
            ``kaamiki.conf.toctree.titles_only``,
            ``kaamiki.conf.code_explain.cache``,
            ``kaamiki.conf.code_explain.comprehensions``,
            ``kaamiki.conf.code_explain.run``,
            ``kaamiki.conf.youtube.click_to_load``,
            ``kaamiki.conf.youtube.privacy``
          - ``True`` or ``False``, and nothing else.
        * - ``kaamiki.conf.show.more_after``
          - A whole number from 3 to 8, in minutes. It can't be set with
            ``kaamiki.conf.show.more`` off.
        * - ``kaamiki.conf.show.previous_next_cards_count``
          - A whole number from 1 to 7. It can't be set with
            ``kaamiki.conf.show.previous_next_cards`` off or
            ``kaamiki.conf.show.previous_next_pages`` on.
        * - ``kaamiki.conf.site.words_per_minute``
          - A whole number from 100 to 350.
        * - ``kaamiki.conf.site.logo_size``
          - A whole number from 8 to 64.
        * - ``kaamiki.conf.toctree.maxdepth``
          - A whole number from 0 to 4, where 0 is no limit.
        * - ``kaamiki.conf.roles.underline_width``,
            ``kaamiki.conf.roles.underline_wobble``
          - A number from 0.5 to 4 and from 0 to 2.
        * - ``kaamiki.conf.code_explain.limit``,
            ``kaamiki.conf.code_explain.budget``
          - A whole number from 1 to 300 and from 1 to 100.
        * - ``kaamiki.conf.code_explain.timeout``
          - A whole number of seconds from 1 to 60.
        * - ``kaamiki.conf.code_explain.memory``,
            ``kaamiki.conf.code_explain.output_limit``
          - A whole number of megabytes, from 128 to 4096 and from 1 to 128.
        * - ``kaamiki.conf.roles.sharpie_colour``,
            ``kaamiki.conf.roles.underline_colour``
          - ``red``, ``yellow``, ``blue``, ``green``, a name in
            ``kaamiki.conf.roles.colours``, a hex colour like ``#7c3aed`` or
            three hsl numbers like ``262 83% 58%``.
        * - ``kaamiki.conf.button.colours``, ``kaamiki.conf.roles.colours``
          - Lowercase names that aren't Kaamiki's own, each with a hex colour
            or hsl numbers.
        * - ``kaamiki.conf.icons.names``
          - A name from the table below and an icon like ``fa-solid fa-house``
            or a pair like
            ``{"pro": "fa-solid fa-house", "free": "fa-regular fa-house"}``, or
            an empty string for none where the table allows it.
        * - ``kaamiki.conf.icons.style``
          - ``solid``, ``regular``, ``light`` or ``thin``. The last two need a
            kit.
        * - ``kaamiki.conf.accordion.marker``
          - ``plus``, ``down`` or ``right``.
        * - ``kaamiki.conf.accordion.marker_position``,
            ``kaamiki.conf.button.icon_position``,
            ``kaamiki.conf.tab.icon_position``
          - ``before`` or ``after``.
        * - ``kaamiki.conf.embed.js_loading``
          - ``defer``, ``async`` or ``normal``.

        * - ``kaamiki.conf.youtube.allow``
          - Permissions from ``accelerometer``, ``autoplay``,
            ``clipboard-write``, ``encrypted-media``, ``fullscreen``,
            ``gyroscope``, ``picture-in-picture`` and ``web-share``, joined by
            a semicolon and a space.
        * - ``kaamiki.conf.youtube.referrer_policy``
          - A referrer policy a browser knows, like ``no-referrer``,
            ``same-origin`` or ``strict-origin-when-cross-origin``.
        * - ``kaamiki.conf.release.kinds``
          - A list of lowercase names, like ``["security"]``, that are all
            different.
        * - ``kaamiki.conf.links.internal_hosts``,
            ``kaamiki.conf.embed.iframe_hosts``
          - A list of plain host names, like ``example.com``, that are all
            different. A host with ``*.`` in it stops the build.
        * - ``kaamiki.conf.embed.css``, ``kaamiki.conf.embed.js``
          - A list of ``.css`` and ``.js`` files that are in
            ``html_static_path``.
        * - ``kaamiki.conf.code_explain.events``
          - ``call``, ``line`` and ``return``, comma-separated.
        * - ``kaamiki.conf.site.feedback``, ``kaamiki.conf.site.license``,
            ``kaamiki.conf.site.open_graph``, ``kaamiki.conf.site.project``,
            ``kaamiki.conf.site.favicons``
          - A dict with only the keys listed for it, each of the type it takes.
            A ``kaamiki.conf.site.feedback`` ``url`` needs ``type`` ``link``,
            and the other way round.
        * - ``kaamiki.conf.release.version_fmt``,
            ``kaamiki.conf.site.last_updated_fmt``, ``html_last_updated_fmt``
          - A date format with only ``%a %A %b %B %d %H %I %j %m %M %p %S %y
            %Y %Z %z``. A release format must read back what it writes.

Kaamiki checks that an icon is written the right way. Without a kit it also
checks that Font Awesome Free has the icon, or a stand-in for it, and stops the
build when it doesn't. With a kit it can't know which Pro icons exist, so a
name Font Awesome doesn't know draws nothing there, and that's yours to check.

Templates are promised some settings as ``km_<name>``, :ref:`listed on the
advanced page <kaamiki-advanced-template-names>`, so if you override a
template, read ``km_toctree_in_header`` and not
``kaamiki.conf.toctree.in_header``.

.. _kaamiki-settings-site:

-------------------------------------------------------------------------------
Your site.
-------------------------------------------------------------------------------

Who you are and how the site presents itself.

.. accordion:: Every setting here

    .. list-table::
        :header-rows: 1
        :widths: 24 22 54

        * - Setting
          - Default
          - What it does
        * - ``kaamiki.conf.mode``
          - ``"dark"``
          - The site's colours. ``"dark"`` and ``"light"`` set them for every
            reader, whatever their device or browser says, with no colour
            button. ``"system"`` follows the reader's device and puts a round
            button in the footer, beside the copyright, that steps through
            light, dark and the device's setting each time it's clicked,
            showing the one it's on. Their pick is kept in their browser and
            wins over the device. In every mode the navbar is the same blurred
            glass over the page, with a subtle line under it. Any other value
            stops the build.
        * - ``kaamiki.conf.site.project``
          - ``{}``
          - A dictionary describing you. ``author`` falls back to Sphinx's
            ``author``, and a site with neither ships no author tag. ``email``
            powers the feedback box. ``source`` is where the byline links to.
            ``avatar`` is the byline's picture.
        * - ``kaamiki.conf.site.license``
          - ``{}``
          - ``name`` and an optional ``url`` for the licence line in the
            footer. A ``url`` without a ``name`` stops the build.
        * - ``kaamiki.conf.site.favicons``
          - ``{}``
          - Paths inside ``html_static_path``. Keys are ``ico``,
            ``size_96``, ``size_svg``, ``size_180`` and ``manifest``. Each one
            you give becomes a ``<link>`` and the rest are skipped. ``ico``
            takes the place of Sphinx's ``html_favicon``, which is still used
            when ``ico`` isn't given.
        * - ``kaamiki.conf.site.logo_size``
          - ``None``
          - The logo's size in pixels, between 8 and 64. Without it the theme's
            own size is used, and it stops the build where there's no logo.
        * - ``kaamiki.conf.site.logos``
          - ``{}``
          - Two logos, one for each colour, as files in ``html_static_path``:
            ``{"light": "logo-light.svg", "dark": "logo-dark.svg"}``. It needs
            both, and it stops the build if ``html_logo`` or the theme option
            ``logo`` is set too. The one that matches the colours the reader
            sees is shown.
        * - ``kaamiki.conf.site.open_graph``
          - ``{}``
          - Defaults for link previews. See :ref:`below <kaamiki-settings-og>`.
        * - ``kaamiki.conf.show.credit``
          - ``False``
          - Adds "Styled with the Kaamiki theme." to the footer.

The logo itself isn't a Kaamiki setting, unless you have one for each colour.
Use Sphinx's ``html_logo``, or the theme option ``logo`` for a file in
``_static``. If both are set, ``html_logo`` wins. A logo from ``html_logo``
that is all black is drawn white on dark and one that is all white is drawn
black on light, so one file works in both. A logo with colours of its own needs
``kaamiki.conf.site.logos``.

.. _kaamiki-settings-og:

Link previews
^^^^^^^^^^^^^

``kaamiki.conf.site.open_graph`` sets the site-wide defaults for how a page
looks when someone pastes its link into a chat or a social network. A page's
own ``:km-page-*:`` fields come first, then these, then whatever Kaamiki can
work out from the page itself.

.. accordion:: Every key

    .. list-table::
        :header-rows: 1
        :widths: 24 76

        * - Key
          - What it does
        * - ``image``
          - The preview picture. A relative path is made absolute with
            ``html_baseurl``, since previews ignore relative ones.
        * - ``image_alt``
          - Alt text for that picture. Only used while the page uses the site's
            picture.
        * - ``site_name``
          - The name shown above the title. Falls back to the project's title.
        * - ``type``
          - ``website`` unless you say otherwise.
        * - ``locale``
          - A locale like ``en_GB``.
        * - ``card``
          - The Twitter card. Defaults to ``summary_large_image``, or
            ``summary`` for a page with no picture.
        * - ``twitter_site``
          - Your handle, for the Twitter card.
        * - ``description``
          - The description for a page that has none of its own.
        * - ``description_length``
          - How many characters a generated description may run to, from 50
            to 300. Defaults to 200.
        * - ``enable``
          - Set it to ``False`` to switch previews off for the whole site.

For example, with this in ``conf.py``:

.. code-block:: python

    kaamiki.conf.site.open_graph = {
        "image": "_static/cover.png",
        "image_alt": "My site's cover",
        "site_name": "My Site",
        "locale": "en_GB",
    }

a page with no fields of its own gets the site's picture, name and locale, a
title taken from its heading and a description taken from its first paragraph.
:doc:`examples/link-preview` shows what a page gets when it sets its own.

.. _kaamiki-settings-chrome:

-------------------------------------------------------------------------------
Page furniture.
-------------------------------------------------------------------------------

The bits around your content. Every ``kaamiki.conf.show`` switch takes ``True``
or ``False``, and a page can override all of them except the ones marked
*site-wide*.

.. accordion:: Every setting here

    .. list-table::
        :header-rows: 1
        :widths: 28 14 58

        * - Setting
          - Default
          - What it does
        * - ``kaamiki.conf.show.breadcrumbs``
          - ``True``
          - The trail above the title, the pages above this one and then its
            own name. There's no home link, and a page that isn't nested shows
            no trail.
        * - ``kaamiki.conf.show.feedback``
          - ``None``
          - The feedback box. ``None`` means "on if there's somewhere to send
            it", which is a ``kaamiki.conf.site.project`` email or a
            ``kaamiki.conf.site.feedback`` URL. ``True`` with neither stops the
            build, and so does ``False`` with a ``kaamiki.conf.site.feedback``
            set.
        * - ``kaamiki.conf.show.more``
          - ``True``
          - Folds a long page behind a *Show more* button. Only pages that
            take ``kaamiki.conf.show.more_after`` minutes or more to read are
            folded, and only the content is: the feedback box and the previous
            and next links stay in view below it. A page the window already
            shows almost all of isn't folded either.
        * - ``kaamiki.conf.show.page_last_updated``
          - ``True``
          - The "Last updated on" line under the page, after the feedback box
            if there is one. It shows whenever this is on and the page has a
            date. The footer's own "Last updated on" line is Sphinx's
            ``html_last_updated_fmt`` and this switch doesn't control it.
        * - ``kaamiki.conf.show.previous_next_cards``
          - ``True``
          - A row of cards at the bottom of a page with the pages a reader
            meets next, as the next button would take them, then the ones
            before when fewer than
            ``kaamiki.conf.show.previous_next_cards_count`` come after. The
            front page is never a card. A page that lists
            :ref:`related pages <kaamiki-page-fields-related>` shows its own
            instead, and a page with no neighbours shows none. Switching
            this off needs ``kaamiki.conf.show.previous_next_pages`` on, since
            a page has to lead on somewhere, and a page that lists related
            pages needs it on too.
        * - ``kaamiki.conf.show.previous_next_cards_count``
          - ``5``
          - How many cards a page gets, from 1 to 7. A site with fewer pages
            shows the ones it has. It needs
            ``kaamiki.conf.show.previous_next_cards`` to be on and
            ``kaamiki.conf.show.previous_next_pages`` off.
        * - ``kaamiki.conf.show.previous_next_pages``
          - ``False``
          - The links to the neighbouring pages, as two round buttons at the
            bottom of a page, in place of the cards. They're off by default
            and a page that has none takes no room. A page that lists
            :ref:`related pages <kaamiki-page-fields-related>` shows those
            instead, whatever this says.
        * - ``kaamiki.conf.show.scrolltop``
          - ``False``
          - A round back-to-top button with an arrow, in the bottom right
            corner.
        * - ``kaamiki.conf.show.searchbox``
          - ``True``
          - The search in the header, an icon that opens into a box when it's
            hovered or focused, if you have a search page.
        * - ``kaamiki.conf.toctree.in_header``
          - ``True``
          - Where the navigation sits on wide screens. On, it's in the header
            as dropdowns on one row, and when they don't fit on one row, which
            is below 960 pixels and a little more for a long menu, it's in the
            menu like on a phone. Off, it's in a sidebar beside the content,
            which becomes the menu below 768 pixels. With scripts turned off
            there are no dropdowns, so the sidebar is used from 768 pixels
            either way.
        * - ``kaamiki.conf.show.not_found``
          - ``True``
          - Writes a ``404.html`` at the top of the output. A page of your own
            called ``404`` is kept and this one isn't written. Switching it off
            removes the ``404.html`` an earlier build wrote. *Site-wide*.
        * - ``kaamiki.conf.show.sitemap``
          - ``True``
          - Writes ``sitemap.xml`` and ``robots.txt``. Needs ``html_baseurl``
            and leaves out pages marked ``noindex``. Switching it off removes
            the two files an earlier build wrote. *Site-wide*.
        * - ``kaamiki.conf.show.more_after``
          - ``5``
          - The minutes of reading before a page is folded, from 3 to 8. It
            can't be set with ``kaamiki.conf.show.more`` off. *Site-wide*.
        * - ``kaamiki.conf.site.words_per_minute``
          - ``238``
          - How fast your readers read, used for the reading time. Only prose
            is counted, so code, tables and walkthrough notes are left out, and
            a set of tabs counts as its longest tab. A whole number from 100 to
            350. *Site-wide*.
        * - ``kaamiki.conf.site.last_updated_fmt``
          - ``""``
          - A date format for every date Kaamiki shows and for the date
            comments at the top of each page. Sphinx's
            ``html_last_updated_fmt`` counts only when this is empty. Without
            either, dates show as ``05 October 2026`` in your site's
            ``language``, and the comments use ``%d %B %Y``. The comments
            always have English month names, and one that doesn't follow the
            format stops the build with its file and line. *Site-wide*.
        * - ``kaamiki.conf.site.copy_headerlinks``
          - ``True``
          - Clicking a heading copies its link. *Site-wide*.

.. _kaamiki-settings-pages:

Overriding a switch from a page
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To override a switch, take its name, swap the underscores for dashes and put
``km-`` in front. A bare field means on and ``false`` means off:

.. code-block:: rst

    :km-toctree-in-header: false
    :km-show-scrolltop:
    :km-show-page-last-updated: false

Any other value, like ``maybe``, stops the build.

Here's one switch, the navigation, at each of the three levels:

.. list-table::
    :header-rows: 1
    :widths: 30 40 30

    * - Where
      - What you write
      - Navigation
    * - Nowhere
      - nothing
      - In the header, from the default
    * - ``conf.py``
      - ``kaamiki.conf.toctree.in_header = False``
      - In a sidebar on every page
    * - A page
      - ``:km-toctree-in-header:`` with no value
      - In the header on that page, even with the line above in ``conf.py``

:doc:`examples/overrides` is a page that moves its own navigation into a
sidebar, hides its breadcrumbs and neighbour links and turns the back-to-top
button on. Open it next to this page to see the difference.

.. _kaamiki-settings-nav:

Navigation
^^^^^^^^^^

.. accordion:: Every setting here

    .. list-table::
        :header-rows: 1
        :widths: 28 14 58

        * - Setting
          - Default
          - What it does
        * - ``kaamiki.conf.toctree.maxdepth``
          - ``0``
          - How deep the sidebar goes. ``0`` means no limit.
        * - ``kaamiki.conf.toctree.includehidden``
          - ``True``
          - Whether pages in ``:hidden:`` toctrees show up in the sidebar.
        * - ``kaamiki.conf.toctree.titles_only``
          - ``True``
          - Shows page titles and not their section headings.
        * - ``kaamiki.conf.site.header_buttons``
          - ``{}``
          - Buttons on the right of the header.
        * - ``kaamiki.conf.site.sidebar_buttons``
          - ``{}``
          - The same idea, listed under "External links" in the sidebar on
            phones.

Both button settings map a name to a dictionary:

.. code-block:: python

    kaamiki.conf.site.header_buttons = {
        "Sponsor": {
            "url": "https://github.com/sponsors/you",
            "icon": "fa-solid fa-heart",
        },
    }

The name is the tooltip. With an ``icon`` (an icon written as in
:ref:`kaamiki-settings-icons`) the button shows just the icon, and without one
it shows the name. ``extras`` is ``data-`` or ``aria-`` attributes for the
link, like ``'data-cal-link="you/30min"'`` for a booking widget, and anything
else stops the build. Both settings take ``extras``.

.. _kaamiki-settings-links:

-------------------------------------------------------------------------------
Links.
-------------------------------------------------------------------------------

.. accordion:: Every setting here

    .. list-table::
        :header-rows: 1
        :widths: 28 14 58

        * - Setting
          - Default
          - What it does
        * - ``kaamiki.conf.links.new_tab``
          - ``True``
          - Links to other sites open in a new tab. Turn it off to keep
            everything in the same tab.
        * - ``kaamiki.conf.links.internal_hosts``
          - ``[]``
          - Other hosts that count as part of your site, like a docs subdomain.
            Links to them stay in the same tab. The host in ``html_baseurl``
            always counts, and ``www.`` is ignored. A host matches itself and
            not its subdomains, so name the subdomain.

Email links never open a new tab. With ``html_baseurl`` set to
``https://example.com/``:

.. code-block:: rst

    `My GitHub <https://github.com/xames3>`_
    :doc:`The installation page <installation>`

The first leaves the site, so it opens in a new tab. The second stays on it.
With ``kaamiki.conf.links.internal_hosts = ["github.com"]`` the first would
stay in the same tab too.

.. _kaamiki-settings-feedback:

-------------------------------------------------------------------------------
Feedback box.
-------------------------------------------------------------------------------

The box at the end of a page asks readers what they think. By default the
button emails the address in ``project["email"]``. Set
``kaamiki.conf.site.feedback`` to change the words or point it elsewhere:

.. code-block:: python

    kaamiki.conf.site.feedback = {
        "title": "Spotted a mistake?",
        "description": "Tell me and I'll fix it.",
        "button": "Write to me",
        "split": True,
    }

.. accordion:: Every key

    .. list-table::
        :header-rows: 1
        :widths: 20 80

        * - Key
          - What it does
        * - ``title``, ``description``, ``button``
          - The three pieces of text. They default to Kaamiki's own words,
            "Feedback", "Tell us how this page can be improved." and "Submit",
            which follow your site's ``language``.
        * - ``icon``
          - A Font Awesome icon for the button.
        * - ``subject``
          - The email's subject. ``%s`` stands for the page's title, and the
            default is "Feedback about" followed by the title.
        * - ``type``
          - Set it to ``link`` to send readers to ``url`` instead of writing an
            email.
        * - ``url``
          - Where a ``link`` button goes. Also counts as somewhere to send
            feedback, so the box shows up without a
            ``kaamiki.conf.site.project`` email.
        * - ``split``
          - Puts the title and the button side by side. It needs an email in
            ``kaamiki.conf.site.project`` or a ``url``, since without those
            there's no button.

Every key has a page field of the same name: ``:km-feedback-title:``,
``:km-feedback-description:``, ``:km-feedback-button:``,
``:km-feedback-icon:``, ``:km-feedback-subject:``, ``:km-feedback-type:``,
``:km-feedback-url:`` and ``:km-feedback-split:``. The page wins over
``kaamiki.conf.site.feedback``, which wins over Kaamiki's words.
:doc:`examples/feedback` is a page that sets its own.

.. _kaamiki-settings-colours:

-------------------------------------------------------------------------------
Buttons and roles.
-------------------------------------------------------------------------------

These set the defaults for the ``button`` directive and a few inline roles.
The directive and the roles can still override them one by one.

.. accordion:: Every setting here

    .. list-table::
        :header-rows: 1
        :widths: 26 20 54

        * - Setting
          - Default
          - What it does
        * - ``kaamiki.conf.button.scheme``
          - ``"light"``
          - The colour of a button that doesn't ask for one. ``chevron`` here
            suits a button with no icon only, so one with ``:fa-icon:`` is
            ``light``.
        * - ``kaamiki.conf.button.colours``
          - ``{}``
          - Your own colour names for buttons, like ``{"brand": "#0a7"}``. Then
            ``:scheme: brand`` works.
        * - ``kaamiki.conf.button.icon_position``
          - ``"before"``
          - Whether a button's icon sits ``before`` or ``after`` its text.
        * - ``kaamiki.conf.roles.colours``
          - ``{}``
          - Colour names the roles understand, so ``:underline:`text <brand>```
            works and you needn't repeat a hex code.
        * - ``kaamiki.conf.roles.sharpie_colour``
          - ``"yellow"``
          - The default colour of the sharpie role.
        * - ``kaamiki.conf.roles.underline_colour``
          - ``"#FF9800"``
          - The default colour of the underline role.
        * - ``kaamiki.conf.roles.underline_width``
          - ``2.5``
          - The line's thickness.
        * - ``kaamiki.conf.roles.underline_wobble``
          - ``1.0``
          - How hand-drawn the line looks. ``0`` is dead straight.

A button with no options uses ``kaamiki.conf.button.scheme`` and
``kaamiki.conf.button.icon_position``:

.. code-block:: rst

    .. button:: https://github.com/xames3/website
        :fa-icon: arrow-right

        Default button

.. button:: https://github.com/xames3/website
    :fa-icon: arrow-right

    Default button

The button's own options beat the settings. ``:scheme:`` picks another colour
and ``:icon-position:`` moves the icon:

.. code-block:: rst

    .. button:: https://github.com/xames3/website
        :fa-icon: arrow-right
        :icon-position: after
        :scheme: green

        Green, icon after

.. button:: https://github.com/xames3/website
    :fa-icon: arrow-right
    :icon-position: after
    :scheme: green

    Green, icon after

To change the default for every button, set it in ``conf.py``. This makes every
button green with its icon after the text, so the first example above would
look like the second:

.. code-block:: python

    kaamiki.conf.button.scheme = "green"
    kaamiki.conf.button.icon_position = "after"

The schemes that come with Kaamiki are ``light``, ``dark``, ``chevron``,
``red``, ``yellow``, ``blue`` and ``green``. A name from
``kaamiki.conf.button.colours`` works in ``:scheme:`` and in
``kaamiki.conf.button.scheme`` too. A name that's neither stops the build and
lists the ones that work.

The sharpie and underline roles work the same way. With no colour they use
``kaamiki.conf.roles.sharpie_colour`` and
``kaamiki.conf.roles.underline_colour``, and a colour after the text wins:

.. code-block:: rst

    This is :sharpie:`important` information.
    This is :sharpie:`critical <red>` information.
    This is :underline:`notable` content.
    This is :underline:`notable <blue?width=4&wobble=0>` content.

This is :sharpie:`important` information.
This is :sharpie:`critical <red>` information.
This is :underline:`notable` content.
This is :underline:`notable <blue?width=4&wobble=0>` content.

A colour is ``red``, ``yellow``, ``blue``, ``green``, a hex colour, three hsl
numbers or a name you gave in ``kaamiki.conf.roles.colours``. With
``kaamiki.conf.roles.colours = {"brand": "#0a7"}`` in ``conf.py``,
``:sharpie:`text <brand>``` is a sharpie in that green.

.. _kaamiki-settings-accordions:

-------------------------------------------------------------------------------
Accordions.
-------------------------------------------------------------------------------

.. accordion:: Every setting here

    .. list-table::
        :header-rows: 1
        :widths: 26 20 54

        * - Setting
          - Default
          - What it does
        * - ``kaamiki.conf.accordion.marker``
          - ``"plus"``
          - What shows an accordion opens: ``"plus"``, ``"down"`` or
            ``"right"``. ``:marker:`` overrides it for one accordion.
        * - ``kaamiki.conf.accordion.marker_position``
          - ``"after"``
          - Whether an accordion's marker sits ``before`` or ``after`` its
            title. ``:marker-position:`` overrides it for one accordion.

.. _kaamiki-settings-tabs:

-------------------------------------------------------------------------------
Tabs.
-------------------------------------------------------------------------------

.. accordion:: Every setting here

    .. list-table::
        :header-rows: 1
        :widths: 26 20 54

        * - Setting
          - Default
          - What it does
        * - ``kaamiki.conf.tab.icon_position``
          - ``"before"``
          - Whether a tab's icon sits ``before`` or ``after`` its title.
            ``:icon-position:`` overrides it for one tab.

.. _kaamiki-settings-media:

-------------------------------------------------------------------------------
Pictures.
-------------------------------------------------------------------------------

A picture that's shown smaller than it is opens in a dialog when it's clicked.
Try this one, a 512px badge shown at 160px, and press Esc to close it:

.. figure:: /_static/favicons/web-app-manifest-512x512.png
    :width: 160px
    :alt: A blue verified badge with a white tick

    Press the badge.

:ref:`Classes <kaamiki-classes-pictures>` says which pictures open and how to
leave one out, and :ref:`How Kaamiki moves
<kaamiki-example-motion-a-picture-that-opens>` shows it fly.

.. accordion:: Every setting here

    .. list-table::
        :header-rows: 1
        :widths: 26 20 54

        * - Setting
          - Default
          - What it does
        * - ``kaamiki.conf.media.enlarge``
          - ``True``
          - A picture that's shown at least 10% smaller than it is, and would
            come out at least 10% bigger on the reader's screen (or whole,
            where the page shows it taller than the screen), opens in a dialog
            when it's clicked, tapped or opened with Enter or Space. A link, a
            video, a picture inside ``code-explain`` or ``code-version`` and
            one with ``km-no-enlarge`` are left alone. ``False`` turns it off.
            ``:km-media-enlarge:`` overrides it for one page, as :ref:`page
            fields <kaamiki-page-fields-media>` explain.

.. _kaamiki-settings-motion:

-------------------------------------------------------------------------------
Motion.
-------------------------------------------------------------------------------

Every animation in the theme can be made quicker or calmer with one number. A
reader who asks their device for less motion gets none of it, whatever you
set. :doc:`How Kaamiki moves <examples/motion>` shows every animation working.
A directive that moves can take a speed of its own, or play nothing, with
:ref:`:speed: and :no-motion: <kaamiki-directives-motion>`.

.. accordion:: Every setting here

    .. list-table::
        :header-rows: 1
        :widths: 26 20 54

        * - Setting
          - Default
          - What it does
        * - ``kaamiki.conf.motion.speed``
          - ``1``
          - How quick every animation is. ``2`` is twice as quick as the
            default and ``0.5`` is half as quick. It takes a number from
            ``0.25`` to ``4``, and anything else stops the build. A
            ``:ticker:`` that isn't given a time counts for 2 seconds over
            it. It's *site-wide*.
        * - ``kaamiki.conf.motion.page_transitions``
          - ``False``
          - Following a link to another page of the site hands over from one
            page to the next, one thing at a time and never two at once. The
            old content eases out, a little way in the direction the reader's
            going, and when it has gone the new page plays its own entrance,
            the one it plays when it loads, from its first frame. The header,
            the sidebar and the footer stay as they are, and going back slides
            the old content out the other way. A browser that can't (Firefox,
            for now) just loads the page, and a reader who asks for less
            motion gets no hand over at all. :ref:`Page to page
            <kaamiki-example-motion-page-to-page>` shows it. It's
            *site-wide*.
        * - ``kaamiki.conf.motion.prefetch``
          - ``True``
          - The page a link leads to is fetched as a reader reaches for it,
            when a pointer rests on the link or a finger touches it, so
            following it is quick. Once the page is quiet the next and the
            previous pages are fetched too. It does nothing for a reader who's
            saving data or on a slow connection, and ``False`` turns it off.
            It's *site-wide*.

.. _kaamiki-settings-releases:

-------------------------------------------------------------------------------
Releases.
-------------------------------------------------------------------------------

.. accordion:: Every setting here

    .. list-table::
        :header-rows: 1
        :widths: 26 20 54

        * - Setting
          - Default
          - What it does
        * - ``kaamiki.conf.release.version_fmt``
          - ``"%Y.%m.%d"``
          - How a version is spelt when it's really a date. A release whose
            version matches it needs no ``:date:``. Empty switches this off.
        * - ``kaamiki.conf.release.kinds``
          - ``[]``
          - The groups of your own for a release's notes. Kaamiki knows
            *Added*, *Changed*, *Deprecated*, *Fixed* and *Removed*. This is
            where you add more, like ``["security"]``. One of the five Kaamiki
            knows stops the build.

With the default format the version is the date, so this release needs nothing
else:

.. code-block:: rst

    .. release::
        :version: 2026.10.19

        Added
            - A new thing

        Fixed
            - An old thing

If your versions look like ``1.4.0`` they don't match, so give the release a
``:date:``:

.. code-block:: rst

    .. release::
        :version: 1.4.0
        :date: 19 October 2026

        Added
            - A new thing

.. _kaamiki-settings-icons:

-------------------------------------------------------------------------------
Icons.
-------------------------------------------------------------------------------

Kaamiki draws its icons with `Font Awesome`_, Free out of the box. A Pro kit
switches every icon to its Pro version, as CSS for a reader without JavaScript.
If Font Awesome doesn't load, because it's blocked, you're offline or a kit
refuses the address, the icons stay empty and show when Font Awesome loads. A
kit only answers the addresses on its allow-list in your Font Awesome account,
so a preview from another address gets no kit.

.. accordion:: Every setting here

    .. list-table::
        :header-rows: 1
        :widths: 20 24 56

        * - Setting
          - Default
          - What it does
        * - ``kaamiki.conf.icons.kit``
          - ``None``
          - The address of your kit script, like
            ``https://kit.fontawesome.com/abc123.js``, and only that form. With
            a kit you get the Pro icons, and ``kaamiki.conf.icons.style``
            decides how they are drawn. Without one, every icon is a Free one.
            When this is empty, Kaamiki reads the address from the
            ``KAAMIKI_FA_KIT`` environment variable, so a build server can
            bring the kit without it being written in ``conf.py``. The setting
            wins when both are given.
        * - ``kaamiki.conf.icons.style``
          - ``"regular"``
          - The style of every icon that doesn't name one. Takes ``solid``,
            ``regular``, ``light`` or ``thin``, and the last two need a kit,
            from ``kaamiki.conf.icons.kit`` or ``KAAMIKI_FA_KIT``.
        * - ``kaamiki.conf.icons.names``
          - ``{}``
          - Swaps one of Kaamiki's own icons for another.
        * - ``kaamiki.conf.byline.icon_style``
          - ``"regular"``
          - The style of the title's icon on a byline's banner and on the
            cards that link to the page. Takes ``solid``, ``regular``,
            ``light`` or ``thin``, or one of them after ``duotone``, as
            ``"duotone regular"``, for a duotone icon with its second layer
            faded. ``duotone`` alone is ``duotone solid``. It needs a kit:
            without one, the icon keeps the title's style. A brand stays a brand, and a byline's own
            ``:fa-icon:`` is drawn as written.

Without a kit, Kaamiki keeps to what Font Awesome Free has. Free draws far
fewer icons in the ``regular`` style than Pro does, so every icon is looked up
in that order. An icon Free has in ``regular`` is drawn that way and one it has
only in ``solid`` is drawn solid. ``light``, ``thin`` and ``duotone`` become
the closest Free style, and a Pro+ pack like ``fa-jelly`` becomes the Free icon
in its own style. ``kaamiki.conf.icons.style = "solid"`` makes every icon
solid where Free has one. A Pro icon with no Free twin has a stand-in:
``badge-check``, ``brackets-curly``, ``file-xml``, ``link-simple``,
``sparkles`` and ``table-columns-merge-previous``. Any other name Free doesn't
have stops the build with the nearest Free name, so a typo never draws a blank
square.

``kaamiki.conf.icons.names`` takes these names, and anything else stops the
build. Each one shows the icon Kaamiki uses with a kit and the Free one it uses
without:

.. accordion:: Every name

    .. list-table::
        :header-rows: 1
        :widths: 34 33 33

        * - Name
          - With a kit
          - Without a kit
        * - ``admonition_danger``
          - ``fa-regular fa-skull-crossbones``
          - ``fa-solid fa-skull-crossbones``
        * - ``admonition_error``
          - ``fa-regular fa-bug``
          - ``fa-solid fa-bug``
        * - ``admonition_hint``
          - ``fa-regular fa-lightbulb``
          - ``fa-solid fa-lightbulb``
        * - ``admonition_important``
          - ``fa-regular fa-star``
          - ``fa-solid fa-star``
        * - ``admonition_note``
          - ``fa-regular fa-circle-info``
          - ``fa-solid fa-circle-info``
        * - ``admonition_seealso``
          - ``fa-regular fa-globe``
          - ``fa-solid fa-globe``
        * - ``admonition_tip``
          - ``fa-regular fa-compass``
          - ``fa-solid fa-compass``
        * - ``admonition_warning``
          - ``fa-regular fa-triangle-exclamation``
          - ``fa-solid fa-triangle-exclamation``
        * - ``breadcrumb_separator_child``
          - ``fa-regular fa-angle-right``
          - ``fa-solid fa-angle-right``
        * - ``breadcrumb_separator_parent``
          - ``fa-regular fa-angles-right``
          - ``fa-solid fa-angles-right``
        * - ``close``
          - ``fa-regular fa-xmark``
          - ``fa-solid fa-xmark``
        * - ``copied``
          - ``fa-regular fa-check``
          - ``fa-solid fa-check``
        * - ``copy``
          - ``fa-regular fa-clipboard``
          - ``fa-solid fa-clipboard``
        * - ``copy_url``
          - ``fa-regular fa-link``
          - ``fa-solid fa-link``
        * - ``external_link``
          - ``fa-regular fa-arrow-up-right-from-square``
          - ``fa-solid fa-arrow-up-right-from-square``
        * - ``feedback``
          - ``fa-regular fa-paper-plane``
          - ``fa-regular fa-paper-plane``
        * - ``language``
          - ``fa-regular fa-language``
          - ``fa-solid fa-language``
        * - ``list_tick``
          - ``fa-regular fa-check``
          - ``fa-solid fa-check``
        * - ``menu``
          - ``fa-regular fa-bars``
          - ``fa-solid fa-bars``
        * - ``nav_arrow``
          - ``fa-solid fa-chevron-down``
          - ``fa-solid fa-chevron-down``
        * - ``page_source``
          - ``fa-regular fa-file-lines``
          - ``fa-regular fa-file-lines``
        * - ``play``
          - ``fa-regular fa-play``
          - ``fa-solid fa-play``
        * - ``reading_time``
          - ``fa-regular fa-clock``
          - ``fa-regular fa-clock``
        * - ``release_date``
          - ``fa-regular fa-calendar``
          - ``fa-regular fa-calendar``
        * - ``release_notes``
          - ``fa-solid fa-tag``
          - ``fa-solid fa-tag``
        * - ``repository_forks``
          - ``fa-solid fa-code-fork``
          - ``fa-solid fa-code-fork``
        * - ``repository_mark``
          - ``fa-brands fa-github``
          - ``fa-brands fa-github``
        * - ``repository_stars``
          - ``fa-solid fa-star``
          - ``fa-solid fa-star``
        * - ``scrolltop``
          - ``fa-regular fa-arrow-up``
          - ``fa-solid fa-arrow-up``
        * - ``search``
          - ``fa-regular fa-magnifying-glass``
          - ``fa-solid fa-magnifying-glass``
        * - ``show_more``
          - ``fa-regular fa-chevron-down``
          - ``fa-solid fa-chevron-down``

With a kit, the "With a kit" column follows ``kaamiki.conf.icons.style``.
``release_notes`` may be left empty with ``""``, so no icon appears. The other
names always need an icon. ``nav_arrow``, ``release_notes``,
``repository_forks``, ``repository_mark`` and ``repository_stars`` are drawn in
one style, whatever ``kaamiki.conf.icons.style`` says. Unless the site sets
``nav_arrow``, its arrow is written in the page as SVG, so it shows from the
first frame without the kit.

Write the icon in whichever way suits you. ``video``, ``fa-video`` and
``fa-solid fa-video`` all mean the same thing, and a bare name gets
``kaamiki.conf.icons.style``. A name that's only a brand, like ``github``, is
drawn as the brand. A family goes before the style, like
``fa-sharp fa-solid fa-video``, and a :ref:`Pro+ pack
<kaamiki-roles-fa-icon-packs>` needs no style, because it has only one, so
``fa-jelly fa-video`` is ``fa-jelly fa-regular fa-video``. A family takes only
its own styles, so ``fa-jelly fa-solid fa-video`` stops the build. To give a
swapped icon one version for each plan, write a
pair. Either half may be left out, and the other is used for both:

.. code-block:: python

    kaamiki.conf.icons.names = {
        "search": "magnifying-glass",
        "play": {
            "pro": "fa-regular fa-circle-play",
            "free": "fa-solid fa-play",
        },
    }

To add names to the ones already set, without writing the dictionary again,
call ``kaamiki.conf.icons.update`` with a dictionary or with keywords:

.. code-block:: python

    kaamiki.conf.icons.update(
        {"search": "magnifying-glass"}, play="circle-play"
    )

The icon of a ``kaamiki.conf.site.header_buttons`` or
``kaamiki.conf.site.sidebar_buttons`` entry, the ``icon`` of
``kaamiki.conf.site.feedback`` and the ``:km-feedback-icon:`` page field are
written the same way.

.. _Font Awesome: https://fontawesome.com/

.. _kaamiki-settings-embeds:

-------------------------------------------------------------------------------
Embeds and videos.
-------------------------------------------------------------------------------

.. accordion:: Every setting here

    .. list-table::
        :header-rows: 1
        :widths: 28 22 50

        * - Setting
          - Default
          - What it does
        * - ``kaamiki.conf.embed.iframe_hosts``
          - ``[]``
          - Hosts an embedded ``<iframe>`` may come from. When empty, nothing
            is checked. When set, anything else stops the build, and subdomains
            of a listed host are fine. It catches a mistake and not an author
            set on getting round it: a script can build a frame in pieces, so
            a script that builds an iframe stops the build, and so does a tag
            or ``srcdoc`` that loads a page some other way. The markup is read
            as a browser reads it, so the order of the attributes, a ``>`` in a
            quoted attribute or a backslash or extra slashes in the address
            don't get a frame past the list.
        * - ``kaamiki.conf.embed.css``, ``kaamiki.conf.embed.js``
          - ``[]``
          - Files every page with an embed loads, before the page's own.
        * - ``kaamiki.conf.embed.js_loading``
          - ``"defer"``
          - How those scripts load: ``defer``, ``async`` or ``normal``.
        * - ``kaamiki.conf.youtube.privacy``
          - ``False``
          - Uses YouTube's no-cookie player for every video, which Safari plays
            only after a second press. ``:no-privacy:`` turns it off for one
            player.
        * - ``kaamiki.conf.youtube.click_to_load``
          - ``True``
          - Shows the video's picture with a play button for every video and
            loads the player on a click. ``:auto-load:`` turns it off
            for one player.
        * - ``kaamiki.conf.youtube.allow``
          - Sensible list
          - The iframe's ``allow`` permissions.
        * - ``kaamiki.conf.youtube.referrer_policy``
          - ``"strict-origin-when-cross-origin"``
          - The iframe's referrer policy.

For example, to only allow embeds from YouTube and your own subdomain:

.. code-block:: python

    kaamiki.conf.embed.iframe_hosts = ["youtube.com", "demo.example.com"]

An embed from any other host stops the build with a message naming the host
and the ones allowed.

.. _kaamiki-settings-code-explain:

-------------------------------------------------------------------------------
Code-explain.
-------------------------------------------------------------------------------

A ``code-explain`` in Python runs the code at build time, in a separate
process, and records every step, once ``kaamiki.conf.code_explain.run`` is
``True``. These settings are its limits. A snippet can ask for *less* than
what's set here, never more, and one that asks for more stops the build.

The process works in a scratch directory that's deleted afterwards, but that's
its working directory and not a sandbox. It runs as the user that builds the
site, so it can read what that user can read, the build's own environment too
(through ``/proc`` on Linux), write anywhere that user can and reach the
network. The limits cover memory, CPU and wall-clock time and how much it may
write or print. Whatever it left running is killed when it ends. They stop a
runaway snippet and aren't a sandbox. Keep secrets out of any build that runs
Python snippets and don't switch it on for pull requests from people you don't
trust.

.. accordion:: Every setting here

    .. list-table::
        :header-rows: 1
        :widths: 30 18 52

        * - Setting
          - Default
          - What it does
        * - ``kaamiki.conf.code_explain.run``
          - ``False``
          - Lets a ``code-explain`` in Python run. Off, it stops the build with
            an error that names this setting. Another language is never run,
            and ``code-version`` runs nothing either way. It needs a POSIX
            system like Linux or macOS, and ``True`` on any other stops the
            build.
        * - ``kaamiki.conf.code_explain.limit``
          - ``100``
          - The most steps a snippet may ask to show.
        * - ``kaamiki.conf.code_explain.budget``
          - ``25``
          - How many raw trace events are collected for each step shown, so
            Kaamiki stops a runaway after ``limit * budget`` events.
        * - ``kaamiki.conf.code_explain.timeout``
          - ``10``
          - The most seconds a snippet may run.
        * - ``kaamiki.conf.code_explain.memory``
          - ``1024``
          - Megabytes of memory the whole run may use, every process the
            snippet starts added together. The system is asked to enforce it
            where it can, and the build also watches the memory the run's
            processes hold and stops one that goes past it, so the limit is
            never skipped. The build fails with "a run that used more than 1024
            MB of memory".
        * - ``kaamiki.conf.code_explain.output_limit``
          - ``64``
          - The most megabytes any one file a snippet writes may take, and the
            most it may print.
        * - ``kaamiki.conf.code_explain.events``
          - ``"line, return"``
          - What makes a step: ``call``, ``line`` or ``return``.
        * - ``kaamiki.conf.code_explain.comprehensions``
          - ``False``
          - Step into comprehensions, which each carry a frame of their own.
        * - ``kaamiki.conf.code_explain.python``
          - ``None``
          - The interpreter that runs snippets. By default it's the one running
            the build. It can't be set with ``kaamiki.conf.code_explain.run``
            off, since nothing runs.
        * - ``kaamiki.conf.code_explain.pythonpath``
          - ``[]``
          - Directories snippets can import from. Relative ones count from the
            source directory.
        * - ``kaamiki.conf.code_explain.cache``
          - ``True``
          - Keeps each trace with Sphinx's doctrees, so an unchanged snippet
            isn't run twice. A snippet that raised is never kept. Deleting the
            build folder clears it.

With ``kaamiki.conf.code_explain.limit = 50`` in ``conf.py``, a
``code-explain`` can ask for ``:limit: 20`` but ``:limit: 80`` stops the build,
naming the setting that refused it. The directive and its options are covered
with the other directives.

