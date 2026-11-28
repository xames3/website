.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 October 2026
.. Last updated on: 28 November 2026

:km-page-title: Bylines, option by option
:km-page-description: Every option of the byline directive, with icons and
    roles and where it can't go. A page takes one byline, so one is live.
:km-page-type: article
:km-header-subheader: Every way to say who wrote it
:km-feedback-title: Did I miss a way to combine them?
:km-feedback-description: Tell me what you tried with a byline that didn't
    work.
:km-feedback-button: Tell me
:km-feedback-icon: fa-user

.. _combos-byline:

===============================================================================
:fa-icon:duotone:`user` Bylines, option by option
===============================================================================

.. rst-class:: km-text-lead

    Who wrote it, in every combination.

A byline shows the author, how long the page takes to read, a button that
copies its link and a way to see its source, and it can name the language it's
written in. A page can hold only one, so the one under this page's title is
live and the rest of the combinations are written out with what each changes.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3
    :avatar-size: 32
    :align: center
    :shade: purple

The byline above is live. It was written with ``:avatar-size: 32`` and
``:align: center``, which are the two options that change what you see most.
The rest of this page is written out, since a page may hold only one.

.. _combos-byline-the-options-one-at-a-time:

-------------------------------------------------------------------------------
The options, one at a time.
-------------------------------------------------------------------------------

.. list-table::
    :header-rows: 1
    :widths: 28 72

    * - Option
      - What it changes
    * - (none)
      - The name, the picture the site gives, how long the page takes
        to read, the copy button and the link to the source.
    * - ``:avatar:``
      - The author's picture. Without it the byline uses the one in
        ``kaamiki.conf.site.project``.
    * - ``:target:``
      - Where the name links to, a profile or a ``mailto:`` link.
    * - ``:avatar-size:``
      - The picture's width and height from 16 to 64 pixels. 20
        without it.
    * - ``:align: left``
      - The author, the reading time, the language (when shown) and the copy
        button sit in one row on the left. It's what you get without it.
    * - ``:align: center``
      - The byline is centred and takes two rows.
    * - ``:align: right``
      - It sits on the right.
    * - ``:hide-reading-time:``
      - Leaves out how long the page takes to read.
    * - ``:hide-copy-url:``
      - Leaves out the copy link button.
    * - ``:hide-source:``
      - Leaves out the link to the page's source.
    * - ``:show-language:``
      - Adds the page's language, which is ``:km-page-language:`` or, without
        it, the site's ``language``.
    * - All three ``:hide-*:``
      - Leaves only the name and the picture.
    * - ``:shade:``
      - The colour of the banner on the cards. Blue without it.
    * - ``:swirl:``
      - The shape of the swirl, ``1`` to ``4``. Without it, the name of the
        page picks one.
    * - ``:fa-icon:``
      - The icon in the banner. The title's icon without it, else none.
    * - ``:banner:``
      - A picture of yours in place of the swirl, an address or a file in
        your docs.
    * - ``:class:``
      - Extra classes.

Each one, written out:

(none)

.. code-block:: rst

    .. byline:: @xames3

``:avatar:``

.. code-block:: rst

    .. byline:: @xames3
        :avatar: https://avatars.githubusercontent.com/u/90549089?v=4

``:target:``

.. code-block:: rst

    .. byline:: @xames3
        :target: mailto:xa@mes3.dev

``:avatar-size:``

.. code-block:: rst

    .. byline:: @xames3
        :avatar-size: 48

``:align: left``

.. code-block:: rst

    .. byline:: @xames3
        :align: left

``:align: center``

.. code-block:: rst

    .. byline:: @xames3
        :align: center

``:align: right``

.. code-block:: rst

    .. byline:: @xames3
        :align: right

``:hide-reading-time:``

.. code-block:: rst

    .. byline:: @xames3
        :hide-reading-time:

``:hide-copy-url:``

.. code-block:: rst

    .. byline:: @xames3
        :hide-copy-url:

``:hide-source:``

.. code-block:: rst

    .. byline:: @xames3
        :hide-source:

``:show-language:``

.. code-block:: rst

    .. byline:: @xames3
        :show-language:

All three ``:hide-*:``

.. code-block:: rst

    .. byline:: @xames3
        :hide-reading-time:
        :hide-copy-url:
        :hide-source:

``:shade:``

.. code-block:: rst

    .. byline:: @xames3
        :shade: green

``:swirl:``

.. code-block:: rst

    .. byline:: @xames3
        :swirl: 3

``:fa-icon:``

.. code-block:: rst

    .. byline:: @xames3
        :fa-icon: fa-regular fa-compass

``:banner:``

.. code-block:: rst

    .. byline:: @xames3
        :banner: https://i.imgur.com/RLsdjyG.jpeg

``:class:``

.. code-block:: rst

    .. byline:: @xames3
        :class: km-tone-blue

.. _combos-byline-with-icons-and-roles:

-------------------------------------------------------------------------------
With icons and roles.
-------------------------------------------------------------------------------

A byline's text is the author's handle, so icons and roles go around it, in the
paragraphs beside it:

The author, :fa-icon:regular:`user` @xames3, writes
:roll:`slowly|clearly|often`.

.. code-block:: rst

    The author, :fa-icon:regular:`user` @xames3, writes
    :roll:`slowly|clearly|often`.

A byline and a line of roles under it.

.. code-block:: rst

    .. byline:: @xames3
        :avatar-size: 24

    Written by :fa-icon:regular:`pen` :sharpie:`xames3`, who
    takes :ticker:`6?short` minutes to read.

.. _combos-byline-where-it-cant-go:

-------------------------------------------------------------------------------
Where it can't go.
-------------------------------------------------------------------------------

A byline belongs to the page itself, so in each of these the build stops. The
message is written under the source:

In an accordion
^^^^^^^^^^^^^^^

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. byline:: @xames3
            :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
            :target: https://github.com/xames3

.. code-block:: text

    byline: expected on the page itself, got it in an accordion

In a tab
^^^^^^^^

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

            .. byline:: @xames3
                :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
                :target: https://github.com/xames3

        .. tab:: Another tab

            Nothing in this one.

.. code-block:: text

    byline: expected on the page itself, got it in a tab

In a column
^^^^^^^^^^^

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top

        .. column::

            .. byline:: @xames3
                :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
                :target: https://github.com/xames3

        .. column::

            Another column.

.. code-block:: text

    byline: expected on the page itself, got it in a column

In a block
^^^^^^^^^^

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. byline:: @xames3
            :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
            :target: https://github.com/xames3

.. code-block:: text

    byline: expected on the page itself, got it in a block

In a note
^^^^^^^^^

.. code-block:: rst

    .. note::

        .. byline:: @xames3
            :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
            :target: https://github.com/xames3

.. code-block:: text

    byline: expected on the page itself, got it in a note

In a list item
^^^^^^^^^^^^^^

.. code-block:: rst

    - A list item that holds it:

      .. byline:: @xames3
          :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
          :target: https://github.com/xames3

.. code-block:: text

    byline: expected on the page itself, got it in a list

In a container
^^^^^^^^^^^^^^

.. code-block:: rst

    .. container:: wide

        .. byline:: @xames3
            :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
            :target: https://github.com/xames3

.. code-block:: text

    byline: expected on the page itself, got it in a container

.. _combos-byline-no-link-in-the-name:

-------------------------------------------------------------------------------
No link in the name.
-------------------------------------------------------------------------------

The name is the link to the author's profile, so a link in it stops the build.
The message is written under the source:

An email in the name
^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. byline:: Written by :email:`me <xa@mes3.dev>`

.. code-block:: text

    byline: expected a name without a link, got one

.. _combos-byline-only-one:

-------------------------------------------------------------------------------
Only one.
-------------------------------------------------------------------------------

A second byline on a page stops the build with the message ``byline: expected
once on a page``.
