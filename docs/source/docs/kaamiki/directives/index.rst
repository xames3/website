.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 19 October 2026
.. Last updated on: 19 November 2026

:km-page-title: Kaamiki directives
:km-page-description: The directives Kaamiki adds to reStructuredText, shown
    working, and how they all behave.
:km-page-type: article
:km-header-subheader: Bylines, buttons, tabs, videos and more
:km-feedback-title: Is a directive missing?
:km-feedback-description: Tell me what you'd want to write in reStructuredText.
:km-feedback-button: Tell me

.. _kaamiki-directives:

===============================================================================
:fa-icon:regular:`cubes` Directives
===============================================================================

.. rst-class:: km-text-lead

    Everything you write with ``.. name::``, shown the way it looks.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3

Directives are the building blocks you write in reStructuredText. Kaamiki adds
the ones below on top of Sphinx's own, and each one on this page is live. List
``"kaamiki"`` in ``extensions`` and name the theme in ``html_theme``, as
:doc:`../installation` shows, and they all work.

Every one of them, with every option on and off and inside every other it can
go in, is on the :doc:`combinations pages <../combinations/index>`.

.. _kaamiki-say-who-wrote-it:

-------------------------------------------------------------------------------
Say who wrote it.
-------------------------------------------------------------------------------

The line under this page's title is a :doc:`byline <byline>`: the author, how
long the page takes to read, a button that copies its link and a way to see
its source. Next to it, a :doc:`repository <repository>` card shows a GitHub
project:

.. columns:: 2
    :valign: middle
    :gap: large

    .. column::

        .. repository:: xames3/xsnumpy

            Re-implementing NumPy features in Python.

    .. column::

        **repository** shows a project with its stars and forks, counted when
        the page loads. :doc:`Read more <repository>`.

.. _kaamiki-lay-it-out:

-------------------------------------------------------------------------------
Lay it out.
-------------------------------------------------------------------------------

.. columns:: 2
    :valign: middle
    :gap: large

    .. column::

        .. accordion:: Content that folds away

            Under a title that opens on a click.

    .. column::

        **accordion** folds content away. :doc:`Read more <accordion>`.

    .. column::

        .. tabs::

            .. tab:: One

                One block at a time.

            .. tab:: Two

                Under a row of titles.

    .. column::

        **tabs** show one block at a time. :doc:`Read more <tabs>`.

    .. column::

        .. block:: A card
            :size: small

            A title and some content.

    .. column::

        **block** frames a title and some content, and can link. :doc:`Read
        more <block>`.

.. carousel::

    .. block:: One
        :size: small

        Swipe to the next.

    .. block:: Two
        :size: small

        And the one after.

    .. block:: Three
        :size: small

        Then back again.

**carousel** sets blocks, pictures, repositories, thumbnails and buttons in a
row to swipe through, with arrows. A title, with ``:preheader:`` above it and
``:subheader:`` under it, makes it read like a section. ``:auto-run:`` moves it
on its own, and ``:direction:`` says which way. :doc:`Read more <carousel>`.

Pieces of content side by side, in one to six :doc:`columns <columns>`, are
what lay out the rest of this page.

.. _kaamiki-link-to-things:

-------------------------------------------------------------------------------
Link to things.
-------------------------------------------------------------------------------

.. columns:: 2
    :valign: middle
    :gap: large

    .. column::

        .. button:: https://example.com
            :scheme: green

            A button

    .. column::

        **button** is a link with a colour and an icon. :doc:`Read more
        <button>`.

A **release** writes one entry of a changelog, with its date and a timeline
beside it. :doc:`Read more <release>`.

.. release::
    :version: 0.9.0
    :date: 2026-10-01

    Added
        - A new thing

.. _kaamiki-bring-things-in:

-------------------------------------------------------------------------------
Bring things in.
-------------------------------------------------------------------------------

.. columns:: 2
    :valign: middle
    :gap: large

    .. column::

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY

    .. column::

        **video**, **youtube** and **thumbnail** put video on a page.
        :doc:`Read more <media>`.

    .. column::

        .. embed:: iframe
            :message: Your own HTML

            <p><strong>{{ message }}</strong></p>

    .. column::

        **embed** is a block of your own HTML, with placeholders. :doc:`Read
        more <embed>`.

.. _kaamiki-walk-through-code:

-------------------------------------------------------------------------------
Walk through code.
-------------------------------------------------------------------------------

**code-explain** steps a reader through a snippet a line at a time with the
values each line held, and **code-version** shows the versions a piece of code
went through. They need room, so they have :doc:`a page of their own
<explainers>` where you can scroll through them.

.. _kaamiki-directives-rules:

-------------------------------------------------------------------------------
How they all behave.
-------------------------------------------------------------------------------

A few things are the same everywhere, so I'll say them once.

Options are checked, all of them. Kaamiki takes what an option accepts or
it stops the build. That's the right word and the right case, a number inside
the range, an address, an icon, a colour or a class written the way it takes.
A misspelt option, a value that isn't one, a number that's valid but absurd
(``:gap: 9999rem``), an empty body and options that don't go together
(``:interval:`` without a second ``:backdrop:``, ``:end:`` before
``:start:``) are all errors. Nothing is clamped, corrected or guessed.

The message is Kaamiki's own. It names the file and the line and says what it
expected and what it got, as in "block: :doc: expected a document of this site,
got 'columns'". The build stops there and never carries on with a warning, so
you fix one mistake at a time.

Kaamiki does the same for any Docutils error on any page, such as an unknown
role or a mistake in a field, whether or not one of its directives caused it.
The build stops at the first one, with or without ``-W``.

Every directive takes ``:class:`` and ``:name:``, which are
:ref:`written the way Docutils' own directives take them
<kaamiki-directives-common>`.

Options are named the same way everywhere. Where a thing links to is
``:target:``, an address, with ``:doc:`` and ``:ref:`` for a document and a
label. A flag that turns something on is a bare word, like ``:autoplay:``.
One that turns off a behaviour starts with ``no-``, like ``:no-privacy:``,
one that hides a part of what's drawn with ``hide-``, like
``:hide-controls:``, and one that swaps a default for its opposite is a word of
its own, like ``:same-tab:``. A list of names, like ``:class:``, is split by
spaces and a list of values, like the addresses in ``:sources:``, by commas.

Colour has three words. A scheme is a whole look, like the ``light``,
``dark`` and ``chevron`` of a button or any of its colours. A colour is a
value, like ``#7c3aed`` or the name of one you gave. A tone is one of the named
hues the theme draws with, ``red``, ``yellow``, ``blue`` and ``green``.

Some directives are once a page. ``byline`` is written once on a page, a
``release`` version once on a page and a ``name`` once on a page.

Some directives belong to the page itself. ``byline``, ``code-explain``
and ``code-version`` go in the body of a page, not inside an accordion, a tab,
a column, a block, a note, a list, a container or a release. A byline describes
the page and not a part of it. A walkthrough needs the page's width to scroll
its notes past the code, so inside any of those it would fall back to the
stacked view a phone gets. Writing one there stops the build and names what it
is in.

A ``release`` belongs in a section. It goes directly on the page or under a
heading, and ``.. only::`` around it is fine, but not inside an accordion, a
tab, a column, a block, a note, a list or another release. Writing one there
stops the build and names what it is in.

The notes of a walkthrough hold prose. A ``lines`` or ``attempt`` note
takes paragraphs, lists, code, tables, figures, admonitions and buttons. An
accordion, tabs, columns, carousel, block, release, repository, thumbnail,
video, youtube, embed or a block of raw HTML in one stops the build.

Some directives need room. The text on a page is 675px wide at most, so a
column is about 335px. A ``columns`` doesn't go in a ``column`` that shares its
row or in a small or medium ``block``, and a ``block`` doesn't go in a
``block``, since a card in a card draws no frame of its own. A ``carousel``
doesn't go in a ``column`` either, since a row of cards needs more room than
that. Writing one there stops the build.

A label is one paragraph. What you write under a ``button`` is its label
and what you write under a ``repository`` is its description. Each is one
paragraph of text, and a list, a second paragraph or a directive in it stops
the build.

A link doesn't hold a link. A button's label, a thumbnail's title, channel and
caption, a byline's name, an accordion's preheader, title and subheader, a
tab's title and the preheader, title, subheader and footer of a block that
links are a link or sit in one. ``:email:``, a hyperlink, ``:ref:`` or
``:doc:`` in one stops the build, and so does ``:roll:`` in a tab's title,
which would move the row of titles, and in a button's label or a thumbnail's
title, channel or caption, which the script doesn't run inside a link.

Links work out whether to open a new tab. Any directive that links somewhere
follows ``kaamiki.conf.links.new_tab`` and
``kaamiki.conf.links.internal_hosts``, so a link to another site opens in a new
tab and one to your own doesn't. A directive with a ``:new-tab:`` or
``:same-tab:`` option, like ``button``, lets you decide for one link.

Text inside a directive is parsed. A caption, a label or a note can use
roles and inline markup like any paragraph.

A title, a label or a caption needs words. An icon adds to them and never
stands for them, so ``accordion``, ``tab``, ``block``, ``button``,
``carousel``, ``release``, ``byline``, ``thumbnail``, ``video``, ``youtube``
and ``repository`` stop the build for one that's only an icon, and so does a
page whose heading is only an icon, or has none. The same goes for a custom
``admonition``, which is named by its title. ``note``, ``tip``, ``warning`` and
the other built-in kinds are named by their kind and may show just their icon.

Defaults come from the settings on ``kaamiki.conf`` in ``conf.py``. When a
directive has an option and a setting for the same thing, the option wins.
:ref:`Settings <kaamiki-settings-precedence>` explains the order.

.. _kaamiki-directives-common:

-------------------------------------------------------------------------------
Options every directive takes.
-------------------------------------------------------------------------------

``:class:`` and ``:name:`` work as they do on Docutils' own directives, such as
``note`` and ``image``, and Kaamiki checks what it's given on top.

``:class:`` takes names separated by spaces. Each one is made into a class the
way Docutils does it, so ``Foo_Bar`` is ``foo-bar`` and ``9lives`` is
``lives``. A comma and a space between names does no harm, but a comma with no
space after it joins two names into one class, so ``big,red`` is ``big-red``.
A name with no letter in it, one that's more than 64 characters long and more
than eight names stop the build. ``:class-title:``,
``:class-body:`` and the other ``:class-*:`` options read their names the same
way.

``:name:`` takes any text. Docutils makes the id from it, so ``My Note`` is
linked to as ``my-note``. A name with no letter in it, one with a control
character and one that's more than 64 characters long stop the build, and so
does a name that's already on the page.

.. _kaamiki-directives-motion:

-------------------------------------------------------------------------------
Speed and motion.
-------------------------------------------------------------------------------

Every animation in the theme takes its time from the site's speed, the
:ref:`kaamiki.conf.motion.speed <kaamiki-settings-motion>` setting. A directive
that moves can take its own, or none, with two options:

.. list-table::
    :header-rows: 1
    :widths: 22 78

    * - Option
      - What it does
    * - ``:speed:``
      - How quick everything in the directive moves, a step of the site's
        speed. ``2`` is twice as quick, ``0.5`` half as quick and ``1`` the
        site's own. It takes ``0.25``, ``0.5``, ``0.75``, ``1``, ``1.5``,
        ``2``, ``3`` or ``4``, and anything else stops the build with the list.
    * - ``:no-motion:``
      - Plays nothing in the directive: every transition and animation in it
        ends as it starts, a ``:roll:`` or a ``:sweep:`` keeps its first
        phrase, a ``:ticker:`` shows its number and a ``byline`` keeps a still
        background.

``accordion``, ``tabs``, ``carousel``, ``byline``, ``repository`` and
``release`` take both. ``code-explain`` and ``code-version`` take
``:no-motion:``, which keeps them stacked, and not ``:speed:``, since their
``:pace:`` is :ref:`how far a step scrolls <kaamiki-code-explain-options>`:

.. code-block:: rst

    .. accordion:: Quick to open
        :speed: 4

        Done before you've seen it start.

    .. tabs::
        :no-motion:

        .. tab:: One

            Still.

        .. tab:: Two

            Also still.

A reader who asks their device for less motion gets the calmer version whatever
a directive's speed says, and ``:no-motion:`` goes no further than the
directive it's on. :doc:`How Kaamiki moves </docs/kaamiki/examples/motion>`
has an accordion of each kind to open.

.. toctree::
    :hidden:
    :maxdepth: 1

    byline
    repository
    accordion
    tabs
    columns
    block
    carousel
    button
    release
    media
    embed
    explainers
