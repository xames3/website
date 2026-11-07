"""\
GitHub Repository Directive
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 29 October 2025
Last updated on: 07 November 2026

A `repository` directive that renders a GitHub project as a block::

    .. repository:: xames3/website
       :hide-forks:

       The source of this website.
"""

import re
import typing as t

import docutils.nodes as nodes
from docutils.parsers import rst

from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import located
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import opens_new_tab
from kaamiki.extensions.utils import paragraph
from kaamiki.extensions.utils import phrase
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import visitor
from kaamiki.extensions.utils import worded

name: t.Final[str] = "repository"
template: t.Final[str] = "directives/repository.html.jinja"
OWNER: t.Final[re.Pattern[str]] = re.compile(
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})"
)
REPO: t.Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9._-]{1,100}")


class Repository(nodes.Element):
    """The repository and its parsed text, waiting for `visit`."""


class directive(rst.Directive):
    """The `repository` directive.

    Options::

        - `hide-stars`: Leave out the stargazer count.
        - `hide-forks`: Leave out the fork count.
        - `name`: A name to link to.
        - `class`: More classes for the block.

    Both counts are shown without them. Any text written below the
    directive is shown under the name and counts.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "hide-stars": rst.directives.flag,
        "hide-forks": rst.directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the text and return the repository's node.

        The argument is a GitHub `owner/name`, since the block asks
        GitHub's API for it.

        :return: The node, followed by the `raw` node for the link
            checker and anything the text reported.
        """
        project = self.arguments.pop().strip()
        owner, slash, repo = project.partition("/")
        if (
            not slash
            or not OWNER.fullmatch(owner)
            or not REPO.fullmatch(repo)
            or repo in (".", "..")
            or repo.endswith(".git")
        ):
            raise self.error(
                f"repository: expected owner/name like xames3/website, got "
                f"{project!r}"
            )
        source = f"https://github.com/{owner}/{repo}"
        config = self.state.document.settings.env.config
        attributes: dict[str, t.Any] = {}
        attributes["project"] = project
        attributes["stars"] = "hide-stars" not in self.options
        attributes["forks"] = "hide-forks" not in self.options
        attributes["classes"] = self.options.get("class", [])
        attributes["new_tab"] = opens_new_tab(source, config)
        text = "\n".join(self.content).strip()
        body, messages = paragraph(self, text, "text")
        if text:
            worded(self, body, "a text")
        element = located(self, Repository("", body, **attributes))
        named(self, element)
        return [element, *trail({"url": source}, ("url",)), *messages]


def plain(node: Repository) -> list[nodes.Node]:
    """Write a repository as words, for a builder that draws no HTML.

    :param node: The repository's node.
    :return: A paragraph with its name and the address of the project,
        written as a link to itself, and one with the text below it.
    """
    url = f"https://github.com/{node['project']}"
    link = nodes.reference("", url, refuri=url)
    found: list[nodes.Node] = [
        nodes.paragraph("", "", nodes.Text(f"{node['project']} "), link)
    ]
    found += [
        nodes.paragraph("", "", *_.children)
        for _ in node.children
        if isinstance(_, phrase) and _.children
    ]
    return found


visit = visitor(template)


node = Repository
