from __future__ import annotations

from snaptranslate.presentation.markup import MarkupSegment, MarkupStyle, normalize_markup, parse_markup


def test_parse_plain_text() -> None:
    assert parse_markup("plain text") == [MarkupSegment("plain text", MarkupStyle())]


def test_parse_basic_styles() -> None:
    assert parse_markup("<b>bold</b> <u>under</u> <s>strike</s> <em>italic</em>") == [
        MarkupSegment("bold", MarkupStyle(bold=True)),
        MarkupSegment(" ", MarkupStyle()),
        MarkupSegment("under", MarkupStyle(underline=True)),
        MarkupSegment(" ", MarkupStyle()),
        MarkupSegment("strike", MarkupStyle(strikethrough=True)),
        MarkupSegment(" ", MarkupStyle()),
        MarkupSegment("italic", MarkupStyle(italic=True)),
    ]


def test_parse_color_markup() -> None:
    assert parse_markup('<c="ffffff">white</c> <c="#fc0">yellow</c>') == [
        MarkupSegment("white", MarkupStyle(color="#ffffff")),
        MarkupSegment(" ", MarkupStyle()),
        MarkupSegment("yellow", MarkupStyle(color="#ffcc00")),
    ]


def test_parse_nested_styles() -> None:
    assert parse_markup('<b>bold <c="ffcc00"><u><em>all</em></u></c></b>') == [
        MarkupSegment("bold ", MarkupStyle(bold=True)),
        MarkupSegment(
            "all",
            MarkupStyle(bold=True, underline=True, italic=True, color="#ffcc00"),
        ),
    ]


def test_parse_line_break_markup() -> None:
    assert parse_markup("line1<br>line2<br/>line3<br />line4") == [
        MarkupSegment("line1\nline2\nline3\nline4", MarkupStyle()),
    ]


def test_parse_line_break_markup_inside_style() -> None:
    assert parse_markup("<b>line1<br>line2</b>") == [
        MarkupSegment("line1\nline2", MarkupStyle(bold=True)),
    ]


def test_normalize_markup_uses_newlines_and_merges_repeated_tags() -> None:
    assert (
        normalize_markup("<c=ff5a5a>[2103]</c><br><c=#ff5a5a>[2103]</c>")
        == "<c=ff5a5a>[2103]\n[2103]</c>"
    )


def test_normalize_markup_removes_empty_tags() -> None:
    assert normalize_markup("<c=55ccff></c> <c=ffffff>test</c>") == " <c=ffffff>test</c>"


def test_normalize_markup_keeps_unknown_colors_in_color_tag_form() -> None:
    assert normalize_markup("<c=123456>test</c> plain") == "<c=123456>test</c> plain"


def test_unknown_and_invalid_tags_are_kept_as_text() -> None:
    assert parse_markup('<x>tag</x> <c="zzzzzz">bad</c>') == [
        MarkupSegment('<x>tag</x> <c="zzzzzz">bad</c>', MarkupStyle()),
    ]


def test_unclosed_tag_applies_to_end() -> None:
    assert parse_markup("start <s>strike") == [
        MarkupSegment("start ", MarkupStyle()),
        MarkupSegment("strike", MarkupStyle(strikethrough=True)),
    ]
