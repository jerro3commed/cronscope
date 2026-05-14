"""Calendar-style monthly view of cron expression fire times."""

from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .parser import CronParseError, parse
from .scheduler import CronScheduler


@dataclass
class CalendarMonth:
    """A single month in the calendar view."""

    expression: str
    year: int
    month: int
    fire_days: Dict[int, int] = field(default_factory=dict)  # day -> run count
    error: Optional[str] = None

    def __bool__(self) -> bool:
        return self.error is None

    @property
    def total_runs(self) -> int:
        return sum(self.fire_days.values())

    @property
    def month_name(self) -> str:
        return calendar.month_name[self.month]


def build_calendar(expression: str, year: int, month: int) -> CalendarMonth:
    """Build a CalendarMonth showing which days the expression fires."""
    try:
        parse(expression)
    except CronParseError as exc:
        return CalendarMonth(
            expression=expression,
            year=year,
            month=month,
            error=str(exc),
        )

    _, days_in_month = calendar.monthrange(year, month)
    start = datetime(year, month, 1, 0, 0)
    end = datetime(year, month, days_in_month, 23, 59) + timedelta(minutes=1)

    scheduler = CronScheduler(expression, start=start)
    fire_days: Dict[int, int] = {}

    for run_dt in scheduler.iter_runs():
        if run_dt >= end:
            break
        day = run_dt.day
        fire_days[day] = fire_days.get(day, 0) + 1

    return CalendarMonth(
        expression=expression,
        year=year,
        month=month,
        fire_days=fire_days,
    )
