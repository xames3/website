.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 19 October 2026
.. Last updated on: 23 November 2026

:km-page-title: The button directive
:km-page-description: Turn a link into a button with a colour, an icon and
    control over where it opens.
:km-page-type: article
:km-header-subheader: A link that looks like a button
:km-feedback-title: Is a button missing something?
:km-feedback-description: Tell me which colour, icon or option you'd want.
:km-feedback-button: Tell me

.. _kaamiki-button:

===============================================================================
:fa-icon:regular:`arrow-pointer` button
===============================================================================

.. rst-class:: km-text-lead

    A link that looks like a button.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3
    :shade: indigo

The argument is where it goes and the text under it is the label, one
paragraph of text. A list, a second paragraph or a directive in it stops the
build. A link to another site opens in a new tab on its own:

.. button:: https://example.com

    Get started

.. code-block:: rst

    .. button:: https://example.com

        Get started

A page of the site is named with ``:doc:`` or ``:ref:`` in place of the
address, so the link works under every builder. A button takes one of the
three:

.. button::
    :doc: /docs/kaamiki/installation

    Install it

.. code-block:: rst

    .. button::
        :doc: /docs/kaamiki/installation

        Install it

.. _kaamiki-every-scheme:

-------------------------------------------------------------------------------
Every scheme.
-------------------------------------------------------------------------------

``:scheme:`` picks the look. ``chevron`` is ``light`` with a chevron on the
right that turns into an arrow on hover.

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        .. button:: https://example.com
            :scheme: light

            Light

        .. code-block:: rst

            .. button:: https://example.com
                :scheme: light

                Light

    .. column::

        .. button:: https://example.com
            :scheme: dark

            Dark

        .. code-block:: rst

            .. button:: https://example.com
                :scheme: dark

                Dark

    .. column::

        .. button:: https://example.com
            :scheme: chevron

            Chevron

        .. code-block:: rst

            .. button:: https://example.com
                :scheme: chevron

                Chevron

    .. column::

        .. button:: https://example.com
            :scheme: red

            Red

        .. code-block:: rst

            .. button:: https://example.com
                :scheme: red

                Red

    .. column::

        .. button:: https://example.com
            :scheme: yellow

            Yellow

        .. code-block:: rst

            .. button:: https://example.com
                :scheme: yellow

                Yellow

    .. column::

        .. button:: https://example.com
            :scheme: blue

            Blue

        .. code-block:: rst

            .. button:: https://example.com
                :scheme: blue

                Blue

    .. column::

        .. button:: https://example.com
            :scheme: green

            Green

        .. code-block:: rst

            .. button:: https://example.com
                :scheme: green

                Green



.. _kaamiki-an-icon-where-you-want-it:

-------------------------------------------------------------------------------
An icon, where you want it.
-------------------------------------------------------------------------------

``:fa-icon:`` takes any icon, written the way
:ref:`icons are written <kaamiki-settings-icons>` in settings, and
``:icon-position:`` puts it ``before`` or ``after`` the label.

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        .. button:: https://example.com
            :fa-icon: heart

            Sponsor

        .. code-block:: rst

            .. button:: https://example.com
                :fa-icon: heart

                Sponsor

    .. column::

        .. button:: https://example.com
            :fa-icon: arrow-right
            :icon-position: after

            Read on

        .. code-block:: rst

            .. button:: https://example.com
                :fa-icon: arrow-right
                :icon-position: after

                Read on

    .. column::

        .. button:: /_static/combos/poster.jpg
            :fa-icon: download
            :download:

            Download

        .. code-block:: rst

            .. button:: /_static/combos/poster.jpg
                :fa-icon: download
                :download:

                Download



The last one points at a file on this site, so it stays in the tab and
downloads.

.. _kaamiki-make-every-button-the-same:

-------------------------------------------------------------------------------
Make every button the same.
-------------------------------------------------------------------------------

Three settings give every button on your site its look, and each option above
beats them for one button:

.. code-block:: python

    kaamiki.conf.button.scheme = "green"
    kaamiki.conf.button.icon_position = "after"
    kaamiki.conf.button.colours = {"brand": "#0a7"}

With ``brand`` in ``kaamiki.conf.button.colours``, ``:scheme: brand`` works. A
scheme that's neither one of the seven nor a name you gave stops the build and
lists the ones that work. The settings are covered in :ref:`buttons and roles
<kaamiki-settings-colours>`.

.. _kaamiki-button-options:

-------------------------------------------------------------------------------
Every option.
-------------------------------------------------------------------------------

.. accordion:: The full table

    .. list-table::
        :header-rows: 1
        :widths: 26 74

        * - Option
          - What it does
        * - ``:doc:``
          - A document of the site the button links to, as the ``:doc:`` role
            names it, in place of the address.
        * - ``:ref:``
          - A label the button links to, as the ``:ref:`` role names it,
            capitals and spaces aside, in place of the address.
        * - ``:scheme:``
          - The colour: ``light``, ``dark``, ``chevron``, ``red``, ``yellow``,
            ``blue`` or ``green``, or a name from
            ``kaamiki.conf.button.colours``. Without it the button uses
            ``kaamiki.conf.button.scheme``. ``chevron`` takes neither
            ``:fa-icon:`` nor ``:icon-position:``, so a button with an icon is
            ``light`` under a site-wide ``chevron``, and an icon with
            ``:scheme: chevron`` stops the build.
        * - ``:align:``
          - Where the button sits: ``left``, ``center`` or ``right``. Defaults
            to ``left``.
        * - ``:fa-icon:``
          - A Font Awesome icon, written the way :ref:`icons are written
            <kaamiki-settings-icons>` in settings. One without a style is drawn
            in ``kaamiki.conf.icons.style``, or solid where Font Awesome Free
            has none of that name in that style.
        * - ``:icon-position:``
          - ``before`` or ``after`` the label. Without it the button
            uses ``kaamiki.conf.button.icon_position``. It needs ``:fa-icon:``
            and stops the build without it.
        * - ``:new-tab:``
          - Opens the link in a new tab, even if it stays on your site. A link
            that opens in one already stops the build, since the option would
            do nothing.
        * - ``:same-tab:``
          - Keeps the link in the same tab, even if it leaves your site. Using
            it with ``:new-tab:`` stops the build, and so does a link that
            stays in the tab already.
        * - ``:rel:``
          - The link's ``rel`` attribute, some of ``author``, ``external``,
            ``help``, ``license``, ``nofollow``, ``noopener``, ``noreferrer``,
            ``sponsored`` and ``ugc``. It adds to the ``noopener noreferrer``
            that a link opening in a new tab always has.
        * - ``:tooltip:``
          - The text a reader sees when they hover over it, up to 120
            characters.
        * - ``:download:``
          - Makes the link a download. A value is used as the file's name, a
            name like ``report.pdf`` and not a path. It can't go with a new
            tab.
        * - ``:name:``
          - A name to link to, as :ref:`every directive takes it
            <kaamiki-directives-common>`.
        * - ``:class:``
          - Extra classes for the button.

.. _kaamiki-button-block:

-------------------------------------------------------------------------------
Anywhere a paragraph goes.
-------------------------------------------------------------------------------

A button works inside a :doc:`block <block>`, a :doc:`column <columns>`, a
:doc:`tab <tabs>` or an :doc:`accordion <accordion>`, which is how the buttons
in :doc:`block's examples <block>` are placed. Its label can't hold a link,
since a button is one already. It can't hold ``:roll:`` either, which the
script doesn't run inside a link.
