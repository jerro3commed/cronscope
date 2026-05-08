"""Tests for cronscope.timeline_formatter."""

from datetime import datetime, timedelta

import pytest

from cronscope.timeline import Timeline, TimelineWindow, build_timeline
from cronscope.timeline_formatter import format_timeline


FIXED_START = datetime(2024, 1, 15, 12, 0, 0)


def _make_window(label: str, count: int) -> TimelineWindow:
    start = FIXED_START
    end = start + timedelta(hours=1)
    w = TimelineWindow(label=label, start=start, end=end)
    w.runs = [start] * count
    return w


def test_format_timeline_returns_string():
    tl = build_timeline("* * * * *", start=FIXED_START, periods=2)
    result = format_timeline(tl, use_color=False)
    assert isinstance(result, str)


def test_format_timeline_contains_expression():
    tl = build_timeline("0 9 * * *", start=FIXED_START, periods=2)
    result = format_timeline(tl, use_color=False)
    assert "0 9 * * *" in result


def test_format_timeline_shows_total_runs():
    tl = build_timeline("0 9 * * *", start=FIXED_START, periods=3, granularity="day")
    result = format_timeline(tl, use_color=False)
    assert "Total runs: 3" in result


def test_format_timeline_shows_window_labels():
    tl = build_timeline("* * * * *", start=FIXED_START, periods=2, granularity="hour")
    result = format_timeline(tl, use_color=False)
    assert "2024-01-15 12:00" in result
    assert "2024-01-15 13:00" in result


def test_format_timeline_error_shown_on_invalid():
    tl = build_timeline("not valid", start=FIXED_START)
    result = format_timeline(tl, use_color=False)
    assert "Error" in result


def test_format_timeline_bar_present():
    tl = build_timeline("* * * * *", start=FIXED_START, periods=1)
    result = format_timeline(tl, use_color=False)
    assert "█" in result or "░" in result


def test_format_timeline_no_color_no_escape_codes():
    tl = build_timeline("* * * * *", start=FIXED_START, periods=1)
    result = format_timeline(tl, use_color=False)
    assert "\033[" not in result


def test_format_timeline_empty_windows_message():
    tl = Timeline(expression="* * * * *", windows=[])
    result = format_timeline(tl, use_color=False)
    assert "No windows" in result
