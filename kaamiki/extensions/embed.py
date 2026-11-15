"""\
Embed Directive
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 11 August 2026
Last updated on: 15 November 2026

An `embed` directive that puts a block of HTML in the page::

    .. embed:: iframe
       :expected-count: 10

       <iframe
           src="https://example.com"
           width="100%"
           height="400px"
           data-expected-count="{{ expected-count }}">
       </iframe>

The argument is `iframe` in lower case, with the markup as the
content. Or it is the path of an HTML fragment, relative to the
document, or to the source directory with a `/` at the start, without
content below the directive. Each option other than `css`, `js`,
`encoding`, `name` and `class` fills the placeholder of the same name,
as `{{ expected-count }}`. The build stops when no option fills a
placeholder, or when no placeholder uses an option. A `{# note #}` in
the fragment does not go on the page. An embed cannot go in the notes
of a walkthrough, or in a block that is a link.

The `css` and `js` options name files in `html_static_path`. They load
in sequence on the pages that use the directive. Here, `embed.html` is
next to the document, and `embed.css` and `embed.js` are in
`html_static_path`::

    .. embed:: embed.html
       :css: embed.css
       :js: embed.js
"""

from __future__ import annotations

import ast
import contextlib
import json
import os.path as p
import re
import typing as t
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import KaamikiDirective
from kaamiki.extensions.utils import Option
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import confdir
from kaamiki.extensions.utils import findall
from kaamiki.extensions.utils import hostnames
from kaamiki.extensions.utils import listed
from kaamiki.extensions.utils import on
from kaamiki.extensions.utils import values

if t.TYPE_CHECKING:
    from collections.abc import Callable

    from sphinx.application import Sphinx


PLACEHOLDER: t.Final[re.Pattern[str]] = re.compile(r"\{\{\s*([\w-]+)\s*\}\}")
# NOTE(xames3): Keeps a value from closing its `<script>` early and
# U+2028/2029 from ending a JavaScript string line.
# https://html.spec.whatwg.org/multipage/scripting.html#restrictions-for-contents-of-script-elements
# https://github.com/tc39/proposal-json-superset
ESCAPES: t.Final[dict[str, str]] = {
    "<": "\\u003c",
    ">": "\\u003e",
    "&": "\\u0026",
    "\u2028": "\\u2028",
    "\u2029": "\\u2029",
}
STYLE_ESCAPES: t.Final[frozenset[str]] = frozenset("<>&\"'\\\n\r{};")
ASSETS: t.Final[frozenset[str]] = frozenset(
    {"css", "js", "encoding", "class", "name"}
)
FRAMES: t.Final[frozenset[str]] = frozenset(
    {"object", "embed", "frame", "frameset"}
)
CONTROLS: t.Final[str] = "".join(map(chr, range(0x21)))


def encode(value: str, kind: str) -> str:
    """Write the value of a placeholder for its place.

    :param value: The value of the option, as written.
    :param kind: `script`, `style`, or another word for markup.
    :return: The value, escaped so that it cannot leave its place:
        HTML-escaped in markup, CSS-escaped in a style, and a JSON
        literal in a script, so `3` is a number there.
    """
    if kind == "script":
        encoded = json.dumps(literal(value), default=str)
        for char, point in ESCAPES.items():
            encoded = encoded.replace(char, point)
        return encoded
    if kind == "style":
        return "".join(
            f"\\{ord(_):x} " if _ in STYLE_ESCAPES else _ for _ in value
        )
    return escape(value, quote=True)


def strip_notes(source: str) -> str:
    """Remove the `{# ... #}` notes from a fragment.

    :param source: The fragment.
    :return: The fragment without its notes, and without the spaces and
        one line break after each note. A note without an end stays.
    """
    kept: list[str] = []
    cursor = 0
    while (start := source.find("{#", cursor)) != -1:
        end = source.find("#}", start + 2)
        if end == -1:
            break
        kept.append(source[cursor:start])
        cursor = end + 2
        while source[cursor : cursor + 1] in (" ", "\t"):
            cursor += 1
        if source.startswith("\n", cursor):
            cursor += 1
    kept.append(source[cursor:])
    return "".join(kept)


class Fragment(HTMLParser):
    """A fragment of HTML, read as a browser reads it."""

    opened: tuple[int, str] | None = None

    def __init__(self, source: str) -> None:
        """Read all of the fragment.

        :param source: The fragment. Then `blocks` holds where each
            `<script>` and `<style>` starts and ends, and which it is.
            `tags` holds each start tag with its attributes, and the
            first tag of a name has priority.
        """
        super().__init__()
        self.lines = [0] + [_.end() for _ in re.finditer("\n", source)]
        self.blocks: list[tuple[int, int, str]] = []
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.feed(source)
        self.close()
        if self.opened is not None:
            self.blocks.append((self.opened[0], len(source), self.opened[1]))

    def at(self) -> int:
        """Say where the current tag starts.

        :return: Its position in the fragment.
        """
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        """Keep a start tag, and where a script or a style starts.

        :param tag: The name of the tag.
        :param attrs: Its attributes, as a list of names and values.
        """
        found: dict[str, str | None] = {}
        for key, value in attrs:
            found.setdefault(key, value)
        self.tags.append((tag, found))
        if tag in ("script", "style"):
            text = self.get_starttag_text() or ""
            self.opened = (self.at() + len(text), tag)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        """Keep a tag that is written with a slash.

        :param tag: The name of the tag. A browser ignores the slash on
            a script or a style, which then continue to their end tag,
            so this reads it as a start tag.
        :param attrs: Its attributes, as a list of names and values.
        """
        self.handle_starttag(tag, attrs)
        if tag not in ("script", "style"):
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        """Close the script or the style that an end tag ends.

        :param tag: The name of the tag.
        """
        if self.opened is not None and self.opened[1] == tag:
            self.blocks.append((self.opened[0], self.at(), tag))
            self.opened = None


def substitute(source: str, values: dict[str, str]) -> str:
    """Fill the placeholders of a fragment, each escaped for its place.

    :param source: The fragment, with its placeholders. It is split at
        the text of its script and style blocks, because each needs a
        different escape. A block without an end continues to the end.
    :param values: The options of the directive, by name as written in
        the rST. A placeholder can use underscores, not hyphens.
    :return: The fragment with each known placeholder filled. An
        unknown placeholder does not change.
    """

    def swap(kind: str) -> Callable[[re.Match[str]], str]:
        def fill(match: re.Match[str]) -> str:
            key = match.group(1).lower()
            if key not in values:
                key = key.replace("_", "-")
            if key not in values:
                return match.group(0)
            return encode(values[key], kind)

        return fill

    out: list[str] = []
    cursor = 0
    for start, end, kind in Fragment(source).blocks:
        out.append(PLACEHOLDER.sub(swap("html"), source[cursor:start]))
        out.append(PLACEHOLDER.sub(swap(kind), source[start:end]))
        cursor = end
    out.append(PLACEHOLDER.sub(swap("html"), source[cursor:]))
    return "".join(out)


type Parsed = (
    str
    | bytes
    | int
    | float
    | complex
    | bool
    | tuple[Parsed, ...]
    | list[Parsed]
    | dict[Parsed, Parsed]
    | set[Parsed]
    | None
)


def literal(value: str) -> Parsed:
    """Read the value of an option as a Python literal when it is one.

    :param value: The value, as written.
    :return: A number, a list or a similar value when it reads as one,
        else the text. Only a script needs this.
    """
    with contextlib.suppress(ValueError, SyntaxError):
        return t.cast("Parsed", ast.literal_eval(value))
    return value


class placeholders(dict[str, "Callable[[str], t.Any]"]):
    """The options of `embed`, with other names as placeholders."""

    def __missing__(self, key: str) -> Callable[[str], t.Any]:
        """Give the converter for a placeholder.

        :param key: The name of the option.
        :return: The converter, which reads the value as text, so that
            docutils does not refuse an unknown option.
        """
        return rst.directives.unchanged


class Embed(KaamikiDirective, spec=placeholders):
    """The `embed` directive.

    Options::

        - `css`: Stylesheets in `html_static_path`, with a comma
          between each.
        - `js`: Scripts in `html_static_path`, with a comma between
          each.
        - `encoding`: The encoding of the fragment file. The default
          is `utf-8`. It needs a file, because inline markup has no
          encoding.
        - `name`: A name for links.
        - `class`: More classes for the `<div>` around the embed.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    css = Option(rst.directives.unchanged)
    js = Option(rst.directives.unchanged)
    encoding = Option(checks.encoding)

    @classmethod
    def made(cls, node: nodes.Node | None) -> bool:
        """Say whether a node is an embed, which is a container.

        :param node: The node to look at.
        :return: `True` for an embed, which holds the `raw` node of its
            styles and scripts. A container from an author does not
            hold it.
        """
        return type(node) is nodes.container and any(
            isinstance(each, nodes.raw) and "css" in each
            for each in node.children
        )

    def build(self) -> list[nodes.Node]:
        """Read the markup, fill its placeholders and give it back.

        :return: One `raw` node, which also holds the stylesheets and
            scripts that the page must load, in a `container` that gets
            the `class` classes.
        """
        file = self.arguments.pop().strip()
        self.assets()
        if file == "iframe":
            if not "".join(self.content).strip():
                self.fail("expected inline HTML content, got none")
            if "encoding" in self.options:
                self.fail(
                    ":encoding: expected a fragment file, got inline HTML"
                )
            source = "\n".join(self.content)
        else:
            source = self.read(file)
        source = strip_notes(source)
        values = {
            key: value.strip()
            for key, value in self.options.items()
            if key not in ASSETS
        }
        self.match(source, values)
        attributes: dict[str, t.Any] = {}
        attributes["text"] = substitute(source, values)
        self.guard(attributes["text"])
        attributes["format"] = "html"
        attributes["css"] = listed(self.options.get("css", ""))
        attributes["js"] = listed(self.options.get("js", ""))
        element = nodes.raw(**attributes)
        classes = ["km-embed", *self.options.get("class", [])]
        wrapper = self.locate(nodes.container("", element, classes=classes))
        self.add_name(wrapper)
        return [wrapper]

    def assets(self) -> None:
        """Check the styles and the scripts that the options name.

        :raises rst.DirectiveError: For a style or a script that is not
            a file in `html_static_path`. Each file found is a
            dependency of the page, so when the file is deleted, the
            page is built again.
        """
        env = self.env
        options = self.options
        statics = [p.join(confdir(env), _) for _ in env.config.html_static_path]
        for option, suffix in (("css", ".css"), ("js", ".js")):
            for file_name in listed(options.get(option, "")):
                if not file_name.endswith(suffix) or not checks.FILE.fullmatch(
                    file_name
                ):
                    self.fail(
                        f":{option}: expected a {suffix} file, got "
                        f"{file_name!r}"
                    )
                path = next(
                    (
                        p.join(_, file_name)
                        for _ in statics
                        if p.isfile(p.join(_, file_name))
                    ),
                    None,
                )
                if path is None:
                    self.fail(
                        f":{option}: expected a file in"
                        f" html_static_path, got {file_name!r}"
                    )
                env.note_dependency(path)

    def match(self, source: str, values: dict[str, str]) -> None:
        """Find an option or a placeholder with a spelling mistake.

        :param source: The fragment, with its placeholders.
        :param values: The options that fill placeholders.
        :raises rst.DirectiveError: For an option that no placeholder
            uses, or a placeholder that no option fills.
        """
        wanted = {
            _.lower().replace("_", "-") for _ in PLACEHOLDER.findall(source)
        }
        unused = sorted(_ for _ in values if _.replace("_", "-") not in wanted)
        if unused:
            self.fail(
                f"{', '.join(f':{_}:' for _ in unused)} expected a"
                " placeholder in the fragment, got none"
            )
        given = {_.replace("_", "-") for _ in values}
        for key in sorted(wanted - given):
            self.fail(
                f"{{{{ {key} }}}} expected an option to fill it, got none"
            )

    def guard(self, markup: str) -> None:
        """Keep an `<iframe>` to the hosts that the site permits.

        :param markup: The embedded HTML, with its placeholders filled.
            Without `kaamiki.conf.embed.iframe_hosts`, nothing is
            checked. With it, a relative path is permitted, and a
            different host must be on the list or a subdomain of a host
            on it. The markup is read as a browser reads it, so the
            sequence of the attributes, a `>` in a quoted value or a
            backslash in the address cannot get a frame past the list.
        :raises rst.DirectiveError: When an iframe comes from a host
            that is not permitted, or a `<script>` has `iframe` in it.
        """
        config = self.config
        allowed = hostnames(values(config).embed.iframe_hosts, www=True)
        if not allowed:
            return
        fragment = Fragment(markup)
        for start, end, kind in fragment.blocks:
            if kind == "script" and "iframe" in markup[start:end].lower():
                self.fail(
                    "expected a script that builds no iframe, got one,"
                    " which kaamiki.conf.embed.iframe_hosts can't check"
                )
        for tag, attributes in fragment.tags:
            banned = "srcdoc" if "srcdoc" in attributes else f"<{tag}>"
            if tag in FRAMES or "srcdoc" in attributes:
                self.fail(
                    f"expected no {banned}, got one, which "
                    "kaamiki.conf.embed.iframe_hosts can't check"
                )
            src = attributes.get("src")
            if (
                tag == "iframe"
                and src is not None
                and not self.allows(src, allowed)
            ):
                self.fail(
                    "expected an iframe from one of"
                    f" {', '.join(sorted(allowed))} in"
                    f" kaamiki.conf.embed.iframe_hosts, got {src!r}"
                )

    @staticmethod
    def allows(src: str, allowed: set[str]) -> bool:
        """Say whether the site permits the source of an iframe.

        :param src: The `src` attribute. It is read as a browser reads
            it: the spaces and control characters around it and the
            tabs and line breaks in it go, a backslash is a slash, and
            slashes at the start are two.
        :param allowed: The hosts that the site permits.
        :return: `True` for `about:blank`, a path, and an `http` or
            `https` address on a permitted host or its subdomain. An
            address with a scheme and no `//` after it is refused,
            because a browser can read it as a host.
        """
        text = re.sub(r"[\t\r\n]", "", src.strip(CONTROLS))
        text = re.sub(r"^[/\\]{2,}", "//", text.replace("\\", "/"))
        if text.lower() == "about:blank":
            return True
        try:
            parts = urlsplit(text)
        except ValueError:
            return False
        if parts.scheme not in ("", "http", "https"):
            return False
        if parts.scheme and not parts.netloc:
            return False
        host = parts.hostname or ""
        return not parts.netloc or any(
            host == _ or host.endswith(f".{_}") for _ in allowed
        )

    def read(self, file: str) -> str:
        """Read an HTML fragment from the disk.

        :param file: The path as written, relative to the document, or
            to the source directory when it starts with a `/`.
        :return: The fragment.
        """
        if self.content:
            self.fail(
                "expected iframe in lower case for inline HTML or the"
                f" path to a fragment file with no content below it, got"
                f" {file!r}"
            )
        if any(ord(_) < 32 for _ in file):
            self.fail(
                f"expected a file name without control characters, got {file!r}"
            )
        env = self.env
        relative, path = env.relfn2path(file, env.docname)
        if p.commonpath(
            [p.realpath(path), p.realpath(env.srcdir)]
        ) != p.realpath(env.srcdir):
            self.fail(
                f"expected a file inside the source directory, got {file!r}"
            )
        try:
            with open(
                path, encoding=self.options.get("encoding", "utf-8")
            ) as fd:
                source = fd.read()
        except (OSError, UnicodeError) as error:
            self.fail(f"expected a file it can read, got {file!r} ({error})")
        env.note_dependency(relative)
        return source


@on("html-page-context")
def html_page_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Give the page its embedded stylesheets and scripts.

    :param app: The Sphinx application instance. The
        `kaamiki.conf.embed.css` and `kaamiki.conf.embed.js` of the
        site come first, then those of the page in their sequence, each
        one time. A page without an `embed` gets none.
    :param pagename: The page that is written.
    :param templatename: The template that writes it.
    :param context: The context of the page, changed in place.
    :param doctree: The resolved doctree, or `None` for a generated
        page.
    """
    del pagename, templatename
    context["km_embed_css"] = []
    context["km_embed_js"] = []
    if doctree is None:
        return
    embeds = [_ for _ in findall(doctree, nodes.raw) if "css" in _]
    if not embeds:
        return
    css = dict.fromkeys(values(app.config).embed.css)
    js = dict.fromkeys(values(app.config).embed.js)
    for raw in embeds:
        css.update(dict.fromkeys(raw.get("css", ())))
        js.update(dict.fromkeys(raw.get("js", ())))
    context["km_embed_css"] = list(css)
    context["km_embed_js"] = list(js)
