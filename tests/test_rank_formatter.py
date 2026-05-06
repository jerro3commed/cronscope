"""Tests for cronscope.rank_formatter module."""

import pytest
from unittest.mock import MagicMock
from cronscope.rank_formatter import format_rank
from cronscope.ranker import RankedExpression


def _make_ranked(expression, rank, runs_per_day, error=None):
    """Helper to create a RankedExpression-like mock."""
    r = MagicMock(spec=RankedExpression)
    r.expression = expression
    r.rank = rank
    r.runs_per_day = runs_per_day
    r.error = error
    r.__bool__ = lambda self: self.error is None
    return r


def test_format_rank_returns_string():
    ranked = [
        _make_ranked("* * * * *", 1, 1440.0),
        _make_ranked("0 * * * *", 2, 24.0),
    ]
    result = format_rank(ranked)
    assert isinstance(result, str)


def test_format_rank_contains_expressions():
    ranked = [
        _make_ranked("* * * * *", 1, 1440.0),
        _make_ranked("0 9 * * 1", 2, 0.14),
    ]
    result = format_rank(ranked)
    assert "* * * * *" in result
    assert "0 9 * * 1" in result


def test_format_rank_shows_rank_numbers():
    ranked = [
        _make_ranked("* * * * *", 1, 1440.0),
        _make_ranked("0 * * * *", 2, 24.0),
        _make_ranked("0 0 * * *", 3, 1.0),
    ]
    result = format_rank(ranked)
    assert "#1" in result
    assert "#2" in result
    assert "#3" in result


def test_format_rank_shows_runs_per_day():
    ranked = [
        _make_ranked("* * * * *", 1, 1440.0),
    ]
    result = format_rank(ranked)
    assert "1440" in result


def test_format_rank_invalid_expression_shows_error():
    ranked = [
        _make_ranked("not a cron", 1, 0.0, error="Invalid expression"),
    ]
    result = format_rank(ranked)
    assert "not a cron" in result
    assert "Invalid expression" in result or "invalid" in result.lower() or "error" in result.lower()


def test_format_rank_empty_list_returns_string():
    result = format_rank([])
    assert isinstance(result, str)


def test_format_rank_no_color_mode():
    ranked = [
        _make_ranked("0 0 * * *", 1, 1.0),
    ]
    result_color = format_rank(ranked, color=True)
    result_no_color = format_rank(ranked, color=False)
    # No-color result should not contain ANSI escape codes
    assert "\x1b[" not in result_no_color
    assert isinstance(result_color, str)


def test_format_rank_single_entry():
    ranked = [
        _make_ranked("30 6 * * 1-5", 1, 0.71),
    ]
    result = format_rank(ranked)
    assert "30 6 * * 1-5" in result
    assert "#1" in result


def test_format_rank_mixed_valid_and_invalid():
    ranked = [
        _make_ranked("* * * * *", 1, 1440.0),
        _make_ranked("bad expr", 2, 0.0, error="Parse error"),
        _make_ranked("0 0 * * *", 3, 1.0),
    ]
    result = format_rank(ranked)
    assert "* * * * *" in result
    assert "bad expr" in result
    assert "0 0 * * *" in result
