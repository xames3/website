.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 11 November 2026
.. Last updated on: 18 November 2026

:km-page-title: How Kaamiki moves
:km-page-description: Every animation in Kaamiki, shown working in one
    document, with something to press, drag or scroll for each.
:km-page-type: article
:km-header-subheader: Every animation, in one document
:km-feedback-title: Did anything feel off?
:km-feedback-description: Tell me which animation felt rushed, jerky or too
    slow.
:km-feedback-button: Tell me
:km-feedback-split:
:km-show-scrolltop:

.. _kaamiki-example-motion:

===============================================================================
How Kaamiki moves
===============================================================================

.. rst-class:: km-text-lead

    Every animation in the theme, shown working in a document that reads like
    any other.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3
    :backdrop: https://i.imgur.com/JOBRcgT.jpg,
        https://i.imgur.com/hUhxigb.jpeg,
        https://i.imgur.com/gcGHqxi.jpg,
        https://i.imgur.com/weM4qDW.jpg

This page is a tour of how Kaamiki moves. Nothing on it is a demo in a box:
each animation turns up where you'd really use it, inside a paragraph, a list
or a table, with the other directives around it. Each section says what to
press, drag, hover or scroll, and the table under :ref:`Folding things away
<kaamiki-example-motion-folding-things-away>` gathers all of them in one place.

Two things change how everything below feels. The first is the speed. Every
animation takes its time from one number, ``kaamiki.conf.motion.speed``, and
the default is ``1``. The second is your device: a reader who asks
for less motion gets the calmer version. Both are on the :ref:`settings page
<kaamiki-settings-motion>`.

.. _kaamiki-example-motion-arriving-on-a-page:

-------------------------------------------------------------------------------
Arriving on a page.
-------------------------------------------------------------------------------

When a page loads it comes in once and in order: the byline, the title, the
lead and then each section below it. Nothing animates again as you scroll, so
the page never moves under you while you read. Reload this one and watch the
top of it:

.. button::
    :doc: /docs/kaamiki/examples/motion
    :fa-icon: fa-solid fa-rotate-right

    Reload this page

Behind the byline the pictures take turns and the waves drift. It's the one
motion that never stops, so it pauses for a reader who asks for less motion.

.. _kaamiki-example-motion-a-long-page-folded:

-------------------------------------------------------------------------------
A long page, folded.
-------------------------------------------------------------------------------

A page that takes five minutes or more to read folds behind a *Show more*
button, so a long one doesn't open as a wall of text. This page is long enough,
so you're probably reading it through that window. Press *Show more* when you
reach it and then *Show less*, which folds the page back up and takes you with
it.

Once you've scrolled down, move back up a little. A round button comes in at
the corner of the screen and a ring around it fills as you read down the page.
Press it and you're taken to the top. The site keeps it off, so this page's
source turns it on with one field:

.. code-block:: rst

    :km-show-scrolltop:

.. _kaamiki-example-motion-folding-things-away:

-------------------------------------------------------------------------------
Folding things away.
-------------------------------------------------------------------------------

An accordion folds content away under a title. Open one and close it, then
press it again halfway through: it turns round from where it is and doesn't
jump. A long one, like the table below, opens just as smoothly, because the
page gets it ready as your pointer comes near.

.. accordion:: What's the dial?

    It's ``kaamiki.conf.motion.speed``, one number from ``0.25`` to ``4`` that
    sets the speed of every animation in the theme. ``1`` is the default
    and ``2`` is twice as quick.

.. accordion:: Every animation on this page

    .. list-table::
        :header-rows: 1
        :widths: 30 30 40

        * - Animation
          - Where
          - What to do
        * - A page coming in
          - The top of any page
          - Reload the page.
        * - The pictures and waves
          - Behind the byline
          - Wait a few seconds.
        * - *Show more* and *Show less*
          - The fold of this page
          - Press either one.
        * - The ring on the back-to-top button
          - The corner of the screen
          - Scroll down, then up a little.
        * - An accordion
          - This section
          - Open one and close it halfway through.
        * - Tabs
          - Choosing between things
          - Pick a tab.
        * - A carousel
          - Choosing between things
          - Swipe it or press an arrow.
        * - A carousel with dots
          - Choosing between things
          - Swipe it or press a dot.
        * - Letters that roll into the next word
          - Words and numbers that move
          - Wait for the last word.
        * - A phrase wiped out and replaced
          - Words and numbers that move
          - Wait for the light to cross it.
        * - Numbers that count
          - Words and numbers that move
          - Scroll them into view.
        * - A highlighter and a pencil line
          - Words and numbers that move
          - Scroll them into view.
        * - A quote typed as it's said
          - Words and numbers that move
          - Scroll it into view.
        * - A greeting and a typed line
          - Words and numbers that move
          - Watch them for a few seconds.
        * - Cards and buttons
          - Cards, buttons and links
          - Hover them.
        * - The arrow on a chevron button
          - Cards, buttons and links
          - Hover *Install it*.
        * - The line under a link
          - Cards, buttons and links
          - Hover a link in the text.
        * - A page fetched ahead
          - Cards, buttons and links
          - Rest your pointer on a link.
        * - The header's dropdowns
          - Moving around the site
          - Open one in a wide window.
        * - The header's search
          - Moving around the site
          - Press it.
        * - A change of colours
          - Moving around the site
          - Press the colour button.
        * - The phone menu
          - Moving around the site
          - Open it in a narrow window and pull it shut.
        * - Numbers on a repository card
          - Projects and releases
          - Scroll the cards into view, on a slow network to see them wait.
        * - The line between releases
          - Projects and releases
          - Scroll the releases into view.
        * - A video starting
          - A picture that becomes a player
          - Press play.
        * - A picture opening and closing
          - A picture that opens
          - Press it, then Esc, a press outside it or a swipe down.
        * - The copy button
          - Copying code
          - Hover a code block and press it.
        * - Code that runs
          - The end of the page
          - Scroll through it.
        * - Code that changes
          - The end of the page
          - Scroll through it.
        * - A directive at its own speed
          - A directive at its own speed
          - Open the accordions and compare them.
        * - A directive that plays nothing
          - A directive at its own speed
          - Open the last accordion.
        * - A page handing over to the next
          - Page to page
          - Follow a link, on a site that has it on.

.. accordion:: More about the speed

    The dial is *site-wide*. A reader can't change it, but their device can,
    and that always wins.

    .. accordion:: And when a reader asks for less?

        They get things fading in and out, briefly, and the loops stop: the
        words stay on the first one and the numbers show at once.

.. _kaamiki-example-motion-choosing-between-things:

-------------------------------------------------------------------------------
Choosing between things.
-------------------------------------------------------------------------------

Tabs show one thing at a time. A pill slides to the tab you pick and its panel
rises in as the old one leaves. This set is a real one: it's how you'd set the
speed:

.. tabs::

    .. tab:: conf.py

        .. code-block:: python

            kaamiki.conf.motion.speed = 1

    .. tab:: Command line

        .. code-block:: console

            $ sphinx-build -b html -D kaamiki_motion_speed=1 \
                docs/source docs/build

    .. tab:: A reader's device

        Nothing to set. Whatever number you choose, a reader who asks their
        device for less motion gets the calmer version.

A carousel is a row of cards with the next one peeking in. Swipe it, scroll it
or use the arrows, which grey out at each end:

.. carousel:: Where to go next.

    .. block:: Accordion
        :size: small
        :doc: ../directives/accordion

        Content that folds away under a title.

    .. block:: Tabs
        :size: small
        :doc: ../directives/tabs

        One block of content at a time.

    .. block:: Carousel
        :size: small
        :doc: ../directives/carousel

        A row of cards to swipe through.

    .. block:: Roles
        :size: small
        :doc: ../roles

        Words that move, glow and count.

    .. block:: Settings
        :size: small
        :doc: ../settings

        What you can change in ``conf.py``.

    .. block:: Combinations
        :size: small
        :doc: ../combinations/index

        Every directive inside every other.

With ``:dots:`` a dot stands for each card in place of the arrows. A pill sits
on the dot of the card you're at and stretches out to the next one when the row
moves, then settles on it. A tap on a dot goes to its card:

.. carousel::
    :dots:

    .. block:: Page fields
        :size: small
        :doc: ../page-fields

        Change a link preview, the feedback box or the layout for one page.

    .. block:: Advanced
        :size: small
        :doc: ../advanced

        Custom properties, template overrides and what a build writes.

    .. block:: Installing
        :size: small
        :doc: ../installation

        One package, named twice in your ``conf.py``.

    .. block:: Directives
        :size: small
        :doc: ../directives/index

        Every directive, shown working.

.. _kaamiki-example-motion-words-and-numbers-that-move:

-------------------------------------------------------------------------------
Words and numbers that move.
-------------------------------------------------------------------------------

Some of the motion is in the words. The sentence below rolls its last word into
the next one by itself, a letter at a time from the left, the way the greeting
on the home page does, and the numbers in it count up when they scroll into
view:

Everything here is meant to :swap:`settle|glide|ease|land` softly, on
:ticker:`8` paces and :ticker:`4` curves.

.. code-block:: rst

    Everything here is meant to :swap:`settle|glide|ease|land` softly, on
    :ticker:`8` paces and :ticker:`4` curves.

The rest of the sentence glides to wherever the new word leaves it, and a word
of another length sends the extra letters in from or out to nothing, as in
:swap:`go|going|forgotten`. The :ref:`swap role <kaamiki-roles-swap>` says what
it takes and what it leaves alone.

A number can be written short, so :ticker:`12400?short` reads in thousands.
Left alone it counts for as long as the site's speed says, 2 seconds, and it
can take its own time, as :ticker:`1900?duration=1s` does.

``:sweep:`` changes a whole phrase instead of a word. A band of light crosses
the text, the old phrase fades out behind it and the new one comes in through
it, and whatever sits below glides to the new height if the phrase wraps
differently:

.. rst-class:: km-text-lead

    :sweep:`One document|Every animation|All of it live`

.. code-block:: rst

    :sweep:`One document|Every animation|All of it live`

Marks draw themselves too. A :sharpie:`highlighter` sweeps across the words and
a :underline:`pencil line <blue>` is drawn beneath them, both as they come into
view.

A quote is typed out the way it's said, and the words that sound like others
are corrected a moment later, which is what speech-to-text does. This is the
line from the :doc:`home page </index>`:

.. epigraph::

    If you want to master something, teach it.

The two embeds below came from the home page too. A greeting changes by itself
and a line types and deletes as if someone were writing it:

.. embed:: /assets/html/greetings.html
    :source: /_static/data/greetings.json
    :interval: 2800
    :duration: 700
    :stagger: 45
    :js: styles/site.js

So far, I've taught...

.. embed:: /assets/html/currently-teaching.html
    :source: /_static/data/currently-teaching.json
    :prefix-text:
    :typing-speed: 120
    :deleting-speed: 80
    :pause-after-typing: 2000
    :pause-after-deleting: 1000
    :js: styles/site.js

.. _kaamiki-example-motion-cards-buttons-and-links:

-------------------------------------------------------------------------------
Cards, buttons and links.
-------------------------------------------------------------------------------

Cards and buttons answer your pointer with a change of colour and nothing else,
so the page feels alive without anything shifting under it. Hover these:

.. columns:: 2
    :flush:
    :valign: top

    .. column::

        .. block:: Page fields
            :size: small
            :doc: ../page-fields

            Change a link preview, the feedback box or the layout for one
            page.

    .. column::

        .. block:: Advanced
            :size: small
            :doc: ../advanced

            Custom properties, template overrides and what a build writes.

.. columns:: 3
    :gap: 1.5rem 0.35rem
    :flush:

    .. column::
        :span: auto

        .. button::
            :doc: /docs/kaamiki/installation
            :scheme: chevron

            Install it

    .. column::
        :span: auto

        .. button::
            :doc: /docs/kaamiki/settings
            :scheme: dark

            Every setting

    .. column::
        :span: auto

        .. button::
            :doc: /docs/kaamiki/roles
            :scheme: yellow

            The roles

A link in the text has a faint line under it. Rest your pointer on the one to
the :doc:`roles page <../roles>` and a full line draws across from the left,
then leaves out to the right when you go. The arrow on *Install it* draws
itself out the same way. Rest your pointer on a link for a moment and the page
it leads to starts loading before you click, so it opens at once. The next and
previous pages load quietly once this one is still. It's
``kaamiki.conf.motion.prefetch``, on by default, and a reader on a slow or
data-saving connection is left alone. Your browser's network panel shows it as
a request for a prefetch.

.. _kaamiki-example-motion-page-to-page:

-------------------------------------------------------------------------------
Page to page.
-------------------------------------------------------------------------------

Following a link can hand over from one page to the next, one thing at a time
and never two at once. The old content eases out first, a little way in the
direction you're going. Nothing of the new page shows until it has gone, and
then the new page plays its entrance, the one it plays when it loads, from its
first frame. The header, the sidebar and the footer stay as they are, since
they're the same on both pages. It's ``kaamiki.conf.motion.page_transitions``,
which is off here, so the buttons below hand over only on a site that has
switched it on:

.. tabs::

    .. tab:: In order

        #. The old content fades out and drifts up, or down when you go back.
        #. The header, the sidebar and the footer carry on as they were.
        #. The new page's byline, title and sections come in, as they do when
           you reload it.

    .. tab:: Switch it on

        .. code-block:: python

            kaamiki.conf.motion.page_transitions = True

        Or from the command line, with
        ``-D kaamiki_motion_page_transitions=1``.

    .. tab:: Who doesn't get it

        Firefox can't hand over between pages yet, so it loads the next page
        and plays its entrance as usual. A reader who asks their device for
        less motion gets no hand over and no entrance. A ``:no-motion:``
        directive stills only what's inside it, so it doesn't stop a hand over.

.. columns:: 2
    :gap: 1.5rem 0.35rem
    :flush:

    .. column::
        :span: auto

        .. button::
            :doc: /docs/kaamiki/directives/accordion
            :scheme: dark

            Follow a link

    .. column::
        :span: auto

        .. button::
            :doc: /docs/kaamiki/examples/motion
            :scheme: chevron

            Back to this page

Going back slides the old content out the other way, and a link that was
fetched ahead hands over just as smoothly, since the page is there already.
:doc:`The settings page <../settings>` has the setting and
:doc:`the advanced page <../advanced>` the custom properties behind it.

.. _kaamiki-example-motion-a-directive-at-its-own-speed:

-------------------------------------------------------------------------------
A directive at its own speed.
-------------------------------------------------------------------------------

Everything above moves at the site's speed, ``kaamiki.conf.motion.speed``. A
directive that moves can take its own with ``:speed:``, a step of the site's:
``2`` is twice as quick, ``0.5`` half as quick and ``1`` the site's own. The
steps are ``0.25``, ``0.5``, ``0.75``, ``1``, ``1.5``, ``2``, ``3`` and ``4``.
Open the three accordions below and compare how long each takes:

.. accordion:: At the site's speed

    Nothing was said, so it takes the speed of everything else.

.. accordion:: Four times as quick
    :speed: 4

    ``:speed: 4``, and it's done before you've seen it start.

.. accordion:: Half as quick
    :speed: 0.5

    ``:speed: 0.5``, and it takes its time.

``:no-motion:`` goes the other way: the directive plays nothing, and what's in
it shows and changes at once, the way it does for a reader who asks for less
motion. That reaches the roles inside it too, so a ``:swap:`` or a ``:ticker:``
in it stands still. Open this one:

.. accordion:: Not moving at all
    :no-motion:

    ``:no-motion:``, and this opened at once. A :ticker:`2025` that's counted
    for 2 seconds elsewhere shows its number here from the first frame.

.. code-block:: rst

    .. accordion:: Four times as quick
        :speed: 4

        Done before you've seen it start.

    .. accordion:: Not moving at all
        :no-motion:

        Opened at once.

A reader who asks their device for less motion gets the calmer version whatever
a directive's speed says. ``:speed:`` works on :doc:`accordions
<../directives/accordion>`, :doc:`tabs <../directives/tabs>`, :doc:`carousels
<../directives/carousel>`, :doc:`bylines <../directives/byline>`,
:doc:`repositories <../directives/repository>` and :doc:`releases
<../directives/release>`, and ``:no-motion:`` on those and on
:doc:`code-explain and code-version <../directives/explainers>`, where
``:pace:`` already means how far a step scrolls.

.. _kaamiki-example-motion-moving-around-the-site:

-------------------------------------------------------------------------------
Moving around the site.
-------------------------------------------------------------------------------

The furniture moves too, and it's all in front of you. In a wide window, the
names in the header open dropdowns that leave the way they came. The search box
grows as you press it. The colour button changes the colours of the whole page,
and the new ones spread out from the button with a soft edge, slowly, instead
of switching at once.

In a narrow window, or on a phone, the menu slides in from the side. Open it
and pull it shut with a finger: it follows you, and a quick flick closes it
from a short way while a slow drag has to go further. Let go early and it
springs back.

.. _kaamiki-example-motion-projects-and-releases:

-------------------------------------------------------------------------------
Projects and releases.
-------------------------------------------------------------------------------

A repository card asks GitHub for its numbers as it scrolls into view. When
GitHub answers, the counts fade in and the digits roll up, one count after the
other. The cards are real, so throttle the network in your browser's developer
tools to see them wait, and :ref:`the directive's page
<kaamiki-repository-while-github-answers>` has the rest:

.. columns:: 2
    :flush:
    :valign: top

    .. column::

        .. repository:: xames3/slowtorch

            A subset of core PyTorch features re-built in pure Python...
            albeit, slowly.

    .. column::

        .. repository:: xames3/xsnumpy

            An experimental re-implementation of a few NumPy features in
            Python.

A release draws the line down to the one before it. The two below are made up
for this page, the real ones are in the :doc:`changelog </changelog>`:

.. release:: Everything settles
    :version: 0.2.0
    :date: 11 November 2026

    The second made-up release, newest first.

    Added
        - A ring around the back-to-top button
        - Dots under a carousel

    Changed
        - An accordion closes quicker than it opens

.. release:: A calm first release
    :version: 0.1.0
    :date: 10 November 2026

    The first made-up release.

    Added
        - A dial for every animation

.. _kaamiki-example-motion-a-picture-that-becomes-a-player:

-------------------------------------------------------------------------------
A picture that becomes a player.
-------------------------------------------------------------------------------

A video starts as a picture with a play button and loads nothing from YouTube
until you press it. Then the player takes the picture's place and starts
playing at once:

.. youtube:: https://www.youtube.com/watch?v=kCc8FmEb1nY
    :caption: A video that loads when you press play.

A thumbnail card links out instead and loads nothing at all:

.. thumbnail:: https://youtu.be/VMj-3S1tku0

.. _kaamiki-example-motion-a-picture-that-opens:

-------------------------------------------------------------------------------
A picture that opens.
-------------------------------------------------------------------------------

A picture that's shown smaller than it is opens when you press it. It lifts
from where it sits to fit the screen, never bigger than it really is, on a
long, soft settle with no bounce. The page dims in step with it and blurs once
it has landed, and the caption fades in last. Closing runs it backwards, to
wherever the picture is by then: the caption goes first, then the blur, then
the picture. Close it with Esc, a press outside it, the close button or a
swipe down, or with Back on a phone, and a second press while it's still
moving turns it round from where it is. Turn the screen or resize the window
with it open, then close it, to see it find its way back. A greyscale picture
(:ref:`classes <kaamiki-classes-pictures>` has some) comes out of its grey as
it lifts and goes back to it as it shrinks. Close it with a press and nothing
is left focused or ringed. Close it from the keyboard and the focus goes back
to the picture, its ring fading away a moment later. This one is 640px wide,
shown at 240px:

.. figure:: /_static/combos/poster.jpg
    :width: 240px
    :alt: A dark frame of a sample clip with five coloured circles

    The sample clip's poster, shown at 240px of its 640.

A reader who asks for less motion gets a brief fade in place of the flight, and
so does a directive that says ``:no-motion:``. ``:speed:`` sets the pace of a
picture inside it like it does for anything else.

Pictures, figures, videos and the player above all stop at the text's 675px and
sit in the middle of it, whatever size they're given. Only the two directives
at the end of this page take more room, since code needs it.

.. _kaamiki-example-motion-copying-code:

-------------------------------------------------------------------------------
Copying code.
-------------------------------------------------------------------------------

A copy button appears when you hover a code block. Press it and the tick fades
in over the icon, then the icon comes back when you've done with it. These are
the defaults of the motion settings:

.. code-block:: python

    kaamiki.conf.motion.speed = 1
    kaamiki.conf.motion.prefetch = True
    kaamiki.conf.motion.page_transitions = False

.. _kaamiki-example-motion-code-that-runs-and-code-that-changes:

-------------------------------------------------------------------------------
Code that runs and code that changes.
-------------------------------------------------------------------------------

The last two need room, so they're at the end. Both step through code as you
scroll in a window wide enough for their 835px and stack in a narrower one. The
first runs a snippet and shows what each line held, here the way a thing eases
to a stop, covering half of what's left every frame:

.. code-explain:: python
    :caption: settle.py
    :watch: position

    .. code::

        target = 100
        position = 0
        for frame in range(1, 6):
            position += (target - position) / 2

    .. lines:: 1-2

        Start at zero with a hundred to go.

    .. lines:: 3-4

        Each frame covers half of what's left, so the steps get smaller and it
        arrives gently.

The second shows the versions a piece of code went through, the lines on their
way out going red and the new ones green. This is how the curve under
``--km-ease-smooth`` came about:

.. code-version:: python
    :caption: ease.py

    .. attempt::

        .. code::

            def ease(t):
                return t

        .. output:: broke

            >>> [round(ease(t / 10), 2) for t in range(11)]
            [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

        Constant speed. It starts and stops all at once, like a machine.

    .. attempt::

        .. code::

            def ease(t):
                return 1 - (1 - t) ** 3

        .. output:: broke

            >>> [round(ease(t / 10), 2) for t in range(11)]
            [0.0, 0.27, 0.49, 0.66, 0.78, 0.88, 0.94, 0.97, 0.99, 1.0, 1.0]

        It lands softly, but the first step already covers 27% of the way.

    .. attempt::

        .. code::

            from math import exp

            def ease(t):
                return 1 - (1 + 8 * t) * exp(-8 * t)

        .. output:: worked

            >>> [round(ease(t / 10), 2) for t in range(11)]
            [0.0, 0.19, 0.48, 0.69, 0.83, 0.91, 0.95, 0.98, 0.99, 0.99, 1.0]

        .. lines:: 4

            A spring. It leaves as gently as it arrives.
