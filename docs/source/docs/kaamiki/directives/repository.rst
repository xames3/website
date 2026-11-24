.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 19 October 2026
.. Last updated on: 23 November 2026

:km-page-title: The repository directive
:km-page-description: Show a GitHub project as a card with its star and fork
    counts and a few words from you.
:km-page-type: article
:km-header-subheader: A GitHub project as a card
:km-feedback-title: Is a card missing something?
:km-feedback-description: Tell me what you'd want it to show.
:km-feedback-button: Tell me

.. _kaamiki-repository:

===============================================================================
:fa-icon:brands:`github` repository
===============================================================================

.. rst-class:: km-text-lead

    A GitHub project as a card.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3
    :shade: graphite

The argument is the project as ``owner/name`` and whatever you write under it
goes below the name. The text is optional, one paragraph, and it can use roles
and inline markup. A list, a second paragraph or a directive in it stops the
build:

.. repository:: xames3/slowtorch

    A subset of core PyTorch features re-built in pure Python.

.. code-block:: rst

    .. repository:: xames3/slowtorch

        A subset of core PyTorch features re-built in pure Python.

The card links to the project on GitHub. The counts are fetched by the reader's
browser when the card scrolls into view, so they're always current and your
build never calls GitHub. The counts fade in and roll up to their numbers when
GitHub answers, one after the other. If GitHub can't be reached the counts
never show, and a reader without scripts doesn't see them. The argument has to
be exactly
``owner/name``: a full GitHub address, or anything with a different shape,
stops the build with a message like this one:

.. code-block:: text

    repository: expected owner/name like octocat/Hello-World, got
    'https://github.com/xames3/slowtorch'

.. _kaamiki-show-only-what-you-want:

-------------------------------------------------------------------------------
Show only what you want.
-------------------------------------------------------------------------------

``:hide-stars:`` and ``:hide-forks:`` leave a count out. Side by side in
:doc:`columns <columns>`, a card has space of its own above and below, so
``:flush:`` takes it off and leaves the spacing to the columns:

.. columns:: 2
    :flush:
    :valign: top

    .. column::

        .. repository:: xames3/xsnumpy
            :hide-forks:

            Re-implementing NumPy features in Python.

        .. code-block:: rst

            .. repository:: xames3/xsnumpy
                :hide-forks:

                Re-implementing NumPy features in Python.

    .. column::

        .. repository:: xames3/xsnumpy
            :hide-stars:

            Re-implementing NumPy features in Python.

        .. code-block:: rst

            .. repository:: xames3/xsnumpy
                :hide-stars:

                Re-implementing NumPy features in Python.



.. _kaamiki-repository-while-github-answers:

-------------------------------------------------------------------------------
While GitHub answers.
-------------------------------------------------------------------------------

Nothing stands where the counts will be while GitHub thinks: the card shows
its name, its text and its link, and the counts fade in and roll up to their
numbers when GitHub answers, one after the other. If GitHub says no or says
nothing, the card keeps its text and its link and shows no counts. The fade and
the roll follow :ref:`the card's speed <kaamiki-directives-motion>`. A reader
who asks for less motion gets a brief fade, and so does a card that says
``:no-motion:``, which rolls nothing.

.. accordion:: See it slow

    The cards on this page are real, so GitHub usually answers before you
    could see anything. Throttle the network in your browser's developer tools
    to a slow connection, reload the page and scroll to the card:

    .. repository:: xames3/slowtorch

        A subset of core PyTorch features re-built in pure Python.

.. _kaamiki-repository-options:

-------------------------------------------------------------------------------
Every option.
-------------------------------------------------------------------------------

.. accordion:: The full table

    .. list-table::
        :header-rows: 1
        :widths: 24 76

        * - Option
          - What it does
        * - ``:hide-stars:``
          - Leaves out the star count, which is shown without it.
        * - ``:hide-forks:``
          - Leaves out the fork count, which is shown without it.
        * - ``:name:``
          - A name to link to, as :ref:`every directive takes it
            <kaamiki-directives-common>`.
        * - ``:class:``
          - Extra classes for the card.
        * - ``:speed:``
          - How quick its motion is, a step of the site's speed, as
            :ref:`every directive that moves takes it
            <kaamiki-directives-motion>`.
        * - ``:no-motion:``
          - Plays nothing in it, as :ref:`every directive that moves takes it
            <kaamiki-directives-motion>`.
