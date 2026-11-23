.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 October 2026
.. Last updated on: 23 November 2026

:km-page-title: Buttons, everywhere
:km-page-description: Every option of the button directive on and off, with
    icons and roles, in a table of every colour and icon position and inside
    every container.
:km-page-type: article
:km-header-subheader: Every way to make a link a button
:km-feedback-title: Did I miss a way to combine them?
:km-feedback-description: Tell me what you tried with a button that didn't
    work.
:km-feedback-button: Tell me
:km-feedback-icon: fa-arrow-pointer

.. _combos-button:

===============================================================================
:fa-icon:regular:`arrow-pointer` Buttons, everywhere
===============================================================================

.. rst-class:: km-text-lead

    A link as a button, in every combination.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3
    :shade: indigo

A button turns a link into a pill with a colour and, if you want one, an icon.
This page writes it with every option on and off, with every colour, icon style
and icon position, with roles in its label and inside every container, so the
markup and the result sit side by side.

.. _combos-button-every-colour-every-icon-position:

-------------------------------------------------------------------------------
Every colour, every icon position.
-------------------------------------------------------------------------------

``:scheme:`` picks the colour and ``:icon-position:`` the side of the icon. The
table is every colour with no icon, an icon before and an icon after.
``chevron`` takes neither icon:

.. list-table::
    :header-rows: 1
    :widths: 16 28 28 28

    * - Scheme
      - No icon
      - Icon before
      - Icon after
    * - ``light``
      - .. button:: https://github.com/xames3/website
            :scheme: light

            Label
      - .. button:: https://github.com/xames3/website
            :scheme: light
            :fa-icon: heart

            Label
      - .. button:: https://github.com/xames3/website
            :scheme: light
            :fa-icon: arrow-right
            :icon-position: after

            Label
    * - ``dark``
      - .. button:: https://github.com/xames3/website
            :scheme: dark

            Label
      - .. button:: https://github.com/xames3/website
            :scheme: dark
            :fa-icon: heart

            Label
      - .. button:: https://github.com/xames3/website
            :scheme: dark
            :fa-icon: arrow-right
            :icon-position: after

            Label
    * - ``red``
      - .. button:: https://github.com/xames3/website
            :scheme: red

            Label
      - .. button:: https://github.com/xames3/website
            :scheme: red
            :fa-icon: heart

            Label
      - .. button:: https://github.com/xames3/website
            :scheme: red
            :fa-icon: arrow-right
            :icon-position: after

            Label
    * - ``yellow``
      - .. button:: https://github.com/xames3/website
            :scheme: yellow

            Label
      - .. button:: https://github.com/xames3/website
            :scheme: yellow
            :fa-icon: heart

            Label
      - .. button:: https://github.com/xames3/website
            :scheme: yellow
            :fa-icon: arrow-right
            :icon-position: after

            Label
    * - ``blue``
      - .. button:: https://github.com/xames3/website
            :scheme: blue

            Label
      - .. button:: https://github.com/xames3/website
            :scheme: blue
            :fa-icon: heart

            Label
      - .. button:: https://github.com/xames3/website
            :scheme: blue
            :fa-icon: arrow-right
            :icon-position: after

            Label
    * - ``green``
      - .. button:: https://github.com/xames3/website
            :scheme: green

            Label
      - .. button:: https://github.com/xames3/website
            :scheme: green
            :fa-icon: heart

            Label
      - .. button:: https://github.com/xames3/website
            :scheme: green
            :fa-icon: arrow-right
            :icon-position: after

            Label
    * - ``chevron``
      - .. button:: https://github.com/xames3/website
            :scheme: chevron

            Label
      - Takes no icon
      - Takes no icon

The source of that table.

.. code-block:: rst

    .. list-table::
        :header-rows: 1
        :widths: 16 28 28 28

        * - Scheme
          - No icon
          - Icon before
          - Icon after
        * - ``light``
          - .. button:: https://github.com/xames3/website
                :scheme: light

                Label
          - .. button:: https://github.com/xames3/website
                :scheme: light
                :fa-icon: heart

                Label
          - .. button:: https://github.com/xames3/website
                :scheme: light
                :fa-icon: arrow-right
                :icon-position: after

                Label
        * - ``dark``
          - .. button:: https://github.com/xames3/website
                :scheme: dark

                Label
          - .. button:: https://github.com/xames3/website
                :scheme: dark
                :fa-icon: heart

                Label
          - .. button:: https://github.com/xames3/website
                :scheme: dark
                :fa-icon: arrow-right
                :icon-position: after

                Label
        * - ``red``
          - .. button:: https://github.com/xames3/website
                :scheme: red

                Label
          - .. button:: https://github.com/xames3/website
                :scheme: red
                :fa-icon: heart

                Label
          - .. button:: https://github.com/xames3/website
                :scheme: red
                :fa-icon: arrow-right
                :icon-position: after

                Label
        * - ``yellow``
          - .. button:: https://github.com/xames3/website
                :scheme: yellow

                Label
          - .. button:: https://github.com/xames3/website
                :scheme: yellow
                :fa-icon: heart

                Label
          - .. button:: https://github.com/xames3/website
                :scheme: yellow
                :fa-icon: arrow-right
                :icon-position: after

                Label
        * - ``blue``
          - .. button:: https://github.com/xames3/website
                :scheme: blue

                Label
          - .. button:: https://github.com/xames3/website
                :scheme: blue
                :fa-icon: heart

                Label
          - .. button:: https://github.com/xames3/website
                :scheme: blue
                :fa-icon: arrow-right
                :icon-position: after

                Label
        * - ``green``
          - .. button:: https://github.com/xames3/website
                :scheme: green

                Label
          - .. button:: https://github.com/xames3/website
                :scheme: green
                :fa-icon: heart

                Label
          - .. button:: https://github.com/xames3/website
                :scheme: green
                :fa-icon: arrow-right
                :icon-position: after

                Label
        * - ``chevron``
          - .. button:: https://github.com/xames3/website
                :scheme: chevron

                Label
          - Takes no icon
          - Takes no icon

.. _combos-button-the-options-one-at-a-time:

-------------------------------------------------------------------------------
The options, one at a time.
-------------------------------------------------------------------------------

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        No options.

        .. button:: https://github.com/xames3/website

            A button

        .. code-block:: rst

            .. button:: https://github.com/xames3/website

                A button

    .. column::

        ``:align: center``

        .. button:: https://github.com/xames3/website
            :align: center

            Centred

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :align: center

                Centred

    .. column::

        ``:align: right``

        .. button:: https://github.com/xames3/website
            :align: right

            On the right

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :align: right

                On the right

    .. column::

        ``:tooltip:``

        .. button:: https://github.com/xames3/website
            :tooltip: What a reader sees on hover

            Hover over me

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :tooltip: What a reader sees on hover

                Hover over me

    .. column::

        ``:new-tab:`` on a link that stays

        .. button::
            :doc: /docs/kaamiki/index
            :new-tab:

            A new tab

        .. code-block:: rst

            .. button::
                :doc: /docs/kaamiki/index
                :new-tab:

                A new tab

    .. column::

        ``:same-tab:`` on a link that leaves

        .. button:: https://github.com/xames3/website
            :same-tab:

            The same tab

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :same-tab:

                The same tab

    .. column::

        ``:rel:``

        .. button:: https://github.com/xames3/website
            :rel: nofollow noopener

            A rel

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :rel: nofollow noopener

                A rel

    .. column::

        ``:download:``

        .. button:: /_static/combos/sample.webm
            :fa-icon: download
            :download: sample.webm

            Download the clip

        .. code-block:: rst

            .. button:: /_static/combos/sample.webm
                :fa-icon: download
                :download: sample.webm

                Download the clip

    .. column::

        ``:class:``

        .. button:: https://github.com/xames3/website
            :class: km-tone-blue

            Extra classes

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :class: km-tone-blue

                Extra classes

.. _combos-button-with-icons:

-------------------------------------------------------------------------------
With icons.
-------------------------------------------------------------------------------

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        Before, the default

        .. button:: https://github.com/xames3/website
            :fa-icon: heart

            Before

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :fa-icon: heart

                Before

    .. column::

        After

        .. button:: https://github.com/xames3/website
            :fa-icon: arrow-right
            :icon-position: after

            After

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :fa-icon: arrow-right
                :icon-position: after

                After

    .. column::

        A style

        .. button:: https://github.com/xames3/website
            :fa-icon: fa-solid fa-heart

            Solid

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :fa-icon: fa-solid fa-heart

                Solid

    .. column::

        A brand

        .. button:: https://github.com/xames3/website
            :fa-icon: fa-brands fa-github

            Brand

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :fa-icon: fa-brands fa-github

                Brand

    .. column::

        Duotone

        .. button:: https://github.com/xames3/website
            :fa-icon: fa-duotone fa-star

            Duotone

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :fa-icon: fa-duotone fa-star

                Duotone

    .. column::

        Moving

        .. button:: https://github.com/xames3/website
            :fa-icon: fa-solid fa-heart fa-beat

            Moving

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :fa-icon: fa-solid fa-heart fa-beat

                Moving

    .. column::

        Spinning

        .. button:: https://github.com/xames3/website
            :fa-icon: fa-solid fa-gear fa-spin

            Spinning

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :fa-icon: fa-solid fa-gear fa-spin

                Spinning

    .. column::

        Bigger

        .. button:: https://github.com/xames3/website
            :fa-icon: fa-regular fa-star fa-lg

            Bigger

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :fa-icon: fa-regular fa-star fa-lg

                Bigger

    .. column::

        Turned

        .. button:: https://github.com/xames3/website
            :fa-icon: fa-regular fa-arrow-right fa-rotate-90

            Turned

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :fa-icon: fa-regular fa-arrow-right fa-rotate-90

                Turned

    .. column::

        Icon and a tooltip

        .. button:: https://github.com/xames3/website
            :fa-icon: circle-info
            :tooltip: With an icon

            Both

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :fa-icon: circle-info
                :tooltip: With an icon

                Both

    .. column::

        Icon in the label

        .. button:: https://github.com/xames3/website

            :fa-icon:regular:`star` In the label

        .. code-block:: rst

            .. button:: https://github.com/xames3/website

                :fa-icon:regular:`star` In the label

    .. column::

        Icon last in the label

        .. button:: https://github.com/xames3/website

            In the label :fa-icon:regular:`star`

        .. code-block:: rst

            .. button:: https://github.com/xames3/website

                In the label :fa-icon:regular:`star`

.. _combos-button-with-roles:

-------------------------------------------------------------------------------
With roles.
-------------------------------------------------------------------------------

Every role that doesn't make a link or move works in a label. ``email``
doesn't, since a button is a link and a link can't hold a link, and ``roll``
doesn't either, since the script doesn't run inside a link:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        .. button:: https://github.com/xames3/website

            Label :sharpie:`highlighted`

        .. code-block:: rst

            .. button:: https://github.com/xames3/website

                Label :sharpie:`highlighted`

    .. column::

        .. button:: https://github.com/xames3/website

            Label :underline:`underlined`

        .. code-block:: rst

            .. button:: https://github.com/xames3/website

                Label :underline:`underlined`

    .. column::

        .. button:: https://github.com/xames3/website

            Label :ticker:`2025?short`

        .. code-block:: rst

            .. button:: https://github.com/xames3/website

                Label :ticker:`2025?short`

    .. column::

        .. button:: https://github.com/xames3/website

            Label :kbd:mac:`Cmd-K`

        .. code-block:: rst

            .. button:: https://github.com/xames3/website

                Label :kbd:mac:`Cmd-K`

    .. column::

        .. button:: https://github.com/xames3/website

            Label :fa-icon:solid:`heart km-tone--red`

        .. code-block:: rst

            .. button:: https://github.com/xames3/website

                Label :fa-icon:solid:`heart km-tone--red`

.. _combos-button-buttons-beside-buttons:

-------------------------------------------------------------------------------
Buttons beside buttons.
-------------------------------------------------------------------------------

Written one after another, each is its own row.

.. button:: https://github.com/xames3/website

    One

.. button:: https://github.com/xames3/website
    :scheme: dark

    Two

.. button:: https://github.com/xames3/website
    :scheme: green
    :fa-icon: check

    Three

.. code-block:: rst

    .. button:: https://github.com/xames3/website

        One

    .. button:: https://github.com/xames3/website
        :scheme: dark

        Two

    .. button:: https://github.com/xames3/website
        :scheme: green
        :fa-icon: check

        Three

Aligned three ways.

.. button:: https://github.com/xames3/website
    :align: left

    Left

.. button:: https://github.com/xames3/website
    :align: center

    Centre

.. button:: https://github.com/xames3/website
    :align: right

    Right

.. code-block:: rst

    .. button:: https://github.com/xames3/website
        :align: left

        Left

    .. button:: https://github.com/xames3/website
        :align: center

        Centre

    .. button:: https://github.com/xames3/website
        :align: right

        Right

.. _combos-button-inside-every-other-container:

-------------------------------------------------------------------------------
Inside every other container.
-------------------------------------------------------------------------------

A button goes anywhere a paragraph does. Here it sits in each container, with
the source under the result.

In an accordion
^^^^^^^^^^^^^^^

.. accordion:: An accordion that holds it
    :open:

    .. button:: https://github.com/xames3/website
        :fa-icon: heart

        A button inside

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. button:: https://github.com/xames3/website
            :fa-icon: heart

            A button inside

In a tab
^^^^^^^^

.. tabs::

    .. tab:: Holds it
        :selected:

        .. button:: https://github.com/xames3/website
            :fa-icon: heart

            A button inside

    .. tab:: Another tab

        Nothing in this one.

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

            .. button:: https://github.com/xames3/website
                :fa-icon: heart

                A button inside

        .. tab:: Another tab

            Nothing in this one.

In a column
^^^^^^^^^^^

.. columns:: 2
    :gap: medium
    :valign: top

    .. column::

        .. button:: https://github.com/xames3/website
            :fa-icon: heart

            A button inside

    .. column::

        Another column.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top

        .. column::

            .. button:: https://github.com/xames3/website
                :fa-icon: heart

                A button inside

        .. column::

            Another column.

In a block
^^^^^^^^^^

.. block:: A block that holds it
    :size: large

    .. button:: https://github.com/xames3/website
        :fa-icon: heart

        A button inside

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. button:: https://github.com/xames3/website
            :fa-icon: heart

            A button inside

In a note
^^^^^^^^^

.. note::

    .. button:: https://github.com/xames3/website
        :fa-icon: heart

        A button inside

.. code-block:: rst

    .. note::

        .. button:: https://github.com/xames3/website
            :fa-icon: heart

            A button inside

In a list item
^^^^^^^^^^^^^^

- A list item that holds it:

  .. button:: https://github.com/xames3/website
      :fa-icon: heart

      A button inside

.. code-block:: rst

    - A list item that holds it:

      .. button:: https://github.com/xames3/website
          :fa-icon: heart

          A button inside

.. _combos-button-in-a-blocks-footer-and-a-columns-top:

-------------------------------------------------------------------------------
In a block's footer and a column's top.
-------------------------------------------------------------------------------

.. block:: A block with a button
    :size: large

    .. button:: https://github.com/xames3/website
        :fa-icon: arrow-right
        :icon-position: after

        Inside the body

.. code-block:: rst

    .. block:: A block with a button
        :size: large

        .. button:: https://github.com/xames3/website
            :fa-icon: arrow-right
            :icon-position: after

            Inside the body

.. _combos-button-no-link-and-no-blocks-in-a-label:

-------------------------------------------------------------------------------
No link and no blocks in a label.
-------------------------------------------------------------------------------

A button is a link already, so a link in its label stops the build, and so do
rolling words, which the script doesn't run inside a link, and anything but
one paragraph. The message is written under the source:

An email in the label
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. button:: https://github.com/xames3

        Mail :email:`me <xa@mes3.dev>`

.. code-block:: text

    button: expected a label without a link, got one

Rolling words in the label
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. button:: https://github.com/xames3

        Label :roll:`this|that|the other`

.. code-block:: text

    button: expected a label that stays put, got :roll:, which the script
    doesn't run inside a link

A list in the label
^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. button:: https://github.com/xames3

        - one
        - two

.. code-block:: text

    button: expected one paragraph of text, got a list

Two paragraphs in the label
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. button:: https://github.com/xames3

        One.

        Two.

.. code-block:: text

    button: expected one paragraph of text, got more than one paragraph

A hyperlink in the label
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. button:: https://github.com/xames3

        See `the docs <https://example.com>`_

.. code-block:: text

    button: expected a label without a link, got one
