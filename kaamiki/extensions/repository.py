"""\
GitHub Repository Directive
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 29 October 2025
Last updated on: 17 October 2026

A `repository` directive that renders a GitHub project as a card::

    .. repository:: xames3/website
       :hide-forks:

       The source of this website.
"""

import typing as t

import docutils.nodes as nodes
from docutils.parsers import rst

from kaamiki.extensions.utils import opens_new_tab
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import visitor

name: t.Final[str] = "repository"
template: t.Final[str] = "directives/repository.html.jinja"


class node(nodes.Element):
    """The repository and its parsed text, waiting for `visit`."""


class directive(rst.Directive):
    """The `repository` directive.

    Options::

        - `hide-stars`: Leave out the stargazer count.
        - `hide-forks`: Leave out the fork count.

    Both counts are shown without them. Any text written below the
    directive is shown under the name and counts.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        "hide-stars": rst.directives.flag,
        "hide-forks": rst.directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the text and return the repository's node.

        The argument is a GitHub `owner/name`, since the card asks
        GitHub's API for it.

        :return: The node, followed by the `raw` node for the link
            checker and anything the text reported.
        """
        owner, repo = self.arguments.pop().strip().split("/")
        source = f"https://github.com/{owner}/{repo}"
        config = self.state.document.settings.env.config
        attributes: dict[str, t.Any] = {}
        attributes["project"] = f"{owner}/{repo}"
        attributes["stars"] = "hide-stars" not in self.options
        attributes["forks"] = "hide-forks" not in self.options
        attributes["new_tab"] = opens_new_tab(source, config)
        text = "\n".join(self.content).strip()
        body, messages = parse(self, text, "text")
        element = node("", body, **attributes)
        link = nodes.raw(source=source, text="", format="html")
        return [element, link, *messages]


visit = visitor(template)
