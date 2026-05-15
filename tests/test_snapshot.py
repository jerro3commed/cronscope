"""Tests for cronscope.snapshot."""

from datetime import datetime

import pytest

from cronscope.snapshot import SnapshotEntry, SnapshotDelta, take_snapshot, diff_snapshots

_NOW = datetime(2024, 6, 1, 12, 0, 0)


def test_take_snapshot_returns_snapshot_entry():
    result = take_snapshot("* * * * *", count=3, now=_NOW)
    assert isinstance(result, SnapshotEntry)


def test_take_snapshot_valid_expression_no_error():
    result = take_snapshot("* * * * *", count=3, now=_NOW)
    assert result.error is None
    assert bool(result) is True


def test_take_snapshot_captures_correct_number_of_runs():
    result = take_snapshot("* * * * *", count=4, now=_NOW)
    assert len(result.next_runs) == 4


def test_take_snapshot_invalid_expression_sets_error():
    result = take_snapshot("invalid expr", count=3, now=_NOW)
    assert result.error is not None
    assert bool(result) is False
    assert result.next_runs == []


def test_take_snapshot_stores_captured_at():
    result = take_snapshot("0 9 * * *", count=2, now=_NOW)
    assert result.captured_at == _NOW


def test_take_snapshot_stores_expression():
    result = take_snapshot("0 9 * * 1", count=2, now=_NOW)
    assert result.expression == "0 9 * * 1"


def test_diff_snapshots_returns_snapshot_delta():
    before = take_snapshot("* * * * *", count=3, now=_NOW)
    after = take_snapshot("* * * * *", count=3, now=_NOW)
    delta = diff_snapshots(before, after)
    assert isinstance(delta, SnapshotDelta)


def test_diff_snapshots_identical_has_no_changes():
    before = take_snapshot("0 12 * * *", count=5, now=_NOW)
    after = take_snapshot("0 12 * * *", count=5, now=_NOW)
    delta = diff_snapshots(before, after)
    assert delta.has_changes is False
    assert delta.added == []
    assert delta.removed == []


def test_diff_snapshots_unchanged_populated_when_identical():
    before = take_snapshot("0 12 * * *", count=5, now=_NOW)
    after = take_snapshot("0 12 * * *", count=5, now=_NOW)
    delta = diff_snapshots(before, after)
    assert len(delta.unchanged) == len(before.next_runs)


def test_diff_snapshots_detects_added_runs():
    from datetime import timedelta

    before = take_snapshot("0 12 * * *", count=3, now=_NOW)
    after = take_snapshot("0 12 * * *", count=3, now=_NOW + timedelta(days=3))
    delta = diff_snapshots(before, after)
    assert len(delta.added) > 0


def test_diff_snapshots_detects_removed_runs():
    from datetime import timedelta

    before = take_snapshot("0 12 * * *", count=3, now=_NOW)
    after = take_snapshot("0 12 * * *", count=3, now=_NOW + timedelta(days=3))
    delta = diff_snapshots(before, after)
    assert len(delta.removed) > 0
