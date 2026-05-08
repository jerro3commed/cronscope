"""Tests for cronscope.group_formatter."""

import pytest
from cronscope.grouper import group
from cronscope.group_formatter import format_group


EVERY_MINUTE = "* * * * *"
HOURLY = "0 * * * *"
INVALID = "not a cron"


def test_format_group_returns_string():
    grouped = group([EVERY_MINUTE])
    result = format_group(grouped)
    assert isinstance(result, str)


def test_format_group_contains_header():
    grouped = group([EVERY_MINUTE])
    result = format_group(grouped, color=False)
    assert "Grouped Cron Expressions" in result


def test_format_group_contains_expression():
    grouped = group([EVERY_MINUTE])
    result = format_group(grouped, color=False)
    assert EVERY_MINUTE in result


def test_format_group_shows_group_label():
    grouped = group([HOURLY], by="hour")
    result = format_group(grouped, color=False)
    assert "hour:*" in result


def test_format_group_shows_invalid_label():
    grouped = group([INVALID])
    result = format_group(grouped, color=False)
    assert "invalid" in result


def test_format_group_shows_error_for_invalid():
    grouped = group([INVALID])
    result = format_group(grouped, color=False)
    assert INVALID in result


def test_format_group_shows_total_line():
    grouped = group([EVERY_MINUTE, HOURLY])
    result = format_group(grouped, color=False)
    assert "Total:" in result


def test_format_group_empty_input_shows_no_expressions_message():
    grouped = group([])
    result = format_group(grouped, color=False)
    assert "No expressions" in result


def test_format_group_shows_ungrouped_section():
    grouped = group([EVERY_MINUTE], by="unknown")
    result = format_group(grouped, color=False)
    assert "ungrouped" in result


def test_format_group_no_color_has_no_ansi():
    grouped = group([EVERY_MINUTE])
    result = format_group(grouped, color=False)
    assert "\033[" not in result


def test_format_group_with_color_has_ansi():
    grouped = group([EVERY_MINUTE])
    result = format_group(grouped, color=True)
    assert "\033[" in result
