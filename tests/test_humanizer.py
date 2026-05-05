"""Tests for cronscope.humanizer."""

import pytest
from cronscope.parser import parse
from cronscope.humanizer import humanize


def test_every_minute():
    assert humanize(parse("* * * * *")) == "every minute"


def test_specific_minute_and_hour():
    result = humanize(parse("0 9 * * *"))
    assert "minute 0" in result
    assert "hour 9" in result


def test_multiple_minutes():
    result = humanize(parse("0,30 * * * *"))
    assert "0" in result
    assert "30" in result


def test_specific_day_of_month():
    result = humanize(parse("0 0 1 * *"))
    assert "day 1" in result


def test_specific_month_by_number():
    result = humanize(parse("0 0 1 6 *"))
    assert "June" in result


def test_specific_month_alias():
    result = humanize(parse("0 0 1 dec *"))
    assert "December" in result


def test_specific_weekday():
    result = humanize(parse("0 9 * * 1"))
    assert "Monday" in result


def test_multiple_weekdays():
    result = humanize(parse("0 9 * * 1,5"))
    assert "Monday" in result
    assert "Friday" in result


def test_many_minutes_uses_count():
    result = humanize(parse("0,5,10,15,20,25 * * * *"))
    assert "6 specific" in result


def test_full_expression():
    result = humanize(parse("30 8 15 3 *"))
    assert "minute 30" in result
    assert "hour 8" in result
    assert "day 15" in result
    assert "March" in result
