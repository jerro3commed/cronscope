"""Tests for cronscope.grouper."""

import pytest
from cronscope.grouper import group, GroupedSchedule, ExpressionGroup


EVERY_MINUTE = "* * * * *"
HOURLY = "0 * * * *"
DAILY_MIDNIGHT = "0 0 * * *"
WEEKLY = "0 9 * * 1"
INVALID = "bad expression"


def test_group_returns_grouped_schedule():
    result = group([EVERY_MINUTE])
    assert isinstance(result, GroupedSchedule)


def test_group_by_frequency_places_every_minute_in_high_frequency():
    result = group([EVERY_MINUTE], by="frequency")
    labels = result.group_labels
    assert any("minute" in lbl or "high" in lbl or "frequent" in lbl for lbl in labels)


def test_group_invalid_expression_goes_to_invalid_group():
    result = group([INVALID], by="frequency")
    assert "invalid" in result.groups
    assert result.groups["invalid"].has_errors


def test_group_invalid_expression_stores_error_message():
    result = group([INVALID], by="frequency")
    grp = result.groups["invalid"]
    assert INVALID in grp.errors
    assert isinstance(grp.errors[INVALID], str)
    assert len(grp.errors[INVALID]) > 0


def test_group_by_hour_uses_hour_field_as_label():
    result = group([HOURLY], by="hour")
    assert "hour:*" in result.groups
    assert HOURLY in result.groups["hour:*"].expressions


def test_group_by_day_uses_dow_field_as_label():
    result = group([WEEKLY], by="day")
    assert "dow:1" in result.groups
    assert WEEKLY in result.groups["dow:1"].expressions


def test_group_unknown_strategy_puts_in_ungrouped():
    result = group([EVERY_MINUTE], by="unknown_strategy")
    assert EVERY_MINUTE in result.ungrouped


def test_group_multiple_expressions_same_group():
    result = group([EVERY_MINUTE, HOURLY], by="hour")
    assert result.total_expressions == 2


def test_group_total_expressions_counts_all():
    result = group([EVERY_MINUTE, DAILY_MIDNIGHT, INVALID], by="frequency")
    assert result.total_expressions == 3


def test_expression_group_bool_true_when_has_expressions():
    grp = ExpressionGroup(label="test", expressions=[EVERY_MINUTE])
    assert bool(grp) is True


def test_expression_group_bool_false_when_empty():
    grp = ExpressionGroup(label="test")
    assert bool(grp) is False


def test_group_labels_are_sorted():
    result = group([EVERY_MINUTE, DAILY_MIDNIGHT], by="hour")
    labels = result.group_labels
    assert labels == sorted(labels)
