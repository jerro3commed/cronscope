"""Tests for CronScheduler next-run logic."""

from datetime import datetime
import pytest

from cronscope.parser import parse
from cronscope.scheduler import CronScheduler


BASE = datetime(2024, 1, 15, 12, 0)  # Monday 2024-01-15 12:00


def _sched(expr: str) -> CronScheduler:
    return CronScheduler(parse(expr), base_time=BASE)


def test_every_minute():
    runs = _sched("* * * * *").next_runs(3)
    assert len(runs) == 3
    assert runs[0] == datetime(2024, 1, 15, 12, 1)
    assert runs[1] == datetime(2024, 1, 15, 12, 2)
    assert runs[2] == datetime(2024, 1, 15, 12, 3)


def test_specific_hour_and_minute():
    runs = _sched("30 14 * * *").next_runs(2)
    assert runs[0] == datetime(2024, 1, 15, 14, 30)
    assert runs[1] == datetime(2024, 1, 16, 14, 30)


def test_specific_day_of_month():
    runs = _sched("0 0 20 * *").next_runs(2)
    assert runs[0] == datetime(2024, 1, 20, 0, 0)
    assert runs[1] == datetime(2024, 2, 20, 0, 0)


def test_specific_month():
    runs = _sched("0 9 1 3 *").next_runs(2)
    assert runs[0] == datetime(2024, 3, 1, 9, 0)
    assert runs[1] == datetime(2025, 3, 1, 9, 0)


def test_weekday_filter():
    # 5 = Friday in cron (1=Mon)
    runs = _sched("0 10 * * 5").next_runs(2)
    for dt in runs:
        assert dt.weekday() == 4  # Python weekday 4 = Friday


def test_iter_runs_is_lazy():
    gen = _sched("* * * * *").iter_runs()
    first = next(gen)
    assert first == datetime(2024, 1, 15, 12, 1)


def test_step_expression():
    runs = _sched("*/15 * * * *").next_runs(4)
    minutes = [r.minute for r in runs[:4]]
    assert 15 in minutes or 0 in minutes  # multiples of 15
    for r in runs:
        assert r.minute % 15 == 0


def test_next_runs_count_matches_requested():
    """next_runs(n) should always return exactly n datetimes."""
    for n in (1, 5, 10):
        runs = _sched("* * * * *").next_runs(n)
        assert len(runs) == n, f"Expected {n} runs, got {len(runs)}"


def test_runs_are_strictly_increasing():
    """Each successive run must be later than the previous one."""
    runs = _sched("*/5 * * * *").next_runs(6)
    for i in range(1, len(runs)):
        assert runs[i] > runs[i - 1], (
            f"Run {i} ({runs[i]}) is not after run {i-1} ({runs[i-1]})"
        )
