"""Tests for cronscope.overlap_formatter."""

from __future__ import annotations

from datetime import datetime

import pytest

from cronscope.overlap import find_overlaps, OverlapReport, OverlapSlot
from cronscope.overlap_formatter import format_overlap

_START = datetime(2024, 1, 1, 0, 0)


def _report_with_overlaps() -> OverlapReport:
    return find_overlaps(["* * * * *", "*/5 * * * *"], count=30, start=_START)


def _report_no_overlaps() -> OverlapReport:
    return find_overlaps(["0 1 * * *", "0 2 * * *"], count=5, start=_START)


def test_format_overlap_returns_string():
    report = _report_with_overlaps()
    result = format_overlap(report, color=False)
    assert isinstance(result, str)


def test_format_overlap_contains_header():
    report = _report_with_overlaps()
    result = format_overlap(report, color=False)
    assert "Overlap Analysis" in result


def test_format_overlap_shows_overlap_count():
    report = _report_with_overlaps()
    result = format_overlap(report, color=False)
    assert str(report.overlap_count) in result


def test_format_overlap_no_overlaps_message():
    report = _report_no_overlaps()
    result = format_overlap(report, color=False)
    assert "No overlapping slots found" in result


def test_format_overlap_shows_expression():
    report = _report_with_overlaps()
    result = format_overlap(report, color=False)
    assert "* * * * *" in result


def test_format_overlap_shows_error_for_invalid():
    report = find_overlaps(["* * * * *", "bad"], count=5, start=_START)
    result = format_overlap(report, color=False)
    assert "bad" in result
    assert "Parse errors" in result


def test_format_overlap_color_false_no_ansi():
    report = _report_with_overlaps()
    result = format_overlap(report, color=False)
    assert "\x1b[" not in result


def test_format_overlap_color_true_has_ansi():
    report = _report_with_overlaps()
    result = format_overlap(report, color=True)
    assert "\x1b[" in result
