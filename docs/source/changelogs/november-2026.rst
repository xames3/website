.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 02 October 2026
.. Last updated on: 16 November 2026

:orphan:
:km-page-title: Kaamiki stops borrowing now!
:km-page-description: The November release of Kaamiki, the first one on PyPI.
    Why I stopped leaning on other people's work, what a reader meets first
    and how to install it.
:km-page-type: article
:km-feedback-title: Tell me what I broke with this release.
:km-feedback-description: If something's not right or missing options, I'd
    like to hear about it.
:km-feedback-button: Share feedback
:km-feedback-icon: fa-message-exclamation
:km-feedback-split:

.. _changelogs-november-2026:

===============================================================================
Kaamiki stops :swap:`borrowing|copying|depending|patching` now!
===============================================================================

.. rst-class:: km-text-lead

    The November release of Kaamiki, the first one on PyPI. These are the
    reasons I wrote directives that show code instead of describing it.

.. byline:: @xames3
    :avatar: https://i.imgur.com/hUhxigb.jpeg
    :target: https://github.com/xames3

This release started as a tidy-up and ended up touching nearly every file in
the theme. Most of it's the sort of change you only notice when it's missing,
which is how I like a theme to behave. The exceptions are the directives that
show code, a carousel and a set of building blocks that are Kaamiki's own.

.. block:: Release notes
    :preheader: :fa-icon:`tag` v2026.11.8
    :ref: v2026.11.8

    Two directives that show code instead of describing it, building blocks of
    my own, a carousel, cards that lead a reader on and a theme that loads the
    way Sphinx expects.

.. rubric:: :fa-icon:`sparkles` Things that are new
    :class: km-text-preheader

.. _the-code-suite:

-------------------------------------------------------------------------------
The ``code-*`` suite.
-------------------------------------------------------------------------------

.. rubric:: Because **"I don't follow"** is a fair thing for a student to say.
    :class: km-text-subheader

I wrote this for my students, who kept telling me they couldn't follow my code.
The ``code-explain`` directive steps a reader through a snippet a line at a
time, with the values each line left behind written beside it. The page
scrolls, the highlight moves along and that's all there is to it. Scroll this
one:

Python is run for real... So the values are what the interpreter saw and not
what I remembered. A rebuild doesn't run it again unless the snippet, the
interpreter or the installed packages changed. A snippet has limits on its
time, its memory and the files it writes. They're limits and not a sandbox, so
only run code you trust. Every other language is told rather than run, and you
write the values yourself.

Most of what I write about code is how it got to be the way it is. I used to
paste the final code and then a copy for every version underneath, which left
many readers diffing them in their head. The ``code-version`` directive shows
the versions one after the other and turns each into the next as you scroll,
the lines on their way out going red and the new ones coming in green:

.. _a-row-that-scrolls:

-------------------------------------------------------------------------------
A row that scrolls with ``carousel``.
-------------------------------------------------------------------------------

I kept stacking cards in a column because I had nowhere else to put them. A
``carousel`` holds blocks, figures, repositories, thumbnails and buttons in one
row that you swipe or step through with its arrows. It shows two cards and a
bit of the third so you know there's more, and ``:cards:`` picks anything from
one to four. It can run on its own in either direction and pauses the moment a
reader hovers, focuses or touches it. A column is too narrow for one, so a
carousel in a column stops the build. This one leads to the other pages of this
site:

.. rubric:: :fa-icon:`heart` You helped me a lot!
    :class: km-text-preheader

.. _goodbye-sphinx-design:

-------------------------------------------------------------------------------
Goodbye, ``sphinx-design``!
-------------------------------------------------------------------------------

.. rubric:: Things are Kaamiki native and they all look and feel the same.
    :class: km-text-subheader

Kaamiki leaned heavily on |sd|_ for all the
interactive bits like dropdowns, grids, cards and tabs. I restyled them to
match. That meant two sets of class names, a stylesheet I didn't write and a
theme that had to sniff a page for ``sd-`` before deciding what to load.

So I finally decided to write my own, one at a time, and kept them looking
the way they did:

.. list-table::
    :header-rows: 1

    * - sphinx-design
      - Kaamiki
    * - ``dropdown``
      - ``accordion``
    * - ``grid`` and ``grid-item``
      - ``columns`` and ``column``
    * - ``card``
      - ``block``
    * - ``tab-set`` and ``tab-item``
      - ``tabs`` and ``tab``

.. _words-can-change-now:

-------------------------------------------------------------------------------
Words can :swap:`change|move|swap|settle` now.
-------------------------------------------------------------------------------

I wanted the titles on my own pages to say what I'm doing, and what I'm doing
changes. The new ``:swap:`` role swaps one word for the next while it's on
screen, like the one in this page's title. Every letter of the old word rolls
into the letter of the new one, from the left, the way the greeting on the home
page does:

.. code-block:: rst

    Rebuilding NumPy to :swap:`understand|re-learn|appreciate` it.

Only what's in the page's content moves. The first word is what search, a
reader without scripting and every copy of a title get, so the navbar, the
sidebar, the breadcrumbs and a link read it as plain text.

I f*cking :fa-icon:solid:`heart km-tone--red` this role in particular!

.. _titles-can-sweep-now:

-------------------------------------------------------------------------------
Titles can :sweep:`sweep|shine|glide|change` now.
-------------------------------------------------------------------------------

``:swap:`` changes one word at a time. I wanted a whole title to change too, so
there's a second role, ``:sweep:``, where a band of light crosses the text and
the old words fade out behind it while the new ones come in through it. It
takes a whole title or just a word, so it works in a heading and in a sentence:

.. code-block:: rst

    :sweep:`Docs that teach|Code you can read and run`
    Docs you can :sweep:`read|search|share` with anyone.

It follows the same rules as ``:swap:``: the first phrase is what search, a
reader without scripting and every copy of a title get, and a reader who asks
for less motion sees nothing move. The light's colours are one CSS token, so
yours can be as quiet as you like.

.. rubric:: :fa-icon:`pen-slash` Fixing mistakes
    :class: km-text-preheader

.. _no-more-patching-sphinx:

-------------------------------------------------------------------------------
No more patching Sphinx.
-------------------------------------------------------------------------------

For the past few releases, Kaamiki used to patch Sphinx's configuration and its
HTML builder and it registered its directives the moment it was imported, so
``linkcheck`` and the other builders, which never load a theme, could still
find them. It worked, but only by side-effect. A theme built on top of Kaamiki
got none of its CSS and JS either, because the theme checked for its own name
rather than asking whose theme it was.

That was a bloody stupid mistake!

Now the theme loads the way Sphinx expects a theme to and behaves like it
should. Name it in ``html_theme`` and Sphinx finds its templates, styles and
scripts. Since Kaamiki provides its own set of custom directives and roles,
they act like any other Sphinx extension. So you list ``"kaamiki"`` in
``extensions`` as well, the same as any other extension:

.. code-block:: python

    extensions = ["kaamiki"]
    html_theme = "kaamiki"

Name one without the other, or another theme beside the extension, and the
build stops with an error that says what to change.

.. _every-page-leads-somewhere:

-------------------------------------------------------------------------------
Every page leads somewhere.
-------------------------------------------------------------------------------

A page used to end with a previous and a next button, which is a fine thing to
find at the end of a tutorial and a poor one at the end of everything else. A
page now ends with cards for the pages around it, in the order of the site. A
page that knows better names its own with ``:km-related-docs:`` and gives them
a heading with ``:km-related-header:``. The old buttons are still there for a
site that wants them.

.. _mistakes-stop-the-build:

-------------------------------------------------------------------------------
Mistakes stop the build.
-------------------------------------------------------------------------------

A directive in the wrong place used to build and look wrong, or not look like
anything. Now the build stops and names the line: a ``block`` inside a
``block``, a ``columns`` in a column that shares its row, a ``release`` that
isn't directly in a section, a link inside something that is a link already.
The same goes for an option or a setting outside the values it can take. The
message names the line and says what's wrong:

.. code-block:: text

    File "index.rst", line 6
        .. block:: Inner
        ^^^^^^^^^^^^^^^^
    kaamiki.KaamikiError: block: expected somewhere else, got it in a block

A video that's been deleted or made private since you wrote the page stops
``make linkcheck`` too. YouTube still serves a page for it, so the link checker
never noticed. :ref:`youtube <kaamiki-media-youtube>` and :ref:`thumbnail
<kaamiki-media-thumbnail>` now hand it the video's picture instead, which goes
with the video. The build stops and names the video's own link, however you
wrote it, with the file and the line it's on:

``extras/best-of-youtube.rst:231: [broken] https://www.youtube.com/watch?v=hoDLj0IzZMU: the video is deleted or private``

.. _a-page-shouldnt-wait-on-a-font:

-------------------------------------------------------------------------------
A page shouldn't wait on a font.
-------------------------------------------------------------------------------

A page used to stay hidden until everything on it had loaded. As Kaamiki relies
heavily on `Font Awesome`_ for its icons, one slow Font Awesome kit and the
reader stared at a blank screen. A page now shows as soon as its fonts are
ready and never waits more than two seconds, so a stalled kit can't keep it
blank. A browser without scripting never hides it at all.

Every icon the theme draws has a Pro icon and a Free one to stand in for it.
With a ``kaamiki.conf.icons.kit`` you get the Pro icons. Without one you get
Font Awesome Free, so a site with no kit draws every icon instead of empty
boxes. A name Free doesn't have stops the build and suggests the nearest one,
so a missing icon is never found by looking at the page.

The Pro+ packs work too. Each one has its own role, like
``:fa-icon:jelly:`house```, and an ``:icon:`` option takes
``fa-jelly fa-house`` the same way. A pack has only one style, so Kaamiki
writes it for you, and a style the pack doesn't have stops the build.
:ref:`The packs <kaamiki-roles-fa-icon-packs>` lists them all.

.. note::

    Put your own kit in ``kaamiki.conf.icons.kit``. The one in this site's
    ``conf.py`` is mine.

.. _players-that-respect-privacy:

-------------------------------------------------------------------------------
Players that respect privacy.
-------------------------------------------------------------------------------

A YouTube player shows the video's picture with a play button and loads when
you click it, from ``youtube-nocookie.com``. Nothing reaches YouTube until a
reader asks for the video. Both are on by default and a video can turn either
off for itself.

.. rubric:: :fa-icon:`gears` Smaller stuff, but a lot of it
    :class: km-text-preheader

.. _everything-of-mine-says-km:

-------------------------------------------------------------------------------
Everything of mine says ``km-*``.
-------------------------------------------------------------------------------

Every class, id and custom property Kaamiki owns starts with ``km-`` and so
does every field a page opens with. There's no guessing which classes are
Kaamiki's and which belong to Sphinx or an extension. An address is a
``url`` in every setting and field and a ``:target:`` in every option, with
``:doc:`` and ``:ref:`` for a page and a label.

.. _things-which-were-missing-from-day-one:

-------------------------------------------------------------------------------
Things which were missing from day one.
-------------------------------------------------------------------------------

Almost every directive had a fixed idea of how it'd be used and no way out of
it. A ``button`` opened a new tab if it left the site and you couldn't say
otherwise. A ``video`` took exactly one file. They have options now, and they
follow one rule: an option says what you want by being there, so ``:new-tab:``
opens a link in a new tab and ``:same-tab:`` keeps it in this one. No option
takes ``true`` or ``false``.

Things the templates had written in, like the reading speed, the toctree depth
and the logo size, are settings now, all under ``kaamiki.conf``. Most of the
``kaamiki.conf.show`` settings can be switched for one page with a
``:km-show-*:`` field, and the page wins over the site.

.. _light-dark-or-the-devices-own:

-------------------------------------------------------------------------------
Light, dark or the device's own.
-------------------------------------------------------------------------------

Kaamiki is dark by default and has a light side now. ``kaamiki.conf.mode``
takes ``"dark"``, ``"light"`` or ``"system"``. The first two are how the site
looks for every reader, whatever their device says, so it looks the way you
meant it to. ``"system"`` follows the reader's device and puts a button beside
the copyright that steps through light, dark and the device's own, so a reader
can pick for themselves. The pick is kept in their browser and wins over the
device. A site with two logos names them in ``kaamiki.conf.site.logos``, and a
single black or white logo turns itself the right way round.

.. _everything-moves-like-it-means-to:

-------------------------------------------------------------------------------
Motion that ends as gently as it starts.
-------------------------------------------------------------------------------

Accordions are springs now. Click one twice while it's opening and it brakes
and turns round from where it is, at the speed it was going, instead of
snapping. An accordion gets ready before the click, when a pointer comes near
it or the page is quiet, so opening a heavy one doesn't stall, and it comes to
rest while it's still moving a pixel or two a frame, so it never crawls
through its last pixels. The ticker's reels are moved by the browser, which
keeps the last digit from struggling as it stops, and ``:swap:`` rolls a word
into the next one a letter at a time, the way the greeting on the home page
does, while the box around it glides to its new width.

The header's dropdown leaves the way it came, and a reader who asks for less
motion gets things fading in and out, briefly, instead of nothing at all.

Smaller things move to match. The scroll-to-top button draws a ring as you read
down a page. Changing the colour mode spreads the new colours out from the
toggle, slowly, through a soft edge, in every browser. The navbar is the same
blurred glass in every mode, with a subtle line under it that fades in as you
scroll. Safari can't hold the blur while the colours spread, so there it drops
until they've settled. A phone's menu follows your finger when you pull it
shut, and a
quick flick shuts it from a short way. A carousel can show a dot for each card
in place of its arrows, with ``:dots:``, and a pill that stretches from one dot
to the next. A link's line draws across from the left as you rest the pointer
on it, a copy button's tick fades in over its icon and a release's line draws
itself down to the next. A ticker with no time of its own counts for 3.2
seconds, the site's speed, as a repository's numbers do, and now at their
card's ``:speed:``. A repository card's counts fade in and roll up when GitHub
answers,
:ref:`one after the other <kaamiki-repository-while-github-answers>`. The
picture behind a byline and the waves share one wider, taller box, and the
title sits a little lower in it.

A directive that moves can take its own speed with ``:speed:`` or play nothing
with ``:no-motion:``. ``2`` is twice as quick as the site, ``0.5`` half as
quick, and a ``:no-motion:`` accordion opens at once, with a ``:swap:`` or a
``:ticker:`` in it standing still. ``accordion``, ``tabs``, ``carousel``,
``byline``, ``repository`` and ``release`` take both, and ``code-explain`` and
``code-version`` take ``:no-motion:``.

``kaamiki.conf.motion.speed`` is a dial for every animation in the theme. The
default, ``0.625``, is calm, and ``1`` is 60% quicker. The page's content
follows its title straight away instead of waiting for the title to finish.
``kaamiki.conf.motion.page_transitions`` is off until you turn it on. With it,
following a link to another page of the site eases the old content out, and
when it has gone the new page plays its own entrance, from its first frame, in
Chrome and Safari for now. Never both at once, and the header, the sidebar and
the footer stay where they are. :ref:`Page to page
<kaamiki-example-motion-page-to-page>` shows how it goes.
``kaamiki.conf.motion.prefetch`` is on: the page a link leads to is fetched as
you reach for it, and the next and the previous pages once the page is quiet,
so following them is quick. :doc:`How Kaamiki moves
</docs/kaamiki/examples/motion>` has every one of these to try on a single
page.

.. _pictures-open-now:

-------------------------------------------------------------------------------
Pictures open now.
-------------------------------------------------------------------------------

A picture that's shown smaller than it is opens when you press it. It settles
out from where it sits to fit the screen, never bigger than it really is, as
the page dims behind it and its caption fades in once it has landed. It flies
back when you close it with Esc, a press outside it, the close button, a swipe
down or Back on a phone. Turn the phone or resize the window with it open and
it still finds its way home:

.. figure:: /_static/combos/poster.jpg
    :width: 240px
    :alt: A dark frame of a sample clip with five coloured circles

    Press it.

A picture that links, a video and a picture on a screen where it would come out
no bigger stay as they are, and ``km-no-enlarge`` leaves one alone.
``kaamiki.conf.media.enlarge`` turns it off for a site and
``:km-media-enlarge:`` for a page, as :ref:`settings <kaamiki-settings-media>`
and :ref:`page fields <kaamiki-page-fields-media>` explain. :ref:`How Kaamiki
moves <kaamiki-example-motion-a-picture-that-opens>` has it flying.

Pictures, figures, videos and the YouTube player stop at the text's 675px now,
where they used to break out wider than it. Only ``code-explain`` and
``code-version`` take more room, since code needs it. :doc:`Classes
</docs/kaamiki/classes>` has the rest.

.. _no-borders-one-font:

-------------------------------------------------------------------------------
No borders, one font.
-------------------------------------------------------------------------------

Borders are gone, except where a line does a job. Everything else stands apart
by its fill, lighter in the dark, so nothing sinks into an OLED screen's black.
The text is set in Inter and the font files come with the theme. Lists draw
their markers in rings, tabs are a rounded strip with a pill that slides to the
picked one and a long accordion or page folds up behind a Show more button.

.. _a-title-that-opens-the-page:

-------------------------------------------------------------------------------
A title that opens the page.
-------------------------------------------------------------------------------

The title, the lead and the byline sit on the left now and the byline is a
single row: the author, the reading time and the link to copy. The page's
language joins it when you ask with ``:show-language:``. Breadcrumbs only show
on a page that sits inside another, as the pages above it and then its own
name. There's no home link, since the logo goes home.

A page without a ``:backdrop:`` gets a faint glow behind its title, so the room
above it never looks empty. And a page loads in order, the byline, the title,
the lead and then each section below it, once. Nothing animates again as you
scroll.

.. _pages-that-stay-light:

-------------------------------------------------------------------------------
Pages that stay light.
-------------------------------------------------------------------------------

The header's dropdowns and a phone's menu list the branch you're reading and
keep the rest folded. That matters once a site has hundreds of pages, as every
page carries its own copy of the menu. A test site of 400 pages builds in 13
seconds and each page weighs 31 KB. Nothing you see changes.

Nothing scrolls sideways either. A table wider than the page scrolls inside its
own box and a long piece of inline code wraps. I checked every page of this
site at twelve widths, from a 320px phone to a 1920px desktop, and none of them
scrolled sideways.

.. URLs used and referenced above:

.. |sd| replace:: ``sphinx-design``
.. _sd: https://sphinx-design.readthedocs.io/en/latest/

.. _Font Awesome: https://fontawesome.com/
