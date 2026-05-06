"""Tests for cronscope.merger and cronscope.merge_formatter."""

from datetime import datetime

import pytest

from cronscope.merger import merge, MergedSchedule
from cronscope.merge_formatter import format_merge

START = datetime(2024, 1, 15, 12, 0)


# ---------------------------------------------------------------------------
# merge()
# ---------------------------------------------------------------------------

def test_merge_returns_merged_schedule():
    result = merge(["* * * * *", "0 9 * * *"], count=3, start=START)
    assert isinstance(result, MergedSchedule)


def test_merge_valid_expressions_stored():
    result = merge(["* * * * *", "0 9 * * *"], count=3, start=START)
    assert "* * * * *" in result.valid_expressions()
    assert "0 9 * * *" in result.valid_expressions()


def test_merge_invalid_expression_recorded_in_errors():
    result = merge(["* * * * *", "not_a_cron"], count=3, start=START)
    assert "not_a_cron" in result.errors
    assert result.has_errors()


def test_merge_invalid_expression_not_in_valid():
    result = merge(["* * * * *", "bad expr"], count=3, start=START)
    assert "bad expr" not in result.valid_expressions()
    assert "bad expr" in result.invalid_expressions()


def test_merge_next_runs_sorted_chronologically():
    result = merge(["0 10 * * *", "0 8 * * *"], count=4, start=START)
    datetimes = [dt for dt, _ in result.next_runs]
    assert datetimes == sorted(datetimes)


def test_merge_respects_count():
    result = merge(["* * * * *", "* * * * *"], count=5, start=START)
    assert len(result.next_runs) <= 5


def test_merge_all_invalid_gives_empty_runs():
    result = merge(["bad1", "bad2"], count=5, start=START)
    assert result.next_runs == []
    assert not result.valid_expressions()


def test_merge_has_errors_false_when_all_valid():
    result = merge(["* * * * *"], count=3, start=START)
    assert not result.has_errors()


# ---------------------------------------------------------------------------
# format_merge()
# ---------------------------------------------------------------------------

def test_format_merge_returns_string():
    result = merge(["* * * * *"], count=3, start=START)
    output = format_merge(result, color=False)
    assert isinstance(output, str)


def test_format_merge_contains_expression():
    result = merge(["0 6 * * *"], count=2, start=START)
    output = format_merge(result, color=False)
    assert "0 6 * * *" in output


def test_format_merge_shows_invalid_section():
    result = merge(["* * * * *", "garbage"], count=2, start=START)
    output = format_merge(result, color=False)
    assert "Invalid expressions" in output
    assert "garbage" in output


def test_format_merge_shows_run_datetimes():
    result = merge(["0 9 * * *"], count=2, start=START)
    output = format_merge(result, color=False)
    assert "2024-01-" in output


def test_format_merge_no_runs_message_when_empty():
    result = merge(["bad"], count=3, start=START)
    output = format_merge(result, color=False)
    assert "No upcoming runs found" in output


def test_format_merge_with_color_does_not_crash():
    result = merge(["* * * * *"], count=2, start=START)
    output = format_merge(result, color=True)
    assert len(output) > 0
