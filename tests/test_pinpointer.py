"""Tests for cronscope.pinpointer."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from cronscope.pinpointer import PinpointResult, pinpoint


def _dt(year=2024, month=6, day=15, hour=12, minute=0):
    return datetime(year, month, day, hour, minute)


def test_pinpoint_returns_pinpoint_result():
    result = pinpoint("* * * * *", target=_dt())
    assert isinstance(result, PinpointResult)


def test_pinpoint_valid_expression_no_error():
    result = pinpoint("* * * * *", target=_dt())
    assert result.error is None
    assert bool(result) is True


def test_pinpoint_invalid_expression_sets_error():
    result = pinpoint("invalid", target=_dt())
    assert result.error is not None
    assert bool(result) is False


def test_pinpoint_stores_expression():
    result = pinpoint("0 9 * * *", target=_dt())
    assert result.expression == "0 9 * * *"


def test_pinpoint_stores_target():
    target = _dt(hour=10, minute=30)
    result = pinpoint("* * * * *", target=target)
    assert result.target == target


def test_pinpoint_every_minute_next_run_is_same_or_later():
    target = _dt(hour=12, minute=0)
    result = pinpoint("* * * * *", target=target)
    assert result.next_run is not None
    assert result.next_run >= target


def test_pinpoint_every_minute_delta_is_non_negative():
    result = pinpoint("* * * * *", target=_dt())
    assert result.delta_seconds is not None
    assert result.delta_seconds >= 0


def test_pinpoint_daily_at_noon_next_run_is_noon():
    # target is before noon
    target = _dt(hour=8, minute=0)
    result = pinpoint("0 12 * * *", target=target)
    assert result.next_run is not None
    assert result.next_run.hour == 12
    assert result.next_run.minute == 0


def test_pinpoint_has_next_true_when_next_run_found():
    result = pinpoint("* * * * *", target=_dt())
    assert result.has_next is True


def test_pinpoint_has_previous_false_for_invalid():
    result = pinpoint("bad expr", target=_dt())
    assert result.has_previous is False


def test_pinpoint_delta_minutes_is_none_for_invalid():
    result = pinpoint("bad expr", target=_dt())
    assert result.delta_minutes is None


def test_pinpoint_delta_minutes_non_negative_for_valid():
    result = pinpoint("* * * * *", target=_dt())
    assert result.delta_minutes is not None
    assert result.delta_minutes >= 0


def test_pinpoint_previous_run_is_before_target():
    target = _dt(hour=14, minute=30)
    result = pinpoint("* * * * *", target=target)
    if result.previous_run is not None:
        assert result.previous_run < target


def test_pinpoint_default_target_is_used_when_none():
    # Should not raise; just verify it returns a result
    result = pinpoint("* * * * *")
    assert isinstance(result, PinpointResult)


def test_pinpoint_next_run_none_for_invalid():
    result = pinpoint("not-valid", target=_dt())
    assert result.next_run is None
