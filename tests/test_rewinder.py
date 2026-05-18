"""Tests for cronscope.rewinder and cronscope.rewind_formatter."""

from datetime import datetime, timedelta

import pytest

from cronscope.rewinder import RewindResult, rewind
from cronscope.rewind_formatter import format_rewind

_UNTIL = datetime(2024, 6, 1, 12, 0)
_SINCE = datetime(2024, 6, 1, 11, 0)


# ---------------------------------------------------------------------------
# rewind()
# ---------------------------------------------------------------------------

def test_rewind_returns_rewind_result():
    result = rewind("* * * * *", since=_SINCE, until=_UNTIL)
    assert isinstance(result, RewindResult)


def test_rewind_valid_expression_no_error():
    result = rewind("* * * * *", since=_SINCE, until=_UNTIL)
    assert result.error is None
    assert bool(result) is True


def test_rewind_invalid_expression_sets_error():
    result = rewind("not-a-cron", since=_SINCE, until=_UNTIL)
    assert result.error is not None
    assert bool(result) is False


def test_rewind_every_minute_fills_window():
    result = rewind("* * * * *", since=_SINCE, until=_UNTIL)
    # 60-minute window → 60 runs (minute 11:00 up to but not including 12:00)
    assert result.count == 60


def test_rewind_runs_are_within_window():
    result = rewind("* * * * *", since=_SINCE, until=_UNTIL)
    for run in result.runs:
        assert _SINCE <= run < _UNTIL


def test_rewind_hourly_expression_one_run():
    result = rewind("0 * * * *", since=_SINCE, until=_UNTIL)
    assert result.count == 1
    assert result.runs[0] == datetime(2024, 6, 1, 11, 0)


def test_rewind_most_recent_is_last():
    result = rewind("* * * * *", since=_SINCE, until=_UNTIL)
    assert result.most_recent == result.runs[-1]


def test_rewind_earliest_is_first():
    result = rewind("* * * * *", since=_SINCE, until=_UNTIL)
    assert result.earliest == result.runs[0]


def test_rewind_default_until_is_approx_now():
    result = rewind("* * * * *", since=_SINCE)
    assert result.until is not None


def test_rewind_default_since_derived_from_count():
    result = rewind("0 * * * *", until=_UNTIL, count=5)
    assert result.since == _UNTIL - timedelta(hours=5)


# ---------------------------------------------------------------------------
# format_rewind()
# ---------------------------------------------------------------------------

def test_format_rewind_returns_string():
    result = rewind("* * * * *", since=_SINCE, until=_UNTIL)
    assert isinstance(format_rewind(result, color=False), str)


def test_format_rewind_contains_expression():
    result = rewind("0 9 * * 1", since=_SINCE, until=_UNTIL)
    output = format_rewind(result, color=False)
    assert "0 9 * * 1" in output


def test_format_rewind_shows_run_count():
    result = rewind("* * * * *", since=_SINCE, until=_UNTIL)
    output = format_rewind(result, color=False)
    assert "60" in output


def test_format_rewind_invalid_shows_error():
    result = rewind("bad expr", since=_SINCE, until=_UNTIL)
    output = format_rewind(result, color=False)
    assert "Error" in output


def test_format_rewind_no_runs_message():
    since = datetime(2024, 6, 1, 11, 30)
    until = datetime(2024, 6, 1, 11, 45)
    result = rewind("0 0 1 1 *", since=since, until=until)
    output = format_rewind(result, color=False)
    assert "no runs" in output
