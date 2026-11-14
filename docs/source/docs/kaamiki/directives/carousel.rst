.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 05 November 2026
.. Last updated on: 12 November 2026

:km-page-title: The carousel directive
:km-page-description: Lay blocks, buttons, pictures, repositories and
    thumbnails out in a row to swipe through, with a title, arrows and a
    mind of its own if you want one.
:km-page-type: article
:km-header-subheader: A row of cards to swipe through
:km-feedback-title: Is a carousel missing something?
:km-feedback-description: Tell me which option you'd want.
:km-feedback-button: Tell me

.. _kaamiki-carousel:

===============================================================================
:fa-icon:regular:`rectangle-history` carousel
===============================================================================

.. rst-class:: km-text-lead

    A row of cards to swipe through.

Each directive under a ``carousel`` is one item in a row. Two items show in
full and a quarter of the third peeks in from the side, unless ``:cards:``
:ref:`says otherwise <kaamiki-how-many-show>`. A reader swipes, scrolls or uses
the arrows to reach the rest, and the arrows grey out at each end. The argument
is the title and it's optional:

.. carousel:: Where to go next.

    .. block:: Directives
        :size: small
        :doc: index

        Every directive, shown working.

    .. block:: Roles
        :size: small
        :doc: ../roles

        Words that move, glow and count.

    .. block:: Settings
        :size: small
        :doc: ../settings

        What you can change in ``conf.py``.

.. code-block:: rst

    .. carousel:: Where to go next.

        .. block:: Directives
            :size: small
            :doc: index

            Every directive, shown working.

        .. block:: Roles
            :size: small
            :doc: ../roles

            Words that move, glow and count.

        .. block:: Settings
            :size: small
            :doc: ../settings

            What you can change in ``conf.py``.

Without a title the group is named "Carousel" for a screen reader. With one,
the title names it. Without JavaScript the row still scrolls, only the arrows
are missing.

.. _kaamiki-a-title-and-what-sits-around-it:

-------------------------------------------------------------------------------
A preheader, a title and a subheader.
-------------------------------------------------------------------------------

``:preheader:`` is a small line above the title, set the way the text above a
section's heading is, and ``:subheader:`` is a dimmer line under it, set the
way a section's is. Both need a title and both are read as reStructuredText, so
roles work in them, in the title too:

.. carousel:: Keep it stupid simple.
    :preheader: :fa-icon:regular:`comments` Preheader
    :subheader: A dimmer line under the title, like the one under a heading.

    .. block:: One
        :size: small

        The first card.

    .. block:: Two
        :size: small

        The second card.

    .. block:: Three
        :size: small

        The third card.

.. code-block:: rst

    .. carousel:: Keep it stupid simple.
        :preheader: :fa-icon:regular:`comments` Preheader
        :subheader: A dimmer line under the title, like the one under a
            heading.

        .. block:: One
            :size: small

            The first card.

The arrows sit on the title's line when the title and they fit on one and below
the items when they don't. Under 768px wide they're always below.

.. _kaamiki-what-goes-inside-a-carousel:

-------------------------------------------------------------------------------
What goes inside.
-------------------------------------------------------------------------------

A ``block``, a ``button``, a ``figure``, an ``image``, a ``repository`` and a
``thumbnail`` go inside, an item each. A picture that links is one too.
Anything else stops the build, a paragraph and a heading among it:

.. carousel::

    .. block:: A block
        :size: small
        :subheader: With a subheader

        The text sits at the bottom of the card.

    .. button:: https://github.com/xames3/website

        A button

    .. repository:: xames3/slowtorch

        A GitHub project.

.. code-block:: rst

    .. carousel::

        .. block:: A block
            :size: small
            :subheader: With a subheader

            The text sits at the bottom of the card.

        .. button:: https://github.com/xames3/website

            A button

        .. repository:: xames3/slowtorch

            A GitHub project.

.. _kaamiki-how-many-show:

-------------------------------------------------------------------------------
How many show.
-------------------------------------------------------------------------------

``:cards:`` is how many items show in full, from 1 to 4. The next one still
peeks in by a quarter of its width, so a reader can tell there's more. Here's
``:cards: 1``:

.. carousel::
    :cards: 1

    .. block:: One
        :size: small

        One card and a quarter of the next.

    .. block:: Two
        :size: small

        The next one.

    .. block:: Three
        :size: small

        And the one after.

.. code-block:: rst

    .. carousel::
        :cards: 1

        .. block:: One
            :size: small

            One card and a quarter of the next.

With no option two show, which is the same as ``:cards: 2``:

.. carousel::

    .. block:: One
        :size: small

        Two cards and a quarter of the next.

    .. block:: Two
        :size: small

        The second.

    .. block:: Three
        :size: small

        The one peeking in.

    .. block:: Four
        :size: small

        Out of sight.

.. code-block:: rst

    .. carousel::

        .. block:: One
            :size: small

            Two cards and a quarter of the next.

Three and four, with the same quarter of the next one showing:

.. carousel::
    :cards: 3

    .. block:: One
        :size: small

        Three cards.

    .. block:: Two
        :size: small

        And a quarter.

    .. block:: Three
        :size: small

        Of the next.

    .. block:: Four
        :size: small

        Peeking in.

    .. block:: Five
        :size: small

        Out of sight.

.. code-block:: rst

    .. carousel::
        :cards: 3

        .. block:: One
            :size: small

            Three cards.

.. carousel::
    :cards: 4

    .. block:: One
        :size: small

        Four.

    .. block:: Two
        :size: small

        Cards.

    .. block:: Three
        :size: small

        And a bit.

    .. block:: Four
        :size: small

        Of the next.

    .. block:: Five
        :size: small

        Peeking in.

    .. block:: Six
        :size: small

        Out of sight.

.. code-block:: rst

    .. carousel::
        :cards: 4

        .. block:: One
            :size: small

            Four.

Four cards are about 150px wide in the page's text, so what's in them is best
short. A phone shows about one and a bit whatever ``:cards:`` says, so the
cards stay readable. That's any screen under 768px wide or under 500px tall,
which counts a phone on its side too.

A carousel needs at least as many items as ``:cards:`` says, so ``:cards: 4``
with three items stops the build and so does a number outside 1 to 4. With
no ``:cards:`` there's no such rule and a carousel of one item builds. When the
items are no more than the number, they all fit and the arrows hide, as they do
:ref:`below <kaamiki-arrows-and-space>`.

.. _kaamiki-a-carousel-that-moves-on-its-own:

-------------------------------------------------------------------------------
A carousel that moves on its own.
-------------------------------------------------------------------------------

``:auto-run:`` moves on by itself, every 4 seconds unless ``:interval:`` says
from 2 to 15, to the right unless ``:direction:`` says ``left``. It wraps round
at the end, it waits while a reader hovers, touches or focuses it or while it's
off screen, and it stays still for a reader who asks their device for less
motion. ``:interval:`` and ``:direction:`` need ``:auto-run:``:

.. carousel:: Always on the move.
    :auto-run:
    :interval: 3
    :direction: left

    .. block:: One
        :size: small

        Going left.

    .. block:: Two
        :size: small

        Every three seconds.

    .. block:: Three
        :size: small

        Until you touch it.

    .. block:: Four
        :size: small

        Then it waits.

.. code-block:: rst

    .. carousel:: Always on the move.
        :auto-run:
        :interval: 3
        :direction: left

        .. block:: One
            :size: small

            Going left.

.. _kaamiki-arrows-and-space:

-------------------------------------------------------------------------------
Arrows and space.
-------------------------------------------------------------------------------

``:gap:`` is the space between items, ``small`` unless it says ``medium`` or
``large``, or a length in ``rem`` like ``1.5rem``. The cards give way to it, so
``:cards:`` of them still fit in the row. ``:hide-arrows:`` leaves the arrows
out, and a reader still swipes or scrolls. When every item fits there's nothing
to move, so the arrows hide by themselves:

.. carousel::
    :gap: large
    :hide-arrows:

    .. block:: One
        :size: small

        A large gap.

    .. block:: Two
        :size: small

        And no arrows.

.. code-block:: rst

    .. carousel::
        :gap: large
        :hide-arrows:

        .. block:: One
            :size: small

            A large gap.

Two cards fit at the default, so there are no arrows to press. A phone shows
about one and a bit, so there they stay:

.. carousel::
    :gap: medium

    .. block:: One
        :size: small

        Two cards fit,

    .. block:: Two
        :size: small

        so no arrows.

.. code-block:: rst

    .. carousel::
        :gap: medium

        .. block:: One
            :size: small

            Two cards fit,

.. _kaamiki-dots-instead-of-arrows:

-------------------------------------------------------------------------------
Dots instead of arrows.
-------------------------------------------------------------------------------

``:dots:`` puts a dot for each item under the row in place of the arrows. A
pill sits on the dot of the item the row has reached and stretches out to the
next dot when the row moves, then settles on it. A tap on a dot goes to its
item. The dots are for the eye and a tap, a reader still swipes, scrolls or
uses the keys, and they hide when every item fits. ``:dots:`` takes the arrows'
place, so ``:hide-arrows:`` with it stops the build:

.. carousel::
    :dots:

    .. block:: One
        :size: small

        The first card.

    .. block:: Two
        :size: small

        The second card.

    .. block:: Three
        :size: small

        The third card.

    .. block:: Four
        :size: small

        The fourth card.

.. code-block:: rst

    .. carousel::
        :dots:

        .. block:: One
            :size: small

            The first card.

.. _kaamiki-carousel-options:

-------------------------------------------------------------------------------
Every option.
-------------------------------------------------------------------------------

.. accordion:: The full table

    .. list-table::
        :header-rows: 1
        :widths: 24 76

        * - Option
          - What it does
        * - the argument
          - The title, read as reStructuredText. It names the group.
        * - ``:preheader:``
          - A line above the title, set like the text above a section's
            heading. It needs a title.
        * - ``:subheader:``
          - A dimmer line under the title, set like a section's. It needs a
            title.
        * - ``:gap:``
          - The space between items. ``small``, the default, ``medium`` or
            ``large``, or a length in ``rem`` that replaces them, up to 4rem,
            like ``1.5rem``. Two lengths are written as ``columns`` takes them
            and the second is used.
        * - ``:cards:``
          - How many items show in full, from 1 to 4, with a quarter of the
            next one beside them. Two when it isn't given. It needs at least
            that many items. A phone shows about one and a bit whatever it
            says.
        * - ``:hide-arrows:``
          - Leaves the arrows out.
        * - ``:dots:``
          - A dot for each item under the row, in place of the arrows. It
            can't go with ``:hide-arrows:``.
        * - ``:speed:``
          - How quick its motion is, a step of the site's speed, as
            :ref:`every directive that moves takes it
            <kaamiki-directives-motion>`.
        * - ``:no-motion:``
          - Plays nothing in it, as :ref:`every directive that moves takes it
            <kaamiki-directives-motion>`.
        * - ``:auto-run:``
          - Moves on by itself and wraps round at the end.
        * - ``:interval:``
          - Seconds between moves, from 2 to 15, 4 when it isn't given. It
            needs ``:auto-run:``.
        * - ``:direction:``
          - ``right``, which is the default, or ``left``. It needs
            ``:auto-run:``.
        * - ``:name:``
          - A name to link to, as :ref:`every directive takes it
            <kaamiki-directives-common>`.
        * - ``:class:``
          - Extra classes for the carousel.

.. _kaamiki-what-stops-the-build-in-a-carousel:

-------------------------------------------------------------------------------
What stops the build.
-------------------------------------------------------------------------------

Each of these stops the build with a message that names the carousel and what
it expected:

* ``:preheader:`` or ``:subheader:`` with no title.
* ``:interval:`` or ``:direction:`` without ``:auto-run:``, an ``:interval:``
  outside 2 to 15 and a ``:gap:`` that isn't a preset or a length.
* ``:cards:`` that isn't a whole number from 1 to 4 and ``:cards:`` with fewer
  items than it says.
* ``:dots:`` together with ``:hide-arrows:``.
* No items, or anything that isn't one of the six above.
* A carousel in a carousel, in a column, in a block that links or in the notes
  of a ``code-explain`` or ``code-version``.

A carousel goes in an accordion, a tab, a note or a list. In a block it goes
only with items that aren't blocks, since a block takes no block. It doesn't go
in a column at all, since a column is about 335px wide and a row of cards needs
more room than that.
