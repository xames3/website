"""\
Explainer Block Grammar
=======================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 12 September 2026
Last updated on: 15 October 2026

The block grammar the explainers carry in their bodies and the readers
for the options beside it.
"""

import re

from docutils.statemachine import StringList

BLOCK: re.Pattern[str] = re.compile(r"^\.\.[ \t]+([a-z][\w-]*)::[ \t]*(.*)$")
COMMENT: re.Pattern[str] = re.compile(r"^\.\.(?:[ \t]|$)")
OPTION: re.Pattern[str] = re.compile(r"^:([\w-]+):(?:[ \t]+(.*))?$")
RANGE: re.Pattern[str] = re.compile(r"^(\d+)(?:\s*[-\u2013]\s*(\d+))?$")


class chunk:
    """One `.. name:: argument` block pulled out of a directive's body.

    `docutils` won't nest an unregistered directive inside another, so
    the walkthrough carries a little block grammar of its own. `split`
    returns one of these per block.
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
    :return: The narrowest indent among the lines carrying text or
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


def blanks(lines: list[str] | StringList, index: int) -> int:
    """Skip the blank lines.

    :param lines: The lines to look through.
    :param index: Where to start.
    :return: The first line from `index` with text on it or the number
        of lines when there isn't one.
    """
    while index < len(lines) and not lines[index].strip():
        index += 1
    return index


def gather(
    content: StringList, first: int, last: int, pad: int = 0
) -> StringList:
    """Copy lines out of the content, each one still knowing where it
    came from.

    :param content: The directive's content.
    :param first: The first line to copy.
    :param last: The line after the last one.
    :param pad: How much indent to take off a line.
    :return: The lines, without any blank ones at either end.
    """
    body = StringList()
    for position in range(first, last):
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
    return body


def read_options(
    raw: list[str], allowed: frozenset[str] | None, line: int, name: str
) -> tuple[dict[str, str], int]:
    """Read the `:name: value` lines a block opens with.

    A line indented under an option carries on its value and a blank
    line between two options doesn't end them. They run to the first
    line that isn't one.

    :param raw: The block's lines, after the one it opens on.
    :param allowed: The option names the block takes or `None` for a
        block that takes none.
    :param line: The document line `raw` starts on.
    :param name: The block's name.
    :return: The options and the line in `raw` the body starts on.
    :raises KeyError: For an option the block doesn't take or takes
        twice, with its line number, its name and the block's name.
    """
    options: dict[str, str] = {}
    cursor = blanks(raw, 0)
    while allowed is not None:
        ahead = blanks(raw, cursor)
        hit = OPTION.match(raw[ahead].strip()) if ahead < len(raw) else None
        if hit is None:
            break
        key = hit.group(1)
        if key not in allowed or key in options:
            raise KeyError(line + ahead + 1, key, name)
        depth = len(raw[ahead]) - len(raw[ahead].lstrip())
        value = [(hit.group(2) or "").strip()]
        cursor = ahead + 1
        while cursor < len(raw) and raw[cursor].strip():
            if len(raw[cursor]) - len(raw[cursor].lstrip()) <= depth:
                break
            value.append(raw[cursor].strip())
            cursor += 1
        options[key] = "\n".join(_ for _ in value if _)
    return options, cursor


def read_block(
    content: StringList,
    index: int,
    offset: int,
    match: re.Match[str],
    allowed: frozenset[str] | None,
) -> tuple[chunk, int]:
    """Read the block that opens on a line.

    :param content: The directive's content.
    :param index: The line the block opens on.
    :param offset: The content's offset in the document.
    :param match: The line, matched against `BLOCK`.
    :param allowed: The option names the block takes.
    :return: The block and the line after it.
    """
    start = index + 1
    end = extent(content, index)
    raw = [content[_] for _ in range(start, end)]
    options, cursor = read_options(raw, allowed, offset + start, match.group(1))
    body = gather(content, start + cursor, end, indentation(raw))
    block = chunk(
        match.group(1),
        match.group(2).strip(),
        options,
        body,
        offset + start + cursor,
    )
    return block, end


def read_prose(
    content: StringList, index: int, offset: int, own: frozenset[str]
) -> tuple[chunk, int]:
    """Read the prose that runs up to the next block.

    :param content: The directive's content.
    :param index: The line the prose starts on.
    :param offset: The content's offset in the document.
    :param own: The block names belonging to this grammar.
    :return: The prose as a nameless chunk and the line after it.
    """
    end = index + 1
    while end < len(content):
        opens = BLOCK.match(content[end])
        if opens is not None and opens.group(1) in own:
            break
        end += 1
    return chunk("", "", {}, gather(content, index, end), offset + index), end


def split(
    content: StringList,
    offset: int,
    own: frozenset[str],
    options: dict[str, frozenset[str]],
    *,
    loose: bool = False,
) -> list[chunk]:
    """Pull this grammar's blocks out of a directive's content.

    Only the blocks in `options` read options, from the lines right
    under the one they open on.

    :param content: The directive's content.
    :param offset: The content's offset in the document.
    :param own: The block names belonging to this grammar.
    :param options: The option names each block takes.
    :param loose: Keep the prose between blocks as nameless chunks
        instead of raising.
    :return: One `chunk` per block found, in the order written.
    :raises ValueError: For the first line belonging to no block, with
        its line number and its text. Never raised when `loose`.
    :raises KeyError: For an option its block doesn't take or takes
        twice, with its line number, its name and the block's name.
    """
    found: list[chunk] = []
    index = blanks(content, 0)
    while index < len(content):
        line = content[index]
        match = BLOCK.match(line)
        if match is not None and match.group(1) in own:
            block, end = read_block(
                content, index, offset, match, options.get(match.group(1))
            )
            found.append(block)
        elif match is None and COMMENT.match(line):
            end = extent(content, index)
        elif loose:
            block, end = read_prose(content, index, offset, own)
            found.append(block)
        else:
            raise ValueError(offset + index + 1, line.strip())
        index = blanks(content, end)
    return found


def linerange(line: str) -> tuple[int, int] | None:
    """Read a `4` or a `4-9` line range off a block's argument.

    :param line: The argument, as written.
    :return: The range as a low/high pair or `None` when the argument
        isn't a pair of line numbers.
    """
    match = RANGE.match(line.strip())
    if match is None:
        return None
    low = int(match.group(1))
    high = int(match.group(2)) if match.group(2) else low
    return min(low, high), max(low, high)
