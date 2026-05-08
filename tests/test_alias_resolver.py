"""Tests for cronscope.alias_resolver."""

import pytest

from cronscope.alias_resolver import (
    AliasResolutionError,
    ResolvedAlias,
    is_macro,
    list_macros,
    resolve,
)


# ---------------------------------------------------------------------------
# is_macro
# ---------------------------------------------------------------------------

def test_is_macro_returns_true_for_known_macro():
    assert is_macro("@daily") is True


def test_is_macro_returns_true_for_yearly():
    assert is_macro("@yearly") is True


def test_is_macro_returns_false_for_standard_expression():
    assert is_macro("0 0 * * *") is False


def test_is_macro_is_case_insensitive():
    assert is_macro("@DAILY") is True


def test_is_macro_returns_false_for_unknown_at_expression():
    assert is_macro("@unknown") is False


# ---------------------------------------------------------------------------
# resolve — macros
# ---------------------------------------------------------------------------

def test_resolve_daily_macro():
    result = resolve("@daily")
    assert isinstance(result, ResolvedAlias)
    assert result.resolved == "0 0 * * *"
    assert result.is_macro is True


def test_resolve_hourly_macro():
    result = resolve("@hourly")
    assert result.resolved == "0 * * * *"
    assert result.is_macro is True


def test_resolve_yearly_and_annually_are_equivalent():
    assert resolve("@yearly").resolved == resolve("@annually").resolved


def test_resolve_daily_and_midnight_are_equivalent():
    assert resolve("@daily").resolved == resolve("@midnight").resolved


def test_resolve_macro_preserves_original():
    result = resolve("@weekly")
    assert result.original == "@weekly"


def test_resolve_macro_has_description():
    result = resolve("@monthly")
    assert len(result.description) > 0


def test_resolve_macro_is_case_insensitive():
    result = resolve("@HOURLY")
    assert result.resolved == "0 * * * *"


def test_resolve_macro_strips_whitespace():
    result = resolve("  @daily  ")
    assert result.resolved == "0 0 * * *"


# ---------------------------------------------------------------------------
# resolve — plain expressions
# ---------------------------------------------------------------------------

def test_resolve_plain_expression_returns_unchanged():
    expr = "*/5 * * * *"
    result = resolve(expr)
    assert result.resolved == expr
    assert result.is_macro is False


def test_resolve_plain_expression_has_empty_description():
    result = resolve("0 12 * * 1")
    assert result.description == ""


def test_resolve_plain_expression_preserves_original():
    expr = "30 6 * * 1-5"
    result = resolve(expr)
    assert result.original == expr


# ---------------------------------------------------------------------------
# resolve — errors
# ---------------------------------------------------------------------------

def test_resolve_unknown_macro_raises_error():
    with pytest.raises(AliasResolutionError):
        resolve("@unknown")


def test_resolve_error_message_contains_macro_name():
    with pytest.raises(AliasResolutionError, match="@bogus"):
        resolve("@bogus")


# ---------------------------------------------------------------------------
# list_macros
# ---------------------------------------------------------------------------

def test_list_macros_returns_tuples():
    macros = list_macros()
    assert len(macros) > 0
    assert all(len(m) == 3 for m in macros)


def test_list_macros_contains_daily():
    names = [m[0] for m in list_macros()]
    assert "@daily" in names


def test_list_macros_all_resolve_to_five_fields():
    for _, expression, _ in list_macros():
        assert len(expression.split()) == 5
