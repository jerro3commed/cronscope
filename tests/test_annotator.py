"""Tests for cronscope.annotator and cronscope.annotation_formatter."""

import pytest
from cronscope.annotator import annotate, AnnotatedExpression, AnnotatedField
from cronscope.annotation_formatter import format_annotation


# ---------------------------------------------------------------------------
# annotate()
# ---------------------------------------------------------------------------

def test_annotate_returns_annotated_expression():
    result = annotate("* * * * *")
    assert isinstance(result, AnnotatedExpression)


def test_annotate_wildcard_expression_has_no_error():
    result = annotate("* * * * *")
    assert bool(result) is True
    assert result.error is None


def test_annotate_wildcard_produces_five_fields():
    result = annotate("* * * * *")
    assert len(result.fields) == 5


def test_annotate_wildcard_notes_say_every():
    result = annotate("* * * * *")
    for field in result.fields:
        assert "every" in field.note


def test_annotate_step_field_note():
    result = annotate("*/15 * * * *")
    minute_field = result.fields[0]
    assert "15" in minute_field.note
    assert "minute" in minute_field.note


def test_annotate_specific_hour():
    result = annotate("0 9 * * *")
    hour_field = result.fields[1]
    assert "9" in hour_field.note


def test_annotate_range_field():
    result = annotate("0 9-17 * * *")
    hour_field = result.fields[1]
    assert "9" in hour_field.note
    assert "17" in hour_field.note


def test_annotate_comma_list_field():
    result = annotate("0 0 * * 1,3,5")
    dow_field = result.fields[4]
    assert "Mon" in dow_field.note or "1" in dow_field.note


def test_annotate_month_number_shows_name():
    result = annotate("0 0 1 6 *")
    month_field = result.fields[3]
    assert "Jun" in month_field.note


def test_annotate_invalid_expression_sets_error():
    result = annotate("not a cron")
    assert bool(result) is False
    assert result.error is not None
    assert len(result.fields) == 0


def test_annotate_stores_raw_expression():
    expr = "30 6 * * 1"
    result = annotate(expr)
    assert result.expression == expr


# ---------------------------------------------------------------------------
# format_annotation()
# ---------------------------------------------------------------------------

def test_format_annotation_returns_string():
    ann = annotate("* * * * *")
    out = format_annotation(ann, color=False)
    assert isinstance(out, str)


def test_format_annotation_contains_expression():
    ann = annotate("0 12 * * *")
    out = format_annotation(ann, color=False)
    assert "0 12 * * *" in out


def test_format_annotation_contains_field_names():
    ann = annotate("* * * * *")
    out = format_annotation(ann, color=False)
    assert "minute" in out
    assert "hour" in out


def test_format_annotation_shows_error_for_invalid():
    ann = annotate("bad expr")
    out = format_annotation(ann, color=False)
    assert "Error" in out


def test_format_annotation_no_color_has_no_escape_codes():
    ann = annotate("*/5 * * * *")
    out = format_annotation(ann, color=False)
    assert "\033[" not in out


def test_format_annotation_with_color_has_escape_codes():
    ann = annotate("*/5 * * * *")
    out = format_annotation(ann, color=True)
    assert "\033[" in out
