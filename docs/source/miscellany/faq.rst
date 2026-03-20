.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 October, 2025
.. Last updated on: 18 March, 2026

:og:title: FAQs
:og:description: Frequently Asked Questions about me and this website
:og:type: article
:prompt: Do you've any question for me?
:promptdesc: Feel free to ask me about things that you're curious about.
:submitbtn: Send in your question
:faicon: user-question

.. _miscellany-faq:

===============================================================================
:fas:`circle-question far` FAQs
===============================================================================

.. author::
    :name: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :github: https://github.com/xames3

One of the best parts of sharing and writing these articles is the chats that
follow. I've had loads of interesting chats in person and a few over email, and
I think I've noticed a pattern.

A lot of the same questions pop up; some are esoteric about a topic, while
others are simple *"why?"* questions. Ever since I transitioned into teaching,
some of you've also questioned that, too.

While many have asked about my thoughts on the late 2025 job situation. Some
have even asked why even I built projects like
:doc:`xsNumPy <../projects/xsnumpy>` and
:doc:`SlowTorch <../projects/slowtorch>`, which seem like reinventing the
wheel.

By the way, all of them are great questions!! Then there are the questions
about what my favourite films are and what I'm currently watching. So to make
this easier for everyone, I've put together my answers to your most frequent
questions.

This isn't just a list, but it's an extension of my story. Some easter eggs, so
to speak...

.. _faq:

-------------------------------------------------------------------------------
Frequently asked questions
-------------------------------------------------------------------------------

.. dropdown:: What the f*ck is XAMES3, and why you use it everywhere? |pop|
    :class-container: site-faq

    .. rubric:: Asked on November 02, 2025
        :class: date-text

    So, *XAMES3* is my alias and username for online profiles. The first part,
    "*XA*", represents my first name, Akshay. The letter X is a sound-alike for
    the first syllable, "**Aksh**". Think of the letter "X" on its own; it
    sounds similar to "*Aksh*".

    A is a sound-alike for the second syllable, "**ay**" (as in "day").

    So, "**Aksh**" + "**ay**" becomes **X-A**.

    The second part, "*MES3*", is a subtle play on my surname, Mestry. MES is
    a straightforward representation of the first syllable, "**Mes**". And the
    number 3 represents "**try**". It is not "try" as we say in English but
    more like "tree".

    So, *XAMES3* is just my name spelled out in short. This is called a
    `gramogram`_ in English. For example, "*c u*" is a gramogram for "see you",
    "*JL*" is a gramogram for "jail", etc.

.. dropdown:: How do you pronounce XAMES3 or XA?
    :class-container: site-faq

    .. rubric:: Asked on November 02, 2025
        :class: date-text

    It's literally pronounced as "X-A" or "X-A-Mes-three".

.. dropdown:: Why did you transitioned into teaching?
    :class-container: site-faq

    .. rubric:: Asked on November 16, 2025
        :class: date-text

    I promised :ref:`Charlotte <charlotte-parks>` that I'd teach someday to
    students or be in academia. Honestly speaking, I meant it as a joke, in
    that moment, but now that I'm teaching, I understand what she meant.

.. dropdown:: What is your role at National Louis University?
    :class-container: site-faq

    .. rubric:: Asked on November 16, 2025
        :class: date-text

    I'm an Adjunct at `National Louis University`_'s Undergraduate college in
    Computer Science & Information Systems (CSIS) Department.

.. dropdown:: What are your primary interests as IT professional?
    :class-container: site-faq

    .. rubric:: Asked on December 02, 2025
        :class: date-text

    Looking back, I'd say I've transitioned from a Software Engineer to AI. So,
    I still love to build or brainstorm about solutions or ideas that solve a
    particular problem. I enjoy AI too, don't get me wrong. But, software
    engineering, in particular:

    - understanding user or customer requirements
    - working with tools or accesses available at my disposal
    - reading and experimenting with documentations
    - debugging logs, and spending time on terminal
    - collaborating with other teams and fellow developers
    - building APIs
    - deployments (not on Fridays, those are f*cking horrible!!)
    - maintaining documentations

    brings me joy!!

.. dropdown:: What is your favourite movie/TV show?
    :class-container: site-faq

    .. rubric:: Asked on December 02, 2025
        :class: date-text

    I'm a huge `Christopher Nolan`_ fan, and I :fas:`heart mrl-0 red` his
    films. I tend to watch a lot of films, so it is difficult to say, what's my
    favourite. But, my go-to movie is `Interstellar`_. I absolutely love the
    music compositions by `Hans Zimmer`_. It is truly a masterpiece!!

    As far as my favourite TV show, I've a few. My go-to would be obviously,
    `Family Guy`_. But, if I were to recommend a TV show to anyone, I'd
    probably say, `Dark`_.

.. dropdown:: What is your website's tech stack? The GitHub source looks simple
    :class-container: site-faq

    .. rubric:: Asked on December 12, 2025
        :class: date-text

    Thanks for checking out the source code on GitHub!! I'm no Frontend
    engineer and have sparse knowledge about modern JS frameworks at best. As
    you may've seen from the source itself, it's built using simple HTML, CSS,
    and vanilla JS (based on answers from StackOverflow).

    There's no proper modern "tech stack" so to speak used for this website.
    I'm using `Sphinx`_ as my primary web-development tool.

    Sphinx is a (python-based) documentation builder framework/package. I've
    written loads of internal technical documentations at my former employers,
    so I'm quite familiar with that. Since, it's written in Python, there's a
    lot of scope for customisation. Plus, there are loads of extensions for
    Sphinx. Although, there are a lot of sphinx extensions out there, I wasn't
    particularly satisfied with them, so I wrote a few of my own which are
    included as part of this theme and website. So, Sphinx covers the backend
    portion of my website.

    My custom extensions are as follows:

    - **author.** This renders author details like name, about, email, GitHub,
      LinkedIn, and a timestamp of article
    - **picture.** Show colour-scheme aware images on the website
    - **repository.** Renders a small widget to show information about the
      GitHub repository. The details include stars and fork counts
    - **thumbnail.** This links YouTube videos by showing thumbnails
      asynchronously
    - **video.** Links any publically accessible video
    - **youtube.** Embeds a YouTube video

    The rest frontend side is completely handled using simple HTML and
    `Jinja2`_ templating. Jinja or Jinja2 is a templating engine written in
    Python and renders something called **Jinja templates**. To stylise the
    website, I'm using vanilla CSS and JS.

.. _gramogram: https://en.wikipedia.org/wiki/Gramogram
.. _National Louis University: https://nl.edu/undergraduate-college
.. _Christopher Nolan: https://www.imdb.com/name/nm0634240
.. _Interstellar: https://en.wikipedia.org/wiki/Interstellar_(film)
.. _Hans Zimmer: https://en.wikipedia.org/wiki/Hans_Zimmer
.. _Family Guy: https://www.hulu.com/series/3c3c0f8b-7366-4d15-88ab
    -18050285978e
.. _Dark: https://www.netflix.com/title/80100172
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _Jinja2: https://jinja.palletsprojects.com/en/stable/
