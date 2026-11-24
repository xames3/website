.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 October 2026
.. Last updated on: 23 November 2026

:km-page-title: Combinations
:km-page-description: Every Kaamiki directive written with every option on and
    off, with icons and roles and with every other directive, one page each.
:km-page-type: article
:km-header-subheader: Every directive, in every combination
:km-feedback-title: Is a combination missing?
:km-feedback-description: Tell me which directives you tried together that
    didn't work.
:km-feedback-button: Tell me
:km-feedback-icon: fa-shapes

.. _combos-index:

===============================================================================
:fa-icon:duotone:`shapes` Combinations
===============================================================================

.. rst-class:: km-text-lead

    Every directive, in every combination.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3
    :shade: purple

The icons page showed every place an icon can go. These pages do the same for
every directive: each option on and off, icons and roles in it and every other
directive inside it and around it, with the markup written out under every
result.

.. _combos-index-one-page-for-each-directive:

-------------------------------------------------------------------------------
One page for each directive.
-------------------------------------------------------------------------------

.. block:: Accordion
    :size: medium
    :doc: accordion
    :preheader: :fa-icon:regular:`square-plus` Content that folds away.

    Every way to use it.

.. block:: Tabs
    :size: medium
    :doc: tabs
    :preheader: :fa-icon:regular:`folders` Content that switches.

    Every way to use it.

.. block:: Columns
    :size: medium
    :doc: columns
    :preheader: :fa-icon:regular:`table-columns` Content side by side.

    Every way to use it.

.. block:: Block
    :size: medium
    :doc: block
    :preheader: :fa-icon:regular:`rectangle-list` Content in a card.

    Every way to use it.

.. block:: Carousel
    :size: medium
    :doc: carousel
    :preheader: :fa-icon:regular:`rectangle-history` Cards in a row to swipe.

    Every way to use it.

.. block:: Button
    :size: medium
    :doc: button
    :preheader: :fa-icon:regular:`arrow-pointer` A link as a pill.

    Every way to use it.

.. block:: Byline
    :size: medium
    :doc: byline
    :preheader: :fa-icon:regular:`user` Who wrote it.

    Every way to use it.

.. block:: Embed
    :size: medium
    :doc: embed
    :preheader: :fa-icon:regular:`code` Your own HTML.

    Every way to use it.

.. block:: code-explain
    :size: medium
    :doc: code-explain
    :preheader: :fa-icon:regular:`list-check` Code stepped through.

    Every way to use it.

.. block:: code-version
    :size: medium
    :doc: code-version
    :preheader: :fa-icon:regular:`code-compare` Code changing.

    Every way to use it.

.. block:: Release
    :size: medium
    :doc: release
    :preheader: :fa-icon:regular:`tag` A changelog entry.

    Every way to use it.

.. block:: Repository
    :size: medium
    :doc: repository
    :preheader: :fa-icon:brands:`github` A GitHub project.

    Every way to use it.

.. block:: Thumbnail
    :size: medium
    :doc: thumbnail
    :preheader: :fa-icon:regular:`image` A video card.

    Every way to use it.

.. block:: Video
    :size: medium
    :doc: video
    :preheader: :fa-icon:regular:`film` A video file.

    Every way to use it.

.. block:: YouTube
    :size: medium
    :doc: youtube
    :preheader: :fa-icon:brands:`youtube` A YouTube player.

    Every way to use it.

.. _combos-index-what-each-page-has:

-------------------------------------------------------------------------------
What each page has.
-------------------------------------------------------------------------------

The pages share a shape, so any directive can be read the same way:

.. list-table::
    :header-rows: 1
    :widths: 32 68

    * - Section
      - What it shows
    * - The options, one at a time
      - The directive with each option on and off, one change at a time.
    * - With icons
      - Where an icon can go in it.
    * - With roles
      - Each role in its text.
    * - Holding every other directive
      - For a container, every other directive written inside it.
    * - Inside every other container
      - For a directive that can go there, written in an accordion, a tab, a
        column, a block, a note and a list item.
    * - Where it can't go
      - For byline, code-explain and code-version, each container that stops
        the build, with the message. A release and a columns have a section
        of their own for it.

.. _combos-index-what-cant-be-combined:

-------------------------------------------------------------------------------
What can't be combined.
-------------------------------------------------------------------------------

Nearly everything goes in everything. A byline, a code-explain and a
code-version belong to the page itself, so any container stops the build, and
so does one of them in another's notes. A release belongs in a section, so it
stops the build in an accordion, a tab, a column, a block, a list, a note and
another release. The notes of a walkthrough take no accordion, tabs, columns,
carousel, block, release, repository, thumbnail, video, youtube, embed or raw
HTML. A block takes no block. A column that shares its row, a small block and a
medium block take no columns. A carousel takes only a block, a button, a
figure, an image, a repository and a thumbnail, and goes in no carousel, no
column and no block that links. A button, a thumbnail, an accordion title and a
tab title take no link. A page can hold one byline, a tab set needs two tabs
and a release version can be written once on the site, so each release here has
a version of its own. A ``hide-controls`` video needs ``autoplay``. The pages
say where one of these applies.

.. _combos-index-icons-and-roles:

-------------------------------------------------------------------------------
Icons and roles.
-------------------------------------------------------------------------------

The icons are on their own page, :doc:`Icons, everywhere <../examples/icons>`,
and the roles they sit beside are on the :doc:`roles page <../roles>`.

.. toctree::
    :hidden:
    :maxdepth: 1

    accordion
    tabs
    columns
    block
    carousel
    button
    byline
    embed
    code-explain
    code-version
    release
    repository
    thumbnail
    video
    youtube
