"""Tests for cronscope.tagger and cronscope.tag_formatter."""

import pytest
from cronscope.tagger import tag, TaggedExpression, _frequency_tag
from cronscope.tag_formatter import format_tags


# ---------------------------------------------------------------------------
# _frequency_tag
# ---------------------------------------------------------------------------

def test_frequency_tag_every_minute():
    assert _frequency_tag(1440) == "every-minute"


def test_frequency_tag_high_frequency():
    assert _frequency_tag(120) == "high-frequency"


def test_frequency_tag_daily():
    assert _frequency_tag(2) == "daily"


def test_frequency_tag_rare():
    assert _frequency_tag(0.01) == "rare"


# ---------------------------------------------------------------------------
# tag()
# ---------------------------------------------------------------------------

def test_tag_returns_list():
    result = tag(["* * * * *"])
    assert isinstance(result, list)
    assert len(result) == 1


def test_tag_valid_expression_has_no_error():
    result = tag(["0 9 * * 1"])
    assert result[0].error is None
    assert bool(result[0]) is True


def test_tag_invalid_expression_has_error():
    result = tag(["not a cron"])
    assert result[0].error is not None
    assert bool(result[0]) is False


def test_tag_every_minute_has_every_minute_tag():
    result = tag(["* * * * *"])
    assert "every-minute" in result[0].tags


def test_tag_daily_expression_tagged_daily():
    result = tag(["0 8 * * *"])
    assert result[0].tags[0] == "daily"


def test_tag_weekday_specific_adds_tag():
    result = tag(["0 9 * * 1"])
    assert "weekday-specific" in result[0].tags


def test_tag_monthday_specific_adds_tag():
    result = tag(["0 0 15 * *"])
    assert "monthday-specific" in result[0].tags


def test_tag_month_specific_adds_tag():
    result = tag(["0 0 1 6 *"])
    assert "month-specific" in result[0].tags


def test_tag_stepped_expression_adds_tag():
    result = tag(["*/15 * * * *"])
    assert "stepped" in result[0].tags


def test_tag_multi_value_expression_adds_tag():
    result = tag(["0,30 * * * *"])
    assert "multi-value" in result[0].tags


def test_tag_multiple_expressions():
    result = tag(["* * * * *", "0 9 * * *", "bad expr"])
    assert len(result) == 3
    assert bool(result[0]) is True
    assert bool(result[2]) is False


# ---------------------------------------------------------------------------
# format_tags()
# ---------------------------------------------------------------------------

def test_format_tags_returns_string():
    tagged = tag(["0 9 * * *"])
    output = format_tags(tagged, color=False)
    assert isinstance(output, str)


def test_format_tags_contains_expression():
    tagged = tag(["0 9 * * *"])
    output = format_tags(tagged, color=False)
    assert "0 9 * * *" in output


def test_format_tags_shows_error_for_invalid():
    tagged = tag(["bad"])
    output = format_tags(tagged, color=False)
    assert "error" in output


def test_format_tags_empty_list():
    output = format_tags([], color=False)
    assert "No expressions" in output
