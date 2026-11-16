.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 October 2026
.. Last updated on: 16 November 2026

:km-page-title: Tabs, everywhere
:km-page-description: Every option of the tabs and tab directives on and off,
    with icons and roles, holding every other directive and inside every
    container that takes them.
:km-page-type: article
:km-header-subheader: Every way to switch content
:km-feedback-title: Did I miss a way to combine them?
:km-feedback-description: Tell me what you tried with tabs that didn't work.
:km-feedback-button: Tell me
:km-feedback-icon: fa-table-columns

.. _combos-tabs:

===============================================================================
:fa-icon:regular:`table-columns` Tabs, everywhere
===============================================================================

.. rst-class:: km-text-lead

    Content that switches, in every combination.

Tabs show one panel at a time. This page writes them with every option on and
off, with icons and roles in their titles, with every other Kaamiki directive
inside a tab and tabs inside every container that takes them, so the markup and
the result sit side by side.

.. _combos-tabs-the-options-of-tabs-one-at-a-time:

-------------------------------------------------------------------------------
The options of tabs, one at a time.
-------------------------------------------------------------------------------

No options.

.. tabs::

    .. tab:: One

        Content of One.

    .. tab:: Two

        Content of Two.

.. code-block:: rst

    .. tabs::

        .. tab:: One

            Content of One.

        .. tab:: Two

            Content of Two.

``:align: left``

.. tabs::
    :align: left

    .. tab:: Left

        Content of Left.

    .. tab:: Centre

        Content of Centre.

    .. tab:: Right

        Content of Right.

.. code-block:: rst

    .. tabs::
        :align: left

        .. tab:: Left

            Content of Left.

        .. tab:: Centre

            Content of Centre.

        .. tab:: Right

            Content of Right.

``:align: right``

.. tabs::
    :align: right

    .. tab:: Left

        Content of Left.

    .. tab:: Centre

        Content of Centre.

    .. tab:: Right

        Content of Right.

.. code-block:: rst

    .. tabs::
        :align: right

        .. tab:: Left

            Content of Left.

        .. tab:: Centre

            Content of Centre.

        .. tab:: Right

            Content of Right.

``:class:`` on the set and ``:class-bar:`` on the row of titles.

.. tabs::
    :class: km-tone-blue
    :class-bar: km-tone-green

    .. tab:: Classes

        Content of Classes.

    .. tab:: Everywhere

        Content of Everywhere.

.. code-block:: rst

    .. tabs::
        :class: km-tone-blue
        :class-bar: km-tone-green

        .. tab:: Classes

            Content of Classes.

        .. tab:: Everywhere

            Content of Everywhere.

Groups and keys
^^^^^^^^^^^^^^^

Tab sets that share a ``:group:`` switch together, by the tab's title or by its
``:key:``. Pick a tab in either set:

.. tabs::
    :group: combos-os

    .. tab:: macOS

        Shown for macOS.

    .. tab:: Windows

        Shown for Windows.

.. tabs::
    :group: combos-os

    .. tab:: macOS

        A second set, also for macOS.

    .. tab:: Windows

        A second set, also for Windows.

.. code-block:: rst

    .. tabs::
        :group: combos-os

        .. tab:: macOS

            Shown for macOS.

        .. tab:: Windows

            Shown for Windows.

    .. tabs::
        :group: combos-os

        .. tab:: macOS

            A second set, also for macOS.

        .. tab:: Windows

            A second set, also for Windows.

Keys match tabs with different titles:

.. tabs::
    :group: combos-lang

    .. tab:: Python
        :key: py

        ``pip install kaamiki-sphinx-theme``

    .. tab:: JavaScript
        :key: js

        ``npm install kaamiki``

.. tabs::
    :group: combos-lang

    .. tab:: The Python way
        :key: py

        Written in Python.

    .. tab:: The JavaScript way
        :key: js

        Written in JavaScript.

.. code-block:: rst

    .. tabs::
        :group: combos-lang

        .. tab:: Python
            :key: py

            ``pip install kaamiki-sphinx-theme``

        .. tab:: JavaScript
            :key: js

            ``npm install kaamiki``

    .. tabs::
        :group: combos-lang

        .. tab:: The Python way
            :key: py

            Written in Python.

        .. tab:: The JavaScript way
            :key: js

            Written in JavaScript.

.. _combos-tabs-the-options-of-tab-one-at-a-time:

-------------------------------------------------------------------------------
The options of tab, one at a time.
-------------------------------------------------------------------------------

``:selected:`` starts on the second tab.

.. tabs::

    .. tab:: First

        Content of First.

    .. tab:: Second
        :selected:

        Content of Second.

.. code-block:: rst

    .. tabs::

        .. tab:: First

            Content of First.

        .. tab:: Second
            :selected:

            Content of Second.

``:fa-icon:`` and ``:icon-position:``.

.. tabs::

    .. tab:: Before
        :fa-icon: fa-regular fa-code

        Content of Before.

    .. tab:: After
        :fa-icon: fa-regular fa-comments
        :icon-position: after

        Content of After.

.. code-block:: rst

    .. tabs::

        .. tab:: Before
            :fa-icon: fa-regular fa-code

            Content of Before.

        .. tab:: After
            :fa-icon: fa-regular fa-comments
            :icon-position: after

            Content of After.

``:class-title:`` and ``:class-body:``.

.. tabs::

    .. tab:: Title classes
        :class-title: km-tone-red

        Content of Title classes.

    .. tab:: Body classes
        :class-body: km-tone-green
        :selected:

        Content of Body classes.

.. code-block:: rst

    .. tabs::

        .. tab:: Title classes
            :class-title: km-tone-red

            Content of Title classes.

        .. tab:: Body classes
            :class-body: km-tone-green
            :selected:

            Content of Body classes.

``:class:`` on a tab's title and its content.

.. tabs::

    .. tab:: Both
        :class: km-tone-blue

        Content of Both.

    .. tab:: Neither

        Content of Neither.

.. code-block:: rst

    .. tabs::

        .. tab:: Both
            :class: km-tone-blue

            Content of Both.

        .. tab:: Neither

            Content of Neither.

.. _combos-tabs-with-icons:

-------------------------------------------------------------------------------
With icons.
-------------------------------------------------------------------------------

A tab's icon takes any style, a brand, a colour, a motion and either side:

Six tabs, six icons.

.. tabs::

    .. tab:: Regular
        :fa-icon: fa-regular fa-star

        Content of Regular.

    .. tab:: Solid
        :fa-icon: fa-solid fa-star

        Content of Solid.

    .. tab:: Brand
        :fa-icon: fa-brands fa-github

        Content of Brand.

    .. tab:: Duotone
        :fa-icon: fa-duotone fa-star

        Content of Duotone.

    .. tab:: After
        :fa-icon: fa-regular fa-star
        :icon-position: after

        Content of After.

    .. tab:: Moving
        :fa-icon: fa-solid fa-heart fa-beat

        Content of Moving.

.. code-block:: rst

    .. tabs::

        .. tab:: Regular
            :fa-icon: fa-regular fa-star

            Content of Regular.

        .. tab:: Solid
            :fa-icon: fa-solid fa-star

            Content of Solid.

        .. tab:: Brand
            :fa-icon: fa-brands fa-github

            Content of Brand.

        .. tab:: Duotone
            :fa-icon: fa-duotone fa-star

            Content of Duotone.

        .. tab:: After
            :fa-icon: fa-regular fa-star
            :icon-position: after

            Content of After.

        .. tab:: Moving
            :fa-icon: fa-solid fa-heart fa-beat

            Content of Moving.

The role in the title, in three places.

.. tabs::

    .. tab:: :fa-icon:regular:`star` Role first

        Content of :fa-icon:regular:`star` Role first.

    .. tab:: Role last :fa-icon:regular:`star`

        Content of Role last :fa-icon:regular:`star`.

    .. tab:: A :fa-icon:regular:`star` role inside

        Content of A :fa-icon:regular:`star` role inside.

.. code-block:: rst

    .. tabs::

        .. tab:: :fa-icon:regular:`star` Role first

            Content of :fa-icon:regular:`star` Role first.

        .. tab:: Role last :fa-icon:regular:`star`

            Content of Role last :fa-icon:regular:`star`.

        .. tab:: A :fa-icon:regular:`star` role inside

            Content of A :fa-icon:regular:`star` role inside.

The option and the role together.

.. tabs::

    .. tab:: Icon and role
        :fa-icon: fa-regular fa-star
        :selected:

        Content of Icon and role.

    .. tab:: Both :fa-icon:regular:`heart`
        :fa-icon: fa-regular fa-code
        :icon-position: after

        Content of Both :fa-icon:regular:`heart`.

.. code-block:: rst

    .. tabs::

        .. tab:: Icon and role
            :fa-icon: fa-regular fa-star
            :selected:

            Content of Icon and role.

        .. tab:: Both :fa-icon:regular:`heart`
            :fa-icon: fa-regular fa-code
            :icon-position: after

            Content of Both :fa-icon:regular:`heart`.

.. _combos-tabs-with-roles:

-------------------------------------------------------------------------------
With roles.
-------------------------------------------------------------------------------

Roles work in the titles and in the content, but ``email`` and ``swap`` are
left out of the titles: a link would fight the click that switches the tab and
a moving word would move the row of titles. They work in the content:

.. tabs::

    .. tab:: Title :sharpie:`highlighted`

        Content Title :sharpie:`highlighted`

    .. tab:: Plain

        Content Plain

.. code-block:: rst

    .. tabs::

        .. tab:: Title :sharpie:`highlighted`

            Content Title :sharpie:`highlighted`

        .. tab:: Plain

            Content Plain

.. tabs::

    .. tab:: Title :underline:`underlined`

        Content Title :underline:`underlined`

    .. tab:: Plain

        Content Plain

.. code-block:: rst

    .. tabs::

        .. tab:: Title :underline:`underlined`

            Content Title :underline:`underlined`

        .. tab:: Plain

            Content Plain

.. tabs::

    .. tab:: Title :ticker:`2025?short`

        Content Title :ticker:`2025?short`

    .. tab:: Plain

        Content Plain

.. code-block:: rst

    .. tabs::

        .. tab:: Title :ticker:`2025?short`

            Content Title :ticker:`2025?short`

        .. tab:: Plain

            Content Plain

.. tabs::

    .. tab:: Title

        Content :swap:`this|that|the other`

    .. tab:: Plain

        Content :swap:`this|that|the other`

.. code-block:: rst

    .. tabs::

        .. tab:: Title

            Content :swap:`this|that|the other`

        .. tab:: Plain

            Content :swap:`this|that|the other`

.. tabs::

    .. tab:: Title :kbd:mac:`Cmd-K`

        Content Title :kbd:mac:`Cmd-K`

    .. tab:: Plain

        Content Plain

.. code-block:: rst

    .. tabs::

        .. tab:: Title :kbd:mac:`Cmd-K`

            Content Title :kbd:mac:`Cmd-K`

        .. tab:: Plain

            Content Plain

.. tabs::

    .. tab:: Title :fa-icon:solid:`heart km-tone--red`

        Content Title :fa-icon:solid:`heart km-tone--red`

    .. tab:: Plain

        Content Plain

.. code-block:: rst

    .. tabs::

        .. tab:: Title :fa-icon:solid:`heart km-tone--red`

            Content Title :fa-icon:solid:`heart km-tone--red`

        .. tab:: Plain

            Content Plain

.. tabs::

    .. tab:: Title

        Content :email:`me <xa@mes3.dev>`

    .. tab:: Plain

        Content :email:`me <xa@mes3.dev>`

.. code-block:: rst

    .. tabs::

        .. tab:: Title

            Content :email:`me <xa@mes3.dev>`

        .. tab:: Plain

            Content :email:`me <xa@mes3.dev>`

.. _combos-tabs-holding-every-other-directive:

-------------------------------------------------------------------------------
Holding every other directive.
-------------------------------------------------------------------------------

A tab takes every directive but byline, code-explain, code-version, release and
tabs. The first three belong to the page itself and a release belongs in a
section, so they stop the build anywhere else. Tabs in a tab stop the build
too, as :ref:`combos-tabs-where-it-cant-go` shows. Each of the others is
written inside it below, with the source under the result.

accordion
^^^^^^^^^

.. tabs::

    .. tab:: Holds it
        :selected:

        .. accordion:: An accordion

            Folded away until it opens.

    .. tab:: Another tab

        Nothing in this one.

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

            .. accordion:: An accordion

                Folded away until it opens.

        .. tab:: Another tab

            Nothing in this one.

block
^^^^^

.. tabs::

    .. tab:: Holds it
        :selected:

        .. block:: A block
            :size: large
            :preheader: :fa-icon:regular:`star` Preheader

            The block's body.

    .. tab:: Another tab

        Nothing in this one.

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

            .. block:: A block
                :size: large
                :preheader: :fa-icon:regular:`star` Preheader

                The block's body.

        .. tab:: Another tab

            Nothing in this one.

button
^^^^^^

.. tabs::

    .. tab:: Holds it
        :selected:

        .. button:: https://github.com/xames3/website
            :fa-icon: heart

            A button

    .. tab:: Another tab

        Nothing in this one.

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

            .. button:: https://github.com/xames3/website
                :fa-icon: heart

                A button

        .. tab:: Another tab

            Nothing in this one.

columns
^^^^^^^

.. tabs::

    .. tab:: Holds it
        :selected:

        .. columns:: 2
            :gap: medium
            :valign: top

            .. column::

                The first column.

            .. column::

                The second column.

    .. tab:: Another tab

        Nothing in this one.

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

            .. columns:: 2
                :gap: medium
                :valign: top

                .. column::

                    The first column.

                .. column::

                    The second column.

        .. tab:: Another tab

            Nothing in this one.

embed
^^^^^

.. tabs::

    .. tab:: Holds it
        :selected:

        .. embed:: iframe

            <p style="padding: 1rem; background: seagreen">
                A block of HTML.
            </p>

    .. tab:: Another tab

        Nothing in this one.

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

            .. embed:: iframe

                <p style="padding: 1rem; background: seagreen">
                    A block of HTML.
                </p>

        .. tab:: Another tab

            Nothing in this one.

repository
^^^^^^^^^^

.. tabs::

    .. tab:: Holds it
        :selected:

        .. repository:: xames3/slowtorch

    .. tab:: Another tab

        Nothing in this one.

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

            .. repository:: xames3/slowtorch

        .. tab:: Another tab

            Nothing in this one.

thumbnail
^^^^^^^^^

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

video
^^^^^

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

youtube
^^^^^^^

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

.. _combos-tabs-inside-every-other-container:

-------------------------------------------------------------------------------
Inside every other container.
-------------------------------------------------------------------------------

A tab set goes anywhere a paragraph does, but not in a tab or a table. Here it
sits in each container that takes it, with the source under the result.

In an accordion
^^^^^^^^^^^^^^^

.. accordion:: An accordion that holds it
    :open:

    .. tabs::

        .. tab:: Held

            Tab content.

        .. tab:: By

            Tab content.

        .. tab:: A container

            Tab content.

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. tabs::

            .. tab:: Held

                Tab content.

            .. tab:: By

                Tab content.

            .. tab:: A container

                Tab content.

In a column
^^^^^^^^^^^

.. columns:: 2
    :gap: medium
    :valign: top

    .. column::

        .. tabs::

            .. tab:: Held

                Tab content.

            .. tab:: By

                Tab content.

            .. tab:: A container

                Tab content.

    .. column::

        Another column.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top

        .. column::

            .. tabs::

                .. tab:: Held

                    Tab content.

                .. tab:: By

                    Tab content.

                .. tab:: A container

                    Tab content.

        .. column::

            Another column.

In a block
^^^^^^^^^^

.. block:: A block that holds it
    :size: large

    .. tabs::

        .. tab:: Held

            Tab content.

        .. tab:: By

            Tab content.

        .. tab:: A container

            Tab content.

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. tabs::

            .. tab:: Held

                Tab content.

            .. tab:: By

                Tab content.

            .. tab:: A container

                Tab content.

In a note
^^^^^^^^^

.. note::

    .. tabs::

        .. tab:: Held

            Tab content.

        .. tab:: By

            Tab content.

        .. tab:: A container

            Tab content.

.. code-block:: rst

    .. note::

        .. tabs::

            .. tab:: Held

                Tab content.

            .. tab:: By

                Tab content.

            .. tab:: A container

                Tab content.

In a list item
^^^^^^^^^^^^^^

- A list item that holds it:

  .. tabs::

      .. tab:: Held

          Tab content.

      .. tab:: By

          Tab content.

      .. tab:: A container

          Tab content.

.. code-block:: rst

    - A list item that holds it:

      .. tabs::

          .. tab:: Held

              Tab content.

          .. tab:: By

              Tab content.

          .. tab:: A container

              Tab content.

.. _combos-tabs-where-it-cant-go:

-------------------------------------------------------------------------------
Where it can't go.
-------------------------------------------------------------------------------

Tabs can't go in a tab, because a row of titles in a row of titles is hard to
use. They can't go in a table either, because a table cell doesn't wrap the row
of titles, so the table gets wider than the page. The message is written under
the source:

In a tab
^^^^^^^^

.. code-block:: rst

    .. tabs::

        .. tab:: Outer one

            .. tabs::

                .. tab:: Inner one

                    One.

                .. tab:: Inner two

                    Two.

        .. tab:: Outer two

            The second outer tab.

.. code-block:: text

    tabs: expected outside a code-explain, a code-version, a block that links,
    a tab and a table, got it in a tab

In a table
^^^^^^^^^^

.. code-block:: rst

    .. list-table::

        * - .. tabs::

                .. tab:: One

                    One.

                .. tab:: Two

                    Two.

          - Another cell.

.. code-block:: text

    tabs: expected outside a code-explain, a code-version, a block that links,
    a tab and a table, got it in a table

.. _combos-tabs-what-a-title-cant-hold:

-------------------------------------------------------------------------------
What a title can't hold.
-------------------------------------------------------------------------------

A title is what you click to show the tab, so a link in it stops the build, and
so does ``:swap:``, which would move the row of titles. A tab's
``:icon-position:`` needs its ``:fa-icon:``. The message is written under the
source:

An email in a title
^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. tabs::

        .. tab:: Mail :email:`me <xa@mes3.dev>`

            One.

        .. tab:: Two

            Two.

.. code-block:: text

    tab: expected a title without a link, got one

A swapping word in a title
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. tabs::

        .. tab:: :swap:`this|that`

            One.

        .. tab:: Two

            Two.

.. code-block:: text

    tab: expected a title that stays put, got :swap:, which moves the tabs

An icon position without an icon
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. tabs::

        .. tab:: One
            :icon-position: after

            One.

        .. tab:: Two

            Two.

.. code-block:: text

    tab: :icon-position: needs :fa-icon:

Two tabs with one title
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. tabs::

        .. tab:: Same

            One.

        .. tab:: Same

            Two.

.. code-block:: text

    tabs: expected each key once, got 'same' more than once
