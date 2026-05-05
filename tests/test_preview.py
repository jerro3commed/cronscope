"""Tests for the high-level preview API."""

from datetime import datetime

import pytest

from cronscope.preview import preview, next_runs
from cronscope.parser import CronParseError

BASE = datetime(2024, 6, 1, 8, 0)


def test_preview_returns_string():
    result = preview("* * * * *", count=3, base_time=BASE, color=False)
    assert isinstance(result, str)
    assert "2024" in result


def test_preview_contains_expression():
    result = preview("0 9 * * 1", count=5, base_time=BASE, color=False)
    assert "0 9 * * 1" in result


def test_preview_invalid_expression():
    result = preview("99 * * * *", base_time=BASE, color=False)
    assert "[ERROR]" in result
    assert "99 * * * *" in result


def test_next_runs_returns_list():
    runs = next_runs("30 6 * * *", count=3, base_time=BASE)
    assert len(runs) == 3
    for dt in runs:
        assert dt.hour == 6
        assert dt.minute == 30


def test_next_runs_raises_on_invalid():
    with pytest.raises(CronParseError):
        next_runs("invalid expression", base_time=BASE)


def test_preview_color_output_contains_ansi():
    result = preview("* * * * *", count=2, base_time=BASE, color=True)
    assert "\033[" in result


def test_preview_no_color_no_ansi():
    result = preview("* * * * *", count=2, base_time=BASE, color=False)
    assert "\033[" not in result
