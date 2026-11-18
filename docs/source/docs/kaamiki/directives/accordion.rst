.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 23 October 2026
.. Last updated on: 18 November 2026

:km-page-title: The accordion directive
:km-page-description: Fold a block of content away under a title that opens on
    a click.
:km-page-type: article
:km-header-subheader: Content that folds away under a title
:km-feedback-title: Is an accordion missing something?
:km-feedback-description: Tell me which marker or option you'd want.
:km-feedback-button: Tell me

.. _kaamiki-accordion:

===============================================================================
:fa-icon:regular:`square-plus` accordion
===============================================================================

.. rst-class:: km-text-lead

    Content that folds away under a title.

The argument is the title and everything under it is the content. The title is
read like a paragraph, so it can hold markup, and the content is read as
reStructuredText, so anything that works on a page works inside it:

.. accordion:: How do you pronounce XAMES3 or XA?

    It's literally pronounced as "X-A" or "X-A-Mes-three".

.. code-block:: rst

    .. accordion:: How do you pronounce XAMES3 or XA?

        It's literally pronounced as "X-A" or "X-A-Mes-three".

.. _kaamiki-markers-and-where-they-sit:

-------------------------------------------------------------------------------
Markers and where they sit.
-------------------------------------------------------------------------------

``:marker:`` picks what shows an accordion opens and ``:marker-position:`` puts
it ``before`` or ``after`` the title. A plus turns into a minus as it opens, a
right chevron turns 90 degrees to point down and a down chevron turns over.

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        .. accordion:: A plus, the default

            It sits after the title.

        .. code-block:: rst

            .. accordion:: A plus, the default

                It sits after the title.

    .. column::

        .. accordion:: A down chevron
            :marker: down
            :marker-position: before

            It sits before the title.

        .. code-block:: rst

            .. accordion:: A down chevron
                :marker: down
                :marker-position: before

                It sits before the title.

    .. column::

        .. accordion:: A right chevron
            :marker: right

            It turns as it opens.

        .. code-block:: rst

            .. accordion:: A right chevron
                :marker: right

                It turns as it opens.

    .. column::

        .. accordion:: A dimmer line
            :subheader: Asked in 2025
            :open:

            It starts unfolded.

        .. code-block:: rst

            .. accordion:: A dimmer line
                :subheader: Asked in 2025
                :open:

                It starts unfolded.



.. _kaamiki-one-at-a-time:

-------------------------------------------------------------------------------
One at a time.
-------------------------------------------------------------------------------

Accordions that share a ``:group:`` fold the rest when one opens. Only one of
a group may start open:

.. accordion:: One
    :group: numbers

    The first.

.. accordion:: Two
    :group: numbers

    The second.

.. code-block:: rst

    .. accordion:: One
        :group: numbers

        The first.

    .. accordion:: Two
        :group: numbers

        The second.

.. _kaamiki-accordions-inside-things:

-------------------------------------------------------------------------------
Accordions inside things, and things inside them.
-------------------------------------------------------------------------------

Other directives work inside an accordion, other accordions and
:doc:`tabs <tabs>` among them. The ones that go on the page itself or in a
section, ``byline``, ``code-explain``, ``code-version`` and ``release``, stop
the build here. A title and a subheader can't hold a link, since the whole
line opens the accordion:

.. accordion:: Two ways to install it

    .. tabs::

        .. tab:: pip

            ``pip install kaamiki-sphinx-theme``

        .. tab:: uv

            ``uv add kaamiki-sphinx-theme``

.. code-block:: rst

    .. accordion:: Two ways to install it

        .. tabs::

            .. tab:: pip

                ``pip install kaamiki-sphinx-theme``

            .. tab:: uv

                ``uv add kaamiki-sphinx-theme``

A link to an accordion, or to anything inside it, opens it. Give it a
``:name:`` and :ref:`point at it <kaamiki-directives-common>` from anywhere.

.. _kaamiki-accordion-long:

-------------------------------------------------------------------------------
Long content.
-------------------------------------------------------------------------------

An accordion whose content is taller than the screen opens to about a
screenful and ends in a Show more button, the same fold a long page gets.
``:hide-show-more:`` opens it in full instead.

.. _kaamiki-accordion-settings:

-------------------------------------------------------------------------------
Make every accordion the same.
-------------------------------------------------------------------------------

``kaamiki.conf.accordion.marker`` picks the marker of every accordion on your
site and ``kaamiki.conf.accordion.marker_position`` moves it. ``:marker:`` and
``:marker-position:`` beat them for one:

.. code-block:: python

    kaamiki.conf.accordion.marker = "down"
    kaamiki.conf.accordion.marker_position = "before"

.. _kaamiki-accordion-options:

-------------------------------------------------------------------------------
Every option.
-------------------------------------------------------------------------------

.. accordion:: The full table

    .. list-table::
        :header-rows: 1
        :widths: 26 74

        * - Option
          - What it does
        * - ``:open:``
          - Starts the accordion open. It starts closed without it. Only one
            accordion of a ``:group:`` may start open.
        * - ``:preheader:``
          - A small line above the title. It's parsed like the title and
            looks like ``km-text--preheader``, the style of the small line
            above a page's own headings.
        * - ``:class-preheader:``
          - Extra classes for the preheader. They come on top of
            ``km-text--preheader``. It needs ``:preheader:`` and stops the
            build without it.
        * - ``:subheader:``
          - A dimmer line under the title. It's parsed like the title and
            looks like ``km-text--subheader``, the style of a page's own
            subheaders.
        * - ``:nested-subheader:``
          - Moves the subheader to the top of the content, so it shows once
            the accordion is open instead of under the title. It needs
            ``:subheader:`` and stops the build without it.
        * - ``:class-subheader:``
          - Extra classes for the subheader. They come on top of
            ``km-text--subheader``. It needs ``:subheader:`` and stops the
            build without it.
        * - ``:marker:``
          - What shows an accordion opens: ``plus``, ``down`` or ``right``.
            With a Font Awesome kit it's drawn in your
            ``kaamiki.conf.icons.style`` and without one it's the Free icon.
            Without the option the accordion uses
            ``kaamiki.conf.accordion.marker``.
        * - ``:marker-position:``
          - ``before`` or ``after`` the title. Without it the accordion uses
            ``kaamiki.conf.accordion.marker_position``.
        * - ``:hide-show-more:``
          - Shows a long content in full. Content taller than the screen is
            folded behind a Show more button without it.
        * - ``:group:``
          - A name shared with other accordions on the page. Opening one
            closes the others in its group.
        * - ``:name:``
          - A name to link to, as :ref:`every directive takes it
            <kaamiki-directives-common>`. A link to it, or to anything inside
            it, opens the accordion.
        * - ``:class:``
          - Extra classes for the accordion.
        * - ``:speed:``
          - How quick its motion is, a step of the site's speed, as
            :ref:`every directive that moves takes it
            <kaamiki-directives-motion>`.
        * - ``:no-motion:``
          - Plays nothing in it, as :ref:`every directive that moves takes it
            <kaamiki-directives-motion>`.
        * - ``:class-title:``
          - Extra classes for the title.
        * - ``:class-body:``
          - Extra classes for the content.
