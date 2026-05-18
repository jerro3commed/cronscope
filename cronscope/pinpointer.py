"""Pinpointer: find the exact next run at or after a specific datetime."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from cronscope.parser import CronParseError, parse
from cronscope.scheduler import CronScheduler


@dataclass
class PinpointResult:
    """Result of a pinpoint query."""

    expression: str
    target: datetime
    next_run: Optional[datetime]
    previous_run: Optional[datetime]
    delta_seconds: Optional[float]
    error: Optional[str] = None

    def __bool__(self) -> bool:
        return self.error is None

    @property
    def has_next(self) -> bool:
        return self.next_run is not None

    @property
    def has_previous(self) -> bool:
        return self.previous_run is not None

    @property
    def delta_minutes(self) -> Optional[float]:
        if self.delta_seconds is None:
            return None
        return round(self.delta_seconds / 60, 2)


def pinpoint(
    expression: str,
    target: Optional[datetime] = None,
    look_back: int = 5,
) -> PinpointResult:
    """Find the next (and most recent previous) run relative to *target*.

    Args:
        expression: A cron expression string.
        target: The reference datetime (defaults to now).
        look_back: How many past runs to scan when searching for the
                   most recent previous run.

    Returns:
        A :class:`PinpointResult` instance.
    """
    if target is None:
        target = datetime.now().replace(second=0, microsecond=0)

    try:
        parse(expression)
    except CronParseError as exc:
        return PinpointResult(
            expression=expression,
            target=target,
            next_run=None,
            previous_run=None,
            delta_seconds=None,
            error=str(exc),
        )

    scheduler = CronScheduler(expression)

    # Next run at or after target
    upcoming = list(scheduler.next_runs(count=1, start=target))
    next_run = upcoming[0] if upcoming else None

    delta_seconds: Optional[float] = None
    if next_run is not None:
        delta_seconds = (next_run - target).total_seconds()

    # Previous run: scan backwards by collecting runs from a window before target
    from datetime import timedelta

    look_back_start = target - timedelta(hours=24)
    past_runs = list(scheduler.next_runs(count=look_back * 60, start=look_back_start))
    previous_run: Optional[datetime] = None
    for run in reversed(past_runs):
        if run < target:
            previous_run = run
            break

    return PinpointResult(
        expression=expression,
        target=target,
        next_run=next_run,
        previous_run=previous_run,
        delta_seconds=delta_seconds,
    )
