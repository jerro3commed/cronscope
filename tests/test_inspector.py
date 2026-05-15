"""Tests for cronscope.inspector and cronscope.inspection_formatter."""

import pytest
from cronscope.inspector import inspect, InspectionResult, FieldInspection
from cronscope.inspection_formatter import format_inspection


def test_inspect_returns_inspection_result():
    result = inspect("* * * * *")
    assert isinstance(result, InspectionResult)


def test_inspect_valid_expression_no_error():
    result = inspect("0 9 * * 1")
    assert result.error is None
    assert bool(result) is True


def test_inspect_invalid_expression_sets_error():
    result = inspect("99 * * * *")
    assert result.error is not None
    assert bool(result) is False


def test_inspect_produces_five_fields():
    result = inspect("*/5 * * * *")
    assert len(result.fields) == 5


def test_inspect_field_names_are_correct():
    result = inspect("* * * * *")
    names = [f.name for f in result.fields]
    assert names == ["minute", "hour", "day_of_month", "month", "day_of_week"]


def test_inspect_wildcard_field_is_wildcard():
    result = inspect("* * * * *")
    for fi in result.fields:
        assert fi.is_wildcard is True


def test_inspect_step_field_detected():
    result = inspect("*/15 * * * *")
    minute_field = result.fields[0]
    assert minute_field.is_step is True
    assert minute_field.is_wildcard is False


def test_inspect_list_field_detected():
    result = inspect("0,30 * * * *")
    minute_field = result.fields[0]
    assert minute_field.is_list is True


def test_inspect_range_field_detected():
    result = inspect("0 9-17 * * *")
    hour_field = result.fields[1]
    assert hour_field.is_range is True


def test_inspect_human_summary_non_empty():
    result = inspect("0 9 * * 1")
    assert isinstance(result.human_summary, str)
    assert len(result.human_summary) > 0


def test_inspect_raw_values_match_expression():
    result = inspect("30 6 1 * *")
    assert result.fields[0].raw == "30"
    assert result.fields[1].raw == "6"
    assert result.fields[2].raw == "1"


def test_format_inspection_returns_string():
    result = inspect("* * * * *")
    output = format_inspection(result, color=False)
    assert isinstance(output, str)


def test_format_inspection_contains_expression():
    result = inspect("0 12 * * *")
    output = format_inspection(result, color=False)
    assert "0 12 * * *" in output


def test_format_inspection_shows_field_names():
    result = inspect("* * * * *")
    output = format_inspection(result, color=False)
    assert "minute" in output
    assert "hour" in output


def test_format_inspection_invalid_shows_error():
    result = inspect("bad expression")
    output = format_inspection(result, color=False)
    assert "Error" in output


def test_format_inspection_shows_summary():
    result = inspect("0 9 * * 1")
    output = format_inspection(result, color=False)
    assert result.human_summary in output
