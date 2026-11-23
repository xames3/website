.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 23 October 2026
.. Last updated on: 23 November 2026

:km-page-title: The columns directive
:km-page-description: Set pieces of content side by side in one to six
    columns that stack on a phone.
:km-page-type: article
:km-header-subheader: Content side by side, stacked on a phone
:km-feedback-title: Is a column missing something?
:km-feedback-description: Tell me which option you'd want.
:km-feedback-button: Tell me

.. _kaamiki-columns:

===============================================================================
:fa-icon:regular:`table-columns` columns
===============================================================================

.. rst-class:: km-text-lead

    Content side by side, stacked on a phone.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3
    :shade: green

``columns`` sets ``column`` directives next to each other. Its argument is how
many columns there are, from 1 to 6, and each ``column`` holds whatever you
like. Once a line is full the next one starts, and on a phone every ``column``
takes the full width, one under the other, except one with ``:span: auto``,
which keeps its own width and is centred. When the columns hold code, they
stay side by side only while the widest code block fits in one, and stack
together when it doesn't, so a line is never cut off:

.. columns:: 2
    :border:

    .. column::

        Left.

    .. column::

        Right.

.. code-block:: rst

    .. columns:: 2
        :border:

        .. column::

            Left.

        .. column::

            Right.

The border is only there so you can see where each column is. The content is
read as reStructuredText, so anything that works on a page works inside a
``column``, other directives included. The exceptions are ``byline``,
``code-explain``, ``code-version`` and ``release``, which go on the page
itself or in a section. A ``columns`` needs more room than a column that
shares its row has. A ``column`` can sit in ``.. only::`` inside its set, to
show it for some builders and not others. This page's own examples are built
from them.

.. _kaamiki-a-wide-column-and-a-narrow-one:

-------------------------------------------------------------------------------
A wide column and a narrow one.
-------------------------------------------------------------------------------

``:span:`` says how many columns a ``column`` takes, and ``:gap:`` sets the
space between them:

.. columns:: 3
    :gap: 1.5rem
    :background:

    .. column::
        :span: 2

        This takes two of the three columns.

    .. column::

        This takes one.

.. code-block:: rst

    .. columns:: 3
        :gap: 1.5rem
        :background:

        .. column::
            :span: 2

            This takes two of the three columns.

        .. column::

            This takes one.

.. _kaamiki-boxes-and-backgrounds:

-------------------------------------------------------------------------------
Boxes and backgrounds.
-------------------------------------------------------------------------------

``:border:`` draws a rounded line round each ``column`` and ``:background:``
fills it with the shade of a code block. ``:padding:`` makes room inside:

.. columns:: 2
    :gap: medium
    :border:

    .. column::

        **First.** A border keeps the content off the edge.

    .. column::

        **Second.** Rows in a line stay as tall as their content.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :border:

        .. column::

            **First.** A border keeps the content off the edge.

        .. column::

            **Second.** Rows in a line stay as tall as their content.

.. columns:: 2
    :gap: medium
    :padding: large
    :background:

    .. column::

        **First.** A background needs no border.

    .. column::

        **Second.** The padding is bigger than the usual 1rem.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :padding: large
        :background:

        .. column::

            **First.** A background needs no border.

        .. column::

            **Second.** The padding is bigger than the usual 1rem.

.. _kaamiki-lining-things-up:

-------------------------------------------------------------------------------
Lining things up.
-------------------------------------------------------------------------------

``:valign:`` lines columns of different heights up at the ``top``, in the
``middle`` (the default) or at the ``bottom``:

.. columns:: 2
    :valign: top

    .. column::

        Short.

    .. column::

        This one runs over a few lines so the line is taller than the first,
        which stays at the top of it. This one runs over a few lines so the
        line is taller than the first.

.. code-block:: rst

    .. columns:: 2
        :valign: top

        .. column::

            Short.

        .. column::

            This one runs over a few lines so the line is taller than the
            first, which stays at the top of it. This one runs over a few
            lines so the line is taller than the first.

A line of text with buttons at the end. The text takes two of the four columns
and the buttons are as wide as their content, ``:span: auto``. On a phone they
stack and centre, with ``:stack-align:`` lining them up and the first length of
``:gap:`` as the space between lines:

.. columns:: 4
    :gap: 1.5rem 0.35rem
    :flush:
    :stack-align: center

    .. column::
        :span: 2

        .. rubric:: Not on social media, but let's connect.

    .. column::
        :span: auto

        .. button:: https://github.com/xames3/website

            GitHub

    .. column::
        :span: auto

        .. button:: mailto:xa@mes3.dev
            :fa-icon: fa-solid fa-envelope
            :scheme: dark

            Send an email

.. code-block:: rst

    .. columns:: 4
        :gap: 1.5rem 0.35rem
        :flush:
        :stack-align: center

        .. column::
            :span: 2

            .. rubric:: Not on social media, but let's connect.

        .. column::
            :span: auto

            .. button:: https://github.com/xames3/website

                GitHub

        .. column::
            :span: auto

            .. button:: mailto:xa@mes3.dev
                :fa-icon: fa-solid fa-envelope
                :scheme: dark

                Send an email

``:flush:`` takes off the space above the first thing in each ``column`` and
below the last, like the space a heading or a repository card has of its own,
so ``:gap:`` and ``:margin:`` decide the spacing.

.. _kaamiki-columns-errors:

-------------------------------------------------------------------------------
Mistakes it catches.
-------------------------------------------------------------------------------

Each of these stops the build with a message naming the line, instead of
columns that look wrong:

- a number of columns that isn't from 1 to 6
- a ``column`` outside a ``columns``
- anything but ``column`` directives inside a ``columns``
- a ``columns`` with no ``column``, and a ``column`` with nothing in it
- a ``columns`` inside a ``column`` that shares its row, and a ``release``, a
  ``byline``, a ``code-explain`` or a ``code-version`` inside any ``column``
- a ``:flush:`` with a ``:padding:``, a ``:border:`` or a ``:background:``
- a ``:span:`` wider than the columns
- a ``:gap:``, ``:padding:`` or ``:margin:`` that isn't a preset or a length
  in ``rem``

.. _kaamiki-columns-options:

-------------------------------------------------------------------------------
Every option.
-------------------------------------------------------------------------------

.. accordion:: The options of columns

    .. list-table::
        :header-rows: 1
        :widths: 26 74

        * - Option
          - What it does
        * - ``:gap:``
          - The space between columns. ``small``, the default, ``medium`` or
            ``large``, or lengths in ``rem`` that replace them, up to 4rem.
            One length is used both ways, like ``1.5rem``. Two are the space
            between lines and then between columns, like ``1rem 2rem``.
        * - ``:valign:``
          - Where columns of different heights line up. ``middle`` (the
            default), ``top`` or ``bottom``.
        * - ``:flush:``
          - Takes off the space above the first thing in each ``column`` and
            below the last. A ``column`` with a ``:padding:``, ``:border:`` or
            ``:background:`` already does, so ``:flush:`` with any of them
            stops the build.
        * - ``:padding:``
          - The space inside each ``column``. ``small``, ``medium`` or
            ``large``, or lengths in ``rem`` written like ``:gap:``. Two
            lengths are the space above and below, then at the sides. A
            ``column`` with a ``:border:`` or a ``:background:`` has ``1rem``
            unless you say otherwise.
        * - ``:border:``
          - Draws a 1px border with rounded corners around each ``column``.
        * - ``:background:``
          - Fills each ``column`` with the same shade as a code block, with
            rounded corners.
        * - ``:margin:``
          - The space above and below the columns. ``medium`` (the default),
            ``small`` or ``large``, or lengths in ``rem`` up to 8rem: one for
            both, or two as above then below, like ``5rem 2rem``.
        * - ``:stack-align:``
          - How the text in the columns lines up when they stack on a phone.
            ``left`` (the default) or ``center``.
        * - ``:name:``
          - A name to link to, as :ref:`every directive takes it
            <kaamiki-directives-common>`.
        * - ``:class:``
          - Extra classes for the columns.
        * - ``:class-column:``
          - Extra classes for every ``column`` in it.

.. accordion:: The options of column

    .. list-table::
        :header-rows: 1
        :widths: 26 74

        * - Option
          - What it does
        * - ``:span:``
          - How many of the columns it takes, or ``auto`` for one as wide as
            its content, which stays that wide and centred on a phone. One
            without it takes one.
        * - ``:name:``
          - A name to link to, as :ref:`every directive takes it
            <kaamiki-directives-common>`.
        * - ``:class:``
          - Extra classes for the ``column``.

    A ``column`` can't span more columns than its ``columns`` has, and a
    ``column`` outside a ``columns`` is an error.
