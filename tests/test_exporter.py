"""Tests for cronscope.exporter module."""

import json
from datetime import datetime

import pytest

from cronscope.exporter import export_json, export_text

START = datetime(2024, 1, 15, 12, 0, 0)


# ---------------------------------------------------------------------------
# export_text
# ---------------------------------------------------------------------------

def test_export_text_contains_expression():
    output = export_text("0 9 * * 1", count=3, start=START)
    assert "0 9 * * 1" in output


def test_export_text_contains_run_lines():
    output = export_text("0 9 * * 1", count=3, start=START)
    assert "1." in output
    assert "2." in output
    assert "3." in output


def test_export_text_respects_count():
    output = export_text("* * * * *", count=4, start=START)
    # Each run line starts with a number followed by a dot
    run_lines = [l for l in output.splitlines() if l.strip() and l.strip()[0].isdigit()]
    assert len(run_lines) == 4


def test_export_text_with_label():
    output = export_text("*/5 * * * *", count=2, start=START, label="My Job")
    assert "My Job" in output
    assert "---" in output  # separator line


def test_export_text_without_label_has_no_separator():
    output = export_text("*/5 * * * *", count=2, start=START)
    assert "---" not in output


def test_export_text_invalid_expression_raises():
    with pytest.raises(ValueError, match="Invalid cron expression"):
        export_text("not a cron", count=3, start=START)


# ---------------------------------------------------------------------------
# export_json
# ---------------------------------------------------------------------------

def test_export_json_is_valid_json():
    raw = export_json("0 0 * * *", count=3, start=START)
    data = json.loads(raw)  # should not raise
    assert isinstance(data, dict)


def test_export_json_contains_expression():
    data = json.loads(export_json("0 0 * * *", count=3, start=START))
    assert data["expression"] == "0 0 * * *"


def test_export_json_next_runs_length():
    data = json.loads(export_json("* * * * *", count=5, start=START))
    assert len(data["next_runs"]) == 5


def test_export_json_iso_format():
    data = json.loads(export_json("0 6 * * *", count=1, start=START))
    run = data["next_runs"][0]
    # Should parse as ISO-like datetime without error
    datetime.strptime(run, "%Y-%m-%dT%H:%M:00")


def test_export_json_with_label():
    data = json.loads(export_json("30 8 * * *", count=2, start=START, label="Backup"))
    assert data["label"] == "Backup"


def test_export_json_without_label_key_absent():
    data = json.loads(export_json("30 8 * * *", count=2, start=START))
    assert "label" not in data


def test_export_json_invalid_expression_raises():
    with pytest.raises(ValueError, match="Invalid cron expression"):
        export_json("bad expr", count=3, start=START)
