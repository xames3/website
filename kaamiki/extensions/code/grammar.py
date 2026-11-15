"""\
Walkthrough Block Grammar
=========================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 12 September 2026
Last updated on: 15 November 2026

The grammar of the blocks in the body of a walkthrough, and the readers
for the options of the blocks.
"""

import re
import typing as t

from docutils.statemachine import StringList

BLOCK: t.Final[re.Pattern[str]] = re.compile(
    r"^\.\.[ \t]+([a-z][\w-]*)::[ \t]*(.*)$"
)
COMMENT: t.Final[re.Pattern[str]] = re.compile(r"^\.\.(?:[ \t]|$)")
OPTION_LINE: t.Final[re.Pattern[str]] = re.compile(
    r"^:([\w-]+):(?:[ \t]+(.*))?$"
)
RANGE: t.Final[re.Pattern[str]] = re.compile(
    r"^([0-9]{1,15})(?:\s*[-\u2013]\s*([0-9]{1,15}))?$"
)


class OptionError(Exception):
    """An option that a block does not take, or takes two times."""

    def __init__(self, line: int, key: str, block: str) -> None:
        """Keep what the message tells.

        :param line: The line of the document with the option.
        :param key: The name of the option.
        :param block: The name of the block.
        """
        super().__init__(line, key, block)
        self.line = line
        self.key = key
        self.block = block


class StrayError(Exception):
    """A line that is not in a block."""

    def __init__(self, line: int, text: str) -> None:
        """Keep what the message tells.

        :param line: The line of the document.
        :param text: The text on the line.
        """
        super().__init__(line, text)
        self.line = line
        self.text = text


class chunk:
    """One `.. name:: argument` block, as `split` gives it."""

    def __init__(
        self,
        name: str,
        argument: str,
        options: dict[str, str],
        body: StringList,
        offset: int,
    ) -> None:
        """Keep the parsed block.

        :param name: The name of the block, after the `..`.
        :param argument: The text after the `::` on the same line.
        :param options: The `:key: value` lines at the start of the body.
        :param body: The content of the block, without its indent.
        :param offset: Where the body starts in the document, for the error
            messages.
        """
        self.name = name
        self.argument = argument
        self.options = options
        self.body = body
        self.offset = offset

    def text(self) -> str:
        """Give the body of the block as one string.

        :return: The lines of the body, joined with newlines.
        """
        return "\n".join(self.body)


def indentation(lines: list[str]) -> int:
    """Measure the indent that the lines of a block share.

    :param lines: The lines to measure, blank lines too.
    :return: The smallest indent of the lines with text, or zero when no line
        has text.
    """
    widths = [len(_) - len(_.lstrip()) for _ in lines if _.strip()]
    return min(widths) if widths else 0


def extent(content: StringList, start: int) -> int:
    """Find where a block that opens on `start` ends.

    :param content: The content of the directive.
    :param start: The line where the block opens.
    :return: The first line after the block, which is the next line that starts
        in column zero.
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
    :return: The first line from `index` with text, or the number of lines when
        there is none.
    """
    while index < len(lines) and not lines[index].strip():
        index += 1
    return index


def gather(
    content: StringList, first: int, last: int, pad: int = 0
) -> StringList:
    """Copy lines from the content, and keep where each line came from.

    :param content: The content of the directive.
    :param first: The first line to copy.
    :param last: The line after the last line.
    :param pad: The indent to remove from each line.
    :return: The lines, without blank lines at the two ends.
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
    """Read the `:name: value` lines at the start of a block.

    :param raw: The lines of the block, after the line where it opens.
    :param allowed: The names of the options that the block takes, or `None` for
        a block without options.
    :param line: The line of the document where `raw` starts.
    :param name: The name of the block.
    :return: The options, and the line in `raw` where the body starts. A line
        indented below an option continues its value. A blank line between two
        options does not end the options.
    :raises OptionError: For an option that the block does not take, or takes
        two times, with its line, its name and the name of the block.
    """
    options: dict[str, str] = {}
    cursor = blanks(raw, 0)
    while allowed is not None:
        ahead = blanks(raw, cursor)
        hit = (
            OPTION_LINE.match(raw[ahead].strip()) if ahead < len(raw) else None
        )
        if hit is None:
            break
        key = hit.group(1)
        if key not in allowed or key in options:
            raise OptionError(line + ahead + 1, key, name)
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

    :param content: The content of the directive.
    :param index: The line where the block opens.
    :param offset: The offset of the content in the document.
    :param match: The line, matched against `BLOCK`.
    :param allowed: The names of the options that the block takes.
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
    """Read the prose before the next block.

    :param content: The content of the directive.
    :param index: The line where the prose starts.
    :param offset: The offset of the content in the document.
    :param own: The names of the blocks of this grammar.
    :return: The prose as a chunk without a name, and the line after it.
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
    """Take the blocks of this grammar from the content of a directive.

    :param content: The content of the directive.
    :param offset: The offset of the content in the document.
    :param own: The names of the blocks of this grammar.
    :param options: The names of the options that each block takes. Only these
        blocks read options, from the lines directly below the line where they
        open.
    :param loose: Keep the prose between blocks as chunks without a name, and do
        not raise an error.
    :return: One `chunk` for each block, in the sequence written.
    :raises StrayError: For the first line that is not in a block, with its line
        and its text. Not with `loose`.
    :raises OptionError: For an option that its block does not take, or takes
        two times, with its line, its name and the name of the block.
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
            raise StrayError(offset + index + 1, line.strip())
        index = blanks(content, end)
    return found


def linerange(line: str) -> tuple[int, int] | None:
    """Read a line range, as `4` or `4-9`, from the argument of a block.

    :param line: The argument, as written.
    :return: The first and the last line, or `None` when the argument is not
        line numbers.
    """
    match = RANGE.fullmatch(line.strip())
    if match is None:
        return None
    low = int(match.group(1))
    high = int(match.group(2)) if match.group(2) else low
    return low, high
