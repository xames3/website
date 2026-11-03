.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 22 February 2025
.. Last updated on: 02 November 2026

:orphan:
:km-page-title: Akshay Mestry
:km-page-description: Stories from what I build, explainers and notes from
    the classroom.
:km-page-type: website
:km-page-image: https://avatars.githubusercontent.com/u/90549089?v=4
:km-feedback-title: So, what do you think?
:km-feedback-description: Got a question about teaching or a great film
    I've somehow missed? Let me know.
:km-feedback-button: Say hello
:km-feedback-icon: fa-solid fa-paper-plane
:km-feedback-split:

.. _home-page:

===============================================================================
Akshay Mestry
===============================================================================

.. rst-class:: km-text-lead

    An educator, a software engineer and a storyteller.

.. byline:: @xames3
    :avatar: https://i.imgur.com/hUhxigb.jpeg
    :target: https://github.com/xames3
    :backdrop: https://i.imgur.com/JOBRcgT.jpg,
        https://i.imgur.com/hUhxigb.jpeg,
        https://i.imgur.com/gcGHqxi.jpg,
        https://i.imgur.com/weM4qDW.jpg

.. embed:: ./assets/html/greetings.html
    :source: _static/greetings.json
    :interval: 2800
    :duration: 700
    :stagger: 45

I'm Akshay (/uh-k-sh-ay/), an educator, engineer, avid cook and currently an
Assistant Professor at `National Louis University`_. Before getting into
academia, I worked at consulting firms, corporate product companies and
startups. This cheeky corner of the internet is where I dump all that: the
wins and the mistakes, one story at a time.

.. rubric:: :fa-icon:`compass-drafting` Build and share
    :class: km-text-pre-section

.. _open-source:

-------------------------------------------------------------------------------
Love for open source.
-------------------------------------------------------------------------------

I :fa-icon:solid:`heart km-tone--red` Open source!

I fell into it by accident and I bloody loved it. It was and still is a
personal reminder to share my struggles and achievements with everyone and
invite collaboration. That naive belief in sharing took me into some brilliant
research labs and projects, working under the guidance of some super-duper
talented people in the industry.

.. embed:: ./assets/html/contributed.html
    :source: _static/contributed.json
    :data-speed: slow
    :data-direction: left

In those labs I worked on machine learning models and optimised their
user-facing libraries. These projects and sometimes our clients (big and/or
small) showed me exactly where my technical depth ended.

.. columns:: 2
    :flush:

    .. column::

        .. repository:: xames3/slowtorch

            A subset of core PyTorch features re-built in pure Python...
            albeit, slowly.

    .. column::

        .. repository:: xames3/xsnumpy

            An experimental re-implementation of a few NumPy features in
            Python.

Beyond these, I've also ended up speaking at a few tech meetups and now
volunteering at `Chicago Code and Coffee`_, rambling about my projects, my
half-baked (somewhat condemning) thoughts on AI and how some frameworks
actually work under the hood.

.. columns:: 4
    :gap: 1.5rem 0.35rem
    :margin: 5rem 2rem
    :flush:
    :stack-align: center

    .. column::
        :span: 2

        .. rubric:: Not on social media, but let's connect.

    .. column::
        :span: auto
        :class: align-right

        .. button:: mailto:xa@mes3.dev
            :scheme: chevron

            Send an email

    .. column::
        :span: auto

        .. button:: https://linkedin.com/in/xames3
            :scheme: dark

            LinkedIn

.. rubric:: :fa-icon:regular:`comments` Keep it stupid simple
    :class: km-text-pre-section

.. _teaching-philosophy:

-------------------------------------------------------------------------------
My teaching philosophy.
-------------------------------------------------------------------------------

What I enjoy most is taking, say, some computer science topic and explaining
it in the simplest way possible, so it clicks for someone who's never bothered
understanding it before. I'd say in practice, my teaching philosophy comes
down to these three things:

- Embrace failures. When you're learning, fail early and often. Don't be
  afraid of being wrong in the early days and learn from your mistakes.
- Show, don't tell. A finished answer hides thinking and reasoning. If I can't
  rebuild or live-code it, I don't understand it well enough to teach it.
- Teach the person in front of me. Every reader and student is different, so
  my approach has to be too. Yes, it's fairly inconvenient at times, but
  necessary.

Early in my software engineering career, I came across a line that's often
credited to Dr Richard Feynman:

.. epigraph::

    If you want to master something, teach it.

I went looking for where he actually said it and couldn't find a source, so
take the credit with a pinch of salt. But I still think, he's right. You can't
really call yourself an :abbr:`SME (Subject-matter expert)` until you can
teach a concept to someone who knows nothing about it and still put up with
their questions without getting cocky about how much you know.

So far, I've taught...

.. embed:: ./assets/html/currently-teaching.html
    :source: _static/courses.json
    :prefix-text:
    :typing-speed: 120
    :deleting-speed: 80
    :pause-after-typing: 2000
    :pause-after-deleting: 1000

My approach to teaching and mentoring has changed loads over the years. You
can read the long versions in future blogs.

.. _National Louis University: https://nl.edu/undergraduate-college/
.. _Chicago Code and Coffee: https://www.meetup.com/code-and-coffee-chicago

.. toctree::
    :caption: Academia
    :hidden:
    :titlesonly:

    academia/thoughts-on-teaching

.. toctree::
    :caption: Journal
    :hidden:
    :maxdepth: 1

.. toctree::
    :caption: Explained
    :hidden:
    :maxdepth: 1

.. toctree::
    :caption: Docs
    :hidden:
    :maxdepth: 1

.. toctree::
    :caption: Extras
    :hidden:
    :maxdepth: 1
