.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 08 March, 2026
.. Last updated on: 29 April, 2026

:og:title: A month into Docker
:og:description: An exhaustive guide to moving from "making it work" to
    understanding the plumbing of containerisation
:og:type: article
:fb:title: This was me, but I'm curious about your story
:fb:description: Have you ever accidentally filled your entire hard drive with
    Docker debris? How did you fix it?
:fb:button: Share your story

.. _explained-a-month-into-docker:

===============================================================================
:fas:`box-open far` A month into Docker
===============================================================================

.. rst-class:: lead

    The month where I moved from "I can make this work" to "I actually
    understand why this works".

.. author:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3

.. role:: console(code)
    :language: console

.. warning::

    This chapter is still being written, and I'm not sure how long will it take
    for me to finish it.

If you're here, I'm assuming you've already read the previous
:doc:`chapter <index>`. We're still in the middle of a pandemic, but it's
October 2020 now. I had spent the last four weeks treating `Docker`_ like any
other :abbr:`CLI (Command Line Interface)` utility. I was shamelessly
copy-pasting code from `StackOverflow`_, running commands without
understanding anything, fixing them as they failed and always hoping they'd
work the next time.

During that whole phase of ignorance, I thought Docker was some kind of magical
black box that somehow kept my machine clean, or so I believed.

In reality, I had simply traded my messy host system for a bloated but still
invisible pile of `containers`_ and `images`_. I was still writing my "hacky"
python scripts to automate various tasks, as that's what I do for the most
part. However, I was starting to notice that my laptop was getting sluggish,
not because of my scripts, but something else entirely. I knew I had to stop
just "typing the commands" and start understanding what the Docker CLI was
actually doing behind the scenes.

.. rubric:: :fab:`skull far` Enter the deadzone
    :class: pre-title-text

.. _invisible-pile-of-dead-containers:

--------------------------------------------------------------------------------
Invisible pile of dead containers.
--------------------------------------------------------------------------------

I started to take things seriously when I tried to save a file and got a "Disk
Full" warning. I was super-duper confused. I mean, I thought I was using Docker
specifically to avoid this problem by not installing multiple versions of
Python and Rust on my machine.

So, what was this warning all about? I had no idea, but I knew I had to fix it
somehow.

With some googling, I learned about the :console:`$ docker ps` command and,
more importantly, running this command with the optional ``-a`` or ``--all``
flag. Running :console:`$ docker ps -a` was an absolute game-changer for me. I
saw the output of the terminal, and my heart dropped. By this point, I
literally had hundreds of dead and unused containers just sitting there, taking
up precious disk space.

This is when I realised that every time I ran a command like
:console:`$ docker run python3:8 python script.py`, I was creating a new,
isolated environment. What I didn't realise was that once my script finished
running, the container didn't just vanish. It stayed there, taking up space in
an **"exited"** state.

I felt absolutely stupid. I was in awe, but still stupid, nonetheless.

As I mentioned :ref:`here <idea-behind-containers>`, a container is a
lightweight, standalone package, and it's similar to an instance of a class, if
we're speaking in programming terms. However, its lifecycle doesn't end just
because the process inside it finishes.

You've to actively manage its death just as much as its birth.

.. _Docker: https://www.docker.com/
.. _containers: https://en.wikipedia.org/wiki/Container_(virtualization)/
.. _images: https://www.techtarget.com/searchitoperations/definition/Docker-image/
.. _StackOverflow: https://stackoverflow.com/
