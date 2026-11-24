.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 19 October 2026
.. Last updated on: 23 November 2026

:km-page-title: Classes
:km-page-description: The classes Kaamiki gives you for text, colour, icons and
    pictures, shown working, with the way to write them in rST.
:km-page-type: article
:km-header-subheader: Small style switches for your pages
:km-feedback-title: Is a class missing?
:km-feedback-description: Tell me which style you'd want for your own pages.
:km-feedback-button: Tell me

.. _kaamiki-classes:

===============================================================================
:fa-icon:duotone:`brush` Classes
===============================================================================

.. rst-class:: km-text-lead

    Small style switches for your own pages.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3
    :shade: purple

Kaamiki names every class the BEM way: ``km-block``, ``km-block__element`` and
``km-block--modifier``. Most are Kaamiki's own and you never write them. The
few below are for you, to change how a paragraph, an icon or a picture looks.

.. _kaamiki-classes-writing:

-------------------------------------------------------------------------------
Writing a class.
-------------------------------------------------------------------------------

Docutils turns every class it's given into an id first, which rewrites
``km-text--lead`` as ``km-text-lead``. A BEM name can't get through
``.. rst-class::``, ``:class:`` or ``:figclass:``, so you write the spelling in
the left column and Kaamiki swaps in the BEM class when it reads the page:

.. list-table::
    :header-rows: 1
    :widths: 30 30 40

    * - You write
      - The page gets
      - What it does
    * - ``km-text-lead``
      - ``km-text--lead``
      - Sets the opening paragraph apart. Also marks the page's lead.
    * - ``km-text-preheader``
      - ``km-text--preheader``
      - A small line above a section's title.
    * - ``km-text-subheader``
      - ``km-text--subheader``
      - A dimmer line under a section's title.
    * - ``km-tone-red``, ``km-tone-green``, ``km-tone-blue``,
        ``km-tone-yellow``
      - ``km-tone--red``, ``km-tone--green``, ``km-tone--blue``,
        ``km-tone--yellow``
      - Colours a paragraph or an icon.
    * - ``km-figure-zoom``
      - ``km-figure--zoom``
      - A picture grows when it's hovered or focused.
    * - ``km-figure-greyscale``
      - ``km-figure--greyscale``
      - A picture is grey until it's hovered or focused.
    * - ``km-figure-fuzzy-blur``
      - ``km-figure--fuzzy-blur``
      - A picture is blurred until it's hovered or focused.
    * - ``km-figure-pixelated-blur``
      - ``km-figure--pixelated-blur``
      - A picture is pixelated until it's hovered or focused.
    * - ``km-no-enlarge``
      - ``km-no-enlarge``
      - A picture that's shown small stays as it is when it's clicked.

The ``:fa-icon:`` role (see :ref:`roles <kaamiki-roles-fa-icon>`) reads its
text itself, so there you write the BEM name: ``:fa-icon:`star
km-tone--blue```. Kaamiki's own directives that take ``:class:`` keep what you
write as it is, so either spelling works there.

.. _kaamiki-classes-text:

-------------------------------------------------------------------------------
Text.
-------------------------------------------------------------------------------

``km-text-lead`` sets the opening paragraph apart, ``km-text-preheader`` is a
small line above a title and ``km-text-subheader`` a dimmer line under one:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        .. rst-class:: km-text-lead

            A lead paragraph.

        .. code-block:: rst

            .. rst-class:: km-text-lead

                A lead paragraph.

    .. column::

        .. rubric:: A line above a title
            :class: km-text-preheader

        .. code-block:: rst

            .. rubric:: A line above a title
                :class: km-text-preheader

    .. column::

        .. rubric:: A subheader line
            :class: km-text-subheader

        .. code-block:: rst

            .. rubric:: A subheader line
                :class: km-text-subheader



.. _kaamiki-classes-colour:

-------------------------------------------------------------------------------
Colour and icons.
-------------------------------------------------------------------------------

``km-tone-*`` colours a paragraph or an icon. An icon needs no class for its
spacing: in the middle of a sentence it keeps the space you typed around it
and at the start or the end of a line Kaamiki gives it ``km-glyph--prefix`` or
``km-glyph--suffix`` for a wider gap:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        .. rst-class:: km-tone-green

            A green paragraph.

        .. code-block:: rst

            .. rst-class:: km-tone-green

                A green paragraph.

    .. column::

        I :fa-icon:solid:`heart km-tone--red` this.

        .. code-block:: rst

            I :fa-icon:solid:`heart km-tone--red` this.

    .. column::

        A :fa-icon:`star km-tone--blue` star.

        .. code-block:: rst

            A :fa-icon:`star km-tone--blue` star.

    .. column::

        Another :fa-icon:`star km-tone--yellow` star.

        .. code-block:: rst

            Another :fa-icon:`star km-tone--yellow` star.



.. _kaamiki-classes-pictures:

-------------------------------------------------------------------------------
Pictures.
-------------------------------------------------------------------------------

A picture, a figure, a video or an embed is never wider than the text, which is
675px, and sits in the middle of it, whatever ``:width:`` or ``:scale:`` asks
for. Only :doc:`code-explain and code-version <directives/explainers>` take
more room, because code needs it.

A picture that's shown smaller than it is opens in a dialog when it's clicked,
tapped or opened with Enter or Space. It flies out from where it sits and flies
back when it's closed with Esc, a click outside it, the close button or a swipe
down, or with Back on a phone. Both of these are 512px, shown at 120px, and
the second one asks to be left alone with ``km-no-enlarge``. A picture that
links somewhere, a video and one on a screen where it would come out no bigger
are left alone too:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        .. figure:: /_static/favicons/web-app-manifest-512x512.png
            :width: 120px
            :alt: A blue verified badge with a white tick

            Click me

        .. code-block:: rst

            .. figure:: /_static/favicons/web-app-manifest-512x512.png
                :width: 120px
                :alt: A blue verified badge with a white tick

                Click me

    .. column::

        .. figure:: /_static/favicons/web-app-manifest-512x512.png
            :width: 120px
            :alt: A blue verified badge with a white tick
            :figclass: km-no-enlarge

            Leave me

        .. code-block:: rst

            .. figure:: /_static/favicons/web-app-manifest-512x512.png
                :width: 120px
                :alt: A blue verified badge with a white tick
                :figclass: km-no-enlarge

                Leave me

A site turns it off with ``kaamiki.conf.media.enlarge`` and a page with
``:km-media-enlarge:``, which :ref:`settings <kaamiki-settings-media>` and
:ref:`page fields <kaamiki-page-fields-media>` explain.
:ref:`How Kaamiki moves <kaamiki-example-motion-a-picture-that-opens>` shows it
open and close.

``km-figure-zoom`` grows a picture when it's hovered or focused,
``km-figure-greyscale`` draws it in grey until it's hovered or focused and
``km-figure-fuzzy-blur`` and ``km-figure-pixelated-blur`` hide it behind a blur
until it's hovered or focused. Give them to a ``figure`` with ``:figclass:``
and mix them as you like, ``km-figure-zoom km-figure-greyscale`` for one. The
dialog shows the picture clean, whatever it's hiding behind on the page:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        .. figure:: /_static/favicons/web-app-manifest-512x512.png
            :width: 120px
            :alt: A blue verified badge with a white tick
            :figclass: km-figure-zoom

            Zoom

        .. code-block:: rst

            .. figure:: /_static/favicons/web-app-manifest-512x512.png
                :width: 120px
                :alt: A blue verified badge with a white tick
                :figclass: km-figure-zoom

                Zoom

    .. column::

        .. figure:: /_static/favicons/web-app-manifest-512x512.png
            :width: 120px
            :alt: A blue verified badge with a white tick
            :figclass: km-figure-fuzzy-blur

            Fuzzy

        .. code-block:: rst

            .. figure:: /_static/favicons/web-app-manifest-512x512.png
                :width: 120px
                :alt: A blue verified badge with a white tick
                :figclass: km-figure-fuzzy-blur

                Fuzzy

    .. column::

        .. figure:: /_static/favicons/web-app-manifest-512x512.png
            :width: 120px
            :alt: A blue verified badge with a white tick
            :figclass: km-figure-pixelated-blur

            Pixelated

        .. code-block:: rst

            .. figure:: /_static/favicons/web-app-manifest-512x512.png
                :width: 120px
                :alt: A blue verified badge with a white tick
                :figclass: km-figure-pixelated-blur

                Pixelated

    .. column::

        .. figure:: /_static/favicons/web-app-manifest-512x512.png
            :width: 120px
            :alt: A blue verified badge with a white tick
            :figclass: km-figure-greyscale

            Greyscale

        .. code-block:: rst

            .. figure:: /_static/favicons/web-app-manifest-512x512.png
                :width: 120px
                :alt: A blue verified badge with a white tick
                :figclass: km-figure-greyscale

                Greyscale
