"""\
Code Explain Directive
======================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 12 September 2026
Last updated on: 15 November 2026

A `code-explain` directive that walks a reader through a snippet, one
line at a time, with the values that it held at each line::

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

The notes scroll past the code, not below it, so a walkthrough needs a
minimum of one `.. lines::` block. It does not take in or move the
content around it. Put it on the page itself. A plain `container` or
an `only` is part of the page. The content of a different directive
and the notes of a different walkthrough are not. A `lines` block
takes a range of lines as its argument, as `4-6`. Each block shows a
note, in the sequence written.

.. note::

    Python runs only when `kaamiki.conf.code_explain.run` is `True` in
    `conf.py`, and then it runs for each page of the site. Without it,
    a Python walkthrough stops the build. It needs a POSIX system,
    Linux or macOS. The Python runs in a temporary directory with a
    small environment, 1GB of memory for all its processes together,
    10 seconds, and 64MB for each file that it writes or prints.

    The system holds each process to the memory where it takes the
    limit, and the build also measures the resident size and stops a
    run that uses more. At the end, the directory goes, and so does
    each process that the snippet left, also the children that left
    their parent on Linux. These are limits and not a sandbox.

    The snippet runs as the user of the build, so it can read what
    that user can read, also the environment of the build (on Linux
    through `/proc`). It can also write to other places and connect
    to the network. Build only pages that you trust, and keep secrets
    out of a build that runs them.

    A site sets the limits and the interpreter through
    `kaamiki.conf.code_explain` in `conf.py`. The `:limit:` and the
    `:timeout:` of a snippet can be lower than those of the site, but
    not higher. A trace is kept next to the doctrees, and it is used
    again while the snippet, its options, the interpreter, the
    installed packages and the files that it imported do not change.

The caption node is `Heading`, because docutils has a `caption` node
already and finds visitors by the name of the class.
"""

from __future__ import annotations

import json
import os.path as p
import re
import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.code.chrome import comment
from kaamiki.extensions.code.chrome import controls
from kaamiki.extensions.code.chrome import known
from kaamiki.extensions.code.chrome import label
from kaamiki.extensions.code.chrome import lexer_for
from kaamiki.extensions.code.chrome import notes_pane
from kaamiki.extensions.code.chrome import output
from kaamiki.extensions.code.chrome import visit_explanation
from kaamiki.extensions.code.grammar import OptionError
from kaamiki.extensions.code.grammar import StrayError
from kaamiki.extensions.code.grammar import linerange
from kaamiki.extensions.code.grammar import split
from kaamiki.extensions.code.tracer import collapse
from kaamiki.extensions.code.tracer import execute
from kaamiki.extensions.code.tracer import replay
from kaamiki.extensions.code.tracer import show
from kaamiki.extensions.utils import BEM
from kaamiki.extensions.utils import Kaamiki
from kaamiki.extensions.utils import KaamikiDirective
from kaamiki.extensions.utils import Option
from kaamiki.extensions.utils import annotated
from kaamiki.extensions.utils import caption_icon
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import findall
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import listed
from kaamiki.extensions.utils import moving
from kaamiki.extensions.utils import on
from kaamiki.extensions.utils import values
from kaamiki.extensions.utils.icons import Icons
from kaamiki.extensions.utils.settings import BOUNDS
from kaamiki.extensions.utils.settings import TRACE_EVENTS
from kaamiki.extensions.utils.settings import option as conf_path

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

    from kaamiki.extensions.code.grammar import chunk
    from kaamiki.extensions.code.tracer import Trace

code_explain: t.Final[BEM] = BEM("code-explain")
lang_icon: t.Final[BEM] = BEM("lang-icon")
CODE_POSITIONS: t.Final[tuple[str, str]] = ("right", "left")
NAME: t.Final[re.Pattern[str]] = re.compile(
    r"[A-Za-z_][\w]*(?:\.[A-Za-z_]\w*|\[[\w'\"-]+\])*"
)
BLOCKS: t.Final[frozenset[str]] = frozenset(
    {"code", "setup", "stdin", "lines"}
)
OPTIONS: t.Final[dict[str, frozenset[str]]] = {
    "lines": frozenset({"at", "clear", "output", "values"}),
}
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
VALUE: t.Final[re.Pattern[str]] = re.compile(
    r"^\s*([^=:]+?)\s*[:=]\s*(.*?)\s*$"
)
ENTRIES: t.Final[re.Pattern[str]] = re.compile(
    r"\n|;\s*(?=[A-Za-z_][\w.\[\]]*\s*[:=](?!=))"
)
PACE: t.Final[int] = 72
PACES: t.Final[tuple[tuple[int, frozenset[str]], ...]] = (
    (104, frozenset({"bash"})),
    (120, frozenset({"c"})),
    (128, frozenset({"c++", "rust"})),
)


class Heading(nodes.paragraph):
    """The caption, parsed as rST, and the icon of the language."""


class PlainCode(nodes.literal_block):
    """The snippet as a plain code block, which the visitors read."""


class Explanations(nodes.container):
    """The notes next to the snippet, which scroll past it."""


class Explanation(nodes.container):
    """The note of one `lines` block."""


def names(argument: str | None) -> str:
    """Check the names that a walkthrough watches.

    :param argument: The names as written, with commas.
    :return: The names.
    :raises ValueError: For a name that is not a Python name, a dotted
        name or an index.
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


class CodeWalk(KaamikiDirective, abstract=True):
    """The base of the `code-explain` and `code-version` directives."""

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    code_position = Option(checks.word(*CODE_POSITIONS), default="right")
    pace = Option(checks.integer(*map(int, BOUNDS["pace"])))
    caption = Option(checks.text)
    linenos = Option(rst.directives.flag)
    lineno_start = Option(
        checks.integer(*map(int, BOUNDS["code_explain_lineno"])), default=1
    )
    no_motion = Option(rst.directives.flag)

    def captioned(self, language: str) -> Heading:
        """Make the header, with the caption parsed as rST.

        :param language: The language named on the directive.
        :return: The header node.
        """
        head = Heading(icon="")
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
        head["icon"] = caption_icon(
            head, language, icons=Icons.of(self.config)
        )
        return head

    def snippet(self, code: str, language: str, start: int) -> PlainCode:
        """Write the snippet as a plain code block.

        :param code: The snippet.
        :param language: The language of the highlight.
        :param start: The number of the first line of the snippet.
        :return: The code block.
        """
        block = PlainCode(code, code)
        block["language"] = language
        block["linenos"] = "linenos" in self.options
        block["highlight_args"] = {"linenostart": start}
        self.set_source_info(block)
        return block


class CodeExplain(CodeWalk, name="code-explain"):
    """The `code-explain` directive.

    Options::

        - `code-position`: The side of the code, `right` or `left`.
          The default is `right`.
        - `watch`: The names to show, with a comma between each.
          Without it, only the return value of a function and the
          exception of the snippet show.
        - `limit`: How many steps to show, from 1 to 300. It cannot
          be more than `kaamiki.conf.code_explain.limit`, which is
          100 by default.
        - `timeout`: How long the snippet can run, in seconds, from
          1 to 60. It cannot be more than
          `kaamiki.conf.code_explain.timeout`.
        - `pythonpath`: The directories to import from, with a comma
          between each, relative to the document. The build stops
          when a directory is not there.
        - `events`: Which of `call`, `line` and `return` make a
          step. The default is `kaamiki.conf.code_explain.events`,
          which is `line` and `return` by default.
        - `comprehensions`: Also go into comprehensions. A site can
          do this for all snippets with
          `kaamiki.conf.code_explain.comprehensions`.
        - `pace`: The pixels of scrolling for each step, from 24 to
          240. The default comes from `pace` for the language.
        - `raises`: The snippet must fail, so it ends on the
          exception. Without it, the build stops when the snippet
          raises. With it, the build stops when the snippet runs to
          the end.
        - `comment`: How the language opens a comment, and closes it
          if necessary (`(* *)`), for a language that Kaamiki does
          not know.
        - `caption`: A line of text above the code, parsed as rST.
        - `linenos`: Show the line numbers.
        - `lineno-start`: The number of the first line, from 0 to
          10000.
        - `emphasize-lines`: The lines to highlight, as `1, 3-5`.
        - `no-motion`: Show it stacked, without motion.
        - `name`: A name for links to the `code-explain`.
        - `class`: More classes for the `code-explain`.

    Options of a `lines` block::

        - `at`: The line in the snippet where the values of the note
          show. The default is the last line of the range.
        - `clear`: The names to stop showing from this note, with a
          comma between each. Each name must show already.
        - `output`: What the note prints, below the code. A
          backslash and an n start a new line.
        - `values`: The values to show from this note, as
          `name: value`, one on each line or with semicolons between
          them. A name that you write again takes the new value.
    """

    watch = Option(names)
    limit = Option(checks.integer(*map(int, BOUNDS["code_explain_limit"])))
    timeout = Option(checks.integer(*map(int, BOUNDS["code_explain_timeout"])))
    pythonpath = Option(checks.text)
    events = Option(checks.text)
    comprehensions = Option(rst.directives.flag)
    raises = Option(rst.directives.flag)
    comment = Option(comment_marks)
    emphasize_lines = Option(checks.text)

    class Node(annotated):
        """The walkthrough, a container for each builder."""

    def build(self) -> list[nodes.Node]:
        """Step through the snippet and make the walkthrough.

        :return: A list holding the one `code-explain` node.
        """
        language = self.arguments.pop().strip() if self.arguments else "python"
        if not known(language):
            self.fail(f"expected a language Pygments knows, got {language!r}")
        code, setup, stdin, notes = self.blocks()
        if not notes:
            self.fail("expected a `.. lines::` block per note, got none")
        start = self.lineno_start
        total = len(code.splitlines())
        ranges = [self.span(_.argument, start, total) for _ in notes]
        traced = language.lower() in PYTHON
        if traced:
            steps = self.trace(code, setup, stdin, notes, ranges, start)
        else:
            steps = self.recite(setup, stdin, notes, ranges, start, total)
        attributes: dict[str, t.Any] = {}
        attributes["classes"] = [
            *self.options.get("class", []),
            *moving(self.options, timed=False),
        ]
        attributes["position"] = self.code_position
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
        element = self.locate(self.Node("", **attributes))
        element += self.captioned(language)
        element += self.snippet(code, language, start)
        element += self.explain(notes)
        self.add_name(element)
        return [element]

    def cache(self) -> str | None:
        """Name the folder that keeps the traces.

        :return: The folder, or `None` when the site set the cache off.
            It is next to the doctrees, so a new build with `-E` and
            `-a` keeps it, and a deleted build removes it.
        """
        env = self.env
        if not values(env.config).code_explain.cache:
            return None
        return p.join(str(env.doctreedir), "kaamiki-code-explain")

    def capped(self, option: str, key: str) -> int:
        """Read a number from the snippet, to the limit of the site.

        :param option: The option of the directive.
        :param key: The setting with the maximum.
        :return: The number from the snippet, or the maximum.
        :raises rst.DirectiveError: When it is more than the site
            permits.
        """
        most = values(self.config)[key]
        asked = self.options.get(option, most)
        if asked > most:
            self.fail(
                f":{option}: expected at most {most} as"
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
        except OptionError as exc:
            takes = ", ".join(f":{_}:" for _ in sorted(OPTIONS[exc.block]))
            self.fail(
                f"`.. {exc.block}::` on line {exc.line} expected"
                f" one of {takes}, each once, got :{exc.key}:"
            )
        except StrayError as exc:
            self.fail(
                "expected text inside a `.. code::`,"
                " `.. setup::`, `.. stdin::` or `.. lines::`, got"
                f" {exc.text!r} on line {exc.line}"
            )
        for block in ("code", "setup", "stdin"):
            if sum(_.name == block for _ in found) > 1:
                self.fail(
                    f"expected one `.. {block}::` block, got more than one"
                )
        code = next((_ for _ in found if _.name == "code"), None)
        if code is None:
            self.fail("expected one `.. code::` block, got none")
        if not code.text().strip():
            self.fail("expected some code in the `.. code::`, got none")
        setup = next((_.text() for _ in found if _.name == "setup"), "")
        stdin = next((_.text() for _ in found if _.name == "stdin"), "")
        notes = [_ for _ in found if _.name == "lines"]
        return code.text(), setup, stdin, notes

    def span(self, argument: str, start: int, total: int) -> tuple[int, int]:
        """Read the lines that a `lines` block explains.

        :param argument: The argument of the block, as written.
        :param start: The number of the first line of the snippet.
        :param total: The number of lines of the snippet.
        :return: The first and the last line that it covers.
        """
        found = linerange(argument)
        if found is None:
            self.fail(f":lines: expected a line range, got {argument!r}")
        low, high = found
        if low > high:
            self.fail(
                f":lines: expected a range that runs up, got {argument!r}"
            )
        if low < start or high > start + total - 1:
            self.fail(
                f":lines: expected a range within"
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
        """Run the snippet and change what it did into steps.

        :param code: The snippet.
        :param setup: The code to run first, without a trace.
        :param stdin: What `input()` reads.
        :param notes: The `lines` blocks.
        :param ranges: The lines that each note covers.
        :param start: The number of the first line of the snippet.
        :return: The steps, in the sequence that they ran. Each step
            gets the note of its line, with the numbers that the reader
            sees.
        :raises rst.DirectiveError: When
            `kaamiki.conf.code_explain.run` is off, because then
            nothing runs.
        """
        env = self.env
        config = env.config
        if not values(config).code_explain.run:
            self.fail(
                "expected kaamiki.conf.code_explain.run = True to"
                " run python, got it off; set it in conf.py if you trust every"
                " page this site builds"
            )
        for block, (low, high) in zip(notes, ranges, strict=True):
            if block.options:
                given = ", ".join(f":{_}:" for _ in sorted(block.options))
                self.fail(
                    f"expected no {given} in a python"
                    f" walkthrough, got them in the note for"
                    f" {label(low, high)}"
                )
        events = frozenset(
            listed(
                self.options.get("events")
                or values(config).code_explain.events
            )
        )
        unknown = events - set(TRACE_EVENTS)
        if unknown or not events:
            self.fail(
                f":events: expected {', '.join(TRACE_EVENTS)},"
                f" got {', '.join(sorted(unknown)) or 'none'}"
            )
        watch = list(dict.fromkeys(listed(self.options.get("watch", ""))))
        here = p.dirname(str(self.state.document.current_source))
        paths = [
            _ if p.isabs(_) else p.abspath(p.join(env.srcdir, _))
            for _ in values(config).code_explain.pythonpath
        ]
        paths += [
            _ if p.isabs(_) else p.abspath(p.join(here, _))
            for _ in listed(self.options.get("pythonpath", ""))
        ]
        for path in paths:
            if not p.isdir(path):
                self.fail(f":pythonpath: expected a directory, got {path!r}")
        most = self.capped("limit", "code_explain_limit")
        budget = most * values(config).code_explain.budget
        traced = execute(
            code,
            setup,
            stdin,
            watch,
            budget,
            self.capped("timeout", "code_explain_timeout"),
            paths,
            comprehensions="comprehensions" in self.options
            or values(config).code_explain.comprehensions,
            python=values(config).code_explain.python,
            cache=self.cache(),
            memory_limit=values(config).code_explain.memory << 20,
            output_limit=values(config).code_explain.output_limit << 20,
        )
        for dependency in traced["deps"]:
            env.note_dependency(dependency)
        error = traced["error"]
        if error is not None and error.get("line") is None:
            self.fail(f"expected a snippet that runs, got {error['text']}")
        steps = [_ for _ in replay(traced, events) if _["line"] >= 1]
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
            self.fail(
                "expected at least 1 step, got none; a snippet"
                " of comments and blank lines runs nothing"
            )
        if traced["truncated"]:
            self.fail(
                f"expected a snippet of at most {budget} steps,"
                " got more, so it's long or never ends; trim it or raise"
                " kaamiki.conf.code_explain.budget"
            )
        if len(steps) > most:
            self.fail(
                f":limit: expected at least {len(steps)} for this"
                f" snippet, got {most}; trim it or raise :limit:"
            )
        self.verify(traced, watch, ranges, steps)
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
        """Make a step of each note, for a snippet that does not run.

        :param setup: The `setup` block, which cannot run here.
        :param stdin: The `stdin` block, which nothing reads here.
        :param notes: The `lines` blocks.
        :param ranges: The lines that each note covers.
        :param start: The number of the first line of the snippet.
        :param total: The number of lines of the snippet.
        :return: One step for each note, in the sequence written.
        """
        unused = [f":{_}:" for _ in TRACED if _ in self.options]
        unused += [
            f"`.. {_}::`"
            for _, text in (("setup", setup), ("stdin", stdin))
            if text
        ]
        if unused:
            self.fail(
                f"{', '.join(unused)} expected a python"
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
                    self.fail(
                        f"expected the note for"
                        f" {label(low, high)} to clear a value that shows, got"
                        f" {key}"
                    )
            fresh: set[str] = set()
            for entry in ENTRIES.split(block.options.get("values", "")):
                match = VALUE.match(entry)
                if match is None:
                    if entry.strip():
                        self.fail(
                            f":values: of the note for"
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
        """Find the line where the values of a note show.

        :param block: The `lines` block.
        :param high: The last line that it covers.
        :param start: The number of the first line of the snippet.
        :param total: The number of lines of the snippet.
        :return: The line, counted from the first line of the snippet.
        """
        at = block.options.get("at")
        if at is None:
            return high - start + 1
        try:
            line = checks.integer(start, start + total - 1)(at)
        except ValueError as exc:
            self.fail(f":at: {exc}")
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
            self.fail(
                f"expected a comment mark for {language}, got"
                " none; set :comment: so the values read as one"
            )
        return {"open": "#", "close": ""}

    def explain(self, notes: list[chunk]) -> Explanations:
        """Parse every `lines` block into the note it stands for.

        :param notes: The `lines` blocks, in the order they were
            written.
        :return: The notes, gathered under one container.
        """
        box = Explanations()
        for index, block in enumerate(notes):
            note = Explanation(index=index)
            self.state.nested_parse(block.body, block.offset, note)
            box += note
        return box

    def verify(
        self,
        traced: Trace,
        watch: list[str],
        ranges: list[tuple[int, int]],
        steps: list[dict[str, t.Any]],
    ) -> None:
        """Stop for a result that the author probably did not want.

        :param traced: What the tracer recorded.
        :param watch: The names to watch.
        :param ranges: The lines that each note covers.
        :param steps: The steps, with their notes.
        :raises rst.DirectiveError: For an error without `:raises:`,
            `:raises:` without an error, a watched name that the
            snippet does not set, or a note that no step shows.
        """
        error = traced["error"]
        raises = "raises" in self.options
        if error is not None and not raises:
            self.fail(
                f"expected a snippet that runs to the end, got"
                f" {error['text']}; add :raises: if that's meant"
            )
        if error is None and raises:
            self.fail(
                ":raises: expected a snippet that raises, got a run to the end"
            )
        unseen = ", ".join(_ for _ in watch if _ not in traced["seen"])
        if unseen:
            self.fail(f":watch: expected names the snippet sets, got {unseen}")
        shown = {_["note"] for _ in steps}
        for index, (low, high) in enumerate(ranges):
            if index not in shown:
                self.fail(
                    f"expected a note that comes up, got the one"
                    f" for {label(low, high)}"
                )

    def emphasis(self, start: int, total: int) -> set[int]:
        """Read the lines that `:emphasize-lines:` names.

        :param start: The number of the first line of the snippet.
        :param total: The number of lines of the snippet.
        :return: The lines to mark.
        """
        end = start + total - 1
        marked: set[int] = set()
        for part in listed(self.options.get("emphasize-lines", "")):
            found = linerange(part)
            if found is None:
                self.fail(f":emphasize-lines: expected ranges, got {part!r}")
            low, high = found
            if low > high:
                self.fail(
                    f":emphasize-lines: expected ranges that run"
                    f" up, got {part!r}"
                )
            if low < start or high > end:
                self.fail(
                    f":emphasize-lines: expected lines within"
                    f" {label(start, end)}, got {part!r}"
                )
            marked.update(range(max(low, start), min(high, end) + 1))
        return marked


def inherit(steps: list[dict[str, t.Any]]) -> None:
    """Give a step without a note the note before it.

    :param steps: The steps, changed in place. The steps before the
        first note take the first note.
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


@html.opens(CodeExplain.Node)
def visit(self: HTMLTranslator, node: CodeExplain.Node) -> None:
    """Open the walkthrough, write its steps and open the pane.

    :param self: The HTML translator, whose body this appends to.
    :param node: The `code-explain` node and its attributes.
    """
    ids: list[str] = node["ids"]
    classes = code_explain(
        f"code-position-{node['position']}", more=node.get("classes", [])
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


html.closes(CodeExplain.Node, "</div></div>")


@html.opens(Heading)
def visit_heading(self: HTMLTranslator, node: Heading) -> None:
    """Open the code side, its frame and the caption.

    :param self: The HTML translator, whose body this appends to.
    :param node: The header node, empty when there is no caption.
    """
    self.body.append(f'<div class="{code_explain.grid()}">')
    self.body.append(f'<div class="{code_explain.side()}">')
    self.body.append(f'<div class="{code_explain.frame()}" data-km-frame>')
    if node.children:
        self.body.append(
            f'<div class="code-block-caption {code_explain.caption()}">'
            '<span class="caption-text">'
        )
        if node["icon"]:
            self.body.append(
                f'<span class="{lang_icon} {node["icon"]}"'
                ' aria-hidden="true"></span>'
            )


@html.closes(Heading)
def depart_heading(self: HTMLTranslator, node: Heading) -> None:
    """Close the caption, the snippet and the code side.

    :param self: The HTML translator, whose body this appends to.
    :param node: The header node.
    """
    icons = Kaamiki.of(self.builder).icons.roles
    if node.children:
        self.body.append("</span>")
        self.body.append(controls(icons))
        self.body.append("</div>")
    else:
        self.body.append(
            f'<div class="{code_explain.corner()}">{controls(icons)}</div>'
        )
    self.body.append(node.parent["pane"])
    self.body.append(output())
    self.body.append("</div></div>")


@html.opens(Explanations)
def visit_explanations(self: HTMLTranslator, node: Explanations) -> None:
    """Open the notes beside the code.

    :param self: The HTML translator, whose body this appends to.
    :param node: The container node (unused).
    """
    del node
    self.body.append(f'<div class="{code_explain.notes()}" data-km-notes>')
    self.body.append(f'<div class="{code_explain.track()}" data-km-track>')


html.closes(Explanations, "</div></div></div>")
html.opens(Explanation)(visit_explanation)
html.closes(Explanation, "</div>")
html.skips(PlainCode)


@on("html-page-context")
def html_page_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, t.Any],
    doctree: nodes.document | None,
) -> None:
    """Load the explainer script only on the pages that use it.

    :param app: The Sphinx application instance.
    :param pagename: The page that is written.
    :param templatename: The template that writes it.
    :param context: The context of the page, changed in place. Only the
        script of Kaamiki is removed, also when a site loads a
        different script with a similar name.
    :param doctree: The resolved doctree, or `None` for a generated
        page.
    """
    del app, pagename, templatename
    if "script_files" not in context:
        return
    if doctree is not None and next(findall(doctree, CodeExplain.Node), None):
        return
    context["script_files"] = [
        _
        for _ in context["script_files"]
        if str(getattr(_, "filename", _)) != f"_static/{SCRIPT}"
    ]
