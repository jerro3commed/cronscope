"""Tests for cronscope.profiler and cronscope.profile_formatter."""

from __future__ import annotations

from datetime import datetime

import pytest

from cronscope.profiler import profile, ProfileResult, WEEKDAY_NAMES
from cronscope.profile_formatter import format_profile


START = datetime(2024, 1, 1, 0, 0, 0)  # Monday


def test_profile_returns_profile_result():
    result = profile("* * * * *", start=START, sample_days=1)
    assert isinstance(result, ProfileResult)


def test_profile_valid_expression_no_error():
    result = profile("* * * * *", start=START, sample_days=1)
    assert result.error is None
    assert bool(result) is True


def test_profile_invalid_expression_sets_error():
    result = profile("bad expr", start=START, sample_days=1)
    assert result.error is not None
    assert bool(result) is False


def test_profile_every_minute_fills_all_hours():
    result = profile("* * * * *", start=START, sample_days=1)
    for h in range(24):
        assert result.runs_per_hour[h] == 60


def test_profile_daily_at_noon_only_hour_12():
    result = profile("0 12 * * *", start=START, sample_days=7)
    assert result.runs_per_hour[12] == 7
    for h in range(24):
        if h != 12:
            assert result.runs_per_hour[h] == 0


def test_profile_total_runs_every_minute_one_day():
    result = profile("* * * * *", start=START, sample_days=1)
    assert result.total_runs == 24 * 60


def test_profile_busiest_hour_daily_at_noon():
    result = profile("0 12 * * *", start=START, sample_days=7)
    assert result.busiest_hour == 12


def test_profile_runs_per_weekday_daily():
    result = profile("0 0 * * *", start=START, sample_days=7)
    for d in range(7):
        assert result.runs_per_weekday[d] == 1


def test_profile_weekday_names_length():
    assert len(WEEKDAY_NAMES) == 7


def test_format_profile_returns_string():
    result = profile("* * * * *", start=START, sample_days=1)
    output = format_profile(result, color=False)
    assert isinstance(output, str)


def test_format_profile_contains_expression():
    result = profile("0 6 * * *", start=START, sample_days=3)
    output = format_profile(result, color=False)
    assert "0 6 * * *" in output


def test_format_profile_shows_total_runs():
    result = profile("0 6 * * *", start=START, sample_days=3)
    output = format_profile(result, color=False)
    assert str(result.total_runs) in output


def test_format_profile_invalid_shows_error():
    result = profile("not valid", start=START, sample_days=1)
    output = format_profile(result, color=False)
    assert "Error" in output


def test_format_profile_shows_hour_labels():
    result = profile("* * * * *", start=START, sample_days=1)
    output = format_profile(result, color=False)
    assert "00:00" in output
    assert "23:00" in output


def test_format_profile_shows_weekday_labels():
    result = profile("* * * * *", start=START, sample_days=7)
    output = format_profile(result, color=False)
    for day in WEEKDAY_NAMES:
        assert day in output
