"""Tests for cronscope.matcher."""

from datetime import datetime

import pytest

from cronscope.matcher import FieldMatchResult, MatchResult, match


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _dt(minute=0, hour=12, day=1, month=1, weekday=0):
    """Build a datetime that lands on the requested cron-field values.

    weekday: 0=Sunday in cron; Python's Monday=0, so we map accordingly.
    """
    # Find a date in January 2024 whose weekday matches the requested cron weekday.
    # cron 0=Sunday → Python isoweekday 7; cron 1=Monday → Python isoweekday 1, etc.
    from datetime import date, timedelta
    base = date(2024, month, day)
    return datetime(base.year, base.month, base.day, hour, minute)


# ---------------------------------------------------------------------------
# basic return types
# ---------------------------------------------------------------------------

def test_match_returns_match_result():
    result = match("* * * * *", datetime(2024, 1, 1, 12, 0))
    assert isinstance(result, MatchResult)


def test_match_wildcard_always_matches():
    result = match("* * * * *", datetime(2024, 6, 15, 9, 37))
    assert result.matched is True


def test_match_produces_five_fields():
    result = match("* * * * *", datetime(2024, 1, 1, 0, 0))
    assert len(result.fields) == 5


def test_field_names_are_correct():
    result = match("* * * * *", datetime(2024, 1, 1, 0, 0))
    names = [f.name for f in result.fields]
    assert names == ["minute", "hour", "day", "month", "weekday"]


# ---------------------------------------------------------------------------
# specific-value matching
# ---------------------------------------------------------------------------

def test_specific_minute_matches():
    result = match("30 * * * *", datetime(2024, 1, 1, 12, 30))
    assert result.matched is True


def test_specific_minute_does_not_match():
    result = match("30 * * * *", datetime(2024, 1, 1, 12, 15))
    assert result.matched is False


def test_specific_hour_matches():
    result = match("0 9 * * *", datetime(2024, 1, 1, 9, 0))
    assert result.matched is True


def test_step_expression_matches():
    result = match("*/15 * * * *", datetime(2024, 1, 1, 12, 45))
    assert result.matched is True


def test_step_expression_does_not_match():
    result = match("*/15 * * * *", datetime(2024, 1, 1, 12, 7))
    assert result.matched is False


def test_range_expression_matches():
    result = match("0 9-17 * * *", datetime(2024, 1, 1, 14, 0))
    assert result.matched is True


def test_comma_list_matches():
    result = match("0 8,12,18 * * *", datetime(2024, 1, 1, 12, 0))
    assert result.matched is True


# ---------------------------------------------------------------------------
# failed_fields
# ---------------------------------------------------------------------------

def test_failed_fields_empty_when_all_match():
    result = match("* * * * *", datetime(2024, 1, 1, 0, 0))
    assert result.failed_fields == []


def test_failed_fields_reports_mismatched_field():
    result = match("30 * * * *", datetime(2024, 1, 1, 12, 0))
    assert len(result.failed_fields) == 1
    assert result.failed_fields[0].name == "minute"


# ---------------------------------------------------------------------------
# invalid expression
# ---------------------------------------------------------------------------

def test_invalid_expression_sets_error():
    result = match("not a cron", datetime(2024, 1, 1, 0, 0))
    assert result.error is not None
    assert result.matched is False


def test_invalid_expression_bool_is_false():
    result = match("99 99 99 99 99", datetime(2024, 1, 1, 0, 0))
    assert bool(result) is False
