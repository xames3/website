.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 19 October 2026
.. Last updated on: 27 November 2026

:km-page-title: Kaamiki page fields
:km-page-description: The fields you can put at the top of a page to change its
    link preview, feedback box, header, pictures and layout, shown on real
    pages.
:km-page-type: article
:km-header-subheader: Per-page control over preview, feedback, pictures and
    layout
:km-feedback-title: Is a field missing?
:km-feedback-description: Tell me what you'd want to change from a page.
:km-feedback-button: Tell me

.. _kaamiki-page-fields:

===============================================================================
:fa-icon:`file-lines fa-swap-opacity` Page fields
===============================================================================

.. rst-class:: km-text-lead

    Lines at the top of a page that change how Kaamiki treats that page alone.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3
    :shade: teal

Page fields are ordinary reStructuredText fields, so there's nothing to install
or switch on. Write them before the title:

.. code-block:: rst

    :km-page-description: What this page is about.
    :km-feedback-title: Did this help?

    ===========
    Page title
    ===========

Every field starts with ``km-`` and then a short group, which tells you what
it's for:

- ``km-page-*`` fields are about the page itself: its link preview, its
  neighbours, its language and whether search engines see it.
- ``km-feedback-*`` fields are about the feedback box at the end of the page.
- ``km-header-*`` fields are about the page's line in the header's dropdowns.
- ``km-related-*`` fields are about the row of related pages at the end of the
  page.
- ``km-media-*`` fields are about the pictures on the page.
- ``km-show-*`` fields switch the page's furniture on or off.

Each one overrides the matching setting in ``conf.py``, so a page only
writes the fields it wants to change. Every field is checked: one that's
spelt wrong, a value it doesn't take, a ``km-show-*`` that isn't ``true`` or
``false``, a ``:km-page-prev:`` that isn't another page and the dates in the
header comments (a day from 2000 to a year ahead, like ``5 October 2026``)
all stop the build with a message that names the page and the line of
the field. :ref:`Which value wins <kaamiki-settings-precedence>` explains the
order.

.. _kaamiki-see-them-on-real-pages:

-------------------------------------------------------------------------------
See them on real pages.
-------------------------------------------------------------------------------

Three pages of this site set fields of their own. Open one next to this page to
see what the fields do:

.. block:: Overriding settings
    :size: small
    :doc: examples/overrides

    Four switches, flipped from one page.

.. block:: The feedback box
    :size: small
    :doc: examples/feedback

    Words, subject and layout of its own.

.. block:: A link preview
    :size: small
    :doc: examples/link-preview

    The tags a page's fields write.

.. _kaamiki-page-fields-rules:

-------------------------------------------------------------------------------
Writing a field.
-------------------------------------------------------------------------------

A field is the name between two colons, then the value on the same line:

.. code-block:: rst

    :km-page-type: article

A long value carries on over the next lines, indented:

.. code-block:: rst

    :km-page-description: A long description that doesn't fit on one line, so
        it carries on here.

Fields go before the title, one after another, with no blank lines between
them. Comments such as ``.. Author:`` can sit above them. A field that doesn't
start with ``km-``, like Sphinx's own ``:orphan:``, is left alone. A ``km-``
field Kaamiki doesn't read stops the build and names the nearest one it does,
so a typo or an old name is caught at once.

A field that switches something on or off, like ``:km-feedback-split:``, is
*on* when you leave the value out and *off* with ``false``. Any other value
stops the build.

.. code-block:: rst

    :km-feedback-split:
    :km-toctree-in-header: false

.. _kaamiki-page-fields-header:

The comments above the fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Three comments at the top of a file are read by Kaamiki, so they're worth
keeping:

.. code-block:: rst

    .. Author: Your Name <you@example.com>
    .. Created on: 19 October 2026
    .. Last updated on: 19 October 2026

They give the page its author and the dates in its link preview, above its
title and in its "Last updated" line. Above the title, the day it was created
follows the part of the site it's in, as on its cards. Any of them you leave
out is filled in for you. A missing date comes from git, from the first commit
for *created* and the latest for *updated*, and then from the day you build.
A missing author comes from the page's ``byline`` directive and then from your
``kaamiki.conf.site.project`` setting. Only the comments before the first line
of the page count, so a date quoted further down is ignored.

The dates follow ``kaamiki.conf.site.last_updated_fmt``, then
``html_last_updated_fmt``, and without either ``%d %B %Y``, as above. Month and
day names are in English and a day has two digits, so it's ``05 October 2026``
and not ``5 October 2026`` or ``2026-10-05``. A date in another form stops the
build with the file, the line and the setting.

.. _kaamiki-page-fields-preview:

-------------------------------------------------------------------------------
Link preview.
-------------------------------------------------------------------------------

These fields set what appears when someone shares the page's link. Each one
overrides the same key in the ``kaamiki.conf.site.open_graph`` setting.

.. accordion:: The fields

    .. list-table::
        :header-rows: 1
        :widths: 28 72

        * - Field
          - What it does
        * - ``:km-page-title:``
          - The title in the preview, up to 120 characters. Defaults to the
            page's heading. The browser tab keeps the heading, after the
            site's name, either way. A page needs a heading with words in it,
            and one with none, or only an icon, stops the build.
        * - ``:km-page-description:``
          - The description in the preview and in the page's ``description``
            tag, up to 300 characters. Defaults to the page's lead, then the
            site's ``description`` and last the page's first paragraph.
        * - ``:km-page-image:``
          - The preview picture, as a path or a full address. Defaults to the
            site's ``image``.
        * - ``:km-page-image-alt:``
          - Alt text for that picture.

        * - ``:km-page-type:``
          - An Open Graph type: ``website``, ``article``, ``book``,
            ``profile``, ``music.song``, ``music.album``, ``music.playlist``,
            ``music.radio_station``, ``video.movie``, ``video.episode``,
            ``video.tv_show`` or ``video.other``. Any other word stops the
            build. An ``article`` also gets its published and modified dates
            and its author.
        * - ``:km-page-locale:``
          - A locale like ``en_GB``.
        * - ``:km-page-card:``
          - The Twitter card, ``summary`` or ``summary_large_image``. A page
            with no picture always uses ``summary``.

The page's lead is the paragraph you mark with the ``km-text-lead`` class (see
:ref:`kaamiki-classes` for how classes are written), which sits right under the
title:

.. code-block:: rst

    .. rst-class:: km-text-lead

        One line that sums the page up.

:doc:`examples/link-preview` is a page that sets some of these and shows the
tags Kaamiki wrote for it.

.. note::

    Setting ``"enable": False`` under ``kaamiki.conf.site.open_graph`` in
    ``conf.py`` turns the Open Graph and Twitter tags off for the whole site.
    The ``description`` tag stays.

.. _kaamiki-page-fields-feedback:

-------------------------------------------------------------------------------
Feedback box.
-------------------------------------------------------------------------------

The feedback box fields mirror the ``kaamiki.conf.site.feedback`` setting, key
for key.

.. accordion:: The fields

    .. list-table::
        :header-rows: 1
        :widths: 28 72

        * - Field
          - What it does
        * - ``:km-feedback-title:``
          - The heading of the box.
        * - ``:km-feedback-description:``
          - The line under the heading.
        * - ``:km-feedback-button:``
          - The button's text.
        * - ``:km-feedback-icon:``
          - A Font Awesome icon for the button, written the way
            :ref:`icons are written <kaamiki-settings-icons>` in settings.
        * - ``:km-feedback-subject:``
          - The email's subject. ``%s`` becomes the page's title.
        * - ``:km-feedback-type:``
          - ``link`` sends readers to ``:km-feedback-url:`` instead of writing
            an email.
        * - ``:km-feedback-url:``
          - Where a ``link`` button goes. It goes with
            ``:km-feedback-type: link`` and only then, and a page with one and
            not the other stops the build.
        * - ``:km-feedback-split:``
          - Puts the title and the button side by side. It stops the build
            where there's no button to put beside the title.

A box has a button, so it needs somewhere to send: an email in
``kaamiki.conf.site.project``, a link in ``kaamiki.conf.site.feedback`` or a
``:km-feedback-url:`` on the page. A site with none has no box, and a page
that gives its own link gets one. To turn the box off for one page, use
``:km-show-feedback: false``, and ``:km-show-feedback:`` on a page with nowhere
to send feedback stops the build. See
:doc:`examples/feedback` for a page that sets several of these.

.. _kaamiki-page-fields-nav:

-------------------------------------------------------------------------------
Neighbours and the header.
-------------------------------------------------------------------------------

.. accordion:: The fields

    .. list-table::
        :header-rows: 1
        :widths: 28 72

        * - Field
          - What it does
        * - ``:km-page-prev:``
          - The page the "previous" link goes to.
        * - ``:km-page-next:``
          - The page the "next" link goes to.
        * - ``:km-header-subheader:``
          - The line under this page's title in the header's
            dropdowns, up to 120 characters.
        * - ``:km-header-no-subheader:``
          - Leaves that line out for this page.

Sphinx works out the previous and next pages from your toctrees, so a page that
isn't in one, an orphan, gets neither. These two fields give it a pair. They
take a document name the way ``:doc:`` does, so a name that doesn't start with
``/`` is relative to the page. They also win over the toctree on a page that
has both:

.. code-block:: rst

    :orphan:
    :km-page-prev: installation
    :km-page-next: /docs/kaamiki/settings

A name that isn't a document, or is the page itself, stops the build with a
message like this one:

.. code-block:: text

    field :km-page-next: expected another page, got 'settings'

The header's dropdowns show a short line under each page's title. Kaamiki picks
it in this order: ``:km-header-subheader:``, then the page's lead, then
``:km-page-description:``, cut to 90 characters. A page with none of those has
no line. Use ``:km-header-no-subheader:`` to remove the line from a page that
would otherwise get one, as long as it has no ``:km-header-subheader:`` of its
own.

.. _kaamiki-page-fields-related:

-------------------------------------------------------------------------------
Related pages.
-------------------------------------------------------------------------------

.. accordion:: The fields

    .. list-table::
        :header-rows: 1
        :widths: 28 72

        * - Field
          - What it does
        * - ``:km-related-docs:``
          - From 1 to 7 pages, split by commas, shown as a row of cards at the
            end of the page.
        * - ``:km-related-skip-page:``
          - Keeps this page out of the cards, like an index page that is only a
            list of links: it's no card on other pages and has none of its own.
            It's a switch, on when the value is left out.
        * - ``:km-related-header:``
          - A title for the row of up to 120 characters, set the way a
            carousel's title is, with the arrows on its line. It's plain text,
            so a role or an icon in it is left out, and one with no words stops
            the build. Without it the row says "More to read." in the site's
            language.

A page with ``:km-related-docs:`` gets a carousel of cards under its feedback
box, where the previous and next buttons would be, and goes without those
buttons. A page without it gets cards too, the pages a reader meets next, five
of them by default, when ``kaamiki.conf.show.previous_next_cards`` is on, as it
is unless you turn it off (see :ref:`settings <kaamiki-settings-pages>`). A
page at the end of the site gets the ones before it. A site with fewer pages
shows the ones it has. The front page is never one of these cards. Three cards
show at once on a wide screen and one and a bit on a phone, and the arrows
scroll the rest. Each card is the page's :ref:`banner
<kaamiki-byline-banner>`, then the part of the site it's in, the day it was
created and its title, which keeps to two lines and is written as the header's
menus write it: an icon stays and every other role is plain text:

.. code-block:: rst

    :km-related-header: Keep reading.
    :km-related-docs: installation, /docs/kaamiki/settings, ../journal/index

The names are the ones ``:doc:`` takes, so a name that doesn't start with ``/``
is relative to the page. A page that's missing, the page itself, a page named
twice or an eighth page stops the build. So does ``:km-related-header:``
without ``:km-related-docs:``, and so does ``:km-related-docs:`` on a page
whose cards are off, either by ``:km-show-previous-next-cards: false`` or by
``kaamiki.conf.show.previous_next_cards``.

A page with ``:km-related-skip-page:`` is passed over when the cards are worked
out, so the next page after it is used instead, and naming it in
``:km-related-docs:`` stops the build, as does ``:km-related-docs:`` on the
page itself, since it has no cards to list.

.. _kaamiki-page-fields-robots:

-------------------------------------------------------------------------------
Search engines.
-------------------------------------------------------------------------------

``:km-page-robots:`` writes a ``robots`` tag for the page and takes the usual
values, separated by commas:

.. code-block:: rst

    :km-page-robots: noindex, nofollow

A page marked ``noindex`` or ``none`` is also left out of ``sitemap.xml`` and
of the site's own search, so its words aren't in the search index.

.. _kaamiki-page-fields-language:

-------------------------------------------------------------------------------
The language it's written in.
-------------------------------------------------------------------------------

``:km-page-language:`` says what language this page is written in, and the
page's byline shows it when the byline asks with ``:show-language:``. It takes
a language code that Babel knows, like ``en``, ``hi`` or ``pt-BR``, and
``pt_BR`` works too:

.. code-block:: rst

    :km-page-language: hi

The field wins over the site's ``language``, so only this page changes. Without
it the byline shows ``language`` from ``conf.py``, which is English unless you
set it. A code Babel doesn't know stops the build at the field, with a message
like this one:

.. code-block:: text

    field :km-page-language: expected a language code like en, hi or pt-BR, got
    'zz'

The byline writes the language's name in its own words and as plain text.
:ref:`The byline directive <kaamiki-byline-languages>` says more about it.

.. _kaamiki-page-fields-show:

-------------------------------------------------------------------------------
Page furniture.
-------------------------------------------------------------------------------

Every ``kaamiki.conf.show`` setting except ``kaamiki.conf.show.not_found``,
``kaamiki.conf.show.sitemap``, ``kaamiki.conf.show.more_after`` and
``kaamiki.conf.show.previous_next_cards_count`` has a field of the same name,
with dashes for the underscores, and so does
``kaamiki.conf.toctree.in_header``:

``:km-show-breadcrumbs:``, ``:km-show-feedback:``, ``:km-show-credit:``,
``:km-show-more:``, ``:km-show-page-last-updated:``,
``:km-show-previous-next-cards:``, ``:km-show-previous-next-pages:``,
``:km-show-scrolltop:``,
``:km-show-searchbox:`` and ``:km-toctree-in-header:``.

They're explained in :ref:`settings <kaamiki-settings-pages>`, and
:doc:`examples/overrides` shows four of them on a real page. ``:km-show-more:``
only decides whether a page that's long enough is folded. A short page never
is, whatever it says.

.. _kaamiki-page-fields-media:

-------------------------------------------------------------------------------
Pictures.
-------------------------------------------------------------------------------

``kaamiki.conf.media.enlarge`` has a field of its own, ``:km-media-enlarge:``.
With ``false`` the pictures on that page stay where they are and nothing opens
when they're pressed, which suits a page that has a viewer of its own. A bare
field turns it on for one page of a site that has it off:

.. code-block:: rst

    :km-media-enlarge: false

:ref:`Settings <kaamiki-settings-media>` says which pictures open, and
:ref:`How Kaamiki moves <kaamiki-example-motion-a-picture-that-opens>` has one
to press.

.. _kaamiki-page-fields-translate:

-------------------------------------------------------------------------------
Translating fields.
-------------------------------------------------------------------------------

If your site is in another language, the text fields can be translated like any
other text in the page. ``:km-page-title:``, ``:km-page-description:``,
``:km-page-image-alt:``, ``:km-header-subheader:``, ``:km-feedback-title:``,
``:km-feedback-description:`` and ``:km-feedback-button:`` are collected into
your message catalogue when you run ``sphinx-build -b gettext``, so a
translator sees them next to the rest of the page.
