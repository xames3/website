.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 October 2026
.. Last updated on: 19 November 2026

:km-page-title: Videos, everywhere
:km-page-description: Every option of the video directive on and off, with a
    real clip, captions and a poster, with icons and roles and inside every
    container.
:km-page-type: article
:km-header-subheader: Every way to play a file
:km-feedback-title: Did I miss a way to combine them?
:km-feedback-description: Tell me what you tried with a video that didn't work.
:km-feedback-button: Tell me
:km-feedback-icon: fa-film

.. _combos-video:

===============================================================================
:fa-icon:regular:`film` Videos, everywhere
===============================================================================

.. rst-class:: km-text-lead

    A video file, in every combination.

A video plays a file from your own site with the controls on. This page writes
it with every option on and off, with a real three-second clip that ships with
the site, with a second format, captions and a poster, with icons and roles and
inside every container, so the markup and the result sit side by side.

.. _combos-video-the-options-one-at-a-time:

-------------------------------------------------------------------------------
The options, one at a time.
-------------------------------------------------------------------------------

No options.

.. video:: _static/combos/sample.webm

.. code-block:: rst

    .. video:: _static/combos/sample.webm

``:caption:``

.. video:: _static/combos/sample.webm
    :caption: A line of text under the video.

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :caption: A line of text under the video.

``:poster:``, shown until the video plays.

.. video:: _static/combos/sample.webm
    :poster: _static/combos/poster.jpg

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :poster: _static/combos/poster.jpg

``:preload: none``, which fetches nothing ahead.

.. video:: _static/combos/sample.webm
    :preload: none
    :poster: _static/combos/poster.jpg

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :preload: none
        :poster: _static/combos/poster.jpg

``:preload: metadata``

.. video:: _static/combos/sample.webm
    :preload: metadata

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :preload: metadata

``:preload: auto``

.. video:: _static/combos/sample.webm
    :preload: auto

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :preload: auto

``:loop:``

.. video:: _static/combos/sample.webm
    :loop:

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :loop:

``:muted:``

.. video:: _static/combos/sample.webm
    :muted:

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :muted:

``:type:``, for a file whose extension doesn't say.

.. video:: _static/combos/sample.webm
    :type: video/webm

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :type: video/webm

``:sources:``, more files of the same video.

.. video:: _static/combos/sample.webm
    :sources: _static/combos/sample-small.webm

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :sources: _static/combos/sample-small.webm

``:track:``, one file for each language.

.. video:: _static/combos/sample.webm
    :track: en=_static/combos/sample.en.vtt,
        hi=_static/combos/sample.hi.vtt
    :caption: With English and Hindi captions.

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :track: en=_static/combos/sample.en.vtt,
            hi=_static/combos/sample.hi.vtt
        :caption: With English and Hindi captions.

``:autoplay:``, which plays muted as soon as it loads.

.. video:: _static/combos/sample.webm
    :autoplay:
    :loop:

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :autoplay:
        :loop:

``:hide-controls:``, which needs ``:autoplay:``.

.. video:: _static/combos/sample.webm
    :autoplay:
    :loop:
    :hide-controls:

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :autoplay:
        :loop:
        :hide-controls:

``:class:``

.. video:: _static/combos/sample.webm
    :class: km-tone-blue

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :class: km-tone-blue

Every option that can go together.

.. video:: _static/combos/sample.webm
    :poster: _static/combos/poster.jpg
    :sources: _static/combos/sample-small.webm
    :track: en=_static/combos/sample.en.vtt
    :preload: metadata
    :loop:
    :muted:
    :caption: Every option that can go together.

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :poster: _static/combos/poster.jpg
        :sources: _static/combos/sample-small.webm
        :track: en=_static/combos/sample.en.vtt
        :preload: metadata
        :loop:
        :muted:
        :caption: Every option that can go together.

.. _combos-video-with-icons:

-------------------------------------------------------------------------------
With icons.
-------------------------------------------------------------------------------

An icon first.

.. video:: _static/combos/sample.webm
    :caption: :fa-icon:regular:`clapperboard` An icon first in the caption.

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :caption: :fa-icon:regular:`clapperboard` An icon first in the caption.

An icon last.

.. video:: _static/combos/sample.webm
    :caption: An icon last in the caption :fa-icon:regular:`clapperboard`

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :caption: An icon last in the caption :fa-icon:regular:`clapperboard`

An icon inside.

.. video:: _static/combos/sample.webm
    :caption: An :fa-icon:regular:`film` icon in the middle.

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :caption: An :fa-icon:regular:`film` icon in the middle.

.. _combos-video-with-roles:

-------------------------------------------------------------------------------
With roles.
-------------------------------------------------------------------------------

.. video:: _static/combos/sample.webm
    :caption: A caption :sharpie:`highlighted`.

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :caption: A caption :sharpie:`highlighted`.

.. video:: _static/combos/sample.webm
    :caption: A caption :underline:`underlined`.

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :caption: A caption :underline:`underlined`.

.. video:: _static/combos/sample.webm
    :caption: A caption :ticker:`2025?short`.

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :caption: A caption :ticker:`2025?short`.

.. video:: _static/combos/sample.webm
    :caption: A caption :roll:`this|that|the other`.

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :caption: A caption :roll:`this|that|the other`.

.. video:: _static/combos/sample.webm
    :caption: A caption :kbd:mac:`Cmd-K`.

.. code-block:: rst

    .. video:: _static/combos/sample.webm
        :caption: A caption :kbd:mac:`Cmd-K`.

.. _combos-video-inside-every-other-container:

-------------------------------------------------------------------------------
Inside every other container.
-------------------------------------------------------------------------------

A video goes anywhere a paragraph does. Here it sits in each container, with
the source under the result.

In an accordion
^^^^^^^^^^^^^^^

.. accordion:: An accordion that holds it
    :open:

    .. video:: _static/combos/sample.webm
        :poster: _static/combos/poster.jpg
        :caption: A short clip.

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. video:: _static/combos/sample.webm
            :poster: _static/combos/poster.jpg
            :caption: A short clip.

In a tab
^^^^^^^^

.. tabs::

    .. tab:: Holds it
        :selected:

        .. video:: _static/combos/sample.webm
            :poster: _static/combos/poster.jpg
            :caption: A short clip.

    .. tab:: Another tab

        Nothing in this one.

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

            .. video:: _static/combos/sample.webm
                :poster: _static/combos/poster.jpg
                :caption: A short clip.

        .. tab:: Another tab

            Nothing in this one.

In a column
^^^^^^^^^^^

.. columns:: 2
    :gap: medium
    :valign: top

    .. column::

        .. video:: _static/combos/sample.webm
            :poster: _static/combos/poster.jpg
            :caption: A short clip.

    .. column::

        Another column.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top

        .. column::

            .. video:: _static/combos/sample.webm
                :poster: _static/combos/poster.jpg
                :caption: A short clip.

        .. column::

            Another column.

In a block
^^^^^^^^^^

.. block:: A block that holds it
    :size: large

    .. video:: _static/combos/sample.webm
        :poster: _static/combos/poster.jpg
        :caption: A short clip.

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. video:: _static/combos/sample.webm
            :poster: _static/combos/poster.jpg
            :caption: A short clip.

In a note
^^^^^^^^^

.. note::

    .. video:: _static/combos/sample.webm
        :poster: _static/combos/poster.jpg
        :caption: A short clip.

.. code-block:: rst

    .. note::

        .. video:: _static/combos/sample.webm
            :poster: _static/combos/poster.jpg
            :caption: A short clip.

In a list item
^^^^^^^^^^^^^^

- A list item that holds it:

  .. video:: _static/combos/sample.webm
      :poster: _static/combos/poster.jpg
      :caption: A short clip.

.. code-block:: rst

    - A list item that holds it:

      .. video:: _static/combos/sample.webm
          :poster: _static/combos/poster.jpg
          :caption: A short clip.
