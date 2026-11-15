.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 October 2026
.. Last updated on: 08 November 2026

:km-page-title: Repositories, everywhere
:km-page-description: Every option of the repository directive on and off, with
    icons and roles, in rows and in cards and inside every container.
:km-page-type: article
:km-header-subheader: Every way to show a project
:km-feedback-title: Did I miss a way to combine them?
:km-feedback-description: Tell me what you tried with a repository that didn't
    work.
:km-feedback-button: Tell me
:km-feedback-icon: fa-brands fa-github

.. _combos-repository:

===============================================================================
:fa-icon:brands:`github` Repositories, everywhere
===============================================================================

.. rst-class:: km-text-lead

    A GitHub project, in every combination.

A repository shows a GitHub project as a card with its stars and forks, counted
when the page loads. This page writes it with every option on and off, with a
description, icons and roles, in rows and inside every container, so the markup
and the result sit side by side.

.. _combos-repository-the-options-one-at-a-time:

-------------------------------------------------------------------------------
The options, one at a time.
-------------------------------------------------------------------------------

No options.

.. repository:: xames3/slowtorch

.. code-block:: rst

    .. repository:: xames3/slowtorch

``:hide-stars:``

.. repository:: xames3/slowtorch
    :hide-stars:

.. code-block:: rst

    .. repository:: xames3/slowtorch
        :hide-stars:

``:hide-forks:``

.. repository:: xames3/slowtorch
    :hide-forks:

.. code-block:: rst

    .. repository:: xames3/slowtorch
        :hide-forks:

Both hidden: only the name.

.. repository:: xames3/slowtorch
    :hide-stars:
    :hide-forks:

.. code-block:: rst

    .. repository:: xames3/slowtorch
        :hide-stars:
        :hide-forks:

``:class:``

.. repository:: xames3/slowtorch
    :class: km-tone-blue

.. code-block:: rst

    .. repository:: xames3/slowtorch
        :class: km-tone-blue

A description, which is the content.

.. repository:: xames3/slowtorch

    A description under the name.

.. code-block:: rst

    .. repository:: xames3/slowtorch

        A description under the name.

A description and an option.

.. repository:: xames3/slowtorch
    :hide-forks:

    A description with ``:hide-forks:``.

.. code-block:: rst

    .. repository:: xames3/slowtorch
        :hide-forks:

        A description with ``:hide-forks:``.

.. _combos-repository-cards-beside-cards:

-------------------------------------------------------------------------------
Cards beside cards.
-------------------------------------------------------------------------------

Two cards in columns.

.. columns:: 2
    :gap: medium
    :valign: top

    .. column::

        .. repository:: xames3/slowtorch

            A subset of PyTorch re-built in Python.

    .. column::

        .. repository:: xames3/xsnumpy

            A NumPy re-implementation.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top

        .. column::

            .. repository:: xames3/slowtorch

                A subset of PyTorch re-built in Python.

        .. column::

            .. repository:: xames3/xsnumpy

                A NumPy re-implementation.

Cards in a block, each with something hidden.

.. block:: Projects
    :size: large
    :preheader: :fa-icon:brands:`github` Open source

    .. repository:: xames3/slowtorch
        :hide-forks:

    .. repository:: xames3/xsnumpy
        :hide-stars:

.. code-block:: rst

    .. block:: Projects
        :size: large
        :preheader: :fa-icon:brands:`github` Open source

        .. repository:: xames3/slowtorch
            :hide-forks:

        .. repository:: xames3/xsnumpy
            :hide-stars:

.. _combos-repository-with-icons:

-------------------------------------------------------------------------------
With icons.
-------------------------------------------------------------------------------

An icon first.

.. repository:: xames3/slowtorch

    :fa-icon:regular:`star` An icon first in the description.

.. code-block:: rst

    .. repository:: xames3/slowtorch

        :fa-icon:regular:`star` An icon first in the description.

An icon last.

.. repository:: xames3/slowtorch

    An icon last in the description :fa-icon:regular:`star`

.. code-block:: rst

    .. repository:: xames3/slowtorch

        An icon last in the description :fa-icon:regular:`star`

An icon inside.

.. repository:: xames3/slowtorch

    An :fa-icon:regular:`star` icon in the middle.

.. code-block:: rst

    .. repository:: xames3/slowtorch

        An :fa-icon:regular:`star` icon in the middle.

.. _combos-repository-with-roles:

-------------------------------------------------------------------------------
With roles.
-------------------------------------------------------------------------------

.. repository:: xames3/slowtorch

    A description :sharpie:`highlighted`.

.. code-block:: rst

    .. repository:: xames3/slowtorch

        A description :sharpie:`highlighted`.

.. repository:: xames3/slowtorch

    A description :underline:`underlined`.

.. code-block:: rst

    .. repository:: xames3/slowtorch

        A description :underline:`underlined`.

.. repository:: xames3/slowtorch

    A description :ticker:`2025?short`.

.. code-block:: rst

    .. repository:: xames3/slowtorch

        A description :ticker:`2025?short`.

.. repository:: xames3/slowtorch

    A description :swap:`this|that|the other`.

.. code-block:: rst

    .. repository:: xames3/slowtorch

        A description :swap:`this|that|the other`.

.. repository:: xames3/slowtorch

    A description :kbd:mac:`Cmd-K`.

.. code-block:: rst

    .. repository:: xames3/slowtorch

        A description :kbd:mac:`Cmd-K`.

.. repository:: xames3/slowtorch

    A description :email:`me <xa@mes3.dev>`.

.. code-block:: rst

    .. repository:: xames3/slowtorch

        A description :email:`me <xa@mes3.dev>`.

.. repository:: xames3/slowtorch

    A description :fa-icon:solid:`heart km-tone--red`.

.. code-block:: rst

    .. repository:: xames3/slowtorch

        A description :fa-icon:solid:`heart km-tone--red`.

.. _combos-repository-inside-every-other-container:

-------------------------------------------------------------------------------
Inside every other container.
-------------------------------------------------------------------------------

A repository card goes anywhere a paragraph does. Here it sits in each
container, with the source under the result.

In an accordion
^^^^^^^^^^^^^^^

.. accordion:: An accordion that holds it
    :open:

    .. repository:: xames3/slowtorch

        A description.

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. repository:: xames3/slowtorch

            A description.

In a tab
^^^^^^^^

.. tabs::

    .. tab:: Holds it
        :selected:

        .. repository:: xames3/slowtorch

            A description.

    .. tab:: Another tab

        Nothing in this one.

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

            .. repository:: xames3/slowtorch

                A description.

        .. tab:: Another tab

            Nothing in this one.

In a column
^^^^^^^^^^^

.. columns:: 2
    :gap: medium
    :valign: top

    .. column::

        .. repository:: xames3/slowtorch

            A description.

    .. column::

        Another column.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top

        .. column::

            .. repository:: xames3/slowtorch

                A description.

        .. column::

            Another column.

In a block
^^^^^^^^^^

.. block:: A block that holds it
    :size: large

    .. repository:: xames3/slowtorch

        A description.

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. repository:: xames3/slowtorch

            A description.

In a note
^^^^^^^^^

.. note::

    .. repository:: xames3/slowtorch

        A description.

.. code-block:: rst

    .. note::

        .. repository:: xames3/slowtorch

            A description.

In a list item
^^^^^^^^^^^^^^

- A list item that holds it:

  .. repository:: xames3/slowtorch

      A description.

.. code-block:: rst

    - A list item that holds it:

      .. repository:: xames3/slowtorch

          A description.

.. _combos-repository-one-paragraph:

-------------------------------------------------------------------------------
One paragraph.
-------------------------------------------------------------------------------

The description is one paragraph of text. A list, a second paragraph or a
directive in it stops the build. The message is written under the source:

A list in the description
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. repository:: xames3/slowtorch

        - one
        - two

.. code-block:: text

    repository: expected one paragraph of text, got a list

A directive in the description
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. repository:: xames3/slowtorch

        .. accordion:: A title

            The content.

.. code-block:: text

    repository: expected one paragraph of text, got a directive
