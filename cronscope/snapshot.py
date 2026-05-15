"""Snapshot: capture and compare cron schedule states at two points in time."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from cronscope.validator import validate
from cronscope.scheduler import CronScheduler


@dataclass
class SnapshotEntry:
    expression: str
    captured_at: datetime
    next_runs: List[datetime]
    error: Optional[str] = None

    def __bool__(self) -> bool:
        return self.error is None


@dataclass
class SnapshotDelta:
    expression: str
    before: SnapshotEntry
    after: SnapshotEntry
    added: List[datetime] = field(default_factory=list)
    removed: List[datetime] = field(default_factory=list)
    unchanged: List[datetime] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed)


def take_snapshot(
    expression: str,
    count: int = 5,
    now: Optional[datetime] = None,
) -> SnapshotEntry:
    """Capture the next *count* runs for *expression* at the current moment."""
    captured_at = now or datetime.now()
    result = validate(expression)
    if not result:
        return SnapshotEntry(
            expression=expression,
            captured_at=captured_at,
            next_runs=[],
            error=result.error,
        )
    scheduler = CronScheduler(expression)
    runs = scheduler.next_runs(count=count, now=captured_at)
    return SnapshotEntry(expression=expression, captured_at=captured_at, next_runs=runs)


def diff_snapshots(before: SnapshotEntry, after: SnapshotEntry) -> SnapshotDelta:
    """Compute which runs were added, removed, or unchanged between two snapshots."""
    before_set = set(before.next_runs)
    after_set = set(after.next_runs)
    return SnapshotDelta(
        expression=after.expression,
        before=before,
        after=after,
        added=sorted(after_set - before_set),
        removed=sorted(before_set - after_set),
        unchanged=sorted(before_set & after_set),
    )
