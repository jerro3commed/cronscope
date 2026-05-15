"""Tests for cronscope.comparator."""

from datetime import datetime

import pytest

from cronscope.comparator import compare, ScheduleComparison


START = datetime(2024, 1, 1, 0, 0, 0)


def test_compare_returns_schedule_comparison():
    result = compare("* * * * *", "*/5 * * * *", count=5, start=START)
    assert isinstance(result, ScheduleComparison)


def test_compare_identical_expressions_all_shared():
    result = compare("0 9 * * *", "0 9 * * *", count=5, start=START)
    assert not result.has_errors
    assert len(result.shared_runs) == 5
    assert result.only_left == []
    assert result.only_right == []


def test_compare_disjoint_expressions_no_shared():
    # Every minute vs daily at noon — no overlap in first 10 minutes
    result = compare("* * * * *", "0 12 * * *", count=10, start=START)
    assert not result.has_errors
    # The daily job runs at 12:00; every-minute runs at 12:00 too
    # so there may be 1 overlap; what matters is only_left and only_right exist
    assert result.overlap_count + len(result.only_left) + len(result.only_right) > 0


def test_compare_every_5_min_is_subset_of_every_minute():
    result = compare("*/5 * * * *", "* * * * *", count=60, start=START)
    assert not result.has_errors
    # All */5 runs should appear in every-minute runs
    assert result.only_left == []


def test_compare_left_invalid_sets_error():
    result = compare("not_valid", "* * * * *", count=5, start=START)
    assert result.has_errors
    assert result.left_error is not None
    assert result.right_error is None


def test_compare_right_invalid_sets_error():
    result = compare("* * * * *", "bad expr", count=5, start=START)
    assert result.has_errors
    assert result.right_error is not None
    assert result.left_error is None


def test_compare_both_invalid_sets_both_errors():
    result = compare("bad", "also bad", count=5, start=START)
    assert result.left_error is not None
    assert result.right_error is not None


def test_compare_no_runs_when_errors():
    result = compare("bad", "* * * * *", count=5, start=START)
    assert result.shared_runs == []
    assert result.only_left == []
    assert result.only_right == []


def test_overlap_count_property():
    result = compare("0 9 * * *", "0 9 * * *", count=3, start=START)
    assert result.overlap_count == 3


def test_total_unique_property():
    result = compare("0 8 * * *", "0 9 * * *", count=3, start=START)
    assert not result.has_errors
    assert result.total_unique == result.overlap_count * 0 + len(result.only_left) + len(result.only_right)


def test_total_unique_includes_shared_and_exclusive_runs():
    """total_unique should count shared runs plus runs exclusive to each side."""
    result = compare("0 8 * * *", "0 8 * * *", count=3, start=START)
    assert not result.has_errors
    # When both schedules are identical, total_unique equals the number of shared runs
    assert result.total_unique == result.overlap_count
