"""Tests for cronscope.summarizer."""

import pytest
from unittest.mock import patch
from datetime import datetime
from cronscope.summarizer import summarize, summarize_table


FIXED_DT = [
    datetime(2024, 1, 15, 10, 0, 0),
    datetime(2024, 1, 15, 10, 1, 0),
    datetime(2024, 1, 15, 10, 2, 0),
]


@pytest.fixture(autouse=True)
def _patch_scheduler(monkeypatch):
    """Patch CronScheduler.next_runs to return fixed datetimes."""
    from cronscope import scheduler as sched_mod
    original = sched_mod.CronScheduler.next_runs

    def _fake_next_runs(self, n=5):
        return FIXED_DT[:n]

    monkeypatch.setattr(sched_mod.CronScheduler, "next_runs", _fake_next_runs)


def test_summarize_returns_list_of_dicts():
    results = summarize(["* * * * *"])
    assert isinstance(results, list)
    assert len(results) == 1
    assert isinstance(results[0], dict)


def test_summarize_valid_expression_keys():
    row = summarize(["0 9 * * 1"])[0]
    assert row["valid"] is True
    assert row["error"] is None
    assert row["expression"] == "0 9 * * 1"
    assert row["label"] == "expr_1"
    assert isinstance(row["human"], str)
    assert isinstance(row["next_runs"], list)


def test_summarize_invalid_expression():
    row = summarize(["not a cron"])[0]
    assert row["valid"] is False
    assert row["error"] is not None
    assert row["next_runs"] == []
    assert row["human"] is None


def test_summarize_multiple_expressions():
    results = summarize(["* * * * *", "0 0 * * *", "bad expr"])
    assert len(results) == 3
    assert results[0]["valid"] is True
    assert results[1]["valid"] is True
    assert results[2]["valid"] is False


def test_summarize_next_runs_count():
    row = summarize(["* * * * *"], count=2)[0]
    assert len(row["next_runs"]) == 2


def test_summarize_next_runs_are_iso_strings():
    row = summarize(["* * * * *"], count=1)[0]
    dt_str = row["next_runs"][0]
    # Should be parseable as ISO format
    datetime.fromisoformat(dt_str)


def test_summarize_custom_label_prefix():
    results = summarize(["* * * * *", "0 0 * * *"], label_prefix="job")
    assert results[0]["label"] == "job_1"
    assert results[1]["label"] == "job_2"


def test_summarize_table_returns_string():
    table = summarize_table(["* * * * *", "0 0 * * *"])
    assert isinstance(table, str)


def test_summarize_table_contains_expression():
    table = summarize_table(["* * * * *"])
    assert "* * * * *" in table


def test_summarize_table_contains_header():
    table = summarize_table(["* * * * *"])
    assert "Expression" in table
    assert "Valid" in table


def test_summarize_table_marks_invalid():
    table = summarize_table(["bad expr"])
    assert "no" in table
