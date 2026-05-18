"""Tests for cronscope.tracer."""

from datetime import datetime
import pytest

from cronscope.tracer import trace, TraceResult, FieldTrace


_EVERY_MINUTE = "* * * * *"
_DAILY_NOON = "0 12 * * *"
_WEEKDAY_ONLY = "0 9 * * 1-5"


def _dt(minute=0, hour=12, day=1, month=6, year=2024, weekday_iso=None):
    """Helper — weekday_iso ignored, just build the datetime."""
    return datetime(year, month, day, hour, minute)


def test_trace_returns_trace_result():
    result = trace(_EVERY_MINUTE, _dt())
    assert isinstance(result, TraceResult)


def test_trace_wildcard_always_matches():
    result = trace(_EVERY_MINUTE, _dt(minute=37, hour=3))
    assert result.matched is True


def test_trace_wildcard_has_no_error():
    result = trace(_EVERY_MINUTE, _dt())
    assert result.error is None
    assert bool(result) is True


def test_trace_produces_five_fields():
    result = trace(_EVERY_MINUTE, _dt())
    assert len(result.fields) == 5


def test_trace_field_names_are_correct():
    result = trace(_EVERY_MINUTE, _dt())
    names = [f.name for f in result.fields]
    assert names == ["minute", "hour", "day", "month", "weekday"]


def test_trace_daily_noon_matches_at_noon():
    dt = datetime(2024, 6, 1, 12, 0)  # Saturday — weekday 6
    result = trace(_DAILY_NOON, dt)
    assert result.matched is True


def test_trace_daily_noon_does_not_match_at_1pm():
    dt = datetime(2024, 6, 1, 13, 0)
    result = trace(_DAILY_NOON, dt)
    assert result.matched is False


def test_trace_failing_field_is_marked():
    dt = datetime(2024, 6, 1, 13, 0)  # hour 13 != 12
    result = trace(_DAILY_NOON, dt)
    hour_field = next(f for f in result.fields if f.name == "hour")
    assert hour_field.matched is False


def test_trace_passing_fields_are_marked():
    dt = datetime(2024, 6, 1, 12, 0)
    result = trace(_DAILY_NOON, dt)
    minute_field = next(f for f in result.fields if f.name == "minute")
    assert minute_field.matched is True


def test_trace_invalid_expression_sets_error():
    result = trace("not a cron", _dt())
    assert result.error is not None
    assert bool(result) is False


def test_trace_invalid_expression_matched_is_false():
    result = trace("60 * * * *", _dt())
    assert result.matched is False


def test_trace_field_carries_pattern():
    dt = datetime(2024, 6, 1, 12, 0)
    result = trace(_DAILY_NOON, dt)
    hour_field = next(f for f in result.fields if f.name == "hour")
    assert hour_field.pattern == "12"


def test_trace_field_carries_dt_value():
    dt = datetime(2024, 6, 1, 12, 0)
    result = trace(_DAILY_NOON, dt)
    hour_field = next(f for f in result.fields if f.name == "hour")
    assert hour_field.value == 12


def test_trace_wildcard_reason_mentions_wildcard():
    result = trace(_EVERY_MINUTE, _dt())
    minute_field = next(f for f in result.fields if f.name == "minute")
    assert "wildcard" in minute_field.reason.lower()
