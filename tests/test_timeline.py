"""Tests for cronscope.timeline."""

from datetime import datetime

import pytest

from cronscope.timeline import build_timeline, Timeline, TimelineWindow


FIXED_START = datetime(2024, 1, 15, 12, 0, 0)


def test_build_timeline_returns_timeline():
    result = build_timeline("* * * * *", start=FIXED_START, periods=2, granularity="hour")
    assert isinstance(result, Timeline)


def test_build_timeline_invalid_expression_sets_error():
    result = build_timeline("not a cron", start=FIXED_START)
    assert not result
    assert result.error is not None
    assert isinstance(result.error, str)


def test_build_timeline_correct_number_of_windows():
    result = build_timeline("* * * * *", start=FIXED_START, periods=6, granularity="hour")
    assert len(result.windows) == 6


def test_build_timeline_every_minute_fills_windows():
    result = build_timeline("* * * * *", start=FIXED_START, periods=2, granularity="hour")
    assert result.total_runs > 0
    for window in result.windows:
        assert window.count == 60


def test_build_timeline_daily_granularity():
    result = build_timeline("0 9 * * *", start=FIXED_START, periods=3, granularity="day")
    assert len(result.windows) == 3
    assert result.total_runs == 3


def test_build_timeline_window_labels_hour():
    result = build_timeline("* * * * *", start=FIXED_START, periods=1, granularity="hour")
    assert result.windows[0].label == "2024-01-15 12:00"


def test_build_timeline_window_labels_day():
    result = build_timeline("0 0 * * *", start=FIXED_START, periods=1, granularity="day")
    assert result.windows[0].label == "2024-01-15"


def test_build_timeline_invalid_granularity_raises():
    with pytest.raises(ValueError, match="granularity"):
        build_timeline("* * * * *", granularity="week")


def test_timeline_bool_true_when_no_error():
    result = build_timeline("* * * * *", start=FIXED_START, periods=1)
    assert bool(result) is True


def test_timeline_bool_false_when_error():
    result = build_timeline("bad expr", start=FIXED_START)
    assert bool(result) is False


def test_timeline_window_bool_false_when_empty():
    from datetime import timedelta
    w = TimelineWindow(
        label="test",
        start=FIXED_START,
        end=FIXED_START + timedelta(hours=1),
    )
    assert bool(w) is False


def test_no_runs_outside_window_range():
    # Run once at 9:00 each day; hourly windows starting at 10:00 should be empty
    start = datetime(2024, 1, 15, 10, 0, 0)
    result = build_timeline("0 9 * * *", start=start, periods=3, granularity="hour")
    assert result.total_runs == 0
