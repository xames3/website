"""\
GitHub Repository Directive
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 29 October, 2025
Last updated on: 10 September, 2026

This module defines a custom `repository` directive for the Kaamiki
Sphinx Theme. The directive allows embedding GitHub repository details
on the document.

The `repository` directive is designed to extend reStructuredText (rST)
capabilities by injecting structured metadata about the content, which
can be styled or processed further using Jinja2 templates.

The `repository` directive can be used in reStructuredText documents as
follows::

    .. code-block:: rst

        .. repository:: xames3/website

The above snippet will be processed and rendered according to the
theme's Jinja2 template, producing a final HTML output.

.. versionadded:: 10.9.2026

    `:stars:` and `:forks:` gate their counters. Naming one shows only
    that one, naming neither shows both. They were accepted but ignored
    before, and `:issues:` never had a counter to point at.

.. versionchanged:: 10.9.2026

    Rendering goes through `utils.render`, one shared Jinja environment
    for the whole theme with autoescaping switched on. The old per-
    module templates had escaping off, so a project name carrying an
    `&`, a `<` or a stray quote quietly emitted broken markup.

.. deprecated:: 10.9.2026

    [1] The module-level `here`, `templates` and `html` path fiddling
        has moved out to `utils`, along with the `jinja2` import. Every
        directive was opening its own template at import time and
        building a bare `jinja2.Template` off it, which is a daft thing
        to do seven times over. `template` is now just the filename.
    [2] The `:issues:` option is gone. The widget renders stars and
        forks, so an issues flag pointed at a counter that was never in
        the template.
    [3] Dropped the `node` class and the `visit`/`depart` pair. This
        directive hands back a `nodes.raw` and never goes anywhere near
        a translator, so all three were dead weight that only existed to
        keep the registration loop happy.
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
from docutils.parsers import rst

from kaamiki.extensions.utils import render

name: t.Final[str] = "repository"
template: t.Final[str] = "repository.html.jinja"


class directive(rst.Directive):
    """Custom `repository` directive for reStructuredText.

    This class defines the behaviour of the `repository` directive,
    including how it processes options and content and how it
    generates nodes to be inserted into the document tree.

    The directive supports the following options::

        - `stars`: Show the stargazer count.
        - `forks`: Show the fork count.

    Both counts are shown when neither flag is given, which is what
    the directive did before either flag meant anything.
    """

    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        "stars": rst.directives.flag,
        "forks": rst.directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        """Parse directive options and create an `repository` node.

        This method gathers all options provided by the user (if any)
        in the `repository` directive, constructs a new `node`
        instance and returns it wrapped in a list.

        The returned node is then placed into the document tree at the
        directive's location. Further processing will convert the node
        into HTML or other formats.

        :return: A list containing a single `node` element.

        .. versionchanged:: 10.9.2026

            [1] Renders through `utils.render`, so the project name is
                escaped on its way into the template.
            [2] `:stars:` and `:forks:` now actually gate their
                counters. Naming a flag shows only that one; naming
                neither shows both, as before.
        """
        stars = "stars" in self.options
        forks = "forks" in self.options
        self.options["project"] = self.arguments.pop().strip()
        self.options["stars"] = stars or not forks
        self.options["forks"] = forks or not stars
        attributes: dict[str, str] = {}
        attributes["text"] = render(template, **self.options)
        attributes["format"] = "html"
        return [nodes.raw(**attributes)]
