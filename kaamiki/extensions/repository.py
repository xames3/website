"""\
GitHub Repository Directive
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 29 October 2025
Last updated on: 15 October 2026

A `repository` directive that renders a GitHub project as a card::

    .. repository:: xames3/website
       :hide-forks:
"""

import typing as t

import docutils.nodes as nodes
from docutils.parsers import rst

from kaamiki.extensions.utils import opens_new_tab
from kaamiki.extensions.utils import render

name: t.Final[str] = "repository"
template: t.Final[str] = "directives/repository.html.jinja"


class directive(rst.Directive):
    """The `repository` directive.

    Options::

        - `hide-stars`: Leave out the stargazer count.
        - `hide-forks`: Leave out the fork count.

    Both counts are shown without them.
    """

    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        "hide-stars": rst.directives.flag,
        "hide-forks": rst.directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        """Render the card and return it as a raw node.

        The argument is a GitHub `owner/name`, since the card asks
        GitHub's API for it.

        :return: A list holding the one `raw` node.
        """
        owner, repo = self.arguments.pop().strip().split("/")
        source = f"https://github.com/{owner}/{repo}"
        config = self.state.document.settings.env.config
        text = render(
            template,
            project=f"{owner}/{repo}",
            stars="hide-stars" not in self.options,
            forks="hide-forks" not in self.options,
            new_tab=opens_new_tab(source, config),
        )
        return [nodes.raw(source=source, text=text, format="html")]
