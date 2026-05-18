"""Rewinder: look back in time and find past runs of a cron expression."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from cronscope.parser import CronParseError, parse
from cronscope.scheduler import CronScheduler


@dataclass
class RewindResult:
    expression: str
    since: datetime
    until: datetime
    runs: List[datetime] = field(default_factory=list)
    error: Optional[str] = None

    def __bool__(self) -> bool:
        return self.error is None

    @property
    def count(self) -> int:
        return len(self.runs)

    @property
    def most_recent(self) -> Optional[datetime]:
        return self.runs[-1] if self.runs else None

    @property
    def earliest(self) -> Optional[datetime]:
        return self.runs[0] if self.runs else None


def rewind(
    expression: str,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    count: int = 10,
) -> RewindResult:
    """Return past runs of *expression* in the window [since, until).

    If *since* is omitted it defaults to *count* hours before *until*.
    If *until* is omitted it defaults to ``datetime.utcnow()``.
    """
    if until is None:
        until = datetime.utcnow().replace(second=0, microsecond=0)
    if since is None:
        since = until - timedelta(hours=count)

    result = RewindResult(expression=expression, since=since, until=until)

    try:
        parse(expression)
    except CronParseError as exc:
        result.error = str(exc)
        return result

    scheduler = CronScheduler(expression)
    cursor = since
    while cursor < until:
        runs = scheduler.next_runs(n=1, after=cursor)
        if not runs:
            break
        run = runs[0]
        if run >= until:
            break
        result.runs.append(run)
        cursor = run + timedelta(minutes=1)

    return result
