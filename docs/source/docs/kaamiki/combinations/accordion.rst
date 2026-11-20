.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 October 2026
.. Last updated on: 19 November 2026

:km-page-title: Accordions, everywhere
:km-page-description: Every option of the accordion directive on and off, with
    icons and roles, holding every other directive and inside every container.
:km-page-type: article
:km-header-subheader: Every way to fold content away
:km-feedback-title: Did I miss a way to combine them?
:km-feedback-description: Tell me what you tried with an accordion that didn't
    work.
:km-feedback-button: Tell me
:km-feedback-icon: fa-square-plus

.. _combos-accordion:

===============================================================================
:fa-icon:regular:`square-plus` Accordions, everywhere
===============================================================================

.. rst-class:: km-text-lead

    Content that folds away, in every combination.

An accordion folds content under a title. This page writes it with each option
on and off, with icons and roles in its title, with every other Kaamiki
directive inside it and inside every container, so the markup and the result
sit side by side.

.. _combos-accordion-the-options-one-at-a-time:

-------------------------------------------------------------------------------
The options, one at a time.
-------------------------------------------------------------------------------

Each accordion below is the default with one thing changed, so the difference
is the line that's shown.

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        No options.

        .. accordion:: A plain accordion

            Closed until it's clicked.

        .. code-block:: rst

            .. accordion:: A plain accordion

                Closed until it's clicked.

    .. column::

        ``:open:``

        .. accordion:: Starts open
            :open:

            Open before anyone clicks.

        .. code-block:: rst

            .. accordion:: Starts open
                :open:

                Open before anyone clicks.

    .. column::

        ``:preheader:``

        .. accordion:: With a preheader
            :preheader: A small line above the title

            The content.

        .. code-block:: rst

            .. accordion:: With a preheader
                :preheader: A small line above the title

                The content.

    .. column::

        ``:subheader:``

        .. accordion:: With a subheader
            :subheader: A dimmer line under the title

            The content.

        .. code-block:: rst

            .. accordion:: With a subheader
                :subheader: A dimmer line under the title

                The content.

    .. column::

        ``:subheader:`` and ``:nested-subheader:``

        .. accordion:: With a nested subheader
            :subheader: Shown once it's open
            :nested-subheader:
            :open:

            The content.

        .. code-block:: rst

            .. accordion:: With a nested subheader
                :subheader: Shown once it's open
                :nested-subheader:
                :open:

                The content.

    .. column::

        ``:class-preheader:``

        .. accordion:: A coloured preheader
            :preheader: In green
            :class-preheader: km-tone-green

            The content.

        .. code-block:: rst

            .. accordion:: A coloured preheader
                :preheader: In green
                :class-preheader: km-tone-green

                The content.

    .. column::

        ``:class-subheader:``

        .. accordion:: A coloured subheader
            :subheader: In green
            :class-subheader: km-tone-green

            The content.

        .. code-block:: rst

            .. accordion:: A coloured subheader
                :subheader: In green
                :class-subheader: km-tone-green

                The content.

    .. column::

        ``:class:``

        .. accordion:: Extra classes
            :class: km-tone-blue
            :open:

            The classes go on the whole accordion.

        .. code-block:: rst

            .. accordion:: Extra classes
                :class: km-tone-blue
                :open:

                The classes go on the whole accordion.

    .. column::

        ``:class-title:``

        .. accordion:: Extra title classes
            :class-title: km-tone-red

            Only the title is red.

        .. code-block:: rst

            .. accordion:: Extra title classes
                :class-title: km-tone-red

                Only the title is red.

    .. column::

        ``:class-body:``

        .. accordion:: Extra body classes
            :class-body: km-tone-green
            :open:

            Only the content is green.

        .. code-block:: rst

            .. accordion:: Extra body classes
                :class-body: km-tone-green
                :open:

                Only the content is green.

.. _combos-accordion-the-marker-in-every-position:

-------------------------------------------------------------------------------
The marker, in every position.
-------------------------------------------------------------------------------

``:marker:`` is ``plus``, ``down`` or ``right`` and ``:marker-position:`` is
``before`` or ``after`` the title. That's six accordions:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        ``:marker: plus`` and ``:marker-position: before``

        .. accordion:: Plus, before
            :marker: plus
            :marker-position: before

            The marker is before the title.

        .. code-block:: rst

            .. accordion:: Plus, before
                :marker: plus
                :marker-position: before

                The marker is before the title.

    .. column::

        ``:marker: plus`` and ``:marker-position: after``

        .. accordion:: Plus, after
            :marker: plus
            :marker-position: after

            The marker is after the title.

        .. code-block:: rst

            .. accordion:: Plus, after
                :marker: plus
                :marker-position: after

                The marker is after the title.

    .. column::

        ``:marker: down`` and ``:marker-position: before``

        .. accordion:: Down, before
            :marker: down
            :marker-position: before

            The marker is before the title.

        .. code-block:: rst

            .. accordion:: Down, before
                :marker: down
                :marker-position: before

                The marker is before the title.

    .. column::

        ``:marker: down`` and ``:marker-position: after``

        .. accordion:: Down, after
            :marker: down
            :marker-position: after

            The marker is after the title.

        .. code-block:: rst

            .. accordion:: Down, after
                :marker: down
                :marker-position: after

                The marker is after the title.

    .. column::

        ``:marker: right`` and ``:marker-position: before``

        .. accordion:: Right, before
            :marker: right
            :marker-position: before

            The marker is before the title.

        .. code-block:: rst

            .. accordion:: Right, before
                :marker: right
                :marker-position: before

                The marker is before the title.

    .. column::

        ``:marker: right`` and ``:marker-position: after``

        .. accordion:: Right, after
            :marker: right
            :marker-position: after

            The marker is after the title.

        .. code-block:: rst

            .. accordion:: Right, after
                :marker: right
                :marker-position: after

                The marker is after the title.

Open, the same six turn their marker:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        .. accordion:: Plus, before, open
            :marker: plus
            :marker-position: before
            :open:

            Open.

        .. code-block:: rst

            .. accordion:: Plus, before, open
                :marker: plus
                :marker-position: before
                :open:

                Open.

    .. column::

        .. accordion:: Plus, after, open
            :marker: plus
            :marker-position: after
            :open:

            Open.

        .. code-block:: rst

            .. accordion:: Plus, after, open
                :marker: plus
                :marker-position: after
                :open:

                Open.

    .. column::

        .. accordion:: Down, before, open
            :marker: down
            :marker-position: before
            :open:

            Open.

        .. code-block:: rst

            .. accordion:: Down, before, open
                :marker: down
                :marker-position: before
                :open:

                Open.

    .. column::

        .. accordion:: Down, after, open
            :marker: down
            :marker-position: after
            :open:

            Open.

        .. code-block:: rst

            .. accordion:: Down, after, open
                :marker: down
                :marker-position: after
                :open:

                Open.

    .. column::

        .. accordion:: Right, before, open
            :marker: right
            :marker-position: before
            :open:

            Open.

        .. code-block:: rst

            .. accordion:: Right, before, open
                :marker: right
                :marker-position: before
                :open:

                Open.

    .. column::

        .. accordion:: Right, after, open
            :marker: right
            :marker-position: after
            :open:

            Open.

        .. code-block:: rst

            .. accordion:: Right, after, open
                :marker: right
                :marker-position: after
                :open:

                Open.

.. _combos-accordion-groups-and-content-taller-than-the-screen:

-------------------------------------------------------------------------------
Groups and content taller than the screen.
-------------------------------------------------------------------------------

Accordions that share a ``:group:`` close each other. Only one of them may
start open:

.. accordion:: First of a group
    :group: combos-accordion-demo
    :open:

    Opening another one closes this.

.. accordion:: Second of a group
    :group: combos-accordion-demo

    Opening this closes the first.

.. accordion:: Third of a group
    :group: combos-accordion-demo

    The same goes for this one.

.. code-block:: rst

    .. accordion:: First of a group
        :group: combos-accordion-demo
        :open:

        Opening another one closes this.

    .. accordion:: Second of a group
        :group: combos-accordion-demo

        Opening this closes the first.

    .. accordion:: Third of a group
        :group: combos-accordion-demo

        The same goes for this one.

Content taller than the screen folds behind a Show more button.
``:hide-show-more:`` shows it in full:

.. accordion:: Folded when it's tall
    :open:

    - Line 1 of a long list, so the content is taller than the screen.
    - Line 2 of a long list, so the content is taller than the screen.
    - Line 3 of a long list, so the content is taller than the screen.
    - Line 4 of a long list, so the content is taller than the screen.
    - Line 5 of a long list, so the content is taller than the screen.
    - Line 6 of a long list, so the content is taller than the screen.
    - Line 7 of a long list, so the content is taller than the screen.
    - Line 8 of a long list, so the content is taller than the screen.
    - Line 9 of a long list, so the content is taller than the screen.
    - Line 10 of a long list, so the content is taller than the screen.
    - Line 11 of a long list, so the content is taller than the screen.
    - Line 12 of a long list, so the content is taller than the screen.
    - Line 13 of a long list, so the content is taller than the screen.
    - Line 14 of a long list, so the content is taller than the screen.
    - Line 15 of a long list, so the content is taller than the screen.
    - Line 16 of a long list, so the content is taller than the screen.
    - Line 17 of a long list, so the content is taller than the screen.
    - Line 18 of a long list, so the content is taller than the screen.
    - Line 19 of a long list, so the content is taller than the screen.
    - Line 20 of a long list, so the content is taller than the screen.
    - Line 21 of a long list, so the content is taller than the screen.
    - Line 22 of a long list, so the content is taller than the screen.
    - Line 23 of a long list, so the content is taller than the screen.
    - Line 24 of a long list, so the content is taller than the screen.
    - Line 25 of a long list, so the content is taller than the screen.
    - Line 26 of a long list, so the content is taller than the screen.
    - Line 27 of a long list, so the content is taller than the screen.
    - Line 28 of a long list, so the content is taller than the screen.
    - Line 29 of a long list, so the content is taller than the screen.
    - Line 30 of a long list, so the content is taller than the screen.
    - Line 31 of a long list, so the content is taller than the screen.
    - Line 32 of a long list, so the content is taller than the screen.
    - Line 33 of a long list, so the content is taller than the screen.
    - Line 34 of a long list, so the content is taller than the screen.
    - Line 35 of a long list, so the content is taller than the screen.

.. code-block:: rst

    .. accordion:: Folded when it's tall
        :open:

        - Line 1 of a long list, so the content is taller than the screen.
        - Line 2 of a long list, so the content is taller than the screen.
        - Line 3 of a long list, so the content is taller than the screen.
        - Line 4 of a long list, so the content is taller than the screen.
        - Line 5 of a long list, so the content is taller than the screen.
        - Line 6 of a long list, so the content is taller than the screen.
        - Line 7 of a long list, so the content is taller than the screen.
        - Line 8 of a long list, so the content is taller than the screen.
        - Line 9 of a long list, so the content is taller than the screen.
        - Line 10 of a long list, so the content is taller than the screen.
        - Line 11 of a long list, so the content is taller than the screen.
        - Line 12 of a long list, so the content is taller than the screen.
        - Line 13 of a long list, so the content is taller than the screen.
        - Line 14 of a long list, so the content is taller than the screen.
        - Line 15 of a long list, so the content is taller than the screen.
        - Line 16 of a long list, so the content is taller than the screen.
        - Line 17 of a long list, so the content is taller than the screen.
        - Line 18 of a long list, so the content is taller than the screen.
        - Line 19 of a long list, so the content is taller than the screen.
        - Line 20 of a long list, so the content is taller than the screen.
        - Line 21 of a long list, so the content is taller than the screen.
        - Line 22 of a long list, so the content is taller than the screen.
        - Line 23 of a long list, so the content is taller than the screen.
        - Line 24 of a long list, so the content is taller than the screen.
        - Line 25 of a long list, so the content is taller than the screen.
        - Line 26 of a long list, so the content is taller than the screen.
        - Line 27 of a long list, so the content is taller than the screen.
        - Line 28 of a long list, so the content is taller than the screen.
        - Line 29 of a long list, so the content is taller than the screen.
        - Line 30 of a long list, so the content is taller than the screen.
        - Line 31 of a long list, so the content is taller than the screen.
        - Line 32 of a long list, so the content is taller than the screen.
        - Line 33 of a long list, so the content is taller than the screen.
        - Line 34 of a long list, so the content is taller than the screen.
        - Line 35 of a long list, so the content is taller than the screen.

.. accordion:: Never folded
    :hide-show-more:
    :open:

    - Line 1 of a long list, so the content is taller than the screen.
    - Line 2 of a long list, so the content is taller than the screen.
    - Line 3 of a long list, so the content is taller than the screen.
    - Line 4 of a long list, so the content is taller than the screen.
    - Line 5 of a long list, so the content is taller than the screen.
    - Line 6 of a long list, so the content is taller than the screen.
    - Line 7 of a long list, so the content is taller than the screen.
    - Line 8 of a long list, so the content is taller than the screen.
    - Line 9 of a long list, so the content is taller than the screen.
    - Line 10 of a long list, so the content is taller than the screen.
    - Line 11 of a long list, so the content is taller than the screen.
    - Line 12 of a long list, so the content is taller than the screen.
    - Line 13 of a long list, so the content is taller than the screen.
    - Line 14 of a long list, so the content is taller than the screen.
    - Line 15 of a long list, so the content is taller than the screen.
    - Line 16 of a long list, so the content is taller than the screen.
    - Line 17 of a long list, so the content is taller than the screen.
    - Line 18 of a long list, so the content is taller than the screen.
    - Line 19 of a long list, so the content is taller than the screen.
    - Line 20 of a long list, so the content is taller than the screen.
    - Line 21 of a long list, so the content is taller than the screen.
    - Line 22 of a long list, so the content is taller than the screen.
    - Line 23 of a long list, so the content is taller than the screen.
    - Line 24 of a long list, so the content is taller than the screen.
    - Line 25 of a long list, so the content is taller than the screen.
    - Line 26 of a long list, so the content is taller than the screen.
    - Line 27 of a long list, so the content is taller than the screen.
    - Line 28 of a long list, so the content is taller than the screen.
    - Line 29 of a long list, so the content is taller than the screen.
    - Line 30 of a long list, so the content is taller than the screen.
    - Line 31 of a long list, so the content is taller than the screen.
    - Line 32 of a long list, so the content is taller than the screen.
    - Line 33 of a long list, so the content is taller than the screen.
    - Line 34 of a long list, so the content is taller than the screen.
    - Line 35 of a long list, so the content is taller than the screen.

.. code-block:: rst

    .. accordion:: Never folded
        :hide-show-more:
        :open:

        - Line 1 of a long list, so the content is taller than the screen.
        - Line 2 of a long list, so the content is taller than the screen.
        - Line 3 of a long list, so the content is taller than the screen.
        - Line 4 of a long list, so the content is taller than the screen.
        - Line 5 of a long list, so the content is taller than the screen.
        - Line 6 of a long list, so the content is taller than the screen.
        - Line 7 of a long list, so the content is taller than the screen.
        - Line 8 of a long list, so the content is taller than the screen.
        - Line 9 of a long list, so the content is taller than the screen.
        - Line 10 of a long list, so the content is taller than the screen.
        - Line 11 of a long list, so the content is taller than the screen.
        - Line 12 of a long list, so the content is taller than the screen.
        - Line 13 of a long list, so the content is taller than the screen.
        - Line 14 of a long list, so the content is taller than the screen.
        - Line 15 of a long list, so the content is taller than the screen.
        - Line 16 of a long list, so the content is taller than the screen.
        - Line 17 of a long list, so the content is taller than the screen.
        - Line 18 of a long list, so the content is taller than the screen.
        - Line 19 of a long list, so the content is taller than the screen.
        - Line 20 of a long list, so the content is taller than the screen.
        - Line 21 of a long list, so the content is taller than the screen.
        - Line 22 of a long list, so the content is taller than the screen.
        - Line 23 of a long list, so the content is taller than the screen.
        - Line 24 of a long list, so the content is taller than the screen.
        - Line 25 of a long list, so the content is taller than the screen.
        - Line 26 of a long list, so the content is taller than the screen.
        - Line 27 of a long list, so the content is taller than the screen.
        - Line 28 of a long list, so the content is taller than the screen.
        - Line 29 of a long list, so the content is taller than the screen.
        - Line 30 of a long list, so the content is taller than the screen.
        - Line 31 of a long list, so the content is taller than the screen.
        - Line 32 of a long list, so the content is taller than the screen.
        - Line 33 of a long list, so the content is taller than the screen.
        - Line 34 of a long list, so the content is taller than the screen.
        - Line 35 of a long list, so the content is taller than the screen.

.. _combos-accordion-with-icons:

-------------------------------------------------------------------------------
With icons.
-------------------------------------------------------------------------------

The title is text, so an icon goes before it, after it or in the middle, and
the marker is an icon too:

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        Icon before the title

        .. accordion:: :fa-icon:regular:`star` An icon before

            The content.

        .. code-block:: rst

            .. accordion:: :fa-icon:regular:`star` An icon before

                The content.

    .. column::

        Icon after the title

        .. accordion:: An icon after :fa-icon:regular:`star`

            The content.

        .. code-block:: rst

            .. accordion:: An icon after :fa-icon:regular:`star`

                The content.

    .. column::

        Icon in the middle

        .. accordion:: An :fa-icon:regular:`star` icon inside

            The content.

        .. code-block:: rst

            .. accordion:: An :fa-icon:regular:`star` icon inside

                The content.

    .. column::

        A coloured icon

        .. accordion:: :fa-icon:solid:`heart km-tone--red` Coloured

            The content.

        .. code-block:: rst

            .. accordion:: :fa-icon:solid:`heart km-tone--red` Coloured

                The content.

    .. column::

        A brand icon

        .. accordion:: :fa-icon:brands:`github` From GitHub

            The content.

        .. code-block:: rst

            .. accordion:: :fa-icon:brands:`github` From GitHub

                The content.

    .. column::

        An icon and a subheader

        .. accordion:: :fa-icon:regular:`book` Reading
            :subheader: With an icon too :fa-icon:regular:`clock`

            The content.

        .. code-block:: rst

            .. accordion:: :fa-icon:regular:`book` Reading
                :subheader: With an icon too :fa-icon:regular:`clock`

                The content.

    .. column::

        An icon and a marker after

        .. accordion:: :fa-icon:regular:`star` With a marker after
            :marker: right
            :marker-position: after

            The content.

        .. code-block:: rst

            .. accordion:: :fa-icon:regular:`star` With a marker after
                :marker: right
                :marker-position: after

                The content.

    .. column::

        Icons in the content

        .. accordion:: Icons inside
            :open:

            :fa-icon:regular:`star` At the start

            In the :fa-icon:regular:`heart` middle

            At the end :fa-icon:regular:`bell`

        .. code-block:: rst

            .. accordion:: Icons inside
                :open:

                :fa-icon:regular:`star` At the start

                In the :fa-icon:regular:`heart` middle

                At the end :fa-icon:regular:`bell`

.. _combos-accordion-with-roles:

-------------------------------------------------------------------------------
With roles.
-------------------------------------------------------------------------------

Every role works in the content. Every role but ``email`` works in the
preheader, the title and the subheader, since the whole line opens the
accordion and a link in it would do two things.

.. columns:: 2
    :gap: medium
    :valign: top
    :flush:

    .. column::

        .. accordion:: Title :sharpie:`highlighted`
            :subheader: Sub :sharpie:`highlighted`
            :open:

            Content :sharpie:`highlighted`.

        .. code-block:: rst

            .. accordion:: Title :sharpie:`highlighted`
                :subheader: Sub :sharpie:`highlighted`
                :open:

                Content :sharpie:`highlighted`.

    .. column::

        .. accordion:: Title :underline:`underlined`
            :subheader: Sub :underline:`underlined`
            :open:

            Content :underline:`underlined`.

        .. code-block:: rst

            .. accordion:: Title :underline:`underlined`
                :subheader: Sub :underline:`underlined`
                :open:

                Content :underline:`underlined`.

    .. column::

        .. accordion:: Title :ticker:`2025?short`
            :subheader: Sub :ticker:`2025?short`
            :open:

            Content :ticker:`2025?short`.

        .. code-block:: rst

            .. accordion:: Title :ticker:`2025?short`
                :subheader: Sub :ticker:`2025?short`
                :open:

                Content :ticker:`2025?short`.

    .. column::

        .. accordion:: Title :roll:`this|that|the other`
            :subheader: Sub :roll:`this|that|the other`
            :open:

            Content :roll:`this|that|the other`.

        .. code-block:: rst

            .. accordion:: Title :roll:`this|that|the other`
                :subheader: Sub :roll:`this|that|the other`
                :open:

                Content :roll:`this|that|the other`.

    .. column::

        .. accordion:: Title :kbd:mac:`Cmd-K`
            :subheader: Sub :kbd:mac:`Cmd-K`
            :open:

            Content :kbd:mac:`Cmd-K`.

        .. code-block:: rst

            .. accordion:: Title :kbd:mac:`Cmd-K`
                :subheader: Sub :kbd:mac:`Cmd-K`
                :open:

                Content :kbd:mac:`Cmd-K`.

    .. column::

        .. accordion:: Title
            :subheader: Sub
            :open:

            Content :email:`me <xa@mes3.dev>`.

        .. code-block:: rst

            .. accordion:: Title
                :subheader: Sub
                :open:

                Content :email:`me <xa@mes3.dev>`.

    .. column::

        .. accordion:: Title :fa-icon:solid:`heart km-tone--red`
            :subheader: Sub :fa-icon:solid:`heart km-tone--red`
            :open:

            Content :fa-icon:solid:`heart km-tone--red`.

        .. code-block:: rst

            .. accordion:: Title :fa-icon:solid:`heart km-tone--red`
                :subheader: Sub :fa-icon:solid:`heart km-tone--red`
                :open:

                Content :fa-icon:solid:`heart km-tone--red`.

.. _combos-accordion-holding-every-other-directive:

-------------------------------------------------------------------------------
Holding every other directive.
-------------------------------------------------------------------------------

An accordion takes every directive but byline, code-explain, code-version and
release. The first three belong to the page itself and a release belongs in a
section, so they stop the build anywhere else. Each of the others is written
inside it below, with the source under the result.

accordion
^^^^^^^^^

.. accordion:: An accordion that holds it
    :open:

    .. accordion:: An accordion

        Folded away until it opens.

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. accordion:: An accordion

            Folded away until it opens.

block
^^^^^

.. accordion:: An accordion that holds it
    :open:

    .. block:: A block
        :size: large
        :preheader: :fa-icon:regular:`star` Preheader

        The block's body.

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. block:: A block
            :size: large
            :preheader: :fa-icon:regular:`star` Preheader

            The block's body.

button
^^^^^^

.. accordion:: An accordion that holds it
    :open:

    .. button:: https://github.com/xames3/website
        :fa-icon: heart

        A button

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. button:: https://github.com/xames3/website
            :fa-icon: heart

            A button

columns
^^^^^^^

.. accordion:: An accordion that holds it
    :open:

    .. columns:: 2
        :gap: medium
        :valign: top

        .. column::

            The first column.

        .. column::

            The second column.

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. columns:: 2
            :gap: medium
            :valign: top

            .. column::

                The first column.

            .. column::

                The second column.

embed
^^^^^

.. accordion:: An accordion that holds it
    :open:

    .. embed:: iframe

        <p style="padding: 1rem; background: seagreen">
            A block of HTML.
        </p>

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. embed:: iframe

            <p style="padding: 1rem; background: seagreen">
                A block of HTML.
            </p>

repository
^^^^^^^^^^

.. accordion:: An accordion that holds it
    :open:

    .. repository:: xames3/slowtorch

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. repository:: xames3/slowtorch

tabs
^^^^

.. accordion:: An accordion that holds it
    :open:

    .. tabs::

        .. tab:: First
            :fa-icon: fa-regular fa-code

            The first tab.

        .. tab:: Second

            The second tab.

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. tabs::

            .. tab:: First
                :fa-icon: fa-regular fa-code

                The first tab.

            .. tab:: Second

                The second tab.

thumbnail
^^^^^^^^^

.. accordion:: An accordion that holds it
    :open:

    .. thumbnail:: https://youtu.be/kCc8FmEb1nY
        :title: A video
        :channel: A channel

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: A video
            :channel: A channel

video
^^^^^

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

youtube
^^^^^^^

.. accordion:: An accordion that holds it
    :open:

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :caption: A video.

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. youtube:: https://youtu.be/kCc8FmEb1nY
            :caption: A video.

.. _combos-accordion-inside-every-other-container:

-------------------------------------------------------------------------------
Inside every other container.
-------------------------------------------------------------------------------

An accordion goes anywhere a paragraph does. Here it sits in each container,
with the source under the result.

In a tab
^^^^^^^^

.. tabs::

    .. tab:: Holds it
        :selected:

        .. accordion:: The accordion
            :open:

            Held by the container.

    .. tab:: Another tab

        Nothing in this one.

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

            .. accordion:: The accordion
                :open:

                Held by the container.

        .. tab:: Another tab

            Nothing in this one.

In a column
^^^^^^^^^^^

.. columns:: 2
    :gap: medium
    :valign: top

    .. column::

        .. accordion:: The accordion
            :open:

            Held by the container.

    .. column::

        Another column.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top

        .. column::

            .. accordion:: The accordion
                :open:

                Held by the container.

        .. column::

            Another column.

In a block
^^^^^^^^^^

.. block:: A block that holds it
    :size: large

    .. accordion:: The accordion
        :open:

        Held by the container.

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. accordion:: The accordion
            :open:

            Held by the container.

In a note
^^^^^^^^^

.. note::

    .. accordion:: The accordion
        :open:

        Held by the container.

.. code-block:: rst

    .. note::

        .. accordion:: The accordion
            :open:

            Held by the container.

In a list item
^^^^^^^^^^^^^^

- A list item that holds it:

  .. accordion:: The accordion
      :open:

      Held by the container.

.. code-block:: rst

    - A list item that holds it:

      .. accordion:: The accordion
          :open:

          Held by the container.

.. _combos-accordion-accordions-of-accordions:

-------------------------------------------------------------------------------
Accordions of accordions.
-------------------------------------------------------------------------------

Three deep, each with its own marker and an icon:

.. accordion:: :fa-icon:regular:`layer-group` The outer one
    :open:
    :marker: plus

    .. accordion:: :fa-icon:regular:`layer-group` The middle one
        :open:
        :marker: down

        .. accordion:: :fa-icon:regular:`layer-group` The inner one
            :open:
            :marker: right

            Three levels down.

.. code-block:: rst

    .. accordion:: :fa-icon:regular:`layer-group` The outer one
        :open:
        :marker: plus

        .. accordion:: :fa-icon:regular:`layer-group` The middle one
            :open:
            :marker: down

            .. accordion:: :fa-icon:regular:`layer-group` The inner one
                :open:
                :marker: right

                Three levels down.

.. _combos-accordion-all-at-once:

-------------------------------------------------------------------------------
All at once.
-------------------------------------------------------------------------------

An accordion in tabs in columns, holding a block with a button, code and a
roles line:

.. columns:: 2
    :gap: medium
    :valign: top

    .. column::

        .. tabs::

            .. tab:: :fa-icon:regular:`folder-open` Folded
                :fa-icon: fa-regular fa-folder-open
                :selected:

                .. accordion:: :fa-icon:regular:`star` Everything in one
                    :subheader: With a :sharpie:`subheader`
                    :open:

                    .. block:: A block
                        :size: large
                        :preheader: :fa-icon:regular:`heart` Preheader
                        :footer: Footer :fa-icon:regular:`arrow-right`

                        .. button:: https://github.com/xames3/website
                            :fa-icon: arrow-right
                            :icon-position: after

                            A button

                        .. code-block:: python
                            :caption: total.py

                            total = sum(range(3))

                        Press :kbd:mac:`Cmd-K` to
                        :roll:`read|write|run`.

            .. tab:: Other

                Another tab.

    .. column::

        .. accordion:: A neighbour
            :open:

            Next to the tabs.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top

        .. column::

            .. tabs::

                .. tab:: :fa-icon:regular:`folder-open` Folded
                    :fa-icon: fa-regular fa-folder-open
                    :selected:

                    .. accordion:: :fa-icon:regular:`star` Everything in one
                        :subheader: With a :sharpie:`subheader`
                        :open:

                        .. block:: A block
                            :size: large
                            :preheader: :fa-icon:regular:`heart` Preheader
                            :footer: Footer :fa-icon:regular:`arrow-right`

                            .. button:: https://github.com/xames3/website
                                :fa-icon: arrow-right
                                :icon-position: after

                                A button

                            .. code-block:: python
                                :caption: total.py

                                total = sum(range(3))

                            Press :kbd:mac:`Cmd-K` to
                            :roll:`read|write|run`.

                .. tab:: Other

                    Another tab.

        .. column::

            .. accordion:: A neighbour
                :open:

                Next to the tabs.

.. _combos-accordion-no-link-in-a-title:

-------------------------------------------------------------------------------
No link in a title.
-------------------------------------------------------------------------------

The whole line opens the accordion, so a link in its title or subheader stops
the build, and so does a title that's only an icon, since an icon adds to the
words and never stands for them. The message is written under the source:

An email in the title
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. accordion:: Mail :email:`me <xa@mes3.dev>`

        The content.

.. code-block:: text

    accordion: expected a title without a link, got one

An email in the subheader
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. accordion:: A title
        :subheader: Mail :email:`me <xa@mes3.dev>`

        The content.

.. code-block:: text

    accordion: expected a subheader without a link, got one

A title that's only an icon
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. accordion:: :fa-icon:regular:`star`

        The content.

.. code-block:: text

    accordion: expected a title with words, got only an icon or nothing
