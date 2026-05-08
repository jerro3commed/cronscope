"""Timeline module: bucket cron runs into time windows for calendar-style visualization."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from cronscope.scheduler import CronScheduler
from cronscope.parser import CronParseError, parse


@dataclass
class TimelineWindow:
    """A single time window (e.g. one hour or one day) with its scheduled runs."""

    label: str
    start: datetime
    end: datetime
    runs: List[datetime] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.runs)

    def __bool__(self) -> bool:
        return bool(self.runs)


@dataclass
class Timeline:
    """Collection of time windows for a cron expression."""

    expression: str
    windows: List[TimelineWindow] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def total_runs(self) -> int:
        return sum(w.count for w in self.windows)

    def __bool__(self) -> bool:
        return self.error is None


def _window_label(start: datetime, granularity: str) -> str:
    if granularity == "hour":
        return start.strftime("%Y-%m-%d %H:00")
    return start.strftime("%Y-%m-%d")


def build_timeline(
    expression: str,
    start: Optional[datetime] = None,
    periods: int = 24,
    granularity: str = "hour",
) -> Timeline:
    """Build a Timeline by bucketing next runs into windows.

    Args:
        expression: A cron expression string.
        start: Window start (defaults to now).
        periods: Number of windows to generate.
        granularity: 'hour' or 'day'.
    """
    if granularity not in ("hour", "day"):
        raise ValueError("granularity must be 'hour' or 'day'")

    try:
        parse(expression)
    except CronParseError as exc:
        return Timeline(expression=expression, error=str(exc))

    now = start or datetime.now().replace(second=0, microsecond=0)
    delta = timedelta(hours=1) if granularity == "hour" else timedelta(days=1)

    windows: List[TimelineWindow] = []
    for i in range(periods):
        w_start = now + i * delta
        w_end = w_start + delta
        windows.append(
            TimelineWindow(
                label=_window_label(w_start, granularity),
                start=w_start,
                end=w_end,
            )
        )

    horizon = now + periods * delta
    scheduler = CronScheduler(expression)
    for run in scheduler.iter_runs(start=now, count=10_000):
        if run >= horizon:
            break
        for window in windows:
            if window.start <= run < window.end:
                window.runs.append(run)
                break

    return Timeline(expression=expression, windows=windows)
