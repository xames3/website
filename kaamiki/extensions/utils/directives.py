"""\
Directive Utilities
===================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 15 November 2026

The helpers that the directives of Kaamiki are built from. `NATIVE`
holds the two options of the directives of docutils, `class` and
`name`, so that a Kaamiki directive reads them in the same way.

https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options
"""

from __future__ import annotations

import os.path as p
import re
import typing as t
from urllib.parse import urlsplit

from docutils import nodes
from docutils.parsers import rst
from markupsafe import Markup
from sphinx import addnodes
from sphinx.util import docname_join
from sphinx.util.docutils import SphinxDirective

from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils.settings import values
from kaamiki.extensions.utils.templates import render

if t.TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Iterable
    from collections.abc import Iterator
    from collections.abc import Mapping
    from collections.abc import Sequence

    from docutils.parsers.rst import Directive
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

    from kaamiki.extensions.roles import KaamikiRole

    Visitor = Callable[[HTMLTranslator, nodes.Element], None]

OPTION: t.Final[re.Pattern[str]] = re.compile(
    r"^\s*- `([\w-]+)`:", re.MULTILINE
)
LINKCHECK_OPTIONS: t.Final[tuple[str, ...]] = ("avatar", "backdrop", "target")
LINKS: t.Final[tuple[type[nodes.Node], ...]] = (
    nodes.reference,
    nodes.footnote_reference,
    nodes.citation_reference,
    addnodes.pending_xref,
)
NATIVE: t.Final[dict[str, Callable[[str | None], t.Any]]] = {
    "class": checks.classes,
    "name": checks.reference_name,
}
SPEEDS: t.Final[tuple[str, ...]] = (
    "0.25",
    "0.5",
    "0.75",
    "1",
    "1.5",
    "2",
    "3",
    "4",
)
NO_MOTION: t.Final[dict[str, Callable[[str | None], t.Any]]] = {
    "no-motion": rst.directives.flag,
}
MOTION: t.Final[dict[str, Callable[[str | None], t.Any]]] = {
    "speed": checks.word(*SPEEDS),
    **NO_MOTION,
}


def moving(options: Mapping[str, t.Any], *, timed: bool = True) -> list[str]:
    """Name the classes of the speed and the stillness of a directive.

    :param options: The options of the directive.
    :param timed: Whether `:speed:` is the speed of the motion. It is
        not an option of `code-explain` and `code-version`, which
        scroll by `:pace:`.
    :return: `km-speed--2` for a `:speed:` of 2 (a point is a dash, as
        in `km-speed--0-5`), and `km-motion--off` for `:no-motion:`.
    """
    found: list[str] = []
    if timed and "speed" in options:
        found.append(f"km-speed--{options['speed'].replace('.', '-')}")
    if "no-motion" in options:
        found.append("km-motion--off")
    return found


def toggle(argument: str | None) -> bool:
    """Read a directive option or a page field as a switch.

    :param argument: The value in the rST, or `None` when it is bare. A
        bare switch is on, and `false` sets it off.
    :return: `True` when it is on.
    :raises ValueError: For a value that is not none, `true` or
        `false`.
    """
    if argument in (None, "", "true"):
        return True
    if argument == "false":
        return False
    raise ValueError(f"expected true or false, got {argument!r}")


def hollow(found: Iterable[nodes.Node]) -> bool:
    """Say whether some parsed nodes hold nothing a reader would see.

    :param found: The nodes.
    :return: `True` when all there is are comments and link targets.
    """
    skipped = (nodes.comment, nodes.target)
    return all(isinstance(_, skipped) for _ in found)


def through(found: Iterable[nodes.Node]) -> Iterator[nodes.Node]:
    """Walk some nodes, and look into each `only`.

    :param found: The nodes.
    :return: Each node that is not an `only`, in the sequence written.
    """
    for each in found:
        if isinstance(each, addnodes.only):
            yield from through(each.children)
        else:
            yield each


def unlinked(
    directive: Directive,
    found: Iterable[nodes.Node] | nodes.Node,
    part: str,
) -> None:
    """Refuse a link in a text that is a link or a control already.

    :param directive: The directive that has the text.
    :param found: The parsed text or its nodes.
    :param part: What the text is, as `a label`.
    :raises rst.DirectiveError: When the text has a link.
    """
    for each in [found] if isinstance(found, nodes.Node) else found:
        if any(isinstance(_, LINKS) for _ in each.findall()):
            raise directive.error(
                f"{directive.name}: expected {part} without a link, got one"
            )


def worded(
    directive: Directive,
    found: Iterable[nodes.Node] | nodes.Node,
    part: str,
) -> None:
    """Refuse a text without words, with only an icon or nothing.

    :param directive: The directive that has the text.
    :param found: The parsed text or its nodes.
    :param part: What the text is, as `a title`.
    :raises rst.DirectiveError: When the text has no words. An icon
        adds to a text and does not replace it, so that a screen reader
        and a reader without icons get the meaning.
    """
    each = [found] if isinstance(found, nodes.Node) else found
    if not "".join(_.astext() for _ in each).strip():
        raise directive.error(
            f"{directive.name}: expected {part} with words, got only an"
            " icon or nothing"
        )


def titled(directive: Directive, argument: str) -> str:
    """Read the title that a directive gets as its argument.

    :param directive: The directive that has the title.
    :param argument: The title as written.
    :return: The title, trimmed.
    :raises rst.DirectiveError: When it is blank or too long.
    """
    try:
        return checks.text(argument)
    except ValueError as error:
        raise directive.error(f"{directive.name}: title {error}") from error


def document(directive: Directive, name: str, option: str) -> str:
    """Find the document that an option names, as `:doc:` writes it.

    :param directive: The directive that has the option.
    :param name: The document, relative to the page, or from the top
        with a `/` at the start.
    :param option: The option where it is written.
    :return: The name of the document.
    :raises rst.DirectiveError: When the site has no such document.
    """
    env = directive.state.document.settings.env
    found = docname_join(env.docname, name.strip())
    if found not in env.found_docs:
        raise directive.error(
            f"{directive.name}: :{option}: expected a document of this site,"
            f" got {name!r}"
        )
    return found


def shipped(directive: Directive, value: str, where: str) -> str:
    """Check that a path is a file of the site.

    :param directive: The directive that has the option.
    :param value: The path or the address, as written. A full address
        or a `#` fragment does not change. A path below `_static` must
        be in `html_static_path`, and another path in
        `html_extra_path`, and it cannot go out of that folder. The
        file is recorded as a dependency of the page, so the page is
        read again when the file changes or goes.
    :param where: How it was written, as `:poster:` or `the address`.
    :return: The value, as written.
    :raises rst.DirectiveError: When the site has no such file or
        when the value has a host but no scheme.
    """
    from kaamiki.extensions.utils.context import confdir

    parts = urlsplit(value)
    if parts.netloc and not parts.scheme:
        raise directive.error(
            f"{directive.name}: {where} expected an address with its"
            f" scheme, https://, got {value!r}"
        )
    if parts.scheme or value.startswith("#"):
        return value
    env = directive.state.document.settings.env
    name = parts.path.lstrip("/")
    config = env.config
    if name.startswith("_static/"):
        name = name.removeprefix("_static/")
        roots = config.html_static_path
    else:
        roots = config.html_extra_path
    for root in (p.normpath(p.join(confdir(env), _)) for _ in roots):
        if p.isfile(root) and p.basename(root) == name:
            found = root
        else:
            found = p.normpath(p.join(root, name))
            if p.commonpath([root, found]) != root:
                continue
        if p.isfile(found):
            env.note_dependency(found)
            return value
    raise directive.error(
        f"{directive.name}: {where} expected a file in html_static_path or"
        f" html_extra_path, got {value!r}"
    )


def named(directive: Directive, node: nodes.Node) -> None:
    """Give a node the name its `:name:` option asks for, once.

    :param directive: The directive that has the option.
    :param node: The node to name.
    :raises rst.DirectiveError: When the page already has the name.
    """
    if "name" not in directive.options:
        return
    page = directive.state.document
    name = nodes.fully_normalize_name(directive.options["name"])
    if name in page.nameids:
        raise directive.error(
            f"{directive.name}: :name: {name!r} is on the page already"
        )
    rst.Directive.add_name(directive, node)


def depart(self: HTMLTranslator, node: nodes.Element) -> None:
    """Close a node that has nothing to close.

    :param self: The HTML translator instance.
    :param node: The node being departed.
    """


def skip(self: nodes.NodeVisitor, node: nodes.Element) -> None:
    """Leave a node out of a builder that has no use for it.

    :param self: The translator.
    :param node: The node being skipped.
    :raises nodes.SkipNode: Always.
    """
    del self, node
    raise nodes.SkipNode


def closer(tag: str) -> Visitor:
    """Make a depart that writes only one closing tag.

    :param tag: The HTML that closes the node, as `</span>`.
    :return: The depart.
    """

    def close_tag(self: HTMLTranslator, node: nodes.Element) -> None:
        del node
        self.body.append(tag)

    return close_tag


class Renderer:
    """The record of how each Kaamiki node is written as HTML."""

    def __init__(self) -> None:
        """Make an empty record."""
        self.visitors: dict[type[nodes.Element], list[t.Any]] = {}

    def opens[V: Callable[..., None]](
        self, node: type[nodes.Element]
    ) -> Callable[[V], V]:
        """Record the function below as the visitor.

        :param node: The node that the function writes.
        :return: The decorator, which gives back the same function.
        """
        return self._recorder(node, 0)

    @t.overload
    def closes(self, node: type[nodes.Element], tag: str) -> None: ...

    @t.overload
    def closes[V: Callable[..., None]](
        self, node: type[nodes.Element]
    ) -> Callable[[V], V]: ...

    def closes(
        self, node: type[nodes.Element], tag: str = ""
    ) -> Callable[[t.Any], t.Any] | None:
        """Record the function below as the depart.

        :param node: The node that the function closes.
        :param tag: The HTML that closes the node. With it, you do not
            write a function.
        :return: The decorator, or `None` when `tag` is given.
        """
        if tag:
            self._recorder(node, 1)(closer(tag))
            return None
        return self._recorder(node, 1)

    def draws(
        self,
        node: type[nodes.Element],
        template: str,
        prepare: Callable[[HTMLTranslator, dict[str, t.Any]], dict[str, t.Any]]
        | None = None,
    ) -> None:
        """Record a template that writes all of a node.

        :param node: The node that the template writes.
        :param template: The template, relative to `theme/templates`.
        :param prepare: The function that changes the attributes of the
            node before the template gets them, as for `visitor`.
        """
        self._recorder(node, 0)(visitor(template, prepare))

    def skips(self, node: type[nodes.Element]) -> None:
        """Record that the HTML builder does not write a node.

        :param node: The node that the HTML builder leaves out.
        """
        self._recorder(node, 0)(skip)

    def register(self, app: Sphinx) -> None:
        """Give Sphinx each recorded node.

        :param app: The Sphinx application instance.
        """
        for node, (visit, leave) in self.visitors.items():
            app.add_node(node, html=(visit, leave))

    def _recorder[V: Callable[..., None]](
        self, node: type[nodes.Element], index: int
    ) -> Callable[[V], V]:
        """Make the decorator that keeps a function.

        :param node: The node.
        :param index: `0` for the visitor and `1` for the depart.
        :return: The decorator, which gives back the same function.
        """

        def record(function: V) -> V:
            self.visitors.setdefault(node, [depart, depart])[index] = function
            return function

        return record


html: t.Final[Renderer] = Renderer()


class BEM:
    """A BEM class name of Kaamiki, as `km-accordion__title`."""

    __slots__ = ("block", "element")

    def __init__(self, block: str, element: str = "") -> None:
        """Name a block or an element of a block.

        :param block: The block, without `km-`, as `accordion`.
        :param element: The element, as `title`.
        """
        self.block = block
        self.element = element

    def __getattr__(self, element: str) -> BEM:
        """Name an element of the block, as `accordion.title`.

        :param element: The element. An underscore becomes a dash.
        :return: The name of the element.
        :raises AttributeError: For a private name, or an element of an
            element, which BEM does not permit.
        """
        if element.startswith("_") or self.element:
            raise AttributeError(element)
        return BEM(self.block, element.replace("_", "-"))

    def __getitem__(self, modifier: str) -> str:
        """Name only a modifier, `text["preheader"]` for one.

        :param modifier: The modifier.
        :return: The modified name, as `km-text--preheader`.
        """
        return f"{self}--{modifier}"

    def __call__(self, *modifiers: str, more: Iterable[str] = ()) -> str:
        """Write the classes of the block or element.

        :param modifiers: The modifiers, as `marker-plus`.
        :param more: Other classes that come after them.
        :return: The name, each modified name and the other classes.
        """
        return " ".join([str(self), *map(self.__getitem__, modifiers), *more])

    def __str__(self) -> str:
        """Write the name.

        :return: `km-accordion` or `km-accordion__title`.
        """
        element = f"__{self.element}" if self.element else ""
        return f"km-{self.block}{element}"


def trail(
    directive: Directive,
    options: dict[str, t.Any],
    keys: Sequence[str] = LINKCHECK_OPTIONS,
) -> list[nodes.Node]:
    """Give `linkcheck` the URLs in the options of a directive.

    :param directive: The directive with the URLs.
    :param options: The options of the directive, as written in the
        rST.
    :param keys: The options with URLs. The default is those of the
        byline.
    :return: One empty `raw` node for each URL, to go next to the node
        of the directive, on its line. Sphinx reads URLs only from
        `reference`, `image` and `raw` nodes.
    """
    found: list[nodes.Node] = []
    for option in keys:
        found += [
            located(directive, nodes.raw("", "", format="html", source=uri))
            for uri in options.get(option, "").split()
            if "://" in uri
        ]
    return found


class phrase(nodes.TextElement):
    """The parsed text of a directive, for its template."""


def located[N: nodes.Node](directive: Directive, node: N) -> N:
    """Give a node its place in the source.

    :param directive: The directive of the text of the node.
    :param node: The node.
    :return: The same node, with the place that `gettext` needs to
        collect the text.
    """
    node.source, node.line = directive.state_machine.get_source_and_line(
        directive.lineno
    )
    return node


def parse(
    directive: Directive, text: str, field: str
) -> tuple[phrase, list[nodes.system_message]]:
    """Parse the text of a directive as a paragraph.

    :param directive: The directive of the text.
    :param text: The text, as written in the rST.
    :param field: The name of the text in the template of the
        directive.
    :return: The parsed text with its name, and what the parser
        reported. The text keeps its place in the source, so that
        `gettext` can collect it.
    """
    words, messages = directive.state.inline_text(text, directive.lineno)
    return located(directive, phrase(text, "", *words, field=field)), messages


BLOCKS: t.Final[tuple[tuple[type[nodes.Node], str], ...]] = (
    (nodes.bullet_list, "a list"),
    (nodes.enumerated_list, "a list"),
    (nodes.definition_list, "a definition list"),
    (nodes.block_quote, "a block quote"),
    (nodes.literal_block, "a code block"),
    (nodes.table, "a table"),
    (nodes.comment, "a comment"),
)


def paragraph(
    directive: Directive, text: str, field: str
) -> tuple[phrase, list[nodes.system_message]]:
    """Parse the content of a directive, which is one paragraph.

    :param directive: The directive of the content.
    :param text: The content, as written in the rST. It is read as a
        page reads it, so a list, a second paragraph or a directive is
        found, not written as text.
    :param field: The name of the text in the template of the
        directive.
    :return: The parsed text with its name, and what the parser
        reported.
    :raises rst.DirectiveError: When the content is not one paragraph.
    """
    if not text.strip():
        return parse(directive, text, field)
    holder = nodes.Element()
    directive.state.nested_parse(
        directive.content, directive.content_offset, holder
    )
    found = [
        _ for _ in holder.children if not isinstance(_, nodes.system_message)
    ]
    messages = [
        _ for _ in holder.children if isinstance(_, nodes.system_message)
    ]
    if len(found) != 1 or type(found[0]) is not nodes.paragraph:
        what = "more than one block"
        if found and all(type(_) is nodes.paragraph for _ in found):
            what = "more than one paragraph"
        if len(found) == 1:
            what = next(
                (name for kind, name in BLOCKS if isinstance(found[0], kind)),
                "a directive",
            )
        raise directive.error(
            f"{directive.name}: expected one paragraph of text, got {what}"
        )
    return (
        located(directive, phrase(text, "", *found[0].children, field=field)),
        messages,
    )


def fields(self: HTMLTranslator, node: nodes.Element) -> dict[str, Markup]:
    """Write the text from `parse` as HTML, one piece for each field.

    :param self: The HTML translator. The translator of the page writes
        each piece, so it reads as a paragraph.
    :param node: The node of the directive, with the text from `parse`.
    :return: The HTML of each field by name, for a template.
    """
    found: dict[str, Markup] = {}
    body = self.body
    for child in node.children:
        if not isinstance(child, phrase) or "field" not in child:
            continue
        self.body = []
        for part in child.children:
            part.walkabout(self)
        found[child["field"]] = Markup("".join(self.body))  # noqa: S704
    self.body = body
    return found


def visitor(
    template: str,
    prepare: Callable[[HTMLTranslator, dict[str, t.Any]], dict[str, t.Any]]
    | None = None,
) -> Callable[[HTMLTranslator, nodes.Element], None]:
    """Make the visitor that writes all of the node of a directive.

    :param template: The template of the directive, relative to
        `theme/templates`. It draws all of the node, so the writer does
        not go into it.
    :param prepare: A function that gets the translator and a copy of
        the attributes of the node, and gives what the template gets. A
        directive changes its paths into addresses there.
    :return: The visitor, which raises `nodes.SkipNode` after it
        writes.
    """

    def visit(self: HTMLTranslator, node: nodes.Element) -> None:
        icons = self.builder.config.html_context["km_fa_icons"]
        attributes = dict(node.attributes)
        if prepare is not None:
            attributes = prepare(self, attributes)
        self.body.append(
            render(
                template, fa_icons=icons, **attributes, **fields(self, node)
            )
        )
        raise nodes.SkipNode

    return visit


def what(found: nodes.Node) -> str:
    """Say what a node is, the way a message names it.

    :param found: The node.
    :return: Its name with an article, `a paragraph` or `an accordion`.
    """
    from kaamiki.extensions import nesting

    return nesting.describe(found)


def listed(value: str) -> list[str]:
    """Split an option with commas into its trimmed parts.

    :param value: The value of the option.
    :return: The parts, in the sequence written.
    """
    return [_.strip() for _ in value.split(",") if _.strip()]


class Option:
    """An option of a directive or a role, read as an attribute."""

    def __init__(
        self,
        check: Callable[[str | None], t.Any],
        *,
        needs: str = "",
        setting: str = "",
        default: t.Any = None,
    ) -> None:
        """Keep how the option is checked.

        :param check: The function that checks the value as written.
        :param needs: The option that must also be there, as
            `subheader`.
        :param setting: The site setting that gives the value when the
            option is absent, as `accordion_marker`.
        :param default: The value when the option and the setting are
            absent.
        """
        self.check = check
        self.needs = needs
        self.setting = setting
        self.default = default
        self.name = ""

    def __set_name__(self, owner: type, name: str) -> None:
        """Name the option as rST writes it, `class-title` for one.

        :param owner: The directive or the role.
        :param name: The attribute. An underscore becomes a dash.
        """
        self.name = name.replace("_", "-")

    @classmethod
    def of(cls, owner: type) -> dict[str, Option]:
        """Collect the options of a class and of its parents.

        :param owner: The directive or the role.
        :return: Each option by its name in rST.
        """
        return {
            each.name: each
            for base in reversed(owner.__mro__)
            for each in vars(base).values()
            if isinstance(each, cls)
        }

    @staticmethod
    def documented(owner: type, names: Iterable[str]) -> None:
        """Make sure that the docstring lists each option.

        :param owner: The directive or the role.
        :param names: The options that it takes.
        :raises TypeError: When the first `Options::` list of the
            docstring does not list each option, and only them.
        """
        options = (owner.__doc__ or "").partition("Options::")[2]
        listed = set(OPTION.findall(options.split("::\n", 1)[0]))
        if listed != set(names):
            raise TypeError(
                f"{owner.__qualname__}: expected the docstring to list"
                f" {sorted(names)}, got {sorted(listed)}"
            )

    @t.overload
    def __get__(self, user: None, owner: type) -> Option: ...

    @t.overload
    def __get__(
        self, user: KaamikiDirective | KaamikiRole, owner: type
    ) -> t.Any: ...

    def __get__(
        self, user: KaamikiDirective | KaamikiRole | None, owner: type
    ) -> t.Any:
        """Read the value of the option in a directive or a role.

        :param user: The directive or the role, or `None` on its class.
        :param owner: The class of the directive or the role.
        :return: For a flag, `True` when it is there. Else the checked
            value, the site setting or the default.
        """
        if user is None:
            return self
        if self.check is rst.directives.flag:
            return self.name in user.options
        if self.name in user.options:
            return user.options[self.name]
        if self.setting:
            return values(user.config)[self.setting]
        return self.default


class KaamikiDirective(SphinxDirective):
    """The base of each Kaamiki directive."""

    registry: t.ClassVar[dict[str, type[KaamikiDirective]]] = {}
    needs: t.ClassVar[dict[str, str]] = {}
    Node: t.ClassVar[type[nodes.Element]]

    def __init_subclass__(
        cls,
        *,
        name: str = "",
        motion: bool = False,
        spec: type[dict[str, t.Any]] = dict,
        abstract: bool = False,
        **kwargs: t.Any,
    ) -> None:
        """Record the directive, collect its options and name its node.

        :param name: The name of the directive in rST. The default is
            the name of the class in lower case.
        :param motion: Whether the directive takes `speed` and
            `no-motion`.
        :param spec: The kind of dictionary for `option_spec`, as one
            that permits more options than it lists.
        :param abstract: Whether the class is only a base for other
            directives. Then it is not recorded or checked.
        :param kwargs: What the parent class takes.
        :raises TypeError: When the docstring does not list each option
            that the directive takes.
        """
        super().__init_subclass__(**kwargs)
        if abstract:
            return
        found = Option.of(cls)
        cls.option_spec = spec(
            {
                **NATIVE,
                **(MOTION if motion else {}),
                **{key: each.check for key, each in found.items()},
            }
        )
        cls.needs = {
            key: each.needs for key, each in found.items() if each.needs
        }
        if "Node" in vars(cls):
            cls.Node.__name__ = cls.__name__
            cls.Node.__qualname__ = f"{cls.__qualname__}.Node"
        Option.documented(cls, cls.option_spec)
        KaamikiDirective.registry[name or cls.__name__.lower()] = cls

    @classmethod
    def made(cls, node: nodes.Node | None) -> bool:
        """Say whether this directive wrote a node.

        :param node: The node to look at.
        :return: `True` when the node is the node of this directive.
        """
        return "Node" in vars(cls) and type(node) is cls.Node

    @property
    def title(self) -> str:
        """The title, which is the argument, trimmed."""
        return titled(self, self.arguments[0])

    @property
    def classes(self) -> list[str]:
        """The classes from `class`, then the classes of its motion."""
        return [*self.options.get("class", []), *moving(self.options)]

    def run(self) -> list[nodes.Node]:
        """Check the options, then make the nodes of the directive.

        :return: What `build` makes.
        """
        for option, need in self.needs.items():
            if option in self.options and need not in self.options:
                self.fail(f":{option}: needs :{need}:")
        self.check()
        return self.build()

    def check(self) -> None:
        """Check what only this directive checks.

        :return: Nothing. By default, it checks nothing.
        """

    def build(self) -> list[nodes.Node]:
        """Make the nodes of the directive.

        :return: The nodes and the messages.
        :raises NotImplementedError: Always. Each directive writes its
            own.
        """
        raise NotImplementedError

    def fail(self, message: str) -> t.NoReturn:
        """Stop the build with a message that starts with the name.

        :param message: The message, without the name of the directive.
        :raises rst.DirectiveError: Always.
        """
        raise self.error(f"{self.name}: {message}")

    def locate[N: nodes.Node](self, node: N) -> N:
        """Give a node the place in the source of the directive.

        :param node: The node.
        :return: The same node.
        """
        return located(self, node)

    def text(
        self, written: str, part: str
    ) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        """Parse a text that must have words and no link.

        :param written: The text, as written in the rST.
        :param part: What the text is, `a title` for one.
        :return: The parsed text and what the parser reported.
        """
        found, messages = self.state.inline_text(written, self.lineno)
        unlinked(self, found, part)
        worded(self, found, part)
        return found, messages

    def fill(
        self, node: nodes.Element, *, besides: tuple[type, ...] = ()
    ) -> None:
        """Parse the content into a node.

        :param node: The node that gets the content.
        :param besides: The kinds of child that are not the content.
        :raises rst.DirectiveError: When the content is empty.
        """
        self.state.nested_parse(self.content, self.content_offset, node)
        if hollow(_ for _ in node.children if not isinstance(_, besides)):
            self.fail("expected some content, got none")

    def add_name(self, node: nodes.Node) -> None:
        """Give the node the name in `name`.

        :param node: The node to name.
        :raises rst.DirectiveError: When the page has the name already.
        """
        named(self, node)
