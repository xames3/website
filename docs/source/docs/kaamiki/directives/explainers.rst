.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 19 October 2026
.. Last updated on: 23 November 2026

:km-page-title: code-explain and code-version
:km-page-description: Step a reader through a snippet line by line, with the
    values it held, or through the versions a piece of code went through.
:km-page-type: article
:km-header-subheader: Code stepped through as the notes scroll past
:km-feedback-title: Did watching the code help?
:km-feedback-description: Tell me what you'd change about how it walks through
    code.
:km-feedback-button: Tell me

.. _kaamiki-explainers:

===============================================================================
:fa-icon:regular:`list-check` code-explain and code-version
===============================================================================

.. rst-class:: km-text-lead

    Watch the code run, and watch it change.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3
    :shade: yellow

A ``code-explain`` steps a reader through a snippet, line by line, while the
notes beside it scroll past. For Python it runs the snippet at build time, once
the site has switched that on with :ref:`kaamiki.conf.code_explain.run
<kaamiki-settings-code-explain>`, and shows the values each line held, so they
are what the interpreter saw and not what you remembered. Scroll this one:

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

A ``code-explain`` needs a ``.. code::`` block and at least one
``.. lines::`` block. A snippet in any language is stepped through, but only
Python is run. For another language you write the values out by hand with
``:values:`` and ``:output:`` on a ``lines`` block. Something that's wrong
stops the build: a note that never comes up, a ``:watch:`` name the snippet
never sets, a snippet that raises without ``:raises:`` and a snippet that runs
past its limits.

A ``code-explain`` and a ``code-version`` go on the page itself, not in an
accordion, a tab, a column, a block, a note, a list or a container, and not in
each other's notes. They scroll their notes past the code when the window gives
them the width they're set to, ``--km-layout-explainer``, which is 835px.
They show the stacked view a phone gets when they're narrower,
for a reader who asks for less motion and on a page too short to scroll one to
the middle of the screen. A note holds paragraphs, lists, code, tables,
figures, admonitions and buttons, and nothing that lays out a block of its own
or can hold one, like a block of raw HTML. Any of those stops the build.

.. _kaamiki-code-explain-options:

-------------------------------------------------------------------------------
Options on code-explain.
-------------------------------------------------------------------------------

``:watch:`` names what to show, comma-separated, like ``total, self.x[0]``.
Without it only a function's return value and what the snippet raises show.
``:code-position:`` puts the code on the ``right`` (the default) or the
``left``. A ``lines`` block takes ``:at:``, ``:clear:``, ``:output:`` and
``:values:`` to write out what a language that isn't run shows, and a range
runs up, like ``2-3``, and has to sit inside the snippet.

.. accordion:: The full table

    .. list-table::
        :header-rows: 1
        :widths: 28 72

        * - Option
          - What it does
        * - ``:code-position:``
          - Which side the code holds: ``right`` (the default) or ``left``.
        * - ``:watch:``
          - Names to show, comma-separated, like ``total, self.x[0]``. Without
            it only a function's return value and what the snippet raises
            show.
        * - ``:limit:``
          - How many steps to show, from 1 to 300. It can lower
            ``kaamiki.conf.code_explain.limit`` but not go past it.
        * - ``:timeout:``
          - How long the snippet may run, in seconds, from 1 to 60 and never
            more than ``kaamiki.conf.code_explain.timeout``.
        * - ``:pythonpath:``
          - Directories to import from, comma-separated and relative to the
            document. One that isn't there stops the build.
        * - ``:events:``
          - Which of ``call``, ``line`` and ``return`` make a step.
        * - ``:comprehensions:``
          - Steps into comprehensions too.
        * - ``:pace:``
          - Pixels of scrolling a step takes, from 24 to 240.
        * - ``:raises:``
          - The snippet is meant to fail, so it ends on the exception.
        * - ``:comment:``
          - How a language Kaamiki doesn't know opens a comment and closes
            one, as ``#`` or ``(* *)``.
        * - ``:caption:``, ``:class:``, ``:name:``
          - A line of text above the code, extra classes and a name to link
            to.
        * - ``:no-motion:``
          - Plays nothing in it, as :ref:`every directive that moves takes it
            <kaamiki-directives-motion>`. The ``:pace:`` of a walkthrough is
            how far a step scrolls, so there's no ``:speed:`` here.
        * - ``:linenos:``, ``:lineno-start:``, ``:emphasize-lines:``
          - Numbers the lines, sets the number the first one gets, from 0 to
            10000, and highlights lines like ``1, 3-5``.

.. _kaamiki-code-version:

-------------------------------------------------------------------------------
Watch the code change.
-------------------------------------------------------------------------------

A ``code-version`` does the same for the versions a piece of code went through.
It shows them one after the other and turns each into the next as you scroll,
the lines on their way out going red and the new ones coming in green. Each
version is an ``.. attempt::`` with its own ``.. code::``, an optional
``.. output:: broke`` or ``worked`` and a note, as prose or ``.. lines::``:

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

.. _kaamiki-code-version-options:

-------------------------------------------------------------------------------
Options on code-version.
-------------------------------------------------------------------------------

It needs at least two attempts and a note. It takes ``:code-position:``,
``:pace:``, ``:caption:``, ``:class:``, ``:name:``, ``:linenos:`` and
``:lineno-start:``, which work as they do on ``code-explain``.

.. _kaamiki-explainers-limits:

-------------------------------------------------------------------------------
What runs.
-------------------------------------------------------------------------------

Running Python is off until a site sets ``kaamiki.conf.code_explain.run =
True``, and that needs a POSIX system like Linux or macOS. Without it a
code-explain in Python stops the build with an error that names the setting. A
code-explain in another language is never run, and neither is a code-version.
When it runs, the Python is in a scratch directory with a bare environment, 1GB
of memory for the whole run and 10 seconds. The memory is the total for every
process the run starts, and the build watches it as well as asking the system
to enforce it, so it's never skipped. That's its working directory and not a
sandbox: it runs as the user that builds the site, so it can write elsewhere
and reach the network. Build only pages whose snippets you trust. The
:ref:`code-explain settings <kaamiki-settings-code-explain>` set the limits,
and a trace is kept next to the doctrees and reused while the snippet, its
options, the interpreter and the installed packages stay the same. A run that
goes past a limit stops the build with a message like these:

.. code-block:: text

    code-explain: expected a snippet that runs, got a run that went past its
    10s
    code-explain: expected a snippet that runs, got a run that used more than
    1024 MB of memory

The script that drives both loads on the pages that have one and nowhere else.
