.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 08 March, 2026
.. Last updated on: 11 June, 2026

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

.. rubric:: :fas:`trash-can far` Out with the dead
    :class: pre-title-text

.. _killing-the-dead:

--------------------------------------------------------------------------------
Killing the dead.
--------------------------------------------------------------------------------

.. rubric:: Or, learning that containers don't disappear just because you want
    them to.
    :class: subtitle-text

Now that I knew the problem, I had to actually fix it. I Googled "how to remove
Docker containers" and found :console:`$ docker rm`.

.. code-block:: console

    $ docker rm <container-id>

Simple enough. I tried it on a container ID I'd copied from the
:console:`$ docker ps -a` output. It worked. One down. About three hundred to
go.

My first instinct was to write a quick script to loop through all the IDs. But
before I'd even opened my editor, I found something much better:
:console:`$ docker container prune`.

.. code-block:: console

    $ docker container prune
    WARNING! This will remove all stopped containers.
    Are you sure you want to continue? [y/N] y
    ...
    Total reclaimed space: 2.3GB

2.3 gigabytes. I had accidentally hoarded 2.3 gigabytes worth of dead
containers. I felt a strange mix of embarrassment and relief at the same time.
My machine breathed again.

But then a thought hit me — could I have avoided this entirely? As it turns
out, yes. There's a flag called ``--rm`` that makes Docker automatically remove
a container the moment it stops running.

.. code-block:: console

    $ docker run --rm python:3.8 python -c "print('hello')"

The container runs, prints, and vanishes. No mess, no cleanup needed. I
remember staring at this flag in the documentation and thinking...
*where were you four weeks ago?!*

.. admonition:: :fas:`badge-check green` One rule to carry forward
    :class: unusual-one note

    Always use ``--rm`` when running throwaway containers. It's the simplest
    habit to build and it will save you from exactly my situation.

.. rubric:: :fas:`terminal far` Foreground vs. background
    :class: pre-title-text

.. _stuck-on-the-terminal:

--------------------------------------------------------------------------------
Stuck on the terminal.
--------------------------------------------------------------------------------

.. rubric:: The first time I ran a server inside Docker and lost my entire
    terminal.
    :class: subtitle-text

With the machine cleaned up, I started experimenting more ambitiously. I wanted
to run an actual server inside Docker — a simple Flask app I had been tinkering
with. So I ran something like:

.. code-block:: console

    $ docker run python:3.8 python server.py

And my terminal just... froze. The server was running, but I couldn't type
anything. It was completely taken hostage.

I know now this is completely normal and expected behaviour. When you run
:console:`$ docker run` without any extra flags, Docker attaches your terminal
directly to the container's process. If that process is a server that runs
forever, so does your terminal session.

The fix is the ``-d`` flag — detached mode.

.. code-block:: console

    $ docker run -d python:3.8 python server.py

Run with ``-d``, and Docker starts the container in the background and
immediately hands your terminal back, along with a container ID. Your terminal
is free. The server is running. It's brilliant.

But then came the obvious next problem: how do I know if the server is actually
doing anything? I couldn't see any output. That's where
:console:`$ docker logs` comes in.

.. code-block:: console

    $ docker logs <container-id>

It dumps whatever the container has printed to stdout. If something went wrong,
the error messages will be there too. Think of it as checking the receipts on a
transaction you never saw happen.

.. rubric:: :fas:`plug far` Opening the door
    :class: pre-title-text

.. _the-server-no-one-could-reach:

--------------------------------------------------------------------------------
The server no one could reach.
--------------------------------------------------------------------------------

.. rubric:: Running a web server inside Docker and not being able to open it
    in a browser.
    :class: subtitle-text

Alright. Server running in the background. I opened my browser and typed
``localhost:5000``. Nothing.

I checked whether the container was running — :console:`$ docker ps`, yes, it
was. I checked the logs — no errors. The server was healthy. So why couldn't I
reach it?

This one stumped me for longer than I'd like to admit.

Here's the thing: containers are isolated. That's the entire point. By default,
the port your application is listening on *inside* the container has no
connection to any port on your actual machine. They're separate worlds. The
container's port 5000 is just floating in there, unreachable, unless you
explicitly create a bridge between the two.

That bridge is called port mapping, and the flag is ``-p``.

.. code-block:: console

    $ docker run -d -p 5000:5000 python:3.8 python server.py

The format is ``-p <host-port>:<container-port>``. So ``-p 5000:5000`` means:
take the container's port 5000 and make it accessible at port 5000 on my
machine.

Now ``localhost:5000`` worked. I felt like I had just connected two entirely
separate train tracks together.

You can also map to a different host port if you need to. Say I had something
already running on my machine's port 5000:

.. code-block:: console

    $ docker run -d -p 8080:5000 python:3.8 python server.py

The container's internal port 5000 is now accessible at ``localhost:8080``. The
container genuinely doesn't care what number you use on the outside — it just
listens on 5000 regardless.

.. rubric:: :fas:`tag far` Know your containers
    :class: pre-title-text

.. _a-container-by-any-other-name:

--------------------------------------------------------------------------------
A container by any other name.
--------------------------------------------------------------------------------

.. rubric:: Why Docker's random name generator is charming but not very useful.
    :class: subtitle-text

By this point, I was running multiple containers, stopping them, restarting
them, and I kept having to copy-paste long container IDs from
:console:`$ docker ps` output. Strings like ``a3f8d91c204b``. Every. Single.
Time.

Then I noticed that Docker also gives containers human-readable names. Things
like ``tender_wozniak``, ``sleepy_darwin``, ``naughty_einstein``. Apparently
Docker generates these by combining a random adjective with a famous scientist's
name. They're genuinely charming at first, but deeply impractical when you have
five containers running and you're trying to figure out which one is which.

The ``--name`` flag solves this immediately.

.. code-block:: console

    $ docker run -d --name my-flask-app -p 5000:5000 python:3.8 python server.py

Now instead of:

.. code-block:: console

    $ docker stop a3f8d91c204b

I can do:

.. code-block:: console

    $ docker stop my-flask-app

It's such a small thing. But it's the difference between feeling in control and
feeling like you're herding cats. Name your containers. Always.

.. rubric:: :fas:`hand far` Graceful vs. forceful
    :class: pre-title-text

.. _stopping-vs-killing:

--------------------------------------------------------------------------------
Stopping vs. killing.
--------------------------------------------------------------------------------

.. rubric:: There's a "please stop" and then there's a "stop. now."
    :class: subtitle-text

Since we're talking about :console:`$ docker stop` — I want to clear up
something that confused me for a while. There are two ways to stop a running
container: :console:`$ docker stop` and :console:`$ docker kill`.

:console:`$ docker stop` sends a ``SIGTERM`` signal to the container's main
process, giving it a chance to shut down gracefully. It waits 10 seconds by
default, and if the container still hasn't stopped by then, it sends ``SIGKILL``
to force it.

:console:`$ docker kill` skips the grace period entirely and sends ``SIGKILL``
straight away. The process inside has no chance to clean up.

For most situations, :console:`$ docker stop` is the right call. It's the
polite option. :console:`$ docker kill` is for when a container is completely
unresponsive or you're in a hurry and genuinely don't care about graceful
shutdown.

Think of it this way: :console:`$ docker stop` is asking someone to leave.
:console:`$ docker kill` is escorting them out.

.. rubric:: :fas:`key far` Configuring containers
    :class: pre-title-text

.. _passing-secrets-into-the-box:

--------------------------------------------------------------------------------
Passing secrets into the box.
--------------------------------------------------------------------------------

.. rubric:: Environment variables, and the moment I tried to debug a Rust
    binary.
    :class: subtitle-text

One of the reasons I started using Docker in the first place was to avoid
installing `Rust`_ directly on my machine. So when I came across a Rust-based
:abbr:`CLI (Command Line Interface)` tool on `Docker Hub`_ that I wanted to
test, running it in a container felt like the natural thing to do.

I pulled the image, ran it, and it immediately panicked. The terminal output
was spectacularly unhelpful:

.. code-block:: console

    thread 'main' panicked at 'something went wrong', src/main.rs:42:9
    note: run with `RUST_BACKTRACE=1` environment variable to display a
          backtrace

Right, ``RUST_BACKTRACE=1``. I'd done this a hundred times on my local machine
by just exporting it in my shell. But now the program was running *inside* a
container. My exported shell variables didn't follow it in there.

The answer is the ``-e`` flag.

.. code-block:: console

    $ docker run --rm -e RUST_BACKTRACE=1 some-rust-tool

The ``-e`` flag sets an environment variable inside the container at runtime.
You can pass as many ``-e`` flags as you need, and they're available to the
process just like any other environment variable. The program has no idea
whether they were set on your local machine or passed in through Docker.

.. code-block:: console

    $ docker run --rm \
        -e RUST_BACKTRACE=1 \
        -e RUST_LOG=debug \
        some-rust-tool

The full stack trace finally appeared, and I was able to understand the
problem. But more importantly, I realised that ``-e`` is how you pass *any*
kind of runtime configuration into a container without baking it into the image
itself. API keys, connection strings, feature flags — all of it, passed in at
runtime and kept out of the image entirely.

.. rubric:: :fas:`door-open far` Peek inside
    :class: pre-title-text

.. _getting-inside-the-box:

--------------------------------------------------------------------------------
Getting inside the box.
--------------------------------------------------------------------------------

.. rubric:: The first time I opened a shell inside a running container.
    :class: subtitle-text

By mid-October, I had a container running but something was behaving oddly. The
logs weren't giving me enough detail. I wanted to actually get inside — open a
terminal within the running container and have a proper look around.

This is what :console:`$ docker exec` is for.

.. code-block:: console

    $ docker exec -it my-flask-app bash

And just like that, I had a shell inside the running container. I could
navigate the filesystem, check if my files were where I expected them to be,
run commands manually, poke around.

The ``-it`` flags are doing the same thing they do in :console:`$ docker run`:

- ``-i`` keeps stdin open so you can type
- ``-t`` allocates a terminal so it looks and behaves like a real one

Together, ``-it`` gives you an interactive terminal session. Without them,
:console:`$ docker exec` just runs the command silently and exits.

One thing to note: not every container has ``bash``. Smaller, minimal images,
especially anything based on ``alpine``, might only have ``sh``. In those
cases:

.. code-block:: console

    $ docker exec -it my-container sh

Knowing you can get a shell inside a running container changes how you debug.
Instead of guessing from the outside, you can just go in and see for yourself.

.. rubric:: :fas:`layer-group far` The other mess
    :class: pre-title-text

.. _the-image-graveyard:

--------------------------------------------------------------------------------
The image graveyard.
--------------------------------------------------------------------------------

.. rubric:: I thought I was pulling one Python image. I was pulling several.
    :class: subtitle-text

With containers under control, I started noticing that my disk was still slowly
filling up. This time the culprit wasn't containers — it was images.

Every time I ran :console:`$ docker run python:3.8`, Docker would check if the
image was already on my machine. If not, it would pull it. What I hadn't
noticed was that I'd been pulling variations of the same image with different
tags. ``python:3.8``, ``python:3.9``, ``python:3.8-slim``, ``python:latest``.
Each one a different download. Each one sitting on my disk.

.. code-block:: console

    $ docker images

The output was not pretty:

.. code-block:: console

    REPOSITORY   TAG         IMAGE ID       CREATED        SIZE
    python       3.9         a1b2c3d4e5f6   2 weeks ago    912MB
    python       3.8         b2c3d4e5f6a1   3 weeks ago    884MB
    python       3.8-slim    c3d4e5f6a1b2   3 weeks ago    128MB
    python       latest      d4e5f6a1b2c3   1 week ago     912MB

Nearly 3GB of Python images alone. And I wasn't actively using half of them.

To remove a specific image:

.. code-block:: console

    $ docker rmi python:3.9

To remove all "dangling" images — ones with no tag and not referenced by any
container:

.. code-block:: console

    $ docker image prune

To be more aggressive and remove all unused images, tagged or not:

.. code-block:: console

    $ docker image prune -a

Be careful with the ``-a`` flag though. It'll remove any image not currently
used by a running container, including ones you might want to keep around for
later.

You can also explicitly pull an image without running it, which is useful when
you want to download something in advance or just make sure you have the latest
version:

.. code-block:: console

    $ docker pull python:3.8-slim

.. rubric:: :fas:`code-compare far` Two dialects
    :class: pre-title-text

.. _old-commands-new-commands:

--------------------------------------------------------------------------------
Old commands, new commands.
--------------------------------------------------------------------------------

.. rubric:: The moment I realised Docker's CLI had two entirely different ways
    to say the same thing.
    :class: subtitle-text

Around the same time, I noticed something that confused me quite a bit. I kept
seeing Docker commands written in two different ways across different tutorials.
Some people wrote :console:`$ docker ps`, others wrote
:console:`$ docker container ls`. Both did the same thing. Was one wrong?
Deprecated? Why did both exist?

Turns out Docker's :abbr:`CLI (Command Line Interface)` has a bit of history.
The original shorter commands (:console:`$ docker ps`, :console:`$ docker rm`,
:console:`$ docker images`, and so on) were what everyone used from the
beginning. At some point, Docker reorganised the CLI into what are now called
management commands — a more structured, verb-noun format grouped by resource
type.

.. list-table::
    :header-rows: 1

    * - Legacy
      - Management command
    * - ``docker ps``
      - ``docker container ls``
    * - ``docker ps -a``
      - ``docker container ls -a``
    * - ``docker rm``
      - ``docker container rm``
    * - ``docker images``
      - ``docker image ls``
    * - ``docker rmi``
      - ``docker image rm``
    * - ``docker pull``
      - ``docker image pull``

This immediately reminded me of `Git`_. Git has what the community calls
"porcelain" commands — the friendly, high-level ones like :bash:`git add`,
:bash:`git commit`, :bash:`git push` — and "plumbing" commands — the
lower-level ones that power everything underneath. You mostly use the porcelain;
the plumbing is there if you need to go deeper.

Docker's management commands are the porcelain equivalent. More structured,
more legible, more consistent. The legacy commands are shorthand that stuck
around because old habits die hard and backwards compatibility matters.

Neither is wrong. Both work. I started preferring the management commands
because they make intent obvious, especially when you're still learning.
:console:`$ docker container rm` tells you immediately what kind of thing
you're deleting. :console:`$ docker rm` just... doesn't.

.. rubric:: :fas:`broom far` Clean slate
    :class: pre-title-text

.. _nuclear-cleanup:

--------------------------------------------------------------------------------
Nuclear cleanup.
--------------------------------------------------------------------------------

.. rubric:: When you want to start completely from scratch.
    :class: subtitle-text

By the end of October, I had developed a proper rhythm with Docker. But every
so often, I'd do a big experimental session — trying different images, testing
random configurations, running things just to see what happened — and I'd want
to wipe everything and start clean.

:console:`$ docker system prune` is the sledgehammer for exactly this.

.. code-block:: console

    $ docker system prune
    WARNING! This will remove:
      - all stopped containers
      - all networks not used by at least one container
      - all dangling images
      - all dangling build cache

    Are you sure you want to continue? [y/N]

It removes stopped containers, unused networks, dangling images, and build
cache in one go. By default it won't touch images that are tagged or currently
in use by a running container, so it's safer than it sounds.

If you want to go even further and remove all unused images as well:

.. code-block:: console

    $ docker system prune -a

And if you want to skip the confirmation prompt, which is handy in scripts:

.. code-block:: console

    $ docker system prune -f

I started running :console:`$ docker system prune` at the end of every
experimental session, like clearing a whiteboard before moving on.

.. rubric:: :fas:`leaf far` A month in the rearview
    :class: pre-title-text

.. _what-i-actually-learned:

--------------------------------------------------------------------------------
What I actually learned.
--------------------------------------------------------------------------------

Looking back at that month, what I actually learned wasn't really about Docker.
It was about not using a :abbr:`CLI (Command Line Interface)` blindly.

My first week was pure copy-paste. :console:`$ docker run`, see something
happen, move on. No understanding of what was being created, what was left
behind, or why. The second, third, and fourth week were the corrective phase —
understanding the lifecycle of a container, managing what I was creating,
learning which flags existed and *why* they existed.

The pattern I kept noticing was this: most Docker problems that beginners run
into — disk space filling up, servers not being reachable, containers that
can't be told apart — are solved by flags that simply weren't mentioned in
whatever quick-start guide got them started. ``--rm``, ``-d``, ``-p``,
``--name``, ``-e``. None of these are advanced features. They're practically
required for normal use. They just don't show up in *"Getting started with
Docker in 5 minutes"*.

None of this is complicated, either. It just takes a month of making the
mistakes to understand why each one matters. Every dead container I cleaned up,
every port mapping I finally got right, every random name I replaced with
something sensible — each of those small frustrations was a lesson I couldn't
have read my way to.

I suppose that's the thing about :abbr:`CLI (Command Line Interface)` tools in
general. The documentation tells you what the flags do. Only the mistakes teach
you why you need them.

.. _Docker: https://www.docker.com/
.. _containers: https://en.wikipedia.org/wiki/Container_(virtualization)/
.. _images: https://www.techtarget.com/searchitoperations/definition/Docker-image/
.. _StackOverflow: https://stackoverflow.com/
.. _Rust: https://rust-lang.org
.. _Docker Hub: https://hub.docker.com/
.. _Git: https://git-scm.com/
