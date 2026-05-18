"""Tests for cronscope.trace_formatter."""

from datetime import datetime
import pytest

from cronscope.tracer import trace
from cronscope.trace_formatter import format_trace


def _dt(hour=12, minute=0):
    return datetime(2024, 6, 3, hour, minute)  # Monday


def test_format_trace_returns_string():
    result = trace("* * * * *", _dt())
    output = format_trace(result, color=False)
    assert isinstance(output, str)


def test_format_trace_contains_expression():
    result = trace("0 12 * * *", _dt())
    output = format_trace(result, color=False)
    assert "0 12 * * *" in output


def test_format_trace_contains_datetime():
    result = trace("0 12 * * *", _dt())
    output = format_trace(result, color=False)
    assert "2024-06-03" in output


def test_format_trace_shows_match_on_match():
    result = trace("0 12 * * *", _dt(hour=12, minute=0))
    output = format_trace(result, color=False)
    assert "MATCH" in output


def test_format_trace_shows_no_match_on_miss():
    result = trace("0 12 * * *", _dt(hour=13, minute=0))
    output = format_trace(result, color=False)
    assert "NO MATCH" in output


def test_format_trace_mentions_failing_field():
    result = trace("0 12 * * *", _dt(hour=13))
    output = format_trace(result, color=False)
    assert "hour" in output


def test_format_trace_shows_all_field_names():
    result = trace("* * * * *", _dt())
    output = format_trace(result, color=False)
    for name in ["minute", "hour", "day", "month", "weekday"]:
        assert name in output


def test_format_trace_invalid_shows_error():
    result = trace("bad expr", _dt())
    output = format_trace(result, color=False)
    assert "Error" in output or "error" in output


def test_format_trace_no_color_has_no_escape_codes():
    result = trace("0 12 * * *", _dt())
    output = format_trace(result, color=False)
    assert "\x1b[" not in output


def test_format_trace_with_color_has_escape_codes():
    result = trace("0 12 * * *", _dt())
    output = format_trace(result, color=True)
    assert "\x1b[" in output
