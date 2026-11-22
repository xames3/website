.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 19 October 2026
.. Last updated on: 22 November 2026

:km-page-title: The byline directive
:km-page-description: Show who wrote a page, how long it takes to read and a
    button that copies its link.
:km-page-type: article
:km-header-subheader: Who wrote it, and how long it takes
:km-feedback-title: Is a byline missing something?
:km-feedback-description: Tell me which option you'd want.
:km-feedback-button: Tell me

.. _kaamiki-byline:

===============================================================================
:fa-icon:regular:`user` byline
===============================================================================

.. rst-class:: km-text-lead

    Who wrote the page, and how long it takes to read.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3

The byline under this title is the directive itself. It shows who wrote the
page, a picture, how long the page takes to read, a button that copies the
page's link and, on the right, a link to the page's source, "Show". It shows
where you put it, so put it right under the title and its lead. On a phone only
the author and the reading time stay. The text after ``::`` is the name, read
like any paragraph, so it can hold markup but not a link, since it's the link
to the author's profile:

.. code-block:: rst

    .. byline:: @xames3
        :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
        :target: https://github.com/xames3

A page has one byline, and it goes on the page itself. Inside an accordion, a
tab, a column, a block, a note, a list or a container it stops the build.

.. _kaamiki-byline-fallbacks:

-------------------------------------------------------------------------------
It fills in the rest.
-------------------------------------------------------------------------------

With nothing but a name, the byline uses your ``kaamiki.conf.site.project``
setting for the rest. The picture, the link and the new-tab behaviour all come
from there, and a link to another site opens in a new tab:

.. code-block:: python

    kaamiki.conf.site.project = {
        "author": "Your Name",
        "avatar": "https://example.com/me.png",
        "source": "https://example.com",
    }

.. code-block:: rst

    .. byline:: Your Name

The directive also tells the rest of the page about itself:

- The name becomes the page's author, which is written into the ``author`` tag
  and, for an ``article``, into the link preview. A ``.. Author:`` comment at
  the top of the file wins when it names someone.
- The reading time counts the prose on the page, using
  ``kaamiki.conf.site.words_per_minute``, and a set of tabs counts as its
  longest tab. It's never shown as less than one minute.
- The source link goes to the page's plain-text copy that Sphinx puts in
  ``_sources`` while ``html_copy_source`` is on, and ``html_sourcelink_suffix``
  says how it ends. It reads "Show" for an ``.rst`` page, "View as Markdown"
  for an ``.md`` one and "View source" for anything else. With
  ``html_copy_source`` or ``html_show_sourcelink`` off there's no link.

.. _kaamiki-byline-languages:

-------------------------------------------------------------------------------
The language it's written in.
-------------------------------------------------------------------------------

The byline names the language the page is written in when you ask with
``:show-language:``. It writes the name from Sphinx's ``language`` in that
language's own words. It's plain text, with no picker and no link to a build in
another language, and ``language`` is English unless you set it:

.. code-block:: python

    language = "fr"

A page can say its own with the page field ``:km-page-language:``, like
``:km-page-language: hi``, which wins over ``language``. :ref:`Page fields
<kaamiki-page-fields-language>` says more.

Without ``:show-language:`` the byline says nothing about it. With it, the
byline leaves the language out when it would make the row wrap, on a narrow
phone or beside a long name, and shows it again once there's room.

.. _kaamiki-hide-what-you-dont-need:

-------------------------------------------------------------------------------
Hide what you don't need.
-------------------------------------------------------------------------------

``:hide-reading-time:``, ``:hide-copy-url:`` and ``:hide-source:`` each take a
part away:

.. code-block:: rst

    .. byline:: @xames3
        :hide-reading-time:
        :hide-source:

.. _kaamiki-byline-options:

-------------------------------------------------------------------------------
Every option.
-------------------------------------------------------------------------------

.. accordion:: The full table

    .. list-table::
        :header-rows: 1
        :widths: 24 76

        * - Option
          - What it does
        * - ``:avatar:``
          - The address of the author's picture. Falls back to the ``avatar``
            in your ``kaamiki.conf.site.project`` setting.
        * - ``:target:``
          - Where the name links to, a profile or a ``mailto:`` link. A path
            counts from the top of the site, like ``:avatar:``. Falls back to
            ``source`` in
            ``kaamiki.conf.site.project``.
        * - ``:avatar-size:``
          - The picture's width and height in pixels, from 16 to 64. Defaults
            to 20. It needs an avatar, from ``:avatar:`` or
            ``kaamiki.conf.site.project``.
        * - ``:align:``
          - Where the byline sits: ``left``, ``center`` or ``right``. Only
            ``left`` puts the author, the reading time, the language (when
            shown) and the copy button in one row, and a phone cuts that row
            to the author and the reading time. Defaults to ``left``.
        * - ``:hide-reading-time:``
          - Hides the reading time, which is shown without it.
        * - ``:hide-copy-url:``
          - Hides the copy-link button, which is shown without it.
        * - ``:hide-source:``
          - Hides the link to the page's source, which is shown without it
            while ``html_copy_source`` and ``html_show_sourcelink`` are on.
        * - ``:show-language:``
          - Shows the page's language, which is hidden without it.
        * - ``:name:``
          - A name to link to, as :ref:`every directive takes it
            <kaamiki-directives-common>`.
        * - ``:class:``
          - Extra classes for the byline.
        * - ``:speed:``
          - How quick its motion is, a step of the site's speed, as
            :ref:`every directive that moves takes it
            <kaamiki-directives-motion>`.
        * - ``:no-motion:``
          - Plays nothing in it, as :ref:`every directive that moves takes it
            <kaamiki-directives-motion>`.
