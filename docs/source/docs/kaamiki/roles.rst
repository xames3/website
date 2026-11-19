.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 19 October 2026
.. Last updated on: 19 November 2026

:km-page-title: Kaamiki roles
:km-page-description: The inline roles Kaamiki adds for links, motion, colour,
    numbers, icons and keys, shown working, with what each one accepts.
:km-page-type: article
:km-header-subheader: Small marks inside a sentence
:km-feedback-title: Is a role missing?
:km-feedback-description: Tell me what you'd want to mark inside a sentence.
:km-feedback-button: Tell me

.. _kaamiki-roles:

===============================================================================
:fa-icon:regular:`pen-to-square` Roles
===============================================================================

.. rst-class:: km-text-lead

    Small marks inside a sentence.

A role is written ``:name:`text```. Kaamiki adds nine, and this one sentence
uses most of them: a :sharpie:`highlight`, a :underline:`pencil line`, a
:ticker:`2025?short` count, the :kbd:mac:`Cmd-K` shortcut, an
:fa-icon:solid:`heart km-tone--red` icon and a word that
:roll:`changes|moves|rolls` while you read.

Where a title is shown for something else, in the navbar, the sidebar, the
breadcrumbs, a table of contents or a link, ``sharpie``, ``underline``,
``ticker`` and ``stylise`` are plain text and ``roll`` and ``sweep`` show
their first word.
An icon stays and a key loses its keycap. A link written with ``:doc:`` or
``:ref:`` is the exception: it shows the title's words and leaves an icon out.

Every role reads its text itself, so each section below shows what to write and
what you get. Every role is checked: a value it doesn't take stops the build
with a message that names the page and the line. Each one is also something
:ref:`you can build your own role on <kaamiki-roles-custom>`.

.. _kaamiki-roles-email:

-------------------------------------------------------------------------------
email
-------------------------------------------------------------------------------

A ``mailto`` link with a subject. The text reads ``label <address>`` or just
the address, and without a label the address is the label. The subject is the
page's title unless the address names one after ``?subject=``, up to 150
characters. It's the only thing the address may ask for, so ``?body=`` or a
second setting stops the build:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        Send me an :email:`email <xa@mes3.dev>`.

        .. code-block:: rst

            Send me an :email:`email <xa@mes3.dev>`.

    .. column::

        Send me an :email:`<xa@mes3.dev>`.

        .. code-block:: rst

            Send me an :email:`<xa@mes3.dev>`.

    .. column::

        Say :email:`hello <xa@mes3.dev?subject=Hello>`.

        .. code-block:: rst

            Say :email:`hello <xa@mes3.dev?subject=Hello>`.

    .. column::

        Send me an :email:`xa@mes3.dev`.

        .. code-block:: rst

            Send me an :email:`xa@mes3.dev`.



In ``email``, ``sharpie``, ``underline`` and ``stylise`` the value is the last
``<...>`` of the text, when it opens the text or follows a space. So
``x < 5``, ``n<10`` and ``List<int>`` are plain text that can be marked. An
empty ``<>`` or ``<?>``, and a ``<`` that's never closed, stop the build.

.. _kaamiki-roles-roll:

-------------------------------------------------------------------------------
roll
-------------------------------------------------------------------------------

The text lists the words, split by ``|``. The first is what the page, its
search and a reader without scripts get. In the page the rest take its place
one by one while the words are on screen and keep doing it, in the font, size
and colour of the text around them. Every letter of the old word rolls over to
the letter of the new one, one after another from the left, the way the
greeting on the home page does, and the rest of the sentence glides to where it
sits next. A reader whose system asks for less motion gets the first word and
nothing moves:

Rebuilding NumPy to :roll:`understand|learn|rebuild` it.

.. code-block:: rst

    Rebuilding NumPy to :roll:`understand|learn|rebuild` it.

A longer or a shorter word lets the extra letters roll in from or out to
nothing, and the words after it glide along on a spring. Press the accordion
and wait for the words:

.. accordion:: Words of different lengths

    A word that grows and shrinks, :roll:`go|going|forgotten`, while a phrase
    changes length too, :roll:`two words|a longer phrase|one`.

A letter is a whole mark, so an accent, an emoji and a flag each roll in one
piece. A script whose letters join or reorder, such as Arabic or Devanagari,
rolls as a word. The rolling is hidden from a screen reader, which is given
the current word as text and never one letter at a time. The roll takes the
site's speed, and ``:speed:`` and ``:no-motion:`` on a directive around the
role change it, as :ref:`the tour of the motion
<kaamiki-example-motion-words-and-numbers-that-move>` shows.

A word can be up to 45 characters long, counted as code points, so an accent
written as its own mark counts too. It can't hold a ``|``, and ``\|`` stops
the build as well. The role can't go in a tab's title, a button's label or a
thumbnail's title, channel or caption, and the build stops there. Where a
title is shown for something else, in the navbar, the sidebar, the
breadcrumbs, a table of contents or a link, the first word stays as plain
text.

.. _kaamiki-roles-sweep:

-------------------------------------------------------------------------------
sweep
-------------------------------------------------------------------------------

It reads like ``roll``, but a band of light crosses the text: the old text
fades out behind it and the new text comes in through it. Each phrase is a
whole title or only a word, split by ``|``. The first is what the page, its
search and a reader without scripts get. In the page the rest take its place
one by one while they are on screen and keep doing it, in the font, size and
colour of the text around them. A reader whose system asks for less motion gets
the first phrase and nothing moves.

A whole title, which can run over more than one line:

.. rst-class:: km-text-lead

    :sweep:`Docs that teach|Code you can read and run|Pages that move when they should`

.. code-block:: rst

    :sweep:`Docs that teach|Code you can read and run|Pages that move when they should`

Or a word in a sentence, where the text after it glides to the new width:

Docs you can :sweep:`read|search|share|take anywhere` with anyone.

.. code-block:: rst

    Docs you can :sweep:`read|search|share|take anywhere` with anyone.

A phrase can be up to 120 characters long, counted as code points, and can't
hold a ``|``. ``\|`` stops the build as well. A sweep takes about three seconds
and the next one starts five and a half after it. A title that wraps onto more
or fewer lines than the one before it makes the room first or gives it back
last, so the page below slides instead of jumping. The role can't go in a tab's
title, a button's label or a thumbnail's title, channel or caption, and the
build stops there. Where a title is shown for something else, in the navbar,
the sidebar, the breadcrumbs, a table of contents or a link, the first phrase
stays as plain text.

The light's colours are ``--km-sweep-colours`` and the times are
``--km-sweep-hold`` and ``--km-motion-sweep``, as :ref:`the advanced page
<kaamiki-advanced-tokens>` shows.

.. _kaamiki-roles-sharpie:

-------------------------------------------------------------------------------
sharpie
-------------------------------------------------------------------------------

A highlighter over a run of text. The colour is the site's
``kaamiki.conf.roles.sharpie_colour``, yellow, unless the role names one after
the text: ``blue``, ``green``, ``red`` or ``yellow``, a hex colour like
``#ff0000``, hsl numbers like ``10 20% 30%`` or a name from
``kaamiki.conf.roles.colours``:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        This is :sharpie:`important` information.

        .. code-block:: rst

            This is :sharpie:`important` information.

    .. column::

        This is :sharpie:`critical <red>` information.

        .. code-block:: rst

            This is :sharpie:`critical <red>` information.

    .. column::

        This is :sharpie:`calm <blue>` information.

        .. code-block:: rst

            This is :sharpie:`calm <blue>` information.

    .. column::

        This is :sharpie:`good <#7c3aed>` news.

        .. code-block:: rst

            This is :sharpie:`good <#7c3aed>` news.



.. _kaamiki-roles-underline:

-------------------------------------------------------------------------------
underline
-------------------------------------------------------------------------------

A pencil underline beneath a run of text. The colour, width and wobble are the
site's ``kaamiki.conf.roles.underline_colour``,
``kaamiki.conf.roles.underline_width`` and
``kaamiki.conf.roles.underline_wobble`` unless the role names its own after the
text. The colour comes first, then the width and the wobble after a ``?`` with
an ``&`` between them. The width runs from 0.5 to 4 and the wobble from 0,
which is straight, to 2:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        This is :underline:`notable` content.

        .. code-block:: rst

            This is :underline:`notable` content.

    .. column::

        This is :underline:`notable <red>` content.

        .. code-block:: rst

            This is :underline:`notable <red>` content.

    .. column::

        This is :underline:`notable <red?width=3>` content.

        .. code-block:: rst

            This is :underline:`notable <red?width=3>` content.

    .. column::

        This is :underline:`neat <blue?wobble=0>` content.

        .. code-block:: rst

            This is :underline:`neat <blue?wobble=0>` content.



.. _kaamiki-roles-stylise:

-------------------------------------------------------------------------------
stylise
-------------------------------------------------------------------------------

A little CSS on a run of text. The text reads ``words <css>``, where the CSS is
declarations of up to 200 characters. Only properties that style text are
accepted: ``background-color``, ``color``, ``font-family``, ``font-size``,
``font-style``, ``font-variant``, ``font-variant-caps``,
``font-variant-numeric``, ``font-weight``, ``letter-spacing``,
``text-decoration`` and its ``-color``, ``-line``, ``-style`` and
``-thickness``, ``text-shadow``, ``text-transform``, ``text-underline-offset``
and ``word-spacing``. A ``url()`` is refused and so is a ``font-size`` above
4rem, 4em, 400% or 64px. Anything else, ``display``, ``opacity`` or ``margin``
say, stops the build:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        It's :stylise:`red <color: red;>` now.

        .. code-block:: rst

            It's :stylise:`red <color: red;>` now.

    .. column::

        It's :stylise:`big <font-size: 1.4rem;>` now.

        .. code-block:: rst

            It's :stylise:`big <font-size: 1.4rem;>` now.



.. _kaamiki-roles-ticker:

-------------------------------------------------------------------------------
ticker
-------------------------------------------------------------------------------

A number that rolls up from zero when it scrolls into view. The text is the
number, then ``short`` and ``duration`` after a ``?``, both optional and in
either order. ``short`` writes the number with a ``k``, ``m`` or ``b``, and a
number below a thousand shows as it is. It takes no value, so ``?short=no``
stops the build. The duration is in ``s`` or ``ms``, from 0.1s to 5s. A ticker
that isn't given one counts for as long as the site's speed says, 2s at
the default ``kaamiki.conf.motion.speed`` of ``1``, and one that is keeps it
as written:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        We've :ticker:`2025` stars.

        .. code-block:: rst

            We've :ticker:`2025` stars.

    .. column::

        We've :ticker:`2025?short` stars.

        .. code-block:: rst

            We've :ticker:`2025?short` stars.

    .. column::

        We've :ticker:`2025?short&duration=1s` stars.

        .. code-block:: rst

            We've :ticker:`2025?short&duration=1s` stars.



.. _kaamiki-roles-fa-icon:

-------------------------------------------------------------------------------
fa-icon
-------------------------------------------------------------------------------

A Font Awesome icon. The text is an icon's name and then any classes, a space
between each. The role names the style or the family: ``fa-icon:brands``,
``fa-icon:solid``, ``fa-icon:regular``, ``fa-icon:light`` or ``fa-icon:thin``
for a style, ``fa-icon:duotone``, ``fa-icon:sharp`` or
``fa-icon:sharp-duotone`` for a Pro family, and one role for each
:ref:`Pro+ pack <kaamiki-roles-fa-icon-packs>`, like ``fa-icon:jelly``. A plain
``fa-icon`` draws in the site's ``kaamiki.conf.icons.style``, which is
``regular`` unless you change it. A role can also name a family and then a
style, the family first, like ``fa-icon:sharp:light`` or
``fa-icon:duotone:thin``. A family takes only its own styles, so
``fa-icon:jelly:solid`` stops the build. An icon in the middle of a sentence
sits between its words like a word does, so the spaces you type around it are
its spacing. One that starts or ends a line is held further from its text, and
a full stop right after it still touches it. The :doc:`icons example
<examples/icons>` shows every place an icon can go:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        Watch on :fa-icon:brands:`youtube`.

        .. code-block:: rst

            Watch on :fa-icon:brands:`youtube`.

    .. column::

        Listen with :fa-icon:`headphones`.

        .. code-block:: rst

            Listen with :fa-icon:`headphones`.

    .. column::

        Show some :fa-icon:solid:`heart km-tone--red` love.

        .. code-block:: rst

            Show some :fa-icon:solid:`heart km-tone--red` love.

    .. column::

        Add a :fa-icon:`star km-tone--yellow` star.

        .. code-block:: rst

            Add a :fa-icon:`star km-tone--yellow` star.

    .. column::

        Go :fa-icon:sharp:light:`house` home.

        .. code-block:: rst

            Go :fa-icon:sharp:light:`house` home.

    .. column::

        A :fa-icon:duotone:thin:`bolt km-tone--blue` thin spark.

        .. code-block:: rst

            A :fa-icon:duotone:thin:`bolt km-tone--blue` thin spark.



Without a Font Awesome Pro kit, a name that isn't in Font Awesome Free stops
the build and, when it can, suggests the nearest one. :ref:`Icons in settings
<kaamiki-settings-icons>` explains the kit and the Free and Pro pairs, and
:ref:`classes <kaamiki-classes>` lists the classes you can add.

.. _kaamiki-roles-fa-icon-packs:

.. rubric:: Pro+ packs

A Pro+ pack has one style, and its role draws in it, so
``:fa-icon:jelly:`house``` is ``fa-jelly fa-regular fa-house``. A pack holds
about 200 of the most common icons, not the whole set, and your kit must have
the pack turned on. Without a kit, each one becomes the Free icon in the
nearest style.

.. list-table::
    :header-rows: 1
    :widths: 40 20 40

    * - Role
      - Icon
      - Style
    * - ``fa-icon:chisel``
      - :fa-icon:chisel:`house`
      - ``regular``
    * - ``fa-icon:etch``
      - :fa-icon:etch:`house`
      - ``solid``
    * - ``fa-icon:graphite``
      - :fa-icon:graphite:`house`
      - ``thin``
    * - ``fa-icon:jelly``
      - :fa-icon:jelly:`house`
      - ``regular``
    * - ``fa-icon:jelly-fill``
      - :fa-icon:jelly-fill:`house`
      - ``regular``
    * - ``fa-icon:jelly-duo``
      - :fa-icon:jelly-duo:`house`
      - ``regular``
    * - ``fa-icon:mosaic``
      - :fa-icon:mosaic:`house`
      - ``solid``
    * - ``fa-icon:notdog``
      - :fa-icon:notdog:`house`
      - ``solid``
    * - ``fa-icon:notdog-duo``
      - :fa-icon:notdog-duo:`house`
      - ``solid``
    * - ``fa-icon:pixel``
      - :fa-icon:pixel:`house`
      - ``regular``
    * - ``fa-icon:slab``
      - :fa-icon:slab:`house`
      - ``regular``
    * - ``fa-icon:slab-press``
      - :fa-icon:slab-press:`house`
      - ``regular``
    * - ``fa-icon:slab-duo``
      - :fa-icon:slab-duo:`house`
      - ``regular``
    * - ``fa-icon:slab-press-duo``
      - :fa-icon:slab-press-duo:`house`
      - ``regular``
    * - ``fa-icon:thumbprint``
      - :fa-icon:thumbprint:`house`
      - ``light``
    * - ``fa-icon:utility``
      - :fa-icon:utility:`house`
      - ``semibold``
    * - ``fa-icon:utility-fill``
      - :fa-icon:utility-fill:`house`
      - ``semibold``
    * - ``fa-icon:utility-duo``
      - :fa-icon:utility-duo:`house`
      - ``semibold``
    * - ``fa-icon:vellum``
      - :fa-icon:vellum:`house`
      - ``solid``
    * - ``fa-icon:whiteboard``
      - :fa-icon:whiteboard:`house`
      - ``semibold``

.. _kaamiki-roles-kbd:

-------------------------------------------------------------------------------
kbd
-------------------------------------------------------------------------------

A keyboard shortcut, printed the way a system prints it. It reads like Sphinx's
own ``kbd``, with keys joined by ``-``, ``+`` or ``^``. The role names the
system: ``kbd:mac``, ``kbd:windows`` or ``kbd:linux``, and a plain ``kbd`` is a
Mac:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        Copy with :kbd:mac:`Cmd-C`.

        .. code-block:: rst

            Copy with :kbd:mac:`Cmd-C`.

    .. column::

        Copy with :kbd:windows:`Ctrl-C`.

        .. code-block:: rst

            Copy with :kbd:windows:`Ctrl-C`.

    .. column::

        Pause with :kbd:`Space`.

        .. code-block:: rst

            Pause with :kbd:`Space`.

    .. column::

        Jump back with :kbd:`Cmd-Up`.

        .. code-block:: rst

            Jump back with :kbd:`Cmd-Up`.



The text stays in the page, so search and screen readers still read "Cmd".
Keys joined into one combo stay on one line when they fit. ``Space`` and
``Bar`` written one after the other, with a space between, are one wide key.
``Super`` is drawn as the Windows logo for ``kbd:windows`` and the Ubuntu logo
for ``kbd:linux``, and written out as a word on a Mac and in a plain ``kbd``.

.. _kaamiki-roles-custom:

-------------------------------------------------------------------------------
Your own roles.
-------------------------------------------------------------------------------

Every role can be the base of one of your own, the way Docutils' ``role``
directive builds them. The new role draws what its base draws, gets a class
named after it and keeps the values you preset:

.. role:: warn(sharpie)
    :colour: red

.. role:: stat(ticker)
    :short:
    :duration: 1s

This is a :warn:`warning` and we have :stat:`2025` stars.

.. code-block:: rst

    .. role:: warn(sharpie)
        :colour: red

    .. role:: stat(ticker)
        :short:
        :duration: 1s

    This is a :warn:`warning` and we have :stat:`2025` stars.

A role's class is its own name, ``warn`` and ``stat`` here, unless ``:class:``
gives it others, which are split by spaces and written the way Docutils reads
them. What the text says wins over a preset, and a preset wins over the site's
setting, so ``:warn:`careful <blue>``` is blue and a plain ``:warn:`careful```
is red. The base can be any role above, another role of your own or one with a
style like ``fa-icon:solid`` or ``kbd:mac``. A preset that isn't right stops
the build at the ``role`` directive, naming the option.

.. accordion:: What each base presets

    .. list-table::
        :header-rows: 1
        :widths: 24 76

        * - Base
          - What it presets
        * - ``sharpie``
          - ``:colour:``, a colour or the name of one, as in the text.
        * - ``underline``
          - ``:colour:``, ``:width:`` and ``:wobble:``, as after the ``?`` in
            the text.
        * - ``ticker``
          - ``:short:``, a flag, and ``:duration:``, like ``1s`` or ``500ms``.
        * - ``stylise``
          - ``:style:``, the CSS, so the text is only the words.
        * - ``email``
          - ``:subject:``, for every address the role writes.
        * - ``roll``, ``sweep``, ``fa-icon``, ``kbd``
          - Nothing besides ``:class:``. Their text is all there is to say.
