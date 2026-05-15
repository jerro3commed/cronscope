"""Cadence analysis: detect regularity and gaps between cron runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from cronscope.scheduler import CronScheduler
from cronscope.parser import CronParseError, parse


@dataclass
class CadenceResult:
    expression: str
    intervals_seconds: List[float] = field(default_factory=list)
    error: Optional[str] = None

    def __bool__(self) -> bool:
        return self.error is None

    @property
    def min_interval(self) -> Optional[timedelta]:
        if not self.intervals_seconds:
            return None
        return timedelta(seconds=min(self.intervals_seconds))

    @property
    def max_interval(self) -> Optional[timedelta]:
        if not self.intervals_seconds:
            return None
        return timedelta(seconds=max(self.intervals_seconds))

    @property
    def avg_interval(self) -> Optional[timedelta]:
        if not self.intervals_seconds:
            return None
        return timedelta(seconds=sum(self.intervals_seconds) / len(self.intervals_seconds))

    @property
    def is_regular(self) -> bool:
        """True if all intervals are equal (perfectly regular cadence)."""
        if len(self.intervals_seconds) < 2:
            return True
        return max(self.intervals_seconds) - min(self.intervals_seconds) < 1.0

    @property
    def longest_gap(self) -> Optional[tuple[timedelta, int]]:
        """Return the longest interval and its index, or None if no intervals exist.

        The index refers to the position in *intervals_seconds* where the gap occurs,
        which corresponds to the gap between run ``index`` and run ``index + 1``.
        """
        if not self.intervals_seconds:
            return None
        idx = max(range(len(self.intervals_seconds)), key=lambda i: self.intervals_seconds[i])
        return timedelta(seconds=self.intervals_seconds[idx]), idx


def analyze_cadence(
    expression: str,
    count: int = 20,
    start: Optional[datetime] = None,
) -> CadenceResult:
    """Compute intervals between the next *count* runs of *expression*."""
    try:
        parse(expression)
    except CronParseError as exc:
        return CadenceResult(expression=expression, error=str(exc))

    if start is None:
        start = datetime.now().replace(second=0, microsecond=0)

    scheduler = CronScheduler(expression)
    runs: List[datetime] = list(scheduler.next_runs(count=count + 1, start=start))

    intervals: List[float] = []
    for i in range(1, len(runs)):
        delta = (runs[i] - runs[i - 1]).total_seconds()
        intervals.append(delta)

    return CadenceResult(expression=expression, intervals_seconds=intervals)
