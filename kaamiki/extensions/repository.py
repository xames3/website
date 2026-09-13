"""\
GitHub Repository Directive
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 29 October, 2025
Last updated on: 12 September, 2026

A `repository` directive that renders a GitHub project as a card::

    .. repository:: xames3/website
       :stars:

The card comes from `repository.html.jinja`. The counts themselves are
fetched by `theme.js` when the card scrolls into view.

.. versionadded:: 10.9.2026

    `:stars:` and `:forks:` gate their counters. Naming one shows only
    that one, naming neither shows both. They were accepted but ignored
    before, and `:issues:` never had a counter to point at.

.. versionchanged:: 10.9.2026

    Rendering goes through `utils.render`, which has autoescaping on.
    The per-module templates it replaced had it off, so a project name
    carrying an `&`, a `<` or a stray quote emitted broken markup.

.. deprecated:: 10.9.2026

    [1] The module-level path fiddling has moved to `utils`, along with
        the `jinja2` import. `template` is now just the filename.
    [2] The `:issues:` option is gone. The widget renders stars and
        forks, so an issues flag pointed at a counter the template
        never had.
    [3] Dropped the `node` class and the `visit`/`depart` pair. This
        directive hands back a `nodes.raw` and never reaches a
        translator, so all three only existed to keep the registration
        loop happy.
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
from docutils.parsers import rst

from kaamiki.extensions.utils import render

name: t.Final[str] = "repository"
template: t.Final[str] = "repository.html.jinja"


class directive(rst.Directive):
    """The `repository` directive.

    Options::

        - `stars`: Show the stargazer count.
        - `forks`: Show the fork count.

    Naming neither shows both, which is what the directive did before
    either flag meant anything.
    """

    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        "stars": rst.directives.flag,
        "forks": rst.directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        """Render the card and return it as a raw node.

        :return: A list holding the one `raw` node.

        .. versionchanged:: 10.9.2026

            [1] Renders through `utils.render`, so the project name is
                escaped on its way into the template.
            [2] `:stars:` and `:forks:` now actually gate their
                counters. Naming a flag shows only that one; naming
                neither shows both, as before.
            [3] The `raw` node carries the repository URL as its
                `source`, which is where `linkcheck` looks. Every
                widget was being skipped by the link checker.
        """
        stars = "stars" in self.options
        forks = "forks" in self.options
        self.options["project"] = self.arguments.pop().strip()
        self.options["stars"] = stars or not forks
        self.options["forks"] = forks or not stars
        attributes: dict[str, str] = {}
        attributes["source"] = f"https://github.com/{self.options['project']}"
        attributes["text"] = render(template, **self.options)
        attributes["format"] = "html"
        return [nodes.raw(**attributes)]
