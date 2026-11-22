"""\
Walkthrough Chrome
==================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 12 September 2026
Last updated on: 21 November 2026

The markup around a walkthrough.
"""

from __future__ import annotations

import html
import typing as t

from pygments.lexers import get_lexer_by_name
from pygments.token import STANDARD_TYPES
from pygments.util import ClassNotFound
from sphinx.locale import _

if t.TYPE_CHECKING:
    from docutils import nodes
    from pygments.lexer import Lexer
    from pygments.token import _TokenType
    from sphinx.writers.html import HTMLTranslator

COMMENTS: t.Final[tuple[tuple[str, str, frozenset[str]], ...]] = (
    (
        "#",
        "",
        frozenset(
            {
                "bash",
                "cmake",
                "coffeescript",
                "console",
                "crystal",
                "docker",
                "dockerfile",
                "elixir",
                "graphql",
                "hcl",
                "julia",
                "make",
                "makefile",
                "nim",
                "nix",
                "perl",
                "powershell",
                "py",
                "py3",
                "python",
                "python3",
                "r",
                "ruby",
                "sh",
                "shell",
                "tcl",
                "terraform",
                "toml",
                "yaml",
                "zsh",
            }
        ),
    ),
    (
        "//",
        "",
        frozenset(
            {
                "c",
                "c#",
                "c++",
                "cpp",
                "cs",
                "csharp",
                "cuda",
                "d",
                "dart",
                "glsl",
                "go",
                "golang",
                "groovy",
                "hlsl",
                "java",
                "javascript",
                "js",
                "json5",
                "jsx",
                "kotlin",
                "kt",
                "less",
                "objective-c",
                "objc",
                "php",
                "proto",
                "protobuf",
                "rs",
                "rust",
                "scala",
                "scss",
                "solidity",
                "swift",
                "ts",
                "tsx",
                "typescript",
                "verilog",
                "zig",
            }
        ),
    ),
    (
        "--",
        "",
        frozenset(
            {
                "ada",
                "applescript",
                "elm",
                "haskell",
                "hs",
                "lua",
                "mysql",
                "plpgsql",
                "postgres",
                "postgresql",
                "sql",
                "sqlite3",
                "tsql",
                "vhdl",
            }
        ),
    ),
    (
        "%",
        "",
        frozenset({"erlang", "latex", "matlab", "octave", "prolog", "tex"}),
    ),
    (
        ";",
        "",
        frozenset(
            {
                "asm",
                "clojure",
                "clj",
                "common-lisp",
                "elisp",
                "emacs-lisp",
                "ini",
                "lisp",
                "nasm",
                "racket",
                "scheme",
            }
        ),
    ),
    (
        "<!--",
        "-->",
        frozenset({"html", "markdown", "md", "svg", "vue", "xml"}),
    ),
    ("/*", "*/", frozenset({"css"})),
)


def known(language: str) -> bool:
    """Say whether Pygments has a lexer for a language.

    :param language: The language of the directive.
    :return: `True` when it has one.
    """
    try:
        lexer_for(language)
    except ClassNotFound:
        return False
    return True


def lexer_for(language: str) -> Lexer:
    """Find the Pygments lexer for a language.

    :param language: The language of the directive.
    :return: The lexer.
    :raises ClassNotFound: When Pygments has no lexer. Use `known` to
        ask first.
    """
    return get_lexer_by_name(language)


def comment(language: str) -> dict[str, str] | None:
    """Find how a language writes a comment.

    :param language: The language of the directive.
    :return: What opens a comment and what closes it, or `None` for a
        language that `COMMENTS` does not know.
    :raises ClassNotFound: When Pygments has no lexer for the language.
    """
    names = {language.lower(), *lexer_for(language).aliases}
    for opens, closes, languages in COMMENTS:
        if names & languages:
            return {"open": opens, "close": closes}
    return None


type Run = str | list[str]


def token_class(kind: _TokenType) -> str:
    """Name the Pygments classes of a token, as its HTML writes them.

    :param kind: The type of the token.
    :return: The classes, or an empty string for plain text.
    """
    chain = [kind]
    while chain[-1] not in STANDARD_TYPES and chain[-1].parent is not None:
        chain.append(chain[-1].parent)
    root = STANDARD_TYPES.get(chain[-1], "")
    names: list[str] = []
    suffix = ""
    for each in reversed(chain[:-1]):
        names.append(root + suffix)
        suffix += f"-{each[-1]}"
    names.append(root + suffix)
    return " ".join(names)


def tokens(code: str, language: str) -> list[list[Run]]:
    """Split a snippet into coloured runs, one list for each line.

    :param code: The snippet.
    :param language: The language of the snippet.
    :return: For each line, its runs. A run is a string for plain
        text, or the Pygments classes and the text.
    """
    lines: list[list[Run]] = [[]]
    for kind, value in lexer_for(language).get_tokens(code):
        name = token_class(kind)
        for index, part in enumerate(value.split("\n")):
            if index:
                lines.append([])
            if part:
                join(lines[-1], name, part)
    end = lines[-1]
    if all(isinstance(run, str) for run in end) and not text(end).strip():
        lines.pop()
    return lines


def join(line: list[Run], name: str, part: str) -> None:
    """Add text to a line, in the last run when its class is the same.

    :param line: The runs of the line.
    :param name: The Pygments classes of the text.
    :param part: The text.
    """
    last = line[-1] if line else None
    if not name and isinstance(last, str):
        line[-1] = last + part
    elif name and isinstance(last, list) and last[0] == name:
        last[1] += part
    else:
        line.append([name, part] if name else part)


def text(line: list[Run]) -> str:
    """Join the runs of a line into its plain text.

    :param line: The runs of the line.
    :return: The text of the line.
    """
    return "".join(run if isinstance(run, str) else run[1] for run in line)


def notes_pane(
    lines: list[list[Run]],
    start: int,
    emphasis: set[int],
    *,
    linenos: bool,
    digits: int = 0,
) -> str:
    """Write the snippet that a walkthrough steps through, as text.

    :param lines: The runs of each line, from `tokens`.
    :param start: The number of the first line.
    :param emphasis: The lines to mark, with the numbers that the
        reader sees.
    :param linenos: Whether to show the line numbers.
    :param digits: The width of the line numbers, so that versions of a
        snippet align. The default is the width that the snippet needs.
    :return: The markup of the pane.
    """
    rows: list[str] = []
    for offset, line in enumerate(lines):
        source = html.escape(text(line), quote=False) or "&nbsp;"
        number = start + offset
        mark = " data-km-emphasis" if number in emphasis else ""
        rows.append(
            f'<span class="km-code-explain__line" data-km-line="{offset + 1}"'
            f' data-km-number="{number}"{mark}>'
            f'<span class="km-code-explain__source">{source}</span>'
            '<span class="km-code-explain__annotation"'
            " data-km-annotation></span>\n</span>"
        )
    gutter = " km-code-explain__code--linenos" if linenos else ""
    digits = digits or len(str(start + max(len(rows), 1) - 1))
    return (
        '<div class="km-code-explain__stage" data-km-stage tabindex="0"'
        f' role="group" aria-label="{html.escape(str(_("Code")))}">'
        f'<pre class="highlight km-code-explain__code{gutter}"'
        f' style="--km-code-explain-gutter: {digits}ch">'
        + "".join(rows)
        + "</pre></div>"
    )


def output() -> str:
    """Write the box for what a snippet prints."""
    return (
        '<pre class="km-code-explain__output" data-km-output'
        f' data-km-empty="{html.escape(str(_("Nothing printed yet")))}"'
        " hidden></pre>"
    )


def label(low: int, high: int) -> str:
    """Name a range of lines, as a warning writes it.

    :param low: The first line.
    :param high: The last line.
    :return: `line 6` or `lines 7-8`.
    """
    if low == high:
        return f"line {low}"
    return f"lines {low}-{high}"


def visit_explanation(self: HTMLTranslator, node: nodes.Element) -> None:
    """Open the note of one `lines` block.

    :param self: The HTML translator, whose body this appends to.
    :param node: The node of the note, with its index.
    """
    self.body.append(
        f'<div class="km-code-explain__note" data-km-note="{node["index"]}">'
    )
