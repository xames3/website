"""\
Walkthrough Directive
=====================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 12 September 2026
Last updated on: 12 October 2026

A `walkthrough` directive that steps a reader through a snippet, line
by line, with the values it held at each one... telling a story::

    .. walkthrough:: python
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

    The Python runs in a scratch directory with a bare environment, a
    1GB of memory, 10 seconds and the directory goes when it finishes.
    A site changes those, and what the snippet may run with, through
    the `walkthrough_*` settings in `html_context`. A snippet's
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
from sphinx.util import logging

from kaamiki.extensions.explainer.chrome import comment
from kaamiki.extensions.explainer.chrome import controls
from kaamiki.extensions.explainer.chrome import label
from kaamiki.extensions.explainer.chrome import lexer_for
from kaamiki.extensions.explainer.chrome import output
from kaamiki.extensions.explainer.chrome import pane
from kaamiki.extensions.explainer.chrome import visit_explanation
from kaamiki.extensions.explainer.grammar import linerange
from kaamiki.extensions.explainer.grammar import split
from kaamiki.extensions.explainer.tracer import budget
from kaamiki.extensions.explainer.tracer import collapse
from kaamiki.extensions.explainer.tracer import execute
from kaamiki.extensions.explainer.tracer import kinds
from kaamiki.extensions.explainer.tracer import limit
from kaamiki.extensions.explainer.tracer import memory
from kaamiki.extensions.explainer.tracer import replay
from kaamiki.extensions.explainer.tracer import show
from kaamiki.extensions.explainer.tracer import timeout
from kaamiki.extensions.explainer.tracer import written
from kaamiki.extensions.utils import badged
from kaamiki.extensions.utils import findall
from kaamiki.extensions.utils import listed
from kaamiki.extensions.utils import skip
from kaamiki.extensions.utils import toggle

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

    from kaamiki.extensions.explainer.grammar import chunk
    from kaamiki.extensions.explainer.tracer import Trace

logger = logging.getLogger(__name__)

name: t.Final[str] = "walkthrough"
POSITIONS: t.Final[tuple[str, str]] = ("right", "left")
BLOCKS: t.Final[frozenset[str]] = frozenset({"code", "setup", "stdin", "lines"})
OPTIONS: t.Final[dict[str, frozenset[str]]] = {
    "lines": frozenset({"at", "clear", "output", "values"}),
}
EVENTS: t.Final[frozenset[str]] = frozenset({"line", "return"})
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
ENTRIES: re.Pattern[str] = re.compile(r"[;\n]")
PACE: t.Final[int] = 72
PACES: t.Final[tuple[tuple[int, frozenset[str]], ...]] = (
    (104, frozenset({"bash"})),
    (112, frozenset({"javascript", "typescript"})),
    (120, frozenset({"c"})),
    (128, frozenset({"c++", "rust"})),
)


class node(nodes.container):
    """The parsed directive, waiting for `visit` to write it out.

    It's a `container` underneath, so a builder that has never heard of
    a walkthrough still has something to write.
    """


class heading(nodes.paragraph):
    """The caption, parsed as rST, the language's icon and the step
    counter.

    docutils already has a `caption` node and finds visitors by class
    name, so this can't borrow that one.
    """


class plain(nodes.literal_block):
    """The snippet as a plain code block, for every builder
    except HTML.
    """


class explanations(nodes.container):
    """The notes beside the snippet, scrolling past it."""


class explanation(nodes.container):
    """One `lines` block's note."""


def position(argument: str) -> str:
    """Check the `code-position` option against its two values.

    :param argument: The value written in the rST.
    :return: The value, once it's known to be `right` or `left`.
    """
    return rst.directives.choice(argument, POSITIONS)


class directive(CodeBlock):
    """The `walkthrough` directive.

    The notes scroll past the code instead of swapping under it, so it
    needs at least one `.. lines::` block. It stands alone, nothing
    around it is pulled in or moved.

    Options::

        - `code-position`: Which side the code holds, `right` for the
          default or `left`.
        - `watch`: Names to show, comma-separated. Without it only a
          function's return value and what the snippet raises show.
        - `limit`: How many steps to show. Defaults to 100.
        - `timeout`: How long the snippet may run, in seconds.
        - `pythonpath`: Directories to import from, comma-separated
          and relative to the document.
        - `events`: Which of `call`, `line` and `return` make a step.
          Defaults to `line` and `return`.
        - `comprehensions`: Step into comprehensions too. `false`
          leaves them out when the site's `walkthrough_comprehensions`
          is on.
        - `pace`: Pixels of scrolling a step takes. Defaults to what
          `pace` picks for the language. This is flaky...
        - `raises`: The snippet is meant to fail, so it ends on the
          exception without a warning.
        - `comment`: How the language opens a comment and closes one
          if it must (`(* *)`), for a language Kaamiki doesn't know.
    """

    option_spec = {  # noqa: RUF012
        **{
            key: value
            for key, value in CodeBlock.option_spec.items()
            if key not in {"dedent", "force"}
        },
        "code-position": position,
        "watch": rst.directives.unchanged,
        "limit": rst.directives.positive_int,
        "timeout": rst.directives.positive_int,
        "pythonpath": rst.directives.unchanged,
        "events": rst.directives.unchanged,
        "comprehensions": toggle,
        "pace": rst.directives.positive_int,
        "raises": rst.directives.flag,
        "comment": rst.directives.unchanged_required,
    }

    def run(self) -> list[nodes.Node]:
        """Step through the snippet and return the walkthrough.

        :return: A list holding the one `walkthrough` node.
        """
        language = self.arguments.pop().strip() if self.arguments else "python"
        code, setup, stdin, notes = self.blocks()
        if not notes:
            raise self.error("walkthrough needs a `.. lines::` block per note")
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
        attributes["pane"] = pane(
            code,
            language,
            start,
            self.emphasis(start, total),
            linenos="linenos" in self.options,
        )
        element = node("", **attributes)
        element += self.caption(len(steps), language)
        element += self.snippet(code, language, start)
        element += self.explain(notes)
        self.add_name(element)
        return [element]

    def setting(self, key: str, default: int) -> int:
        """Read a whole number the site sets for the walkthrough.

        :param key: The setting's name in `html_context`.
        :param default: What it is without one.
        :return: The number, above zero.
        :raises rst.DirectiveError: When the site set anything else.
        """
        site = self.state.document.settings.env.config.html_context
        value = site.get(key)
        if value is None:
            return default
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise self.error(
                f"{key} needs a whole number above zero, got {value!r}"
            )
        return value

    def cache(self) -> str | None:
        """Name the folder traces are kept in, unless the site turned
        that off.

        It sits with the doctrees, so a build that starts over with
        `-E` and `-a` keeps it and deleting the build takes it away.

        :return: The folder or `None` for no cache.
        """
        env = self.state.document.settings.env
        if not env.config.html_context.get("walkthrough_cache", True):
            return None
        return p.join(str(env.doctreedir), "kaamiki-walkthrough")

    def capped(self, option: str, key: str, default: int) -> int:
        """Read a number the snippet asks for, up to what the site
        allows.

        :param option: The directive's option.
        :param key: The setting that holds the most it may ask for.
        :param default: The most, when the site sets none.
        :return: What the snippet asked for or the most.
        """
        most = self.setting(key, default)
        asked = self.options.get(option)
        if asked is None:
            return most
        if asked > most:
            self.warn(
                f":{option}: {asked} is more than {key} allows; using {most}"
            )
            return most
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
                f"`.. {block}::` on line {line} has :{key}:, which it does"
                f" not take or takes twice; it takes {takes}"
            ) from exc
        except ValueError as exc:
            line, text = exc.args
            raise self.error(
                f"walkthrough has {text!r} on line {line}, outside any"
                " `.. code::`, `.. setup::`, `.. stdin::` or `.. lines::`"
            ) from exc
        for block in ("code", "setup", "stdin"):
            if sum(_.name == block for _ in found) > 1:
                raise self.error(f"walkthrough takes one `.. {block}::` block")
        code = next((_ for _ in found if _.name == "code"), None)
        if code is None:
            raise self.error("walkthrough requires a `.. code::` block")
        if not code.text().strip():
            raise self.error("walkthrough has no code in its `.. code::`")
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
            raise self.error(f"lines needs a line range, got {argument!r}")
        low, high = found
        if low < start or high > start + total - 1:
            self.warn(
                f"{label(low, high)} is outside the snippet, which is"
                f" {label(start, start + total - 1)}"
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
        the reader sees them numbered.

        :param code: The snippet.
        :param setup: Code to run first, untraced.
        :param stdin: What `input()` reads.
        :param notes: The `lines` blocks.
        :param ranges: The lines each note covers.
        :param start: The number the snippet's first line is given.
        :return: The steps, in the order they ran.
        """
        for block, (low, high) in zip(notes, ranges, strict=True):
            if block.options:
                self.warn(
                    f"the note for {label(low, high)} writes out values,"
                    " but a python walkthrough reads them off the snippet"
                )
        env = self.state.document.settings.env
        site = env.config.html_context
        events = frozenset(
            listed(self.options.get("events") or site.get("walkthrough_events"))
        )
        if events - kinds:
            raise self.error(
                f"events takes {', '.join(sorted(kinds))},"
                f" got {', '.join(sorted(events - kinds))}"
            )
        watch = list(dict.fromkeys(listed(self.options.get("watch", ""))))
        here = p.dirname(str(self.state.document.current_source))
        paths = [
            _ if p.isabs(_) else p.abspath(p.join(env.srcdir, _))
            for _ in listed(site.get("walkthrough_pythonpath"))
        ]
        paths += [
            _ if p.isabs(_) else p.abspath(p.join(here, _))
            for _ in listed(self.options.get("pythonpath", ""))
        ]
        most = self.capped("limit", "walkthrough_limit", limit)
        traced = execute(
            code,
            setup,
            stdin,
            watch,
            most * self.setting("walkthrough_budget", budget),
            self.capped("timeout", "walkthrough_timeout", timeout),
            paths,
            comprehensions=self.options.get(
                "comprehensions", bool(site.get("walkthrough_comprehensions"))
            ),
            python=site.get("walkthrough_python") or None,
            cache=self.cache(),
            memory_limit=self.setting("walkthrough_memory", memory) << 20,
            output_limit=self.setting("walkthrough_output_limit", written)
            << 20,
        )
        for dependency in traced["deps"]:
            env.note_dependency(dependency)
        error = traced["error"]
        if error is not None and error.get("line") is None:
            raise self.error(f"walkthrough could not run: {error['text']}")
        steps = replay(traced, events or EVENTS)
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
            raise self.error("walkthrough captured no steps")
        cut = traced["truncated"] or len(steps) > most
        steps = steps[:most]
        self.check(traced, watch, ranges, steps, cut=cut)
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
            self.warn(f"{', '.join(unused)} only apply to a python walkthrough")
        values: dict[str, tuple[int, str]] = {}
        steps: list[dict[str, t.Any]] = []
        for index, (block, (low, high)) in enumerate(
            zip(notes, ranges, strict=True)
        ):
            where = self.place(block, high, start, total)
            for key in listed(block.options.get("clear")):
                if values.pop(key, None) is None:
                    self.warn(
                        f"the note for {label(low, high)} clears {key},"
                        " which is not showing"
                    )
            fresh: set[str] = set()
            for entry in ENTRIES.split(block.options.get("values", "")):
                match = VALUE.match(entry)
                if match is None:
                    if entry.strip():
                        self.warn(
                            f"the note for {label(low, high)} has {entry!r}"
                            " in :values:, which is not `name: value`"
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
        if not at.isdigit():
            raise self.error(f":at: takes a line number, got {at!r}")
        if not start <= int(at) <= start + total - 1:
            self.warn(
                f":at: {at} is outside the snippet, which is"
                f" {label(start, start + total - 1)}, so the values sit"
                f" beside {label(high, high)}"
            )
            return high - start + 1
        return int(at) - start + 1

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
            self.warn(
                f"Kaamiki does not know how {language} writes a comment;"
                " set :comment: so the values read as one"
            )
        return {"open": "#", "close": ""}

    def caption(self, count: int, language: str) -> heading:
        """Build the header, with the caption parsed as rST and the
        icon of the snippet's language.

        The caption keeps its place in the source, so `gettext` can
        collect it.

        :param count: How many steps the walkthrough holds.
        :param language: The language named on the directive.
        :return: The header node.
        """
        head = heading(count=count, icon="")
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
        site = self.state.document.settings.env.config.html_context
        head["icon"] = badged(head, language, kit=bool(site.get("fa_kit")))
        return head

    def snippet(self, code: str, language: str, start: int) -> plain:
        """Write the snippet out as a plain code block.

        :param code: The snippet.
        :param language: The language to highlight it in.
        :param start: The number the snippet's first line is given.
        :return: The code block.
        """
        block = plain(code, code)
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
        *,
        cut: bool,
    ) -> None:
        """Warn about whatever the author probably didn't mean.

        :param traced: What the tracer saw.
        :param watch: The names asked for.
        :param ranges: The lines each note covers.
        :param steps: The steps, with their notes.
        :param cut: Whether the steps stop short of the snippet's end.
        """
        error = traced["error"]
        raises = "raises" in self.options
        if error is not None and not raises:
            self.warn(
                f"the snippet raised {error['text']}; add :raises: if"
                " it is meant to"
            )
        if error is None and raises:
            self.warn(":raises: is set, but the snippet ran to the end")
        if cut:
            self.warn(
                f"stopped after {len(steps)} steps; raise :limit: or trim"
                " the snippet"
            )
        unseen = ", ".join(_ for _ in watch if _ not in traced["seen"])
        if unseen:
            self.warn(
                f":watch: asks for {unseen}, which the snippet never sets"
            )
        shown = {_["note"] for _ in steps}
        for index, (low, high) in enumerate(ranges):
            if index not in shown:
                self.warn(f"the note for {label(low, high)} never comes up")

    def warn(self, message: str) -> None:
        """Log a warning against this directive."""
        logger.warning(
            "walkthrough: %s",
            message,
            location=self.get_location(),
            type="walkthrough",
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
                raise self.error(f"emphasize-lines got {part!r}")
            low, high = found
            if low < start or high > end:
                self.warn(
                    f":emphasize-lines: {part} is outside the snippet,"
                    f" which is {label(start, end)}"
                )
            marked.update(range(max(low, start), min(high, end) + 1))
        return marked


def inherit(steps: list[dict[str, t.Any]]) -> None:
    """Give a step no note covers the note before it."""
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


# HACK(xames3): This needs to be optimised sometime in the future. I
# honestly feel this is just a patch to make it work for the very few
# languages I've tested so far.
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


def visit(self: HTMLTranslator, node: node) -> None:
    """Open the walkthrough, write its steps and open the pane.

    :param self: The HTML translator, whose body this appends to.
    :param node: The `walkthrough` node and its attributes.
    """
    ids: list[str] = node["ids"]
    classes = " ".join(
        [
            "km-walkthrough",
            f"km-walkthrough--{node['position']}",
            *node.get("classes", []),
        ]
    )
    anchor = f' id="{self.attval(ids[0])}"' if ids else ""
    self.body.append(f'<div{anchor} class="{classes}" data-km-walkthrough>')
    self.body.extend(f'<span id="{self.attval(_)}"></span>' for _ in ids[1:])
    self.body.append(
        '<script type="application/json" data-km-payload>'
        + json.dumps(node["payload"]).replace("<", "\\u003c")
        + "</script>"
    )
    self.body.append('<div class="km-walkthrough__pane" data-km-pane>')


def depart(self: HTMLTranslator, node: node) -> None:
    """Close the pane and the walkthrough.

    :param self: The HTML translator, whose body this appends to.
    :param node: The `walkthrough` node (unused).
    """
    del node
    self.body.append("</div></div>")


def visit_heading(self: HTMLTranslator, node: heading) -> None:
    """Open the code's side, its frame and the caption, icon first.

    :param self: The HTML translator, whose body this appends to.
    :param node: The header node, empty when there's no caption.
    """
    self.body.append('<div class="km-walkthrough__grid">')
    self.body.append('<div class="km-walkthrough__side">')
    self.body.append('<div class="km-walkthrough__frame" data-km-frame>')
    if node.children:
        self.body.append(
            '<div class="code-block-caption km-walkthrough__caption">'
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
    :param node: The header node, carrying the step count.
    """
    if node.children:
        self.body.append("</span>")
        self.body.append(controls(node["count"]))
        self.body.append("</div>")
    else:
        self.body.append(
            f'<div class="km-walkthrough__corner">{controls(node["count"])}'
            "</div>"
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
    self.body.append('<div class="km-walkthrough__notes" data-km-notes>')
    self.body.append('<div class="km-walkthrough__track" data-km-track>')


def depart_explanations(self: HTMLTranslator, node: explanations) -> None:
    """Close the notes and the row they share with the code.

    :param self: The HTML translator, whose body this appends to.
    :param node: The container node (unused).
    """
    del node
    self.body.append("</div></div></div>")


def close(self: HTMLTranslator, node: nodes.Element) -> None:
    """Close whichever `div` the matching visitor opened.

    :param self: The HTML translator, whose body this appends to.
    :param node: The node being departed (unused).
    """
    del node
    self.body.append("</div>")


def register(app: Sphinx) -> None:
    """Register the nodes only a walkthrough has.

    :param app: The Sphinx application instance.
    """
    app.add_node(heading, html=(visit_heading, depart_heading))
    app.add_node(plain, html=(skip, None))
    app.add_node(explanations, html=(visit_explanations, depart_explanations))
    app.add_node(explanation, html=(visit_explanation, close))
