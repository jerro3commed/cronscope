"""Tests for cronscope.differ and cronscope.diff_formatter."""

import pytest
from cronscope.differ import diff, FieldDiff, CronDiff
from cronscope.diff_formatter import format_diff


def test_identical_expressions_are_identical():
    result = diff("* * * * *", "* * * * *")
    assert result.is_identical
    assert len(result.changed_fields) == 0


def test_single_field_change_detected():
    result = diff("0 * * * *", "5 * * * *")
    assert not result.is_identical
    changed = result.changed_fields
    assert len(changed) == 1
    assert changed[0].name == "minute"
    assert changed[0].left == "0"
    assert changed[0].right == "5"


def test_multiple_fields_changed():
    result = diff("0 6 * * 1", "30 12 * * 5")
    names = {f.name for f in result.changed_fields}
    assert "minute" in names
    assert "hour" in names
    assert "day_of_week" in names
    assert len(result.changed_fields) == 3


def test_unchanged_fields_are_not_in_changed_fields():
    result = diff("0 6 1 * *", "0 6 15 * *")
    unchanged = [f for f in result.fields if not f.changed]
    unchanged_names = {f.name for f in unchanged}
    assert "minute" in unchanged_names
    assert "hour" in unchanged_names


def test_invalid_left_expression_sets_error():
    result = diff("invalid", "* * * * *")
    assert result.left_error is not None
    assert result.has_errors


def test_invalid_right_expression_sets_error():
    result = diff("* * * * *", "bad expr")
    assert result.right_error is not None
    assert result.has_errors


def test_both_invalid_expressions():
    result = diff("nope", "also nope")
    assert result.left_error is not None
    assert result.right_error is not None


def test_format_diff_identical(capsys):
    result = diff("* * * * *", "* * * * *")
    output = format_diff(result, color=False)
    assert "identical" in output.lower()


def test_format_diff_shows_changed_field():
    result = diff("0 * * * *", "5 * * * *")
    output = format_diff(result, color=False)
    assert "minute" in output
    assert "changed" in output


def test_format_diff_shows_error_on_invalid():
    result = diff("bad", "* * * * *")
    output = format_diff(result, color=False)
    assert "Error" in output


def test_format_diff_no_color_has_no_ansi():
    result = diff("0 6 * * 1", "0 12 * * 1")
    output = format_diff(result, color=False)
    assert "\x1b[" not in output


def test_format_diff_with_color_has_ansi():
    result = diff("0 6 * * 1", "0 12 * * 1")
    output = format_diff(result, color=True)
    assert "\x1b[" in output
