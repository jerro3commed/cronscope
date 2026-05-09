"""Tests for cronscope.flattener."""

from datetime import datetime

import pytest

from cronscope.flattener import flatten, FlatRun, FlattenedSchedule


START = datetime(2024, 1, 15, 12, 0, 0)


def test_flatten_returns_flattened_schedule():
    result = flatten(["* * * * *"], count=5, start=START)
    assert isinstance(result, FlattenedSchedule)


def test_flatten_runs_are_flat_run_instances():
    result = flatten(["* * * * *"], count=3, start=START)
    for run in result.runs:
        assert isinstance(run, FlatRun)


def test_flatten_single_expression_respects_count():
    result = flatten(["* * * * *"], count=5, start=START)
    assert len(result.runs) == 5


def test_flatten_runs_are_sorted_chronologically():
    result = flatten(["0 * * * *", "30 * * * *"], count=6, start=START)
    dts = [r.dt for r in result.runs]
    assert dts == sorted(dts)


def test_flatten_run_carries_source_expression():
    result = flatten(["0 9 * * *"], count=2, start=START)
    for run in result.runs:
        assert run.expression == "0 9 * * *"


def test_flatten_multiple_expressions_mixed_sources():
    result = flatten(["0 8 * * *", "0 20 * * *"], count=4, start=START)
    sources = {r.expression for r in result.runs}
    assert "0 8 * * *" in sources
    assert "0 20 * * *" in sources


def test_flatten_invalid_expression_recorded_in_errors():
    result = flatten(["not a cron"], count=5, start=START)
    assert "not a cron" in result.errors


def test_flatten_invalid_expression_has_no_runs():
    result = flatten(["not a cron"], count=5, start=START)
    assert result.runs == []


def test_flatten_mixed_valid_and_invalid():
    result = flatten(["* * * * *", "bad expr"], count=3, start=START)
    assert len(result.runs) == 3
    assert "bad expr" in result.errors


def test_flatten_bool_false_when_errors():
    result = flatten(["bad"], count=5, start=START)
    assert not bool(result)


def test_flatten_bool_true_when_no_errors():
    result = flatten(["* * * * *"], count=3, start=START)
    assert bool(result)


def test_flatten_has_errors_property():
    result = flatten(["bad"], count=5, start=START)
    assert result.has_errors is True


def test_flatten_total_capped_at_count():
    # Two high-frequency expressions; total should still be capped.
    result = flatten(["* * * * *", "*/2 * * * *"], count=5, start=START)
    assert len(result.runs) <= 5


def test_flat_run_ordering():
    a = FlatRun(dt=datetime(2024, 1, 15, 12, 0), expression="a")
    b = FlatRun(dt=datetime(2024, 1, 15, 13, 0), expression="b")
    assert a < b
