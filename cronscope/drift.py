"""Drift analysis: measure how much a cron schedule drifts from a target interval."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from cronscope.scheduler import CronScheduler
from cronscope.parser import CronParseError, parse


@dataclass
class DriftResult:
    expression: str
    target_interval: timedelta
    actual_intervals: List[timedelta] = field(default_factory=list)
    error: Optional[str] = None

    def __bool__(self) -> bool:
        return self.error is None

    @property
    def max_drift(self) -> Optional[timedelta]:
        if not self.actual_intervals:
            return None
        return max(abs(iv - self.target_interval) for iv in self.actual_intervals)

    @property
    def avg_drift(self) -> Optional[timedelta]:
        if not self.actual_intervals:
            return None
        total = sum((abs(iv - self.target_interval) for iv in self.actual_intervals), timedelta())
        return total / len(self.actual_intervals)

    @property
    def is_exact(self) -> bool:
        if not self.actual_intervals:
            return False
        return all(iv == self.target_interval for iv in self.actual_intervals)


def analyze_drift(
    expression: str,
    target_minutes: int,
    count: int = 20,
    start: Optional[datetime] = None,
) -> DriftResult:
    """Analyze how consistently a cron expression fires relative to a target interval."""
    target = timedelta(minutes=target_minutes)
    result = DriftResult(expression=expression, target_interval=target)

    try:
        parse(expression)
    except CronParseError as exc:
        result.error = str(exc)
        return result

    if start is None:
        start = datetime.now().replace(second=0, microsecond=0)

    scheduler = CronScheduler(expression)
    runs = list(scheduler.next_runs(count + 1, after=start))

    if len(runs) < 2:
        result.error = "Not enough run times to compute drift."
        return result

    result.actual_intervals = [
        runs[i + 1] - runs[i] for i in range(len(runs) - 1)
    ]
    return result
