.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 October 2026
.. Last updated on: 19 November 2026

:km-page-title: Releases, everywhere
:km-page-description: Every option of the release directive on and off, with
    every group and with icons and roles.
:km-page-type: article
:km-header-subheader: Every way to write a changelog entry
:km-feedback-title: Did I miss a way to combine them?
:km-feedback-description: Tell me what you tried with a release that didn't
    work.
:km-feedback-button: Tell me
:km-feedback-icon: fa-tag

.. _combos-release:

===============================================================================
:fa-icon:regular:`tag` Releases, everywhere
===============================================================================

.. rst-class:: km-text-lead

    A changelog entry, in every combination.

A release is one entry of a changelog: a version, a date, a summary and notes
in groups. This page writes it with every option on and off, with every group
and with icons and roles, so the markup and the result sit side by side. Every
release here has a version of its own, since a version may be written once on
the whole site.

.. _combos-release-the-options-one-at-a-time:

-------------------------------------------------------------------------------
The options, one at a time.
-------------------------------------------------------------------------------

Only ``:version:``: the version is the title.

.. release::
    :version: demo-release-1

    A short summary.

    Added
        - A new thing

    Fixed
        - An old thing

.. code-block:: rst

    .. release::
        :version: demo-release-1

        A short summary.

        Added
            - A new thing

        Fixed
            - An old thing

The argument, a title of its own.

.. release:: A title of its own
    :version: demo-release-2

    A short summary.

    Added
        - A new thing

    Fixed
        - An old thing

.. code-block:: rst

    .. release:: A title of its own
        :version: demo-release-2

        A short summary.

        Added
            - A new thing

        Fixed
            - An old thing

``:date:``, written as a date.

.. release::
    :version: demo-release-3
    :date: 2026-10-05

    A short summary.

    Added
        - A new thing

    Fixed
        - An old thing

.. code-block:: rst

    .. release::
        :version: demo-release-3
        :date: 2026-10-05

        A short summary.

        Added
            - A new thing

        Fixed
            - An old thing

``:date:``, written out.

.. release::
    :version: demo-release-4
    :date: 30 October 2026

    A short summary.

    Added
        - A new thing

    Fixed
        - An old thing

.. code-block:: rst

    .. release::
        :version: demo-release-4
        :date: 30 October 2026

        A short summary.

        Added
            - A new thing

        Fixed
            - An old thing

``:article:``, a page that tells the story.

.. release::
    :version: demo-release-5
    :article: ../roles

    A short summary.

    Added
        - A new thing

    Fixed
        - An old thing

.. code-block:: rst

    .. release::
        :version: demo-release-5
        :article: ../roles

        A short summary.

        Added
            - A new thing

        Fixed
            - An old thing

``:article-label:``

.. release::
    :version: demo-release-6
    :article: ../roles
    :article-label: The long read

    A short summary.

    Added
        - A new thing

    Fixed
        - An old thing

.. code-block:: rst

    .. release::
        :version: demo-release-6
        :article: ../roles
        :article-label: The long read

        A short summary.

        Added
            - A new thing

        Fixed
            - An old thing

``:target:``, the release elsewhere.

.. release::
    :version: demo-release-7
    :target: https://github.com/xames3/website/releases

    A short summary.

    Added
        - A new thing

    Fixed
        - An old thing

.. code-block:: rst

    .. release::
        :version: demo-release-7
        :target: https://github.com/xames3/website/releases

        A short summary.

        Added
            - A new thing

        Fixed
            - An old thing

``:article:`` and ``:target:`` together.

.. release::
    :version: demo-release-8
    :article: ../roles
    :target: https://github.com/xames3/website/releases

    A short summary.

    Added
        - A new thing

    Fixed
        - An old thing

.. code-block:: rst

    .. release::
        :version: demo-release-8
        :article: ../roles
        :target: https://github.com/xames3/website/releases

        A short summary.

        Added
            - A new thing

        Fixed
            - An old thing

``:class:``

.. release::
    :version: demo-release-9
    :class: km-tone-blue

    A short summary.

    Added
        - A new thing

    Fixed
        - An old thing

.. code-block:: rst

    .. release::
        :version: demo-release-9
        :class: km-tone-blue

        A short summary.

        Added
            - A new thing

        Fixed
            - An old thing

Every option at once.

.. release:: Everything on
    :version: demo-release-10
    :date: 30 October 2026
    :article: ../roles
    :article-label: The long read
    :target: https://github.com/xames3/website/releases
    :class: km-tone-green

    A short summary.

    Added
        - A new thing

    Fixed
        - An old thing

.. code-block:: rst

    .. release:: Everything on
        :version: demo-release-10
        :date: 30 October 2026
        :article: ../roles
        :article-label: The long read
        :target: https://github.com/xames3/website/releases
        :class: km-tone-green

        A short summary.

        Added
            - A new thing

        Fixed
            - An old thing

.. _combos-release-every-group:

-------------------------------------------------------------------------------
Every group.
-------------------------------------------------------------------------------

The terms of the definition list name the groups. Kaamiki knows *Added*,
*Changed*, *Deprecated*, *Fixed* and *Removed*:

.. release:: All five groups
    :version: demo-release-11

    Every group, in the order they're written.

    Added
        - A new thing

    Changed
        - A better thing

    Deprecated
        - A thing going away

    Fixed
        - An old thing

    Removed
        - A gone thing

.. code-block:: rst

    .. release:: All five groups
        :version: demo-release-11

        Every group, in the order they're written.

        Added
            - A new thing

        Changed
            - A better thing

        Deprecated
            - A thing going away

        Fixed
            - An old thing

        Removed
            - A gone thing

One group, no summary.

.. release:: One group
    :version: demo-release-12

    Added
        - Just one

.. code-block:: rst

    .. release:: One group
        :version: demo-release-12

        Added
            - Just one

Several notes in a group.

.. release:: Many notes
    :version: demo-release-13

    Added
        - First
        - Second
        - Third with :fa-icon:regular:`star`
        - Fourth

.. code-block:: rst

    .. release:: Many notes
        :version: demo-release-13

        Added
            - First
            - Second
            - Third with :fa-icon:regular:`star`
            - Fourth

A group that isn't one of these five stops the build, unless it's a name in
``kaamiki.conf.release.kinds``.

A summary and nothing else.

.. release:: A summary only
    :version: demo-release-14

    Only a summary, with no groups at all.

.. code-block:: rst

    .. release:: A summary only
        :version: demo-release-14

        Only a summary, with no groups at all.

.. _combos-release-a-changelog-newest-first:

-------------------------------------------------------------------------------
A changelog, newest first.
-------------------------------------------------------------------------------

Releases written one after another, newest first.

.. release:: The third
    :version: demo-release-15
    :date: 2026-10-30

    Added
        - Newest

.. release:: The second
    :version: demo-release-16
    :date: 2026-10-15

    Fixed
        - Middle

.. release:: The first
    :version: demo-release-17
    :date: 2026-10-01

    Added
        - Oldest

.. code-block:: rst

    .. release:: The third
        :version: demo-release-15
        :date: 2026-10-30

        Added
            - Newest

    .. release:: The second
        :version: demo-release-16
        :date: 2026-10-15

        Fixed
            - Middle

    .. release:: The first
        :version: demo-release-17
        :date: 2026-10-01

        Added
            - Oldest

.. _combos-release-with-icons:

-------------------------------------------------------------------------------
With icons.
-------------------------------------------------------------------------------

An icon in the title, the summary and the notes.

.. release:: Icons in the title :fa-icon:regular:`star`
    :version: demo-release-18

    :fa-icon:regular:`star` A summary with an icon first.

    Added
        - :fa-icon:regular:`star` Icon first
        - Icon last :fa-icon:regular:`star`
        - An :fa-icon:regular:`star` icon inside

.. code-block:: rst

    .. release:: Icons in the title :fa-icon:regular:`star`
        :version: demo-release-18

        :fa-icon:regular:`star` A summary with an icon first.

        Added
            - :fa-icon:regular:`star` Icon first
            - Icon last :fa-icon:regular:`star`
            - An :fa-icon:regular:`star` icon inside

.. _combos-release-with-roles:

-------------------------------------------------------------------------------
With roles.
-------------------------------------------------------------------------------

.. release:: A title :sharpie:`highlighted`
    :version: demo-release-19

    A summary :sharpie:`highlighted`.

    Added
        - A note :sharpie:`highlighted`

.. code-block:: rst

    .. release:: A title :sharpie:`highlighted`
        :version: demo-release-19

        A summary :sharpie:`highlighted`.

        Added
            - A note :sharpie:`highlighted`

.. release:: A title :underline:`underlined`
    :version: demo-release-20

    A summary :underline:`underlined`.

    Added
        - A note :underline:`underlined`

.. code-block:: rst

    .. release:: A title :underline:`underlined`
        :version: demo-release-20

        A summary :underline:`underlined`.

        Added
            - A note :underline:`underlined`

.. release:: A title :ticker:`2025?short`
    :version: demo-release-21

    A summary :ticker:`2025?short`.

    Added
        - A note :ticker:`2025?short`

.. code-block:: rst

    .. release:: A title :ticker:`2025?short`
        :version: demo-release-21

        A summary :ticker:`2025?short`.

        Added
            - A note :ticker:`2025?short`

.. release:: A title :roll:`this|that|the other`
    :version: demo-release-22

    A summary :roll:`this|that|the other`.

    Added
        - A note :roll:`this|that|the other`

.. code-block:: rst

    .. release:: A title :roll:`this|that|the other`
        :version: demo-release-22

        A summary :roll:`this|that|the other`.

        Added
            - A note :roll:`this|that|the other`

.. release:: A title :kbd:mac:`Cmd-K`
    :version: demo-release-23

    A summary :kbd:mac:`Cmd-K`.

    Added
        - A note :kbd:mac:`Cmd-K`

.. code-block:: rst

    .. release:: A title :kbd:mac:`Cmd-K`
        :version: demo-release-23

        A summary :kbd:mac:`Cmd-K`.

        Added
            - A note :kbd:mac:`Cmd-K`

.. release:: A title :email:`me <xa@mes3.dev>`
    :version: demo-release-24

    A summary :email:`me <xa@mes3.dev>`.

    Added
        - A note :email:`me <xa@mes3.dev>`

.. code-block:: rst

    .. release:: A title :email:`me <xa@mes3.dev>`
        :version: demo-release-24

        A summary :email:`me <xa@mes3.dev>`.

        Added
            - A note :email:`me <xa@mes3.dev>`

.. release:: A title :fa-icon:solid:`heart km-tone--red`
    :version: demo-release-25

    A summary :fa-icon:solid:`heart km-tone--red`.

    Added
        - A note :fa-icon:solid:`heart km-tone--red`

.. code-block:: rst

    .. release:: A title :fa-icon:solid:`heart km-tone--red`
        :version: demo-release-25

        A summary :fa-icon:solid:`heart km-tone--red`.

        Added
            - A note :fa-icon:solid:`heart km-tone--red`

.. _combos-release-holding-every-other-directive:

-------------------------------------------------------------------------------
Holding every other directive.
-------------------------------------------------------------------------------

A release takes every directive but byline, code-explain and code-version,
which belong to the page itself and stop the build anywhere else. Each is
written inside it below, with the source under the result.

accordion
^^^^^^^^^

.. release:: A release that holds it
    :version: demo-release-26

    .. accordion:: An accordion

        Folded away until it opens.

.. code-block:: rst

    .. release:: A release that holds it
        :version: demo-release-26

        .. accordion:: An accordion

            Folded away until it opens.

block
^^^^^

.. release:: A release that holds it
    :version: demo-release-27

    .. block:: A block
        :size: large
        :preheader: :fa-icon:regular:`star` Preheader

        The block's body.

.. code-block:: rst

    .. release:: A release that holds it
        :version: demo-release-27

        .. block:: A block
            :size: large
            :preheader: :fa-icon:regular:`star` Preheader

            The block's body.

button
^^^^^^

.. release:: A release that holds it
    :version: demo-release-28

    .. button:: https://github.com/xames3/website
        :fa-icon: heart

        A button

.. code-block:: rst

    .. release:: A release that holds it
        :version: demo-release-28

        .. button:: https://github.com/xames3/website
            :fa-icon: heart

            A button

columns
^^^^^^^

.. release:: A release that holds it
    :version: demo-release-29

    .. columns:: 2
        :gap: medium
        :valign: top

        .. column::

            The first column.

        .. column::

            The second column.

.. code-block:: rst

    .. release:: A release that holds it
        :version: demo-release-29

        .. columns:: 2
            :gap: medium
            :valign: top

            .. column::

                The first column.

            .. column::

                The second column.

embed
^^^^^

.. release:: A release that holds it
    :version: demo-release-30

    .. embed:: iframe

        <p style="padding: 1rem; background: seagreen">
            A block of HTML.
        </p>

.. code-block:: rst

    .. release:: A release that holds it
        :version: demo-release-30

        .. embed:: iframe

            <p style="padding: 1rem; background: seagreen">
                A block of HTML.
            </p>

repository
^^^^^^^^^^

.. release:: A release that holds it
    :version: demo-release-31

    .. repository:: xames3/slowtorch

.. code-block:: rst

    .. release:: A release that holds it
        :version: demo-release-31

        .. repository:: xames3/slowtorch

tabs
^^^^

.. release:: A release that holds it
    :version: demo-release-32

    .. tabs::

        .. tab:: First
            :fa-icon: fa-regular fa-code

            The first tab.

        .. tab:: Second

            The second tab.

.. code-block:: rst

    .. release:: A release that holds it
        :version: demo-release-32

        .. tabs::

            .. tab:: First
                :fa-icon: fa-regular fa-code

                The first tab.

            .. tab:: Second

                The second tab.

thumbnail
^^^^^^^^^

.. release:: A release that holds it
    :version: demo-release-33

    .. thumbnail:: https://youtu.be/kCc8FmEb1nY
        :title: A video
        :channel: A channel

.. code-block:: rst

    .. release:: A release that holds it
        :version: demo-release-33

        .. thumbnail:: https://youtu.be/kCc8FmEb1nY
            :title: A video
            :channel: A channel

video
^^^^^

.. release:: A release that holds it
    :version: demo-release-34

    .. video:: _static/combos/sample.webm
        :poster: _static/combos/poster.jpg
        :caption: A short clip.

.. code-block:: rst

    .. release:: A release that holds it
        :version: demo-release-34

        .. video:: _static/combos/sample.webm
            :poster: _static/combos/poster.jpg
            :caption: A short clip.

youtube
^^^^^^^

.. release:: A release that holds it
    :version: demo-release-35

    .. youtube:: https://youtu.be/kCc8FmEb1nY
        :caption: A video.

.. code-block:: rst

    .. release:: A release that holds it
        :version: demo-release-35

        .. youtube:: https://youtu.be/kCc8FmEb1nY
            :caption: A video.

.. _combos-release-not-in-a-release:

-------------------------------------------------------------------------------
Not in a release.
-------------------------------------------------------------------------------

A release holds no other release, so the build stops with the message under the
source:

.. code-block:: rst

    .. release:: The outer one
        :version: demo-release-36

        .. release:: The inner one
            :version: demo-release-37

            Held by the outer one.

.. code-block:: text

    release: expected directly in a section, got it in a release

.. _combos-release-not-in-a-column:

-------------------------------------------------------------------------------
Not in a column.
-------------------------------------------------------------------------------

A release goes directly in a section and a column isn't one, so the build
stops with the message under the source:

.. code-block:: rst

    .. columns:: 2

        .. column::

            .. release:: In a column
                :version: demo-release-38

                Held by a column.

        .. column::

            Beside it.

.. code-block:: text

    release: expected directly in a section, got it in a column

.. _combos-release-not-in-anything-but-a-section:

-------------------------------------------------------------------------------
Not in anything but a section.
-------------------------------------------------------------------------------

A release goes directly in a section, on the page or under a heading, and
``.. only::`` around it is fine. Anywhere else it stops the build, whether
that's an accordion, a tab, a block, a column, a list, a note or another
release. The message names what it was in:

.. code-block:: rst

    .. accordion:: An accordion that holds it

        .. release::
            :version: demo-release-39

            A short summary.

            Added
                - A new thing

            Fixed
                - An old thing

.. code-block:: text

    release: expected directly in a section, got it in an accordion
