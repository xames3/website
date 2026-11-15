.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 11 October 2026
.. Last updated on: 11 November 2026

:km-page-title: Kaamiki
:km-page-description: A dark Sphinx theme and a set of extensions for teaching
    with code.
:km-page-type: article
:km-header-subheader: The Sphinx theme and extensions running this website.
:km-feedback-title: I'd love to hear your feedback.
:km-feedback-description: Let me know what you think of Kaamiki.
:km-feedback-button: Share feedback
:km-feedback-icon: fa-message-exclamation
:km-feedback-split:

.. _kaamiki-docs:

===============================================================================
:fa-icon:regular:`badge-check` Kaamiki
===============================================================================

.. rst-class:: km-text-lead

    The Sphinx theme and extensions behind this website, and how to use them on
    yours.

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3/website

Kaamiki is a dark Sphinx theme and a set of extensions for teaching with code.
It can step a reader through a snippet while the code runs beside it, show the
versions a piece of code went through, fold content under a title, put it in
tabs or lay it out in columns. Every page of this website is built with it, and
everything below is live.

.. _kaamiki-a-taste-of-kaamiki:

-------------------------------------------------------------------------------
A taste of it.
-------------------------------------------------------------------------------

.. columns:: 2
    :gap: medium
    :valign: top

    .. column::

        .. tabs::

            .. tab:: pip

                ``pip install kaamiki-sphinx-theme``

            .. tab:: uv

                ``uv add kaamiki-sphinx-theme``

    .. column::

        .. accordion:: What does the install give me?

            A theme, directives, roles and settings, under one name.

.. button:: https://github.com/xames3/website
    :fa-icon: fa-brands fa-github

    View the source

.. _kaamiki-everything-you-can-do-with-it:

-------------------------------------------------------------------------------
Everything you can do with it.
-------------------------------------------------------------------------------

.. block:: Installing
    :size: medium
    :doc: installation
    :preheader: :fa-icon:regular:`download` Start here

    One package, named twice in your ``conf.py``.

.. block:: Directives
    :size: medium
    :doc: directives/index
    :preheader: :fa-icon:regular:`cubes` Build with them

    Bylines, buttons, tabs, columns, videos and code that runs, each one
    shown working.

.. block:: Roles
    :size: medium
    :doc: roles
    :preheader: :fa-icon:regular:`pen-to-square` Mark a sentence

    A highlighter, a pencil line, a counter and a word that changes.

.. block:: Settings
    :size: medium
    :doc: settings
    :preheader: :fa-icon:regular:`sliders` Make it yours

    Everything you can change from ``conf.py``, grouped by what it does.

.. block:: Page fields
    :size: medium
    :doc: page-fields
    :preheader: :fa-icon:regular:`file-lines` Per page

    Change a link preview, the feedback box or the layout for one page.

.. block:: Advanced
    :size: medium
    :doc: advanced
    :preheader: :fa-icon:regular:`gear` Go deeper

    Custom properties, template overrides, what a build writes and more.

.. block:: Examples
    :size: medium
    :doc: examples/motion
    :preheader: :fa-icon:regular:`gear` Go deeper

    Custom properties, template overrides, what a build writes and more.

.. _kaamiki-reason-behind-writing-kaamiki:

-------------------------------------------------------------------------------
Why I wrote Kaamiki.
-------------------------------------------------------------------------------

My students kept telling me they couldn't follow my code. So I wrote a
directive that steps through it a line at a time with the values beside it, and
then one that shows how code changed. The rest came after: an accordion, tabs,
columns and blocks of my own, and options that check what they're given.
:doc:`The story of the November release </changelogs/november-2026>` tells it.

.. toctree::
    :hidden:
    :maxdepth: 1
    :caption: Getting started

    installation

.. toctree::
    :hidden:
    :maxdepth: 1
    :caption: Reference

    directives/index
    roles
    settings
    page-fields
    classes

.. toctree::
    :hidden:
    :maxdepth: 1
    :caption: Advanced

    advanced

.. toctree::
    :hidden:
    :maxdepth: 1
    :caption: Combinations

    combinations/index

.. toctree::
    :hidden:
    :maxdepth: 1
    :caption: Examples

    examples/overrides
    examples/feedback
    examples/link-preview
    examples/icons
    examples/motion
