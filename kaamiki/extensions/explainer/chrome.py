"""\
Explainer Chrome
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 12 September, 2026
Last updated on: 01 October, 2026

The markup an explainer wraps itself in.
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


def lexer_for(language: str) -> Lexer:
    """Find the Pygments lexer for a language.

    :param language: The language named on the directive.
    :return: Its lexer, falling back to plain text for a name Pygments
        does not know.
    """
    try:
        return get_lexer_by_name(language)
    except ClassNotFound:
        return get_lexer_by_name("text")


def comment(language: str) -> dict[str, str] | None:
    """Find how a language writes a comment, for the values beside it.

    :param language: The language named on the directive.
    :return: What opens a comment and what closes it or `None` for a
        language `COMMENTS` does not know.
    """
    names = {language.lower(), *lexer_for(language).aliases}
    for opens, closes, languages in COMMENTS:
        if names & languages:
            return {"open": opens, "close": closes}
    return None


def highlight(code: str, language: str) -> list[str]:
    """Highlight a snippet and give it back a line at a time.

    :param code: The snippet.
    :param language: The language to highlight it as.
    :return: One string of markup per line.
    """
    formatter = HtmlFormatter(nowrap=True)
    body: str = pygmentise(code, lexer_for(language), formatter)
    lines: list[str] = body.split("\n")
    if lines and not lines[-1].strip():
        lines.pop()
    return lines


def pane(
    code: str,
    language: str,
    start: int,
    emphasis: set[int],
    *,
    linenos: bool,
) -> str:
    """Write the highlighted snippet the stepper walks through.

    :param code: The snippet.
    :param language: The language to highlight it as.
    :param start: The number to give the first line.
    :param emphasis: The lines to mark, numbered as the reader sees
        them.
    :param linenos: Whether to show a line-number gutter.
    :return: The pane's markup.
    """
    width = max((len(_.expandtabs(4)) for _ in code.splitlines()), default=0)
    rows: list[str] = []
    for offset, line in enumerate(highlight(code, language)):
        number = start + offset
        mark = " data-km-emphasis" if number in emphasis else ""
        rows.append(
            f'<span class="km-walkthrough__line" data-km-line="{offset + 1}"'
            f' data-km-number="{number}"{mark}>'
            f'<span class="km-walkthrough__src">{line or "&nbsp;"}</span>'
            '<span class="km-walkthrough__ann" data-km-ann></span>\n</span>'
        )
    gutter = " km-walkthrough__code--linenos" if linenos else ""
    digits = len(str(start + max(len(rows), 1) - 1))
    return (
        '<div class="km-walkthrough__stage" data-km-stage tabindex="0">'
        f'<pre class="highlight km-walkthrough__code{gutter}"'
        f' style="--km-walkthrough-col: {width + 4};'
        f' --km-walkthrough-gutter: {digits}ch">'
        + "".join(rows)
        + "</pre></div>"
    )


def controls(count: int) -> str:
    """Write what sits at the end of an explainer's caption.

    With no caption, the same markup sits in the snippet's top corner
    instead.

    :param count: How many steps the explainer holds.
    :return: The markup.
    """
    steps = str(_("1 step")) if count == 1 else str(_("%d steps")) % count
    return (
        '<span class="km-walkthrough__counter" data-km-counter>'
        f"{html.escape(steps)}</span>"
        '<span class="km-walkthrough__pager">'
        '<button type="button" class="km-walkthrough__step" data-km-step="-1"'
        f' aria-label="{html.escape(str(_("Previous step")))}"></button>'
        '<button type="button" class="km-walkthrough__step" data-km-step="1"'
        f' aria-label="{html.escape(str(_("Next step")))}"></button>'
        "</span>"
        '<button type="button" class="km-walkthrough__copy o-tooltip--left"'
        f' data-km-copy data-tooltip="{html.escape(str(_("Copy")))}"'
        f' aria-label="{html.escape(str(_("Copy the snippet")))}">'
        "</button>"
    )


def output() -> str:
    """Write the box a snippet's prints land in."""
    return (
        '<pre class="km-walkthrough__out" data-km-out'
        f' data-km-empty="{html.escape(str(_("Nothing printed yet")))}"'
        " hidden></pre>"
    )


def label(low: int, high: int) -> str:
    """Name a range of lines the way a warning prints it.

    :param low: The first line.
    :param high: The last line.
    :return: `line 6` or `lines 7-8` with an en dash.
    """
    if low == high:
        return f"line {low}"
    return f"lines {low}-{high}"


def visit_explanation(self: HTMLTranslator, node: nodes.Element) -> None:
    """Open one `lines` block's note.

    :param self: The HTML translator, whose body this appends to.
    :param node: The explanation node, carrying its index.
    """
    self.body.append(
        f'<div class="km-walkthrough__note" data-km-note="{node["index"]}">'
    )


def depart_explanation(self: HTMLTranslator, node: nodes.Element) -> None:
    """Close one `lines` block's note.

    :param self: The HTML translator, whose body this appends to.
    :param node: The explanation node (unused).
    """
    self.body.append("</div>")
