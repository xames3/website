.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 October 2026
.. Last updated on: 23 November 2026

:km-page-title: code-explain, option by option
:km-page-description: Every option of the code-explain directive on and off, in
    Python and in languages that are written out by hand, with icons and roles
    and where it can't go.
:km-page-type: article
:km-header-subheader: Every way to walk through code
:km-feedback-title: Did I miss a way to combine them?
:km-feedback-description: Tell me what you tried with code-explain that didn't
    work.
:km-feedback-button: Tell me
:km-feedback-icon: fa-list-check

.. _combos-code-explain:

===============================================================================
:fa-icon:regular:`list-check` code-explain, option by option
===============================================================================

.. rst-class:: km-text-lead

    Code stepped through, in every combination.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3
    :shade: yellow

A code-explain steps a reader through a snippet a line at a time, with the
values each line left behind. This page writes it with every option on and off,
in Python and in a language that's written out by hand, with icons and roles,
so the markup and the result sit side by side. It goes on the page itself, so
the containers it can't go in are written out at the end.

.. _combos-code-explain-the-options-one-at-a-time:

-------------------------------------------------------------------------------
The options, one at a time.
-------------------------------------------------------------------------------

``:watch:``, the one most snippets need.

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

.. code-block:: rst

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

``:watch:`` with two names.

.. code-explain:: python
    :caption: total.py
    :watch: total, i

    .. code::

        total = 0
        for i in range(3):
            total += i

    .. lines:: 1

        Start at zero.

    .. lines:: 2-3

        Add each number in turn.

.. code-block:: rst

    .. code-explain:: python
        :caption: total.py
        :watch: total, i

        .. code::

            total = 0
            for i in range(3):
                total += i

        .. lines:: 1

            Start at zero.

        .. lines:: 2-3

            Add each number in turn.

``:code-position: left``

.. code-explain:: python
    :caption: total.py
    :watch: total
    :code-position: left

    .. code::

        total = 0
        for i in range(3):
            total += i

    .. lines:: 1

        Start at zero.

    .. lines:: 2-3

        Add each number in turn.

.. code-block:: rst

    .. code-explain:: python
        :caption: total.py
        :watch: total
        :code-position: left

        .. code::

            total = 0
            for i in range(3):
                total += i

        .. lines:: 1

            Start at zero.

        .. lines:: 2-3

            Add each number in turn.

``:limit: 4``, the most steps the snippet may take. A snippet with more stops
the build.

.. code-explain:: python
    :caption: total.py
    :watch: total
    :limit: 4

    .. code::

        total = 0
        for i in range(3):
            total += i

    .. lines:: 1

        Start at zero.

    .. lines:: 2-3

        Add each number in turn.

.. code-block:: rst

    .. code-explain:: python
        :caption: total.py
        :watch: total
        :limit: 4

        .. code::

            total = 0
            for i in range(3):
                total += i

        .. lines:: 1

            Start at zero.

        .. lines:: 2-3

            Add each number in turn.

``:timeout: 5``

.. code-explain:: python
    :caption: total.py
    :watch: total
    :timeout: 5

    .. code::

        total = 0
        for i in range(3):
            total += i

    .. lines:: 1

        Start at zero.

    .. lines:: 2-3

        Add each number in turn.

.. code-block:: rst

    .. code-explain:: python
        :caption: total.py
        :watch: total
        :timeout: 5

        .. code::

            total = 0
            for i in range(3):
                total += i

        .. lines:: 1

            Start at zero.

        .. lines:: 2-3

            Add each number in turn.

``:events:``, with ``call``, ``line`` and ``return`` all making a step.

.. code-explain:: python
    :caption: total.py
    :watch: total
    :events: call, line, return

    .. code::

        total = 0
        for i in range(3):
            total += i

    .. lines:: 1

        Start at zero.

    .. lines:: 2-3

        Add each number in turn.

.. code-block:: rst

    .. code-explain:: python
        :caption: total.py
        :watch: total
        :events: call, line, return

        .. code::

            total = 0
            for i in range(3):
                total += i

        .. lines:: 1

            Start at zero.

        .. lines:: 2-3

            Add each number in turn.

``:pace: 160``, pixels of scrolling a step takes.

.. code-explain:: python
    :caption: total.py
    :watch: total
    :pace: 160

    .. code::

        total = 0
        for i in range(3):
            total += i

    .. lines:: 1

        Start at zero.

    .. lines:: 2-3

        Add each number in turn.

.. code-block:: rst

    .. code-explain:: python
        :caption: total.py
        :watch: total
        :pace: 160

        .. code::

            total = 0
            for i in range(3):
                total += i

        .. lines:: 1

            Start at zero.

        .. lines:: 2-3

            Add each number in turn.

``:linenos:``

.. code-explain:: python
    :caption: total.py
    :watch: total
    :linenos:

    .. code::

        total = 0
        for i in range(3):
            total += i

    .. lines:: 1

        Start at zero.

    .. lines:: 2-3

        Add each number in turn.

.. code-block:: rst

    .. code-explain:: python
        :caption: total.py
        :watch: total
        :linenos:

        .. code::

            total = 0
            for i in range(3):
                total += i

        .. lines:: 1

            Start at zero.

        .. lines:: 2-3

            Add each number in turn.

``:lineno-start: 10``, so the notes name lines 10 to 12.

.. code-explain:: python
    :caption: total.py
    :watch: total
    :linenos:
    :lineno-start: 10

    .. code::

        total = 0
        for i in range(3):
            total += i

    .. lines:: 10

        Start at zero.

    .. lines:: 11-12

        Add each number in turn.

.. code-block:: rst

    .. code-explain:: python
        :caption: total.py
        :watch: total
        :linenos:
        :lineno-start: 10

        .. code::

            total = 0
            for i in range(3):
                total += i

        .. lines:: 10

            Start at zero.

        .. lines:: 11-12

            Add each number in turn.

``:emphasize-lines: 3``

.. code-explain:: python
    :caption: total.py
    :watch: total
    :emphasize-lines: 3

    .. code::

        total = 0
        for i in range(3):
            total += i

    .. lines:: 1

        Start at zero.

    .. lines:: 2-3

        Add each number in turn.

.. code-block:: rst

    .. code-explain:: python
        :caption: total.py
        :watch: total
        :emphasize-lines: 3

        .. code::

            total = 0
            for i in range(3):
                total += i

        .. lines:: 1

            Start at zero.

        .. lines:: 2-3

            Add each number in turn.

``:class:``

.. code-explain:: python
    :caption: total.py
    :watch: total
    :class: km-tone-blue

    .. code::

        total = 0
        for i in range(3):
            total += i

    .. lines:: 1

        Start at zero.

    .. lines:: 2-3

        Add each number in turn.

.. code-block:: rst

    .. code-explain:: python
        :caption: total.py
        :watch: total
        :class: km-tone-blue

        .. code::

            total = 0
            for i in range(3):
                total += i

        .. lines:: 1

            Start at zero.

        .. lines:: 2-3

            Add each number in turn.

``:comprehensions:``, which steps into the comprehension.

.. code-explain:: python
    :caption: squares.py
    :watch: squares
    :comprehensions:

    .. code::

        squares = [n * n for n in range(3)]

    .. lines:: 1

        The comprehension builds a list.

.. code-block:: rst

    .. code-explain:: python
        :caption: squares.py
        :watch: squares
        :comprehensions:

        .. code::

            squares = [n * n for n in range(3)]

        .. lines:: 1

            The comprehension builds a list.

``:raises:``, for a snippet that's meant to fail.

.. code-explain:: python
    :caption: boom.py
    :raises:

    .. code::

        values = [1, 2]
        values[5]

    .. lines:: 1

        A list of two.

    .. lines:: 2

        There's no sixth item, so this raises.

.. code-block:: rst

    .. code-explain:: python
        :caption: boom.py
        :raises:

        .. code::

            values = [1, 2]
            values[5]

        .. lines:: 1

            A list of two.

        .. lines:: 2

            There's no sixth item, so this raises.

Without ``:watch:`` only a function's return value shows.

.. code-explain:: python
    :caption: double.py

    .. code::

        def double(x):
            return x * 2

        double(21)

    .. lines:: 1-2

        A function.

    .. lines:: 4

        Call it.

.. code-block:: rst

    .. code-explain:: python
        :caption: double.py

        .. code::

            def double(x):
                return x * 2

            double(21)

        .. lines:: 1-2

            A function.

        .. lines:: 4

            Call it.

.. _combos-code-explain-languages-that-are-not-run:

-------------------------------------------------------------------------------
Languages that aren't run.
-------------------------------------------------------------------------------

Only Python is run. Any other language is stepped through with the values
written out by hand in ``:values:`` and ``:output:``, and ``:comment:`` says
how it opens a comment:

A language that isn't run, written out by hand.

.. code-explain:: javascript
    :caption: count.js

    .. code::

        let n = 1;
        n += 1;
        console.log(n);

    .. lines:: 1
        :values: n: 1

        Start.

    .. lines:: 2-3
        :values: n: 2
        :output: 2

        Then.

.. code-block:: rst

    .. code-explain:: javascript
        :caption: count.js

        .. code::

            let n = 1;
            n += 1;
            console.log(n);

        .. lines:: 1
            :values: n: 1

            Start.

        .. lines:: 2-3
            :values: n: 2
            :output: 2

            Then.

The same, in C.

.. code-explain:: c
    :caption: count.c

    .. code::

        int i = 0;
        i += 2;

    .. lines:: 1
        :values: i: 0

        Start.

    .. lines:: 2
        :values: i: 2

        Add two.

.. code-block:: rst

    .. code-explain:: c
        :caption: count.c

        .. code::

            int i = 0;
            i += 2;

        .. lines:: 1
            :values: i: 0

            Start.

        .. lines:: 2
            :values: i: 2

            Add two.

A language Kaamiki doesn't know, with ``:comment:``.

.. code-explain:: lisp
    :caption: add.lisp
    :comment: ;

    .. code::

        (setq total 0)
        (setq total (+ total 2))

    .. lines:: 1
        :values: total: 0

        Start.

    .. lines:: 2
        :values: total: 2

        Add two.

.. code-block:: rst

    .. code-explain:: lisp
        :caption: add.lisp
        :comment: ;

        .. code::

            (setq total 0)
            (setq total (+ total 2))

        .. lines:: 1
            :values: total: 0

            Start.

        .. lines:: 2
            :values: total: 2

            Add two.

.. _combos-code-explain-with-icons:

-------------------------------------------------------------------------------
With icons.
-------------------------------------------------------------------------------

An icon first in the caption, which replaces the language's.

.. code-explain:: python
    :caption: :fa-icon:solid:`flask` An icon before the caption
    :watch: total

    .. code::

        total = 0
        for i in range(3):
            total += i

    .. lines:: 1

        Start at zero.

    .. lines:: 2-3

        Add each number in turn.

.. code-block:: rst

    .. code-explain:: python
        :caption: :fa-icon:solid:`flask` An icon before the caption
        :watch: total

        .. code::

            total = 0
            for i in range(3):
                total += i

        .. lines:: 1

            Start at zero.

        .. lines:: 2-3

            Add each number in turn.

An icon last in the caption.

.. code-explain:: python
    :caption: An icon after the caption :fa-icon:solid:`flask`
    :watch: total

    .. code::

        total = 0
        for i in range(3):
            total += i

    .. lines:: 1

        Start at zero.

    .. lines:: 2-3

        Add each number in turn.

.. code-block:: rst

    .. code-explain:: python
        :caption: An icon after the caption :fa-icon:solid:`flask`
        :watch: total

        .. code::

            total = 0
            for i in range(3):
                total += i

        .. lines:: 1

            Start at zero.

        .. lines:: 2-3

            Add each number in turn.

No icon of your own: the language's icon is drawn.

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

.. code-block:: rst

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

Icons in the notes.

.. code-explain:: python
    :caption: total.py
    :watch: total

    .. code::

        total = 0
        for i in range(3):
            total += i

    .. lines:: 1

        Start at :fa-icon:regular:`flag` zero.

    .. lines:: 2-3

        :fa-icon:regular:`plus` Add each number.

.. code-block:: rst

    .. code-explain:: python
        :caption: total.py
        :watch: total

        .. code::

            total = 0
            for i in range(3):
                total += i

        .. lines:: 1

            Start at :fa-icon:regular:`flag` zero.

        .. lines:: 2-3

            :fa-icon:regular:`plus` Add each number.

.. _combos-code-explain-with-roles:

-------------------------------------------------------------------------------
With roles.
-------------------------------------------------------------------------------

Roles in the notes.

.. code-explain:: python
    :caption: total.py
    :watch: total

    .. code::

        total = 0
        for i in range(3):
            total += i

    .. lines:: 1

        Start at :sharpie:`zero`.

    .. lines:: 2-3

        Add each :underline:`number` in
        :roll:`turn|order|sequence`, press :kbd:mac:`Cmd-K`.

.. code-block:: rst

    .. code-explain:: python
        :caption: total.py
        :watch: total

        .. code::

            total = 0
            for i in range(3):
                total += i

        .. lines:: 1

            Start at :sharpie:`zero`.

        .. lines:: 2-3

            Add each :underline:`number` in
            :roll:`turn|order|sequence`, press :kbd:mac:`Cmd-K`.

.. _combos-code-explain-where-it-cant-go:

-------------------------------------------------------------------------------
Where it can't go.
-------------------------------------------------------------------------------

A code-explain belongs to the page itself, so in each of these the build stops.
The message is written under the source:

In an accordion
^^^^^^^^^^^^^^^

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

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

.. code-block:: text

    code-explain: expected on the page itself, got it in an accordion

In a tab
^^^^^^^^

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

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

        .. tab:: Another tab

            Nothing in this one.

.. code-block:: text

    code-explain: expected on the page itself, got it in a tab

In a column
^^^^^^^^^^^

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top

        .. column::

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

        .. column::

            Another column.

.. code-block:: text

    code-explain: expected on the page itself, got it in a column

In a block
^^^^^^^^^^

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

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

.. code-block:: text

    code-explain: expected on the page itself, got it in a block

In a note
^^^^^^^^^

.. code-block:: rst

    .. note::

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

.. code-block:: text

    code-explain: expected on the page itself, got it in a note

In a list item
^^^^^^^^^^^^^^

.. code-block:: rst

    - A list item that holds it:

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

.. code-block:: text

    code-explain: expected on the page itself, got it in a list

In a container
^^^^^^^^^^^^^^

.. code-block:: rst

    .. container:: wide

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

.. code-block:: text

    code-explain: expected on the page itself, got it in a container

.. _combos-code-explain-what-a-note-can-hold:

-------------------------------------------------------------------------------
What a note can hold.
-------------------------------------------------------------------------------

A note holds paragraphs, lists, code, tables, figures, admonitions and buttons.
A directive that lays out a block of its own stops the build, and so does a
block of raw HTML or a walkthrough in another walkthrough's notes:

An accordion in a note
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. code-explain:: python

        .. code::

            total = 0

        .. lines:: 1

            .. accordion:: An accordion

                Folded away until it opens.

.. code-block:: text

    accordion: expected outside a code-explain, a code-version and a block that
    links, got it in a code-explain

Tabs in a note
^^^^^^^^^^^^^^

.. code-block:: rst

    .. code-explain:: python

        .. code::

            total = 0

        .. lines:: 1

            .. tabs::

                .. tab:: First
                    :fa-icon: fa-regular fa-code

                    The first tab.

                .. tab:: Second

                    The second tab.

.. code-block:: text

    tabs: expected outside a code-explain, a code-version, a block that links,
    a tab and a table, got it in a code-explain

A video in a note
^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. code-explain:: python

        .. code::

            total = 0

        .. lines:: 1

            .. video:: _static/combos/sample.webm
                :poster: _static/combos/poster.jpg
                :caption: A short clip.

.. code-block:: text

    video: expected outside a code-explain, a code-version and a block that
    links, got it in a code-explain

Raw HTML in a note
^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. code-explain:: python

        .. code::

            total = 0

        .. lines:: 1

            .. raw:: html

                <p>Some HTML.</p>

.. code-block:: text

    raw: expected outside a code-explain and a code-version, got it in a
    code-explain

A code-version in a note
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst

    .. code-explain:: python

        .. code::

            total = 0

        .. lines:: 1

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

    code-version: expected on the page itself, got it in a code-explain
