.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 October 2026
.. Last updated on: 16 November 2026

:km-page-title: Blocks, everywhere
:km-page-description: Every option of the block directive on and off, with
    icons and roles, holding every other directive and inside every container.
:km-page-type: article
:km-header-subheader: Every way to make a card
:km-feedback-title: Did I miss a way to combine them?
:km-feedback-description: Tell me what you tried with a block that didn't work.
:km-feedback-button: Tell me
:km-feedback-icon: fa-rectangle-list

.. _combos-block:

===============================================================================
:fa-icon:regular:`rectangle-list` Blocks, everywhere
===============================================================================

.. rst-class:: km-text-lead

    Content in a card, in every combination.

A block is a card with a title and a body, and blocks written one after another
make a row. This page writes it with every option on and off, with icons and
roles, with every other Kaamiki directive inside it and inside every container,
so the markup and the result sit side by side.

.. _combos-block-the-options-one-at-a-time:

-------------------------------------------------------------------------------
The options, one at a time.
-------------------------------------------------------------------------------

No options.

.. block:: A block

    The block's body.

.. code-block:: rst

    .. block:: A block

        The block's body.

``:subheader:``

.. block:: With a subheader
    :subheader: A smaller line under the title

    The block's body.

.. code-block:: rst

    .. block:: With a subheader
        :subheader: A smaller line under the title

        The block's body.

``:preheader:``

.. block:: With a preheader
    :preheader: Above the title

    The block's body.

.. code-block:: rst

    .. block:: With a preheader
        :preheader: Above the title

        The block's body.

``:footer:``

.. block:: With a footer
    :footer: At the bottom

    The block's body.

.. code-block:: rst

    .. block:: With a footer
        :footer: At the bottom

        The block's body.

``:preheader:``, ``:subheader:`` and ``:footer:`` together.

.. block:: With both
    :preheader: Above
    :footer: Below
    :subheader: Under

    The block's body.

.. code-block:: rst

    .. block:: With both
        :preheader: Above
        :footer: Below
        :subheader: Under

        The block's body.

``:target:``, so the whole block is a link.

.. block:: A link to an address
    :target: https://github.com/xames3/website
    :preheader: :fa-icon:brands:`github` GitHub

    The block's body.

.. code-block:: rst

    .. block:: A link to an address
        :target: https://github.com/xames3/website
        :preheader: :fa-icon:brands:`github` GitHub

        The block's body.

``:doc:``, a document of this site.

.. block:: A link to a document
    :doc: ../roles
    :preheader: :fa-icon:regular:`pen-to-square` Roles

    The block's body.

.. code-block:: rst

    .. block:: A link to a document
        :doc: ../roles
        :preheader: :fa-icon:regular:`pen-to-square` Roles

        The block's body.

``:ref:``, a label.

.. block:: A link to a label
    :ref: kaamiki-roles-fa-icon
    :preheader: :fa-icon:regular:`icons` The fa-icon role

    The block's body.

.. code-block:: rst

    .. block:: A link to a label
        :ref: kaamiki-roles-fa-icon
        :preheader: :fa-icon:regular:`icons` The fa-icon role

        The block's body.

``:class:``

.. block:: Extra classes
    :class: km-tone-blue

    The block's body.

.. code-block:: rst

    .. block:: Extra classes
        :class: km-tone-blue

        The block's body.

.. _combos-block-sizes-and-blocks-in-rows:

-------------------------------------------------------------------------------
Sizes and blocks in rows.
-------------------------------------------------------------------------------

``:size:`` says how many fit in a row. ``large`` is the default and fills it,
``medium`` fits two and ``small`` fits three:

Two ``large`` blocks, one per row.

.. block:: Large

    The block's body.

.. block:: Another large

    The block's body.

.. code-block:: rst

    .. block:: Large

        The block's body.

    .. block:: Another large

        The block's body.

Four ``medium`` blocks, two a row.

.. block:: Medium 1
    :size: medium

    The block's body.

.. block:: Medium 2
    :size: medium

    The block's body.

.. block:: Medium 3
    :size: medium

    The block's body.

.. block:: Medium 4
    :size: medium

    The block's body.

.. code-block:: rst

    .. block:: Medium 1
        :size: medium

        The block's body.

    .. block:: Medium 2
        :size: medium

        The block's body.

    .. block:: Medium 3
        :size: medium

        The block's body.

    .. block:: Medium 4
        :size: medium

        The block's body.

Six ``small`` blocks, three a row.

.. block:: Small 1
    :size: small

    The block's body.

.. block:: Small 2
    :size: small

    The block's body.

.. block:: Small 3
    :size: small

    The block's body.

.. block:: Small 4
    :size: small

    The block's body.

.. block:: Small 5
    :size: small

    The block's body.

.. block:: Small 6
    :size: small

    The block's body.

.. code-block:: rst

    .. block:: Small 1
        :size: small

        The block's body.

    .. block:: Small 2
        :size: small

        The block's body.

    .. block:: Small 3
        :size: small

        The block's body.

    .. block:: Small 4
        :size: small

        The block's body.

    .. block:: Small 5
        :size: small

        The block's body.

    .. block:: Small 6
        :size: small

        The block's body.

A block of another size starts a new row.

.. block:: Small
    :size: small

    The block's body.

.. block:: Small
    :size: small

    The block's body.

.. block:: Medium
    :size: medium

    The block's body.

.. block:: Large

    The block's body.

.. code-block:: rst

    .. block:: Small
        :size: small

        The block's body.

    .. block:: Small
        :size: small

        The block's body.

    .. block:: Medium
        :size: medium

        The block's body.

    .. block:: Large

        The block's body.

So does a paragraph.

.. block:: One
    :size: medium

    The block's body.

A paragraph between two blocks starts a new row.

.. block:: Two
    :size: medium

    The block's body.

.. code-block:: rst

    .. block:: One
        :size: medium

        The block's body.

    A paragraph between two blocks starts a new row.

    .. block:: Two
        :size: medium

        The block's body.

.. _combos-block-with-icons:

-------------------------------------------------------------------------------
With icons.
-------------------------------------------------------------------------------

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        Icon first in the preheader

        .. block:: Preheader
            :preheader: :fa-icon:regular:`star` Icon first

            The block's body.

        .. code-block:: rst

            .. block:: Preheader
                :preheader: :fa-icon:regular:`star` Icon first

                The block's body.

    .. column::

        Icon last in the preheader

        .. block:: Preheader
            :preheader: Icon last :fa-icon:regular:`star`

            The block's body.

        .. code-block:: rst

            .. block:: Preheader
                :preheader: Icon last :fa-icon:regular:`star`

                The block's body.

    .. column::

        Icon inside the preheader

        .. block:: Preheader
            :preheader: An :fa-icon:regular:`star` icon inside

            The block's body.

        .. code-block:: rst

            .. block:: Preheader
                :preheader: An :fa-icon:regular:`star` icon inside

                The block's body.

    .. column::

        Icon in the footer

        .. block:: Footer
            :footer: Icon last :fa-icon:regular:`arrow-right`

            The block's body.

        .. code-block:: rst

            .. block:: Footer
                :footer: Icon last :fa-icon:regular:`arrow-right`

                The block's body.

    .. column::

        Icons in both

        .. block:: Both
            :preheader: :fa-icon:regular:`star` Preheader
            :footer: Footer :fa-icon:regular:`heart`

            The block's body.

        .. code-block:: rst

            .. block:: Both
                :preheader: :fa-icon:regular:`star` Preheader
                :footer: Footer :fa-icon:regular:`heart`

                The block's body.

    .. column::

        Icon in the title

        .. block:: :fa-icon:regular:`star` In the title

            The block's body.

        .. code-block:: rst

            .. block:: :fa-icon:regular:`star` In the title

                The block's body.

    .. column::

        Icon in the subheader

        .. block:: Subheader
            :subheader: With an icon :fa-icon:regular:`star`

            The block's body.

        .. code-block:: rst

            .. block:: Subheader
                :subheader: With an icon :fa-icon:regular:`star`

                The block's body.

    .. column::

        A coloured icon

        .. block:: Coloured
            :preheader: :fa-icon:solid:`heart km-tone--red` Red

            The block's body.

        .. code-block:: rst

            .. block:: Coloured
                :preheader: :fa-icon:solid:`heart km-tone--red` Red

                The block's body.

    .. column::

        A brand icon

        .. block:: Brand
            :preheader: :fa-icon:brands:`github` GitHub

            The block's body.

        .. code-block:: rst

            .. block:: Brand
                :preheader: :fa-icon:brands:`github` GitHub

                The block's body.

    .. column::

        Icons in the body

        .. block:: Body

            :fa-icon:regular:`star` At the start

            In the :fa-icon:regular:`heart` middle

            At the end :fa-icon:regular:`bell`

        .. code-block:: rst

            .. block:: Body

                :fa-icon:regular:`star` At the start

                In the :fa-icon:regular:`heart` middle

                At the end :fa-icon:regular:`bell`

.. _combos-block-with-roles:

-------------------------------------------------------------------------------
With roles.
-------------------------------------------------------------------------------

.. block:: Title :sharpie:`highlighted`
    :preheader: Preheader :sharpie:`highlighted`
    :footer: Footer :sharpie:`highlighted`
    :subheader: Sub :sharpie:`highlighted`

    Body :sharpie:`highlighted`

.. code-block:: rst

    .. block:: Title :sharpie:`highlighted`
        :preheader: Preheader :sharpie:`highlighted`
        :footer: Footer :sharpie:`highlighted`
        :subheader: Sub :sharpie:`highlighted`

        Body :sharpie:`highlighted`

.. block:: Title :underline:`underlined`
    :preheader: Preheader :underline:`underlined`
    :footer: Footer :underline:`underlined`
    :subheader: Sub :underline:`underlined`

    Body :underline:`underlined`

.. code-block:: rst

    .. block:: Title :underline:`underlined`
        :preheader: Preheader :underline:`underlined`
        :footer: Footer :underline:`underlined`
        :subheader: Sub :underline:`underlined`

        Body :underline:`underlined`

.. block:: Title :ticker:`2025?short`
    :preheader: Preheader :ticker:`2025?short`
    :footer: Footer :ticker:`2025?short`
    :subheader: Sub :ticker:`2025?short`

    Body :ticker:`2025?short`

.. code-block:: rst

    .. block:: Title :ticker:`2025?short`
        :preheader: Preheader :ticker:`2025?short`
        :footer: Footer :ticker:`2025?short`
        :subheader: Sub :ticker:`2025?short`

        Body :ticker:`2025?short`

.. block:: Title :swap:`this|that|the other`
    :preheader: Preheader :swap:`this|that|the other`
    :footer: Footer :swap:`this|that|the other`
    :subheader: Sub :swap:`this|that|the other`

    Body :swap:`this|that|the other`

.. code-block:: rst

    .. block:: Title :swap:`this|that|the other`
        :preheader: Preheader :swap:`this|that|the other`
        :footer: Footer :swap:`this|that|the other`
        :subheader: Sub :swap:`this|that|the other`

        Body :swap:`this|that|the other`

.. block:: Title :kbd:mac:`Cmd-K`
    :preheader: Preheader :kbd:mac:`Cmd-K`
    :footer: Footer :kbd:mac:`Cmd-K`
    :subheader: Sub :kbd:mac:`Cmd-K`

    Body :kbd:mac:`Cmd-K`

.. code-block:: rst

    .. block:: Title :kbd:mac:`Cmd-K`
        :preheader: Preheader :kbd:mac:`Cmd-K`
        :footer: Footer :kbd:mac:`Cmd-K`
        :subheader: Sub :kbd:mac:`Cmd-K`

        Body :kbd:mac:`Cmd-K`

.. block:: Title :email:`me <xa@mes3.dev>`
    :preheader: Preheader :email:`me <xa@mes3.dev>`
    :footer: Footer :email:`me <xa@mes3.dev>`
    :subheader: Sub :email:`me <xa@mes3.dev>`

    Body :email:`me <xa@mes3.dev>`

.. code-block:: rst

    .. block:: Title :email:`me <xa@mes3.dev>`
        :preheader: Preheader :email:`me <xa@mes3.dev>`
        :footer: Footer :email:`me <xa@mes3.dev>`
        :subheader: Sub :email:`me <xa@mes3.dev>`

        Body :email:`me <xa@mes3.dev>`

.. block:: Title :fa-icon:solid:`heart km-tone--red`
    :preheader: Preheader :fa-icon:solid:`heart km-tone--red`
    :footer: Footer :fa-icon:solid:`heart km-tone--red`
    :subheader: Sub :fa-icon:solid:`heart km-tone--red`

    Body :fa-icon:solid:`heart km-tone--red`

.. code-block:: rst

    .. block:: Title :fa-icon:solid:`heart km-tone--red`
        :preheader: Preheader :fa-icon:solid:`heart km-tone--red`
        :footer: Footer :fa-icon:solid:`heart km-tone--red`
        :subheader: Sub :fa-icon:solid:`heart km-tone--red`

        Body :fa-icon:solid:`heart km-tone--red`

.. _combos-block-holding-every-other-directive:

-------------------------------------------------------------------------------
Holding every other directive.
-------------------------------------------------------------------------------

A block takes every directive but byline, code-explain, code-version and
release. The first three belong to the page itself and a release belongs in a
section, so they stop the build anywhere else. Each of the others is written
inside it below, with the source under the result.

accordion
^^^^^^^^^

.. block:: A block that holds it
    :size: large

    .. accordion:: An accordion

        Folded away until it opens.

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. accordion:: An accordion

            Folded away until it opens.

button
^^^^^^

.. block:: A block that holds it
    :size: large

    .. button:: https://github.com/xames3/website
        :fa-icon: heart

        A button

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. button:: https://github.com/xames3/website
            :fa-icon: heart

            A button

columns
^^^^^^^

.. block:: A block that holds it
    :size: large

    .. columns:: 2
        :gap: medium
        :valign: top

        .. column::

            The first column.

        .. column::

            The second column.

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. columns:: 2
            :gap: medium
            :valign: top

            .. column::

                The first column.

            .. column::

                The second column.

embed
^^^^^

.. block:: A block that holds it
    :size: large

    .. embed:: iframe

        <p style="padding: 1rem; background: seagreen">
            A block of HTML.
        </p>

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. embed:: iframe

            <p style="padding: 1rem; background: seagreen">
                A block of HTML.
            </p>

repository
^^^^^^^^^^

.. block:: A block that holds it
    :size: large

    .. repository:: xames3/slowtorch

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. repository:: xames3/slowtorch

tabs
^^^^

.. block:: A block that holds it
    :size: large

    .. tabs::

        .. tab:: First
            :fa-icon: fa-regular fa-code

            The first tab.

        .. tab:: Second

            The second tab.

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. tabs::

            .. tab:: First
                :fa-icon: fa-regular fa-code

                The first tab.

            .. tab:: Second

                The second tab.

thumbnail
^^^^^^^^^

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

video
^^^^^

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

youtube
^^^^^^^

.. block:: A block that holds it
    :size: large

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :caption: A video.

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. youtube:: https://youtu.be/kCc8FmEb1nY
            :caption: A video.

.. _combos-block-inside-every-other-container:

-------------------------------------------------------------------------------
Inside every other container.
-------------------------------------------------------------------------------

A block goes anywhere a paragraph does. Here it sits in each container, with
the source under the result.

In an accordion
^^^^^^^^^^^^^^^

.. accordion:: An accordion that holds it
    :open:

    .. block:: The block

        The block's body.

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. block:: The block

            The block's body.

In a tab
^^^^^^^^

.. tabs::

    .. tab:: Holds it
        :selected:

        .. block:: The block

            The block's body.

    .. tab:: Another tab

        Nothing in this one.

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

            .. block:: The block

                The block's body.

        .. tab:: Another tab

            Nothing in this one.

In a column
^^^^^^^^^^^

Blocks in a column aren't put in rows. They sit one under the other, each as
wide as the column.

.. columns:: 2
    :gap: medium
    :valign: top

    .. column::

        .. block:: The block

            The block's body.

    .. column::

        Another column.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top

        .. column::

            .. block:: The block

                The block's body.

        .. column::

            Another column.

In a note
^^^^^^^^^

.. note::

    .. block:: The block

        The block's body.

.. code-block:: rst

    .. note::

        .. block:: The block

            The block's body.

In a list item
^^^^^^^^^^^^^^

- A list item that holds it:

  .. block:: The block

      The block's body.

.. code-block:: rst

    - A list item that holds it:

      .. block:: The block

          The block's body.

.. _combos-block-not-in-a-block:

-------------------------------------------------------------------------------
Not in a block.
-------------------------------------------------------------------------------

A card in a card draws no frame of its own, so a block in a block stops the
build. The message is written under the source:

A block in a block
^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. block:: The outer block

        .. block:: The inner block

            Inside.

.. code-block:: text

    block: expected outside a code-explain, a code-version and a block, got it
    in a block

.. _combos-block-no-link-in-a-block-that-links:

-------------------------------------------------------------------------------
No link in a block that links.
-------------------------------------------------------------------------------

A block with a ``:target:``, ``:doc:`` or ``:ref:`` is a link as a whole, so a
link in its preheader, title, subheader or footer stops the build. A block that
doesn't link takes them. The body of one that does takes a link too, but not an
accordion, tabs, a video, a youtube, an embed or a walkthrough. The message is
written under the source:

An email in the title
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. block:: Mail :email:`me <xa@mes3.dev>`
        :target: https://example.com

        The body.

.. code-block:: text

    block: expected a title without a link, got one

An email in the preheader
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. block:: A title
        :preheader: Mail :email:`me <xa@mes3.dev>`
        :target: https://example.com

        The body.

.. code-block:: text

    block: expected a preheader without a link, got one

An accordion in the body
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. block:: A title
        :target: https://example.com

        .. accordion:: An accordion

            Folded away until it opens.

.. code-block:: text

    accordion: expected outside a code-explain, a code-version and a block that
    links, got it in a block that links
