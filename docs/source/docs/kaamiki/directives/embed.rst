.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 19 October 2026
.. Last updated on: 19 November 2026

:km-page-title: The embed directive
:km-page-description: Put a block of your own HTML on a page, with
    placeholders that options fill and checks on where an iframe may come from.
:km-page-type: article
:km-header-subheader: A block of your own HTML
:km-feedback-title: Is an embed option missing?
:km-feedback-description: Tell me which option or check you'd want.
:km-feedback-button: Tell me

.. _kaamiki-embed:

===============================================================================
:fa-icon:regular:`code` embed
===============================================================================

.. rst-class:: km-text-lead

    Your own HTML, for the things reStructuredText can't say.

An iframe, a small widget or a styled box. The argument is ``iframe``, in
lower case, and the HTML goes below as the content. Any option you give fills
a placeholder in the HTML, written ``{{ name }}``:

.. embed:: iframe
    :colour: seagreen
    :message: Hello from an embed

    <div style="padding: 1rem; border-radius: 8px;
                background: {{ colour }}; color: white;">
        {{ message }}
    </div>

.. code-block:: rst

    .. embed:: iframe
        :colour: seagreen
        :message: Hello from an embed

        <div style="padding: 1rem; border-radius: 8px;
                    background: {{ colour }}; color: white;">
            {{ message }}
        </div>

The value is escaped for the place it lands, so a quote or a ``<`` in an option
can't break the HTML around it. In markup it's HTML-escaped, in a ``<style>``
it's CSS-escaped and in a ``<script>`` it's written as a JSON literal, and
Kaamiki tells the three apart. A ``{# note #}`` in the HTML is left out of the
page.

.. _kaamiki-embed-files:

-------------------------------------------------------------------------------
HTML from a file.
-------------------------------------------------------------------------------

A bigger embed can live in a file of its own. Use the file as the argument,
relative to the page or, with a leading ``/``, to the source directory, and
inside it. A file and content can't be used together, and a control character
in the file's name stops the build:

.. code-block:: rst

    .. embed:: ./assets/html/logos.html
        :source: /_static/data/logos.json
        :speed: slow
        :direction: left
        :css: embed.css
        :js: embed.js

``:css:`` and ``:js:`` name files under ``html_static_path``, comma-separated.
They load, in that order, on the pages that use the directive and nowhere else.
Each other option fills the placeholder of the same name in the file, so this
file has a ``{{ source }}``, a ``{{ speed }}`` and a ``{{ direction }}`` for
the data source, the speed and the direction of, for example, a scrolling row
of logos.

.. _kaamiki-result-and-source-in-tabs:

-------------------------------------------------------------------------------
The result and its source, in tabs.
-------------------------------------------------------------------------------

An embed is just a block, so it sits in a tab beside the code that makes it:

.. tabs::

    .. tab:: Result

        .. embed:: iframe
            :message: Hello

            <p><strong>{{ message }}</strong></p>

    .. tab:: Source

        .. code-block:: html

            <p><strong>{{ message }}</strong></p>

.. code-block:: rst

    .. tabs::

        .. tab:: Result

            .. embed:: iframe
                :message: Hello

                <p><strong>{{ message }}</strong></p>

        .. tab:: Source

            .. code-block:: html

                <p><strong>{{ message }}</strong></p>

.. _kaamiki-embed-checks:

-------------------------------------------------------------------------------
What it checks.
-------------------------------------------------------------------------------

- An option that nothing in the HTML asks for stops the build. It's almost
  always a misspelt name.
- A placeholder with no option to fill it stops the build too, with
  ``embed: {{ key }} expected an option to fill it, got none``. It isn't a
  warning, since a placeholder is almost always a misspelt option.
- A placeholder may spell its name with underscores or hyphens, so
  ``{{ expected_count }}`` is filled by ``:expected-count:``.
- Inside a script, a value is read as a number or a list when it looks like
  one, so a script gets ``10`` and not ``"10"``. Everywhere else it's written
  as you wrote it, escaped as above.

.. _kaamiki-embed-settings:

-------------------------------------------------------------------------------
Settings behind it.
-------------------------------------------------------------------------------

Three settings apply to every embed, each covered in :ref:`embeds and videos
<kaamiki-settings-embeds>`:

- ``kaamiki.conf.embed.iframe_hosts`` limits which hosts an ``<iframe>`` may
  load from. With it set, an iframe from any other host stops the build.
  Without it nothing is checked. It catches a mistake and not an author set on
  getting round it: a script can build a frame in pieces, so a script that
  builds an iframe stops the build, and so do ``srcdoc`` and the tags that load
  a page some other way. The markup is read as a browser reads it, so the order
  of the attributes, a ``>`` in a quoted attribute or a backslash or extra
  slashes in the address don't get a frame past the list.
- ``kaamiki.conf.embed.css`` and ``kaamiki.conf.embed.js`` are loaded on every
  page with an embed, before the page's own ``:css:`` and ``:js:``.
- ``kaamiki.conf.embed.js_loading`` says whether those scripts are ``defer``,
  ``async`` or ``normal``.

.. code-block:: python

    kaamiki.conf.embed.iframe_hosts = ["youtube.com", "example.com"]

.. _kaamiki-embed-options:

-------------------------------------------------------------------------------
Every option.
-------------------------------------------------------------------------------

.. accordion:: The full table

    .. list-table::
        :header-rows: 1
        :widths: 26 74

        * - Option
          - What it does
        * - ``:css:``, ``:js:``
          - Files under ``html_static_path``, comma-separated, loaded on the
            pages that use the directive.
        * - ``:encoding:``
          - How the file is encoded, ``utf-8`` unless you say otherwise. It
            needs a file, and inline HTML with it stops the build.
        * - ``:name:``
          - A name to link to, as :ref:`every directive takes it
            <kaamiki-directives-common>`.
        * - ``:class:``
          - Extra classes for the ``<div>`` every embed sits in.
        * - Any other
          - A placeholder: its name, in lowercase as Docutils reads every
            option, fills the ``{{ name }}`` of the same name.
