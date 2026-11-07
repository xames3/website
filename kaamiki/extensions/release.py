"""\
Release Directive
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 30 September 2026
Last updated on: 07 November 2026

A `release` directive that writes one entry of a changelog::

    .. release:: Loads through Sphinx alone
       :version: 2026.10.5
       :article: changelogs/october-2026

       The first paragraph sums the release up.

       Added
           - What's new, a line each.
       Fixed
           - What works now.
"""

from __future__ import annotations

import re
import typing as t
from datetime import datetime as dt

import docutils.nodes as nodes
import docutils.parsers.rst as rst
from sphinx import addnodes
from sphinx.locale import _

from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import dated
from kaamiki.extensions.utils import day
from kaamiki.extensions.utils import document
from kaamiki.extensions.utils import ensure_articles
from kaamiki.extensions.utils import findall
from kaamiki.extensions.utils import glyph
from kaamiki.extensions.utils import hollow
from kaamiki.extensions.utils import located
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import render
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils import stored
from kaamiki.extensions.utils import worded
from kaamiki.extensions.utils.checks import fail
from kaamiki.extensions.utils.checks import location
from kaamiki.extensions.utils.dates import within

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "release"
template: t.Final[str] = "directives/release.html.jinja"
BUTTON: t.Final[tuple[str, ...]] = ("km-button", "km-button--scheme-light")
NOTES: t.Final[str] = "km-release__notes"
VERSION: t.Final[re.Pattern[str]] = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9._+-]{0,63}"
)


class Release(nodes.Element):
    """The release's date and version, waiting for `visit`."""


def release_version(argument: str | None) -> str:
    """Check the version of a release.

    :param argument: The version as written.
    :return: The version, trimmed.
    :raises ValueError: When it isn't written like 2026.10.5.
    """
    found = (argument or "").strip()
    if not VERSION.fullmatch(found):
        raise ValueError(f"expected a version like 2026.10.5, got {argument!r}")
    return found


class directive(rst.Directive):
    """The `release` directive.

    Options::

        - `version`: The release's version, like `2026.10.5`. It is
          needed and a site uses each once.
        - `article`: A page telling the story behind the release, as
          `:doc:` would name it. It's linked under the notes.
        - `article-label`: What the article's link says, up to 60
          characters. It needs `article`. Defaults to "Read release
          notes".
        - `date`: The day it went out, as `5 October 2026` or
          `2026-10-05`. It wins over the version.
        - `target`: The release elsewhere, a GitHub release say. It's
          linked next to the article.
        - `name`: Another name to link to, beside the version.
        - `class`: More classes for the release.

    The argument is the title, what the release is about, and is
    optional. Without one the version is the title. A release is a
    section, so it goes directly in one: on the page or under a
    heading, an `only` aside. It never goes in an accordion, a tab, a
    block, a column, a list or a note.

    The definition lists in the content are the change groups. Each
    term is one of `Added`, `Changed`, `Deprecated`, `Fixed` and
    `Removed`, or a group in the site's `kaamiki.conf.release.kinds`,
    wherever the list sits in the content, and a list inside a group is
    left alone.

    The site's `kaamiki.conf.release.version_fmt` says how a version
    spells its date, `%Y.%m.%d` by default. A version that doesn't and
    has no `:date:` is shown without one.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "version": release_version,
        "article": checks.text,
        "article-label": lambda _: checks.text(_, 60),
        "date": checks.text,
        "target": checks.link,
    }

    def run(self) -> list[nodes.Node]:
        """Build the release's section and return it.

        The section's id is the version with dashes for dots. Its date
        is written when the page is, so it reads like the
        "Last updated" line. The section and its names are in the page
        before the content is read, so a directive in the content that
        takes a name the release has is the one refused.

        :return: The section, followed by anything its title reported.
        """
        if "version" not in self.options:
            raise self.error(
                "release: :version: expected a version like 2026.10.5, got none"
            )
        version = self.options["version"]
        env = self.state.document.settings.env
        pages = ensure_versions(env).setdefault(version, {})
        if env.docname in pages:
            raise self.error(
                f"release: :version: expected a version not on this page"
                f" yet, got {version!r}"
            )
        section = located(
            self,
            nodes.section(
                "", classes=["km-release", *self.options.get("class", [])]
            ),
        )
        pages[env.docname] = location(section)
        target = re.sub(r"[^\w-]+", "-", version)
        same = env.temp_data.setdefault("km_release_ids", {})
        if same.setdefault(target, version) != version:
            raise self.error(
                f"release: :version: expected an id of its own, got"
                f" {version!r}, which makes {target!r} like {same[target]!r}"
            )
        if "article-label" in self.options and "article" not in self.options:
            raise self.error("release: :article-label: needs :article:")
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
        attributes: dict[str, t.Any] = {}
        attributes["version"] = version
        attributes["datetime"] = released.date().isoformat() if released else ""
        attributes["titled"] = bool(self.arguments)
        body = nodes.container(classes=["km-release__body"])
        section.extend([title, Release("", **attributes), body])
        named(self, section)
        if not named_too:
            self.state.document.note_explicit_target(section, section)
        self.state.nested_parse(self.content, self.content_offset, body)
        if hollow(body.children):
            raise self.error("release: expected some content, got none")
        more = self.more()
        if more is not None:
            body.insert(1, more)
        self.label(body)
        return [section, *messages]

    def released(self, version: str) -> dt | None:
        """Work out the day a release went out.

        The `:date:` option says it, failing that the version does when
        it's spelt like `kaamiki.conf.release.version_fmt`.

        :param version: The version, as written.
        :return: The day or `None` when nothing says.
        :raises rst.DirectiveError: When `:date:` isn't a date.
        """
        if "date" in self.options:
            iso = day(self.options["date"].strip())
            if not iso:
                raise self.error(
                    f"release: :date: expected a date like 5 October 2026 or"
                    f" 2026-10-05, got {self.options['date']!r}"
                )
            made = dt.fromisoformat(iso).astimezone()
            if not within(iso):
                raise self.error(
                    "release: :date: expected a date from 2000 to a year"
                    f" ahead, got {self.options['date']!r}"
                )
            return made
        env = self.state.document.settings.env
        form = setting(env.config, "release_version_fmt")
        if not form:
            return None
        try:
            return dt.strptime(version, form).astimezone()
        except ValueError:
            return None

    def heading(
        self, version: str
    ) -> tuple[nodes.title, list[nodes.system_message]]:
        """Make the release's title, inline markup and all.

        :param version: The version, which stands in for a title the
            release hasn't got and is written as it is, since it's a
            name and not text with markup.
        :return: The title and whatever parsing it reported.
        """
        text = " ".join(self.arguments).strip() or version
        words: list[nodes.Node] = [nodes.Text(text)]
        messages: list[nodes.system_message] = []
        if self.arguments:
            words, messages = self.state.inline_text(text, self.lineno)
            worded(self, words, "a title")
        title = located(
            self,
            nodes.title(text, "", *words, classes=["km-release__title"]),
        )
        return title, messages

    def label(self, body: nodes.container) -> None:
        """Mark the groups a release sorts its notes into.

        Each term in a definition list of the release, wherever it sits
        in the content, gets a class named after it, `Added` becoming
        `km-release__kind--added`, for the stylesheet to colour. A
        definition list inside another is left alone.

        A term in the site's own language is matched against Kaamiki's
        translation of each name. A group the site named in
        `kaamiki.conf.release.kinds` also gets the colour it was given.

        :param body: The release's parsed content, changed in place.
        """
        env = self.state.document.settings.env
        tones = {
            str(key).strip().lower(): str(value).strip().lower()
            for key, value in setting(env.config, "release_kinds").items()
        }
        # NOTE(xames3): Translated here and not at import, as Kaamiki's
        # words only join Sphinx's catalogue once it has set up.
        # https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx.application.Sphinx.add_message_catalog
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
                kind = next(
                    (
                        key
                        for key, word in kinds.items()
                        if said in {key, word.lower()}
                    ),
                    None,
                )
                if kind is None and said not in tones:
                    raise self.error(
                        f"release: expected a group of"
                        f" {', '.join(kinds.values())}, or one in"
                        f" kaamiki.conf.release.kinds, got {term.astext()!r}"
                    )
                term["classes"].extend(
                    [
                        "km-release__kind",
                        f"km-release__kind--{kind or nodes.make_id(said)}",
                    ]
                )
                if kind is None:
                    term["classes"].append(f"km-release__tone--{tones[said]}")

    def more(self) -> nodes.paragraph | None:
        """Link the article and the release elsewhere, if there are
        any.

        :return: A paragraph holding the links or `None` without any.
        """
        env = self.state.document.settings.env
        urls: list[nodes.Node] = []
        if "article" in self.options:
            ensure_articles(env).setdefault(
                document(self, self.options["article"], "article"), set()
            ).add(env.docname)
            text = self.options.get("article-label") or str(
                _("Read release notes")
            )
            urls.append(
                addnodes.pending_xref(
                    "",
                    nodes.inline(text, text),
                    refdomain="std",
                    reftype="doc",
                    reftarget=self.options["article"],
                    refdoc=env.docname,
                    refexplicit=True,
                    refwarn=True,
                    classes=[*BUTTON, NOTES],
                )
            )
        if "target" in self.options:
            text = str(_("View release"))
            urls.append(
                nodes.reference(
                    "",
                    text,
                    refuri=self.options["target"],
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


def plain(node: Release) -> list[nodes.Node]:
    """Write a release's date and version as words, for a builder that
    draws no HTML.

    :param node: The `release` node and its attributes.
    :return: A paragraph with the version, when a title has taken
        its place as the heading, and the date. A release with neither
        has a comment, which writes nothing.
    """
    iso = node["datetime"]
    config = node.document.settings.env.config if node.document else None
    date = dated(dt.fromisoformat(iso), config) if iso and config else ""
    line = ", ".join(
        _ for _ in (node["version"] if node["titled"] else "", date) if _
    )
    return [nodes.paragraph("", line)] if line else [nodes.comment()]


def visit(self: HTMLTranslator, node: Release) -> None:
    """Write the date and version out when the HTML writer reaches
    them.

    :param self: The HTML translator, whose body this appends to.
    :param node: The `release` node and its attributes.
    """
    attributes = dict(node.attributes)
    attributes["fa_icons"] = self.builder.config.html_context["km_fa_icons"]
    iso = attributes.get("datetime")
    attributes["date"] = (
        dated(dt.fromisoformat(iso), self.builder.config) if iso else ""
    )
    self.body.append(render(template, **attributes))


def ensure_versions(env: BuildEnvironment) -> dict[str, dict[str, str]]:
    """Hold the places each release version is written, making the
    store the first time it's asked for.

    :param env: The build environment.
    :return: Every version a `release` names, with each page it is on
        and the `source:line` it is written at there.
    """
    return stored(env, "versions", {})


def clear(app: Sphinx, env: BuildEnvironment, docnames: list[str]) -> None:
    """Forget every page that's about to be read before the first is.

    Sphinx's serial reader forgets a page just before it reads it, in
    name order, so a release moved to a page that sorts earlier is
    still held by the page it came from and its version is reported as
    a duplicate label. The parallel reader forgets all of them first,
    which is what this does for the serial one, so both agree.

    :param app: The Sphinx application instance (unused).
    :param env: The build environment.
    :param docnames: The pages to be read.
    """
    del app
    for docname in docnames:
        env.clear_doc(docname)


def purge(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    """Forget the articles and versions a page's releases had, as it's
    re-read.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param docname: The page about to be read again.
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


def merge(
    app: Sphinx,
    env: BuildEnvironment,
    docnames: set[str],
    other: BuildEnvironment,
) -> None:
    """Take in the articles and versions a parallel reader found.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param docnames: The pages the reader read.
    :param other: The reader's build environment.
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


def settle(app: Sphinx, env: BuildEnvironment) -> None:
    """Stop the build when two pages wrote the same version.

    It waits until every page is read, since a page that is read again
    may be the one that gave a version up. A serial reader purges a
    page just before it reads it, in name order, so the page a release
    was moved from still has it when the page it moved to is read.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :raises KaamikiError: For the first version on two pages, named at
        the later page.
    """
    del app
    for version, pages in sorted(ensure_versions(env).items()):
        if len(pages) > 1:
            first, last = sorted(pages)[:2]
            fail(
                f"release: version {version!r} is on the page {first!r}"
                f" already, at {pages[first]}",
                pages[last],
            )


def tag(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Put the site's `release_notes` icon on the link to a release's
    article.

    Sphinx writes a link to a page out of its text alone, so the icon
    goes in once the link has been resolved. An empty icon leaves the
    link bare. The class that marks the link goes once it's been used,
    as no style asks for it.

    :param app: The Sphinx application instance.
    :param doctree: The page's resolved doctree.
    :param docname: The page being resolved (unused).
    """
    del docname
    if app.builder.format != "html":
        return
    classes = app.config.html_context["km_fa_icons"]["release_notes"]
    after = setting(app.config, "button_icon_position") == "after"
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


def register(app: Sphinx) -> None:
    """Keep track of the articles releases link to and tag them.

    :param app: The Sphinx application instance.
    """
    app.connect("env-before-read-docs", clear)
    app.connect("env-purge-doc", purge)
    app.connect("env-merge-info", merge)
    app.connect("env-updated", settle)
    app.connect("doctree-resolved", tag)


node = Release
