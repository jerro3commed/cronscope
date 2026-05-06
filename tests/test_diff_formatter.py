"""Tests for cronscope.diff_formatter."""

import pytest
from cronscope.diff_formatter import format_diff
from cronscope.differ import diff


def test_format_diff_returns_string():
    d = diff("* * * * *", "0 * * * *")
    result = format_diff(d)
    assert isinstance(result, str)


def test_format_diff_contains_both_expressions():
    d = diff("* * * * *", "0 * * * *")
    result = format_diff(d)
    assert "* * * * *" in result
    assert "0 * * * *" in result


def test_format_diff_identical_expressions():
    d = diff("0 9 * * 1", "0 9 * * 1")
    result = format_diff(d)
    assert "identical" in result.lower() or "no changes" in result.lower() or "unchanged" in result.lower()


def test_format_diff_changed_field_mentioned():
    d = diff("* * * * *", "0 * * * *")
    result = format_diff(d)
    # The minute field changed from * to 0
    assert "minute" in result.lower()


def test_format_diff_shows_left_and_right_values():
    d = diff("* * * * *", "0 * * * *")
    result = format_diff(d)
    assert "*" in result
    assert "0" in result


def test_format_diff_invalid_left_expression():
    d = diff("bad expr", "* * * * *")
    result = format_diff(d)
    assert "error" in result.lower() or "invalid" in result.lower()


def test_format_diff_invalid_right_expression():
    d = diff("* * * * *", "bad expr")
    result = format_diff(d)
    assert "error" in result.lower() or "invalid" in result.lower()


def test_format_diff_no_color_flag():
    d = diff("* * * * *", "0 * * * *")
    result_color = format_diff(d, color=True)
    result_plain = format_diff(d, color=False)
    # Plain text should not contain ANSI escape codes
    assert "\033[" not in result_plain


def test_format_diff_multiple_changed_fields():
    d = diff("* * * * *", "0 9 1 * *")
    result = format_diff(d)
    assert "minute" in result.lower()
    assert "hour" in result.lower()
