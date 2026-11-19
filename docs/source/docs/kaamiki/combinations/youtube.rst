.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 October 2026
.. Last updated on: 19 November 2026

:km-page-title: YouTube players, everywhere
:km-page-description: Every option of the youtube directive on and off, with
    every shape, with icons and roles and inside every container.
:km-page-type: article
:km-header-subheader: Every way to embed a YouTube video
:km-feedback-title: Did I miss a way to combine them?
:km-feedback-description: Tell me what you tried with a YouTube player that
    didn't work.
:km-feedback-button: Tell me
:km-feedback-icon: fa-brands fa-youtube

.. _combos-youtube:

===============================================================================
:fa-icon:brands:`youtube` YouTube players, everywhere
===============================================================================

.. rst-class:: km-text-lead

    A YouTube player, in every combination.

A youtube embeds a video's player. This page writes it with every option on and
off, with every shape, with icons and roles and inside every container, so the
markup and the result sit side by side. A player shows the video's picture with
a play button and loads on a click, which is the default, and two are live
players written with ``:auto-load:``.

.. _combos-youtube-the-link-in-every-form:

-------------------------------------------------------------------------------
The link, in every form.
-------------------------------------------------------------------------------

The argument is a link in any of YouTube's forms or a bare id:

A watch link.

.. youtube:: https://www.youtube.com/watch?v=kCc8FmEb1nY

.. code-block:: rst

    .. youtube:: https://www.youtube.com/watch?v=kCc8FmEb1nY

A ``youtu.be`` link.

.. youtube:: https://youtu.be/kCc8FmEb1nY

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY

An embed link.

.. youtube:: https://www.youtube.com/embed/kCc8FmEb1nY

.. code-block:: rst

    .. youtube:: https://www.youtube.com/embed/kCc8FmEb1nY

A bare 11-character id.

.. youtube:: kCc8FmEb1nY

.. code-block:: rst

    .. youtube:: kCc8FmEb1nY

.. _combos-youtube-the-options-one-at-a-time:

-------------------------------------------------------------------------------
The options, one at a time.
-------------------------------------------------------------------------------

A player, with no options. It shows the video's picture with a play button and
loads on a click.

.. youtube:: https://youtu.be/kCc8FmEb1nY

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY

``:auto-load:``, a live player.

.. youtube:: https://youtu.be/kCc8FmEb1nY
    :auto-load:

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :auto-load:

``:caption:``

.. youtube:: https://youtu.be/kCc8FmEb1nY
    :caption: A line of text under the player.

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :caption: A line of text under the player.

``:start:`` and ``:end:``, in seconds.

.. youtube:: https://youtu.be/kCc8FmEb1nY
    :start: 30
    :end: 60

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :start: 30
        :end: 60

``:closed-captions:``, closed captions on.

.. youtube:: https://youtu.be/kCc8FmEb1nY
    :closed-captions:

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :closed-captions:

``:player-language:``

.. youtube:: https://youtu.be/kCc8FmEb1nY
    :player-language: pt-BR

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :player-language: pt-BR

``:no-privacy:``, which embeds from ``youtube.com`` and not
``youtube-nocookie.com``.

.. youtube:: https://youtu.be/kCc8FmEb1nY
    :no-privacy:

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :no-privacy:

``:loop:``

.. youtube:: https://youtu.be/kCc8FmEb1nY
    :loop:

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :loop:

``:muted:``

.. youtube:: https://youtu.be/kCc8FmEb1nY
    :muted:

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :muted:

``:autoplay:`` plays muted as soon as the page loads, so it loads the player at
once and takes neither ``:click-to-load:`` nor ``:auto-load:``. It's
written out and not run.

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :autoplay:

``:hide-controls:``, which needs ``:autoplay:``, so it's written out and not
run as well.

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :autoplay:
        :hide-controls:

``:class:``

.. youtube:: https://youtu.be/kCc8FmEb1nY
    :class: km-tone-blue

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :class: km-tone-blue

A live player with ``:auto-load:``, ``:start:`` and ``:closed-captions:``.

.. youtube:: https://youtu.be/kCc8FmEb1nY
    :auto-load:
    :start: 10
    :closed-captions:
    :caption: A live player with three options.

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :auto-load:
        :start: 10
        :closed-captions:
        :caption: A live player with three options.

.. _combos-youtube-every-shape:

-------------------------------------------------------------------------------
Every shape.
-------------------------------------------------------------------------------

``:ratio:`` is ``16:9`` (the default), ``4:3``, ``21:9``, ``1:1`` or ``9:16``:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        ``:ratio: 16:9``

        .. youtube:: https://youtu.be/kCc8FmEb1nY
            :ratio: 16:9

        .. code-block:: rst

            .. youtube:: https://youtu.be/kCc8FmEb1nY
                :ratio: 16:9

    .. column::

        ``:ratio: 4:3``

        .. youtube:: https://youtu.be/kCc8FmEb1nY
            :ratio: 4:3

        .. code-block:: rst

            .. youtube:: https://youtu.be/kCc8FmEb1nY
                :ratio: 4:3

    .. column::

        ``:ratio: 21:9``

        .. youtube:: https://youtu.be/kCc8FmEb1nY
            :ratio: 21:9

        .. code-block:: rst

            .. youtube:: https://youtu.be/kCc8FmEb1nY
                :ratio: 21:9

    .. column::

        ``:ratio: 1:1``

        .. youtube:: https://youtu.be/kCc8FmEb1nY
            :ratio: 1:1

        .. code-block:: rst

            .. youtube:: https://youtu.be/kCc8FmEb1nY
                :ratio: 1:1

    .. column::

        ``:ratio: 9:16``

        .. youtube:: https://youtu.be/kCc8FmEb1nY
            :ratio: 9:16

        .. code-block:: rst

            .. youtube:: https://youtu.be/kCc8FmEb1nY
                :ratio: 9:16

.. _combos-youtube-with-icons:

-------------------------------------------------------------------------------
With icons.
-------------------------------------------------------------------------------

An icon first in the caption.

.. youtube:: https://youtu.be/kCc8FmEb1nY
    :caption: :fa-icon:brands:`youtube` An icon first.

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :caption: :fa-icon:brands:`youtube` An icon first.

An icon last.

.. youtube:: https://youtu.be/kCc8FmEb1nY
    :caption: An icon last :fa-icon:regular:`arrow-right`

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :caption: An icon last :fa-icon:regular:`arrow-right`

An icon inside.

.. youtube:: https://youtu.be/kCc8FmEb1nY
    :caption: An :fa-icon:regular:`star` icon inside.

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :caption: An :fa-icon:regular:`star` icon inside.

.. _combos-youtube-with-roles:

-------------------------------------------------------------------------------
With roles.
-------------------------------------------------------------------------------

.. youtube:: https://youtu.be/kCc8FmEb1nY
    :caption: A caption :sharpie:`highlighted`.

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :caption: A caption :sharpie:`highlighted`.

.. youtube:: https://youtu.be/kCc8FmEb1nY
    :caption: A caption :underline:`underlined`.

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :caption: A caption :underline:`underlined`.

.. youtube:: https://youtu.be/kCc8FmEb1nY
    :caption: A caption :ticker:`2025?short`.

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :caption: A caption :ticker:`2025?short`.

.. youtube:: https://youtu.be/kCc8FmEb1nY
    :caption: A caption :roll:`this|that|the other`.

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :caption: A caption :roll:`this|that|the other`.

.. youtube:: https://youtu.be/kCc8FmEb1nY
    :caption: A caption :kbd:mac:`Cmd-K`.

.. code-block:: rst

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :caption: A caption :kbd:mac:`Cmd-K`.

.. _combos-youtube-inside-every-other-container:

-------------------------------------------------------------------------------
Inside every other container.
-------------------------------------------------------------------------------

A youtube player goes anywhere a paragraph does. Here it sits in each
container, with the source under the result.

In an accordion
^^^^^^^^^^^^^^^

.. accordion:: An accordion that holds it
    :open:

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :caption: A video.

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. youtube:: https://youtu.be/kCc8FmEb1nY
            :caption: A video.

In a tab
^^^^^^^^

.. tabs::

    .. tab:: Holds it
        :selected:

        .. youtube:: https://youtu.be/kCc8FmEb1nY
            :caption: A video.

    .. tab:: Another tab

        Nothing in this one.

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

            .. youtube:: https://youtu.be/kCc8FmEb1nY
                :caption: A video.

        .. tab:: Another tab

            Nothing in this one.

In a column
^^^^^^^^^^^

.. columns:: 2
    :gap: medium
    :valign: top

    .. column::

        .. youtube:: https://youtu.be/kCc8FmEb1nY
            :caption: A video.

    .. column::

        Another column.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top

        .. column::

            .. youtube:: https://youtu.be/kCc8FmEb1nY
                :caption: A video.

        .. column::

            Another column.

In a block
^^^^^^^^^^

.. block:: A block that holds it
    :size: large

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :caption: A video.

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. youtube:: https://youtu.be/kCc8FmEb1nY
            :caption: A video.

In a note
^^^^^^^^^

.. note::

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :caption: A video.

.. code-block:: rst

    .. note::

        .. youtube:: https://youtu.be/kCc8FmEb1nY
            :caption: A video.

In a list item
^^^^^^^^^^^^^^

- A list item that holds it:

  .. youtube:: https://youtu.be/kCc8FmEb1nY
      :caption: A video.

.. code-block:: rst

    - A list item that holds it:

      .. youtube:: https://youtu.be/kCc8FmEb1nY
          :caption: A video.

.. _combos-youtube-where-it-cant-go:

-------------------------------------------------------------------------------
Where it can't go.
-------------------------------------------------------------------------------

A video can't go in a table cell: the cell is only as wide as its text, so the
video gets no width and doesn't show. The message is written under the source:

In a table
^^^^^^^^^^

.. code-block:: rst

    .. list-table::

        * - .. youtube:: https://youtu.be/kCc8FmEb1nY

          - Another cell.

.. code-block:: text

    youtube: expected outside a code-explain, a code-version, a block that
    links and a table, got it in a table
