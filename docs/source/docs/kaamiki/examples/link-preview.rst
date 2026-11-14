.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 19 October 2026
.. Last updated on: 08 November 2026

:km-page-title: Setting a link preview
:km-page-description: A page with its own link preview.
:km-page-type: article
:km-page-card: summary
:km-header-subheader: What a page gets when it sets its own
:km-feedback-title: Is a preview tag missing?
:km-feedback-description: Tell me which tag you'd want a page to set.
:km-feedback-button: Tell me

.. _kaamiki-example-link-preview:

===============================================================================
Setting a link preview
===============================================================================

This page sets its preview from the top of its source:

.. code-block:: rst

    :km-page-title: Setting a link preview
    :km-page-description: A page with its own link preview.
    :km-page-type: article
    :km-page-card: summary

Kaamiki turns those into the tags in the page's ``<head>``. Here are the main
ones it wrote for this page, with this website's
``kaamiki.conf.site.open_graph`` setting behind it:

.. code-block:: html

    <meta name="description" content="A page with its own link preview." />
    <meta property="og:title" content="Setting a link preview" />
    <meta property="og:type" content="article" />
    <meta property="og:site_name" content="Akshay Mestry" />
    <meta property="og:description"
        content="A page with its own link preview." />
    <meta property="og:locale" content="en_GB" />
    <meta property="og:image"
        content="https://avatars.githubusercontent.com/u/90549089?v=4" />
    <meta property="og:image:alt" content="Akshay Mestry" />
    <meta name="twitter:card" content="summary" />

The page set its title, description, type and card, so those come from the
fields. It set no image or locale, so the picture, its alt text, the locale and
the site name come from ``kaamiki.conf.site.open_graph`` in ``conf.py``. A page
that sets nothing gets all of it from the heading and its first paragraph.

The fields a page can set are ``:km-page-title:``, ``:km-page-description:``,
``:km-page-image:``, ``:km-page-image-alt:``, ``:km-page-type:``,
``:km-page-locale:`` and ``:km-page-card:``. Back to the :doc:`settings page
<../settings>`.
