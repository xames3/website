"""\
Explainer Block Grammar
=======================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 12 September, 2026
Last updated on: 01 October, 2026

The little block grammar the explainers carry in their bodies and the
readers for the options that go beside it.
"""

from __future__ import annotations

import re

from docutils.statemachine import StringList

BLOCK: re.Pattern[str] = re.compile(r"^\.\.[ \t]+([a-z][\w-]*)::[ \t]*(.*)$")
COMMENT: re.Pattern[str] = re.compile(r"^\.\.(?:[ \t]|$)")
OPTION: re.Pattern[str] = re.compile(r"^:([\w-]+):(?:[ \t]+(.*))?$")
RANGE: re.Pattern[str] = re.compile(r"^(\d+)(?:\s*[-\u2013]\s*(\d+))?$")


class chunk:
    """One `.. name:: argument` block pulled out of a directive's body.

    The stepping directives carry their own little block grammar,
    since docutils will not nest an unregistered directive inside
    another one. `split` hands back one of these per block it finds.
    """

    def __init__(
        self,
        name: str,
        argument: str,
        options: dict[str, str],
        body: StringList,
        offset: int,
    ) -> None:
        """Hold the parsed block.

        :param name: The block's name, as written after the `..`.
        :param argument: Whatever followed the `::` on the same line.
        :param options: The `:key: value` lines opening the body.
        :param body: The block's content, dedented.
        :param offset: Where the body starts in the document, for
            error reporting.
        """
        self.name = name
        self.argument = argument
        self.options = options
        self.body = body
        self.offset = offset

    def text(self) -> str:
        """Give the block's body back as one string.

        :return: The body, newline-joined.
        """
        return "\n".join(self.body)


def indentation(lines: list[str]) -> int:
    """Measure the common indent across a block's lines.

    :param lines: The lines to measure, blanks included.
    :return: The narrowest indent among the lines carrying text, or
        zero when none of them do.
    """
    widths = [len(_) - len(_.lstrip()) for _ in lines if _.strip()]
    return min(widths) if widths else 0


def extent(content: StringList, start: int) -> int:
    """Find where a block that opens on `start` ends.

    :param content: The directive's content.
    :param start: The line the block opens on.
    :return: The first line after it, which is the next one starting in
        column zero.
    """
    end = start + 1
    while end < len(content):
        line = content[end]
        if line.strip() and not line[:1].isspace():
            break
        end += 1
    return end


def split(
    content: StringList,
    offset: int,
    own: frozenset[str],
    options: dict[str, frozenset[str]] | None = None,
) -> list[chunk]:
    """Pull this grammar's blocks out of a directive's content.

    :param content: The directive's content.
    :param offset: The content's offset in the document.
    :param own: The block names belonging to this grammar.
    :param options: The option names each block takes. Only those
        blocks read options and only from `:name:` lines followed by a
        space or nothing, so prose opening with a role is left alone.
        A line indented under an option carries on its value and a
        blank line between two options does not end them; they run to
        the first line that is not one.
    :return: One `chunk` per block found, in the order written.
    :raises ValueError: For the first line belonging to no block, with
        its line number and its text.
    :raises KeyError: For an option its block does not take, or takes
        twice, with its line number, its name and the block's name.
    """
    found: list[chunk] = []
    index = 0
    while index < len(content):
        line = content[index]
        if not line.strip():
            index += 1
            continue
        match = BLOCK.match(line)
        if match is None or match.group(1) not in own:
            if match is None and COMMENT.match(line):
                index = extent(content, index)
                continue
            raise ValueError(offset + index + 1, line.strip())
        name = match.group(1)
        start = index + 1
        end = extent(content, index)
        raw = [content[_] for _ in range(start, end)]
        pad = indentation(raw)
        allowed = (options or {}).get(name)
        read: dict[str, str] = {}
        cursor = 0
        while cursor < len(raw) and not raw[cursor].strip():
            cursor += 1
        while allowed is not None and cursor < len(raw):
            ahead = cursor
            while ahead < len(raw) and not raw[ahead].strip():
                ahead += 1
            hit = OPTION.match(raw[ahead].strip()) if ahead < len(raw) else None
            if hit is None:
                break
            cursor = ahead
            key = hit.group(1)
            if key not in allowed or key in read:
                raise KeyError(offset + start + cursor + 1, key, name)
            depth = len(raw[cursor]) - len(raw[cursor].lstrip())
            value = [(hit.group(2) or "").strip()]
            cursor += 1
            while cursor < len(raw) and raw[cursor].strip():
                if len(raw[cursor]) - len(raw[cursor].lstrip()) <= depth:
                    break
                value.append(raw[cursor].strip())
                cursor += 1
            read[key] = "\n".join(_ for _ in value if _)
        body = StringList()
        for position in range(start + cursor, end):
            source, line_no = content.info(position)
            text = content[position]
            body.append(
                text[pad:] if text[:pad].strip() == "" else text.lstrip(),
                source,
                line_no or 0,
            )
        while len(body) and not body[0].strip():
            del body[0]
        while len(body) and not body[-1].strip():
            del body[-1]
        found.append(
            chunk(
                name,
                match.group(2).strip(),
                read,
                body,
                offset + start + cursor,
            )
        )
        index = end
    return found


def linerange(line: str) -> tuple[int, int] | None:
    """Read a `4` or a `4-9` line range off a block's argument.

    :param line: The argument, as written.
    :return: The range as a low/high pair, or `None` when the argument
        is not a pair of line numbers.
    """
    match = RANGE.match(line.strip())
    if match is None:
        return None
    low = int(match.group(1))
    high = int(match.group(2)) if match.group(2) else low
    return min(low, high), max(low, high)


def parse_list(value: str | None) -> list[str]:
    """Split a comma-separated option into its parts.

    :param value: The option's value, or `None` when unset.
    :return: The parts, trimmed, with the empties dropped.
    """
    return [_.strip() for _ in (value or "").split(",") if _.strip()]
