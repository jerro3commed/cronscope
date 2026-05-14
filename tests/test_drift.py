"""Tests for cronscope.drift."""

from datetime import datetime, timedelta

import pytest

from cronscope.drift import DriftResult, analyze_drift

START = datetime(2024, 1, 1, 0, 0, 0)


def test_analyze_drift_returns_drift_result():
    result = analyze_drift("* * * * *", target_minutes=1, count=5, start=START)
    assert isinstance(result, DriftResult)


def test_analyze_drift_every_minute_is_exact():
    result = analyze_drift("* * * * *", target_minutes=1, count=10, start=START)
    assert bool(result) is True
    assert result.is_exact is True


def test_analyze_drift_every_minute_zero_drift():
    result = analyze_drift("* * * * *", target_minutes=1, count=10, start=START)
    assert result.max_drift == timedelta(0)
    assert result.avg_drift == timedelta(0)


def test_analyze_drift_every_5_min_vs_1_min_target():
    result = analyze_drift("*/5 * * * *", target_minutes=1, count=5, start=START)
    assert bool(result) is True
    assert result.max_drift == timedelta(minutes=4)
    assert result.avg_drift == timedelta(minutes=4)


def test_analyze_drift_invalid_expression_sets_error():
    result = analyze_drift("not a cron", target_minutes=5, start=START)
    assert bool(result) is False
    assert result.error is not None
    assert result.max_drift is None
    assert result.avg_drift is None


def test_analyze_drift_is_exact_false_when_mismatched():
    result = analyze_drift("*/5 * * * *", target_minutes=1, count=5, start=START)
    assert result.is_exact is False


def test_analyze_drift_actual_intervals_length():
    result = analyze_drift("* * * * *", target_minutes=1, count=8, start=START)
    assert len(result.actual_intervals) == 8


def test_analyze_drift_target_interval_stored():
    result = analyze_drift("* * * * *", target_minutes=15, count=5, start=START)
    assert result.target_interval == timedelta(minutes=15)


def test_drift_result_bool_true_no_error():
    r = DriftResult(expression="* * * * *", target_interval=timedelta(minutes=1))
    assert bool(r) is True


def test_drift_result_bool_false_with_error():
    r = DriftResult(
        expression="bad",
        target_interval=timedelta(minutes=1),
        error="parse error",
    )
    assert bool(r) is False


def test_drift_result_max_drift_none_when_no_intervals():
    r = DriftResult(expression="* * * * *", target_interval=timedelta(minutes=1))
    assert r.max_drift is None


def test_drift_result_avg_drift_none_when_no_intervals():
    r = DriftResult(expression="* * * * *", target_interval=timedelta(minutes=1))
    assert r.avg_drift is None
