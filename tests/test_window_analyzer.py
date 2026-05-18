"""Tests for cronscope.window_analyzer."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

import pytest

from cronscope.window_analyzer import (
    WindowAnalysis,
    WindowCount,
    analyze_windows,
)


NOW = datetime(2024, 6, 1, 0, 0, 0)


def test_analyze_windows_returns_window_analysis():
    result = analyze_windows("* * * * *", now=NOW, days=1, window_hours=6)
    assert isinstance(result, WindowAnalysis)


def test_analyze_windows_invalid_expression_sets_error():
    result = analyze_windows("not a cron", now=NOW)
    assert not result
    assert result.error is not None
    assert isinstance(result.error, str)


def test_analyze_windows_correct_number_of_windows():
    result = analyze_windows("* * * * *", now=NOW, days=2, window_hours=6)
    assert bool(result)
    assert len(result.windows) == 8  # 2 days * 4 windows/day


def test_analyze_windows_every_minute_fills_all_windows():
    result = analyze_windows("* * * * *", now=NOW, days=1, window_hours=6)
    assert bool(result)
    for window in result.windows:
        assert window.count > 0


def test_analyze_windows_total_matches_sum():
    result = analyze_windows("0 12 * * *", now=NOW, days=7, window_hours=6)
    assert bool(result)
    assert result.total == sum(w.count for w in result.windows)


def test_analyze_windows_busiest_has_max_count():
    result = analyze_windows("0 12 * * *", now=NOW, days=7, window_hours=6)
    assert bool(result)
    busiest = result.busiest
    assert busiest is not None
    assert busiest.count == max(w.count for w in result.windows)


def test_analyze_windows_quietest_has_min_count():
    result = analyze_windows("0 12 * * *", now=NOW, days=7, window_hours=6)
    assert bool(result)
    quietest = result.quietest
    assert quietest is not None
    assert quietest.count == min(w.count for w in result.windows)


def test_window_count_bool_true_when_nonzero():
    wc = WindowCount(label="Mon", start=NOW, end=NOW, count=5)
    assert bool(wc)


def test_window_count_bool_false_when_zero():
    wc = WindowCount(label="Mon", start=NOW, end=NOW, count=0)
    assert not bool(wc)


def test_analyze_windows_error_result_bool_false():
    result = WindowAnalysis(expression="bad", error="oops")
    assert not bool(result)


def test_analyze_windows_valid_result_bool_true():
    result = analyze_windows("* * * * *", now=NOW, days=1, window_hours=6)
    assert bool(result)


def test_analyze_windows_window_labels_are_strings():
    result = analyze_windows("* * * * *", now=NOW, days=1, window_hours=6)
    for window in result.windows:
        assert isinstance(window.label, str)
        assert len(window.label) > 0
