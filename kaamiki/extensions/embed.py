"""\
Embed Directive
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 11 August 2026
Last updated on: 07 November 2026

An `embed` directive that drops a block of HTML into the page.

    .. embed:: iframe
       :expected-count: 10

       <iframe
           src="https://example.com"
           width="100%"
           height="400px"
           data-expected-count="{{ expected-count }}">
       </iframe>

Every other option is a placeholder, so `{{ expected-count }}` is
replaced by the option's value, escaped for where it lands. In markup
and in a `<style>` the value is written as it was written. In a
`<script>` it is read as a Python literal first, so `10` is a number
there and `'10'` a string.

A larger embed can live in a file of its own, named as the argument,
relative to the document or to the source directory with a leading `/`.
The `:css:` and `:js:` options are for the files under
`html_static_path`, which load in order on the pages that use the
directive::

    .. embed:: ../assets/html/embed.html
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

from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import confdir
from kaamiki.extensions.utils import findall
from kaamiki.extensions.utils import hostnames
from kaamiki.extensions.utils import listed
from kaamiki.extensions.utils import located
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import setting

if t.TYPE_CHECKING:
    from collections.abc import Callable

    from sphinx.application import Sphinx


name: t.Final[str] = "embed"
PLACEHOLDER: re.Pattern[str] = re.compile(r"\{\{\s*([\w-]+)\s*\}\}")
# NOTE(xames3): Keeps a value from closing its `<script>` early and
# U+2028/2029 from ending a JavaScript string line.
# https://html.spec.whatwg.org/multipage/scripting.html#restrictions-for-contents-of-script-elements
# https://github.com/tc39/proposal-json-superset
ESCAPES: dict[str, str] = {
    "<": "\\u003c",
    ">": "\\u003e",
    "&": "\\u0026",
    "\u2028": "\\u2028",
    "\u2029": "\\u2029",
}
STYLE_ESCAPES: frozenset[str] = frozenset("<>&\"'\\\n\r{};")
ASSETS: t.Final[frozenset[str]] = frozenset(
    {"css", "js", "encoding", "class", "name"}
)
FRAMES: t.Final[frozenset[str]] = frozenset(
    {"object", "embed", "frame", "frameset"}
)
CONTROLS: t.Final[str] = "".join(map(chr, range(0x21)))


def encode(value: str, kind: str) -> str:
    """Write a placeholder's value for where it sits.

    :param value: The option's value, as written.
    :param kind: `script`, `style` or anything else for markup.
    :return: The value, escaped so it can't break out of its place. A
        script gets it as a literal, a number for `3`, and markup and
        style get it as written.
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
    """Take the `{# ... #}` notes out of a fragment.

    The spaces after a note and one line break go with it. Each note is
    found by looking for its end, so a fragment of openings and no end
    costs no more than any other of its length.

    :param source: The fragment.
    :return: The fragment without its notes. A note that never ends is
        left in.
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
    """A fragment of HTML, read the way a browser tokenises it.

    :param source: The fragment.
    """

    opened: tuple[int, str] | None = None

    def __init__(self, source: str) -> None:
        """Read the whole fragment.

        `blocks` holds the text of each `<script>` and `<style>` as
        where it starts, where it ends and which it is, and `tags`
        every start tag with its attributes, the first of a name
        winning.
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
        """Say where the tag being handled starts.

        :return: Its place in the fragment.
        """
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        """Keep a start tag, and where a script or a style begins.

        :param tag: The tag's name.
        :param attrs: Its attributes, a list of names and values.
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
        """Keep a tag written with a slash.

        A browser ignores the slash on a script or a style, which then
        go on to their end tag, so it is read as a start tag here.

        :param tag: The tag's name.
        :param attrs: Its attributes, a list of names and values.
        """
        self.handle_starttag(tag, attrs)
        if tag not in ("script", "style"):
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        """Close the script or style an end tag ends.

        :param tag: The tag's name.
        """
        if self.opened is not None and self.opened[1] == tag:
            self.blocks.append((self.opened[0], self.at(), tag))
            self.opened = None


def substitute(source: str, values: dict[str, str]) -> str:
    """Fill a fragment's placeholders, escaping each for where it sits.

    Markup, `<script>` and `<style>` want different escaping, so the
    source is split on the text of its script and style blocks and each
    part gets its own. A block that never ends runs to the end.

    :param source: The fragment, placeholders and all.
    :param values: Directive options, keyed as they're written in the
        rST. A placeholder may spell them with underscores instead of
        hyphens.
    :return: The fragment with every known placeholder filled in.
        Anything unrecognised is left alone.
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
    """Read an option's value as a Python literal where it's one.

    A script is the one place that wants it, `3` is a number there.

    :param value: The value, as written.
    :return: A number, list or the like when it reads as one and the
        text otherwise.
    """
    with contextlib.suppress(ValueError, SyntaxError):
        return t.cast("Parsed", ast.literal_eval(value))
    return value


class placeholders(dict[str, "Callable[[str], t.Any]"]):
    """The option specification of `embed`.

    It holds the options `embed` has of its own. Any other name is the
    value of a placeholder, so docutils reads it as text instead of
    refusing it as an unknown option.
    """

    def __missing__(self, key: str) -> Callable[[str], t.Any]:
        """Answer for a placeholder.

        :param key: The option's name.
        :return: The converter that reads its value as text.
        """
        return rst.directives.unchanged


class directive(rst.Directive):
    """The `embed` directive.

    The argument is `iframe` in lower case, with the markup as content,
    or the path to an HTML fragment with nothing below the directive.
    An embed can't sit in the notes of a walkthrough, nor in a block
    that links.

    Options::

        - `css`: Stylesheets under `html_static_path`, comma-separated.
        - `js`: Scripts under `html_static_path`, comma-separated.
        - `encoding`: The fragment file's encoding. Defaults to
          `utf-8`. It needs a file, markup written inline has none.
        - `name`: A name to link to.
        - `class`: More classes for the `<div>` wrapped around the
          embed.

    Every other option is a placeholder's value. Option names are
    lowercase, as docutils reads them, and so are the placeholders. A
    value is written as it was written, except in a `<script>`, where
    it's read as a Python literal.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = placeholders(
        {
            "css": rst.directives.unchanged,
            "js": rst.directives.unchanged,
            "encoding": checks.encoding,
            **NATIVE,
        }
    )

    def run(self) -> list[nodes.Node]:
        """Read the markup, fill its placeholders and return it.

        :return: A list holding the one `raw` node, which also carries
            the stylesheets and scripts the page is to load for it. It
            sits in a `container`, which `:class:` adds classes to.
        """
        file = self.arguments.pop().strip()
        self.assets()
        if file == "iframe":
            if not "".join(self.content).strip():
                raise self.error(
                    "embed: expected inline HTML content, got none"
                )
            if "encoding" in self.options:
                raise self.error(
                    "embed: :encoding: expected a fragment file, got inline"
                    " HTML"
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
        self.check(source, values)
        attributes: dict[str, t.Any] = {}
        attributes["text"] = substitute(source, values)
        self.guard(attributes["text"])
        attributes["format"] = "html"
        attributes["css"] = listed(self.options.get("css", ""))
        attributes["js"] = listed(self.options.get("js", ""))
        element = nodes.raw(**attributes)
        classes = ["km-embed", *self.options.get("class", [])]
        wrapper = located(self, nodes.container("", element, classes=classes))
        named(self, wrapper)
        return [wrapper]

    def assets(self) -> None:
        """Check the styles and scripts, the options that name files.

        Each file found is a dependency of the page, so deleting it
        makes the page out of date.

        :raises rst.DirectiveError: For a style or a script that isn't
            a file under `html_static_path`.
        """
        env = self.state.document.settings.env
        options = self.options
        statics = [p.join(confdir(env), _) for _ in env.config.html_static_path]
        for option, suffix in (("css", ".css"), ("js", ".js")):
            for file_name in listed(options.get(option, "")):
                if not file_name.endswith(suffix) or not checks.FILE.fullmatch(
                    file_name
                ):
                    raise self.error(
                        f"embed: :{option}: expected a {suffix} file, got "
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
                    raise self.error(
                        f"embed: :{option}: expected a file in"
                        f" html_static_path, got {file_name!r}"
                    )
                env.note_dependency(path)

    def check(self, source: str, values: dict[str, str]) -> None:
        """Catch an option or a placeholder that's been misspelt.

        An option the fragment never asks for is an error, and so is a
        placeholder no option fills.

        :param source: The fragment, placeholders and all.
        :param values: The options that fill placeholders.
        """
        wanted = {
            _.lower().replace("_", "-") for _ in PLACEHOLDER.findall(source)
        }
        unused = sorted(_ for _ in values if _.replace("_", "-") not in wanted)
        if unused:
            raise self.error(
                f"embed: {', '.join(f':{_}:' for _ in unused)} expected a"
                " placeholder in the fragment, got none"
            )
        given = {_.replace("_", "-") for _ in values}
        for key in sorted(wanted - given):
            raise self.error(
                f"embed: {{{{ {key} }}}} expected an option to fill it,"
                " got none"
            )

    def guard(self, markup: str) -> None:
        """Keep an `<iframe>` to the hosts the site allows.

        Nothing is checked without `kaamiki.conf.embed.iframe_hosts`.
        With it, a source on a relative path is allowed and one from
        another host has to be on the list, or on a subdomain of a host
        that is. The markup is read the way a browser reads it, so the
        order of the attributes, a `>` in a quoted one or a backslash
        in the address won't get a frame past the list.

        It catches a mistake and not an author set on getting round it:
        a script can build a frame in ways no check can read, so one
        that says `iframe` is refused and the rest are let through.

        :param markup: The embedded HTML, placeholders filled in.
        :raises rst.DirectiveError: When an iframe comes from a host
            that isn't allowed.
        """
        config = self.state.document.settings.env.config
        allowed = hostnames(setting(config, "embed_iframe_hosts"), www=True)
        if not allowed:
            return
        fragment = Fragment(markup)
        for start, end, kind in fragment.blocks:
            if kind == "script" and "iframe" in markup[start:end].lower():
                raise self.error(
                    "embed: expected a script that builds no iframe, got one,"
                    " which kaamiki.conf.embed.iframe_hosts cannot check"
                )
        for tag, attributes in fragment.tags:
            banned = "srcdoc" if "srcdoc" in attributes else f"<{tag}>"
            if tag in FRAMES or "srcdoc" in attributes:
                raise self.error(
                    f"embed: expected no {banned}, got one, which "
                    "kaamiki.conf.embed.iframe_hosts cannot check"
                )
            src = attributes.get("src")
            if (
                tag == "iframe"
                and src is not None
                and not self.allows(src, allowed)
            ):
                raise self.error(
                    "embed: expected an iframe from one of"
                    f" {', '.join(sorted(allowed))} in"
                    f" kaamiki.conf.embed.iframe_hosts, got {src!r}"
                )

    @staticmethod
    def allows(src: str, allowed: set[str]) -> bool:
        """Say whether an iframe's source is one the site allows.

        The address is read as a browser reads it: the spaces and
        control characters around it go, so do tabs and line breaks
        inside it, a backslash is a slash and a run of slashes at the
        start is two.

        :param src: The `src` attribute.
        :param allowed: The hosts the site allows.
        :return: `True` for `about:blank`, a path and an `http` or
            `https` address on an allowed host or a subdomain of one.
            An address with a scheme and no `//` after it is refused,
            since a browser may read it as a host.
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
        """Read an HTML fragment off disk.

        The path is relative to the document or to the source directory
        when it starts with a `/`.

        :param file: The path, as written.
        :return: The fragment.
        """
        if self.content:
            raise self.error(
                "embed: expected iframe in lower case for inline HTML or the"
                f" path to a fragment file with no content below it, got"
                f" {file!r}"
            )
        if any(ord(_) < 32 for _ in file):
            raise self.error(
                "embed: expected a file name without control characters"
            )
        env = self.state.document.settings.env
        relative, path = env.relfn2path(file, env.docname)
        if p.commonpath(
            [p.realpath(path), p.realpath(env.srcdir)]
        ) != p.realpath(env.srcdir):
            raise self.error(
                "embed: expected a file inside the source directory, got"
                f" {file!r}"
            )
        try:
            with open(
                path, encoding=self.options.get("encoding", "utf-8")
            ) as fd:
                source = fd.read()
        except (OSError, UnicodeError) as error:
            raise self.error(
                f"embed: expected a file it can read, got {file!r} ({error})"
            ) from error
        env.note_dependency(relative)
        return source


def html_page_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Hand the page its own embedded stylesheets and scripts.

    The site's `kaamiki.conf.embed.css` and `kaamiki.conf.embed.js`
    come first, then the page's own in the order it names them, each
    once. They go in the page's context, so a page without an `embed`
    gets none.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree or `None` for generated
        pages.
    """
    del pagename, templatename
    context["km_embed_css"] = []
    context["km_embed_js"] = []
    if doctree is None:
        return
    embeds = [_ for _ in findall(doctree, nodes.raw) if "css" in _]
    if not embeds:
        return
    css = dict.fromkeys(setting(app.config, "embed_css"))
    js = dict.fromkeys(setting(app.config, "embed_js"))
    for raw in embeds:
        css.update(dict.fromkeys(raw.get("css", ())))
        js.update(dict.fromkeys(raw.get("js", ())))
    context["km_embed_css"] = list(css)
    context["km_embed_js"] = list(js)
