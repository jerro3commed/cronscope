"""Tests for cronscope.normalizer."""

import pytest
from cronscope.normalizer import normalize, NormalizeResult


def test_normalize_returns_normalize_result():
    result = normalize("* * * * *")
    assert isinstance(result, NormalizeResult)


def test_normalize_valid_expression_no_error():
    result = normalize("0 12 * * *")
    assert result.error is None


def test_normalize_invalid_expression_sets_error():
    result = normalize("99 * * * *")
    assert result.error is not None


def test_normalize_bool_true_for_valid():
    result = normalize("* * * * *")
    assert bool(result) is True


def test_normalize_bool_false_for_invalid():
    result = normalize("invalid")
    assert bool(result) is False


def test_normalize_step_one_becomes_wildcard():
    result = normalize("*/1 * * * *")
    assert result
    assert result.fields[0] == "*"


def test_normalize_step_other_than_one_preserved():
    result = normalize("*/5 * * * *")
    assert result
    assert result.fields[0] == "*/5"


def test_normalize_comma_list_sorted():
    result = normalize("5,3,1 * * * *")
    assert result
    assert result.fields[0] == "1,3,5"


def test_normalize_comma_list_already_sorted_unchanged():
    result = normalize("1,3,5 * * * *")
    assert result
    assert result.fields[0] == "1,3,5"


def test_normalize_preserves_wildcard():
    result = normalize("* * * * *")
    assert result
    assert result.normalized == "* * * * *"


def test_normalize_stores_original():
    expr = "*/1 5,3 * * *"
    result = normalize(expr)
    assert result.original == expr


def test_normalize_produces_five_fields():
    result = normalize("0 0 * * *")
    assert result
    assert len(result.fields) == 5


def test_normalize_macro_daily_expands():
    result = normalize("@daily")
    assert result
    assert result.was_macro is True
    assert result.normalized == "0 0 * * *"


def test_normalize_macro_hourly_expands():
    result = normalize("@hourly")
    assert result
    assert result.was_macro is True
    assert result.normalized == "0 * * * *"


def test_normalize_non_macro_was_macro_false():
    result = normalize("0 12 * * *")
    assert result
    assert result.was_macro is False


def test_normalize_invalid_stores_original_and_no_fields():
    result = normalize("bad expr here")
    assert not result
    assert result.original == "bad expr here"
    assert result.fields == []
    assert result.normalized is None
