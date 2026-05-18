"""Tests for cronscope.deduplicator."""

import pytest

from cronscope.deduplicator import DeduplicatedGroup, DeduplicationResult, deduplicate


def test_deduplicate_returns_deduplication_result():
    result = deduplicate(["* * * * *"])
    assert isinstance(result, DeduplicationResult)


def test_deduplicate_single_unique_expression():
    result = deduplicate(["* * * * *"])
    assert result.unique_count == 1
    assert result.duplicate_count == 0


def test_deduplicate_identical_expressions_grouped():
    result = deduplicate(["0 12 * * *", "0 12 * * *"])
    assert result.unique_count == 1
    assert result.groups[0].count == 2


def test_deduplicate_duplicate_flag_set():
    result = deduplicate(["0 0 * * *", "0 0 * * *"])
    assert result.groups[0].is_duplicate is True


def test_deduplicate_no_duplicate_flag_for_single():
    result = deduplicate(["0 6 * * 1"])
    assert result.groups[0].is_duplicate is False


def test_deduplicate_distinct_expressions_separate_groups():
    result = deduplicate(["* * * * *", "0 0 * * *"])
    assert result.unique_count == 2


def test_deduplicate_invalid_expression_goes_to_invalid():
    result = deduplicate(["not a cron"])
    assert len(result.invalid) == 1
    assert result.unique_count == 0


def test_deduplicate_invalid_stores_expression_and_message():
    result = deduplicate(["bad expr"])
    expr, msg = result.invalid[0]
    assert expr == "bad expr"
    assert isinstance(msg, str) and len(msg) > 0


def test_deduplicate_mixed_valid_and_invalid():
    result = deduplicate(["* * * * *", "!!!"])
    assert result.unique_count == 1
    assert len(result.invalid) == 1


def test_deduplicate_total_expressions_counts_all():
    result = deduplicate(["* * * * *", "0 0 * * *", "bad"])
    assert result.total_expressions == 3


def test_deduplicate_group_bool_true_for_valid():
    result = deduplicate(["* * * * *"])
    assert bool(result.groups[0]) is True


def test_deduplicate_canonical_is_normalized_form():
    result = deduplicate(["0 12 * * *"])
    canonical = result.groups[0].canonical
    assert isinstance(canonical, str)
    assert len(canonical) > 0


def test_deduplicate_empty_list_returns_empty_result():
    result = deduplicate([])
    assert result.unique_count == 0
    assert len(result.invalid) == 0
    assert result.total_expressions == 0
