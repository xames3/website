.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 October 2026
.. Last updated on: 08 November 2026

:km-page-title: code-version, option by option
:km-page-description: Every option of the code-version directive on and off,
    with outputs and notes, with icons and roles and where it can't go.
:km-page-type: article
:km-header-subheader: Every way to show code changing
:km-feedback-title: Did I miss a way to combine them?
:km-feedback-description: Tell me what you tried with code-version that didn't
    work.
:km-feedback-button: Tell me
:km-feedback-icon: fa-code-compare

.. _combos-code-version:

===============================================================================
:fa-icon:regular:`code-compare` code-version, option by option
===============================================================================

.. rst-class:: km-text-lead

    Code changing, in every combination.

A code-version shows the versions a piece of code went through, one after the
other, turning each into the next as you scroll. This page writes it with every
option on and off, with two and three attempts, with icons and roles, so the
markup and the result sit side by side. It goes on the page itself, so the
containers it can't go in are written out at the end.

.. _combos-code-version-the-options-one-at-a-time:

-------------------------------------------------------------------------------
The options, one at a time.
-------------------------------------------------------------------------------

No options: two attempts.

.. code-version:: python
    :caption: average.py

    .. attempt::

        .. code::

            def average(numbers):
                return sum(numbers) / len(numbers)

        .. output:: broke

            >>> average([])
            ZeroDivisionError: division by zero

        Fine until a list comes in empty.

    .. attempt::

        .. code::

            def average(numbers):
                if not numbers:
                    return 0
                return sum(numbers) / len(numbers)

        .. output:: worked

            >>> average([])
            0

        .. lines:: 2-3

            An empty list is zero now.

.. code-block:: rst

    .. code-version:: python
        :caption: average.py

        .. attempt::

            .. code::

                def average(numbers):
                    return sum(numbers) / len(numbers)

            .. output:: broke

                >>> average([])
                ZeroDivisionError: division by zero

            Fine until a list comes in empty.

        .. attempt::

            .. code::

                def average(numbers):
                    if not numbers:
                        return 0
                    return sum(numbers) / len(numbers)

            .. output:: worked

                >>> average([])
                0

            .. lines:: 2-3

                An empty list is zero now.

Three attempts.

.. code-version:: python
    :caption: average.py

    .. attempt::

        .. code::

            def average(numbers):
                return sum(numbers) / len(numbers)

        .. output:: broke

            >>> average([])
            ZeroDivisionError: division by zero

        Fine until a list comes in empty.

    .. attempt::

        .. code::

            def average(numbers):
                if not numbers:
                    return 0
                return sum(numbers) / len(numbers)

        .. output:: worked

            >>> average([])
            0

        .. lines:: 2-3

            An empty list is zero now.

    .. attempt::

        .. code::

            def average(numbers):
                if not numbers:
                    return None
                return sum(numbers) / len(numbers)

        .. output:: worked

            >>> average([])

        Maybe none is more honest than zero.

.. code-block:: rst

    .. code-version:: python
        :caption: average.py

        .. attempt::

            .. code::

                def average(numbers):
                    return sum(numbers) / len(numbers)

            .. output:: broke

                >>> average([])
                ZeroDivisionError: division by zero

            Fine until a list comes in empty.

        .. attempt::

            .. code::

                def average(numbers):
                    if not numbers:
                        return 0
                    return sum(numbers) / len(numbers)

            .. output:: worked

                >>> average([])
                0

            .. lines:: 2-3

                An empty list is zero now.

        .. attempt::

            .. code::

                def average(numbers):
                    if not numbers:
                        return None
                    return sum(numbers) / len(numbers)

            .. output:: worked

                >>> average([])

            Maybe none is more honest than zero.

``:code-position: left``

.. code-version:: python
    :caption: average.py
    :code-position: left

    .. attempt::

        .. code::

            def average(numbers):
                return sum(numbers) / len(numbers)

        .. output:: broke

            >>> average([])
            ZeroDivisionError: division by zero

        Fine until a list comes in empty.

    .. attempt::

        .. code::

            def average(numbers):
                if not numbers:
                    return 0
                return sum(numbers) / len(numbers)

        .. output:: worked

            >>> average([])
            0

        .. lines:: 2-3

            An empty list is zero now.

.. code-block:: rst

    .. code-version:: python
        :caption: average.py
        :code-position: left

        .. attempt::

            .. code::

                def average(numbers):
                    return sum(numbers) / len(numbers)

            .. output:: broke

                >>> average([])
                ZeroDivisionError: division by zero

            Fine until a list comes in empty.

        .. attempt::

            .. code::

                def average(numbers):
                    if not numbers:
                        return 0
                    return sum(numbers) / len(numbers)

            .. output:: worked

                >>> average([])
                0

            .. lines:: 2-3

                An empty list is zero now.

``:pace: 160``, pixels of scrolling a version takes.

.. code-version:: python
    :caption: average.py
    :pace: 160

    .. attempt::

        .. code::

            def average(numbers):
                return sum(numbers) / len(numbers)

        .. output:: broke

            >>> average([])
            ZeroDivisionError: division by zero

        Fine until a list comes in empty.

    .. attempt::

        .. code::

            def average(numbers):
                if not numbers:
                    return 0
                return sum(numbers) / len(numbers)

        .. output:: worked

            >>> average([])
            0

        .. lines:: 2-3

            An empty list is zero now.

.. code-block:: rst

    .. code-version:: python
        :caption: average.py
        :pace: 160

        .. attempt::

            .. code::

                def average(numbers):
                    return sum(numbers) / len(numbers)

            .. output:: broke

                >>> average([])
                ZeroDivisionError: division by zero

            Fine until a list comes in empty.

        .. attempt::

            .. code::

                def average(numbers):
                    if not numbers:
                        return 0
                    return sum(numbers) / len(numbers)

            .. output:: worked

                >>> average([])
                0

            .. lines:: 2-3

                An empty list is zero now.

``:linenos:``

.. code-version:: python
    :caption: average.py
    :linenos:

    .. attempt::

        .. code::

            def average(numbers):
                return sum(numbers) / len(numbers)

        .. output:: broke

            >>> average([])
            ZeroDivisionError: division by zero

        Fine until a list comes in empty.

    .. attempt::

        .. code::

            def average(numbers):
                if not numbers:
                    return 0
                return sum(numbers) / len(numbers)

        .. output:: worked

            >>> average([])
            0

        .. lines:: 2-3

            An empty list is zero now.

.. code-block:: rst

    .. code-version:: python
        :caption: average.py
        :linenos:

        .. attempt::

            .. code::

                def average(numbers):
                    return sum(numbers) / len(numbers)

            .. output:: broke

                >>> average([])
                ZeroDivisionError: division by zero

            Fine until a list comes in empty.

        .. attempt::

            .. code::

                def average(numbers):
                    if not numbers:
                        return 0
                    return sum(numbers) / len(numbers)

            .. output:: worked

                >>> average([])
                0

            .. lines:: 2-3

                An empty list is zero now.

``:lineno-start: 10``, so the note names lines 11 and 12.

.. code-version:: python
    :caption: average.py
    :linenos:
    :lineno-start: 10

    .. attempt::

        .. code::

            def average(numbers):
                return sum(numbers) / len(numbers)

        .. output:: broke

            >>> average([])
            ZeroDivisionError: division by zero

        Fine until a list comes in empty.

    .. attempt::

        .. code::

            def average(numbers):
                if not numbers:
                    return 0
                return sum(numbers) / len(numbers)

        .. output:: worked

            >>> average([])
            0

        .. lines:: 11-12

            An empty list is zero now.

.. code-block:: rst

    .. code-version:: python
        :caption: average.py
        :linenos:
        :lineno-start: 10

        .. attempt::

            .. code::

                def average(numbers):
                    return sum(numbers) / len(numbers)

            .. output:: broke

                >>> average([])
                ZeroDivisionError: division by zero

            Fine until a list comes in empty.

        .. attempt::

            .. code::

                def average(numbers):
                    if not numbers:
                        return 0
                    return sum(numbers) / len(numbers)

            .. output:: worked

                >>> average([])
                0

            .. lines:: 11-12

                An empty list is zero now.

``:class:``

.. code-version:: python
    :caption: average.py
    :class: km-tone-blue

    .. attempt::

        .. code::

            def average(numbers):
                return sum(numbers) / len(numbers)

        .. output:: broke

            >>> average([])
            ZeroDivisionError: division by zero

        Fine until a list comes in empty.

    .. attempt::

        .. code::

            def average(numbers):
                if not numbers:
                    return 0
                return sum(numbers) / len(numbers)

        .. output:: worked

            >>> average([])
            0

        .. lines:: 2-3

            An empty list is zero now.

.. code-block:: rst

    .. code-version:: python
        :caption: average.py
        :class: km-tone-blue

        .. attempt::

            .. code::

                def average(numbers):
                    return sum(numbers) / len(numbers)

            .. output:: broke

                >>> average([])
                ZeroDivisionError: division by zero

            Fine until a list comes in empty.

        .. attempt::

            .. code::

                def average(numbers):
                    if not numbers:
                        return 0
                    return sum(numbers) / len(numbers)

            .. output:: worked

                >>> average([])
                0

            .. lines:: 2-3

                An empty list is zero now.

No caption.

.. code-version:: python

    .. attempt::

        .. code::

            def average(numbers):
                return sum(numbers) / len(numbers)

        .. output:: broke

            >>> average([])
            ZeroDivisionError: division by zero

        Fine until a list comes in empty.

    .. attempt::

        .. code::

            def average(numbers):
                if not numbers:
                    return 0
                return sum(numbers) / len(numbers)

        .. output:: worked

            >>> average([])
            0

        .. lines:: 2-3

            An empty list is zero now.

.. code-block:: rst

    .. code-version:: python

        .. attempt::

            .. code::

                def average(numbers):
                    return sum(numbers) / len(numbers)

            .. output:: broke

                >>> average([])
                ZeroDivisionError: division by zero

            Fine until a list comes in empty.

        .. attempt::

            .. code::

                def average(numbers):
                    if not numbers:
                        return 0
                    return sum(numbers) / len(numbers)

            .. output:: worked

                >>> average([])
                0

            .. lines:: 2-3

                An empty list is zero now.

.. _combos-code-version-notes-and-outputs:

-------------------------------------------------------------------------------
Notes and outputs.
-------------------------------------------------------------------------------

An attempt's note is prose or a ``lines`` block, and its output is ``broke`` or
``worked``. This pair has neither:

.. code-version:: python
    :caption: plain.py

    .. attempt::

        .. code::

            x = 1

        A first attempt, with no output.

    .. attempt::

        .. code::

            x = 2

        A second attempt, with no output.

.. code-block:: rst

    .. code-version:: python
        :caption: plain.py

        .. attempt::

            .. code::

                x = 1

            A first attempt, with no output.

        .. attempt::

            .. code::

                x = 2

            A second attempt, with no output.

.. _combos-code-version-in-another-language:

-------------------------------------------------------------------------------
In another language.
-------------------------------------------------------------------------------

.. code-version:: javascript
    :caption: add.js

    .. attempt::

        .. code::

            const add = (a, b) => a - b;

        .. output:: broke

            add(2, 3) // -1

        A minus where a plus was meant.

    .. attempt::

        .. code::

            const add = (a, b) => a + b;

        .. output:: worked

            add(2, 3) // 5

        Fixed.

.. code-block:: rst

    .. code-version:: javascript
        :caption: add.js

        .. attempt::

            .. code::

                const add = (a, b) => a - b;

            .. output:: broke

                add(2, 3) // -1

            A minus where a plus was meant.

        .. attempt::

            .. code::

                const add = (a, b) => a + b;

            .. output:: worked

                add(2, 3) // 5

            Fixed.

.. _combos-code-version-with-icons:

-------------------------------------------------------------------------------
With icons.
-------------------------------------------------------------------------------

An icon first in the caption.

.. code-version:: python
    :caption: :fa-icon:solid:`flask` An icon before the caption

    .. attempt::

        .. code::

            def average(numbers):
                return sum(numbers) / len(numbers)

        .. output:: broke

            >>> average([])
            ZeroDivisionError: division by zero

        Fine until a list comes in empty.

    .. attempt::

        .. code::

            def average(numbers):
                if not numbers:
                    return 0
                return sum(numbers) / len(numbers)

        .. output:: worked

            >>> average([])
            0

        .. lines:: 2-3

            An empty list is zero now.

.. code-block:: rst

    .. code-version:: python
        :caption: :fa-icon:solid:`flask` An icon before the caption

        .. attempt::

            .. code::

                def average(numbers):
                    return sum(numbers) / len(numbers)

            .. output:: broke

                >>> average([])
                ZeroDivisionError: division by zero

            Fine until a list comes in empty.

        .. attempt::

            .. code::

                def average(numbers):
                    if not numbers:
                        return 0
                    return sum(numbers) / len(numbers)

            .. output:: worked

                >>> average([])
                0

            .. lines:: 2-3

                An empty list is zero now.

An icon last in the caption.

.. code-version:: python
    :caption: An icon after the caption :fa-icon:solid:`flask`

    .. attempt::

        .. code::

            def average(numbers):
                return sum(numbers) / len(numbers)

        .. output:: broke

            >>> average([])
            ZeroDivisionError: division by zero

        Fine until a list comes in empty.

    .. attempt::

        .. code::

            def average(numbers):
                if not numbers:
                    return 0
                return sum(numbers) / len(numbers)

        .. output:: worked

            >>> average([])
            0

        .. lines:: 2-3

            An empty list is zero now.

.. code-block:: rst

    .. code-version:: python
        :caption: An icon after the caption :fa-icon:solid:`flask`

        .. attempt::

            .. code::

                def average(numbers):
                    return sum(numbers) / len(numbers)

            .. output:: broke

                >>> average([])
                ZeroDivisionError: division by zero

            Fine until a list comes in empty.

        .. attempt::

            .. code::

                def average(numbers):
                    if not numbers:
                        return 0
                    return sum(numbers) / len(numbers)

            .. output:: worked

                >>> average([])
                0

            .. lines:: 2-3

                An empty list is zero now.

Icons in the notes.

.. code-version:: python
    :caption: average.py

    .. attempt::

        .. code::

            def average(numbers):
                return sum(numbers) / len(numbers)

        .. output:: broke

            >>> average([])
            ZeroDivisionError: division by zero

        :fa-icon:regular:`triangle-exclamation` Fine until a list
        comes in empty.

    .. attempt::

        .. code::

            def average(numbers):
                if not numbers:
                    return 0
                return sum(numbers) / len(numbers)

        .. output:: worked

            >>> average([])
            0

        .. lines:: 2-3

            :fa-icon:regular:`check` An empty list is zero
            now.

.. code-block:: rst

    .. code-version:: python
        :caption: average.py

        .. attempt::

            .. code::

                def average(numbers):
                    return sum(numbers) / len(numbers)

            .. output:: broke

                >>> average([])
                ZeroDivisionError: division by zero

            :fa-icon:regular:`triangle-exclamation` Fine until a list
            comes in empty.

        .. attempt::

            .. code::

                def average(numbers):
                    if not numbers:
                        return 0
                    return sum(numbers) / len(numbers)

            .. output:: worked

                >>> average([])
                0

            .. lines:: 2-3

                :fa-icon:regular:`check` An empty list is zero
                now.

.. _combos-code-version-with-roles:

-------------------------------------------------------------------------------
With roles.
-------------------------------------------------------------------------------

Roles in the notes.

.. code-version:: python
    :caption: average.py

    .. attempt::

        .. code::

            def average(numbers):
                return sum(numbers) / len(numbers)

        .. output:: broke

            >>> average([])
            ZeroDivisionError: division by zero

        Fine until a list comes in :sharpie:`empty`.

    .. attempt::

        .. code::

            def average(numbers):
                if not numbers:
                    return 0
                return sum(numbers) / len(numbers)

        .. output:: worked

            >>> average([])
            0

        .. lines:: 2-3

            An :underline:`empty` list is zero now, press
            :kbd:mac:`Cmd-K` and :swap:`read|write|run`.

.. code-block:: rst

    .. code-version:: python
        :caption: average.py

        .. attempt::

            .. code::

                def average(numbers):
                    return sum(numbers) / len(numbers)

            .. output:: broke

                >>> average([])
                ZeroDivisionError: division by zero

            Fine until a list comes in :sharpie:`empty`.

        .. attempt::

            .. code::

                def average(numbers):
                    if not numbers:
                        return 0
                    return sum(numbers) / len(numbers)

            .. output:: worked

                >>> average([])
                0

            .. lines:: 2-3

                An :underline:`empty` list is zero now, press
                :kbd:mac:`Cmd-K` and :swap:`read|write|run`.

.. _combos-code-version-where-it-cant-go:

-------------------------------------------------------------------------------
Where it can't go.
-------------------------------------------------------------------------------

A code-version belongs to the page itself, so in each of these the build stops.
The message is written under the source:

In an accordion
^^^^^^^^^^^^^^^

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. code-version:: python
            :caption: average.py

            .. attempt::

                .. code::

                    def average(numbers):
                        return sum(numbers) / len(numbers)

                .. output:: broke

                    >>> average([])
                    ZeroDivisionError: division by zero

                Fine until a list comes in empty.

            .. attempt::

                .. code::

                    def average(numbers):
                        if not numbers:
                            return 0
                        return sum(numbers) / len(numbers)

                .. output:: worked

                    >>> average([])
                    0

                .. lines:: 2-3

                    An empty list is zero now.

.. code-block:: text

    code-version: expected on the page itself, got it in an accordion

In a tab
^^^^^^^^

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

            .. code-version:: python
                :caption: average.py

                .. attempt::

                    .. code::

                        def average(numbers):
                            return sum(numbers) / len(numbers)

                    .. output:: broke

                        >>> average([])
                        ZeroDivisionError: division by zero

                    Fine until a list comes in empty.

                .. attempt::

                    .. code::

                        def average(numbers):
                            if not numbers:
                                return 0
                            return sum(numbers) / len(numbers)

                    .. output:: worked

                        >>> average([])
                        0

                    .. lines:: 2-3

                        An empty list is zero now.

        .. tab:: Another tab

            Nothing in this one.

.. code-block:: text

    code-version: expected on the page itself, got it in a tab

In a column
^^^^^^^^^^^

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top

        .. column::

            .. code-version:: python
                :caption: average.py

                .. attempt::

                    .. code::

                        def average(numbers):
                            return sum(numbers) / len(numbers)

                    .. output:: broke

                        >>> average([])
                        ZeroDivisionError: division by zero

                    Fine until a list comes in empty.

                .. attempt::

                    .. code::

                        def average(numbers):
                            if not numbers:
                                return 0
                            return sum(numbers) / len(numbers)

                    .. output:: worked

                        >>> average([])
                        0

                    .. lines:: 2-3

                        An empty list is zero now.

        .. column::

            Another column.

.. code-block:: text

    code-version: expected on the page itself, got it in a column

In a block
^^^^^^^^^^

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. code-version:: python
            :caption: average.py

            .. attempt::

                .. code::

                    def average(numbers):
                        return sum(numbers) / len(numbers)

                .. output:: broke

                    >>> average([])
                    ZeroDivisionError: division by zero

                Fine until a list comes in empty.

            .. attempt::

                .. code::

                    def average(numbers):
                        if not numbers:
                            return 0
                        return sum(numbers) / len(numbers)

                .. output:: worked

                    >>> average([])
                    0

                .. lines:: 2-3

                    An empty list is zero now.

.. code-block:: text

    code-version: expected on the page itself, got it in a block

In a note
^^^^^^^^^

.. code-block:: rst

    .. note::

        .. code-version:: python
            :caption: average.py

            .. attempt::

                .. code::

                    def average(numbers):
                        return sum(numbers) / len(numbers)

                .. output:: broke

                    >>> average([])
                    ZeroDivisionError: division by zero

                Fine until a list comes in empty.

            .. attempt::

                .. code::

                    def average(numbers):
                        if not numbers:
                            return 0
                        return sum(numbers) / len(numbers)

                .. output:: worked

                    >>> average([])
                    0

                .. lines:: 2-3

                    An empty list is zero now.

.. code-block:: text

    code-version: expected on the page itself, got it in a note

In a list item
^^^^^^^^^^^^^^

.. code-block:: rst

    - A list item that holds it:

      .. code-version:: python
          :caption: average.py

          .. attempt::

              .. code::

                  def average(numbers):
                      return sum(numbers) / len(numbers)

              .. output:: broke

                  >>> average([])
                  ZeroDivisionError: division by zero

              Fine until a list comes in empty.

          .. attempt::

              .. code::

                  def average(numbers):
                      if not numbers:
                          return 0
                      return sum(numbers) / len(numbers)

              .. output:: worked

                  >>> average([])
                  0

              .. lines:: 2-3

                  An empty list is zero now.

.. code-block:: text

    code-version: expected on the page itself, got it in a list

In a container
^^^^^^^^^^^^^^

.. code-block:: rst

    .. container:: wide

        .. code-version:: python
            :caption: average.py

            .. attempt::

                .. code::

                    def average(numbers):
                        return sum(numbers) / len(numbers)

                .. output:: broke

                    >>> average([])
                    ZeroDivisionError: division by zero

                Fine until a list comes in empty.

            .. attempt::

                .. code::

                    def average(numbers):
                        if not numbers:
                            return 0
                        return sum(numbers) / len(numbers)

                .. output:: worked

                    >>> average([])
                    0

                .. lines:: 2-3

                    An empty list is zero now.

.. code-block:: text

    code-version: expected on the page itself, got it in a container

.. _combos-code-version-what-a-note-can-hold:

-------------------------------------------------------------------------------
What a note can hold.
-------------------------------------------------------------------------------

A note holds paragraphs, lists, code, tables, figures, admonitions and buttons.
A directive that lays out a block of its own stops the build, and so does a
block of raw HTML or a walkthrough in another walkthrough's notes:

An accordion in a note
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. code-version:: python

        .. attempt::

            .. code::

                a = 1

            .. output:: broke

                1

            .. accordion:: An accordion

                Folded away until it opens.

        .. attempt::

            .. code::

                a = 2

            .. output:: worked

                2

            Fine.

.. code-block:: text

    accordion: expected somewhere else, got it in a code-version

Tabs in a note
^^^^^^^^^^^^^^

.. code-block:: rst

    .. code-version:: python

        .. attempt::

            .. code::

                a = 1

            .. output:: broke

                1

            .. tabs::

                .. tab:: First
                    :fa-icon: fa-regular fa-code

                    The first tab.

                .. tab:: Second

                    The second tab.

        .. attempt::

            .. code::

                a = 2

            .. output:: worked

                2

            Fine.

.. code-block:: text

    tabs: expected somewhere else, got it in a code-version

A video in a note
^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. code-version:: python

        .. attempt::

            .. code::

                a = 1

            .. output:: broke

                1

            .. video:: _static/combos/sample.webm
                :poster: _static/combos/poster.jpg
                :caption: A short clip.

        .. attempt::

            .. code::

                a = 2

            .. output:: worked

                2

            Fine.

.. code-block:: text

    video: expected somewhere else, got it in a code-version

Raw HTML in a note
^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. code-version:: python

        .. attempt::

            .. code::

                def average(numbers):
                    return sum(numbers) / len(numbers)

            .. output:: broke

                >>> average([])
                ZeroDivisionError: division by zero

            Fine until a list comes in empty.

        .. attempt::

            .. code::

                def average(numbers):
                    if not numbers:
                        return 0
                    return sum(numbers) / len(numbers)

            .. output:: worked

                >>> average([])
                0

            .. raw:: html

                <p>Some HTML.</p>

.. code-block:: text

    raw: expected somewhere else, got it in a code-version

A code-explain in a note
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. code-version:: python

        .. attempt::

            .. code::

                a = 1

            .. output:: broke

                1

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

        .. attempt::

            .. code::

                a = 2

            .. output:: worked

                2

            Fine.

.. code-block:: text

    code-explain: expected on the page itself, got it in a code-version
