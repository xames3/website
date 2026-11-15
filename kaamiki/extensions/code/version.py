"""\
Code Version Directive
======================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 28 September 2026
Last updated on: 15 November 2026

A `code-version` directive that steps a reader through the versions a
piece of code went through on its way to what it is now::

    .. code-version:: python
       :caption: xsnumpy/_core.py

       .. attempt::

           .. code::

               def __repr__(self):
                   return f"array({self._data})"

           .. output:: broke

               >>> array([[1, 2], [3, 4]])
               array([1, 2, 3, 4])

           Fine for scalars. Fell over the moment it met a 2D array.

       .. attempt::

           .. code::

               def __repr__(self):
                   if self.ndim == 1:
                       return f"array({self._data})"

           .. lines:: 2-3

               The 1D case keeps what already worked.
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
from sphinx.locale import _

from kaamiki.extensions.code import explain
from kaamiki.extensions.code.chrome import known
from kaamiki.extensions.code.chrome import label
from kaamiki.extensions.code.chrome import notes_pane
from kaamiki.extensions.code.grammar import StrayError
from kaamiki.extensions.code.grammar import linerange
from kaamiki.extensions.code.grammar import split
from kaamiki.extensions.utils import BEM
from kaamiki.extensions.utils import findall
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import moving

if t.TYPE_CHECKING:
    from sphinx.writers.html import HTMLTranslator

    from kaamiki.extensions.code.grammar import chunk

    type Pieces = tuple[chunk, chunk | None, list[chunk]]

name: t.Final[str] = "code-version"
code_version: t.Final[BEM] = BEM("code-version")
ATTEMPT: t.Final[frozenset[str]] = frozenset({"attempt"})
PARTS: t.Final[frozenset[str]] = frozenset({"code", "lines", "output"})
VERDICTS: t.Final[frozenset[str]] = frozenset({"broke", "worked"})
STRETCH: t.Final[float] = 2.5


class Attempt(nodes.container):
    """One attempt: its code, what it printed and its notes."""


class Draft(nodes.container):
    """An attempt's code and what it printed, framed on their own.

    The script never shows these. They hold the versions it swaps
    between, and they're the page for a reader with no scripting.
    """


class Outcome(nodes.literal_block):
    """What an attempt printed, as the author wrote it."""


class CodeVersion(explain.CodeWalk, name="code-version"):
    """The `code-version` directive.

    The argument is the language of all the versions. The default is
    `python`. Put it on the page itself. A plain `container` or an
    `only` is part of the page. The content of a different directive,
    and the notes of a walkthrough, are not.

    Options::

        - `code-position`: The side of the code, `right` or `left`. The
          default is `right`.
        - `pace`: The pixels of scrolling for each step, from 24 to 240.
          A step that brings in a version takes `STRETCH` times that.
        - `caption`: A line of text above the code, parsed as rST.
        - `linenos`: Show the line numbers.
        - `lineno-start`: The number of the first line, from 0 to 10000.
        - `no-motion`: Show it stacked, without motion.
        - `name`: A name for links to the `code-version`.
        - `class`: More classes for the `code-version`.
    """

    class Node(explain.CodeExplain.Node):
        """The versions, written as a walkthrough with notes."""

    def build(self) -> list[nodes.Node]:
        """Read each attempt and make the directive's node.

        :return: A list holding the one `code-version` node.
        """
        language = self.arguments.pop().strip() if self.arguments else "python"
        if not known(language):
            self.fail(f"expected a language Pygments knows, got {language!r}")
        start = self.options.get("lineno-start", 1)
        drafts = [
            self.unpack(block, index)
            for index, block in enumerate(self.attempts(), start=1)
        ]
        if not any(notes for _, _, notes in drafts):
            self.fail("expected a note, in prose or `.. lines::`, got none")
        codes = [code.text() for code, _, _ in drafts]
        digits = len(str(start + max(len(_.splitlines()) for _ in codes) - 1))
        base = self.options.get("pace", explain.pace(language))
        attributes: dict[str, t.Any] = {}
        attributes["classes"] = [
            "km-code-version",
            *self.options.get("class", []),
            *moving(self.options, timed=False),
        ]
        attributes["position"] = self.options.get("code-position", "right")
        attributes["payload"] = {
            "steps": self.steps(drafts, start, base),
            "pace": base,
            "code": codes[0],
            "codes": codes,
        }
        attributes["pane"] = notes_pane(
            codes[0],
            language,
            start,
            set(),
            linenos="linenos" in self.options,
            digits=digits,
        )
        element = self.locate(self.Node("", **attributes))
        element += self.captioned(language)
        element += self.story(drafts, language, start, digits)
        self.add_name(element)
        return [element]

    def attempts(self) -> list[chunk]:
        """Pull the `attempt` blocks out of the directive's content.

        :return: The blocks, in the order they were written.
        """
        try:
            found = split(self.content, self.content_offset, ATTEMPT, {})
        except StrayError as exc:
            self.fail(
                "expected text inside an `.. attempt::`, got"
                f" {exc.text!r} on line {exc.line}"
            )
        if not found:
            self.fail("expected an `.. attempt::` per version, got none")
        for block in found:
            if block.argument:
                self.fail(
                    f"`.. attempt::` expected no name, got {block.argument!r}"
                )
        if len(found) == 1:
            self.fail("expected at least 2 attempts, got 1")
        return found

    def unpack(self, block: chunk, at: int) -> Pieces:
        """Split an attempt into its code, its output and its notes.

        The prose in an attempt is one note, whichever blocks it sits
        around, until a `.. lines::` comes along. Each of those is a
        note of its own, and prose after one starts another.

        :param block: The `attempt` block.
        :param at: Which attempt it is, counting from one.
        :return: The `code` block, the `output` block or `None`, and
            the notes in the order they were written, prose as nameless
            chunks and the rest as `lines` blocks.
        """
        found = split(block.body, block.offset, PARTS, {}, loose=True)
        for kind in ("code", "output"):
            if sum(_.name == kind for _ in found) > 1:
                self.fail(
                    f"attempt {at} expected one {kind}, got more than one"
                )
        code = next((_ for _ in found if _.name == "code"), None)
        if code is None:
            self.fail(f"attempt {at} expected one `.. code::` block, got none")
        if not code.body:
            self.fail(
                f"attempt {at} expected some code in the `.. code::`, got none"
            )
        printed = next((_ for _ in found if _.name == "output"), None)
        if printed is not None and printed.argument not in VERDICTS | {""}:
            self.fail(
                f"the output of attempt {at} expected broke or"
                f" worked, or nothing, got {printed.argument!r}"
            )
        if printed is not None and not printed.body:
            self.fail(
                f"the output of attempt {at} expected some text, got none"
            )
        notes: list[chunk] = []
        for part in found:
            if part.name == "lines":
                notes.append(part)
            elif part.name == "" and notes and notes[-1].name == "":
                source, line = part.body.info(0)
                notes[-1].body.append("", source, line or 0)
                notes[-1].body.extend(part.body)
            elif part.name == "":
                notes.append(part)
        return code, printed, notes

    def span(
        self, argument: str, start: int, total: int, at: int = 0
    ) -> tuple[int, int]:
        """Read the lines a `lines` block points at, in its own
        version.

        :param argument: The block's argument, as written.
        :param start: The number every version's first line is given.
        :param total: How many lines this version has.
        :param at: Which attempt it belongs to, counting from one.
        :return: The first and the last line it covers.
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
                f":lines: expected a range within attempt {at},"
                f" {label(start, start + total - 1)}, got {label(low, high)}"
            )
        return found

    def steps(
        self, drafts: list[Pieces], start: int, base: int
    ) -> list[dict[str, t.Any]]:
        """Make a step of every note, attempt by attempt.

        An attempt with nothing to say still gets a step, since its
        version has to come up. It borrows the note before it, or the
        first note there is when none comes before it. The first step
        of every attempt brings its version in, so it takes `STRETCH`
        times the scrolling, and its last step is where its output
        lands.

        :param drafts: The attempts, unpacked.
        :param start: The number every version's first line is given.
        :param base: How much scrolling a step takes, in pixels.
        :return: The steps, in the order they come up.
        """
        steps: list[dict[str, t.Any]] = []
        count = 0
        for index, (code, printed, notes) in enumerate(drafts):
            total = len(code.text().splitlines())
            first = len(steps)
            for part in notes:
                step: dict[str, t.Any] = {"version": index, "note": count}
                if part.name == "lines":
                    low, high = self.span(
                        part.argument, start, total, index + 1
                    )
                    step["line"] = low - start + 1
                    if high != low:
                        step["end"] = high - start + 1
                count += 1
                steps.append(step)
            if len(steps) == first:
                steps.append({"version": index, "note": None})
            steps[first]["pace"] = round(base * STRETCH)
            if printed is not None:
                steps[-1]["out"] = printed.text()
                if printed.argument:
                    steps[-1]["verdict"] = printed.argument
        explain.inherit(steps)
        return steps

    def story(
        self, drafts: list[Pieces], language: str, start: int, digits: int
    ) -> explain.Explanations:
        """Parse every attempt into its frame and its notes.

        :param drafts: The attempts, unpacked.
        :param language: The language to highlight the code in.
        :param start: The number every version's first line is given.
        :param digits: The characters the widest version's line numbers
            take, so every version's code starts in the same column.
        :return: The attempts, under the container the notes go in.
        """
        box = explain.Explanations()
        count = 0
        for index, (code, printed, notes) in enumerate(drafts):
            group = Attempt()
            frame = Draft(index=index, digits=digits)
            frame += self.snippet(code.text(), language, start)
            if printed is not None:
                result = Outcome(printed.text(), printed.text())
                result["language"] = "text"
                result["verdict"] = printed.argument
                self.set_source_info(result)
                frame += result
            group += frame
            for part in notes:
                note = explain.Explanation(index=count)
                self.state.nested_parse(part.body, part.offset, note)
                group += note
                count += 1
            box += group
        return box


html.opens(CodeVersion.Node)(explain.visit)
html.closes(CodeVersion.Node, "</div></div>")


@html.opens(Attempt)
def visit_attempt(self: HTMLTranslator, element: Attempt) -> None:
    """Open one attempt.

    :param self: The HTML translator, whose body this appends to.
    :param element: The attempt (unused).
    """
    del element
    self.body.append(f'<div class="{code_version.attempt()}">')


html.closes(Attempt, "</div>")


@html.opens(Draft)
def visit_draft(self: HTMLTranslator, element: Draft) -> None:
    """Open an attempt's frame and write its code.

    The code is written the way the pane writes it, a line at a time,
    which is also where the script picks each version's lines up from.

    :param self: The HTML translator, whose body this appends to.
    :param element: The frame, carrying its index and the gutter's
        width, and holding the plain code block.
    """
    code = next(findall(element, explain.PlainCode))
    index = element["index"]
    self.body.append(
        f'<div class="{code_version.draft()}" data-km-draft="{index}">'
    )
    self.body.append(
        notes_pane(
            code.astext(),
            code["language"],
            code["highlight_args"]["linenostart"],
            set(),
            linenos=code["linenos"],
            digits=element["digits"],
        )
    )


html.closes(Draft, "</div>")


@html.opens(Outcome)
def visit_outcome(self: HTMLTranslator, element: Outcome) -> None:
    """Write what an attempt printed, coloured by how it went.

    :param self: The HTML translator, whose body this appends to.
    :param element: The output, carrying its verdict.
    :raises nodes.SkipNode: Always, having written it whole.
    """
    verdict = element["verdict"]
    words = {"broke": str(_("Broke")), "worked": str(_("Worked"))}
    spoken = (
        f'<span class="sr-only">{self.encode(words[verdict])}: </span>'
        if verdict
        else ""
    )
    self.body.append(
        f'<pre class="{explain.code_explain.output()}"'
        + (f' data-km-verdict="{verdict}"' if verdict else "")
        + f">{spoken}{self.encode(element.astext())}</pre>"
    )
    raise nodes.SkipNode
