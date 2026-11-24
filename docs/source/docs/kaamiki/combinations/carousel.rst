.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 05 November 2026
.. Last updated on: 23 November 2026

:km-page-title: Carousels, everywhere
:km-page-description: Every option of the carousel directive on and off, with
    every kind of item, icons and roles, and inside every container.
:km-page-type: article
:km-header-subheader: Every way to make a row to swipe through
:km-feedback-title: Did I miss a way to combine them?
:km-feedback-description: Tell me what you tried with a carousel that didn't
    work.
:km-feedback-button: Tell me
:km-feedback-icon: fa-rectangle-history

.. _combos-carousel:

===============================================================================
:fa-icon:regular:`rectangle-history` Carousels, everywhere
===============================================================================

.. rst-class:: km-text-lead

    Cards in a row, in every combination.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3
    :shade: orange

A carousel lays blocks, buttons, pictures, repositories and thumbnails out in a
row a reader swipes through. This page writes it with every option on and off,
with every kind of item, with icons and roles and inside every container, so
the markup and the result sit side by side.

.. _combos-carousel-the-options-one-at-a-time:

-------------------------------------------------------------------------------
The options, one at a time.
-------------------------------------------------------------------------------

No options.

.. carousel::

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel::

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

The argument, which is the title.

.. carousel:: A title.

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: A title.

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

``:preheader:``, which needs a title.

.. carousel:: A title.
    :preheader: Above the title

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: A title.
        :preheader: Above the title

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

``:subheader:``, which needs a title.

.. carousel:: A title.
    :subheader: A dimmer line under the title

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: A title.
        :subheader: A dimmer line under the title

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

A title with both.

.. carousel:: A title.
    :preheader: Above
    :subheader: Under

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: A title.
        :preheader: Above
        :subheader: Under

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

``:gap: medium``

.. carousel::
    :gap: medium

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel::
        :gap: medium

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

``:gap: large``

.. carousel::
    :gap: large

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel::
        :gap: large

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

``:cards: 1``, one card and a quarter of the next.

.. carousel::
    :cards: 1

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel::
        :cards: 1

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

``:cards: 2``, which is what it shows with no option.

.. carousel::
    :cards: 2

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

    .. block:: Item 4
        :size: small

        Text of item 4.

.. code-block:: rst

    .. carousel::
        :cards: 2

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

        .. block:: Item 4
            :size: small

            Text of item 4.

``:cards: 3``, three cards and a quarter of the next.

.. carousel::
    :cards: 3

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

    .. block:: Item 4
        :size: small

        Text of item 4.

    .. block:: Item 5
        :size: small

        Text of item 5.

.. code-block:: rst

    .. carousel::
        :cards: 3

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

        .. block:: Item 4
            :size: small

            Text of item 4.

        .. block:: Item 5
            :size: small

            Text of item 5.

``:cards: 4``, four cards and a quarter of the next.

.. carousel::
    :cards: 4

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

    .. block:: Item 4
        :size: small

        Text of item 4.

    .. block:: Item 5
        :size: small

        Text of item 5.

    .. block:: Item 6
        :size: small

        Text of item 6.

.. code-block:: rst

    .. carousel::
        :cards: 4

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

        .. block:: Item 4
            :size: small

            Text of item 4.

        .. block:: Item 5
            :size: small

            Text of item 5.

        .. block:: Item 6
            :size: small

            Text of item 6.

``:cards: 3`` with ``:gap: large``, which still shows three.

.. carousel::
    :cards: 3
    :gap: large

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

    .. block:: Item 4
        :size: small

        Text of item 4.

    .. block:: Item 5
        :size: small

        Text of item 5.

.. code-block:: rst

    .. carousel::
        :cards: 3
        :gap: large

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

        .. block:: Item 4
            :size: small

            Text of item 4.

        .. block:: Item 5
            :size: small

            Text of item 5.

``:hide-arrows:``, and a reader still swipes.

.. carousel:: A title.
    :hide-arrows:

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: A title.
        :hide-arrows:

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

``:auto-run:``, every four seconds to the right.

.. carousel:: A title.
    :auto-run:

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

    .. block:: Item 4
        :size: small

        Text of item 4.

.. code-block:: rst

    .. carousel:: A title.
        :auto-run:

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

        .. block:: Item 4
            :size: small

            Text of item 4.

``:auto-run:`` with ``:interval:`` and ``:direction:``.

.. carousel:: A title.
    :auto-run:
    :interval: 2
    :direction: left

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

    .. block:: Item 4
        :size: small

        Text of item 4.

.. code-block:: rst

    .. carousel:: A title.
        :auto-run:
        :interval: 2
        :direction: left

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

        .. block:: Item 4
            :size: small

            Text of item 4.

``:class:``

.. carousel:: A title.
    :class: km-tone-blue

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: A title.
        :class: km-tone-blue

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

Every option.

.. carousel:: A title.
    :preheader: Above
    :subheader: Under
    :gap: medium
    :cards: 3
    :auto-run:
    :interval: 5
    :direction: left
    :class: km-tone-green

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

    .. block:: Item 4
        :size: small

        Text of item 4.

.. code-block:: rst

    .. carousel:: A title.
        :preheader: Above
        :subheader: Under
        :gap: medium
        :cards: 3
        :auto-run:
        :interval: 5
        :direction: left
        :class: km-tone-green

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

        .. block:: Item 4
            :size: small

            Text of item 4.

.. _combos-carousel-when-everything-fits:

-------------------------------------------------------------------------------
When everything fits.
-------------------------------------------------------------------------------

Two cards fit in the row, so there's nothing to move and the arrows hide by
themselves:

A title and two cards.

.. carousel:: Two cards.

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

.. code-block:: rst

    .. carousel:: Two cards.

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

One card.

.. carousel::

    .. block:: Item 1
        :size: small

        Text of item 1.

.. code-block:: rst

    .. carousel::

        .. block:: Item 1
            :size: small

            Text of item 1.

``:cards: 3``, and three cards fit.

.. carousel:: Three cards.
    :cards: 3

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: Three cards.
        :cards: 3

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

.. _combos-carousel-what-it-holds:

-------------------------------------------------------------------------------
What it holds.
-------------------------------------------------------------------------------

A block, a button, a figure, an image, a repository and a thumbnail are the
items. Each is written under a carousel below, with other items beside it:

Blocks, one with a subheader and one that links.

.. carousel:: Blocks.

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small
        :subheader: With a subheader

        Text of item 2.

    .. block:: Item 3
        :size: small
        :target: https://github.com/xames3/website

        Text of item 3.

.. code-block:: rst

    .. carousel:: Blocks.

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small
            :subheader: With a subheader

            Text of item 2.

        .. block:: Item 3
            :size: small
            :target: https://github.com/xames3/website

            Text of item 3.

Buttons.

.. carousel:: Buttons.

    .. button:: https://github.com/xames3/website
        :fa-icon: heart

        One

    .. button:: https://github.com/xames3
        :scheme: dark

        Two

    .. button:: https://example.com
        :scheme: red

        Three

.. code-block:: rst

    .. carousel:: Buttons.

        .. button:: https://github.com/xames3/website
            :fa-icon: heart

            One

        .. button:: https://github.com/xames3
            :scheme: dark

            Two

        .. button:: https://example.com
            :scheme: red

            Three

Images and a figure.

.. carousel:: Pictures.

    .. image:: /_static/combos/poster.jpg
        :alt: A dark frame of a sample clip with five coloured circles

    .. image:: /_static/combos/poster.jpg
        :alt: A dark frame of a sample clip with five coloured circles
        :width: 50%

    .. figure:: /_static/combos/poster.jpg
        :alt: A dark frame of a sample clip with five coloured circles

        A caption.

.. code-block:: rst

    .. carousel:: Pictures.

        .. image:: /_static/combos/poster.jpg
            :alt: A dark frame of a sample clip with five coloured circles

        .. image:: /_static/combos/poster.jpg
            :alt: A dark frame of a sample clip with five coloured circles
            :width: 50%

        .. figure:: /_static/combos/poster.jpg
            :alt: A dark frame of a sample clip with five coloured circles

            A caption.

A picture that links is an item too.

.. carousel:: Pictures that link.

    .. image:: /_static/combos/poster.jpg
        :alt: The xames3/website repository on GitHub
        :target: https://github.com/xames3/website

    .. image:: /_static/combos/poster.jpg
        :alt: The xames3 profile on GitHub
        :target: https://github.com/xames3

.. code-block:: rst

    .. carousel:: Pictures that link.

        .. image:: /_static/combos/poster.jpg
            :alt: The xames3/website repository on GitHub
            :target: https://github.com/xames3/website

        .. image:: /_static/combos/poster.jpg
            :alt: The xames3 profile on GitHub
            :target: https://github.com/xames3

Repositories.

.. carousel:: Repositories.

    .. repository:: xames3/slowtorch

        A subset of PyTorch.

    .. repository:: xames3/xsnumpy
        :hide-forks:

        NumPy in Python.

    .. repository:: xames3/website
        :hide-stars:

.. code-block:: rst

    .. carousel:: Repositories.

        .. repository:: xames3/slowtorch

            A subset of PyTorch.

        .. repository:: xames3/xsnumpy
            :hide-forks:

            NumPy in Python.

        .. repository:: xames3/website
            :hide-stars:

Thumbnails.

.. carousel:: Thumbnails.

    .. thumbnail:: https://youtu.be/kCc8FmEb1nY
        :title: One

    .. thumbnail:: https://youtu.be/VMj-3S1tku0
        :title: Two
        :greyscale:

    .. thumbnail:: https://youtu.be/kCc8FmEb1nY
        :title: Three

.. code-block:: rst

    .. carousel:: Thumbnails.

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: One

        .. thumbnail:: https://youtu.be/VMj-3S1tku0
            :title: Two
            :greyscale:

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: Three

Every kind of item in one row.

.. carousel:: A mix.

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. button:: https://example.com

        A button

    .. repository:: xames3/slowtorch

    .. thumbnail:: https://youtu.be/kCc8FmEb1nY
        :title: A video

    .. image:: /_static/combos/poster.jpg
        :alt: A dark frame of a sample clip with five coloured circles

.. code-block:: rst

    .. carousel:: A mix.

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. button:: https://example.com

            A button

        .. repository:: xames3/slowtorch

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: A video

        .. image:: /_static/combos/poster.jpg
            :alt: A dark frame of a sample clip with five coloured circles

.. _combos-carousel-with-icons:

-------------------------------------------------------------------------------
With icons.
-------------------------------------------------------------------------------

Icon in the title.

.. carousel:: :fa-icon:regular:`star` In the title.

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: :fa-icon:regular:`star` In the title.

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

Icon in the preheader.

.. carousel:: A title.
    :preheader: :fa-icon:regular:`star` Icon first

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: A title.
        :preheader: :fa-icon:regular:`star` Icon first

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

Icon last in the preheader.

.. carousel:: A title.
    :preheader: Icon last :fa-icon:regular:`star`

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: A title.
        :preheader: Icon last :fa-icon:regular:`star`

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

Icon in the subheader.

.. carousel:: A title.
    :subheader: With an icon :fa-icon:regular:`star`

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: A title.
        :subheader: With an icon :fa-icon:regular:`star`

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

A coloured icon.

.. carousel:: A title.
    :preheader: :fa-icon:solid:`heart km-tone--red` Red

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: A title.
        :preheader: :fa-icon:solid:`heart km-tone--red` Red

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

A brand icon.

.. carousel:: A title.
    :preheader: :fa-icon:brands:`github` GitHub

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: A title.
        :preheader: :fa-icon:brands:`github` GitHub

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

.. _combos-carousel-with-roles:

-------------------------------------------------------------------------------
With roles.
-------------------------------------------------------------------------------

.. carousel:: Title :sharpie:`highlighted`
    :preheader: Preheader :sharpie:`highlighted`
    :subheader: Sub :sharpie:`highlighted`

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: Title :sharpie:`highlighted`
        :preheader: Preheader :sharpie:`highlighted`
        :subheader: Sub :sharpie:`highlighted`

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

.. carousel:: Title :underline:`underlined`
    :preheader: Preheader :underline:`underlined`
    :subheader: Sub :underline:`underlined`

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: Title :underline:`underlined`
        :preheader: Preheader :underline:`underlined`
        :subheader: Sub :underline:`underlined`

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

.. carousel:: Title :ticker:`2025?short`
    :preheader: Preheader :ticker:`2025?short`
    :subheader: Sub :ticker:`2025?short`

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: Title :ticker:`2025?short`
        :preheader: Preheader :ticker:`2025?short`
        :subheader: Sub :ticker:`2025?short`

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

.. carousel:: Title :roll:`this|that|the other`
    :preheader: Preheader :roll:`this|that|the other`
    :subheader: Sub :roll:`this|that|the other`

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: Title :roll:`this|that|the other`
        :preheader: Preheader :roll:`this|that|the other`
        :subheader: Sub :roll:`this|that|the other`

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

.. carousel:: Title :kbd:mac:`Cmd-K`
    :preheader: Preheader :kbd:mac:`Cmd-K`
    :subheader: Sub :kbd:mac:`Cmd-K`

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: Title :kbd:mac:`Cmd-K`
        :preheader: Preheader :kbd:mac:`Cmd-K`
        :subheader: Sub :kbd:mac:`Cmd-K`

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

.. carousel:: Title :fa-icon:solid:`heart km-tone--red`
    :preheader: Preheader :fa-icon:solid:`heart km-tone--red`
    :subheader: Sub :fa-icon:solid:`heart km-tone--red`

    .. block:: Item 1
        :size: small

        Text of item 1.

    .. block:: Item 2
        :size: small

        Text of item 2.

    .. block:: Item 3
        :size: small

        Text of item 3.

.. code-block:: rst

    .. carousel:: Title :fa-icon:solid:`heart km-tone--red`
        :preheader: Preheader :fa-icon:solid:`heart km-tone--red`
        :subheader: Sub :fa-icon:solid:`heart km-tone--red`

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

.. _combos-carousel-inside-every-other-container:

-------------------------------------------------------------------------------
Inside every other container.
-------------------------------------------------------------------------------

A carousel goes in most places a paragraph does, but not in a column, which is
too narrow for a row of cards. Here it sits in each of the others, with the
source under the result.

In an accordion
^^^^^^^^^^^^^^^

.. accordion:: An accordion that holds it
    :open:

    .. carousel:: A carousel that sits inside.

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

        .. block:: Item 4
            :size: small

            Text of item 4.

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. carousel:: A carousel that sits inside.

            .. block:: Item 1
                :size: small

                Text of item 1.

            .. block:: Item 2
                :size: small

                Text of item 2.

            .. block:: Item 3
                :size: small

                Text of item 3.

            .. block:: Item 4
                :size: small

                Text of item 4.

In a tab
^^^^^^^^

.. tabs::

    .. tab:: Holds it
        :selected:

        .. carousel:: A carousel that sits inside.

            .. block:: Item 1
                :size: small

                Text of item 1.

            .. block:: Item 2
                :size: small

                Text of item 2.

            .. block:: Item 3
                :size: small

                Text of item 3.

            .. block:: Item 4
                :size: small

                Text of item 4.

    .. tab:: Another tab

        Nothing in this one.

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

            .. carousel:: A carousel that sits inside.

                .. block:: Item 1
                    :size: small

                    Text of item 1.

                .. block:: Item 2
                    :size: small

                    Text of item 2.

                .. block:: Item 3
                    :size: small

                    Text of item 3.

                .. block:: Item 4
                    :size: small

                    Text of item 4.

        .. tab:: Another tab

            Nothing in this one.

In a note
^^^^^^^^^

.. note::

    .. carousel:: A carousel that sits inside.

        .. block:: Item 1
            :size: small

            Text of item 1.

        .. block:: Item 2
            :size: small

            Text of item 2.

        .. block:: Item 3
            :size: small

            Text of item 3.

        .. block:: Item 4
            :size: small

            Text of item 4.

.. code-block:: rst

    .. note::

        .. carousel:: A carousel that sits inside.

            .. block:: Item 1
                :size: small

                Text of item 1.

            .. block:: Item 2
                :size: small

                Text of item 2.

            .. block:: Item 3
                :size: small

                Text of item 3.

            .. block:: Item 4
                :size: small

                Text of item 4.

In a list item
^^^^^^^^^^^^^^

- A list item that holds it:

  .. carousel:: A carousel that sits inside.

      .. block:: Item 1
          :size: small

          Text of item 1.

      .. block:: Item 2
          :size: small

          Text of item 2.

      .. block:: Item 3
          :size: small

          Text of item 3.

      .. block:: Item 4
          :size: small

          Text of item 4.

.. code-block:: rst

    - A list item that holds it:

      .. carousel:: A carousel that sits inside.

          .. block:: Item 1
              :size: small

              Text of item 1.

          .. block:: Item 2
              :size: small

              Text of item 2.

          .. block:: Item 3
              :size: small

              Text of item 3.

          .. block:: Item 4
              :size: small

              Text of item 4.

.. _combos-carousel-in-a-block-without-blocks:

-------------------------------------------------------------------------------
In a block, without blocks.
-------------------------------------------------------------------------------

A carousel of blocks can't go in a block, since a block takes no block. One of
buttons, pictures, repositories or thumbnails can:

.. block:: A block that holds it
    :size: large

    .. carousel:: Thumbnails in a block.

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: One

        .. thumbnail:: https://youtu.be/VMj-3S1tku0
            :title: Two

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: Three

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. carousel:: Thumbnails in a block.

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :title: One

            .. thumbnail:: https://youtu.be/VMj-3S1tku0
                :title: Two

            .. thumbnail:: https://youtu.be/kCc8FmEb1nY
                :title: Three

.. _combos-carousel-what-it-cant-hold:

-------------------------------------------------------------------------------
What it can't hold.
-------------------------------------------------------------------------------

A carousel takes the six items above and nothing else, and it takes at least
one. The message is written under the source:

A paragraph
^^^^^^^^^^^

.. code-block:: rst

    .. carousel::

        Just some text.

        .. block:: A block

            Inside.

.. code-block:: text

    carousel: expected blocks, buttons, figures, images,
    repositories and thumbnails, got a paragraph

An accordion
^^^^^^^^^^^^

.. code-block:: rst

    .. carousel::

        .. accordion:: Folded

            Away.

        .. block:: A block

            Inside.

.. code-block:: text

    carousel: expected blocks, buttons, figures, images,
    repositories and thumbnails, got an accordion

A carousel in a carousel
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. carousel::

        .. carousel::

            .. block:: Inner

                Inside.

.. code-block:: text

    carousel: expected blocks, buttons, figures, images,
    repositories and thumbnails, got a carousel

No items
^^^^^^^^

.. code-block:: rst

    .. carousel::

.. code-block:: text

    carousel: expected at least 1 item, got none

.. _combos-carousel-where-it-cant-go:

-------------------------------------------------------------------------------
Where it can't go.
-------------------------------------------------------------------------------

A carousel goes in an accordion, a tab, a note and a list item, but not in a
column or a table cell, which are too narrow for a row of cards. A carousel of
blocks can't go in a block, since a block takes no block, and none can go in a
block that links, since the block is one big link and a reader's swipe would
follow it, nor in the notes of a walkthrough. The message is written under the
source:

In a column
^^^^^^^^^^^

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top

        .. column::

            .. carousel::

                .. block:: Inside

                    Text.

        .. column::

            Another column.

.. code-block:: text

    carousel: expected outside a code-explain, a code-version, a block that
    links, a column and a table, got it in a column

In a table
^^^^^^^^^^

.. code-block:: rst

    .. list-table::

        * - .. carousel::

                .. block:: Inside

                    Text.

          - Another cell.

.. code-block:: text

    carousel: expected outside a code-explain, a code-version, a block that
    links, a column and a table, got it in a table

A carousel of blocks in a block
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. block:: The outer block

        .. carousel::

            .. block:: Inner

                Inside.

.. code-block:: text

    block: expected outside a code-explain, a code-version and a block, got it
    in a block

In a block that links
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. block:: A block that links
        :target: https://example.com

        .. carousel::

            .. block:: Inside

                Text.

.. code-block:: text

    carousel: expected outside a code-explain, a code-version, a block that
    links, a column and a table, got it in a block that links

In a walkthrough's notes
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. code-explain:: c

        .. code::

            int a = 1;

        .. lines:: 1

            .. carousel::

                .. block:: Inside

                    Text.

.. code-block:: text

    carousel: expected outside a code-explain, a code-version, a block that
    links, a column and a table, got it in a code-explain

.. _combos-carousel-options-that-need-others:

-------------------------------------------------------------------------------
Options that need others.
-------------------------------------------------------------------------------

``:preheader:`` and ``:subheader:`` need a title, and ``:interval:`` and
``:direction:`` need ``:auto-run:``. An ``:interval:`` is from 2 to 15, a
``:gap:`` is a preset or a length and ``:cards:`` is a whole number from 1 to
4, with at least that many items in the carousel. The message is written under
the source:

A preheader with no title
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. carousel::
        :preheader: Above

        .. block:: A block

            Inside.

.. code-block:: text

    carousel: :preheader: needs a title

An interval without auto-run
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. carousel::
        :interval: 5

        .. block:: A block

            Inside.

.. code-block:: text

    carousel: :interval: needs :auto-run:

An interval out of range
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. carousel::
        :auto-run:
        :interval: 16

        .. block:: A block

            Inside.

.. code-block:: text

    carousel: :interval: expected 2 to 15, got '16'

A gap that isn't a preset or a length
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. carousel::
        :gap: huge

        .. block:: A block

            Inside.

.. code-block:: text

    carousel: :gap: expected small, medium, large or one or two lengths from 0
    to 4rem like 1.5rem or 1rem 2rem, got 'huge'

Cards out of range
^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. carousel::
        :cards: 5

        .. block:: A block

            Inside.

.. code-block:: text

    carousel: :cards: expected 1 to 4, got '5'

Cards that aren't a whole number
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. carousel::
        :cards: 2.5

        .. block:: A block

            Inside.

.. code-block:: text

    carousel: :cards: expected a whole number, got '2.5'

More cards than items
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. carousel::
        :cards: 4

        .. block:: One

            Inside.

        .. block:: Two

            Inside.

        .. block:: Three

            Inside.

.. code-block:: text

    carousel: :cards: 4 needs at least 4 items, got 3
