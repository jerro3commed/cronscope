"""Tests for cronscope.calendar_view and cronscope.calendar_formatter."""

import calendar
from datetime import datetime

import pytest

from cronscope.calendar_view import CalendarMonth, build_calendar
from cronscope.calendar_formatter import format_calendar


def test_build_calendar_returns_calendar_month():
    result = build_calendar("0 9 * * *", 2024, 6)
    assert isinstance(result, CalendarMonth)


def test_build_calendar_invalid_expression_sets_error():
    result = build_calendar("invalid", 2024, 6)
    assert result.error is not None
    assert not result


def test_build_calendar_valid_expression_no_error():
    result = build_calendar("0 9 * * *", 2024, 6)
    assert result.error is None
    assert bool(result)


def test_build_calendar_daily_fires_every_day():
    result = build_calendar("0 9 * * *", 2024, 6)
    _, days_in_month = calendar.monthrange(2024, 6)
    assert len(result.fire_days) == days_in_month


def test_build_calendar_daily_one_run_per_day():
    result = build_calendar("0 9 * * *", 2024, 6)
    for count in result.fire_days.values():
        assert count == 1


def test_build_calendar_every_minute_many_runs():
    result = build_calendar("* * * * *", 2024, 1)
    assert result.total_runs == 31 * 24 * 60


def test_build_calendar_specific_day_of_month():
    result = build_calendar("0 0 15 * *", 2024, 6)
    assert 15 in result.fire_days
    assert len(result.fire_days) == 1


def test_build_calendar_month_name():
    result = build_calendar("0 9 * * *", 2024, 3)
    assert result.month_name == "March"


def test_build_calendar_total_runs_matches_sum():
    result = build_calendar("0 */6 * * *", 2024, 6)
    assert result.total_runs == sum(result.fire_days.values())


def test_format_calendar_returns_string():
    result = build_calendar("0 9 * * *", 2024, 6)
    output = format_calendar(result, color=False)
    assert isinstance(output, str)


def test_format_calendar_contains_expression():
    result = build_calendar("0 9 * * *", 2024, 6)
    output = format_calendar(result, color=False)
    assert "0 9 * * *" in output


def test_format_calendar_contains_month_name():
    result = build_calendar("0 9 * * *", 2024, 6)
    output = format_calendar(result, color=False)
    assert "June" in output


def test_format_calendar_shows_total_runs():
    result = build_calendar("0 9 * * *", 2024, 6)
    output = format_calendar(result, color=False)
    assert "Total runs" in output


def test_format_calendar_error_shows_error_message():
    result = build_calendar("bad expr", 2024, 6)
    output = format_calendar(result, color=False)
    assert "Error" in output


def test_format_calendar_marks_fire_days_with_asterisk():
    result = build_calendar("0 0 15 * *", 2024, 6)
    output = format_calendar(result, color=False)
    assert "15*" in output
