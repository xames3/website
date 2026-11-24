.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 19 October 2026
.. Last updated on: 23 November 2026

:km-page-title: Overriding settings from a page
:km-page-description: A page that changes Kaamiki's page furniture for itself.
:km-page-type: article
:km-header-subheader: Four switches, flipped from one page
:km-feedback-title: Did the switches make sense?
:km-feedback-description: Tell me which override you'd want to see here.
:km-feedback-button: Tell me
:km-toctree-in-header: false
:km-show-breadcrumbs: false
:km-show-previous-next-pages:
:km-show-scrolltop:

.. _kaamiki-example-overrides:

===============================================================================
:fa-icon:duotone:`toggle-on` Overriding settings from a page
===============================================================================

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3
    :shade: orange

This page sets four fields at the very top of its source:

.. code-block:: rst

    :km-toctree-in-header: false
    :km-show-breadcrumbs: false
    :km-show-previous-next-pages:
    :km-show-scrolltop:

Compare it with the :doc:`settings page <../settings>`, which sets none of
them. With the breadcrumbs gone here, that link is also the way back.

.. list-table::
    :header-rows: 1
    :widths: 30 20 25 25

    * - Field
      - Site setting
      - Default
      - On this page
    * - ``:km-toctree-in-header: false``
      - not set
      - Navigation in the header
      - Navigation in a sidebar
    * - ``:km-show-breadcrumbs: false``
      - not set
      - Trail shown
      - Trail hidden
    * - ``:km-show-previous-next-pages:``
      - not set
      - Cards shown
      - Buttons shown, no cards
    * - ``:km-show-scrolltop:``
      - not set
      - Button hidden
      - Button shown

The first two switch off something that's on by default. The last two switch
on something that's off by default, which is why they have no value. A bare
field means on.

Look at the top of this page and then at the settings page. Here the navigation
sits in a sidebar on the left and the header has no dropdowns. There it's the
other way round. On a phone you won't see a difference, since both pages keep
the navigation in the menu.

The back-to-top button only appears once you've scrolled down a little, so the
rest of this page is here to give you something to scroll. The links to the
previous and next pages are at the very bottom.

.. _kaamiki-example-overrides-site:

-------------------------------------------------------------------------------
Doing it for every page.
-------------------------------------------------------------------------------

To switch the same things for the whole site, set them in ``conf.py`` instead:

.. code-block:: python

    kaamiki.conf.show.breadcrumbs = False
    kaamiki.conf.show.previous_next_pages = True
    kaamiki.conf.show.scrolltop = True
    kaamiki.conf.toctree.in_header = False

Every page now behaves like this one. A page that wants the old behaviour back
sets the opposite field, for instance ``:km-toctree-in-header:`` with no value
to put the navigation back in the header.

.. _kaamiki-example-overrides-mix:

-------------------------------------------------------------------------------
Mixing both.
-------------------------------------------------------------------------------

The two levels combine freely. A page only has to mention what it wants to
change, and everything else follows the site. If a page has
``:km-show-scrolltop:`` and the site has ``kaamiki.conf.show.scrolltop =
False``, that page has the button and all others don't. If it's the other way
round, with the site on and the page saying ``:km-show-scrolltop: false``, only
that page loses it.
