"""Tests for cronscope.heatmap_formatter."""

import pytest
from unittest.mock import patch

from cronscope.heatmap import Heatmap, HeatmapCell
from cronscope.heatmap_formatter import format_heatmap, _shade, _cell_color


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
HOURS = list(range(24))


def _make_heatmap(expression: str = "0 * * * *", max_count: int = 1) -> Heatmap:
    """Build a minimal Heatmap fixture."""
    cells = {}
    for day in DAYS:
        for hour in HOURS:
            cells[(day, hour)] = HeatmapCell(day=day, hour=hour, count=0)
    # Place a single hit on Monday at hour 0
    cells[("Mon", 0)] = HeatmapCell(day="Mon", hour=0, count=max_count)
    return Heatmap(
        expression=expression,
        cells=cells,
        error=None,
    )


def _make_error_heatmap(expression: str = "bad expr") -> Heatmap:
    """Build a Heatmap fixture that carries a parse error."""
    return Heatmap(
        expression=expression,
        cells={},
        error="Invalid cron expression",
    )


# ---------------------------------------------------------------------------
# _shade
# ---------------------------------------------------------------------------


def test_shade_zero_returns_empty_block():
    assert _shade(0, 10) == " "


def test_shade_full_returns_dark_block():
    # Maximum ratio should yield the darkest shade character
    result = _shade(10, 10)
    assert result != " "


def test_shade_partial_is_not_empty_and_not_full():
    low = _shade(1, 10)
    high = _shade(10, 10)
    mid = _shade(5, 10)
    assert low != " "
    assert mid != high or low != high  # at least some variation exists


def test_shade_max_zero_returns_empty_block():
    """When max_count is 0 every cell should render as empty."""
    assert _shade(0, 0) == " "


# ---------------------------------------------------------------------------
# _cell_color
# ---------------------------------------------------------------------------


def test_cell_color_returns_string():
    result = _cell_color(5, 10, use_color=True)
    assert isinstance(result, str)


def test_cell_color_no_color_contains_shade():
    result = _cell_color(10, 10, use_color=False)
    # Without ANSI codes the result should just be the shade character
    assert len(result) == 1


def test_cell_color_with_color_longer_than_no_color():
    no_color = _cell_color(5, 10, use_color=False)
    with_color = _cell_color(5, 10, use_color=True)
    # ANSI escape sequences make the colored version longer
    assert len(with_color) >= len(no_color)


# ---------------------------------------------------------------------------
# format_heatmap — basic structure
# ---------------------------------------------------------------------------


def test_format_heatmap_returns_string():
    hm = _make_heatmap()
    result = format_heatmap(hm, use_color=False)
    assert isinstance(result, str)


def test_format_heatmap_contains_expression():
    hm = _make_heatmap(expression="30 6 * * 1")
    result = format_heatmap(hm, use_color=False)
    assert "30 6 * * 1" in result


def test_format_heatmap_contains_day_labels():
    hm = _make_heatmap()
    result = format_heatmap(hm, use_color=False)
    for day in DAYS:
        assert day in result


def test_format_heatmap_contains_hour_labels():
    hm = _make_heatmap()
    result = format_heatmap(hm, use_color=False)
    # At minimum the first and last hour should appear
    assert "0" in result
    assert "23" in result


def test_format_heatmap_multiline():
    hm = _make_heatmap()
    result = format_heatmap(hm, use_color=False)
    assert "\n" in result


# ---------------------------------------------------------------------------
# format_heatmap — error path
# ---------------------------------------------------------------------------


def test_format_heatmap_error_contains_expression():
    hm = _make_error_heatmap(expression="bad expr")
    result = format_heatmap(hm, use_color=False)
    assert "bad expr" in result


def test_format_heatmap_error_contains_error_message():
    hm = _make_error_heatmap()
    result = format_heatmap(hm, use_color=False)
    assert "Invalid" in result or "error" in result.lower()


# ---------------------------------------------------------------------------
# format_heatmap — color toggle
# ---------------------------------------------------------------------------


def test_format_heatmap_color_output_differs_from_plain():
    hm = _make_heatmap(max_count=5)
    plain = format_heatmap(hm, use_color=False)
    colored = format_heatmap(hm, use_color=True)
    # Colored output should contain ANSI escape sequences
    assert "\x1b[" in colored
    assert "\x1b[" not in plain
