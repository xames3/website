.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 October 2026
.. Last updated on: 19 November 2026

:km-page-title: Thumbnails, everywhere
:km-page-description: Every option of the thumbnail directive on and off, with
    icons and roles, in rows and inside every container.
:km-page-type: article
:km-header-subheader: Every way to link to a video
:km-feedback-title: Did I miss a way to combine them?
:km-feedback-description: Tell me what you tried with a thumbnail that didn't
    work.
:km-feedback-button: Tell me
:km-feedback-icon: fa-image

.. _combos-thumbnail:

===============================================================================
:fa-icon:regular:`image` Thumbnails, everywhere
===============================================================================

.. rst-class:: km-text-lead

    A video card, in every combination.

A thumbnail is a card for a video that links to it on YouTube and embeds
nothing. This page writes it with every option on and off, with icons and
roles, in rows and inside every container, so the markup and the result sit
side by side.

.. _combos-thumbnail-the-options-one-at-a-time:

-------------------------------------------------------------------------------
The options, one at a time.
-------------------------------------------------------------------------------

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        No options.

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY

    .. column::

        ``:title:``

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: The video's title

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :title: The video's title

    .. column::

        ``:channel:``

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :channel: The channel

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :channel: The channel

    .. column::

        ``:caption:``

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :caption: A line under the channel

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :caption: A line under the channel

    .. column::

        ``:greyscale:``

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :greyscale:

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :greyscale:

    .. column::

        ``:class:``

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :class: km-tone-blue

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :class: km-tone-blue

    .. column::

        ``:title:`` and ``:channel:``

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: A title
            :channel: A channel

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :title: A title
                :channel: A channel

    .. column::

        Every option

        .. thumbnail:: https://youtu.be/VMj-3S1tku0
            :title: A title
            :channel: A channel
            :caption: A caption
            :greyscale:
            :class: km-tone-green

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/VMj-3S1tku0
                :title: A title
                :channel: A channel
                :caption: A caption
                :greyscale:
                :class: km-tone-green

.. _combos-thumbnail-in-a-row:

-------------------------------------------------------------------------------
In a row.
-------------------------------------------------------------------------------

Three cards in three columns.

.. columns:: 3
    :gap: medium
    :valign: top

    .. column::

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: One

    .. column::

        .. thumbnail:: https://youtu.be/VMj-3S1tku0
            :title: Two
            :greyscale:

    .. column::

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: Three

.. code-block:: rst

    .. columns:: 3
        :gap: medium
        :valign: top

        .. column::

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :title: One

        .. column::

            .. thumbnail:: https://youtu.be/VMj-3S1tku0
                :title: Two
                :greyscale:

        .. column::

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :title: Three

.. _combos-thumbnail-with-icons:

-------------------------------------------------------------------------------
With icons.
-------------------------------------------------------------------------------

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        Icon first in the title

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: :fa-icon:regular:`star` A title

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :title: :fa-icon:regular:`star` A title

    .. column::

        Icon last in the title

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: A title :fa-icon:regular:`star`

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :title: A title :fa-icon:regular:`star`

    .. column::

        Icon in the channel

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :channel: :fa-icon:brands:`youtube` A channel

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :channel: :fa-icon:brands:`youtube` A channel

    .. column::

        Icon in the caption

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :caption: Watch :fa-icon:regular:`arrow-right`

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :caption: Watch :fa-icon:regular:`arrow-right`

.. _combos-thumbnail-with-roles:

-------------------------------------------------------------------------------
With roles.
-------------------------------------------------------------------------------

Every role that doesn't make a link or move works in a card. ``email`` doesn't,
since a thumbnail is a link and a link can't hold a link, and ``roll``
doesn't either, since the script doesn't run inside a link:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: A title :sharpie:`highlighted`
            :caption: A caption :sharpie:`highlighted`

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :title: A title :sharpie:`highlighted`
                :caption: A caption :sharpie:`highlighted`

    .. column::

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: A title :underline:`underlined`
            :caption: A caption :underline:`underlined`

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :title: A title :underline:`underlined`
                :caption: A caption :underline:`underlined`

    .. column::

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: A title :ticker:`2025?short`
            :caption: A caption :ticker:`2025?short`

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :title: A title :ticker:`2025?short`
                :caption: A caption :ticker:`2025?short`

    .. column::

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: A title :kbd:mac:`Cmd-K`
            :caption: A caption :kbd:mac:`Cmd-K`

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :title: A title :kbd:mac:`Cmd-K`
                :caption: A caption :kbd:mac:`Cmd-K`

    .. column::

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: A title :fa-icon:solid:`heart km-tone--red`
            :caption: A caption :fa-icon:solid:`heart km-tone--red`

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :title: A title :fa-icon:solid:`heart km-tone--red`
                :caption: A caption :fa-icon:solid:`heart km-tone--red`

.. _combos-thumbnail-inside-every-other-container:

-------------------------------------------------------------------------------
Inside every other container.
-------------------------------------------------------------------------------

A thumbnail goes anywhere a paragraph does. Here it sits in each container,
with the source under the result.

In an accordion
^^^^^^^^^^^^^^^

.. accordion:: An accordion that holds it
    :open:

    .. thumbnail:: https://youtu.be/kCc8FmEb1nY
        :title: A video
        :channel: A channel

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: A video
            :channel: A channel

In a tab
^^^^^^^^

.. tabs::

    .. tab:: Holds it
        :selected:

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: A video
            :channel: A channel

    .. tab:: Another tab

        Nothing in this one.

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :title: A video
                :channel: A channel

        .. tab:: Another tab

            Nothing in this one.

In a column
^^^^^^^^^^^

.. columns:: 2
    :gap: medium
    :valign: top

    .. column::

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: A video
            :channel: A channel

    .. column::

        Another column.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top

        .. column::

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :title: A video
                :channel: A channel

        .. column::

            Another column.

In a block
^^^^^^^^^^

.. block:: A block that holds it
    :size: large

    .. thumbnail:: https://youtu.be/kCc8FmEb1nY
        :title: A video
        :channel: A channel

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: A video
            :channel: A channel

In a note
^^^^^^^^^

.. note::

    .. thumbnail:: https://youtu.be/kCc8FmEb1nY
        :title: A video
        :channel: A channel

.. code-block:: rst

    .. note::

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: A video
            :channel: A channel

In a list item
^^^^^^^^^^^^^^

- A list item that holds it:

  .. thumbnail:: https://youtu.be/kCc8FmEb1nY
      :title: A video
      :channel: A channel

.. code-block:: rst

    - A list item that holds it:

      .. thumbnail:: https://youtu.be/kCc8FmEb1nY
          :title: A video
          :channel: A channel

.. _combos-thumbnail-no-link-in-a-card:

-------------------------------------------------------------------------------
No link in a card.
-------------------------------------------------------------------------------

The whole card is a link, so a link in its title, channel or caption stops the
build, and so do rolling words, which the script doesn't run inside a link.
The message is written under the source:

An email in the title
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. thumbnail:: https://youtu.be/kCc8FmEb1nY
        :title: Mail :email:`me <xa@mes3.dev>`

.. code-block:: text

    thumbnail: expected a title without a link, got one

An email in the caption
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. thumbnail:: https://youtu.be/kCc8FmEb1nY
        :caption: Mail :email:`me <xa@mes3.dev>`

.. code-block:: text

    thumbnail: expected a caption without a link, got one

Rolling words in the title
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. thumbnail:: https://youtu.be/kCc8FmEb1nY
        :title: A title :roll:`this|that|the other`

.. code-block:: text

    thumbnail: expected a title that stays put, got :roll:, which the script
    doesn't run inside a link
