"""Tests for cronscope.heatmap and cronscope.heatmap_formatter."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

import pytest

from cronscope.heatmap import DAYS, HOURS, Heatmap, build_heatmap
from cronscope.heatmap_formatter import format_heatmap


FIXED_START = datetime(2024, 1, 1, 0, 0)  # Monday


# ---------------------------------------------------------------------------
# build_heatmap
# ---------------------------------------------------------------------------

def test_build_heatmap_returns_heatmap_instance():
    result = build_heatmap("* * * * *", weeks=1, start=FIXED_START)
    assert isinstance(result, Heatmap)


def test_build_heatmap_invalid_expression_sets_error():
    result = build_heatmap("not a cron", weeks=1, start=FIXED_START)
    assert not result
    assert result.error is not None


def test_build_heatmap_every_minute_fills_all_cells():
    result = build_heatmap("* * * * *", weeks=1, start=FIXED_START)
    assert bool(result)
    for d in range(7):
        for h in HOURS:
            assert result.get(d, h) > 0


def test_build_heatmap_daily_at_noon_only_hour_12():
    result = build_heatmap("0 12 * * *", weeks=4, start=FIXED_START)
    assert bool(result)
    for d in range(7):
        assert result.get(d, 12) > 0
        assert result.get(d, 11) == 0
        assert result.get(d, 13) == 0


def test_build_heatmap_cells_keys_are_days_and_hours():
    result = build_heatmap("0 0 * * *", weeks=2, start=FIXED_START)
    assert set(result.cells.keys()) == set(range(7))
    for day_map in result.cells.values():
        assert set(day_map.keys()) == set(HOURS)


def test_build_heatmap_max_count_is_positive_for_every_minute():
    result = build_heatmap("* * * * *", weeks=1, start=FIXED_START)
    assert result.max_count > 0


def test_build_heatmap_max_count_zero_on_error():
    result = build_heatmap("bad expr", weeks=1)
    assert result.max_count == 0


# ---------------------------------------------------------------------------
# format_heatmap
# ---------------------------------------------------------------------------

def test_format_heatmap_returns_string():
    hm = build_heatmap("0 9 * * 1-5", weeks=2, start=FIXED_START)
    output = format_heatmap(hm, color=False)
    assert isinstance(output, str)


def test_format_heatmap_contains_expression():
    expr = "0 9 * * 1-5"
    hm = build_heatmap(expr, weeks=2, start=FIXED_START)
    output = format_heatmap(hm, color=False)
    assert expr in output


def test_format_heatmap_contains_day_labels():
    hm = build_heatmap("* * * * *", weeks=1, start=FIXED_START)
    output = format_heatmap(hm, color=False)
    for day in DAYS:
        assert day in output


def test_format_heatmap_error_shown_on_invalid():
    hm = build_heatmap("bad", weeks=1)
    output = format_heatmap(hm, color=False)
    assert "Error" in output


def test_format_heatmap_no_color_has_no_ansi():
    hm = build_heatmap("0 0 * * *", weeks=1, start=FIXED_START)
    output = format_heatmap(hm, color=False)
    assert "\033[" not in output
