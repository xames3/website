"""\
GitHub Repository Directive
===========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 29 October 2025
Last updated on: 15 November 2026

A `repository` directive that shows a GitHub project with its numbers::

    .. repository:: octocat/Hello-World
       :hide-forks:

       My first repository on GitHub.

Without options, the two numbers show. The text below the directive
shows below the name and the numbers.
"""

from __future__ import annotations

import re
import typing as t

import docutils.nodes as nodes
from docutils.parsers import rst

from kaamiki.extensions.utils import KaamikiDirective
from kaamiki.extensions.utils import Option
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import opens_new_tab
from kaamiki.extensions.utils import paragraph
from kaamiki.extensions.utils import phrase
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import worded

template: t.Final[str] = "directives/repository.html.jinja"
OWNER: t.Final[re.Pattern[str]] = re.compile(
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})"
)
REPO: t.Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9._-]{1,100}")


class Repository(KaamikiDirective, motion=True):
    """The `repository` directive.

    Options::

        - `hide-stars`: Do not show the number of stargazers.
        - `hide-forks`: Do not show the number of forks.
        - `speed`: The speed of its motion, relative to the site,
          one of `0.25`, `0.5`, `0.75`, `1`, `1.5`, `2`, `3` or
          `4`. `2` is two times as fast.
        - `no-motion`: Do not move it.
        - `name`: A name for links.
        - `class`: More classes for the repository.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = False
    hide_stars = Option(rst.directives.flag)
    hide_forks = Option(rst.directives.flag)

    class Node(nodes.Element):
        """The repository and its parsed text, which `visit` writes."""

    def build(self) -> list[nodes.Node]:
        """Make the node of the repository.

        :return: The node, the `raw` node for the link checker, and
            what the parser reported. The argument is `owner/name`.
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
            self.fail(
                "expected owner/name like octocat/Hello-World, got"
                f" {project!r}"
            )
        source = f"https://github.com/{owner}/{repo}"
        attributes: dict[str, t.Any] = {
            "project": project,
            "stars": not self.hide_stars,
            "forks": not self.hide_forks,
            "classes": self.classes,
            "new_tab": opens_new_tab(source, self.config),
        }
        written = "\n".join(self.content).strip()
        body, messages = paragraph(self, written, "text")
        if written:
            worded(self, body, "a text")
        node = self.locate(self.Node("", body, **attributes))
        self.add_name(node)
        return [node, *trail(self, {"url": source}, ("url",)), *messages]

    @staticmethod
    def plain(node: Repository.Node) -> list[nodes.Node]:
        """Write a repository as words, for a builder without HTML.

        :param node: The node of the repository.
        :return: A paragraph with its name and a link to the project,
            and a paragraph with the text below it.
        """
        url = f"https://github.com/{node['project']}"
        link = nodes.reference("", url, refuri=url)
        found: list[nodes.Node] = [
            nodes.paragraph("", "", nodes.Text(f"{node['project']} "), link)
        ]
        found += [
            nodes.paragraph("", "", *each.children)
            for each in node.children
            if isinstance(each, phrase) and each.children
        ]
        return found


html.draws(Repository.Node, template)
