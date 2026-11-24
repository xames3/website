.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 19 October 2026
.. Last updated on: 23 November 2026

:km-page-title: The release directive
:km-page-description: Write one entry of a changelog with its version, its date
    and the notes grouped as added, changed, fixed and removed.
:km-page-type: article
:km-header-subheader: One entry of a changelog
:km-feedback-title: Is a release missing something?
:km-feedback-description: Tell me which option or group you'd want.
:km-feedback-button: Tell me

.. _kaamiki-release:

===============================================================================
:fa-icon:regular:`tag` release
===============================================================================

.. rst-class:: km-text-lead

    One entry of a changelog.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3
    :shade: green

The argument is the title, ``:version:`` is the version and the notes under it
are a definition list with each term naming a group. Stack as many as you like
on one page, newest first.
A release goes directly in a section, not in a ``column`` or any other
container, and holds no other release. A walkthrough goes on the page, not in
a release.
This website's :doc:`changelog </changelog>` is a page of them:

.. release:: An example release
    :version: 1.4.0
    :date: 19 October 2026

    A short summary of the release.

    Added
        - A new thing

    Fixed
        - An old thing

.. code-block:: rst

    .. release:: An example release
        :version: 1.4.0
        :date: 19 October 2026

        A short summary of the release.

        Added
            - A new thing

        Fixed
            - An old thing

A version names one release, so writing the same version twice, on one page or
on two, stops the build. A version is up to 64 letters, numbers and ``.``,
``_``, ``+`` or ``-``, starting with a letter or a number, like ``2026.11.8``
or ``v1.2.0``. On two pages the message names the first page and where the
version is:

.. code-block:: text

    release: :version: expected a version not on the page 'changelog' yet, got
    'v1.2.0', which is at changelog.rst:12

.. _kaamiki-release-groups:

-------------------------------------------------------------------------------
Groups of changes.
-------------------------------------------------------------------------------

The terms of the definition list name the groups. Kaamiki knows *Added*,
*Changed*, *Deprecated*, *Fixed* and *Removed*, in your site's language too.
A group is a title and its list, with no icon or colour of its own:

.. release::
    :version: 1.3.0
    :date: 2026-10-05

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

    .. release::
        :version: 1.3.0
        :date: 2026-10-05

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

A definition list anywhere in the release's content counts, a note's included,
so an ordinary one there stops the build too. Any other group stops the build
until you name it in ``kaamiki.conf.release.kinds``, in lowercase. The group is
still written as you like in the release, so *Security* matches ``"security"``:

.. code-block:: python

    kaamiki.conf.release.kinds = ["security"]

.. _kaamiki-release-dates:

-------------------------------------------------------------------------------
Where the date comes from.
-------------------------------------------------------------------------------

A release looks for its date in this order:

1. ``:date:``, written ``5 October 2026`` or ``2026-10-05``. Anything else, a
   day before 2000 or one more than a year ahead stops the build.
2. The version itself, if it's spelt the way
   ``kaamiki.conf.release.version_fmt`` says. The default is ``%Y.%m.%d``, so
   ``2026.10.19`` is 19 October 2026.
3. Nothing. The release is shown without a date.

The date is written the way the rest of the site writes dates, which follows
``kaamiki.conf.site.last_updated_fmt`` and your site's ``language``. If your
versions look like ``1.4.0``, give each release a ``:date:``. If they're dates,
set nothing. If they follow another date style, change the format:

.. code-block:: python

    kaamiki.conf.release.version_fmt = "%d-%m-%Y"

.. _kaamiki-release-article:

-------------------------------------------------------------------------------
Link the story behind it.
-------------------------------------------------------------------------------

An ``:article:`` is a page of your own that tells the longer story. The release
links to it, under the notes, as "Read release notes", and the article gets a
"previous" link back to the page the release is on, as long as it has no
previous page of its own. This is how the entry for v2026.11.8 on the
:doc:`changelog </changelog>` reaches its article:

.. code-block:: rst

    .. release:: Kaamiki stops borrowing now!
        :version: v2026.11.8
        :article: changelogs/november-2026

        Two directives that show code instead of describing it.

``:target:`` links the release somewhere else too, such as a GitHub release, as
"View release". The icon on the article link is the ``release_notes`` icon,
always a solid tag, and the one in front of the date is ``release_date``, a
calendar in your icon style. Both can be changed with
``kaamiki.conf.icons.names``.

.. _kaamiki-release-options:

-------------------------------------------------------------------------------
Every option.
-------------------------------------------------------------------------------

.. accordion:: The full table

    .. list-table::
        :header-rows: 1
        :widths: 26 74

        * - Option
          - What it does
        * - ``:version:``
          - The release's version, which a site uses once. It's needed. Without
            a title, the version is the title.
        * - ``:date:``
          - The day it went out. It wins over the version.
        * - ``:article:``
          - A page telling the story behind the release, named the way
            ``:doc:`` names a page, which has to exist. It's linked under the
            notes as "Read release notes".
        * - ``:article-label:``
          - What that link says instead, up to 60 characters. It needs
            ``:article:``.
        * - ``:target:``
          - The release elsewhere, such as a GitHub release. It's linked next
            to the article as "View release".
        * - ``:name:``
          - Another name to link to, beside the version, as :ref:`every
            directive takes it <kaamiki-directives-common>`.
        * - ``:class:``
          - Extra classes for the release.
        * - ``:speed:``
          - How quick its motion is, a step of the site's speed, as
            :ref:`every directive that moves takes it
            <kaamiki-directives-motion>`.
        * - ``:no-motion:``
          - Plays nothing in it, as :ref:`every directive that moves takes it
            <kaamiki-directives-motion>`.
