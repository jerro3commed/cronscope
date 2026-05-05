"""Tests for cronscope.formatter module."""

from datetime import datetime
from cronscope.formatter import (
    _c,
    format_next_runs,
    format_validation_error,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_RESET,
)


SAMPLE_RUNS = [
    datetime(2024, 1, 15, 9, 0),
    datetime(2024, 1, 15, 9, 15),
    datetime(2024, 1, 15, 9, 30),
]


def test_c_with_color():
    result = _c("hello", COLOR_GREEN, use_color=True)
    assert COLOR_GREEN in result
    assert COLOR_RESET in result
    assert "hello" in result


def test_c_without_color():
    result = _c("hello", COLOR_GREEN, use_color=False)
    assert result == "hello"
    assert COLOR_GREEN not in result


def test_format_next_runs_contains_expression():
    result = format_next_runs("*/15 * * * *", SAMPLE_RUNS, use_color=False)
    assert "*/15 * * * *" in result


def test_format_next_runs_contains_dates():
    result = format_next_runs("*/15 * * * *", SAMPLE_RUNS, use_color=False)
    assert "2024-01-15 09:00" in result
    assert "2024-01-15 09:15" in result


def test_format_next_runs_count_label():
    result = format_next_runs("*/15 * * * *", SAMPLE_RUNS, use_color=False)
    assert "Next 3 run(s)" in result


def test_format_next_runs_with_explanation():
    result = format_next_runs(
        "*/15 * * * *", SAMPLE_RUNS,
        use_color=False,
        explanation="Runs every 15 minute(s) (every value)."
    )
    assert "every 15 minute" in result


def test_format_next_runs_no_explanation():
    result = format_next_runs("* * * * *", SAMPLE_RUNS, use_color=False)
    assert isinstance(result, str)


def test_format_validation_error_contains_expression():
    result = format_validation_error("bad expr", "Unknown field", use_color=False)
    assert "bad expr" in result


def test_format_validation_error_contains_error_message():
    result = format_validation_error("bad expr", "Unknown field", use_color=False)
    assert "Unknown field" in result


def test_format_validation_error_no_color():
    result = format_validation_error("bad", "oops", use_color=False)
    assert COLOR_RED not in result
