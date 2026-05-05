"""Tests for cronscope.explainer module."""

import pytest
from cronscope.explainer import explain
from cronscope.parser import CronParseError


def test_explain_wildcard_is_every_minute():
    result = explain("* * * * *")
    assert "every minute" in result.lower()


def test_explain_specific_minute():
    result = explain("30 * * * *")
    assert "minute 30" in result


def test_explain_specific_hour():
    result = explain("0 9 * * *")
    assert "hour 9" in result


def test_explain_step_in_minutes():
    result = explain("*/15 * * * *")
    assert "every 15 minute(s)" in result


def test_explain_step_in_hours():
    result = explain("0 */6 * * *")
    assert "every 6 hour(s)" in result


def test_explain_specific_month():
    result = explain("0 0 1 6 *")
    assert "June" in result


def test_explain_comma_list_months():
    result = explain("0 0 1 1,6,12 *")
    assert "January" in result
    assert "June" in result
    assert "December" in result


def test_explain_day_of_week():
    result = explain("0 9 * * 1")
    assert "Monday" in result


def test_explain_range_field():
    result = explain("0 9 1-15 * *")
    assert "1 through 15" in result


def test_explain_returns_string():
    result = explain("5 4 * * 0")
    assert isinstance(result, str)
    assert result.startswith("Runs ")
    assert result.endswith(".")


def test_explain_invalid_raises():
    with pytest.raises(CronParseError):
        explain("invalid expression")


def test_explain_complex_expression():
    result = explain("*/5 8-18 * * 1-5")
    assert isinstance(result, str)
    assert len(result) > 10
