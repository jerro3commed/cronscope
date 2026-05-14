"""Tests for cronscope.cadence and cronscope.cadence_formatter."""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from cronscope.cadence import CadenceResult, analyze_cadence
from cronscope.cadence_formatter import format_cadence, _fmt_td


START = datetime(2024, 1, 1, 0, 0, 0)


# ---------------------------------------------------------------------------
# CadenceResult unit tests
# ---------------------------------------------------------------------------

def test_cadence_result_bool_true_when_no_error():
    r = CadenceResult(expression="* * * * *", intervals_seconds=[60.0])
    assert bool(r) is True


def test_cadence_result_bool_false_when_error():
    r = CadenceResult(expression="bad", error="parse error")
    assert bool(r) is False


def test_cadence_result_min_max_avg():
    r = CadenceResult(expression="* * * * *", intervals_seconds=[60.0, 120.0, 90.0])
    assert r.min_interval == timedelta(seconds=60)
    assert r.max_interval == timedelta(seconds=120)
    assert r.avg_interval == timedelta(seconds=90)


def test_cadence_result_is_regular_when_equal_intervals():
    r = CadenceResult(expression="* * * * *", intervals_seconds=[60.0, 60.0, 60.0])
    assert r.is_regular is True


def test_cadence_result_is_irregular_when_varying():
    r = CadenceResult(expression="0 * * * *", intervals_seconds=[3600.0, 7200.0])
    assert r.is_regular is False


def test_cadence_result_none_when_empty():
    r = CadenceResult(expression="* * * * *", intervals_seconds=[])
    assert r.min_interval is None
    assert r.max_interval is None
    assert r.avg_interval is None


# ---------------------------------------------------------------------------
# analyze_cadence integration tests
# ---------------------------------------------------------------------------

def test_analyze_cadence_returns_cadence_result():
    result = analyze_cadence("* * * * *", count=5, start=START)
    assert isinstance(result, CadenceResult)


def test_analyze_cadence_every_minute_is_regular():
    result = analyze_cadence("* * * * *", count=10, start=START)
    assert bool(result) is True
    assert result.is_regular is True


def test_analyze_cadence_every_minute_interval_is_60s():
    result = analyze_cadence("* * * * *", count=5, start=START)
    assert all(s == 60.0 for s in result.intervals_seconds)


def test_analyze_cadence_invalid_expression_sets_error():
    result = analyze_cadence("not a cron", count=5, start=START)
    assert not result
    assert result.error is not None


def test_analyze_cadence_count_produces_n_minus_one_intervals():
    result = analyze_cadence("* * * * *", count=8, start=START)
    assert len(result.intervals_seconds) == 8


# ---------------------------------------------------------------------------
# _fmt_td helper
# ---------------------------------------------------------------------------

def test_fmt_td_none_returns_na():
    assert _fmt_td(None) == "n/a"


def test_fmt_td_seconds_only():
    assert _fmt_td(timedelta(seconds=45)) == "45s"


def test_fmt_td_minutes_and_seconds():
    assert _fmt_td(timedelta(seconds=125)) == "2m 5s"


def test_fmt_td_hours():
    assert _fmt_td(timedelta(hours=2)) == "2h"


# ---------------------------------------------------------------------------
# format_cadence formatter tests
# ---------------------------------------------------------------------------

def test_format_cadence_returns_string():
    result = analyze_cadence("* * * * *", count=5, start=START)
    assert isinstance(format_cadence(result, color=False), str)


def test_format_cadence_contains_expression():
    result = analyze_cadence("0 9 * * 1", count=5, start=START)
    output = format_cadence(result, color=False)
    assert "0 9 * * 1" in output


def test_format_cadence_shows_regularity():
    result = analyze_cadence("* * * * *", count=5, start=START)
    output = format_cadence(result, color=False)
    assert "regular" in output


def test_format_cadence_error_shows_error_message():
    result = CadenceResult(expression="bad expr", error="Invalid field")
    output = format_cadence(result, color=False)
    assert "Error" in output
    assert "Invalid field" in output
