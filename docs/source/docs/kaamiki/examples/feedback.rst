.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 19 October 2026
.. Last updated on: 23 November 2026

:km-page-title: Changing the feedback box
:km-page-description: A page that sets its own feedback text, button and
    layout.
:km-page-type: article
:km-header-subheader: Page fields against the settings
:km-feedback-title: Did this make sense?
:km-feedback-description: Tell me which part was confusing and I'll rewrite
    it.
:km-feedback-button: Write to me
:km-feedback-subject: About %s
:km-feedback-split:

.. _kaamiki-example-feedback:

===============================================================================
:fa-icon:duotone:`message-pen` Changing the feedback box
===============================================================================

.. byline:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :target: https://github.com/xames3
    :shade: yellow

Scroll to the end of this page. The feedback box there doesn't use Kaamiki's
words, it uses these fields from the top of this page's source:

.. code-block:: rst

    :km-feedback-title: Did this make sense?
    :km-feedback-description: Tell me which part was confusing and I'll rewrite
        it.
    :km-feedback-button: Write to me
    :km-feedback-subject: About %s
    :km-feedback-split:

``:km-feedback-split:`` puts the title and the button side by side. In the
email the button opens, ``%s`` becomes this page's title, so the subject reads
"About Changing the feedback box".

Any field you leave out falls back to the ``kaamiki.conf.site.feedback``
setting in ``conf.py`` and then to Kaamiki's own words. This page leaves out
``:km-feedback-icon:``, ``:km-feedback-type:`` and ``:km-feedback-url:``, so
the button keeps the default icon and still sends an email to the address in
``kaamiki.conf.site.project``.

To send readers to a form instead of an email, add both of these:

.. code-block:: rst

    :km-feedback-type: link
    :km-feedback-url: https://example.com/feedback

Go back to the :doc:`settings page <../settings>` to compare. Its box uses the
site's words, since it sets no fields.
