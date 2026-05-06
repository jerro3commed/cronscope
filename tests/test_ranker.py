"""Tests for cronscope.ranker and cronscope.rank_formatter."""

import pytest
from cronscope.ranker import rank, RankedExpression
from cronscope.rank_formatter import format_rank


def test_rank_returns_list_of_ranked_expressions():
    results = rank(["* * * * *", "0 * * * *"])
    assert isinstance(results, list)
    assert all(isinstance(r, RankedExpression) for r in results)


def test_rank_most_frequent_is_first():
    results = rank(["0 * * * *", "* * * * *"])
    assert results[0].runs_per_day > results[1].runs_per_day
    assert results[0].rank == 1


def test_rank_assigns_sequential_ranks():
    results = rank(["0 0 * * *", "0 * * * *", "* * * * *"])
    valid = [r for r in results if r.error is None]
    ranks = sorted(r.rank for r in valid)
    assert ranks == list(range(1, len(valid) + 1))


def test_rank_invalid_expression_has_error():
    results = rank(["not_a_cron"])
    assert results[0].error is not None
    assert results[0].runs_per_day == 0.0


def test_rank_mixed_valid_and_invalid():
    results = rank(["* * * * *", "bad expr", "0 0 * * *"])
    valid = [r for r in results if r.error is None]
    invalid = [r for r in results if r.error is not None]
    assert len(valid) == 2
    assert len(invalid) == 1


def test_rank_with_labels():
    results = rank(["* * * * *", "0 0 * * *"], labels=["every minute", "daily"])
    labels = {r.expression: r.label for r in results}
    assert labels["* * * * *"] == "every minute"
    assert labels["0 0 * * *"] == "daily"


def test_rank_bool_true_for_valid():
    results = rank(["* * * * *"])
    assert bool(results[0]) is True


def test_rank_bool_false_for_invalid():
    results = rank(["invalid"])
    assert bool(results[0]) is False


def test_format_rank_returns_string():
    results = rank(["* * * * *", "0 0 * * *"])
    output = format_rank(results)
    assert isinstance(output, str)


def test_format_rank_contains_expression():
    results = rank(["0 12 * * *"])
    output = format_rank(results, color=False)
    assert "0 12 * * *" in output


def test_format_rank_contains_rank_number():
    results = rank(["* * * * *"])
    output = format_rank(results, color=False)
    assert "#1" in output


def test_format_rank_empty_list():
    output = format_rank([], color=False)
    assert "No expressions" in output


def test_format_rank_shows_error_for_invalid(capsys):
    results = rank(["bad"])
    output = format_rank(results, color=False)
    assert "ERROR" in output
