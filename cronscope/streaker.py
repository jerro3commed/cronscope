"""Streak analysis: find longest consecutive day runs for a cron expression."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from cronscope.scheduler import CronScheduler
from cronscope.parser import parse, CronParseError


@dataclass
class StreakResult:
    expression: str
    longest_streak: int
    current_streak: int
    streak_start: Optional[datetime]
    streak_end: Optional[datetime]
    error: Optional[str] = None
    _days_checked: List[datetime] = field(default_factory=list, repr=False)

    def __bool__(self) -> bool:
        return self.error is None


def _active_days(expression: str, since: datetime, days: int) -> List[datetime]:
    """Return list of dates (day precision) on which the expression fires."""
    sched = CronScheduler(expression)
    end = since + timedelta(days=days)
    active = set()
    for run in sched.iter_runs(since):
        if run >= end:
            break
        active.add(run.date())
    return sorted(active)


def streak(expression: str, since: Optional[datetime] = None, days: int = 30) -> StreakResult:
    """Analyse consecutive active days for *expression* over a window of *days*."""
    if since is None:
        since = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        parse(expression)
    except CronParseError as exc:
        return StreakResult(
            expression=expression,
            longest_streak=0,
            current_streak=0,
            streak_start=None,
            streak_end=None,
            error=str(exc),
        )

    active_dates = _active_days(expression, since, days)

    if not active_dates:
        return StreakResult(
            expression=expression,
            longest_streak=0,
            current_streak=0,
            streak_start=None,
            streak_end=None,
        )

    longest = current = 1
    longest_start = longest_end = active_dates[0]
    cur_start = active_dates[0]

    for prev, cur in zip(active_dates, active_dates[1:]):
        if (cur - prev).days == 1:
            current += 1
            if current > longest:
                longest = current
                longest_start = cur_start
                longest_end = cur
        else:
            current = 1
            cur_start = cur

    today = since.date()
    current_streak = 0
    for d in reversed(active_dates):
        if (today - d).days == current_streak:
            current_streak += 1
        else:
            break

    return StreakResult(
        expression=expression,
        longest_streak=longest,
        current_streak=current_streak,
        streak_start=datetime.combine(longest_start, datetime.min.time()),
        streak_end=datetime.combine(longest_end, datetime.min.time()),
        _days_checked=active_dates,
    )
