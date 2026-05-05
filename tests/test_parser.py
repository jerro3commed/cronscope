"""Tests for the cron expression parser."""

import pytest
from cronscope.parser import parse, CronExpression, CronParseError


def test_parse_wildcard_expression():
    expr = parse("* * * * *")
    assert isinstance(expr, CronExpression)
    assert expr.minute == "*"
    assert expr.hour == "*"
    assert expr.raw == "* * * * *"


def test_parse_standard_expression():
    expr = parse("30 8 * * 1-5")
    assert expr.minute == "30"
    assert expr.hour == "8"
    assert expr.day_of_week == "1-5"


def test_parse_with_step():
    expr = parse("*/15 * * * *")
    assert expr.minute == "*/15"


def test_parse_with_comma_list():
    expr = parse("0 9,17 * * *")
    assert expr.hour == "9,17"


def test_parse_month_alias():
    expr = parse("0 0 1 jan *")
    assert expr.month == "jan"


def test_parse_dow_alias():
    expr = parse("0 0 * * mon")
    assert expr.day_of_week == "mon"


def test_invalid_field_count_raises():
    with pytest.raises(CronParseError, match="Expected 5 fields"):
        parse("* * * *")


def test_minute_out_of_range_raises():
    with pytest.raises(CronParseError, match="out of bounds"):
        parse("60 * * * *")


def test_hour_out_of_range_raises():
    with pytest.raises(CronParseError, match="out of bounds"):
        parse("0 24 * * *")


def test_invalid_range_raises():
    with pytest.raises(CronParseError, match="Invalid"):
        parse("0 0 * * abc")


def test_invalid_step_raises():
    with pytest.raises(CronParseError, match="Invalid step"):
        parse("*/abc * * * *")


def test_complex_expression():
    expr = parse("5,10 0-6 */2 1,6 mon-fri")
    assert expr.minute == "5,10"
    assert expr.hour == "0-6"
    assert expr.day_of_month == "*/2"
    assert expr.month == "1,6"
    assert expr.day_of_week == "mon-fri"
