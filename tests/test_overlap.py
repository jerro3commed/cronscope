"""Tests for cronscope.overlap."""

from __future__ import annotations

from datetime import datetime

import pytest

from cronscope.overlap import find_overlaps, OverlapReport, OverlapSlot

_START = datetime(2024, 1, 1, 0, 0)


def test_find_overlaps_returns_overlap_report():
    report = find_overlaps(["* * * * *", "*/5 * * * *"], count=10, start=_START)
    assert isinstance(report, OverlapReport)


def test_every_minute_and_every_5_min_overlap():
    report = find_overlaps(["* * * * *", "*/5 * * * *"], count=60, start=_START)
    assert report.has_overlaps
    assert report.overlap_count > 0


def test_disjoint_hours_do_not_overlap():
    # one fires at hour 1, other at hour 2 — never same slot
    report = find_overlaps(["0 1 * * *", "0 2 * * *"], count=5, start=_START)
    assert not report.has_overlaps


def test_identical_expressions_all_slots_overlap():
    report = find_overlaps(["0 9 * * *", "0 9 * * *"], count=5, start=_START)
    assert report.has_overlaps
    for slot in report.slots:
        assert len(slot.expressions) == 2


def test_invalid_expression_recorded_in_errors():
    report = find_overlaps(["* * * * *", "bad expr"], count=5, start=_START)
    assert "bad expr" in report.errors


def test_invalid_expression_does_not_prevent_valid_analysis():
    report = find_overlaps(["* * * * *", "*/5 * * * *", "not-valid"], count=30, start=_START)
    assert report.has_overlaps  # the two valid ones still overlap


def test_bool_false_when_errors_present():
    report = find_overlaps(["* * * * *", "bad"], count=5, start=_START)
    assert not bool(report)


def test_bool_true_when_no_errors():
    report = find_overlaps(["* * * * *", "*/5 * * * *"], count=5, start=_START)
    assert bool(report)


def test_slot_timestamps_are_sorted():
    report = find_overlaps(["* * * * *", "*/2 * * * *"], count=20, start=_START)
    timestamps = [s.timestamp for s in report.slots]
    assert timestamps == sorted(timestamps)


def test_expressions_stored_on_report():
    exprs = ["* * * * *", "*/10 * * * *"]
    report = find_overlaps(exprs, count=5, start=_START)
    assert report.expressions == exprs
