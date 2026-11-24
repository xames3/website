.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 23 October 2026
.. Last updated on: 23 November 2026

:km-page-title: The block directive
:km-page-description: Frame a title and some content as a card that can link to
    an address, a page or a label.
:km-page-type: article
:km-header-subheader: A card with a title and some content
:km-feedback-title: Is a block missing something?
:km-feedback-description: Tell me which option you'd want.
:km-feedback-button: Tell me

.. _kaamiki-block:

===============================================================================
:fa-icon:regular:`rectangle-list` block
===============================================================================

.. rst-class:: km-text-lead

    A card with a title and some content.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3

The argument is the title and everything under it is the content. The title is
read like a paragraph, so it can hold markup, and the content is read as
reStructuredText, so buttons, repository cards and other directives all work
inside it:

.. block:: Kaamiki

    A Sphinx theme built for teaching.

.. code-block:: rst

    .. block:: Kaamiki

        A Sphinx theme built for teaching.

.. _kaamiki-three-two-or-one-in-a-line:

-------------------------------------------------------------------------------
Three, two or one in a line.
-------------------------------------------------------------------------------

Blocks written one after another form rows, and ``:size:`` says how many fit
in one: ``small`` is three, ``medium`` is two and ``large``, the default, is
one. A block of another size, or a paragraph between two blocks, starts a new
row. Inside a ``column`` they aren't put in rows at all: they sit one under
the other, each as wide as the column. On a phone they stack:

.. block:: One
    :size: small

    The first of three.

.. block:: Two
    :size: small

    The second.

.. block:: Three
    :size: small

    The third.

.. code-block:: rst

    .. block:: One
        :size: small

        The first of three.

    .. block:: Two
        :size: small

        The second.

    .. block:: Three
        :size: small

        The third.

Inside :doc:`columns <columns>` a block takes the whole ``column`` and ignores
``:size:``, because the columns decide where it goes.

.. _kaamiki-a-preheader-a-subheader-and-a-footer:

-------------------------------------------------------------------------------
A preheader, a subheader and a footer.
-------------------------------------------------------------------------------

``:preheader:``, ``:subheader:`` and ``:footer:`` are read like a paragraph, so
roles work in them. ``:preheader:`` is a small line above the title and
``:subheader:`` a smaller one under it:

.. block:: Teaching
    :preheader: :fa-icon:regular:`comments` Keep it stupid simple
    :subheader: A story from 2025
    :footer: Last updated on 23 October 2026

    What I enjoy most is explaining a topic so it clicks.

.. code-block:: rst

    .. block:: Teaching
        :preheader: :fa-icon:regular:`comments` Keep it stupid simple
        :subheader: A story from 2025
        :footer: Last updated on 23 October 2026

        What I enjoy most is explaining a topic so it clicks.

.. _kaamiki-block-links:

-------------------------------------------------------------------------------
A whole block is a link.
-------------------------------------------------------------------------------

Give it a ``:target:`` (an address), a ``:doc:`` (a document) or a ``:ref:``
(a label) and a click anywhere on it goes there. Its fill changes when you
point at it and links inside it keep working. A link to another site opens in
a new tab, as a link does anywhere else on the site. Its preheader, title,
subheader and footer can't hold a link of their own:

.. block:: The columns directive
    :subheader: Next door
    :doc: columns

    Content side by side, stacked on a phone.

.. code-block:: rst

    .. block:: The columns directive
        :subheader: Next door
        :doc: columns

        Content side by side, stacked on a phone.

.. _kaamiki-anything-goes-inside:

-------------------------------------------------------------------------------
Almost anything goes inside.
-------------------------------------------------------------------------------

Everything but ``byline``, ``code-explain``, ``code-version`` and ``release``,
which go on the page itself or in a section. Another ``block`` doesn't go in
one either, since a card in a card draws no frame of its own, and a ``columns``
has no room in a small or medium one. Here are a
repository card, flat so the block is the only frame, and a button at the end
of a block:

.. block:: A subset of PyTorch

    .. repository:: xames3/slowtorch

        A subset of core PyTorch features re-built in pure Python.

    .. button:: https://github.com/xames3/slowtorch
        :scheme: green

        View the source

.. code-block:: rst

    .. block:: A subset of PyTorch

        .. repository:: xames3/slowtorch

            A subset of core PyTorch features re-built in pure Python.

        .. button:: https://github.com/xames3/slowtorch
            :scheme: green

            View the source

.. _kaamiki-block-errors:

-------------------------------------------------------------------------------
Mistakes it catches.
-------------------------------------------------------------------------------

Each of these stops the build with a message naming the line:

- more than one of ``:target:``, ``:doc:`` and ``:ref:``
- a ``:size:`` that isn't one of the words above
- a block with no title
- a ``byline``, ``code-explain``, ``code-version``, ``release`` or another
  ``block`` inside it
- a link in the preheader, title, subheader or footer of a block that's a link
- an ``accordion``, ``tabs``, ``video``, ``youtube``, ``embed`` or walkthrough
  in the body of a block that's a link
- a ``columns`` in a small or medium ``block``
- a link to a document or a label that doesn't exist

.. _kaamiki-block-options:

-------------------------------------------------------------------------------
Every option.
-------------------------------------------------------------------------------

.. accordion:: The full table

    .. list-table::
        :header-rows: 1
        :widths: 26 74

        * - Option
          - What it does
        * - ``:preheader:``
          - A small line above the title. It's parsed like a paragraph, so
            roles work, like ``:fa-icon:regular:`heart` Love``.
        * - ``:subheader:``
          - A smaller line under the title.
        * - ``:footer:``
          - Text at the bottom, written like ``:preheader:``.
        * - ``:target:``
          - An address the whole block links to. It's ``http``, ``https``,
            ``mailto:``, a path on the site or a ``#`` fragment.
        * - ``:doc:``
          - A document the whole block links to, written like the argument of
            the ``:doc:`` role, so it can be relative to the page. It has to
            exist.
        * - ``:ref:``
          - A label the whole block links to, written as the ``:ref:`` role
            writes it, so colons, spaces and capitals are fine. A block takes
            one of ``:target:``, ``:doc:`` and ``:ref:``.
        * - ``:size:``
          - How wide it is when blocks sit side by side: ``small``,
            ``medium`` or ``large``, the default.
        * - ``:name:``
          - A name to link to, as :ref:`every directive takes it
            <kaamiki-directives-common>`.
        * - ``:class:``
          - Extra classes for the block.
