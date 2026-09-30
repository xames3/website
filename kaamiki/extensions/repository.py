"""\
GitHub Repository Directive
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 29 October, 2025
Last updated on: 29 September, 2026

A `repository` directive that renders a GitHub project as a card::

    .. repository:: xames3/website
       :stars:

The card comes from `repository.html.jinja`. The counts themselves are
fetched by `theme.js` when the card scrolls into view.
"""

from __future__ import annotations

import re
import typing as t

import docutils.nodes as nodes
from docutils.parsers import rst

from kaamiki.extensions.utils import render

name: t.Final[str] = "repository"
template: t.Final[str] = "repository.html.jinja"
OWNER_NAME: re.Pattern[str] = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?/(?!\.{1,2}$)[A-Za-z0-9_.-]{1,100}$"
)


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

        The argument has to be a GitHub `owner/name`, since the card
        asks GitHub's API for it by that name. Anything else would ask
        for a repository that isn't there and show 0 for good, so it
        fails the directive instead.

        :return: A list holding the one `raw` node.
        :raises rst.DirectiveError: When the argument isn't an
            `owner/name`.
        """
        stars = "stars" in self.options
        forks = "forks" in self.options
        project = self.arguments.pop().strip()
        if not OWNER_NAME.match(project):
            raise self.error(
                f"repository needs a GitHub owner/name, like"
                f" xames3/xsnumpy; got {project!r}"
            )
        self.options["project"] = project
        self.options["stars"] = stars or not forks
        self.options["forks"] = forks or not stars
        attributes: dict[str, str] = {}
        attributes["source"] = f"https://github.com/{self.options['project']}"
        attributes["text"] = render(template, **self.options)
        attributes["format"] = "html"
        return [nodes.raw(**attributes)]
