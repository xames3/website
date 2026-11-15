"""\
Walkthrough Chrome
==================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 12 September 2026
Last updated on: 15 November 2026

The markup around a walkthrough.
"""

from __future__ import annotations

import html
import typing as t

from pygments import highlight as pygmentise
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound
from sphinx.locale import _

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from docutils import nodes
    from pygments.lexer import Lexer
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
    ("<!--", "-->", frozenset({"html", "markdown", "md", "svg", "vue", "xml"})),
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
    :raises ClassNotFound: When Pygments has no lexer. Use `known` to ask first.
    """
    return get_lexer_by_name(language)


def comment(language: str) -> dict[str, str] | None:
    """Find how a language writes a comment, for the values next to the code.

    :param language: The language of the directive.
    :return: What opens a comment and what closes it, or `None` for a language
        that `COMMENTS` does not know.
    :raises ClassNotFound: When Pygments has no lexer for the language.
    """
    names = {language.lower(), *lexer_for(language).aliases}
    for opens, closes, languages in COMMENTS:
        if names & languages:
            return {"open": opens, "close": closes}
    return None


def highlight(code: str, language: str) -> list[str]:
    """Highlight a snippet, one line at a time.

    :param code: The snippet.
    :param language: The language of the snippet.
    :return: One string of markup for each line.
    """
    formatter = HtmlFormatter(nowrap=True)
    body: str = pygmentise(code, lexer_for(language), formatter)
    lines: list[str] = body.split("\n")
    if lines and not lines[-1].strip():
        lines.pop()
    return lines


def notes_pane(
    code: str,
    language: str,
    start: int,
    emphasis: set[int],
    *,
    linenos: bool,
    digits: int = 0,
) -> str:
    """Write the highlighted snippet that a walkthrough steps through.

    :param code: The snippet.
    :param language: The language of the snippet.
    :param start: The number of the first line.
    :param emphasis: The lines to mark, with the numbers that the reader sees.
    :param linenos: Whether to show the line numbers.
    :param digits: The width of the line numbers, so that versions of a snippet
        align. The default is the width that the snippet needs.
    :return: The markup of the pane.
    """
    rows: list[str] = []
    for offset, line in enumerate(highlight(code, language)):
        number = start + offset
        mark = " data-km-emphasis" if number in emphasis else ""
        rows.append(
            f'<span class="km-code-explain__line" data-km-line="{offset + 1}"'
            f' data-km-number="{number}"{mark}>'
            f'<span class="km-code-explain__source">{line or "&nbsp;"}</span>'
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


def controls(icons: Mapping[str, str]) -> str:
    """Write the controls at the end of the caption of a walkthrough.

    :param icons: The named icons of the site.
    :return: The markup. Without a caption, it goes in the top corner of the
        snippet. The button holds its two icons, and the stylesheet shows the
        icon for its state.
    """
    marks = "".join(
        f'<i class="{icons[key]} km-code-explain__{name}"'
        ' aria-hidden="true"></i>'
        for key, name in (("copy", "clipboard"), ("copied", "done"))
        if icons[key]
    )
    return (
        '<button type="button" class="km-code-explain__copy" data-km-copy'
        f' aria-label="{html.escape(str(_("Copy the snippet")))}">'
        f"{marks}</button>"
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
