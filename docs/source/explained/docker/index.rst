.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 August, 2025
.. Last updated on: 29 June, 2026

:og:title: A week into Docker
:og:description: Begineer's guide to Docker and containerisation
:og:type: article
:og:image: https://i.imgur.com/TL3wLY8.jpeg
:fb:title: But, I'd love to hear from you
:fb:description: What was the moment that made you realise you needed a tool
    like Docker? Or if you're new to this, what's the one thing you're hoping
    it'll solve for you?
:fb:button: Let me know
:fb:mode: split

.. _explained-a-week-into-docker:

===============================================================================
:fas:`box-isometric-tape far` A week into Docker
===============================================================================

.. rst-class:: lead

    How a week of using Docker transformed the way I manage my local
    development environments and why I think it was worth a look.

.. author:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3

.. role:: console(code)
    :language: console

This is my story from September 2020, roughly five years ago, as of writing
this article. It was in the middle of the pandemic. I was switching jobs. I
knew I would get a new machine from my next employer, but I had no idea when.

The pandemic was still at its peak and I had to make the most of what I had.
With how things were going, I knew I wouldn't get a new machine anytime soon,
so I had to improvise and make my work machine last me a while longer.

As some of you know, I love writing code. It's what I do for the most part and
during lockdown, I wrote a lot. I tried to keep myself busy with work and other
side projects and while doing that, I got my machine messy really quick. I had
multiple versions of Python, Rust, various dependencies, configs, tools and
frameworks that I won't be using after my "experimentation" phase.

I knew `Docker`_ was a thing, but I never really got around to using it. I
personally thought it was too much of a hassle to set up until I had no other
option.

So, I decided to give it a try.

.. rubric:: And here I'm today, talking about Docker.
.. rubric:: Think of this as the start of a journey we can take together.
    :class: subtitle-text

In this first chapter, I want to walk you through my initial experience with
this whole containerisation business and explain the basic ideas that finally
made sense to me. In future articles, I'll dive into the practical side of
things, like how to write a Dockerfile, manage containers and use it in your
own projects.

.. _docker-enters-the-chat:

-------------------------------------------------------------------------------
Docker enters the chat.
-------------------------------------------------------------------------------

Learning and exploring Docker wasn't initially on my bingo list, but I'm glad I
did. Since then, it has made my "dodgy" projects super-duper manageable and my
local machine still thanks me for it. I don't want to get too technical or
nerdy right now, but I want to make are we're on the same page.

Docker is a **platform** that allows you to develop, ship and run code inside
:ref:`containers <idea-behind-containers>`.

.. note::

    Docker is not the only containerisation platform, but it's perhaps the most
    popular one and that's why people synonymously use the term Docker to
    refer to containers in general. But in reality, they are not the same
    thing.

Simply put, it's basically a service that allows you to ship your application
or code in a container that has all the things it needs to run. This means your
application or code will run the same way regardless of where it's being run.
You'll get the same results on your local machine, your friend's machine, or a
server in the cloud.

.. rubric:: But what did Docker do?
.. rubric::
    Docker was introduced in 2013 and solved the classic **"it works on my
    machine"** problem.
    :class: subtitle-text

.. figure:: https://i.imgur.com/csI4fZe.png
    :alt: It works on my machine
    :figclass: zoom grayscale

In the spirit of keeping things simple, I'd say there are two main ideas around
Docker: `Docker Engine`_ and `Docker Hub`_ and let's just stick with these two
for now.

1. **Docker Engine.** This is the core part of Docker that runs on your
   machine. It creates and manages containers. In a nutshell, it's the main
   thing that makes Docker work on your machine. Like how Git is the tool
   that makes version control possible, Docker Engine is the tool that makes
   containerisation possible.

2. **Docker Hub.** This is a cloud-based registry service where you can find
   and share container images. Again, you can think of it as a GitHub or GitLab
   for Docker images. You can pull images from Docker Hub to run containers on
   your local machine, or you can push your own images to Docker Hub to share
   them with others.

.. rubric:: :fab:`bolt far` Crafting environment = Instant isolation
    :class: pre-title-text
.. rubric:: Magic of Docker Engine.

When I first started using Docker, I'll be honest, I really didn't understand
what was going on. Almost every tutorial I watched started with using the
:console:`$ docker run` command. I knew that I could type it out and
auto-magically, I'm dropped in an isolated environment where I can run my code
or do whatever I want without messing up my local machine.

.. code-block:: console

    $ docker run python:3.8 python -c "print('Hello from inside a container')"
    Unable to find image 'python:3.8' locally
    3.8: Pulling from library/python
    001c52e26ad5: Pull complete
    d9d4b9b6e964: Pull complete
    2068746827ec: Pull complete
    Digest: sha256:cba7af3b9b9183b3f46de79c9d3f4b89a71bf3...
    Status: Downloaded newer image for python:3.8
    Hello from inside a container!

But as I started using it more, I realised that there's a lot more to it and
Docker Engine is doing some really fancy stuff behind the scenes. Remember how
I mentioned my machine was getting messy with all the different versions of
Python and other dependencies?

Well, when I ran the :console:`$ docker run` command, it was Docker Engine that
was creating an isolated environment to run my experiments within it.

.. code-block:: console

    $ docker run python:3.8 python -V
    Python 3.8.20
    $ docker run python:3.9 python -V
    Python 3.9.21

These environments are what we call **containers**.

.. rubric:: :fab:`truck-fast far` From ships to shipping
    :class: pre-title-text

.. _idea-behind-containers:

-------------------------------------------------------------------------------
Idea behind Containers.
-------------------------------------------------------------------------------

In the 1950s, `Malcolm McLean`_ came up with the concept of "containerisation"
by inventing and standardising the modern shipping containers, but his idea was
to make shipping goods easier and more efficient.

What it all meant was that instead of loading and unloading goods every time
they were transferred from one mode of transport to another, they could be
packed into a standardised container that could be easily moved around.

Docker, the company, took this idea and applied it to software development. The
name "Docker" itself is inspired by the idea of shipping containers. A
container is a lightweight, standalone package that includes everything needed
to run your application code.

Each container is isolated from the others and from the host system. So, you
can run multiple containers on the same machine without them interfering with
each other.

.. _containers-are-not-vms:

-------------------------------------------------------------------------------
Containers ≠ VMs
-------------------------------------------------------------------------------

Initially, it was quite hard for me to wrap my head around the concept of
containers and sandboxing. I mean, how is it any different from a
:abbr:`GUI (Graphical User Interface)`-less `Virtual machine`_? It's acting the
same way, innit?

Well, not exactly.

You see, both :abbr:`VMs (Virtual Machines)` and containers are used to create
isolated environments, but they both do it differently. VMs run a full copy of
an operating system (guest) inside your local machine (host). At the same time,
containers share your host OS kernel.

.. admonition:: :fas:`sparkles` Quick analogy
    :class: unusual-one hint

    Think of it this way, having a VM is like renting an entire flat/apartment
    when you just need a room. Whereas using a container is like renting a room
    in a shared flat/apartment where you share some common facilities like the
    kitchen and bathroom.

    The latter is much faster and cost-effective.

To expand a bit more, a VM creates a separate copy of an operating system on
top of your existing OS using something called a `Hypervisor`_.

.. note::

    This is **not** dual-booting, where you have two OSs installed on your
    machine and you choose which one to boot into.

In a VM, you have your actual OS (host) running and inside it, you have
another OS (guest) running as a separate entity. VMs run like a regular
application on your local machine. It's like running Windows on your Mac
using `Parallels`_ or running Linux on your Windows using `VirtualBox`_.

Since a VM runs just like a regular application, it needs its resources like
CPU, memory, storage and processing power. It's thorough, but it's also heavy.

Very heavy... I mean, you're running multiple bloody OSs at the same time!

Containers, on the other hand, share the host OS' resources (kernel) and run as
isolated processes (not technically) in the user space on the host OS. In
simple terms, they are lightweight and efficient compared to VMs. They start up
quickly and use fewer resources because they don't need to boot up a whole OS.

You can run many more containers on the same hardware compared to VMs. This
makes containers ideal for deploying applications in a microservices
architecture where you have multiple small, independent services running
together.

.. rubric:: Containers and VMs, summarised.
.. rubric::
    The below table can paint a rough picture why containers are better in some
    scenarios.
    :class: subtitle-text

.. list-table::
    :header-rows: 1

    * - Feature
      - Containers
      - Virtual Machines (VMs)
    * - Isolation
      - :fas:`circle-check far yellow` Shared OS resources
      - :fas:`circle-check green` Full isolation
    * - Storage
      - :fas:`circle-check far yellow` Volatile
      - :fas:`circle-check green` Persistent
    * - Resource usage
      - :fas:`circle-check green` Low (efficient)
      - :fas:`triangle-exclamation red` High (CPU, RAM, Storage)
    * - Size
      - :fas:`circle-check green` Lightweight (MBs)
      - :fas:`triangle-exclamation red` Heavyweight (GBs)
    * - Startup speed
      - :fas:`circle-check green` Fast (seconds)
      - :fas:`circle-check far yellow` Slow (minutes)
    * - Flexibiltiy
      - :fas:`circle-check green` More flexible migrations
      - :fas:`circle-check far yellow` Limited in comparison
    * - Scalability
      - :fas:`circle-check green` Inexpensive
      - :fas:`triangle-exclamation red` Costly

.. _pulling-images-from-the-internet:

-------------------------------------------------------------------------------
Pulling images from the internet.
-------------------------------------------------------------------------------

After understanding what containers do and how they're better in comparison to
VMs, I realised why Docker is so popular among developers. I started using it
for my personal projects, but now I had another problem.

I had a messy local machine, but with multiple Docker containers with the same
Python versions. I realised I needed to clean up and manage my containers
better, or follow some best practices.

I wondered where I had been getting all these containers from in the first
place. I knew I was pulling these **containers\*** from the internet, but I had
no idea from where.

.. container:: inline-container

    .. grid:: 2

        .. grid-item::
            :columns: auto

            .. rubric:: That's when I discovered Docker Hub.

        .. grid-item::
            :columns: auto
            :class: align-right

            .. grid:: 2

                .. grid-item::

                    .. button:: https://hub.docker.com/

                        Learn more

.. rubric:: `Docker Hub`_ is a cloud-based registry service where you can find
    and share **container images**, not containers.
    :class: subtitle-text

But what's an image now? With a bit of research, I found out that a Docker
image is a lightweight executable package that includes it needs to run the
code, including the runtime, libraries, environment variables and
configuration files.

Wait, that sounds a lot like a container to me... But not quite.

A Docker image is a blueprint for creating containers. When you run a Docker
image, it creates a container based on that image. It is a read-only template
that contains the instructions for creating a container.

.. admonition:: :fas:`sparkles` Quick analogy
    :class: unusual-one hint

    In programming terms, you can think of an image as a class and a container
    as an instance of that class. You can have multiple containers (instances)
    running from the same image (class) at the same time.

And Docker Hub is where you can find and share these images. You can pull
images from Docker Hub to run containers on your local machine, or you can push
your own images to Docker Hub to share them with others.

Docker Hub has loads of pre-built images for various applications and services,
like databases, web servers, programming languages and more. This makes it
easy to get started with Docker and quickly set up your development
environment.

Yet another reason why Docker is so popular among developers.

.. _one-week-into-docker:

-------------------------------------------------------------------------------
One week into Docker.
-------------------------------------------------------------------------------

By now, I was a week into using Docker. I had a basic understanding of what
Docker and containerisation are and roughly how the whole ecosystem works. I
was excited to explore and experiment even more. Sure, I was confused in the
beginning, but I slowly started to get the hang of it. First, it was between
containers and virtual machines, then between containers and images. I think
the biggest culprits were the terminologies themselves. They are so similar
that it can get really confusing for a beginner.

But once I got the hang of it, I realised how powerful the whole concept of
containerisation is and how it can make my life easier. After a few weeks, I
realised that even containerisation isn't a new concept. It's been around and
experimented with for decades within the Linux community. There are other
containerisation implementations like `LXC`_ and `OpenVZ`_, but Docker made it
easy and accessible for everyone.

In the next chapter, I'll share my experiences of running my first container
and how it changed the way I started working on my local machine.

.. _Docker: https://www.docker.com/
.. _containers: https://en.wikipedia.org/wiki/Container_(virtualization)/
.. _Docker Engine: https://docs.docker.com/engine/
.. _Docker Hub: https://hub.docker.com/
.. _Malcolm McLean: https://en.wikipedia.org/wiki/Malcom_McLean/
.. _Virtual machine: https://www.vmware.com/topics/virtual-machine/
.. _Hypervisor: https://en.wikipedia.org/wiki/Hypervisor/
.. _Parallels: https://www.parallels.com/
.. _VirtualBox: https://www.virtualbox.org/
.. _LXC: https://linuxcontainers.org/
.. _OpenVZ: https://openvz.org/
