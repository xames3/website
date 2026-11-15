.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 October 2025
.. Last updated on: 13 November 2026

:km-page-title: Questions I get asked
:km-page-description: Frequently asked questions about me and this website...
    answered
:km-page-type: article
:km-feedback-title: Do you've any questions for me?
:km-feedback-description: Feel free to ask anything you're curious about.
:km-feedback-button: Send in your questions

.. _extras-questions-i-get-asked:

===============================================================================
:fa-icon:regular:`comments` Questions I get asked
===============================================================================

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3

.. seealso::

    I add any new questions every few weeks and update older responses if
    anything has changed since my last reply. If your question isn't listed
    here it'll probably be added in the next few weeks.

One of the best parts of sharing and writing these articles is the chats that
follow. I've had loads of interesting chats in person and a few over email and
I think I've noticed a pattern. A lot of the same questions pop up; some are
esoteric about a topic, while others are simple *"why?"* questions. Ever since
I transitioned into teaching, some of you've also questioned that, too.

By the way, all of them are great questions! Then there are the questions
about what my favourite films are and what I'm currently watching. So to make
this easier for everyone, I've put together my answers to your most frequent
questions.

It's an extension of my story really, with a few easter eggs.

.. _faq:

.. columns:: 6
    :class: km-wide

    .. column::
        :span: 2

        .. rubric:: Frequently asked questions.

    .. column::
        :span: 4

        .. accordion:: What the f*ck is XAMES3 and why you use it everywhere?
            |pop|
            :group: faq
            :subheader: Asked on 02 November 2025
            :nested-subheader:

            So, *XAMES3* is my alias and username for online profiles. The
            first part, "*XA*", represents my first name, Akshay. The letter X
            is a sound-alike for the first syllable, "**Aksh**". Think of the
            letter "X" on its own; it sounds similar to "*Aksh*".

            A is a sound-alike for the second syllable, "**ay**" (as in "day").

            So, "**Aksh**" + "**ay**" becomes **X-A**.

            The second part, "*MES3*", is a subtle play on my surname, Mestry.
            MES is a straightforward representation of the first syllable,
            "**Mes**". And the number 3 represents "**try**". It isn't "try" as
            we say in English but more like "tree".

            So, *XAMES3* is just my name spelled out in short. This is called a
            `gramogram`_ in English. For example, "*c u*" is a gramogram for
            "see you", "*JL*" is a gramogram for "jail", etc.

        .. accordion:: How do you pronounce XAMES3 or XA?
            :group: faq
            :subheader: Asked on 02 November 2025
            :nested-subheader:

            It's literally pronounced as "X-A" or "X-A-Mes-three".

        .. accordion:: Why did you transitioned into teaching?
            :group: faq
            :subheader: Asked on 16 November 2025
            :nested-subheader:

            I promised :ref:`Charlotte <charlotte-parks>` that I'd teach
            someday to students or be in academia. Honestly speaking, I meant
            it as a joke, in that moment, but now that I'm teaching, I
            understand what she meant.

        .. accordion:: What's your role at National Louis University?
            :group: faq
            :subheader: Asked on 16 November 2025
            :nested-subheader:

            I'm an :strike:`Adjunct` :strike:`Assistant` Adjunct Professor at
            `National Louis University`_'s Undergraduate college in Computer
            Science & Information Systems (CSIS) Department.

        .. accordion:: What are your primary interests as IT professional?
            :group: faq
            :subheader: Asked on 02 December 2025
            :nested-subheader:

            Looking back, I'd say I've transitioned from a Software Engineer to
            AI. So, I still love to build or brainstorm about solutions or
            ideas that solve a particular problem. I enjoy AI too, don't get me
            wrong. But, software engineering, in particular:

            - understanding user or customer requirements
            - working with tools or accesses available at my disposal
            - reading and experimenting with documentations
            - debugging logs and spending time on terminal
            - collaborating with other teams and fellow developers
            - building APIs
            - deployments (not on Fridays, those are f*cking horrible!)
            - maintaining documentations

            brings me joy!

        .. accordion:: What's your favourite movie/TV show?
            :group: faq
            :subheader: Asked on 02 December 2025
            :nested-subheader:

            I'm a huge `Christopher Nolan`_ fan and I
            :fa-icon:solid:`heart km-tone--red` his films. I tend to watch a
            lot of films, so it's difficult to say, what's my favourite. But,
            my go-to movie is `Interstellar`_. I absolutely love the music
            compositions by `Hans Zimmer`_. It's truly a masterpiece!

            As far as my favourite TV show, I've a few. My go-to would be
            obviously, `Family Guy`_. But, if I were to recommend a TV show to
            anyone, I'd probably say, `Dark`_.

        .. accordion:: What's your website's tech stack? The GitHub source
            looks simple
            :group: faq
            :subheader: Asked on 12 December 2025
            :nested-subheader:

            Thanks for checking out the source code on GitHub! I'm no Frontend
            engineer and have sparse knowledge about modern JS frameworks at
            best. As you may've seen from the source itself, it's built using
            simple HTML, CSS and vanilla JS (based on answers from
            StackOverflow).

            There's no proper modern "tech stack" so to speak used for this
            website. I'm using `Sphinx`_ as my primary web-development tool.

            Sphinx is a (python-based) documentation builder framework/package.
            I've written loads of internal technical documentations at my
            former employers, so I'm quite familiar with that. Since, it's
            written in Python, there's a lot of scope for customisation. Plus,
            there are loads of extensions for Sphinx. Although, there are a lot
            of sphinx extensions out there, I wasn't particularly satisfied
            with them, so I wrote a few of my own which are included as part of
            this theme and website. So, Sphinx covers the backend portion of my
            website.

            My custom extensions are as follows:

            - ``byline`` renders author details like name, picture, reading
              time and a button that copies the page's link
            - ``repository`` renders a small widget to show information about
              the GitHub repository. The details include stars and fork counts
            - ``thumbnail`` links YouTube videos by showing thumbnails
              asynchronously
            - ``video`` links any publically accessible video
            - ``youtube`` embeds a YouTube video

            The rest frontend side is completely handled using simple HTML and
            `Jinja2`_ templating. Jinja or Jinja2 is a templating engine
            written in Python and renders something called **Jinja templates**.
            To stylise the website, I'm using vanilla CSS and JS.


.. _gramogram: https://en.wikipedia.org/wiki/Gramogram
.. _National Louis University: https://nl.edu/undergraduate-college/
.. _Christopher Nolan: https://www.imdb.com/name/nm0634240
.. _Interstellar: https://en.wikipedia.org/wiki/Interstellar_(film)
.. _Hans Zimmer: https://en.wikipedia.org/wiki/Hans_Zimmer
.. _Family Guy: https://www.hulu.com/series/3c3c0f8b-7366-4d15-88ab
    -18050285978e
.. _Dark: https://www.netflix.com/title/80100172
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _Jinja2: https://jinja.palletsprojects.com/en/stable/
