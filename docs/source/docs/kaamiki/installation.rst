.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 19 October 2026
.. Last updated on: 19 November 2026

:km-related-header: Where next?
:km-related-docs: /docs/kaamiki/page-fields, /docs/kaamiki/settings
:km-page-title: Installing Kaamiki
:km-page-description: Install Kaamiki from PyPI as kaamiki-sphinx-theme, switch
    it on in your Sphinx project and build your first page.
:km-page-type: article
:km-header-subheader: From pip install to your first build
:km-feedback-title: Did the install go well?
:km-feedback-description: Tell me where you got stuck and I'll fix this page.
:km-feedback-button: Tell me

.. _kaamiki-installation:

===============================================================================
:fa-icon:regular:`download` Installing Kaamiki
===============================================================================

.. rst-class:: km-text-lead

    From pip install to your first build.

This page takes you from an empty Sphinx project to a built page that uses
Kaamiki.

.. _kaamiki-requirements:

-------------------------------------------------------------------------------
What you need.
-------------------------------------------------------------------------------

You need Python 3.14 or newer and Sphinx 9.1 or newer, below Sphinx 11. Kaamiki
uses newer syntax, so older versions of Python can't import it. Docutils,
Jinja2, MarkupSafe, Babel, Pygments, Beautiful Soup and lightningcss come
along with the install.

.. _kaamiki-install:

-------------------------------------------------------------------------------
Install it.
-------------------------------------------------------------------------------

The package on PyPI is ``kaamiki-sphinx-theme``. Everywhere else, in your
``conf.py`` and in Python, it's just ``kaamiki``:

.. tabs::
    :group: installer

    .. tab:: pip

        .. code-block:: console

            pip install kaamiki-sphinx-theme

    .. tab:: uv

        .. code-block:: console

            uv add kaamiki-sphinx-theme

    .. tab:: From the source

        .. code-block:: console

            git clone https://github.com/xames3/website
            cd website
            pip install -e .

If you'd like to work on Kaamiki itself, the last tab installs it in editable
mode, so your changes show up straight away. The PyPI project named ``kaamiki``
is an older package and not this theme, so install ``kaamiki-sphinx-theme``.

.. _kaamiki-enable:

-------------------------------------------------------------------------------
Switch it on.
-------------------------------------------------------------------------------

Kaamiki is two things in one package, so you name it twice in your
``conf.py``:

.. columns:: 2
    :gap: medium
    :background:
    :valign: top

    .. column::

        **html_theme** is the theme: the templates, the styles and the scripts
        that make a page look like this one.

    .. column::

        **extensions** is the extension: the directives, roles and settings
        you write in reStructuredText and in ``conf.py``.

.. code-block:: python

    extensions = ["kaamiki"]
    html_theme = "kaamiki"

You need both, and nothing else is supported. Leave one out, or put another
theme beside the extension, and the build stops with an error that says what to
change. A theme that inherits from Kaamiki isn't supported either. With the
extension and another theme the error reads:

.. code-block:: text

    html_theme: expected 'kaamiki' because 'kaamiki' is in extensions, got
    'alabaster'. The extension only works with its own theme, so set
    html_theme = 'kaamiki' in conf.py

and with the theme and no extension:

.. code-block:: text

    extensions: expected 'kaamiki' in it, the kaamiki theme needs its
    extension, so add 'kaamiki' to extensions in conf.py

Two more values help, and Kaamiki can't guess them:

.. code-block:: python

    author = "Your Name"
    html_baseurl = "https://example.com/"

``author`` is the name on bylines, and a site that leaves it out ships no
author tag. ``html_baseurl`` is your site's address, an ``http`` or ``https``
one with a host and a path and no query or fragment, with or without the slash
at the end, and it does four things:

- Links to any other host open in a new tab. Your own host stays in the same
  tab.
- Relative picture paths in link previews become absolute, which previews need.
- ``sitemap.xml`` and ``robots.txt`` get written.
- Canonical links are added to each page.

Without it Kaamiki still builds, it just skips these. A minimal ``conf.py`` is
then:

.. code-block:: python

    project = "My Project"
    author = "Your Name"
    html_baseurl = "https://example.com/"

    extensions = ["kaamiki"]
    html_theme = "kaamiki"

.. _kaamiki-first-build:

-------------------------------------------------------------------------------
Build your first page.
-------------------------------------------------------------------------------

Put this in ``index.rst`` next to your ``conf.py`` and build it:

.. tabs::

    .. tab:: index.rst

        .. code-block:: rst

            :km-page-description: My first page with Kaamiki.

            ===========
            Hello there
            ===========

            This page is built with Kaamiki.

            .. button:: https://example.com
                :scheme: green

                A button

    .. tab:: Build

        .. code-block:: console

            sphinx-build -b dirhtml . _build

Open ``_build/index.html`` in a browser. You should see the Kaamiki header, a
green button and, at the end of the page, a feedback box. The feedback box
needs somewhere to send feedback, so it only shows up once you set an email in
:doc:`settings`.

``dirhtml`` gives you clean addresses like ``/docs/kaamiki/`` instead of
``/docs/kaamiki.html``, which is what this website uses. The plain ``html``
builder works too.

.. _kaamiki-next:

-------------------------------------------------------------------------------
Where to go next.
-------------------------------------------------------------------------------

.. carousel::
    :hide-arrows:

    .. block:: Directives
        :size: small
        :doc: directives/index

        Buttons, tabs, columns and more, shown working.

    .. block:: Roles
        :size: small
        :doc: roles

        Small marks inside a sentence.

    .. block:: Settings
        :size: small
        :doc: settings

        Everything you can change from ``conf.py``.
