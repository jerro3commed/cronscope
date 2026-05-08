"""Compare two cron expressions by their next-run schedules."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .scheduler import CronScheduler
from .parser import CronParseError, parse


@dataclass
class ScheduleComparison:
    """Result of comparing two cron expressions' next-run schedules."""

    left: str
    right: str
    left_error: Optional[str] = None
    right_error: Optional[str] = None
    shared_runs: List[datetime] = field(default_factory=list)
    only_left: List[datetime] = field(default_factory=list)
    only_right: List[datetime] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return self.left_error is not None or self.right_error is not None

    @property
    def overlap_count(self) -> int:
        return len(self.shared_runs)

    @property
    def total_unique(self) -> int:
        return len(self.only_left) + len(self.only_right)


def compare(
    left: str,
    right: str,
    count: int = 10,
    start: Optional[datetime] = None,
) -> ScheduleComparison:
    """Compare the next *count* runs of two cron expressions.

    Returns a :class:`ScheduleComparison` describing which runs are shared
    and which are exclusive to each expression.
    """
    result = ScheduleComparison(left=left, right=right)

    try:
        parse(left)
    except CronParseError as exc:
        result.left_error = str(exc)

    try:
        parse(right)
    except CronParseError as exc:
        result.right_error = str(exc)

    if result.has_errors:
        return result

    now = start or datetime.now()
    left_runs = set(CronScheduler(left).next_runs(count, now))
    right_runs = set(CronScheduler(right).next_runs(count, now))

    result.shared_runs = sorted(left_runs & right_runs)
    result.only_left = sorted(left_runs - right_runs)
    result.only_right = sorted(right_runs - left_runs)

    return result
