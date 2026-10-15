.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 02 October 2026
.. Last updated on: 14 October 2026

:orphan:
:km-pg-title: Kaamiki 2026.10.28
:km-pg-description: What went into the October release of Kaamiki, what was
    wrong with the versions before it and how to use the new directives.
:km-pg-type: article

.. _changelog-october-2026:

===============================================================================
Loads through Sphinx alone
===============================================================================

.. rst-class:: km-lead

    What went into the October release and why most of it is invisible.

.. author:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :url: https://github.com/xames3

This release started as a tidy-up and ended up touching nearly every file in
the theme. Most of it is the sort of change you only notice when it's missing,
which is how I like a theme to behave. The exceptions are two new directives,
``walkthrough`` and ``attempts``, and a long list of options that directives
should have had from the start. The full list is in the
:ref:`changelog <2026.10.28>`; this is the story behind it.

I had planned this as 2026.10.5. By the time I'd stopped finding things to fix
and rewritten the walkthrough from scratch, the date was wrong, so it's
2026.10.28 instead.

-------------------------------------------------------------------------------
Sphinx and nothing else
-------------------------------------------------------------------------------

Kaamiki used to patch Sphinx's configuration and its HTML builder and it
registered its directives the moment it was imported, so ``linkcheck`` and the
other builders, which never load a theme, could still find them. It worked,
but only by side effect. A theme built on top of Kaamiki got none of its
stylesheets and scripts either, because the theme checked for its own name
rather than asking whose theme it was.

Now the theme loads the way Sphinx expects a theme to. Name it in
``html_theme`` and the HTML build has everything it needs. Run the other
builders too and you list ``"kaamiki"`` in ``extensions`` as well, the same as
any other extension:

.. code-block:: diff

    -import kaamiki  # registered the directives as a side effect
    -
     html_theme = "kaamiki"
    +extensions = ["kaamiki"]  # only if you run builders other than HTML

The directive templates are looked up through the builder's own loader now, so
a ``templates_path`` of your own can replace ``author.html.jinja`` the same way
it already replaced ``layout.html``.

-------------------------------------------------------------------------------
Pages that don't wait
-------------------------------------------------------------------------------

A page used to stay hidden until everything on it had loaded. One slow Font
Awesome kit and the reader stared at a blank screen. A page now shows the
moment the document is ready and a browser without scripting never hides it
at all.

A site without a ``fa_kit`` used to get no icons whatsoever, just empty boxes.
It gets Font Awesome Free now, and every icon the theme draws by default
exists in it.

-------------------------------------------------------------------------------
Everything with a ``km-*`` on it
-------------------------------------------------------------------------------

Every class, id and custom property the theme owns starts with ``km-`` and a
page's own fields are ``:km-pg-*:`` and ``:km-fb-*:``. That breaks old pages,
so check yours if they set ``:og:*:`` or ``:fb:*:`` fields. In return, there is
no guessing which classes are Kaamiki's and which belong to Sphinx or an
extension:

.. code-block:: diff
    :caption: conf.py

    -:og:title: Stepping through xsNumPy
    -:og:description: The xsNumPy story again, except you can watch it run
    -:fb:title: Does watching it run help?
    +:km-pg-title: Stepping through xsNumPy
    +:km-pg-description: The xsNumPy story again, except you can watch it run
    +:km-fb-title: Does watching it run help?

Along with it, anything that takes an address now calls it ``url``.
``header_buttons``, ``sidebar_buttons``, ``license`` and ``feedback`` were not
consistent about it, some said ``link`` and some said ``url``, and a typo
there failed quietly. If your ``conf.py`` has a ``"link"`` in any of them,
rename it:

.. code-block:: diff
    :caption: conf.py

     html_context = {
         "license": {
             "name": "CC BY 4.0",
    -        "link": "https://creativecommons.org/licenses/by/4.0/",
    +        "url": "https://creativecommons.org/licenses/by/4.0/",
         },
         "header_buttons": {
    -        "Check my availability": {"link": "#", "icon": "..."},
    +        "Check my availability": {"url": "#", "icon": "..."},
         },
     }

The ``mark`` role is ``sharpie`` for the same reason. The name described the
HTML element and not the thing it does:

.. code-block:: diff
    :caption: file.rst

    -This is :mark:`important`.
    +This is :sharpie:`important`.

-------------------------------------------------------------------------------
Walkthroughs
-------------------------------------------------------------------------------

The ``walkthrough`` directive steps a reader through a snippet a line at a
time, with the values each line left behind written beside it. The earlier
version of it was a pager, a "Step 3 of 9" counter and a pair of buttons. It
looked fine in a screenshot and was tedious to read, because a reader had to
stop scrolling to go forward and then start scrolling again to carry on. Worse,
it moved things around on the page with script, which jittered in Safari.

The new one is scrolling and nothing else. The page scrolls until the code is
in the middle of the screen, then the notes take over and each scroll moves
the highlight along, and when the last note has gone the page carries on. On
a phone, with reduced motion asked for or inside a folded page, none of that
happens and each note simply gets its own copy of the code above it.

A note is a ``.. lines::`` block, so there is one per thing worth saying:

.. code-block:: rst

    .. walkthrough:: python
        :caption: xsnumpy/_core.py
        :watch: shape, stride, strides
        :code-position: left

        .. setup::

            itemsize = 8

        .. code::

            def calc_strides(shape, itemsize):
                strides = []
                stride = itemsize
                for dim in reversed(shape):
                    strides.append(stride)
                    stride *= dim
                return tuple(reversed(strides))

            calc_strides((3, 4), itemsize)

        .. lines:: 4-6

            Then I walk the shape **backwards**.

Python is run for real, in a scratch directory with a bare environment, so the
values are what the interpreter saw and not what I remembered. It is also kept
next to the doctrees, so a rebuild doesn't run it again unless the snippet, the
interpreter or the installed packages changed. Every other language is told
rather than run, and you write the values yourself in ``:values:``:

.. code-block:: rst

    .. walkthrough:: c
        :caption: strides.c

        .. code::

            size_t offset = 2 * strides[0] + 1 * strides[1];
            double value = *(double *)(data + offset);

        .. lines:: 1
            :values: offset: 72

            ``(2, 1)`` is 2 x 32 + 1 x 8, which is **72 bytes** in.

        .. lines:: 2
            :values: value: 21.0

            Cast, dereference and out comes the 21.

Steps that would only move the highlight within a note that is already showing
are folded into the one before, so a reader never scrolls through a step that
changes nothing.

-------------------------------------------------------------------------------
Attempts
-------------------------------------------------------------------------------

Most of what I write about code is how it got to be the way it is, and that is
a story about the versions that didn't work. Until now I told it by pasting the
final code and then a smaller copy of it for every version underneath,
narrating my way through them. It works, sort of, but the reader has to diff
them in their head and I had to keep every copy in step by hand:

.. code-block:: rst

    The first version fell over the moment it met a 2D array:

    .. code-block:: python

        def __repr__(self):
            return f"array({self._data})"

    So I gave the 1D case its own branch:

    .. code-block:: python
        :emphasize-lines: 2-3

        def __repr__(self):
            if self.ndim == 1:
                return f"array({self._data})"

``attempts`` shows the versions one after the other and turns each into the
next as you scroll. The lines on their way out go red and the new ones come in
green. What an attempt printed lands under it once its notes have been read:

.. code-block:: rst

    .. attempts:: python
        :caption: xsnumpy/_core.py

        .. attempt::

            .. code::

                def __repr__(self):
                    return f"array({self._data})"

            .. output:: broke

                >>> array([[1, 2], [3, 4]])
                array([1, 2, 3, 4])

            Fine for scalars. Fell over the moment it met a 2D array.

        .. attempt::

            .. code::

                def __repr__(self):
                    if self.ndim == 1:
                        return f"array({self._data})"

            .. lines:: 2-3

                The 1D case keeps what already worked.

The same story is one block now, with the code, what it printed and the note
for each version kept together. Output is written by hand, because most of
these are fragments that would never run on their own. ``broke`` or ``worked``
after ``.. output::`` colours the box and that is all the verdict there is.

-------------------------------------------------------------------------------
Directives that do what you'd expect
-------------------------------------------------------------------------------

Almost every directive had a fixed idea of how it would be used and no way out
of it. A ``button`` opened a new tab if it left the site and you couldn't say
otherwise. A ``video`` took exactly one file. ``youtube`` always embedded the
player, so a page with three of them loaded three players before anyone
pressed play. They have options now:

.. code-block:: rst

    .. button:: https://xa.mes3.dev/changelog
        :scheme: green
        :fa-icon: arrow-right
        :fa-icon-position: after
        :no-new-tab:

        Read the changelog

    .. video:: _static/clip.mp4
        :sources: _static/clip.webm
        :poster: _static/clip.png
        :track: en=_static/clip.en.vtt, hi=_static/clip.hi.vtt
        :loop:
        :muted:

        A short clip, with captions in two languages.

    .. youtube:: https://www.youtube.com/watch?v=PhabJpIPONI
        :startfrom: 90
        :endat: 150
        :click-to-load:
        :privacy:

        Shows the video's picture and loads the player only once it is
        clicked.

``author`` takes ``:avatar-size:``, ``:interval:``, ``:hide-reading-time:``
and ``:hide-copy-url:``. ``embed`` can be told which hosts an ``<iframe>`` may
come from and ``thumbnail`` takes ``:grayscale:``. It used to be grey until
hovered whether you wanted that or not and it is drawn in colour now.

There is a ``release`` directive as well, the one writing this site's
changelog. It also takes an article, a date and a link:

.. code-block:: rst

    .. release:: 2026.10.28
        :title: Loads through Sphinx alone
        :article: changelogs/october-2026
        :article-label: Read release notes
        :url: https://github.com/xames3/website

        The biggest release yet.

        Added
            - A ``walkthrough`` directive.
            - An ``attempts`` directive.

A version that doesn't read as a date, ``v1.2.0`` say, no longer fails the
directive. It is shown without one, unless ``:date:`` gives it one.

-------------------------------------------------------------------------------
Settings and per-page switches
-------------------------------------------------------------------------------

Several things the templates had written in are settings now, the reading
speed, the toctree depth, the logo size, the hosts that count as the site and
the feedback box's words. One date format is used everywhere, from
``html_last_updated_fmt`` first and ``last_updated_on_fmt`` after it.

Any ``show_*`` setting can be turned off on a single page with a field, and
the page wins over the site:

.. code-block:: rst

    :km-show-feedback: false
    :km-show-toctree: false

Settings that are read while pages are read, ``button_scheme`` and
``walkthrough_limit`` among them, used to leave the old output in the saved
pages when you changed them. Sphinx only re-reads pages for settings it knows
about, and mine it didn't, so you had to build with ``-E`` and wonder why.
Changing one now sends every page back through reading.

The same goes for the buttons at the bottom of a page. Sphinx works out the
previous and next pages from the toctree, so a page that sits in none of them,
an orphan like this article, got neither and the reader had to find their way
back by hand. An article a ``release`` links to now goes back to the page the
release is on, which is how this one finds the changelog. Any other page can
name its own, as ``:doc:`` would write them, and the field wins over the
toctree:

.. code-block:: rst

    :orphan:
    :km-pg-prev: /changelog
    :km-pg-next: /changelogs/november-2026

The title of a neighbour is written into the page, so a page is read again
when a neighbour it names is retitled, moved or removed.

-------------------------------------------------------------------------------
The look
-------------------------------------------------------------------------------

Borders are gone, except where a line does a job. Everything else stands apart
by its fill, lighter in the dark, so nothing sinks into an OLED screen's black.
Lists draw their markers in rings, tabs are a rounded strip with a pill that
slides to the picked one, and a dropdown or a page that runs past a screenful
folds up with a Show more button. All of this is in the full
list and none of it needs anything from you.

-------------------------------------------------------------------------------
Before you upgrade
-------------------------------------------------------------------------------

- Kaamiki is dark only now. Delete ``colour_mode``, ``show_colour_modes``
  and the ``dark_mode`` and ``light_mode`` icons from your ``conf.py``, and
  rename the theme option ``dark_logo`` to ``logo``.
- Write ``:grayscale:`` on the thumbnails that should be grey, as
  ``thumbnail_grayscale`` is gone.
- Rename ``show_last_updated_on`` to ``show_page_last_updated`` and
  ``show_show_more`` to ``show_more``.
- Use ``:no-new-tab:`` for ``:same-tab:``, ``:hide-controls:`` for
  ``:controls: false``, ``:muted:`` for ``:mute:`` and ``:hide-stars:`` or
  ``:hide-forks:`` where ``:stars:`` or ``:forks:`` picked one.
- Rename ``link`` to ``url`` in ``header_buttons``, ``sidebar_buttons``,
  ``license`` and ``feedback``.
- Rename ``:og:*:`` and ``:fb:*:`` page fields to ``:km-pg-*:`` and
  ``:km-fb-*:``.
- Use ``:sharpie:`` where you used ``:mark:``.
- List ``"kaamiki"`` in ``extensions`` if you run builders other than HTML.
- Put the ``license`` back if you relied on the footer's old "CC BY 4.0",
  which every site got whether it was licensed that way or not.
- Load your cal.com script yourself, through ``html_js_files``. The theme
  doesn't ship a loader for one site's booking button:

  .. code-block:: diff

       html_static_path = ["_static"]
      +html_js_files = [("cal.js", {"defer": "defer"})]
