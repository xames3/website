"""\
Release Directive
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 30 September 2026
Last updated on: 16 November 2026

A `release` directive that writes one entry of a changelog::

    .. release:: The first release
       :version: 2026.11.8
       :article: changelogs/november-2026

       The first paragraph sums the release up.

       Added
           - What's new, a line each.
       Fixed
           - What works now.

The argument is the title, which tells what the release is about. It
is optional. Without it, the version is the title. A release is a
section, so it goes directly in a section: on the page or below a
heading. An `only` is permitted around it. It cannot go in an
accordion, a tab, a block, a column, a list or a note.

The definition lists in the content are the groups of changes. Each
term is `Added`, `Changed`, `Deprecated`, `Fixed`, `Removed`, or a
group in `kaamiki.conf.release.kinds` of the site. A list can be
anywhere in the content, and a list in a group does not change.
`kaamiki.conf.release.version_fmt` tells how a version writes its
date, and the default is `%Y.%m.%d`. A version that does not use it,
without a `:date:`, shows no date.
"""

from __future__ import annotations

import functools
import re
import typing as t
from datetime import datetime as dt

import docutils.nodes as nodes
from sphinx import addnodes
from sphinx.locale import _

from kaamiki.extensions.utils import Kaamiki
from kaamiki.extensions.utils import KaamikiDirective
from kaamiki.extensions.utils import Option
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import dated
from kaamiki.extensions.utils import day
from kaamiki.extensions.utils import document
from kaamiki.extensions.utils import ensure_articles
from kaamiki.extensions.utils import findall
from kaamiki.extensions.utils import glyph
from kaamiki.extensions.utils import hollow
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import on
from kaamiki.extensions.utils import optional
from kaamiki.extensions.utils import render
from kaamiki.extensions.utils import stored
from kaamiki.extensions.utils import values
from kaamiki.extensions.utils import worded
from kaamiki.extensions.utils.build import writes_pages
from kaamiki.extensions.utils.checks import fail
from kaamiki.extensions.utils.checks import location
from kaamiki.extensions.utils.dates import within

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment
    from sphinx.writers.html import HTMLTranslator

template: t.Final[str] = "directives/release.html.jinja"
BUTTON: t.Final[tuple[str, ...]] = ("km-button", "km-button--scheme-light")
NOTES: t.Final[str] = "km-release__notes"
VERSION: t.Final[re.Pattern[str]] = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9._+-]{0,63}"
)
WANTED: t.Final[str] = (
    "a version of up to 64 letters, numbers and ._+- that starts with a"
    " letter or a number"
)


def release_version(argument: str | None) -> str:
    """Check the version of a release.

    :param argument: The version as written.
    :return: The version, trimmed.
    :raises ValueError: When it is not up to 64 letters, numbers and
        `._+-` that start with a letter or a number.
    """
    found = (argument or "").strip()
    if not VERSION.fullmatch(found):
        raise ValueError(f"expected {WANTED}, got {argument!r}")
    return found


class Release(KaamikiDirective, motion=True):
    """The `release` directive.

    Options::

        - `version`: The version of the release, as `2026.11.8`
          or `v1.2.0`, with a maximum of 64 letters, numbers and
          `._+-`. It is necessary, and a site uses each version
          only one time.
        - `article`: A page with the story of the release, named
          as `:doc:` names it. Its link is below the notes.
        - `article-label`: The text of the link to the article,
          with a maximum of 60 characters. It needs `article`.
          The default is "Read release notes".
        - `date`: The day of the release, as `5 October 2026` or
          `2026-10-05`. It has priority over the version.
        - `target`: The release on a different site, as a GitHub
          release. Its link is next to the article.
        - `speed`: The speed of its motion, relative to the site,
          one of `0.25`, `0.5`, `0.75`, `1`, `1.5`, `2`, `3` or
          `4`. `2` is two times as fast.
        - `no-motion`: Do not move it.
        - `name`: One more name for links, next to the version.
        - `class`: More classes for the release.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    version = Option(release_version)
    article = Option(checks.text)
    article_label = Option(
        functools.partial(checks.text, maximum=60), needs="article"
    )
    date = Option(checks.text)
    target = Option(checks.link)

    class Node(nodes.Element):
        """The date and the version of the release."""

    @classmethod
    def made(cls, node: nodes.Node | None) -> bool:
        """Say whether a node is a release, which is a section.

        :param node: The node to look at.
        :return: `True` for a release, which holds the node of its
            version and date. A section from an author does not hold
            it.
        """
        return isinstance(node, nodes.section) and any(
            isinstance(each, cls.Node) for each in node.children
        )

    def check(self) -> None:
        """Make sure that the release has a version.

        :raises rst.DirectiveError: When it has no `version`.
        """
        if self.version is None:
            self.fail(f":version: expected {WANTED}, got none")

    def build(self) -> list[nodes.Node]:
        """Make the section of the release.

        :return: The section and what its title reported. The id of the
            section is the version, with a dash for each character that
            is not a letter, a number, `_` or `-`. The date gets its
            format when the page is written. The build refuses a
            directive in the content that takes a name of the release.
        """
        version = self.version
        docname = self.env.docname
        pages = ensure_versions(self.env).setdefault(version, {})
        if docname in pages:
            self.fail(
                ":version: expected a version not on this page yet, got"
                f" {version!r}"
            )
        section = self.locate(
            nodes.section("", classes=["km-release", *self.classes])
        )
        pages[docname] = location(section)
        target = re.sub(r"[^\w-]+", "-", version)
        same = t.cast(
            "dict[str, str]",
            self.env.temp_data.setdefault("km_release_ids", {}),
        )
        if same.setdefault(target, version) != version:
            self.fail(
                f":version: expected an id of its own, got {version!r}, which"
                f" makes {target!r} like {same[target]!r}"
            )
        released = self.released(version)
        title, messages = self.heading(version)
        section["ids"].append(target)
        section["names"].append(nodes.fully_normalize_name(version))
        named_too = "name" in self.options
        if named_too:
            alias = nodes.make_id(
                nodes.fully_normalize_name(self.options["name"])
            )
            if alias:
                section["ids"].insert(0, alias)
        attributes: dict[str, t.Any] = {
            "version": version,
            "datetime": released.date().isoformat() if released else "",
            "titled": bool(self.arguments),
        }
        body = nodes.container(classes=["km-release__body"])
        section.extend([title, self.Node("", **attributes), body])
        self.add_name(section)
        if not named_too:
            self.state.document.note_explicit_target(section, section)
        self.state.nested_parse(self.content, self.content_offset, body)
        if hollow(body.children):
            self.fail("expected some content, got none")
        more = self.more()
        if more is not None:
            body.insert(1, more)
        self.label(body)
        return [section, *messages]

    def released(self, version: str) -> dt | None:
        """Find the day of the release.

        :param version: The version, as written.
        :return: The day from `:date:`, else from the version when it
            follows `kaamiki.conf.release.version_fmt`, else `None`.
        :raises rst.DirectiveError: When `:date:` is not a date.
        """
        if "date" in self.options:
            iso = day(self.options["date"].strip())
            if not iso:
                self.fail(
                    ":date: expected a date like 5 October 2026 or"
                    f" 2026-10-05, got {self.options['date']!r}"
                )
            made = dt.fromisoformat(iso).astimezone()
            if not within(iso):
                self.fail(
                    ":date: expected a date from 2000 to a year ahead, got"
                    f" {self.options['date']!r}"
                )
            return made
        form = values(self.config).release.version_fmt
        if not form:
            return None
        try:
            return dt.strptime(version, form).astimezone()
        except ValueError:
            return None

    def heading(
        self, version: str
    ) -> tuple[nodes.title, list[nodes.system_message]]:
        """Make the title of the release, with its inline markup.

        :param version: The version, which is the title when the
            release has none. It is written as it is, because it is a
            name and not text with markup.
        :return: The title and what the parser reported.
        """
        text = " ".join(self.arguments).strip() or version
        words: list[nodes.Node] = [nodes.Text(text)]
        messages: list[nodes.system_message] = []
        if self.arguments:
            words, messages = self.state.inline_text(text, self.lineno)
            worded(self, words, "a title")
        title = self.locate(
            nodes.title(text, "", *words, classes=["km-release__title"])
        )
        return title, messages

    def label(self, body: nodes.container) -> None:
        """Mark the groups of the notes of a release.

        :param body: The parsed content of the release, changed in
            place. Each term in a definition list of the release gets
            `km-release__kind`, but not a list in a different list. A
            term in the language of the site is compared with the
            translation of each name. A group in
            `kaamiki.conf.release.kinds` is also correct. The names are
            translated here and not at import, because the words of
            Kaamiki join the catalogue of Sphinx only after setup.
        """
        own = {
            str(key).strip().lower()
            for key in values(self.config).release.kinds
        }
        kinds = {
            "added": str(_("Added")),
            "changed": str(_("Changed")),
            "deprecated": str(_("Deprecated")),
            "fixed": str(_("Fixed")),
            "removed": str(_("Removed")),
        }
        for changes in list(body.findall(nodes.definition_list)):
            host = changes.parent
            while host is not body and not isinstance(
                host, nodes.definition_list
            ):
                host = host.parent if host is not None else body
            if host is not body:
                continue
            changes["classes"].append("km-release__changes")
            for item in changes.children:
                term = item.next_node(nodes.term)
                if term is None:
                    continue
                said = term.astext().strip().lower()
                known = any(
                    said in {key, word.lower()} for key, word in kinds.items()
                )
                if not known and said not in own:
                    names = list(kinds.values())
                    self.fail(
                        f"expected a group of {', '.join(names[:-1])} or"
                        f" {names[-1]}, or one in kaamiki.conf.release.kinds,"
                        f" got {term.astext()!r}"
                    )
                term["classes"].append("km-release__kind")

    def more(self) -> nodes.paragraph | None:
        """Link the article and the release on a different site.

        :return: A paragraph with the links, or `None` without links.
        """
        urls: list[nodes.Node] = []
        if self.article:
            ensure_articles(self.env).setdefault(
                document(self, self.article, "article"), set()
            ).add(self.env.docname)
            text = self.article_label or str(_("Read release notes"))
            urls.append(
                addnodes.pending_xref(
                    "",
                    nodes.inline(text, text),
                    refdomain="std",
                    reftype="doc",
                    reftarget=self.article,
                    refdoc=self.env.docname,
                    refexplicit=True,
                    refwarn=True,
                    classes=[*BUTTON, NOTES],
                )
            )
        if self.target:
            text = str(_("View release"))
            urls.append(
                nodes.reference(
                    "",
                    text,
                    refuri=self.target,
                    classes=list(BUTTON),
                )
            )
        if not urls:
            return None
        spaced: list[nodes.Node] = []
        for url in urls:
            if spaced:
                spaced.append(nodes.Text(" "))
            spaced.append(url)
        return nodes.paragraph(
            "", "", *spaced, classes=["km-release__more", "km-button-row"]
        )


@html.opens(Release.Node)
def visit(self: HTMLTranslator, node: Release.Node) -> None:
    """Write the date and the version.

    :param self: The HTML translator, whose body this appends to.
    :param node: The `release` node and its attributes.
    """
    attributes = dict(node.attributes)
    iso = attributes.get("datetime")
    attributes["date"] = (
        dated(dt.fromisoformat(iso), self.builder.config) if iso else ""
    )
    self.body.append(render(template, optional=optional(node), **attributes))


def ensure_versions(env: BuildEnvironment) -> dict[str, dict[str, str]]:
    """Hold where each version of a release is written.

    :param env: The build environment.
    :return: Each version that a `release` names, with each page that
        has it and its `source:line` there. The store is made when it
        is first used.
    """
    return stored(env, "versions", {})


@on("env-before-read-docs")
def clear(app: Sphinx, env: BuildEnvironment, docnames: list[str]) -> None:
    """Forget each page that is read again, before the first is read.

    :param app: The Sphinx application instance (unused).
    :param env: The build environment.
    :param docnames: The pages that are read.
    """
    del app
    for docname in docnames:
        env.clear_doc(docname)


@on("env-purge-doc")
def purge(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    """Forget the articles and the versions of the releases of a page.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param docname: The page that is read again.
    """
    del app
    found = ensure_articles(env)
    for article in list(found):
        found[article].discard(docname)
        if not found[article]:
            del found[article]
    seen = ensure_versions(env)
    for version in list(seen):
        seen[version].pop(docname, None)
        if not seen[version]:
            del seen[version]


@on("env-merge-info")
def merge(
    app: Sphinx,
    env: BuildEnvironment,
    docnames: set[str],
    other: BuildEnvironment,
) -> None:
    """Take the articles and the versions that a parallel reader found.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param docnames: The pages that the reader read.
    :param other: The build environment of the reader.
    """
    del app
    for article, pages in ensure_articles(other).items():
        read = pages & docnames
        if read:
            ensure_articles(env).setdefault(article, set()).update(read)
    for version, places in ensure_versions(other).items():
        for page, where in places.items():
            if page in docnames:
                ensure_versions(env).setdefault(version, {})[page] = where


@on("env-updated")
def settle(app: Sphinx, env: BuildEnvironment) -> None:
    """Stop the build when two pages have the same version.

    :param app: The Sphinx application instance.
    :param env: The build environment, with each page read.
    :raises KaamikiError: For the first version on two pages, at the
        later page.
    """
    del app
    for version, pages in sorted(ensure_versions(env).items()):
        if len(pages) > 1:
            first, last = sorted(pages)[:2]
            fail(
                "release: :version: expected a version not on the page"
                f" {first!r} yet, got {version!r}, which is at {pages[first]}",
                pages[last],
            )


@on("doctree-resolved")
def tag(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Put the `release_notes` icon on the link to the article.

    :param app: The Sphinx application instance.
    :param doctree: The resolved doctree of the page. The icon goes in
        after the link is resolved. An empty icon leaves the link
        without an icon, and the class that marks the link goes.
    :param docname: The page that is resolved (unused).
    """
    del docname
    if not writes_pages(app):
        return
    classes = Kaamiki.of(app.builder).icons.roles["release_notes"]
    after = values(app.config).button.icon_position == "after"
    for link in findall(doctree, nodes.reference):
        if NOTES not in link["classes"]:
            continue
        link["classes"].remove(NOTES)
        if not classes:
            continue
        badge = glyph("", "", classes=[*classes.split(), "km-button__icon"])
        link.parent["classes"].append("km-button-row--align-left")
        if after:
            badge["classes"].append("km-button__icon--icon-position-after")
            link += badge
        else:
            link.insert(0, badge)
