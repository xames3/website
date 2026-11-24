.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 October 2026
.. Last updated on: 23 November 2026

:km-page-title: Icons, everywhere
:km-page-description: Every place a Font Awesome icon can go on this website,
    written out and shown working side by side.
:km-page-type: article
:km-header-subheader: Every place an icon can go
:km-feedback-title: Did I miss a place for an icon?
:km-feedback-description: Tell me where you tried one and it didn't sit right.
:km-feedback-button: Tell me
:km-feedback-icon: fa-icons

.. _kaamiki-example-icons:

===============================================================================
:fa-icon:regular:`icons` Icons, everywhere
===============================================================================

.. rst-class:: km-text-lead

    Every place an icon can go, written out and shown working.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3
    :shade: purple

An icon can sit in a sentence, a heading, an admonition, a button, a tab, a
code caption and in the furniture of the page itself. Each section below
writes the markup out next to what it draws, so one page can be scrolled to
check them all. The last two sections copy the header and the sidebar, which
lets their icons be seen next to everything else.

.. _kaamiki-icons-the-places:

-------------------------------------------------------------------------------
The places, in one list.
-------------------------------------------------------------------------------

.. list-table::
    :header-rows: 1
    :widths: 30 40 30

    * - Where
      - What you write
      - Shown in
    * - A sentence
      - The ``fa-icon`` role
      - :ref:`The role <kaamiki-icons-the-role>`
    * - A size, a motion or a colour
      - Classes after the icon's name
      - :ref:`Sizes, motion and colour <kaamiki-icons-sizes-motion-colour>`
    * - The start, middle or end of a line
      - The same role, placed there
      - :ref:`Where an icon sits <kaamiki-icons-where-it-sits>`
    * - Lists, tables, quotes and rubrics
      - The role inside them
      - :ref:`In text <kaamiki-icons-in-text>`
    * - A heading
      - The role in the title
      - :ref:`In headings <kaamiki-icons-in-headings>`
    * - An admonition
      - The role in its title or its body
      - :ref:`In admonitions <kaamiki-icons-in-admonitions>`
    * - A button or a tab
      - ``:fa-icon:`` and ``:icon-position:``
      - :ref:`In directives <kaamiki-icons-in-directives>`
    * - An accordion or a block
      - The role in its title, preheader or footer
      - :ref:`In directives <kaamiki-icons-in-directives>`
    * - A code caption
      - The language's own icon or the role
      - :ref:`In code <kaamiki-icons-in-code>`
    * - A keyboard shortcut
      - The ``kbd`` role
      - :ref:`In code <kaamiki-icons-in-code>`
    * - A page's title
      - The role in the page title
      - :ref:`In the page itself <kaamiki-icons-in-the-page>`
    * - The feedback box
      - ``:km-feedback-icon:``
      - :ref:`In the page itself <kaamiki-icons-in-the-page>`
    * - The theme's own icons
      - ``kaamiki.conf.icons.names``
      - :ref:`In the page itself <kaamiki-icons-in-the-page>`
    * - The header
      - Page titles and ``kaamiki.conf.site.header_buttons``
      - :ref:`The navbar <kaamiki-icons-the-navbar>`
    * - The sidebar
      - Page titles and ``kaamiki.conf.site.sidebar_buttons``
      - :ref:`The sidebar <kaamiki-icons-the-sidebar>`

.. _kaamiki-icons-the-role:

-------------------------------------------------------------------------------
The role, in every style.
-------------------------------------------------------------------------------

The :ref:`fa-icon role <kaamiki-roles-fa-icon>` draws an icon in the line. The
role names the style and the text names the icon, so ``:fa-icon:solid:`star```
is a solid star. A name works with or without the ``fa-`` ahead of it:

.. list-table::
    :header-rows: 1
    :widths: 46 14 40

    * - You write
      - You get
      - Style
    * - ``:fa-icon:`star```
      - :fa-icon:`star`
      - The site's ``kaamiki.conf.icons.style``
    * - ``:fa-icon:`fa-star```
      - :fa-icon:`fa-star`
      - The same, with the ``fa-``
    * - ``:fa-icon:regular:`star```
      - :fa-icon:regular:`star`
      - Regular
    * - ``:fa-icon:solid:`star```
      - :fa-icon:solid:`star`
      - Solid
    * - ``:fa-icon:light:`star```
      - :fa-icon:light:`star`
      - Light
    * - ``:fa-icon:thin:`star```
      - :fa-icon:thin:`star`
      - Thin
    * - ``:fa-icon:duotone:`star```
      - :fa-icon:duotone:`star`
      - Duotone
    * - ``:fa-icon:brands:`github```
      - :fa-icon:brands:`github`
      - Brands

.. _kaamiki-icons-sizes-motion-colour:

-------------------------------------------------------------------------------
Sizes, motion and colour.
-------------------------------------------------------------------------------

Anything after the name is a class, with a space between each. ``fa-2xs`` to
``fa-2xl`` and ``fa-1x`` to ``fa-10x`` set the size, the motion and turning
classes move the icon and four tones colour it. Any other class stops the
build.

.. columns:: 2
    :gap: medium
    :valign: top

    .. column::

        .. list-table::
            :header-rows: 1
            :widths: 60 40

            * - Size
              - You get
            * - ``:fa-icon:`star fa-2xs```
              - :fa-icon:`star fa-2xs`
            * - ``:fa-icon:`star fa-xs```
              - :fa-icon:`star fa-xs`
            * - ``:fa-icon:`star fa-sm```
              - :fa-icon:`star fa-sm`
            * - ``:fa-icon:`star fa-lg```
              - :fa-icon:`star fa-lg`
            * - ``:fa-icon:`star fa-xl```
              - :fa-icon:`star fa-xl`
            * - ``:fa-icon:`star fa-2xl```
              - :fa-icon:`star fa-2xl`
            * - ``:fa-icon:`star fa-2x```
              - :fa-icon:`star fa-2x`
            * - ``:fa-icon:`star fa-3x```
              - :fa-icon:`star fa-3x`
            * - ``:fa-icon:`house fa-fw```
              - :fa-icon:`house fa-fw`

    .. column::

        .. list-table::
            :header-rows: 1
            :widths: 60 40

            * - Motion
              - You get
            * - ``:fa-icon:`heart fa-beat```
              - :fa-icon:`heart fa-beat`
            * - ``:fa-icon:`heart fa-beat-fade```
              - :fa-icon:`heart fa-beat-fade`
            * - ``:fa-icon:`arrow-down fa-bounce```
              - :fa-icon:`arrow-down fa-bounce`
            * - ``:fa-icon:`star fa-fade```
              - :fa-icon:`star fa-fade`
            * - ``:fa-icon:`spinner fa-pulse```
              - :fa-icon:`spinner fa-pulse`
            * - ``:fa-icon:`bell fa-shake```
              - :fa-icon:`bell fa-shake`
            * - ``:fa-icon:`gear fa-spin```
              - :fa-icon:`gear fa-spin`
            * - ``:fa-icon:`gear fa-spin-reverse```
              - :fa-icon:`gear fa-spin-reverse`
            * - ``:fa-icon:`spinner fa-spin-pulse```
              - :fa-icon:`spinner fa-spin-pulse`

.. list-table::
    :header-rows: 1
    :widths: 60 40

    * - Turn
      - You get
    * - ``:fa-icon:`arrow-right fa-rotate-90```
      - :fa-icon:`arrow-right fa-rotate-90`
    * - ``:fa-icon:`arrow-right fa-rotate-180```
      - :fa-icon:`arrow-right fa-rotate-180`
    * - ``:fa-icon:`arrow-right fa-rotate-270```
      - :fa-icon:`arrow-right fa-rotate-270`
    * - ``:fa-icon:`arrow-right fa-flip-horizontal```
      - :fa-icon:`arrow-right fa-flip-horizontal`
    * - ``:fa-icon:`arrow-right fa-flip-vertical```
      - :fa-icon:`arrow-right fa-flip-vertical`
    * - ``:fa-icon:`arrow-right fa-flip-both```
      - :fa-icon:`arrow-right fa-flip-both`

.. list-table::
    :header-rows: 1
    :widths: 60 40

    * - Colour
      - You get
    * - ``:fa-icon:solid:`heart km-tone--red```
      - :fa-icon:solid:`heart km-tone--red`
    * - ``:fa-icon:solid:`star km-tone--yellow```
      - :fa-icon:solid:`star km-tone--yellow`
    * - ``:fa-icon:solid:`circle-info km-tone--blue```
      - :fa-icon:solid:`circle-info km-tone--blue`
    * - ``:fa-icon:solid:`circle-check km-tone--green```
      - :fa-icon:solid:`circle-check km-tone--green`
    * - Size, motion and colour together
      - :fa-icon:solid:`heart fa-lg fa-beat km-tone--red`

.. _kaamiki-icons-where-it-sits:

-------------------------------------------------------------------------------
Where an icon sits in a line.
-------------------------------------------------------------------------------

An icon is spaced by what is around it. One at the start or the end of a line
keeps further from its text than one in the middle of a sentence, which sits
between its words the way a word does. Both show below, in a table and then in
paragraphs of their own:

.. list-table::
    :header-rows: 1
    :widths: 50 50

    * - You write
      - You get
    * - ``:fa-icon:regular:`star` Before the text``
      - :fa-icon:regular:`star` Before the text
    * - ``After the text :fa-icon:regular:`star```
      - After the text :fa-icon:regular:`star`
    * - ``In the :fa-icon:regular:`star` middle``
      - In the :fa-icon:regular:`star` middle
    * - ``One :fa-icon:regular:`star` and two :fa-icon:regular:`heart` more
        :fa-icon:regular:`bell` in a sentence``
      - One :fa-icon:regular:`star` and two :fa-icon:regular:`heart` more
        :fa-icon:regular:`bell` in a sentence
    * - ``Watch on :fa-icon:brands:`youtube`.``
      - Watch on :fa-icon:brands:`youtube`.
    * - ``:fa-icon:regular:`star``` on its own
      - :fa-icon:regular:`star`
    * - ``:fa-icon:regular:`star` :fa-icon:regular:`heart` Two before``
      - :fa-icon:regular:`star` :fa-icon:regular:`heart` Two before
    * - ``Two after :fa-icon:regular:`star` :fa-icon:regular:`heart```
      - Two after :fa-icon:regular:`star` :fa-icon:regular:`heart`

:fa-icon:regular:`star` This paragraph starts with an icon and carries on long
enough to wrap onto a second line, so the icon stays with the first one.

This paragraph ends with an icon :fa-icon:regular:`star`

This paragraph has an icon :fa-icon:regular:`star` in the middle, another
:fa-icon:regular:`heart` a little further along and a third
:fa-icon:regular:`bell` near the end, with the text wrapping around all of
them as it would in any sentence.

.. _kaamiki-icons-in-text:

-------------------------------------------------------------------------------
In text.
-------------------------------------------------------------------------------

Everywhere text goes, an icon can go. Each of these is written the same way, so
only where the icon sits changes.

Paragraphs and their neighbours
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An icon sits happily beside **bold** text :fa-icon:regular:`bold`, *italic*
text :fa-icon:regular:`italic`, ``literal`` text :fa-icon:regular:`code`, a
:doc:`link <../roles>` :fa-icon:regular:`link` and a
:kbd:`Cmd-K` shortcut :fa-icon:regular:`keyboard` in the same line.

Lists
^^^^^

- :fa-icon:regular:`star` A bullet with an icon before its text
- A bullet with an icon after its text :fa-icon:regular:`star`
- A bullet with an :fa-icon:regular:`star` icon in the middle
- A bullet with no icon at all

1. :fa-icon:regular:`star` A numbered item with an icon before its text
2. A numbered item with an icon after its text :fa-icon:regular:`star`
3. A numbered item with an :fa-icon:regular:`star` icon in the middle

Definitions, quotes and lines
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:fa-icon:regular:`star` A term with an icon before it
    Its definition, with an :fa-icon:regular:`heart` icon in the middle.

A term with an icon after it :fa-icon:regular:`star`
    Its definition, with an icon at the end :fa-icon:regular:`heart`

    :fa-icon:regular:`quote-left` A quotation that opens with an icon, set in
    a block quote.

    -- :fa-icon:regular:`user` Someone, with an icon before the name

| :fa-icon:regular:`star` A line of a line block that starts with an icon
| A line of a line block that ends with one :fa-icon:regular:`star`
| A line of a line block with one :fa-icon:regular:`star` in the middle

Tables
^^^^^^

.. list-table::
    :header-rows: 1
    :widths: 34 33 33

    * - :fa-icon:regular:`table` Header, icon first
      - Header, icon last :fa-icon:regular:`table`
      - A :fa-icon:regular:`table` header, icon inside
    * - :fa-icon:regular:`star` Cell, icon first
      - Cell, icon last :fa-icon:regular:`star`
      - A :fa-icon:regular:`star` cell, icon inside
    * - :fa-icon:solid:`circle-check km-tone--green` Passed
      - :fa-icon:solid:`circle-xmark km-tone--red` Failed
      - :fa-icon:solid:`triangle-exclamation km-tone--yellow` Skipped

Rubrics
^^^^^^^

A rubric with the ``km-text-preheader`` class is the small line above a
section, and it takes an icon like any other line:

.. rubric:: :fa-icon:regular:`compass-drafting` A rubric, icon first
    :class: km-text-preheader

.. rubric:: A rubric, icon last :fa-icon:regular:`compass-drafting`
    :class: km-text-preheader

.. rubric:: A rubric with an :fa-icon:regular:`compass-drafting` icon inside
    :class: km-text-preheader

.. _kaamiki-icons-in-headings:

-------------------------------------------------------------------------------
In headings.
-------------------------------------------------------------------------------

A heading's title is text, so it takes the role. A page's own title is the
exception: its icon is the one the navigation shows, which the :ref:`page
itself <kaamiki-icons-in-the-page>` explains. Every heading below is a real
one:

:fa-icon:regular:`star` A heading with an icon first
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Text under it.

A heading with an icon last :fa-icon:regular:`star`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Text under it.

A heading with an :fa-icon:regular:`star` icon inside
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Text under it.

.. _kaamiki-icons-in-admonitions:

-------------------------------------------------------------------------------
In admonitions.
-------------------------------------------------------------------------------

An admonition draws the icon of its kind at its left and keeps its title out of
sight. This website's ``am-unusual-one`` class puts the title back and drops
that icon, so a title is where an icon of your own goes. A generic
``admonition`` takes a kind in ``:class:``:

.. admonition:: :fa-icon:regular:`lightbulb` An icon before the title
    :class: am-unusual-one tip

    The body, with an :fa-icon:regular:`heart` icon in the middle of a line.

.. admonition:: An icon after the title :fa-icon:regular:`lightbulb`
    :class: am-unusual-one note

    The body, with an icon at the end of its line :fa-icon:regular:`heart`

.. admonition:: A title with an :fa-icon:regular:`lightbulb` icon inside
    :class: am-unusual-one warning

    :fa-icon:regular:`heart` The body, with an icon at the start of its line.

.. admonition:: :fa-icon:regular:`star` Both ends :fa-icon:regular:`heart`
    :class: am-unusual-one important

    Both ends of the title carry one.

.. admonition:: :fa-icon:solid:`bell km-tone--yellow` A coloured icon
    :class: am-unusual-one danger

    The tone is part of the role, so the title's own colour is left alone.

.. admonition:: :fa-icon:brands:`github` A brand icon
    :class: am-unusual-one seealso

    Brands draw like any other icon.

A generic ``admonition`` is named by its title, so a title that's only an icon
stops the build with "admonition: expected a title with words". The built-in
kinds below are named by their kind and may show just their icon.

The built-in kinds keep the icon they draw and take icons in their body:

.. note::

    :fa-icon:regular:`circle-info` A ``note``, with an icon first.

.. tip::

    A ``tip``, with an icon last :fa-icon:regular:`lightbulb`

.. hint::

    A ``hint``, with an :fa-icon:regular:`eye` icon inside.

.. important::

    :fa-icon:regular:`star` An ``important``, with an icon first.

.. warning::

    A ``warning``, with an icon last :fa-icon:regular:`triangle-exclamation`

.. caution::

    A ``caution``, with an :fa-icon:regular:`hand` icon inside.

.. attention::

    :fa-icon:regular:`bullseye` An ``attention``, with an icon first.

.. danger::

    A ``danger``, with an icon last :fa-icon:regular:`skull`

.. error::

    An ``error``, with an :fa-icon:regular:`circle-xmark` icon inside.

.. seealso::

    - :fa-icon:regular:`link` A ``seealso`` with a list, icons first
    - A ``seealso`` with a list, icons last :fa-icon:regular:`link`

.. _kaamiki-icons-in-directives:

-------------------------------------------------------------------------------
In directives.
-------------------------------------------------------------------------------

Some directives take an icon as an option and some take the role in a title.
Here's each one:

Buttons
^^^^^^^

A ``button`` takes ``:fa-icon:`` and ``:icon-position:``. The option is written
like an icon in the settings, so a style comes first and the classes last.

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        .. button:: https://github.com/xames3/website
            :fa-icon: heart

            Icon before the label

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :fa-icon: heart

                Icon before the label

    .. column::

        .. button:: https://github.com/xames3/website
            :fa-icon: arrow-right
            :icon-position: after

            Icon after the label

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :fa-icon: arrow-right
                :icon-position: after

                Icon after the label

    .. column::

        .. button:: https://github.com/xames3/website
            :fa-icon: fa-brands fa-github

            A brand icon

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :fa-icon: fa-brands fa-github

                A brand icon

    .. column::

        .. button:: https://github.com/xames3/website
            :fa-icon: fa-solid fa-heart fa-beat
            :scheme: red

            A moving icon

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :fa-icon: fa-solid fa-heart fa-beat
                :scheme: red

                A moving icon

    .. column::

        .. button:: https://github.com/xames3/website
            :fa-icon: download
            :scheme: dark

            A dark button

        .. code-block:: rst

            .. button:: https://github.com/xames3/website
                :fa-icon: download
                :scheme: dark

                A dark button

    .. column::

        .. button:: https://github.com/xames3/website

            No icon at all

        .. code-block:: rst

            .. button:: https://github.com/xames3/website

                No icon at all

Tabs
^^^^

A ``tab`` takes the same two options. The icon is the title's, so it sits
before or after the words and the title stays one line.

.. tabs::

    .. tab:: Before
        :fa-icon: fa-regular fa-code
        :selected:

        A tab with its icon before the title :fa-icon:regular:`code`

    .. tab:: After
        :fa-icon: fa-regular fa-comments
        :icon-position: after

        A tab with its icon after the title :fa-icon:regular:`comments`

    .. tab:: Brand
        :fa-icon: fa-brands fa-python

        A tab with a brand icon :fa-icon:brands:`python`

    .. tab:: Plain

        A tab with no icon at all.

.. code-block:: rst

    .. tabs::

        .. tab:: Before
            :fa-icon: fa-regular fa-code
            :selected:

            A tab with its icon before the title

        .. tab:: After
            :fa-icon: fa-regular fa-comments
            :icon-position: after

            A tab with its icon after the title

Accordions
^^^^^^^^^^

An ``accordion``'s title takes the role, and ``:marker:`` and
``:marker-position:`` choose the icon that shows it opens.

.. accordion:: :fa-icon:regular:`star` An icon before the title

    The content, with an :fa-icon:regular:`heart` icon in the middle.

.. accordion:: An icon after the title :fa-icon:regular:`star`

    The content, with an icon at the end :fa-icon:regular:`heart`

.. accordion:: A title with an :fa-icon:regular:`star` icon inside
    :marker: down

    :fa-icon:regular:`heart` The content, with an icon at the start.

.. accordion:: A right marker, after the title
    :marker: right
    :marker-position: after

    The marker is an icon too.

.. accordion:: A down marker, before the title
    :marker: down
    :marker-position: before

    The marker is an icon too.

.. code-block:: rst

    .. accordion:: :fa-icon:regular:`star` An icon before the title

        The content.

    .. accordion:: A right marker, after the title
        :marker: right
        :marker-position: after

        The marker is an icon too.

Blocks
^^^^^^

A ``block`` takes the role in its ``:preheader:`` and its ``:footer:``:

.. block:: A preheader
    :size: medium
    :preheader: :fa-icon:regular:`download` Icon first

    The preheader's icon is before its text.

.. block:: A footer
    :size: medium
    :footer: Icon last :fa-icon:regular:`arrow-right`

    The footer's icon is after its text.

.. block:: Both
    :size: medium
    :preheader: :fa-icon:regular:`star` Preheader
    :footer: Footer :fa-icon:regular:`heart`

    Both ends of the block carry one.

.. block:: A link
    :size: medium
    :doc: ../roles
    :preheader: Icon :fa-icon:regular:`heart` inside

    A block that links to a page.

.. code-block:: rst

    .. block:: Both
        :size: medium
        :preheader: :fa-icon:regular:`star` Preheader
        :footer: Footer :fa-icon:regular:`heart`

        Both ends of the block carry one.

Columns and cards
^^^^^^^^^^^^^^^^^

A ``columns`` cell is as narrow as its column, so an icon wraps with the text.

.. columns:: 3
    :gap: medium
    :valign: top

    .. column::

        :fa-icon:regular:`star` A cell with an icon at the start, wrapping
        onto a second line.

    .. column::

        A cell with an icon at the end, wrapping onto a second line
        :fa-icon:regular:`star`

    .. column::

        A cell with an :fa-icon:regular:`star` icon in the middle, wrapping
        onto a second line.

A ``repository`` card draws a star and a fork count of its own:

.. repository:: xames3/slowtorch

.. _kaamiki-icons-in-code:

-------------------------------------------------------------------------------
In code.
-------------------------------------------------------------------------------

A code block's caption wears the icon of its language, picked for it. A
language with no icon of its own, like a diff, hands over to the caption's file
name, and a caption that opens with an icon of its own keeps it.

Captions
^^^^^^^^

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        .. code-block:: python
            :caption: total.py

            total = sum(range(3))

    .. column::

        .. code-block:: console
            :caption: Terminal

            $ python total.py

    .. column::

        .. code-block:: javascript
            :caption: total.js

            const total = 3;

    .. column::

        .. code-block:: html
            :caption: index.html

            <p>Hello</p>

    .. column::

        .. code-block:: css
            :caption: site.css

            p { color: red; }

    .. column::

        .. code-block:: json
            :caption: data.json

            {"total": 3}

    .. column::

        .. code-block:: yaml
            :caption: config.yml

            total: 3

    .. column::

        .. code-block:: rst
            :caption: index.rst

            A paragraph.

    .. column::

        .. code-block:: sql
            :caption: query.sql

            SELECT 3;

    .. column::

        .. code-block:: diff
            :caption: setup.py

            - total = 2
            + total = 3

    .. column::

        .. code-block:: diff
            :caption: notes.xyz

            - total = 2
            + total = 3

    .. column::

        .. code-block:: python
            :caption: :fa-icon:solid:`flask` Its own icon first

            total = sum(range(3))

    .. column::

        .. code-block:: python
            :caption: Its own icon last :fa-icon:solid:`flask`

            total = sum(range(3))

    .. column::

        .. code-block:: python

            total = sum(range(3))

Code that runs
^^^^^^^^^^^^^^

A ``code-explain`` and a ``code-version`` head their code the same way:

.. code-explain:: python
    :caption: total.py
    :watch: total

    .. code::

        total = 0
        for i in range(3):
            total += i

    .. lines:: 1

        Start at zero.

    .. lines:: 2-3

        Add each number in turn.

Keys
^^^^

The ``kbd`` role draws an icon for the arrows, the globe and Super:

.. list-table::
    :header-rows: 1
    :widths: 50 50

    * - You write
      - You get
    * - ``:kbd:mac:`Cmd-Up```
      - :kbd:mac:`Cmd-Up`
    * - ``:kbd:mac:`Globe-E```
      - :kbd:mac:`Globe-E`
    * - ``:kbd:windows:`Super-Left```
      - :kbd:windows:`Super-Left`
    * - ``:kbd:linux:`Super-L```
      - :kbd:linux:`Super-L`
    * - ``:kbd:windows:`Ctrl-Shift-Esc```
      - :kbd:windows:`Ctrl-Shift-Esc`

.. _kaamiki-icons-in-the-page:

-------------------------------------------------------------------------------
In the page itself.
-------------------------------------------------------------------------------

The page's own furniture is drawn with icons too, and each has its own way in.

The title. This page's title starts with :fa-icon:regular:`icons`, written
the same way as in a sentence. The navigation lists the title as it is, so the
icon turns up in the header's dropdown and in the sidebar. The breadcrumbs
leave it out and the title itself hides it.

The feedback box. At the end of this page, the button wears the icon the
page's ``:km-feedback-icon:`` field names, ``fa-icons``.

The theme's own icons. Kaamiki draws these itself and
``kaamiki.conf.icons.names`` swaps any of them. Here are the ones that sit in
the page's furniture, in the style the site uses with a kit. :ref:`Icons in
settings <kaamiki-settings-icons>` lists all 30:

.. list-table::
    :header-rows: 1
    :widths: 40 15 45

    * - Name
      - Icon
      - Where it shows
    * - ``breadcrumb_separator_child``
      - :fa-icon:regular:`angle-right`
      - Between two steps
    * - ``breadcrumb_separator_parent``
      - :fa-icon:regular:`angles-right`
      - After the first step of the trail
    * - ``close``
      - :fa-icon:regular:`xmark`
      - The close button of an enlarged picture
    * - ``copy_url``
      - :fa-icon:regular:`link`
      - The copy link button
    * - ``external_link``
      - :fa-icon:regular:`arrow-up-right-from-square`
      - A sidebar link with no icon
    * - ``feedback``
      - :fa-icon:regular:`paper-plane`
      - The feedback button
    * - ``language``
      - :fa-icon:regular:`language`
      - The language in a byline
    * - ``menu``
      - :fa-icon:regular:`bars`
      - The button that opens the sidebar
    * - ``page_source``
      - :fa-icon:regular:`file-lines`
      - The link to a page's source
    * - ``play``
      - :fa-icon:regular:`play`
      - A video that hasn't started
    * - ``reading_time``
      - :fa-icon:regular:`clock`
      - The time to read a page
    * - ``release_date``
      - :fa-icon:regular:`calendar`
      - The date a release came out
    * - ``release_notes``
      - :fa-icon:solid:`tag`
      - A link to a release
    * - ``scrolltop``
      - :fa-icon:regular:`arrow-up`
      - The button back to the top
    * - ``search``
      - :fa-icon:regular:`magnifying-glass`
      - The search in the header
    * - ``show_more``
      - :fa-icon:regular:`chevron-down`
      - The button under a folded page

:ref:`Icons in settings <kaamiki-settings-icons>` explains how an icon is
written there and what a site with no kit draws instead.

.. _kaamiki-icons-the-navbar:

-------------------------------------------------------------------------------
The navbar, simulated.
-------------------------------------------------------------------------------

This is the header's own markup, copied here so its icons sit on a page of
their own. Below it is the menu that opens under **Extras** with an icon, a
tone, a long title and no icon, in one list. It can fall behind the real one,
which is built from the page titles above.

.. embed:: /assets/html/icons-navbar.html

.. _kaamiki-icons-the-sidebar:

-------------------------------------------------------------------------------
The sidebar, simulated.
-------------------------------------------------------------------------------

The sidebar is the same list on a narrow screen and on a page that sets
``:km-toctree-in-header: false``, as the
:doc:`overrides example <overrides>` does. This is its markup, with the current
page, a nested entry, a title with no icon and the external links under it:

.. embed:: /assets/html/icons-sidebar.html
