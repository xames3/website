.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 28 October 2026
.. Last updated on: 16 November 2026

:km-page-title: Advanced Kaamiki
:km-page-description: What a Sphinx author who wants more control needs to
    know: Kaamiki's custom properties, how to override its templates, what a
    build writes and the odds and ends it handles for you.
:km-page-type: article
:km-header-subheader: Tokens, templates, build outputs and the odds and ends
:km-feedback-title: Is something missing here?
:km-feedback-description: Tell me what you'd want to override or know.
:km-feedback-button: Tell me

.. _kaamiki-advanced:

===============================================================================
:fa-icon:regular:`gear` Advanced
===============================================================================

.. rst-class:: km-text-lead

    For when the settings aren't enough.

This page is for people who already know how Sphinx finds a theme, loads a
stylesheet and looks up a template. Everything here is something you can lean
on. Nothing here is needed to use Kaamiki.

.. block:: Tokens
    :size: small
    :ref: kaamiki-advanced-tokens

    Change a colour, a font or a speed.

.. block:: Templates
    :size: small
    :ref: kaamiki-advanced-templates

    Replace a part of a page, or all of it.

.. block:: The build
    :size: small
    :ref: kaamiki-advanced-build

    What it writes besides your pages.

.. _kaamiki-advanced-tokens:

-------------------------------------------------------------------------------
Everything of Kaamiki's says km-.
-------------------------------------------------------------------------------

Every class, id, data attribute, custom property and template variable Kaamiki
owns starts with ``km-``, ``--km-`` or ``km_``, and a page's own fields are
``:km-page-*:``. So nothing of Kaamiki's can collide with Sphinx's, your
extensions' or yours, and a rule written against ``km-`` is a rule about
Kaamiki.

The custom properties are the easy way to change how it looks. They're all
declared on ``:root``, so a stylesheet you load afterwards wins at the same
specificity. ``html_css_files`` loads yours after Kaamiki's:

.. code-block:: python

    html_static_path = ["_static"]
    html_css_files = ["mine.css"]

.. code-block:: css
    :caption: _static/mine.css

    :root {
        --km-colour-red: 120 60% 40%;
        --km-font-sans: "Source Sans 3", sans-serif;
    }

A ``--km-colour-*`` is three numbers, a hue and two percentages, and not a
colour, because Kaamiki writes ``hsl(var(--km-colour-red))`` and mixes them
with other values. ``color-scheme`` follows ``kaamiki.conf.mode``, so it's
``dark`` by default.

.. accordion:: The families of tokens

    .. list-table::
        :header-rows: 1
        :widths: 28 72

        * - Starts with
          - What it sets
        * - ``--km-colour-``
          - The palette: greys, the four hues and what each part of the page
            uses, like ``--km-colour-link``, ``--km-colour-code-bg`` and the
            ``--km-colour-button-*`` states. The focus ring is
            ``--km-colour-focus`` and the quiet text of bylines, captions and
            the footer is ``--km-colour-meta``, two greys that keep their
            contrast on the dark page.
        * - ``--km-font-``
          - The two families, ``--km-font-sans`` and ``--km-font-mono``, and
            the sizes, like ``--km-font-size-base``.
        * - ``--km-weight-``, ``--km-tracking-``
          - How heavy and how tightly set the headings, the lead and a button
            are.
        * - ``--km-layout-``
          - Widths and heights: the text column, which pictures and videos stop
            at, the wider one code uses, the sidebar, the shell and the
            header's height.
        * - ``--km-space-``
          - The spacing scale. ``--km-space-1`` is a quarter of a ``rem`` and
            every step is another quarter, so ``--km-space-4`` is ``1rem`` and
            ``--km-space-0-5`` is an eighth. Every margin, padding and gap of
            the theme is one of them, so a change to a step changes the rhythm
            of the whole site and scales with the reader's text size.
        * - ``--km-backdrop-``
          - The blur and tint behind the phone's menu.
        * - ``--km-radius-``
          - The three corner sizes, ``--km-radius-round``,
            ``--km-radius-normal`` and ``--km-radius-tiny``.
        * - ``--km-duration-``, ``--km-ease-``, ``--km-spring-``
          - How long and how smooth every motion is. ``--km-motion-speed`` is
            the dial that scales every duration, ``0.625`` by default and ``2``
            for twice as quick as ``1``. The theme turns motion down for a
            reader who asks for less.
        * - ``--km-reveal-``
          - How a page fades in, block by block.
        * - ``--km-nav-``, ``--km-title-skip``
          - How a page hands over to the next, with
            ``kaamiki.conf.motion.page_transitions`` on. ``--km-nav-out`` is
            how long the old content takes to leave (0.6 of
            ``--km-motion-fade``), ``--km-nav-dir`` which way it drifts (``1``,
            or ``-1`` going back), ``--km-nav-hold`` the longest the old
            page's header, sidebar and footer are held for while the new page
            loads (1.5 of ``--km-motion-enter``) and ``--km-title-skip`` how
            far into its fade the new page's first thing starts (0.35 of
            ``--km-duration-slow``), so there's something to see as the old
            content goes. ``data-km-nav`` on the root says which way the reader
            went.
        * - ``--km-code-``
          - The padding, line height and caption bar of code blocks.
        * - ``--km-layer-``
          - The stacking order of the header, dropdowns and the rest.
        * - ``--km-show-more-``
          - How tall a folded page is, how it fades and where its button docks.
        * - ``--km-swap-``, ``--km-sweep-``, ``--km-ticker-``,
            ``--km-tooltip-``
          - How long the swap role holds a word (4000ms, the roll itself takes
            ``--km-motion-state`` and each letter starts
            ``--km-motion-stagger`` after the one before), how long the sweep
            role rests between phrases (``--km-sweep-hold``, 5500ms), how long
            a sweep takes (``--km-sweep-duration``) and the colours of its
            light (``--km-sweep-colours``), how long a ticker counts
            (``--km-ticker-duration``, 2000ms over the site's speed, 3200ms by
            default) and how long a tooltip stays (1800ms).
        * - ``--km-motion-ambient``
          - How long a loop that never ends takes for a round (1600ms over the
            site's speed).

The colours that matter most to a brand have a setting that needs no CSS:
``kaamiki.conf.button.colours`` and ``kaamiki.conf.roles.colours`` take names
of your own, as :ref:`buttons and roles <kaamiki-settings-colours>` shows.

.. _kaamiki-advanced-templates:

-------------------------------------------------------------------------------
Replace a part of a page.
-------------------------------------------------------------------------------

Kaamiki's templates are found the way Sphinx finds any theme's, so a file of
the same name in your ``templates_path`` replaces it. To change a part and keep
the rest, extend the theme's own with Sphinx's ``!`` prefix and fill a block:

.. code-block:: python

    templates_path = ["_templates"]

.. code-block:: jinja
    :caption: _templates/layout.html

    {%- extends "!layout.html" %}
    {%- block km_footer_after %}
        <p>Built by me.</p>
    {%- endblock km_footer_after %}

A directive's template works the same way, under ``directives/``. This one
replaces what ``button`` writes with a plain link:

.. code-block:: jinja
    :caption: _templates/directives/button.html.jinja

    {% block km_button %}
        <a class="mine-button" href="{{ kaamiki.directive.url }}">
            {{- kaamiki.directive.text -}}
        </a>
    {% endblock km_button %}

The pieces a page includes, like ``components/breadcrumbs.html.jinja``, are
replaced by a file of the same name too. All three kinds work, and each one
does what it says in a build of its own.

.. accordion:: The blocks you can fill

    .. list-table::
        :header-rows: 1
        :widths: 30 70

        * - Block
          - Where it sits
        * - ``km_header_before``, ``km_header_after``
          - Before and after the header.
        * - ``km_header_left``, ``km_website_logo``
          - The header's left side and the logo in it.
        * - ``km_header_right``, ``km_mobile_menu``, ``km_header_buttons``
          - The header's right side, the phone's menu button and the buttons.
        * - ``km_sidebar``, ``km_main``, ``km_aside``
          - The sidebar, the content column and a column beside it.
        * - ``km_footer_before``, ``km_footer_after``
          - Before and after the footer.
        * - ``km_body_before``, ``km_body_after``, ``km_feedback``
          - In ``page.html``: above and below a page's content, and the
            feedback box.
        * - ``km_social``, ``km_thirdparty``, ``km_icons``
          - In the ``<head>``: the link-preview tags, the Font Awesome kit's
            script and its stylesheet.
        * - ``km_button``, ``km_byline``, ``km_carousel_arrows``,
            ``km_release``, ``km_repository``, ``km_video``, ``km_youtube``,
            ``km_youtube_thumbnail``
          - What each directive writes, in ``directives/``. The carousel's
            block is its arrows.

Sphinx's own blocks, like ``extrahead`` and ``scripts``, are there as well.

The sidebar is Kaamiki's ``sections/sidebar.html.jinja``, which ``theme.toml``
names, so ``html_sidebars`` means what Sphinx says. The default list has only
that template. An empty list for a page removes the sidebar and the header's
menu button, and so does a list that doesn't name it. Any other template you
name, a file in your ``templates_path``, is drawn after it in the sidebar
column, and a name that isn't a template stops the build. The layout options of
Sphinx's basic theme, like ``nosidebar``, ``sidebarwidth`` and
``body_max_width``, stop the build in ``html_theme_options``: the sidebar is
fixed and the ``kaamiki.conf.toctree`` settings set the navigation.

.. _kaamiki-advanced-template-names:

.. accordion:: What a template can read

    A template reads one name, ``kaamiki``, with the same paths as
    ``kaamiki.conf`` in ``conf.py``: ``kaamiki.show.breadcrumbs`` is
    ``kaamiki.conf.show.breadcrumbs``. Each setting is there, with its default
    when the site sets none and with a page's own fields already applied. The
    values are read only, and a name that isn't one stops the build with the
    nearest name, so a typo can't hide.

    - Worked out in place of the setting: ``kaamiki.show.feedback`` is
      ``True`` or ``False`` from the email and the feedback address when the
      setting is ``None``; ``kaamiki.icons.kit`` is the kit the build uses;
      ``kaamiki.site.project`` has its defaults and the author;
      ``kaamiki.site.license``, ``kaamiki.site.header_buttons`` and
      ``kaamiki.site.sidebar_buttons`` also say if each link opens a new tab.
    - Worked out next to the settings: ``kaamiki.icons.roles``, the class of
      each icon; ``kaamiki.toctree.args``; ``kaamiki.links.rel``;
      ``kaamiki.site.title``, which is ``html_title`` or the project's name;
      ``kaamiki.credit.url`` and ``kaamiki.credit.new_tab``;
      ``kaamiki.fa_free.css`` and ``kaamiki.fa_free.integrity``.
    - Set for each page: ``kaamiki.site.feedback``, the feedback box's words;
      ``kaamiki.site.open_graph``, the link preview tags;
      ``kaamiki.embed.css`` and ``kaamiki.embed.js``, the files the page's
      embeds load, the site's first; ``kaamiki.toctree.header``, the
      navigation with each page's lead; ``kaamiki.page.author``, the page's
      author, which is empty when neither the page nor the site names one;
      ``kaamiki.page.updated_on``, the day it was last updated; and
      ``kaamiki.page.related``, the row of cards that takes the place of the
      previous and next buttons, or ``None`` when a page has none.

    A directive's template also reads the values of its own options under
    ``kaamiki.directive``, as ``kaamiki.directive.url``,
    ``kaamiki.directive.text``, ``kaamiki.directive.look`` and so on, next to
    every name above. An option the page leaves out is undefined there, and
    any other name stops the build. Read the shipped template to see them.

.. note::

    Keep ``role="main"`` on the element that holds a page's content. Sphinx's
    search reads each result's summary from ``[role="main"]`` and shows a
    result with no snippet without it.

.. _kaamiki-advanced-build:

-------------------------------------------------------------------------------
What the build writes.
-------------------------------------------------------------------------------

Besides your pages, a build adds a few things. Each has a switch or a way to
leave it out:

.. list-table::
    :header-rows: 1
    :widths: 30 70

    * - It writes
      - How to control it
    * - ``sitemap.xml`` and ``robots.txt``
      - Needs ``html_baseurl``. Pages marked ``noindex`` are left out. A
        ``robots.txt`` of yours in ``html_extra_path`` is kept.
        ``kaamiki.conf.show.sitemap`` turns both off.
    * - ``404.html`` at the top of the output
      - ``kaamiki.conf.show.not_found`` turns it off. A ``404.html`` in your
        ``templates_path`` replaces it, and a page of your own called ``404``
        is kept, so Kaamiki's isn't written.
    * - Canonical links
      - Come from ``html_baseurl``.
    * - The browser tab's title
      - ``<site> - <page title>``. ``<site>`` is ``html_title`` or, without
        one, ``project``, and the home page shows only that.
    * - Open Graph and Twitter tags
      - From a page's ``:km-page-*:`` fields, then
        ``kaamiki.conf.site.open_graph``. ``"enable": False`` turns them off.
    * - ``description``, ``author`` and ``robots`` tags
      - From the page's own fields and its ``byline``.
    * - Favicon links
      - From ``kaamiki.conf.site.favicons``.
    * - Minified stylesheets and the fonts
      - The stylesheets pass through ``lightningcss`` as the build finishes.
        Inter and Geist Mono ship with the theme, with their licences, so the
        fonts load from your own site. Icons come from Font Awesome.

A file Kaamiki wrote in an earlier build goes when this build doesn't write it,
so switching ``kaamiki.conf.show.not_found`` or ``kaamiki.conf.show.sitemap``
off doesn't leave the old one behind. Each starts with a comment saying Kaamiki
wrote it, and only a file with that comment is removed, so a ``404.html`` or a
``robots.txt`` of your own stays. The build log says which went.

Two more ways reach the settings. ``-D kaamiki_<group>_<name>=value`` on the
command line wins over ``conf.py``, entry by entry for the settings that are
dictionaries, like ``-D kaamiki_site_open_graph.enable=0``, as
:ref:`On the command line <kaamiki-settings-command-line>` shows.
``KAAMIKI_FA_KIT`` names your Font Awesome kit from the environment when
``kaamiki.conf.icons.kit`` doesn't. Kaamiki has no page for the general index,
so ``html_use_index`` is left off, with a warning if you set it to ``True``.
Kaamiki has three warnings, ``kaamiki.css`` for a stylesheet it couldn't
minify, ``kaamiki.settings`` for that ``html_use_index`` and
``kaamiki.errors`` for a Sphinx that has moved its error handler, so Kaamiki's
errors print as Sphinx's. All three can be quieted through
``suppress_warnings``. Everything else it finds wrong stops the build,
and that includes an embed with a ``{{ key }}`` placeholder that no option
fills.

.. _kaamiki-advanced-misc:

-------------------------------------------------------------------------------
Misc things Kaamiki does.
-------------------------------------------------------------------------------

The odds and ends that you only notice when they're missing.

.. _kaamiki-languages:

Languages
^^^^^^^^^

Everything the theme writes reads in your site's ``language``. Kaamiki ships
English, and its own words join Sphinx's catalogue, so the words you translate
in your own project win over the theme's. Any other language falls back to
English until you give it words. Make a
``locale/fr/LC_MESSAGES/sphinx.po`` with only the words you want to change:

.. code-block:: python

    language = "fr"
    locale_dirs = ["locale"]

.. code-block:: po
    :caption: locale/fr/LC_MESSAGES/sphinx.po

    msgid "Skip to content"
    msgstr "Aller au contenu"

``sphinx-build -b gettext`` collects a page's ``:km-page-*:`` and
``:km-feedback-*:`` words and a directive's text too, so a translator sees them
next to the rest of the page. The theme's own catalogue,
``kaamiki/locale/sphinx.pot``, lists every word it writes.

.. _kaamiki-supported-browsers:

Browsers
^^^^^^^^

The stylesheets are built for these versions and newer: Chrome and Edge 120,
Firefox 121, Safari and iOS Safari 17, Opera 106 and Samsung Internet 25. The
script needs nothing else, and a browser without scripting still gets every
page's content.

.. _kaamiki-content-security-policy:

Content Security Policy
^^^^^^^^^^^^^^^^^^^^^^^

If your host sends a Content Security Policy, a few things need allowing. Every
page has one inline script, which sets the theme up before the page paints. It
has no nonce, because a static page can't carry a new one for each response, so
allow it by its hash or with ``'unsafe-inline'`` in ``script-src``, and the
browser names the hash in the console. Directives and roles write inline
``style`` attributes for button colours, tickers, the logo size and the
underline role, so ``style-src`` needs ``'unsafe-inline'`` or
``style-src-attr``. The default Font Awesome stylesheet comes from
``ka-f.fontawesome.com``, pinned to a release and carrying a subresource
integrity hash. A kit's script from ``kit.fontawesome.com`` loads ``async``
without one. Allow ``ka-f.fontawesome.com`` for the stylesheet and the fonts,
and ``kit.fontawesome.com`` as well when you use a kit.

.. _kaamiki-everything-else:

Everything else
^^^^^^^^^^^^^^^

Builders
    HTML is what Kaamiki is for. It takes ``html``, ``dirhtml`` and
    ``linkcheck``. Any other builder, like ``singlehtml``, ``epub`` or
    ``latex``, stops the build.

Parallel builds
    ``-j`` is safe, and a page is read again when a setting that shapes it
    changes, so you never need ``-E`` to see one.

Dates
    A page's dates come from its header comments, then from git, then from the
    day you build. They're written in your ``language``, in the format of
    ``kaamiki.conf.site.last_updated_fmt`` or ``html_last_updated_fmt``.

Reading time
    Prose only, at ``kaamiki.conf.site.words_per_minute`` (100 to 350), never
    less than a minute.

New tabs
    A link to another host opens in one, as ``kaamiki.conf.links.new_tab`` and
    ``kaamiki.conf.links.internal_hosts`` say.

Headings
    A click on one copies its link. ``kaamiki.conf.site.copy_headerlinks``
    turns that off.

Long pages
    A page, or an accordion, taller than a screen folds behind a Show more
    button. ``kaamiki.conf.show.more`` and ``kaamiki.conf.show.more_after`` set
    when.

Scrolling parts
    A code block, a table, a row of tabs or the phone's menu that has more to
    show fades the edge it goes on past, and fades the other edge once it has
    been scrolled.

Breadcrumbs
    A page inside another shows the pages above it and then itself. A page
    with nothing above it shows none, but keeps the room, so its title sits
    where every other page's does. The whole trail shows while it fits. On a
    narrower screen the middle pages fold into a ``...`` that links to the
    nearest of them, and the name of the page itself shortens last.

Motion
    A reader who asked for less gets a still background and no animated
    reveal.

Large sites
    Sphinx draws the whole toctree on every page, so a site of thousands of
    pages still takes time in proportion to the pages squared.

Versions
    Python 3.14 or newer and Sphinx 9.1 or newer.
