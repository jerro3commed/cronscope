"""Profile cron expressions by analyzing their run distribution across time slots."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from .scheduler import CronScheduler
from .parser import CronParseError


@dataclass
class ProfileResult:
    expression: str
    error: Optional[str] = None
    runs_per_hour: Dict[int, int] = field(default_factory=dict)
    runs_per_weekday: Dict[int, int] = field(default_factory=dict)
    busiest_hour: Optional[int] = None
    busiest_weekday: Optional[int] = None
    total_runs: int = 0
    sample_days: int = 0

    def __bool__(self) -> bool:
        return self.error is None


WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def profile(
    expression: str,
    start: Optional[datetime] = None,
    sample_days: int = 7,
) -> ProfileResult:
    """Profile a cron expression over a sample window of days."""
    if start is None:
        start = datetime.now().replace(second=0, microsecond=0)

    try:
        sched = CronScheduler(expression, start)
    except CronParseError as exc:
        return ProfileResult(expression=expression, error=str(exc))

    from datetime import timedelta

    end = start + timedelta(days=sample_days)
    runs_per_hour: Dict[int, int] = {h: 0 for h in range(24)}
    runs_per_weekday: Dict[int, int] = {d: 0 for d in range(7)}
    total = 0

    for run_dt in sched.iter_runs():
        if run_dt >= end:
            break
        runs_per_hour[run_dt.hour] += 1
        runs_per_weekday[run_dt.weekday()] += 1
        total += 1

    busiest_hour = max(runs_per_hour, key=lambda h: runs_per_hour[h]) if total else None
    busiest_weekday = (
        max(runs_per_weekday, key=lambda d: runs_per_weekday[d]) if total else None
    )

    return ProfileResult(
        expression=expression,
        runs_per_hour=runs_per_hour,
        runs_per_weekday=runs_per_weekday,
        busiest_hour=busiest_hour,
        busiest_weekday=busiest_weekday,
        total_runs=total,
        sample_days=sample_days,
    )
