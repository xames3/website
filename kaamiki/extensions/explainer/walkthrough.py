"""\
Walkthrough Directive
=====================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 12 September, 2026
Last updated on: 01 October, 2026

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

Any other language is not run. Each `.. lines::` is a step of its own,
in the order written and brings its own values and prints::

    .. walkthrough:: c

       .. code::

           int total = 0;
           total += 3;

       .. lines:: 2
           :values: total: 3

           Add three.

.. note::

    The Python runs in a scratch directory with a bare environment, a
    gigabyte of memory and ten seconds and the directory goes when it
    finishes.
"""

from __future__ import annotations

import json
import os.path as p
import re
import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst
from docutils.transforms import Transform
from sphinx.directives.code import CodeBlock
from sphinx.util import logging

from kaamiki.extensions.explainer.chrome import comment
from kaamiki.extensions.explainer.chrome import controls
from kaamiki.extensions.explainer.chrome import depart_explanation
from kaamiki.extensions.explainer.chrome import label
from kaamiki.extensions.explainer.chrome import lexer_for
from kaamiki.extensions.explainer.chrome import output
from kaamiki.extensions.explainer.chrome import pane
from kaamiki.extensions.explainer.chrome import visit_explanation
from kaamiki.extensions.explainer.grammar import linerange
from kaamiki.extensions.explainer.grammar import parse_list
from kaamiki.extensions.explainer.grammar import split
from kaamiki.extensions.explainer.tracer import budget
from kaamiki.extensions.explainer.tracer import collapse
from kaamiki.extensions.explainer.tracer import execute
from kaamiki.extensions.explainer.tracer import kinds
from kaamiki.extensions.explainer.tracer import limit
from kaamiki.extensions.explainer.tracer import replay
from kaamiki.extensions.explainer.tracer import show
from kaamiki.extensions.explainer.tracer import timeout
from kaamiki.extensions.utils import findall

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.writers.html import HTMLTranslator

    from kaamiki.extensions.explainer.grammar import chunk
    from kaamiki.extensions.explainer.tracer import Trace

logger = logging.getLogger(__name__)

name: t.Final[str] = "walkthrough"
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

    It is a `container` underneath, as are its notes, so a builder that
    has never heard of a walkthrough still has something to write.
    """


class lead(nodes.container):
    """The paragraph or two leading into the walkthrough, taken in."""


class tail(nodes.container):
    """The prose after the walkthrough in its section, taken in."""


class heading(nodes.paragraph):
    """The caption, parsed as rST and the step counter.

    docutils already has a `caption` node and finds a node's visitor by
    its class name, so this cannot borrow that one.
    """


class plain(nodes.literal_block):
    """The snippet as a plain code block, for every builder but HTML."""


class explanations(nodes.container):
    """The notes under the snippet, one of which shows at a time."""


class explanation(nodes.container):
    """One `lines` block's note.

    Calling it `note` would take over every `.. note::` on the site, for
    the same reason `heading` is not a `caption`.
    """


class directive(CodeBlock):
    """The `walkthrough` directive.

    The argument is the snippet's language and defaults to `python`.
    It takes the options `code-block` does, bar `dedent` and `force`,
    and adds its own. All but `pace` only mean anything to a Python
    snippet, since only that one is run::

        - `watch`: The names to show, comma-separated. Leaving it out
          shows none, only what a function returns and what the
          snippet raises.
        - `limit`: How many steps to show. Defaults to 100.
        - `timeout`: How long the snippet may run, in seconds.
        - `pythonpath`: Directories to import from, comma-separated and
          relative to the document.
        - `events`: Which of `call`, `line` and `return` make a step.
          Defaults to `line` and `return`.
        - `comprehensions`: Step into comprehensions too.
        - `pace`: How much scrolling a step takes, in pixels. Defaults
          to what `pace` picks for the language.
        - `raises`: The snippet is meant to fail, so it ends on the
          exception rather than warning about it.
        - `comment`: How the snippet's language opens a comment and
          closes one if it must (`(* *)`), for a language the theme
          does not know. The values are written as that comment.
    """

    option_spec = {  # noqa: RUF012
        **{
            key: value
            for key, value in CodeBlock.option_spec.items()
            if key not in {"dedent", "force"}
        },
        "watch": rst.directives.unchanged,
        "limit": rst.directives.positive_int,
        "timeout": rst.directives.positive_int,
        "pythonpath": rst.directives.unchanged,
        "events": rst.directives.unchanged,
        "comprehensions": rst.directives.flag,
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
        element += self.caption(len(steps))
        element += self.snippet(code, language, start)
        element += self.explain(notes)
        self.add_name(element)
        return [element]

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

        Each step is given the note whose lines it sits on, counting
        them the way the reader sees them numbered.

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
        events = frozenset(parse_list(self.options.get("events", "")))
        if events - kinds:
            raise self.error(
                f"events takes {', '.join(sorted(kinds))},"
                f" got {', '.join(sorted(events - kinds))}"
            )
        watch = list(dict.fromkeys(parse_list(self.options.get("watch", ""))))
        here = p.dirname(str(self.state.document.current_source))
        paths = [
            _ if p.isabs(_) else p.abspath(p.join(here, _))
            for _ in parse_list(self.options.get("pythonpath", ""))
        ]
        most = self.options.get("limit", limit)
        traced = execute(
            code,
            setup,
            stdin,
            watch,
            most * budget,
            self.options.get("timeout", timeout),
            paths,
            comprehensions="comprehensions" in self.options,
        )
        env = self.state.document.settings.env
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
        r"""Make a step of every note, for a snippet that is not run.

        :param setup: The `setup` block, which cannot run here.
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
        if not notes:
            raise self.error("walkthrough needs a `.. lines::` block per step")
        values: dict[str, tuple[int, str]] = {}
        steps: list[dict[str, t.Any]] = []
        for index, (block, (low, high)) in enumerate(
            zip(notes, ranges, strict=True)
        ):
            where = self.place(block, high, start, total)
            for key in parse_list(block.options.get("clear")):
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
                f"the theme does not know how {language} writes a comment;"
                " set :comment: so the values read as one"
            )
        return {"open": "#", "close": ""}

    def caption(self, count: int) -> heading:
        """Build the header, with the caption parsed as rST.

        :param count: How many steps the walkthrough holds.
        :return: The header node.
        """
        head = heading(count=count)
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
        head.extend(parsed[0].children)
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

        :param notes: The `lines` blocks, in the order they were written.
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
        """Warn about whatever the author probably did not mean.

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
        for part in parse_list(self.options.get("emphasize-lines", "")):
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


class adopt(Transform):
    """Take the prose either side of a walkthrough into it."""

    default_priority = 900

    def apply(self, **kwargs: t.Any) -> None:
        """Move the prose around every walkthrough into it."""
        for element in list(findall(self.document, node)):
            parent = element.parent
            if parent is None:
                continue
            index = parent.index(element)
            before: list[nodes.Node] = []
            for sibling in reversed(parent.children[:index]):
                if len(before) == 2 or not leading(sibling):
                    break
                before.insert(0, sibling)
            after: list[nodes.Node] = []
            for sibling in parent.children[index + 1 :]:
                if not prose(sibling):
                    break
                after.append(sibling)
            for sibling in before + after:
                parent.remove(sibling)
            if before:
                element.insert(0, lead("", *before))
                element["classes"].append("km-walkthrough--lead")
            if after:
                element += tail("", *after)


def leading(sibling: nodes.Node) -> bool:
    """Say whether something before a walkthrough can be taken into it.

    :param sibling: The node before the walkthrough.
    :return: `True` when it is a plain paragraph.
    """
    return isinstance(sibling, nodes.paragraph) and not sibling["classes"]


def prose(sibling: nodes.Node) -> bool:
    """Say whether something after a walkthrough can be taken into it.

    :param sibling: The node after the walkthrough.
    :return: `True` when it is prose belonging to this section.
    """
    if not isinstance(sibling, nodes.Element):
        return False
    if isinstance(sibling, nodes.paragraph) and sibling["classes"]:
        return False
    if not isinstance(sibling, nodes.Body) or isinstance(
        sibling, nodes.Invisible
    ):
        return False
    if "km-pre-title-text" in sibling["classes"]:
        return False
    return next(iter(findall(sibling, node)), None) is None


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
    classes = " ".join(["km-walkthrough", *node.get("classes", [])])
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
    self.body.append(
        '<span class="sr-only" aria-live="polite" data-km-status></span>'
        "</div></div>"
    )


def visit_lead(self: HTMLTranslator, node: lead) -> None:
    """Open the paragraphs that lead into the walkthrough.

    :param self: The HTML translator, whose body this appends to.
    :param node: The lead node (unused).
    """
    self.body.append('<div class="km-walkthrough__lead" data-km-lead>')


def visit_tail(self: HTMLTranslator, node: tail) -> None:
    """Open the prose that follows the walkthrough.

    :param self: The HTML translator, whose body this appends to.
    :param node: The tail node (unused).
    """
    self.body.append('<div class="km-walkthrough__tail">')


def visit_heading(self: HTMLTranslator, node: heading) -> None:
    """Open the snippet's frame and, when there is one, its caption.

    :param self: The HTML translator, whose body this appends to.
    :param node: The header node, empty when there is no caption.
    """
    self.body.append('<div class="km-walkthrough__frame" data-km-frame>')
    if node.children:
        self.body.append(
            '<div class="code-block-caption km-walkthrough__caption">'
            '<span class="caption-text">'
        )


def depart_heading(self: HTMLTranslator, node: heading) -> None:
    """Close the caption, then write the snippet and close the frame.

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
    self.body.append("</div>")


def visit_explanations(self: HTMLTranslator, node: explanations) -> None:
    """Open the notes under the snippet.

    :param self: The HTML translator, whose body this appends to.
    :param node: The container node (unused).
    """
    self.body.append('<div class="km-walkthrough__notes" data-km-notes>')


def close(self: HTMLTranslator, node: nodes.Element) -> None:
    """Close whichever `div` the matching visitor opened.

    :param self: The HTML translator, whose body this appends to.
    :param node: The node being departed (unused).
    """
    self.body.append("</div>")


def skip(self: HTMLTranslator, node: plain) -> None:
    """Leave the plain snippet out of HTML, which has the real one.

    :param self: The HTML translator (unused).
    :param node: The plain snippet (unused).
    :raises nodes.SkipNode: Always.
    """
    raise nodes.SkipNode


def register(app: Sphinx) -> None:
    """Register the nodes and the transform the directive loop misses.

    :param app: The Sphinx application instance.
    """
    app.add_transform(adopt)
    app.add_node(lead, html=(visit_lead, close))
    app.add_node(tail, html=(visit_tail, close))
    app.add_node(heading, html=(visit_heading, depart_heading))
    app.add_node(plain, html=(skip, None))
    app.add_node(explanations, html=(visit_explanations, close))
    app.add_node(explanation, html=(visit_explanation, depart_explanation))
