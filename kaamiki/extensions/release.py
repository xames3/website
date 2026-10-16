"""\
Release Directive
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 30 September 2026
Last updated on: 16 October 2026

A `release` directive that writes one entry of a changelog::

    .. release:: 2026.10.5
       :title: Loads through Sphinx alone
       :article: changelogs/october-2026

       The first paragraph sums the release up.

       Added
           - What's new, a line each.
       Fixed
           - What works now.
"""

import re
import typing as t
from datetime import datetime as dt

import docutils.nodes as nodes
import docutils.parsers.rst as rst
from sphinx import addnodes
from sphinx.locale import _
from sphinx.util import docname_join

from kaamiki.extensions.roles import glyph
from kaamiki.extensions.utils import articles
from kaamiki.extensions.utils import dated
from kaamiki.extensions.utils import day
from kaamiki.extensions.utils import findall
from kaamiki.extensions.utils import icon
from kaamiki.extensions.utils import render
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils.settings import TONES

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "release"
template: t.Final[str] = "directives/release.html.jinja"
BUTTON: t.Final[tuple[str, ...]] = (
    "sd-sphinx-override",
    "sd-btn",
    "sd-text-wrap",
    "sd-btn-light",
)
NOTES: t.Final[str] = "km-release__notes"


class node(nodes.Element):
    """The release's date and version, waiting for `visit`."""


class directive(rst.Directive):
    """The `release` directive.

    Options::

        - `title`: What the release is about. Without one, the version
          is the title.
        - `article`: A page telling the story behind the release, as
          `:doc:` would name it. It's linked under the notes.
        - `article-label`: What the article's link says. Defaults to
          "Read release notes".
        - `date`: The day it went out, as `5 October 2026` or
          `2026-10-05`. It wins over the version.
        - `url`: The release elsewhere, a GitHub release say. It's
          linked next to the article.

    The site's `release_version_fmt` says how a version spells its
    date, `%Y.%m.%d` by default. A version that doesn't and has
    no `:date:` is shown without one.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        "title": rst.directives.unchanged_required,
        "article": rst.directives.unchanged_required,
        "article-label": rst.directives.unchanged_required,
        "date": rst.directives.unchanged_required,
        "url": rst.directives.uri,
    }

    def run(self) -> list[nodes.Node]:
        """Build the release's section and return it.

        The section's id is the version with dashes for dots. Its date
        is written when the page is, so it reads like the
        "Last updated" line.

        :return: The section, followed by anything its title reported.
        """
        version = self.arguments.pop().strip()
        released = self.released(version)
        title, messages = self.heading(version)
        section = nodes.section("", classes=["km-release"])
        section.source, section.line = self.state_machine.get_source_and_line(
            self.lineno
        )
        section["ids"].append(re.sub(r"[^\w-]+", "-", version))
        section["names"].append(nodes.fully_normalize_name(version))
        self.state.document.note_explicit_target(section, section)
        attributes: dict[str, t.Any] = {}
        attributes["version"] = version
        attributes["datetime"] = released.date().isoformat() if released else ""
        attributes["titled"] = "title" in self.options
        body = nodes.container(classes=["km-release__body"])
        self.state.nested_parse(self.content, self.content_offset, body)
        more = self.more()
        if more is not None:
            body.insert(1, more)
        self.label(body)
        section.extend([title, node("", **attributes), body])
        return [section, *messages]

    def released(self, version: str) -> dt | None:
        """Work out the day a release went out.

        The `:date:` option says it, failing that the version does when
        it's spelt like `release_version_fmt`.

        :param version: The version, as written.
        :return: The day or `None` when nothing says.
        :raises rst.DirectiveError: When `:date:` isn't a date.
        """
        if "date" in self.options:
            iso = day(self.options["date"].strip())
            if not iso:
                raise self.error(
                    f"release needs a date like 5 October 2026 or"
                    f" 2026-10-05 in :date:; got {self.options['date']!r}"
                )
            return dt.fromisoformat(iso).astimezone()
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
            release hasn't got.
        :return: The title and whatever parsing it reported.
        """
        text = self.options.get("title", version)
        words, messages = self.state.inline_text(text, self.lineno)
        title = nodes.title(text, "", *words, classes=["km-release__title"])
        title.source, title.line = self.state_machine.get_source_and_line(
            self.lineno
        )
        return title, messages

    def label(self, body: nodes.container) -> None:
        """Mark the groups a release sorts its notes into.

        Each term in the definition list under the release gets a class
        named after it, `Added` becoming `km-release__kind--added`, for
        the stylesheet to colour.

        A term in the site's own language is matched against Kaamiki's
        translation of each name. A group the site named in
        `release_kinds` also gets the colour it was given.

        :param body: The release's parsed content, changed in place.
        """
        env = self.state.document.settings.env
        tones = {
            str(key).strip().lower(): str(value).strip().lower()
            for key, value in setting(env.config, "release_kinds").items()
        }
        # NOTE(xames3): Translated here and not at import, as Kaamiki's
        # words only join Sphinx's catalogue once it has set up.
        kinds = {
            "added": str(_("Added")),
            "changed": str(_("Changed")),
            "deprecated": str(_("Deprecated")),
            "fixed": str(_("Fixed")),
            "removed": str(_("Removed")),
        }
        for changes in body.children:
            if not isinstance(changes, nodes.definition_list):
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
                    nodes.make_id(said),
                )
                term["classes"].extend(
                    ["km-release__kind", f"km-release__kind--{kind}"]
                )
                tone = tones.get(said)
                if tone is not None and kind not in kinds:
                    if tone not in TONES:
                        raise self.error(
                            f"release_kinds has {tone!r} for {said}; a colour"
                            f" is one of {', '.join(TONES)}"
                        )
                    term["classes"].append(f"km-release__tone--{tone}")

    def more(self) -> nodes.paragraph | None:
        """Link the article and the release elsewhere, if there are
        any.

        :return: A paragraph holding the links or `None` without any.
        """
        env = self.state.document.settings.env
        urls: list[nodes.Node] = []
        if "article" in self.options:
            articles(env)[
                docname_join(env.docname, self.options["article"])
            ] = env.docname
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
        if "url" in self.options:
            text = str(_("View release"))
            urls.append(
                nodes.reference(
                    "",
                    text,
                    refuri=self.options["url"],
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
        return nodes.paragraph("", "", *spaced, classes=["km-release__more"])


def visit(self: HTMLTranslator, node: node) -> None:
    """Write the date and version out when the HTML writer reaches them.

    :param self: The HTML translator, whose body this appends to.
    :param node: The `release` node and its attributes.
    """
    attributes = dict(node.attributes)
    iso = attributes.get("datetime")
    attributes["date"] = (
        dated(dt.fromisoformat(iso), self.builder.config) if iso else ""
    )
    self.body.append(render(template, **attributes))


def purge(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    """Forget the articles a page's releases linked, as it's re-read.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param docname: The page about to be read again.
    """
    del app
    found = articles(env)
    for article in [key for key, page in found.items() if page == docname]:
        del found[article]


def merge(
    app: Sphinx,
    env: BuildEnvironment,
    docnames: set[str],
    other: BuildEnvironment,
) -> None:
    """Take in the articles a parallel reader found.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param docnames: The pages the reader read.
    :param other: The reader's build environment.
    """
    del app
    articles(env).update(
        {key: page for key, page in articles(other).items() if page in docnames}
    )


def tag(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Put the site's `release_notes` icon on the link to a release's
    article.

    Sphinx writes a link to a page out of its text alone, so the icon
    goes in once the link has been resolved. An empty icon leaves the
    link bare.

    :param app: The Sphinx application instance.
    :param doctree: The page's resolved doctree.
    :param docname: The page being resolved (unused).
    """
    del docname
    if app.builder.format != "html":
        return
    classes = icon(app.config.html_context["km_fa_icons"]["release_notes"])
    if not classes:
        return
    after = setting(app.config, "button_icon_position") == "after"
    for link in findall(doctree, nodes.reference):
        if NOTES not in link["classes"]:
            continue
        badge = glyph("", "", classes=classes.split())
        if after:
            badge["classes"].append("km-icon-after")
            link += badge
        else:
            link.insert(0, badge)


def register(app: Sphinx) -> None:
    """Keep track of the articles releases link to and tag them.

    :param app: The Sphinx application instance.
    """
    app.connect("env-purge-doc", purge)
    app.connect("env-merge-info", merge)
    app.connect("doctree-resolved", tag)
