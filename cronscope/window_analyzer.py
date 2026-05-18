"""Analyze how many times a cron expression fires within named time windows."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from cronscope.scheduler import CronScheduler
from cronscope.parser import CronParseError


@dataclass
class WindowCount:
    label: str
    start: datetime
    end: datetime
    count: int

    def __bool__(self) -> bool:
        return self.count > 0


@dataclass
class WindowAnalysis:
    expression: str
    windows: List[WindowCount] = field(default_factory=list)
    error: Optional[str] = None

    def __bool__(self) -> bool:
        return self.error is None

    @property
    def total(self) -> int:
        return sum(w.count for w in self.windows)

    @property
    def busiest(self) -> Optional[WindowCount]:
        if not self.windows:
            return None
        return max(self.windows, key=lambda w: w.count)

    @property
    def quietest(self) -> Optional[WindowCount]:
        if not self.windows:
            return None
        return min(self.windows, key=lambda w: w.count)


def analyze_windows(
    expression: str,
    now: Optional[datetime] = None,
    days: int = 7,
    window_hours: int = 6,
) -> WindowAnalysis:
    """Count cron fires in equal-sized windows over the given number of days."""
    if now is None:
        now = datetime.now().replace(second=0, microsecond=0)

    try:
        sched = CronScheduler(expression)
    except CronParseError as exc:
        return WindowAnalysis(expression=expression, error=str(exc))

    total_hours = days * 24
    num_windows = total_hours // window_hours

    # Collect all runs in the full range
    end_of_range = now + timedelta(days=days)
    all_runs = list(sched.iter_runs(now, limit=100_000, end=end_of_range))

    windows: List[WindowCount] = []
    for i in range(num_windows):
        w_start = now + timedelta(hours=i * window_hours)
        w_end = w_start + timedelta(hours=window_hours)
        label = w_start.strftime("%a %d %b %H:%M")
        count = sum(1 for r in all_runs if w_start <= r < w_end)
        windows.append(WindowCount(label=label, start=w_start, end=w_end, count=count))

    return WindowAnalysis(expression=expression, windows=windows)
