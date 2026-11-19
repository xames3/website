.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 October 2026
.. Last updated on: 19 November 2026

:km-page-title: Columns, everywhere
:km-page-description: Every option of the columns and column directives on and
    off, with icons and roles, holding every other directive and inside every
    container.
:km-page-type: article
:km-header-subheader: Every way to lay content out
:km-feedback-title: Did I miss a way to combine them?
:km-feedback-description: Tell me what you tried with columns that didn't work.
:km-feedback-button: Tell me
:km-feedback-icon: fa-table-columns

.. _combos-columns:

===============================================================================
:fa-icon:regular:`table-columns` Columns, everywhere
===============================================================================

.. rst-class:: km-text-lead

    Content side by side, in every combination.

Columns put content side by side and stack it on a phone. This page writes them
with every option on and off, with icons and roles, with every other Kaamiki
directive in a column and columns inside every container, so the markup and the
result sit side by side.

.. _combos-columns-how-many-and-how-wide:

-------------------------------------------------------------------------------
How many, and how wide.
-------------------------------------------------------------------------------

Two columns.

.. columns:: 2

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2

        .. column::

            Column 1.

        .. column::

            Column 2.

Three columns.

.. columns:: 3

    .. column::

        Column 1.

    .. column::

        Column 2.

    .. column::

        Column 3.

.. code-block:: rst

    .. columns:: 3

        .. column::

            Column 1.

        .. column::

            Column 2.

        .. column::

            Column 3.

Four columns.

.. columns:: 4

    .. column::

        Column 1.

    .. column::

        Column 2.

    .. column::

        Column 3.

    .. column::

        Column 4.

.. code-block:: rst

    .. columns:: 4

        .. column::

            Column 1.

        .. column::

            Column 2.

        .. column::

            Column 3.

        .. column::

            Column 4.

``:span: 2`` in three columns.

.. columns:: 3

    .. column::
        :span: 2

        A column that spans two.

    .. column::

        One.

.. code-block:: rst

    .. columns:: 3

        .. column::
            :span: 2

            A column that spans two.

        .. column::

            One.

``:span: auto`` is as wide as its content.

.. columns:: 3

    .. column::
        :span: auto

        Auto

    .. column::

        The rest of the room goes to the others.

    .. column::

        Another.

.. code-block:: rst

    .. columns:: 3

        .. column::
            :span: auto

            Auto

        .. column::

            The rest of the room goes to the others.

        .. column::

            Another.

.. _combos-columns-the-options-of-columns-one-at-a-time:

-------------------------------------------------------------------------------
The options of columns, one at a time.
-------------------------------------------------------------------------------

``:gap: small``

.. columns:: 2
    :gap: small

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2
        :gap: small

        .. column::

            Column 1.

        .. column::

            Column 2.

``:gap: medium``

.. columns:: 2
    :gap: medium

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2
        :gap: medium

        .. column::

            Column 1.

        .. column::

            Column 2.

``:gap: large``

.. columns:: 2
    :gap: large

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2
        :gap: large

        .. column::

            Column 1.

        .. column::

            Column 2.

``:gap: 0.5rem``

.. columns:: 2
    :gap: 0.5rem

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2
        :gap: 0.5rem

        .. column::

            Column 1.

        .. column::

            Column 2.

``:gap: 1rem 3rem``

.. columns:: 2
    :gap: 1rem 3rem

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2
        :gap: 1rem 3rem

        .. column::

            Column 1.

        .. column::

            Column 2.

``:valign: top``

.. columns:: 2
    :valign: top

    .. column::

        A short column.

    .. column::

        A taller column,

        with two paragraphs

        and a third.

.. code-block:: rst

    .. columns:: 2
        :valign: top

        .. column::

            A short column.

        .. column::

            A taller column,

            with two paragraphs

            and a third.

``:valign: middle``

.. columns:: 2
    :valign: middle

    .. column::

        A short column.

    .. column::

        A taller column,

        with two paragraphs

        and a third.

.. code-block:: rst

    .. columns:: 2
        :valign: middle

        .. column::

            A short column.

        .. column::

            A taller column,

            with two paragraphs

            and a third.

``:valign: bottom``

.. columns:: 2
    :valign: bottom

    .. column::

        A short column.

    .. column::

        A taller column,

        with two paragraphs

        and a third.

.. code-block:: rst

    .. columns:: 2
        :valign: bottom

        .. column::

            A short column.

        .. column::

            A taller column,

            with two paragraphs

            and a third.

``:flush:``, which takes the space off the first and last thing in a column.

.. columns:: 2
    :flush:

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2
        :flush:

        .. column::

            Column 1.

        .. column::

            Column 2.

Without ``:flush:`` for comparison.

.. columns:: 2

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2

        .. column::

            Column 1.

        .. column::

            Column 2.

``:padding: small`` with ``:border:``

.. columns:: 2
    :padding: small
    :border:

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2
        :padding: small
        :border:

        .. column::

            Column 1.

        .. column::

            Column 2.

``:padding: medium`` with ``:border:``

.. columns:: 2
    :padding: medium
    :border:

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2
        :padding: medium
        :border:

        .. column::

            Column 1.

        .. column::

            Column 2.

``:padding: large`` with ``:border:``

.. columns:: 2
    :padding: large
    :border:

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2
        :padding: large
        :border:

        .. column::

            Column 1.

        .. column::

            Column 2.

``:padding: 0.5rem 2rem`` with ``:border:``

.. columns:: 2
    :padding: 0.5rem 2rem
    :border:

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2
        :padding: 0.5rem 2rem
        :border:

        .. column::

            Column 1.

        .. column::

            Column 2.

``:border:``

.. columns:: 2
    :border:

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2
        :border:

        .. column::

            Column 1.

        .. column::

            Column 2.

``:background:``

.. columns:: 2
    :background:

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2
        :background:

        .. column::

            Column 1.

        .. column::

            Column 2.

``:border:``, ``:background:`` and ``:padding: large``.

.. columns:: 2
    :border:
    :background:
    :padding: large

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2
        :border:
        :background:
        :padding: large

        .. column::

            Column 1.

        .. column::

            Column 2.

``:margin: small``

.. columns:: 2
    :margin: small
    :border:

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2
        :margin: small
        :border:

        .. column::

            Column 1.

        .. column::

            Column 2.

``:margin: medium``

.. columns:: 2
    :margin: medium
    :border:

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2
        :margin: medium
        :border:

        .. column::

            Column 1.

        .. column::

            Column 2.

``:margin: large``

.. columns:: 2
    :margin: large
    :border:

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2
        :margin: large
        :border:

        .. column::

            Column 1.

        .. column::

            Column 2.

``:margin: 4rem 1rem``

.. columns:: 2
    :margin: 4rem 1rem
    :border:

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2
        :margin: 4rem 1rem
        :border:

        .. column::

            Column 1.

        .. column::

            Column 2.

``:stack-align: center``. It shows on a phone, where the columns stack.

.. columns:: 2
    :stack-align: center

    .. column::

        Centred when stacked on a phone.

    .. column::

        So is this.

.. code-block:: rst

    .. columns:: 2
        :stack-align: center

        .. column::

            Centred when stacked on a phone.

        .. column::

            So is this.

``:class:`` and ``:class-column:``.

.. columns:: 2
    :class: km-tone-blue
    :class-column: km-tone-green

    .. column::

        Column 1.

    .. column::

        Column 2.

.. code-block:: rst

    .. columns:: 2
        :class: km-tone-blue
        :class-column: km-tone-green

        .. column::

            Column 1.

        .. column::

            Column 2.

.. _combos-columns-with-icons:

-------------------------------------------------------------------------------
With icons.
-------------------------------------------------------------------------------

Three columns, three positions.

.. columns:: 3

    .. column::

        :fa-icon:regular:`star` An icon at the start, wrapping onto a
        second line.

    .. column::

        An icon at the end, wrapping onto
        a second line :fa-icon:regular:`star`

    .. column::

        An :fa-icon:regular:`star` icon in the middle, wrapping onto a
        second line.

.. code-block:: rst

    .. columns:: 3

        .. column::

            :fa-icon:regular:`star` An icon at the start, wrapping onto a
            second line.

        .. column::

            An icon at the end, wrapping onto
            a second line :fa-icon:regular:`star`

        .. column::

            An :fa-icon:regular:`star` icon in the middle, wrapping onto a
            second line.

Icons as the heads of bordered cards.

.. columns:: 3
    :border:
    :padding: medium

    .. column::

        :fa-icon:solid:`house fa-2x`

        A big icon above.

    .. column::

        :fa-icon:brands:`github fa-2x`

        A brand.

    .. column::

        :fa-icon:solid:`heart fa-2x km-tone--red`

        A colour.

.. code-block:: rst

    .. columns:: 3
        :border:
        :padding: medium

        .. column::

            :fa-icon:solid:`house fa-2x`

            A big icon above.

        .. column::

            :fa-icon:brands:`github fa-2x`

            A brand.

        .. column::

            :fa-icon:solid:`heart fa-2x km-tone--red`

            A colour.

.. _combos-columns-with-roles:

-------------------------------------------------------------------------------
With roles.
-------------------------------------------------------------------------------

.. columns:: 2

    .. column::

        Column :sharpie:`highlighted`

    .. column::

        Another :sharpie:`highlighted`

.. code-block:: rst

    .. columns:: 2

        .. column::

            Column :sharpie:`highlighted`

        .. column::

            Another :sharpie:`highlighted`

.. columns:: 2

    .. column::

        Column :underline:`underlined`

    .. column::

        Another :underline:`underlined`

.. code-block:: rst

    .. columns:: 2

        .. column::

            Column :underline:`underlined`

        .. column::

            Another :underline:`underlined`

.. columns:: 2

    .. column::

        Column :ticker:`2025?short`

    .. column::

        Another :ticker:`2025?short`

.. code-block:: rst

    .. columns:: 2

        .. column::

            Column :ticker:`2025?short`

        .. column::

            Another :ticker:`2025?short`

.. columns:: 2

    .. column::

        Column :roll:`this|that|the other`

    .. column::

        Another :roll:`this|that|the other`

.. code-block:: rst

    .. columns:: 2

        .. column::

            Column :roll:`this|that|the other`

        .. column::

            Another :roll:`this|that|the other`

.. columns:: 2

    .. column::

        Column :kbd:mac:`Cmd-K`

    .. column::

        Another :kbd:mac:`Cmd-K`

.. code-block:: rst

    .. columns:: 2

        .. column::

            Column :kbd:mac:`Cmd-K`

        .. column::

            Another :kbd:mac:`Cmd-K`

.. columns:: 2

    .. column::

        Column :email:`me <xa@mes3.dev>`

    .. column::

        Another :email:`me <xa@mes3.dev>`

.. code-block:: rst

    .. columns:: 2

        .. column::

            Column :email:`me <xa@mes3.dev>`

        .. column::

            Another :email:`me <xa@mes3.dev>`

.. columns:: 2

    .. column::

        Column :fa-icon:solid:`heart km-tone--red`

    .. column::

        Another :fa-icon:solid:`heart km-tone--red`

.. code-block:: rst

    .. columns:: 2

        .. column::

            Column :fa-icon:solid:`heart km-tone--red`

        .. column::

            Another :fa-icon:solid:`heart km-tone--red`

.. _combos-columns-holding-every-other-directive:

-------------------------------------------------------------------------------
Holding every other directive.
-------------------------------------------------------------------------------

A column takes every directive but byline, code-explain and code-version, which
belong to the page itself and stop the build anywhere else. Each is written
inside it below, with the source under the result.

accordion
^^^^^^^^^

.. columns:: 2
    :gap: medium
    :valign: top
    :border:
    :padding: medium

    .. column::

        .. accordion:: An accordion

            Folded away until it opens.

    .. column::

        Another column, bordered too.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top
        :border:
        :padding: medium

        .. column::

            .. accordion:: An accordion

                Folded away until it opens.

        .. column::

            Another column, bordered too.

block
^^^^^

.. columns:: 2
    :gap: medium
    :valign: top
    :border:
    :padding: medium

    .. column::

        .. block:: A block
            :size: large
            :preheader: :fa-icon:regular:`star` Preheader

            The block's body.

    .. column::

        Another column, bordered too.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top
        :border:
        :padding: medium

        .. column::

            .. block:: A block
                :size: large
                :preheader: :fa-icon:regular:`star` Preheader

                The block's body.

        .. column::

            Another column, bordered too.

button
^^^^^^

.. columns:: 2
    :gap: medium
    :valign: top
    :border:
    :padding: medium

    .. column::

        .. button:: https://github.com/xames3/website
            :fa-icon: heart

            A button

    .. column::

        Another column, bordered too.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top
        :border:
        :padding: medium

        .. column::

            .. button:: https://github.com/xames3/website
                :fa-icon: heart

                A button

        .. column::

            Another column, bordered too.

embed
^^^^^

.. columns:: 2
    :gap: medium
    :valign: top
    :border:
    :padding: medium

    .. column::

        .. embed:: iframe

            <p style="padding: 1rem; background: seagreen">
                A block of HTML.
            </p>

    .. column::

        Another column, bordered too.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top
        :border:
        :padding: medium

        .. column::

            .. embed:: iframe

                <p style="padding: 1rem; background: seagreen">
                    A block of HTML.
                </p>

        .. column::

            Another column, bordered too.

repository
^^^^^^^^^^

.. columns:: 2
    :gap: medium
    :valign: top
    :border:
    :padding: medium

    .. column::

        .. repository:: xames3/slowtorch

    .. column::

        Another column, bordered too.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top
        :border:
        :padding: medium

        .. column::

            .. repository:: xames3/slowtorch

        .. column::

            Another column, bordered too.

tabs
^^^^

.. columns:: 2
    :gap: medium
    :valign: top
    :border:
    :padding: medium

    .. column::

        .. tabs::

            .. tab:: First
                :fa-icon: fa-regular fa-code

                The first tab.

            .. tab:: Second

                The second tab.

    .. column::

        Another column, bordered too.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top
        :border:
        :padding: medium

        .. column::

            .. tabs::

                .. tab:: First
                    :fa-icon: fa-regular fa-code

                    The first tab.

                .. tab:: Second

                    The second tab.

        .. column::

            Another column, bordered too.

thumbnail
^^^^^^^^^

.. columns:: 2
    :gap: medium
    :valign: top
    :border:
    :padding: medium

    .. column::

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: A video
            :channel: A channel

    .. column::

        Another column, bordered too.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top
        :border:
        :padding: medium

        .. column::

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :title: A video
                :channel: A channel

        .. column::

            Another column, bordered too.

video
^^^^^

.. columns:: 2
    :gap: medium
    :valign: top
    :border:
    :padding: medium

    .. column::

        .. video:: _static/combos/sample.webm
            :poster: _static/combos/poster.jpg
            :caption: A short clip.

    .. column::

        Another column, bordered too.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top
        :border:
        :padding: medium

        .. column::

            .. video:: _static/combos/sample.webm
                :poster: _static/combos/poster.jpg
                :caption: A short clip.

        .. column::

            Another column, bordered too.

youtube
^^^^^^^

.. columns:: 2
    :gap: medium
    :valign: top
    :border:
    :padding: medium

    .. column::

        .. youtube:: https://youtu.be/kCc8FmEb1nY
            :caption: A video.

    .. column::

        Another column, bordered too.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top
        :border:
        :padding: medium

        .. column::

            .. youtube:: https://youtu.be/kCc8FmEb1nY
                :caption: A video.

        .. column::

            Another column, bordered too.

.. _combos-columns-inside-every-other-container:

-------------------------------------------------------------------------------
Inside every other container.
-------------------------------------------------------------------------------

Columns goes anywhere a paragraph does. Here it sits in each container, with
the source under the result.

In an accordion
^^^^^^^^^^^^^^^

.. accordion:: An accordion that holds it
    :open:

    .. columns:: 2

        .. column::

            Column 1.

        .. column::

            Column 2.

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. columns:: 2

            .. column::

                Column 1.

            .. column::

                Column 2.

In a tab
^^^^^^^^

.. tabs::

    .. tab:: Holds it
        :selected:

        .. columns:: 2

            .. column::

                Column 1.

            .. column::

                Column 2.

    .. tab:: Another tab

        Nothing in this one.

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

            .. columns:: 2

                .. column::

                    Column 1.

                .. column::

                    Column 2.

        .. tab:: Another tab

            Nothing in this one.

In a block
^^^^^^^^^^

.. block:: A block that holds it
    :size: large

    .. columns:: 2

        .. column::

            Column 1.

        .. column::

            Column 2.

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. columns:: 2

            .. column::

                Column 1.

            .. column::

                Column 2.

In a note
^^^^^^^^^

.. note::

    .. columns:: 2

        .. column::

            Column 1.

        .. column::

            Column 2.

.. code-block:: rst

    .. note::

        .. columns:: 2

            .. column::

                Column 1.

            .. column::

                Column 2.

In a list item
^^^^^^^^^^^^^^

- A list item that holds it:

  .. columns:: 2

      .. column::

          Column 1.

      .. column::

          Column 2.

.. code-block:: rst

    - A list item that holds it:

      .. columns:: 2

          .. column::

              Column 1.

          .. column::

              Column 2.

.. _combos-columns-where-it-cant-go:

-------------------------------------------------------------------------------
Where it can't go.
-------------------------------------------------------------------------------

A column that shares its row is about 335px wide at most, so a columns has no
room in it and the build stops. The same goes for a small or a medium block. A
column that spans its whole set, a set of one column and a large block have
room, and so does a list item. A table cell doesn't: it's only as wide as its
text, so the columns get squeezed and the build stops too. The message is
written under the source:

Columns in a column
^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. columns:: 2

        .. column::

            .. columns:: 2

                .. column::

                    One.

                .. column::

                    Two.

        .. column::

            Beside it.

.. code-block:: text

    columns: expected outside a code-explain, a code-version, a table and a
    narrow column or block, got it in a column

Columns in a small block
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. block:: A small block
        :size: small

        .. columns:: 2

            .. column::

                One.

            .. column::

                Two.

.. code-block:: text

    columns: expected outside a code-explain, a code-version, a table and a
    narrow column or block, got it in a small block

Columns in a table
^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. list-table::

        * - .. columns:: 2

                .. column::

                    One.

                .. column::

                    Two.

          - Another cell.

.. code-block:: text

    columns: expected outside a code-explain, a code-version, a table and a
    narrow column or block, got it in a table
