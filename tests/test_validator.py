"""Tests for cronscope.validator module."""

import pytest
from cronscope.validator import validate, validate_many, is_valid, ValidationResult


def test_validate_valid_expression_returns_valid_result():
    result = validate("* * * * *")
    assert result.valid is True
    assert result.error is None
    assert result.expression == "* * * * *"


def test_validate_valid_expression_includes_fields():
    result = validate("30 8 * * 1")
    assert result.fields is not None
    assert result.fields["minute"] == "30"
    assert result.fields["hour"] == "8"
    assert result.fields["day_of_week"] == "1"


def test_validate_invalid_expression_returns_invalid_result():
    result = validate("99 * * * *")
    assert result.valid is False
    assert result.error is not None
    assert len(result.error) > 0


def test_validate_too_few_fields():
    result = validate("* * *")
    assert result.valid is False
    assert result.error is not None


def test_validate_too_many_fields():
    result = validate("* * * * * *")
    assert result.valid is False


def test_validate_result_bool_true():
    result = validate("0 12 * * *")
    assert bool(result) is True


def test_validate_result_bool_false():
    result = validate("invalid")
    assert bool(result) is False


def test_validate_with_step():
    result = validate("*/15 * * * *")
    assert result.valid is True
    assert result.fields["minute"] == "*/15"


def test_validate_with_alias():
    result = validate("0 0 * jan *")
    assert result.valid is True


def test_validate_many_mixed():
    expressions = ["* * * * *", "bad expr", "0 6 * * 1"]
    results = validate_many(expressions)
    assert len(results) == 3
    assert results[0].valid is True
    assert results[1].valid is False
    assert results[2].valid is True


def test_validate_many_preserves_order():
    expressions = ["0 1 * * *", "0 2 * * *", "0 3 * * *"]
    results = validate_many(expressions)
    for i, result in enumerate(results):
        assert result.expression == expressions[i]
        assert result.valid is True


def test_is_valid_true():
    assert is_valid("0 0 1 1 *") is True


def test_is_valid_false():
    assert is_valid("60 * * * *") is False


def test_validate_stores_expression():
    expr = "5 4 * * sun"
    result = validate(expr)
    assert result.expression == expr
