"""\
Code Explain Directive
======================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 12 September 2026
Last updated on: 07 November 2026

A `code-explain` directive that steps a reader through a snippet, line
by line, with the values it held at each one... telling a story::

    .. code-explain:: python
       :caption: xsnumpy/_core.py
       :watch: shape, stride, strides

       .. setup::

           itemsize = 8

       .. code::

           def calc_strides(shape, itemsize):
               strides = []
               stride = itemsize
               for dim in reversed(shape):
                   strides.append(stride)
                   stride *= dim
               return tuple(reversed(strides))

           calc_strides((3, 4), itemsize)

       .. lines:: 4-6

           Then I walk the shape **backwards**.

.. note::

    Python is only run when a site sets `kaamiki.conf.code_explain.run`
    to `True` in `conf.py`, and then it runs for every page the site
    builds. Without it a Python walkthrough stops the build.
    The Python runs in a scratch directory with a bare environment,
    1GB of memory for each process where the system keeps to the limit,
    10 seconds and 64MB for any file it writes or prints.

    The directory goes when it finishes and so does anything the
    snippet left running, children that went off on their own included
    on Linux. Those are limits and not a sandbox.

    The snippet runs as the user building the site, so it can read what
    that user can, the build's environment included
    (on Linux through `/proc`), write elsewhere and reach the network.

    Build only pages you trust and keep secrets out of any build that
    runs them. A site changes the limits, and what the snippet may run
    with, through `kaamiki.conf.code_explain` in `conf.py`. A snippet's
    own `:limit:` and `:timeout:` can lower what the site sets but not
    go past it. A trace is kept next to the doctrees and used again
    while the snippet, its options, the interpreter, the installed
    packages and the files it imported stay the same.
"""

from __future__ import annotations

import json
import os.path as p
import re
import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst
from sphinx.directives.code import CodeBlock

from kaamiki.extensions.code.chrome import comment
from kaamiki.extensions.code.chrome import controls
from kaamiki.extensions.code.chrome import known
from kaamiki.extensions.code.chrome import label
from kaamiki.extensions.code.chrome import lexer_for
from kaamiki.extensions.code.chrome import notes_pane
from kaamiki.extensions.code.chrome import output
from kaamiki.extensions.code.chrome import visit_explanation
from kaamiki.extensions.code.grammar import linerange
from kaamiki.extensions.code.grammar import split
from kaamiki.extensions.code.tracer import collapse
from kaamiki.extensions.code.tracer import execute
from kaamiki.extensions.code.tracer import replay
from kaamiki.extensions.code.tracer import show
from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import annotated
from kaamiki.extensions.utils import caption_icon
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import close
from kaamiki.extensions.utils import findall
from kaamiki.extensions.utils import listed
from kaamiki.extensions.utils import located
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils import skip
from kaamiki.extensions.utils.icons import Icons
from kaamiki.extensions.utils.settings import BOUNDS
from kaamiki.extensions.utils.settings import TRACE_EVENTS
from kaamiki.extensions.utils.settings import option as conf_path

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

    from kaamiki.extensions.code.grammar import chunk
    from kaamiki.extensions.code.tracer import Trace

name: t.Final[str] = "code-explain"
CODE_POSITIONS: t.Final[tuple[str, str]] = ("right", "left")
SHARED: t.Final[dict[str, t.Any]] = {
    "code-position": checks.word(*CODE_POSITIONS),
    "pace": checks.integer(*map(int, BOUNDS["pace"])),
    "caption": checks.text,
    "lineno-start": checks.integer(*map(int, BOUNDS["code_explain_lineno"])),
}
NAME: t.Final[re.Pattern[str]] = re.compile(
    r"[A-Za-z_][\w]*(?:\.[A-Za-z_]\w*|\[[\w'\"-]+\])*"
)
BLOCKS: t.Final[frozenset[str]] = frozenset({"code", "setup", "stdin", "lines"})
OPTIONS: t.Final[dict[str, frozenset[str]]] = {
    "lines": frozenset({"at", "clear", "output", "values"}),
}
DEFAULT_EVENTS: t.Final[frozenset[str]] = frozenset({"line", "return"})
SCRIPT: t.Final[str] = "scripts/explainer.js"
PYTHON: t.Final[frozenset[str]] = frozenset({"py", "py3", "python", "python3"})
TRACED: t.Final[tuple[str, ...]] = (
    "comprehensions",
    "events",
    "limit",
    "pythonpath",
    "raises",
    "timeout",
    "watch",
)
VALUE: re.Pattern[str] = re.compile(r"^\s*([^=:]+?)\s*[:=]\s*(.*?)\s*$")
ENTRIES: re.Pattern[str] = re.compile(
    r"\n|;\s*(?=[A-Za-z_][\w.\[\]]*\s*[:=](?!=))"
)
PACE: t.Final[int] = 72
PACES: t.Final[tuple[tuple[int, frozenset[str]], ...]] = (
    (104, frozenset({"bash"})),
    (120, frozenset({"c"})),
    (128, frozenset({"c++", "rust"})),
)


class CodeExplain(annotated):
    """The parsed directive, waiting for `visit` to write it out.

    It's a `container` underneath, so a builder that has never heard of
    a walkthrough still has something to write.
    """


class heading(nodes.paragraph):
    """The caption, parsed as rST and the language's icon.

    docutils already has a `caption` node and finds visitors by class
    name, so this can't borrow that one.
    """


class plain_code(nodes.literal_block):
    """The snippet as a plain code block, for every builder
    except HTML.
    """


class explanations(nodes.container):
    """The notes beside the snippet, scrolling past it."""


class explanation(nodes.container):
    """One `lines` block's note."""


def names(argument: str | None) -> str:
    """Check the names a walkthrough watches.

    :param argument: The names as written, comma-separated.
    :return: The names.
    :raises ValueError: For one that isn't a Python name, or a
        dotted name or an index of one.
    """
    found = checks.text(argument)
    for each in listed(found):
        if not NAME.fullmatch(each):
            raise ValueError(
                f"expected Python names like total or self.x[0], got {each!r}"
            )
    return found


def comment_marks(argument: str | None) -> str:
    """Check how a language opens a comment and closes one.

    :param argument: The one or two marks as written.
    :return: The marks.
    :raises ValueError: For more than two or for marks that are text.
    """
    found = checks.text(argument, 12).split()
    if len(found) > 2 or any(_.isalnum() for _ in found):
        raise ValueError(
            f"expected a comment mark like # or (* *), got {argument!r}"
        )
    return " ".join(found)


class directive(CodeBlock):
    """The `code-explain` directive.

    The notes scroll past the code instead of swapping under it, so it
    needs at least one `.. lines::` block. It stands alone, nothing
    around it is pulled in or moved. It goes on the page itself, where
    a plain `container` or an `only` still counts as the page, and not
    in another directive's content, another walkthrough's notes
    included.

    Options::

        - `code-position`: Which side the code sits on, `right` for
          the default or `left`.
        - `watch`: Names to show, comma-separated. Without it only a
          function's return value and what the snippet raises show.
        - `limit`: How many steps to show, from 1 to 300 and up to the
          site's `kaamiki.conf.code_explain.limit`, which is 100 unless
          it says otherwise.
        - `timeout`: How long the snippet may run, in seconds, from 1
          to 60 and up to the site's
          `kaamiki.conf.code_explain.timeout`.
        - `pythonpath`: Directories to import from, comma-separated
          and relative to the document. One that isn't there stops the
          build.
        - `events`: Which of `call`, `line` and `return` make a step.
          Defaults to `line` and `return`.
        - `comprehensions`: Step into comprehensions too, which a site
          can do for every snippet with
          `kaamiki.conf.code_explain.comprehensions`.
        - `pace`: Pixels of scrolling a step takes, from 24 to 240.
          Defaults to what `pace` picks for the language.
        - `raises`: The snippet is meant to fail, so it ends on the
          exception. Without it a snippet that raises stops the build,
          and with it one that runs to the end does too.
        - `comment`: How the language opens a comment and closes one
          if it must (`(* *)`), for a language Kaamiki doesn't know.
        - `caption`: A line of text above the code, parsed as rST.
        - `linenos`: Number the lines.
        - `lineno-start`: The number the first line is given, from 0 to
          10000.
        - `emphasize-lines`: Lines to highlight, as `1, 3-5`.
        - `name`: A name to link the `code-explain` by.
        - `class`: More classes for the `code-explain`.

    A `lines` block takes a range of lines as its argument, like `4-6`,
    and the options below. A note is shown for each block, in the order
    written.

    Options of a `lines` block::

        - `at`: The line the note's values are written beside, within
          the snippet. Defaults to the last line of the range.
        - `clear`: Names to stop showing from this note on,
          comma-separated. Each must be showing already.
        - `output`: What the note prints, shown under the code. A
          backslash and an n start a new line.
        - `values`: The values to show from this note on, written as
          `name: value`, one to a line or split by semicolons. A name
          written again takes the new value.
    """

    option_spec = {  # noqa: RUF012
        **{
            key: value
            for key, value in CodeBlock.option_spec.items()
            if key not in {"dedent", "force"}
        },
        **SHARED,
        "watch": names,
        "limit": checks.integer(*map(int, BOUNDS["code_explain_limit"])),
        "timeout": checks.integer(*map(int, BOUNDS["code_explain_timeout"])),
        "pythonpath": checks.text,
        "events": checks.text,
        "comprehensions": rst.directives.flag,
        "raises": rst.directives.flag,
        "comment": comment_marks,
        **NATIVE,
        "emphasize-lines": checks.text,
    }

    def run(self) -> list[nodes.Node]:
        """Step through the snippet and return the walkthrough.

        :return: A list holding the one `code-explain` node.
        """
        language = self.arguments.pop().strip() if self.arguments else "python"
        if not known(language):
            raise self.error(
                f"{self.name}: expected a language Pygments knows, got"
                f" {language!r}"
            )
        code, setup, stdin, notes = self.blocks()
        if not notes:
            raise self.error(
                "code-explain: expected a `.. lines::` block per note, got none"
            )
        start = self.options.get("lineno-start", 1)
        total = len(code.splitlines())
        ranges = [self.span(_.argument, start, total) for _ in notes]
        traced = language.lower() in PYTHON
        if traced:
            steps = self.trace(code, setup, stdin, notes, ranges, start)
        else:
            steps = self.recite(setup, stdin, notes, ranges, start, total)
        attributes: dict[str, t.Any] = {}
        attributes["classes"] = self.options.get("class", [])
        attributes["position"] = self.options.get("code-position", "right")
        attributes["payload"] = {
            "steps": [compact(_) for _ in steps],
            "pace": self.options.get("pace", pace(language)),
            "code": code,
            "comment": self.marker(language, steps),
        }
        if traced and setup:
            attributes["payload"]["setup"] = setup
        attributes["pane"] = notes_pane(
            code,
            language,
            start,
            self.emphasis(start, total),
            linenos="linenos" in self.options,
        )
        element = located(self, CodeExplain("", **attributes))
        element += self.caption(language)
        element += self.snippet(code, language, start)
        element += self.explain(notes)
        named(self, element)
        return [element]

    def cache(self) -> str | None:
        """Name the folder traces are kept in, unless the site turned
        that off.

        It sits with the doctrees, so a build that starts over with
        `-E` and `-a` keeps it and deleting the build takes it away.

        :return: The folder or `None` for no cache.
        """
        env = self.state.document.settings.env
        if not setting(env.config, "code_explain_cache"):
            return None
        return p.join(str(env.doctreedir), "kaamiki-code-explain")

    def capped(self, option: str, key: str) -> int:
        """Read a number the snippet asks for, up to what the site
        allows.

        :param option: The directive's option.
        :param key: The setting that holds the most it may ask for.
        :return: What the snippet asked for or the most.
        :raises rst.DirectiveError: When it asks for more than the site
            allows.
        """
        most = setting(self.state.document.settings.env.config, key)
        asked = self.options.get(option, most)
        if asked > most:
            raise self.error(
                f"{self.name}: :{option}: expected at most {most} as"
                f" {conf_path(key)} allows, got {asked!r}"
            )
        return int(asked)

    def blocks(self) -> tuple[str, str, str, list[chunk]]:
        """Pull the snippet, its setup, its input and its notes out.

        :return: The snippet, the setup, what `input()` reads and the
            `lines` blocks in the order they were written.
        """
        try:
            found = split(self.content, self.content_offset, BLOCKS, OPTIONS)
        except KeyError as exc:
            line, key, block = exc.args
            takes = ", ".join(f":{_}:" for _ in sorted(OPTIONS[block]))
            raise self.error(
                f"{self.name}: `.. {block}::` on line {line} expected one of"
                f" {takes}, each once, got :{key}:"
            ) from exc
        except ValueError as exc:
            line, text = exc.args
            raise self.error(
                "code-explain: expected text inside a `.. code::`,"
                " `.. setup::`, `.. stdin::` or `.. lines::`, got"
                f" {text!r} on line {line}"
            ) from exc
        for block in ("code", "setup", "stdin"):
            if sum(_.name == block for _ in found) > 1:
                raise self.error(
                    "code-explain: expected one `.. "
                    f"{block}::` block, got more than one"
                )
        code = next((_ for _ in found if _.name == "code"), None)
        if code is None:
            raise self.error(
                "code-explain: expected one `.. code::` block, got none"
            )
        if not code.text().strip():
            raise self.error(
                "code-explain: expected some code in the `.. code::`, got none"
            )
        setup = next((_.text() for _ in found if _.name == "setup"), "")
        stdin = next((_.text() for _ in found if _.name == "stdin"), "")
        notes = [_ for _ in found if _.name == "lines"]
        return code.text(), setup, stdin, notes

    def span(self, argument: str, start: int, total: int) -> tuple[int, int]:
        """Read the lines a `lines` block explains.

        :param argument: The block's argument, as written.
        :param start: The number the snippet's first line is given.
        :param total: How many lines the snippet has.
        :return: The first and the last line it covers.
        """
        found = linerange(argument)
        if found is None:
            raise self.error(
                f"{self.name}: :lines: expected a line range, got {argument!r}"
            )
        low, high = found
        if low > high:
            raise self.error(
                f"{self.name}: :lines: expected a range that runs up, got "
                f"{argument!r}"
            )
        if low < start or high > start + total - 1:
            raise self.error(
                f"{self.name}: :lines: expected a range within"
                f" {label(start, start + total - 1)}, got {label(low, high)}"
            )
        return found

    def trace(
        self,
        code: str,
        setup: str,
        stdin: str,
        notes: list[chunk],
        ranges: list[tuple[int, int]],
        start: int,
    ) -> list[dict[str, t.Any]]:
        """Run the snippet and turn what it did into steps.

        Each step gets the note whose lines it sits on, counted the way
        the reader sees them numbered. Nothing is run unless the site
        set `kaamiki.conf.code_explain.run`, and the build stops
        without it.

        :param code: The snippet.
        :param setup: Code to run first, untraced.
        :param stdin: What `input()` reads.
        :param notes: The `lines` blocks.
        :param ranges: The lines each note covers.
        :param start: The number the snippet's first line is given.
        :return: The steps, in the order they ran.
        """
        env = self.state.document.settings.env
        config = env.config
        if not setting(config, "code_explain_run"):
            raise self.error(
                f"{self.name}: expected kaamiki.conf.code_explain.run = True to"
                " run python, got it off; set it in conf.py if you trust every"
                " page this site builds"
            )
        for block, (low, high) in zip(notes, ranges, strict=True):
            if block.options:
                raise self.error(
                    f"{self.name}: expected no :values: in a python"
                    f" walkthrough, got them in the note for {label(low, high)}"
                )
        events = frozenset(
            listed(
                self.options.get("events")
                or setting(config, "code_explain_events")
            )
        )
        unknown = events - set(TRACE_EVENTS)
        if unknown:
            raise self.error(
                f"{self.name}: :events: expected {', '.join(TRACE_EVENTS)},"
                f" got {', '.join(sorted(unknown))}"
            )
        watch = list(dict.fromkeys(listed(self.options.get("watch", ""))))
        here = p.dirname(str(self.state.document.current_source))
        paths = [
            _ if p.isabs(_) else p.abspath(p.join(env.srcdir, _))
            for _ in setting(config, "code_explain_pythonpath")
        ]
        paths += [
            _ if p.isabs(_) else p.abspath(p.join(here, _))
            for _ in listed(self.options.get("pythonpath", ""))
        ]
        for path in paths:
            if not p.isdir(path):
                raise self.error(
                    f"{self.name}: :pythonpath: expected a directory, got"
                    f" {path!r}"
                )
        most = self.capped("limit", "code_explain_limit")
        budget = most * setting(config, "code_explain_budget")
        traced = execute(
            code,
            setup,
            stdin,
            watch,
            budget,
            self.capped("timeout", "code_explain_timeout"),
            paths,
            comprehensions="comprehensions" in self.options
            or bool(setting(config, "code_explain_comprehensions")),
            python=setting(config, "code_explain_python"),
            cache=self.cache(),
            memory_limit=setting(config, "code_explain_memory") << 20,
            output_limit=setting(config, "code_explain_output_limit") << 20,
        )
        for dependency in traced["deps"]:
            env.note_dependency(dependency)
        error = traced["error"]
        if error is not None and error.get("line") is None:
            raise self.error(
                f"{self.name}: expected a snippet that runs, got"
                f" {error['text']}"
            )
        steps = [
            _
            for _ in replay(traced, events or DEFAULT_EVENTS)
            if _["line"] >= 1
        ]
        for step in steps:
            line = step["line"] + start - 1
            step["note"] = next(
                (
                    index
                    for index, (low, high) in enumerate(ranges)
                    if low <= line <= high
                ),
                None,
            )
        steps = collapse(steps)
        if not steps:
            raise self.error(
                f"{self.name}: expected at least 1 step, got none; a snippet"
                " of comments and blank lines runs nothing"
            )
        if traced["truncated"]:
            raise self.error(
                f"{self.name}: expected a snippet of at most {budget} steps,"
                " got more, so it is long or never ends; trim it or raise"
                " kaamiki.conf.code_explain.budget"
            )
        if len(steps) > most:
            raise self.error(
                f"{self.name}: :limit: expected at least {len(steps)} for this"
                f" snippet, got {most}; trim it or raise :limit:"
            )
        self.check(traced, watch, ranges, steps)
        inherit(steps)
        return steps

    def recite(
        self,
        setup: str,
        stdin: str,
        notes: list[chunk],
        ranges: list[tuple[int, int]],
        start: int,
        total: int,
    ) -> list[dict[str, t.Any]]:
        """Make a step of every note, for a snippet that isn't run.

        :param setup: The `setup` block, which can't run here.
        :param stdin: The `stdin` block, which has nothing to read it.
        :param notes: The `lines` blocks.
        :param ranges: The lines each note covers.
        :param start: The number the snippet's first line is given.
        :param total: How many lines the snippet has.
        :return: One step per note, in the order written.
        """
        unused = [f":{_}:" for _ in TRACED if _ in self.options]
        unused += [
            f"`.. {_}::`"
            for _, text in (("setup", setup), ("stdin", stdin))
            if text
        ]
        if unused:
            raise self.error(
                f"{self.name}: {', '.join(unused)} expected a python"
                " code-explain, got another language"
            )
        values: dict[str, tuple[int, str]] = {}
        steps: list[dict[str, t.Any]] = []
        for index, (block, (low, high)) in enumerate(
            zip(notes, ranges, strict=True)
        ):
            where = self.place(block, high, start, total)
            for key in listed(block.options.get("clear", "")):
                if values.pop(key, None) is None:
                    raise self.error(
                        f"{self.name}: expected the note for"
                        f" {label(low, high)} to clear a value that shows, got"
                        f" {key}"
                    )
            fresh: set[str] = set()
            for entry in ENTRIES.split(block.options.get("values", "")):
                match = VALUE.match(entry)
                if match is None:
                    if entry.strip():
                        raise self.error(
                            f"{self.name}: :values: of the note for"
                            f" {label(low, high)} expected `name: value`, got"
                            f" {entry!r}"
                        )
                    continue
                values[match.group(1)] = (where, match.group(2))
                fresh.add(match.group(1))
            out = block.options.get("output", "").replace("\\n", "\n")
            steps.append(
                {
                    "line": low - start + 1,
                    "end": high - start + 1,
                    "frame": 0,
                    "note": index,
                    "vars": [
                        [key, place, *show(text), key in fresh]
                        for key, (place, text) in values.items()
                    ],
                    "out": f"{out}\n" if out else "",
                    "ret": None,
                    "error": None,
                }
            )
        return steps

    def place(self, block: chunk, high: int, start: int, total: int) -> int:
        """Find the line a note's values are written beside.

        :param block: The `lines` block.
        :param high: The last line it covers.
        :param start: The number the snippet's first line is given.
        :param total: How many lines the snippet has.
        :return: The line, counted from the snippet's first.
        """
        at = block.options.get("at")
        if at is None:
            return high - start + 1
        try:
            line = checks.integer(start, start + total - 1)(at)
        except ValueError as exc:
            raise self.error(f"{self.name}: :at: {exc}") from exc
        return line - start + 1

    def marker(
        self, language: str, steps: list[dict[str, t.Any]]
    ) -> dict[str, str]:
        """Work out how the values are written as a comment.

        :param language: The language named on the directive.
        :param steps: The steps, to see whether any value is shown.
        :return: What opens the comment and what closes it.
        """
        given = self.options.get("comment", "").split()
        if given:
            return {"open": given[0], "close": " ".join(given[1:])}
        known = comment(language)
        if known is not None:
            return known
        if any(_.get("vars") for _ in steps):
            raise self.error(
                f"{self.name}: expected a comment mark for {language}, got"
                " none; set :comment: so the values read as one"
            )
        return {"open": "#", "close": ""}

    def caption(self, language: str) -> heading:
        """Build the header, with the caption parsed as rST and the
        icon of the snippet's language.

        The caption keeps its place in the source, so `gettext` can
        collect it.

        :param language: The language named on the directive.
        :return: The header node.
        """
        head = heading(icon="")
        if not self.options.get("caption"):
            return head
        parsed = self.parse_text_to_nodes(
            self.options["caption"], offset=self.content_offset
        )
        if not parsed or not isinstance(parsed[0], nodes.Element):
            return head
        source, line = self.get_source_info()
        for child in findall(parsed[0], nodes.Element):
            child.source = source
            child.line = line
        head.rawsource = self.options["caption"]
        head.source, head.line = source, line
        head.extend(parsed[0].children)
        config = self.state.document.settings.env.config
        head["icon"] = caption_icon(head, language, icons=Icons.of(config))
        return head

    def snippet(self, code: str, language: str, start: int) -> plain_code:
        """Write the snippet out as a plain code block.

        :param code: The snippet.
        :param language: The language to highlight it in.
        :param start: The number the snippet's first line is given.
        :return: The code block.
        """
        block = plain_code(code, code)
        block["language"] = language
        block["linenos"] = "linenos" in self.options
        block["highlight_args"] = {"linenostart": start}
        self.set_source_info(block)
        return block

    def explain(self, notes: list[chunk]) -> explanations:
        """Parse every `lines` block into the note it stands for.

        :param notes: The `lines` blocks, in the order they were
            written.
        :return: The notes, gathered under one container.
        """
        box = explanations()
        for index, block in enumerate(notes):
            note = explanation(index=index)
            self.state.nested_parse(block.body, block.offset, note)
            box += note
        return box

    def check(
        self,
        traced: Trace,
        watch: list[str],
        ranges: list[tuple[int, int]],
        steps: list[dict[str, t.Any]],
    ) -> None:
        """Stop for whatever the author probably didn't mean.

        :param traced: What the tracer saw.
        :param watch: The names asked for.
        :param ranges: The lines each note covers.
        :param steps: The steps, with their notes.
        """
        error = traced["error"]
        raises = "raises" in self.options
        if error is not None and not raises:
            raise self.error(
                f"{self.name}: expected a snippet that runs to the end, got"
                f" {error['text']}; add :raises: if that is meant"
            )
        if error is None and raises:
            raise self.error(
                f"{self.name}: :raises: expected a snippet that raises, got a"
                " run to the end"
            )
        unseen = ", ".join(_ for _ in watch if _ not in traced["seen"])
        if unseen:
            raise self.error(
                f"{self.name}: :watch: expected names the snippet sets, got"
                f" {unseen}"
            )
        shown = {_["note"] for _ in steps}
        for index, (low, high) in enumerate(ranges):
            if index not in shown:
                raise self.error(
                    f"{self.name}: expected a note that comes up, got the one"
                    f" for {label(low, high)}"
                )

    def emphasis(self, start: int, total: int) -> set[int]:
        """Read `:emphasize-lines:` as the lines it names.

        :param start: The number the snippet's first line is given.
        :param total: How many lines the snippet has.
        :return: The lines to mark.
        """
        end = start + total - 1
        marked: set[int] = set()
        for part in listed(self.options.get("emphasize-lines", "")):
            found = linerange(part)
            if found is None:
                raise self.error(
                    f"{self.name}: :emphasize-lines: expected ranges, got "
                    f"{part!r}"
                )
            low, high = found
            if low > high:
                raise self.error(
                    f"{self.name}: :emphasize-lines: expected ranges that run"
                    f" up, got {part!r}"
                )
            if low < start or high > end:
                raise self.error(
                    f"{self.name}: :emphasize-lines: expected lines within"
                    f" {label(start, end)}, got {part!r}"
                )
            marked.update(range(max(low, start), min(high, end) + 1))
        return marked


def inherit(steps: list[dict[str, t.Any]]) -> None:
    """Give a step no note covers the note before it.

    The steps that come before the first note take that one, since
    there's none before them.
    """
    last = next((_["note"] for _ in steps if _["note"] is not None), None)
    for step in steps:
        if step["note"] is None:
            step["note"] = last
        else:
            last = step["note"]


def compact(step: dict[str, t.Any]) -> dict[str, t.Any]:
    """Write a step the way the page reads it, leaving out the empties.

    :param step: The step as replayed.
    :return: The step as the script expects it.
    """
    out: dict[str, t.Any] = {"line": step["line"]}
    if step.get("end", step["line"]) != step["line"]:
        out["end"] = step["end"]
    if step["note"] is not None:
        out["note"] = step["note"]
    if step["vars"]:
        out["vars"] = [
            [name, where, full, short, int(fresh)]
            for name, where, full, short, fresh in step["vars"]
        ]
    for key in ("out", "ret", "error"):
        if step[key]:
            out[key] = step[key]
    return out


def pace(language: str) -> int:
    """Pick how much scrolling a step takes, for a language.

    :param language: The language named on the directive.
    :return: The scrolling, in pixels. Python gets `PACE` and anything
        not in `PACES` gets 112.
    """
    if language.lower() in PYTHON:
        return PACE
    names = {language.lower(), *lexer_for(language).aliases}
    for pixels, languages in PACES:
        if names & languages:
            return pixels
    return 112


def visit(self: HTMLTranslator, node: CodeExplain) -> None:
    """Open the walkthrough, write its steps and open the pane.

    :param self: The HTML translator, whose body this appends to.
    :param node: The `code-explain` node and its attributes.
    """
    ids: list[str] = node["ids"]
    classes = " ".join(
        [
            "km-code-explain",
            f"km-code-explain--code-position-{node['position']}",
            *node.get("classes", []),
        ]
    )
    anchor = f' id="{self.attval(ids[0])}"' if ids else ""
    self.body.append(f'<div{anchor} class="{classes}" data-km-code-explain>')
    self.body.extend(f'<span id="{self.attval(_)}"></span>' for _ in ids[1:])
    self.body.append(
        '<script type="application/json" data-km-payload>'
        + json.dumps(node["payload"]).replace("<", "\\u003c")
        + "</script>"
    )
    self.body.append("<div data-km-pane>")


def depart(self: HTMLTranslator, node: CodeExplain) -> None:
    """Close the pane and the walkthrough.

    :param self: The HTML translator, whose body this appends to.
    :param node: The `code-explain` node (unused).
    """
    del node
    self.body.append("</div></div>")


def visit_heading(self: HTMLTranslator, node: heading) -> None:
    """Open the code's side, its frame and the caption, icon first.

    :param self: The HTML translator, whose body this appends to.
    :param node: The header node, empty when there's no caption.
    """
    self.body.append('<div class="km-code-explain__grid">')
    self.body.append('<div class="km-code-explain__side">')
    self.body.append('<div class="km-code-explain__frame" data-km-frame>')
    if node.children:
        self.body.append(
            '<div class="code-block-caption km-code-explain__caption">'
            '<span class="caption-text">'
        )
        if node["icon"]:
            self.body.append(
                f'<span class="km-lang-icon {node["icon"]}"'
                ' aria-hidden="true"></span>'
            )


def depart_heading(self: HTMLTranslator, node: heading) -> None:
    """Close the caption, then write the snippet and close the code's
    side.

    :param self: The HTML translator, whose body this appends to.
    :param node: The header node.
    """
    icons = self.builder.config.html_context["km_fa_icons"]
    if node.children:
        self.body.append("</span>")
        self.body.append(controls(icons))
        self.body.append("</div>")
    else:
        self.body.append(
            f'<div class="km-code-explain__corner">{controls(icons)}</div>'
        )
    self.body.append(node.parent["pane"])
    self.body.append(output())
    self.body.append("</div></div>")


def visit_explanations(self: HTMLTranslator, node: explanations) -> None:
    """Open the notes beside the code.

    :param self: The HTML translator, whose body this appends to.
    :param node: The container node (unused).
    """
    del node
    self.body.append('<div class="km-code-explain__notes" data-km-notes>')
    self.body.append('<div class="km-code-explain__track" data-km-track>')


def depart_explanations(self: HTMLTranslator, node: explanations) -> None:
    """Close the notes and the row they share with the code.

    :param self: The HTML translator, whose body this appends to.
    :param node: The container node (unused).
    """
    del node
    self.body.append("</div></div></div>")


def register(app: Sphinx) -> None:
    """Register the nodes only a walkthrough has.

    :param app: The Sphinx application instance.
    """
    app.add_node(heading, html=(visit_heading, depart_heading))
    app.add_node(plain_code, html=(skip, None))
    app.add_node(explanations, html=(visit_explanations, depart_explanations))
    app.add_node(explanation, html=(visit_explanation, close))


def html_page_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Load the explainer script only on the pages that use it.

    A page without a walkthrough or attempts has nothing for it to
    start. Only Kaamiki's own script is left out, whatever else a site
    loads with a name that ends the same way.

    :param app: The Sphinx application instance.
    :param pagename: The page being rendered.
    :param templatename: The template rendering it.
    :param context: The page's rendering context, updated in place.
    :param doctree: The resolved doctree or `None` for generated
        pages.
    """
    del app, pagename, templatename
    if "script_files" not in context:
        return
    if doctree is not None and next(findall(doctree, CodeExplain), None):
        return
    context["script_files"] = [
        _
        for _ in context["script_files"]
        if str(getattr(_, "filename", _)) != f"_static/{SCRIPT}"
    ]


node = CodeExplain
