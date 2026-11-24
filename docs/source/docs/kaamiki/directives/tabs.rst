.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 23 October 2026
.. Last updated on: 23 November 2026

:km-page-title: The tabs directive
:km-page-description: Show one block of content at a time under a strip of
    titles, with icons, groups that switch together and links into a tab.
:km-page-type: article
:km-header-subheader: One block at a time under a row of titles
:km-feedback-title: Is a tab missing something?
:km-feedback-description: Tell me which option you'd want.
:km-feedback-button: Tell me

.. _kaamiki-tabs:

===============================================================================
:fa-icon:regular:`folders` tabs
===============================================================================

.. rst-class:: km-text-lead

    One block of content at a time, under a row of titles.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3

``tabs`` holds ``tab`` directives and shows one of them. Each tab's argument is
its title and everything under it is its content. The first tab shows to start
with, a set needs at least two and the build stops with fewer. A set holds
``tab`` directives and nothing else:

.. tabs::

    .. tab:: pip

        ``pip install kaamiki-sphinx-theme``

    .. tab:: uv

        ``uv add kaamiki-sphinx-theme``

.. code-block:: rst

    .. tabs::

        .. tab:: pip

            ``pip install kaamiki-sphinx-theme``

        .. tab:: uv

            ``uv add kaamiki-sphinx-theme``

A title is read like a paragraph, so it can hold markup, but not a link, since
it's what you click to show the tab, and not ``:roll:``, which would move
the row of titles. A screen reader announces them as tabs, and the arrow keys,
Home and End move between them. Without JavaScript the tabs still switch,
because underneath each one is a radio button.
The content is read as reStructuredText, so anything that works on a page
works inside a tab, other directives and other tabs included, but for
``byline``, ``code-explain``, ``code-version`` and ``release``, which go on
the page itself or in a section. A ``tab`` can sit in ``.. only::`` inside its
set, to show it for some builders and not others.

.. _kaamiki-icons-and-a-tab-that-shows-first:

-------------------------------------------------------------------------------
Icons, and a tab that shows first.
-------------------------------------------------------------------------------

A ``tab`` takes ``:fa-icon:`` and ``:icon-position:``, and ``:selected:`` makes
it the one that shows to start with:

.. tabs::

    .. tab:: Programming
        :fa-icon: fa-regular fa-code

        Videos about programming.

    .. tab:: Talks
        :fa-icon: fa-regular fa-comments
        :icon-position: after
        :selected:

        Interviews and talks.

.. code-block:: rst

    .. tabs::

        .. tab:: Programming
            :fa-icon: fa-regular fa-code

            Videos about programming.

        .. tab:: Talks
            :fa-icon: fa-regular fa-comments
            :icon-position: after
            :selected:

            Interviews and talks.

.. _kaamiki-tab-sets-that-switch-together:

-------------------------------------------------------------------------------
Sets that switch together.
-------------------------------------------------------------------------------

Give sets the same ``:group:`` and picking a tab picks the tab with the same
title in every set on the page. The browser remembers the choice on your other
pages too:

.. tabs::
    :group: install

    .. tab:: pip

        ``pip install kaamiki-sphinx-theme``

    .. tab:: uv

        ``uv add kaamiki-sphinx-theme``

A paragraph between them.

.. tabs::
    :group: install

    .. tab:: pip

        ``pip show kaamiki-sphinx-theme``

    .. tab:: uv

        ``uv pip show kaamiki-sphinx-theme``

.. code-block:: rst

    .. tabs::
        :group: install

        .. tab:: pip

            ``pip install kaamiki-sphinx-theme``

        .. tab:: uv

            ``uv add kaamiki-sphinx-theme``

    A paragraph between them.

    .. tabs::
        :group: install

        .. tab:: pip

            ``pip show kaamiki-sphinx-theme``

        .. tab:: uv

            ``uv pip show kaamiki-sphinx-theme``

Tabs that mean the same thing under different titles, like "pip" and "pip
(macOS)", match by a ``:key:``:

.. code-block:: rst

    .. tab:: pip (macOS)
        :key: pip

        ``pip install kaamiki-sphinx-theme``

.. _kaamiki-link-straight-to-a-tab:

-------------------------------------------------------------------------------
Link straight to a tab.
-------------------------------------------------------------------------------

A ``:name:`` on a tab makes it something a link can point at. The link, or any
link to something inside the tab, shows it:

.. tabs::

    .. tab:: Setup

        Some setup.

    .. tab:: Usage
        :name: usage-tab

        Some usage.

:ref:`Jump to the usage tab <usage-tab>`.

.. code-block:: rst

    .. tabs::

        .. tab:: Setup

            Some setup.

        .. tab:: Usage
            :name: usage-tab

            Some usage.

    :ref:`Jump to the usage tab <usage-tab>`.

.. _kaamiki-where-the-titles-sit:

-------------------------------------------------------------------------------
Where the titles sit.
-------------------------------------------------------------------------------

``:align:`` puts the row of titles on the ``left``, in the ``center`` (the
default) or on the ``right``:

.. tabs::
    :align: left

    .. tab:: Left

        The row sits on the left.

    .. tab:: Slides

        The pill slides across.

.. code-block:: rst

    .. tabs::
        :align: left

        .. tab:: Left

            The row sits on the left.

        .. tab:: Slides

            The pill slides across.

.. _kaamiki-tabs-settings:

-------------------------------------------------------------------------------
Make every tab the same.
-------------------------------------------------------------------------------

``kaamiki.conf.tab.icon_position`` moves the icon of every tab on your site and
``:icon-position:`` beats it for one tab:

.. code-block:: python

    kaamiki.conf.tab.icon_position = "after"

.. _kaamiki-tabs-options:

-------------------------------------------------------------------------------
Every option.
-------------------------------------------------------------------------------

.. accordion:: The options of tabs

    .. list-table::
        :header-rows: 1
        :widths: 26 74

        * - Option
          - What it does
        * - ``:group:``
          - A name shared with other tab sets on the page. Picking a tab picks
            the tab with the same key in each of them, which is its title
            unless you give it a ``:key:``.
        * - ``:align:``
          - Where the row of titles sits: ``left``, ``center`` or ``right``.
            Defaults to ``center``.
        * - ``:name:``
          - A name to link to, as :ref:`every directive takes it
            <kaamiki-directives-common>`.
        * - ``:class:``
          - Extra classes for the tab set.
        * - ``:speed:``
          - How quick its motion is, a step of the site's speed, as
            :ref:`every directive that moves takes it
            <kaamiki-directives-motion>`.
        * - ``:no-motion:``
          - Plays nothing in it, as :ref:`every directive that moves takes it
            <kaamiki-directives-motion>`.
        * - ``:class-bar:``
          - Extra classes for the row of titles.

.. accordion:: The options of tab

    .. list-table::
        :header-rows: 1
        :widths: 26 74

        * - Option
          - What it does
        * - ``:fa-icon:``
          - A Font Awesome icon for the title, written the way :ref:`icons are
            written <kaamiki-settings-icons>` in settings. One without a style
            is drawn in ``kaamiki.conf.icons.style``, or solid where Font
            Awesome Free has none of that name in that style.
        * - ``:icon-position:``
          - ``before`` or ``after`` the title, and it needs ``:fa-icon:``.
            Without it the tab uses ``kaamiki.conf.tab.icon_position``.
        * - ``:selected:``
          - Shows this tab to start with. Only one tab can have it.
        * - ``:key:``
          - What ``:group:`` matches the tab by. Without it the key is the
            title, and two tabs of one set can't have the same one, so give
            one of them a ``:key:``.
        * - ``:name:``
          - A name to link to, as :ref:`every directive takes it
            <kaamiki-directives-common>`. A link to it, or to anything inside
            it, shows the tab.
        * - ``:class:``
          - Extra classes for the title and the content.
        * - ``:class-title:``
          - Extra classes for the title.
        * - ``:class-body:``
          - Extra classes for the content.
