.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 19 October 2026
.. Last updated on: 19 November 2026

:km-page-title: Video, YouTube and thumbnails
:km-page-description: Put your own video, a YouTube player or a card that links
    to a YouTube video on a page.
:km-page-type: article
:km-header-subheader: Your video, YouTube's player and a card
:km-feedback-title: Is a video option missing?
:km-feedback-description: Tell me which option you'd want.
:km-feedback-button: Tell me

.. _kaamiki-media:

===============================================================================
:fa-icon:regular:`film` video, youtube and thumbnail
===============================================================================

.. rst-class:: km-text-lead

    Three ways to put a video on a page.

``video`` plays a file you host, ``youtube`` embeds YouTube's player and
``thumbnail`` shows a card that links to a YouTube video without loading
anything from it. All three take the video as the argument and a line of text
under it with ``:caption:``. A caption with nothing in it stops the build, and
so does any text below the directive.

Each is as wide as the text at most, 675px, and sits in the middle of it, at
whatever shape ``:ratio:`` gives it. A video has a full screen of its own, so
none of them opens in a dialog the way :ref:`a picture does
<kaamiki-classes-pictures>`.

.. _kaamiki-media-youtube:

-------------------------------------------------------------------------------
youtube
-------------------------------------------------------------------------------

The argument is a YouTube link. Watch links, ``youtu.be`` links, embed, shorts
and live links all work, and so does a bare 11-character video id. Anything
else stops the build. The page shows the video's picture with a solid play
button and loads the player when it's clicked, through
``kaamiki.conf.youtube.click_to_load``, which ``:auto-load:`` turns off for
one player. The player comes from ``youtube.com``, so it plays on the first
press everywhere. ``kaamiki.conf.youtube.privacy`` or ``:privacy:`` switch to
``youtube-nocookie.com``, which Safari plays only after a second press:

.. youtube:: https://www.youtube.com/watch?v=kCc8FmEb1nY
    :caption: A caption under the player.

.. code-block:: rst

    .. youtube:: https://www.youtube.com/watch?v=kCc8FmEb1nY
        :caption: A caption under the player.

``make linkcheck`` asks YouTube for that picture, so it fails on the picture of
a video that's been deleted or made private.

``:ratio:`` is the player's shape: ``16:9`` (the default), ``4:3``, ``21:9``,
``1:1`` or ``9:16``:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        .. youtube:: https://youtu.be/kCc8FmEb1nY
            :ratio: 4:3

        .. code-block:: rst

            .. youtube:: https://youtu.be/kCc8FmEb1nY
                :ratio: 4:3

    .. column::

        .. youtube:: https://youtu.be/kCc8FmEb1nY
            :ratio: 1:1

        .. code-block:: rst

            .. youtube:: https://youtu.be/kCc8FmEb1nY
                :ratio: 1:1



The rest sits in the table at the bottom of this section.

.. accordion:: The options of youtube

    .. list-table::
        :header-rows: 1
        :widths: 26 74

        * - Option
          - What it does
        * - ``:autoplay:``
          - Plays the video, muted, as soon as it loads. It loads the player
            at once, so it takes neither ``:click-to-load:`` nor
            ``:auto-load:``, and ``:muted:`` as well stops the build.
        * - ``:closed-captions:``
          - Turns closed captions on.
        * - ``:caption:``
          - A line of text under the player, parsed like a paragraph.
        * - ``:start:``
          - Seconds to start playing from, from 1 to 10800. A link's own
            ``t=`` or ``start=``, like ``t=1h2m3s``, is used when it isn't
            written.
        * - ``:end:``
          - Seconds to stop playing at, from 1 to 10800 and after
            ``:start:``.
        * - ``:no-privacy:``
          - Embeds from ``youtube.com``, for a site that turned
            ``kaamiki.conf.youtube.privacy`` on. It stops the build where
            that's off already, which is the default.
        * - ``:privacy:``
          - Embeds from ``youtube-nocookie.com``, which Safari plays only after
            a second press. It stops the build where
            ``kaamiki.conf.youtube.privacy`` is on already.
        * - ``:hide-controls:``
          - Hides the player's controls. Without ``:autoplay:`` there'd be no
            way to play it, so that stops the build.
        * - ``:loop:``
          - Plays the video over and over.
        * - ``:muted:``
          - Starts with the sound off.
        * - ``:player-language:``
          - The player's language and its captions', as a code Babel knows,
            like ``en`` or ``pt-BR``.
        * - ``:ratio:``
          - The player's shape: ``16:9`` (the default), ``4:3``, ``21:9``,
            ``1:1`` or ``9:16``.
        * - ``:auto-load:``
          - Loads the player with the page, where
            ``kaamiki.conf.youtube.click_to_load`` is on, which is the default.
        * - ``:click-to-load:``
          - Shows the video's picture with a play button and loads the player
            on a click, for a site that turned
            ``kaamiki.conf.youtube.click_to_load`` off. It stops the build
            where that's on already.
        * - ``:name:``
          - A name to link to, as :ref:`every directive takes it
            <kaamiki-directives-common>`.
        * - ``:class:``
          - Extra classes for the player.

The player's ``allow`` permissions and referrer policy come from
``kaamiki.conf.youtube.allow`` and ``kaamiki.conf.youtube.referrer_policy``,
which you can change in ``conf.py``. See :ref:`embeds and videos
<kaamiki-settings-embeds>`.

.. _kaamiki-media-thumbnail:

-------------------------------------------------------------------------------
thumbnail
-------------------------------------------------------------------------------

A card for a video that links to it on YouTube. Unlike the player, it embeds
nothing. The whole card is the link, so its title, channel and caption can't
hold one. They can't hold ``:roll:`` either, which the script doesn't run
inside a link. ``:greyscale:`` draws the picture in grey until it's hovered:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY

    .. column::

        .. thumbnail:: https://youtu.be/VMj-3S1tku0
            :greyscale:

        .. code-block:: rst

            .. thumbnail:: https://youtu.be/VMj-3S1tku0
                :greyscale:



The card's picture comes from YouTube's servers. So do its title and channel,
unless you write them with ``:title:`` and ``:channel:``, and the card says
"YouTube video" and "Watch on YouTube" until they arrive or when they can't.
``kaamiki.conf.youtube.privacy`` is for players, so it changes nothing here.
``make linkcheck`` asks YouTube for the picture, so it fails on the picture of
a video that's been deleted or made private.

.. accordion:: The options of thumbnail

    .. list-table::
        :header-rows: 1
        :widths: 26 74

        * - Option
          - What it does
        * - ``:title:``
          - The video's title, shown on the card.
        * - ``:channel:``
          - The channel's name.
        * - ``:caption:``
          - A line of text under the channel, parsed like a paragraph.
        * - ``:greyscale:``
          - Draws the picture in grey until it's hovered. It's in colour
            without it.
        * - ``:name:``
          - A name to link to, as :ref:`every directive takes it
            <kaamiki-directives-common>`.
        * - ``:class:``
          - Extra classes for the card.

.. _kaamiki-media-video:

-------------------------------------------------------------------------------
video
-------------------------------------------------------------------------------

Plays a file from your own site or anywhere else. The argument is the file's
address, and a path that isn't a full address counts from the top of your
site. One under ``_static`` has to be a file in ``html_static_path`` and any
other one a file in ``html_extra_path``, and neither can climb out of its
folder. The video is shown with its controls on, and its type is worked out
from the file's extension. On a phone it plays in the page and not full
screen. A video needs a file of yours, so here's the source only:

.. code-block:: rst

    .. video:: _static/intro.mp4
        :poster: _static/intro.png
        :caption: A short introduction.

A video with a few formats and captions. Each ``:track:`` is labelled with the
language's name, so ``en`` shows as English, and a code Kaamiki doesn't know
stops the build:

.. code-block:: rst

    .. video:: _static/intro.mp4
        :sources: _static/intro.webm
        :track: en=_static/intro.en.vtt, hi=_static/intro.hi.vtt
        :preload: metadata
        :caption: A short introduction.

.. accordion:: The options of video

    .. list-table::
        :header-rows: 1
        :widths: 26 74

        * - Option
          - What it does
        * - ``:autoplay:``
          - Plays the video, muted, as soon as it loads. ``:muted:`` with it
            stops the build, and ``:hide-controls:`` needs it.
        * - ``:caption:``
          - A line of text under the video, parsed like a paragraph.
        * - ``:type:``
          - The video's MIME type, one of ``video/mp4``, ``video/webm``,
            ``video/ogg`` and ``video/quicktime``. It's needed for a file
            whose extension isn't ``.mp4``, ``.m4v``, ``.webm``, ``.ogv``,
            ``.ogg`` or ``.mov``, and it can't disagree with one of those:
            ``.mp4`` and ``.m4v`` are ``video/mp4``, ``.webm`` is
            ``video/webm``, ``.ogv`` and ``.ogg`` are ``video/ogg`` and
            ``.mov`` is written as ``video/mp4`` unless you say
            ``video/quicktime``.
        * - ``:sources:``
          - More files of the same video, up to four besides the first, all
            different from it and each other, comma-separated, for browsers
            that can't play the first one.
        * - ``:poster:``
          - The picture shown until the video plays, a web address or a path
            of a ``.jpg``, ``.jpeg``, ``.png``, ``.webp``, ``.avif``, ``.gif``
            or ``.svg``.
        * - ``:preload:``
          - How much the browser fetches ahead: ``none``, ``metadata`` or
            ``auto``. ``none`` with ``:autoplay:`` stops the build.
        * - ``:loop:``
          - Plays the video over and over.
        * - ``:muted:``
          - Starts with the sound off.
        * - ``:hide-controls:``
          - Hides the player's controls. Without ``:autoplay:`` there'd be no
            way to play it, so that stops the build.
        * - ``:track:``
          - Captions, as ``language=file.vtt`` pairs, comma-separated, up to
            8. The language is a code Babel knows, and a language or a file
            can be in it once.
        * - ``:name:``
          - A name to link to, as :ref:`every directive takes it
            <kaamiki-directives-common>`.
        * - ``:class:``
          - Extra classes for the video.
