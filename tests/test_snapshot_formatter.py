"""Tests for cronscope.snapshot_formatter."""

from datetime import datetime

import pytest

from cronscope.snapshot import take_snapshot, diff_snapshots
from cronscope.snapshot_formatter import format_snapshot, format_snapshot_delta

_NOW = datetime(2024, 6, 1, 12, 0, 0)


def test_format_snapshot_returns_string():
    entry = take_snapshot("* * * * *", count=3, now=_NOW)
    result = format_snapshot(entry, color=False)
    assert isinstance(result, str)


def test_format_snapshot_contains_expression():
    entry = take_snapshot("0 9 * * 1", count=2, now=_NOW)
    result = format_snapshot(entry, color=False)
    assert "0 9 * * 1" in result


def test_format_snapshot_contains_captured_at():
    entry = take_snapshot("* * * * *", count=2, now=_NOW)
    result = format_snapshot(entry, color=False)
    assert "2024-06-01" in result


def test_format_snapshot_shows_run_dates():
    entry = take_snapshot("* * * * *", count=2, now=_NOW)
    result = format_snapshot(entry, color=False)
    assert "2024" in result


def test_format_snapshot_invalid_shows_error():
    entry = take_snapshot("bad expr", count=3, now=_NOW)
    result = format_snapshot(entry, color=False)
    assert "Error" in result


def test_format_snapshot_color_does_not_crash():
    entry = take_snapshot("* * * * *", count=2, now=_NOW)
    result = format_snapshot(entry, color=True)
    assert isinstance(result, str)


def test_format_snapshot_delta_returns_string():
    before = take_snapshot("0 12 * * *", count=5, now=_NOW)
    after = take_snapshot("0 12 * * *", count=5, now=_NOW)
    delta = diff_snapshots(before, after)
    result = format_snapshot_delta(delta, color=False)
    assert isinstance(result, str)


def test_format_snapshot_delta_contains_expression():
    before = take_snapshot("0 12 * * *", count=3, now=_NOW)
    after = take_snapshot("0 12 * * *", count=3, now=_NOW)
    delta = diff_snapshots(before, after)
    result = format_snapshot_delta(delta, color=False)
    assert "0 12 * * *" in result


def test_format_snapshot_delta_no_changes_message():
    before = take_snapshot("0 12 * * *", count=5, now=_NOW)
    after = take_snapshot("0 12 * * *", count=5, now=_NOW)
    delta = diff_snapshots(before, after)
    result = format_snapshot_delta(delta, color=False)
    assert "No changes" in result


def test_format_snapshot_delta_shows_unchanged_count():
    before = take_snapshot("0 12 * * *", count=5, now=_NOW)
    after = take_snapshot("0 12 * * *", count=5, now=_NOW)
    delta = diff_snapshots(before, after)
    result = format_snapshot_delta(delta, color=False)
    assert "Unchanged" in result
