.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 30 October 2026
.. Last updated on: 19 November 2026

:km-page-title: Embeds, everywhere
:km-page-description: Every option of the embed directive on and off, from
    content and from files, with icons, with Kaamiki's own classes and inside
    every container.
:km-page-type: article
:km-header-subheader: Every way to put your own HTML on a page
:km-feedback-title: Did I miss a way to combine them?
:km-feedback-description: Tell me what you tried with an embed that didn't
    work.
:km-feedback-button: Tell me
:km-feedback-icon: fa-code

.. _combos-embed:

===============================================================================
:fa-icon:regular:`code` Embeds, everywhere
===============================================================================

.. rst-class:: km-text-lead

    Your own HTML, in every combination.

An embed puts a block of your own HTML on a page, with placeholders that
options fill. This page writes it with every option on and off, from content
and from files, with icons and Kaamiki's own classes inside it and inside every
container, so the markup and the result sit side by side.

.. _combos-embed-from-content-with-placeholders:

-------------------------------------------------------------------------------
From content, with placeholders.
-------------------------------------------------------------------------------

Plain HTML.

.. embed:: iframe

    <p style="padding: 1rem; background: seagreen">
        No placeholders.
    </p>

.. code-block:: rst

    .. embed:: iframe

        <p style="padding: 1rem; background: seagreen">
            No placeholders.
        </p>

Two options, two placeholders.

.. embed:: iframe
    :colour: seagreen
    :message: Hello from an embed

    <p style="padding: 1rem; background: {{ colour }}">
        {{ message }}
    </p>

.. code-block:: rst

    .. embed:: iframe
        :colour: seagreen
        :message: Hello from an embed

        <p style="padding: 1rem; background: {{ colour }}">
            {{ message }}
        </p>

A value is escaped for where it lands.

.. embed:: iframe
    :message: <b> and "quotes" are escaped

    <p>{{ message }}</p>

.. code-block:: rst

    .. embed:: iframe
        :message: <b> and "quotes" are escaped

        <p>{{ message }}</p>

``:class:``

.. embed:: iframe
    :class: km-tone-blue

    <p>Extra classes on the wrapping div.</p>

.. code-block:: rst

    .. embed:: iframe
        :class: km-tone-blue

        <p>Extra classes on the wrapping div.</p>

.. _combos-embed-from-a-file:

-------------------------------------------------------------------------------
From a file.
-------------------------------------------------------------------------------

A file, with placeholders, a stylesheet and a script (``:css:`` and ``:js:``).

.. embed:: /assets/html/combos-card.html
    :title: A card from a file
    :message: Its text came from an option.
    :css: combos/embed-demo.css
    :js: combos/embed-demo.js

.. code-block:: rst

    .. embed:: /assets/html/combos-card.html
        :title: A card from a file
        :message: Its text came from an option.
        :css: combos/embed-demo.css
        :js: combos/embed-demo.js

``:encoding:``, for a file that isn't UTF-8.

.. embed:: /assets/files/combos-latin1.html
    :encoding: latin-1

.. code-block:: rst

    .. embed:: /assets/files/combos-latin1.html
        :encoding: latin-1

A bigger file: the sidebar copy from the icons page.

.. embed:: /assets/html/icons-sidebar.html

.. code-block:: rst

    .. embed:: /assets/html/icons-sidebar.html

.. _combos-embed-with-icons:

-------------------------------------------------------------------------------
With icons.
-------------------------------------------------------------------------------

Font Awesome in the HTML itself.

.. embed:: iframe

    <p><i class="fa-regular fa-star"></i> An icon before,
       an icon <i class="fa-solid fa-heart km-tone--red"></i> inside
       and one after <i class="fa-brands fa-github"></i></p>

.. code-block:: rst

    .. embed:: iframe

        <p><i class="fa-regular fa-star"></i> An icon before,
           an icon <i class="fa-solid fa-heart km-tone--red"></i> inside
           and one after <i class="fa-brands fa-github"></i></p>

An icon named by an option.

.. embed:: iframe
    :icon: fa-regular fa-star

    <p><i class="{{ icon }}"></i> The icon came from an option.</p>

.. code-block:: rst

    .. embed:: iframe
        :icon: fa-regular fa-star

        <p><i class="{{ icon }}"></i> The icon came from an option.</p>

.. _combos-embed-with-kaamikis-own-classes:

-------------------------------------------------------------------------------
With Kaamiki's own classes.
-------------------------------------------------------------------------------

The page's classes work inside the HTML.

.. embed:: iframe

    <p class="km-text-lead">A lead paragraph.</p>
    <p class="km-tone-green">A green paragraph.</p>
    <p class="km-text--subheader">A subheader line.</p>

.. code-block:: rst

    .. embed:: iframe

        <p class="km-text-lead">A lead paragraph.</p>
        <p class="km-tone-green">A green paragraph.</p>
        <p class="km-text--subheader">A subheader line.</p>

An iframe, with its own document.

.. embed:: iframe

    <iframe srcdoc="<p style='font-family: sans-serif'>An iframe.</p>"
            width="100%" height="60"></iframe>

.. code-block:: rst

    .. embed:: iframe

        <iframe srcdoc="<p style='font-family: sans-serif'>An iframe.</p>"
                width="100%" height="60"></iframe>

.. _combos-embed-inside-every-other-container:

-------------------------------------------------------------------------------
Inside every other container.
-------------------------------------------------------------------------------

An embed goes anywhere a paragraph does. Here it sits in each container, with
the source under the result.

In an accordion
^^^^^^^^^^^^^^^

.. accordion:: An accordion that holds it
    :open:

    .. embed:: iframe

        <p style="padding: 1rem; background: seagreen">
            A block of HTML.
        </p>

.. code-block:: rst

    .. accordion:: An accordion that holds it
        :open:

        .. embed:: iframe

            <p style="padding: 1rem; background: seagreen">
                A block of HTML.
            </p>

In a tab
^^^^^^^^

.. tabs::

    .. tab:: Holds it
        :selected:

        .. embed:: iframe

            <p style="padding: 1rem; background: seagreen">
                A block of HTML.
            </p>

    .. tab:: Another tab

        Nothing in this one.

.. code-block:: rst

    .. tabs::

        .. tab:: Holds it
            :selected:

            .. embed:: iframe

                <p style="padding: 1rem; background: seagreen">
                    A block of HTML.
                </p>

        .. tab:: Another tab

            Nothing in this one.

In a column
^^^^^^^^^^^

.. columns:: 2
    :gap: medium
    :valign: top

    .. column::

        .. embed:: iframe

            <p style="padding: 1rem; background: seagreen">
                A block of HTML.
            </p>

    .. column::

        Another column.

.. code-block:: rst

    .. columns:: 2
        :gap: medium
        :valign: top

        .. column::

            .. embed:: iframe

                <p style="padding: 1rem; background: seagreen">
                    A block of HTML.
                </p>

        .. column::

            Another column.

In a block
^^^^^^^^^^

.. block:: A block that holds it
    :size: large

    .. embed:: iframe

        <p style="padding: 1rem; background: seagreen">
            A block of HTML.
        </p>

.. code-block:: rst

    .. block:: A block that holds it
        :size: large

        .. embed:: iframe

            <p style="padding: 1rem; background: seagreen">
                A block of HTML.
            </p>

In a note
^^^^^^^^^

.. note::

    .. embed:: iframe

        <p style="padding: 1rem; background: seagreen">
            A block of HTML.
        </p>

.. code-block:: rst

    .. note::

        .. embed:: iframe

            <p style="padding: 1rem; background: seagreen">
                A block of HTML.
            </p>

In a list item
^^^^^^^^^^^^^^

- A list item that holds it:

  .. embed:: iframe

      <p style="padding: 1rem; background: seagreen">
          A block of HTML.
      </p>

.. code-block:: rst

    - A list item that holds it:

      .. embed:: iframe

          <p style="padding: 1rem; background: seagreen">
              A block of HTML.
          </p>

.. _combos-embed-roles-around-it:

-------------------------------------------------------------------------------
Roles around it.
-------------------------------------------------------------------------------

An embed is HTML, so roles go in the text around it:

Before the embed, :sharpie:`highlighted`.

.. embed:: iframe

    <p style="padding: 1rem; background: seagreen">
        A block of HTML.
    </p>

After the embed, :sharpie:`highlighted`.

.. code-block:: rst

    Before the embed, :sharpie:`highlighted`.

    .. embed:: iframe

        <p style="padding: 1rem; background: seagreen">
            A block of HTML.
        </p>

    After the embed, :sharpie:`highlighted`.

Before the embed, :underline:`underlined`.

.. embed:: iframe

    <p style="padding: 1rem; background: seagreen">
        A block of HTML.
    </p>

After the embed, :underline:`underlined`.

.. code-block:: rst

    Before the embed, :underline:`underlined`.

    .. embed:: iframe

        <p style="padding: 1rem; background: seagreen">
            A block of HTML.
        </p>

    After the embed, :underline:`underlined`.

Before the embed, :ticker:`2025?short`.

.. embed:: iframe

    <p style="padding: 1rem; background: seagreen">
        A block of HTML.
    </p>

After the embed, :ticker:`2025?short`.

.. code-block:: rst

    Before the embed, :ticker:`2025?short`.

    .. embed:: iframe

        <p style="padding: 1rem; background: seagreen">
            A block of HTML.
        </p>

    After the embed, :ticker:`2025?short`.

Before the embed, :roll:`this|that|the other`.

.. embed:: iframe

    <p style="padding: 1rem; background: seagreen">
        A block of HTML.
    </p>

After the embed, :roll:`this|that|the other`.

.. code-block:: rst

    Before the embed, :roll:`this|that|the other`.

    .. embed:: iframe

        <p style="padding: 1rem; background: seagreen">
            A block of HTML.
        </p>

    After the embed, :roll:`this|that|the other`.
