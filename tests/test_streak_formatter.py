"""Tests for cronscope.streak_formatter."""

from datetime import datetime

import pytest

from cronscope.streaker import StreakResult
from cronscope.streak_formatter import format_streak

_ANCHOR = datetime(2024, 1, 1)
_ANCHOR2 = datetime(2024, 1, 5)


def _valid_result(**kwargs) -> StreakResult:
    defaults = dict(
        expression="0 9 * * *",
        longest_streak=7,
        current_streak=3,
        streak_start=_ANCHOR,
        streak_end=_ANCHOR2,
        error=None,
    )
    defaults.update(kwargs)
    r = StreakResult(**defaults)
    r._days_checked = [_ANCHOR.date(), _ANCHOR2.date()]
    return r


def test_format_streak_returns_string():
    result = _valid_result()
    output = format_streak(result, color=False)
    assert isinstance(output, str)


def test_format_streak_contains_expression():
    result = _valid_result(expression="*/5 * * * *")
    output = format_streak(result, color=False)
    assert "*/5 * * * *" in output


def test_format_streak_shows_longest_streak():
    result = _valid_result(longest_streak=12)
    output = format_streak(result, color=False)
    assert "12" in output


def test_format_streak_shows_current_streak():
    result = _valid_result(current_streak=4)
    output = format_streak(result, color=False)
    assert "4" in output


def test_format_streak_shows_date_range():
    result = _valid_result(streak_start=_ANCHOR, streak_end=_ANCHOR2)
    output = format_streak(result, color=False)
    assert "2024-01-01" in output
    assert "2024-01-05" in output


def test_format_streak_error_shows_error_message():
    result = StreakResult(
        expression="bad expr",
        longest_streak=0,
        current_streak=0,
        streak_start=None,
        streak_end=None,
        error="Invalid cron field",
    )
    output = format_streak(result, color=False)
    assert "Error" in output
    assert "Invalid cron field" in output


def test_format_streak_error_no_date_range():
    result = StreakResult(
        expression="bad",
        longest_streak=0,
        current_streak=0,
        streak_start=None,
        streak_end=None,
        error="oops",
    )
    output = format_streak(result, color=False)
    assert "2024" not in output


def test_format_streak_shows_active_days_count():
    result = _valid_result()
    result._days_checked = [_ANCHOR.date()] * 5
    output = format_streak(result, color=False)
    assert "5" in output


def test_format_streak_with_color_returns_string():
    result = _valid_result()
    output = format_streak(result, color=True)
    assert isinstance(output, str)
    assert len(output) > 0
