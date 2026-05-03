from __future__ import annotations

import re
from dataclasses import dataclass


_TAG_PATTERN = re.compile(r"<[^>]*>")
_COLOR_TAG_PATTERN = re.compile(r"""^<c=(?P<quote>["']?)(?P<color>#?[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?)(?P=quote)>$""")
_STYLE_TAGS = {"b", "u", "s", "em"}
_LINE_BREAK_TAGS = {"br", "br/"}


@dataclass(frozen=True)
class MarkupStyle:
    bold: bool = False
    underline: bool = False
    strikethrough: bool = False
    italic: bool = False
    color: str | None = None


@dataclass(frozen=True)
class MarkupSegment:
    text: str
    style: MarkupStyle


@dataclass(frozen=True)
class _OpenTag:
    name: str
    color: str | None = None


def parse_markup(text: str) -> list[MarkupSegment]:
    segments: list[MarkupSegment] = []
    open_tags: list[_OpenTag] = []
    cursor = 0

    for match in _TAG_PATTERN.finditer(text):
        literal = match.group(0)
        _append_segment(segments, text[cursor : match.start()], _style_from_open_tags(open_tags))

        tag = _parse_open_tag(literal)
        if _is_line_break_tag(literal):
            _append_segment(segments, "\n", _style_from_open_tags(open_tags))
        elif tag:
            _set_open_tag(open_tags, tag)
        elif _is_close_tag(literal):
            tag_name = literal[2:-1].strip().lower()
            if _has_open_tag(open_tags, tag_name):
                _close_tag(open_tags, tag_name)
            else:
                _append_segment(segments, literal, _style_from_open_tags(open_tags))
        else:
            _append_segment(segments, literal, _style_from_open_tags(open_tags))
        cursor = match.end()

    _append_segment(segments, text[cursor:], _style_from_open_tags(open_tags))
    return segments


def normalize_markup(text: str) -> str:
    """Return display markup with real newlines and merged repeated tags."""
    return _serialize_markup(_compact_segments(parse_markup(text)))


def _parse_open_tag(literal: str) -> _OpenTag | None:
    name = literal[1:-1].strip().lower()
    if name in _STYLE_TAGS:
        return _OpenTag(name)

    match = _COLOR_TAG_PATTERN.match(literal)
    if match:
        return _OpenTag("c", _normalize_color(match.group("color")))
    return None


def _is_line_break_tag(literal: str) -> bool:
    return literal[1:-1].strip().lower().replace(" ", "") in _LINE_BREAK_TAGS


def _is_close_tag(literal: str) -> bool:
    name = literal[2:-1].strip().lower() if literal.startswith("</") else ""
    return name in _STYLE_TAGS or name == "c"


def _has_open_tag(open_tags: list[_OpenTag], name: str) -> bool:
    return any(tag.name == name for tag in open_tags)


def _close_tag(open_tags: list[_OpenTag], name: str) -> None:
    for index in range(len(open_tags) - 1, -1, -1):
        if open_tags[index].name == name:
            del open_tags[index]
            return


def _set_open_tag(open_tags: list[_OpenTag], tag: _OpenTag) -> None:
    if tag.name == "c":
        _close_all_tags(open_tags, "c")
    elif tag.name in _STYLE_TAGS:
        _close_all_tags(open_tags, tag.name)
    open_tags.append(tag)


def _close_all_tags(open_tags: list[_OpenTag], name: str) -> None:
    open_tags[:] = [tag for tag in open_tags if tag.name != name]


def _style_from_open_tags(open_tags: list[_OpenTag]) -> MarkupStyle:
    color = next((tag.color for tag in reversed(open_tags) if tag.name == "c"), None)
    return MarkupStyle(
        bold=any(tag.name == "b" for tag in open_tags),
        underline=any(tag.name == "u" for tag in open_tags),
        strikethrough=any(tag.name == "s" for tag in open_tags),
        italic=any(tag.name == "em" for tag in open_tags),
        color=color,
    )


def _normalize_color(color: str) -> str:
    color = color.lstrip("#").lower()
    if len(color) == 3:
        color = "".join(character * 2 for character in color)
    return f"#{color}"


def _compact_segments(segments: list[MarkupSegment]) -> list[MarkupSegment]:
    compacted: list[MarkupSegment] = []
    for index, segment in enumerate(segments):
        if (
            segment.text
            and set(segment.text) <= {"\n"}
            and compacted
            and index + 1 < len(segments)
            and compacted[-1].style == segments[index + 1].style
            and compacted[-1].style != MarkupStyle()
        ):
            _append_segment(compacted, segment.text, compacted[-1].style)
            continue
        _append_segment(compacted, segment.text, segment.style)
    return compacted


def _serialize_markup(segments: list[MarkupSegment]) -> str:
    return "".join(_serialize_segment(segment) for segment in segments)


def _serialize_segment(segment: MarkupSegment) -> str:
    if segment.style == MarkupStyle():
        return segment.text

    opening_tags: list[str] = []
    closing_tags: list[str] = []
    if segment.style.color:
        opening_tags.append(f"<c={segment.style.color.lstrip('#')}>")
        closing_tags.append("</c>")
    if segment.style.bold:
        opening_tags.append("<b>")
        closing_tags.append("</b>")
    if segment.style.underline:
        opening_tags.append("<u>")
        closing_tags.append("</u>")
    if segment.style.strikethrough:
        opening_tags.append("<s>")
        closing_tags.append("</s>")
    if segment.style.italic:
        opening_tags.append("<em>")
        closing_tags.append("</em>")

    return "".join(opening_tags) + segment.text + "".join(reversed(closing_tags))


def _append_segment(segments: list[MarkupSegment], text: str, style: MarkupStyle) -> None:
    if not text:
        return
    if segments and segments[-1].style == style:
        previous = segments[-1]
        segments[-1] = MarkupSegment(previous.text + text, style)
        return
    segments.append(MarkupSegment(text, style))
