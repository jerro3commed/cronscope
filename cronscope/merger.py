"""Merge multiple cron expressions into a unified schedule summary."""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from cronscope.validator import validate
from cronscope.scheduler import CronScheduler


@dataclass
class MergedSchedule:
    """Result of merging multiple cron expressions."""

    expressions: List[str]
    errors: dict  # expr -> error message
    next_runs: List[tuple]  # (datetime, expr)
    count: int

    def has_errors(self) -> bool:
        return bool(self.errors)

    def valid_expressions(self) -> List[str]:
        return [e for e in self.expressions if e not in self.errors]

    def invalid_expressions(self) -> List[str]:
        return list(self.errors.keys())


def merge(
    expressions: List[str],
    count: int = 5,
    start: Optional[datetime] = None,
) -> MergedSchedule:
    """Merge multiple cron expressions into a unified chronological schedule.

    Args:
        expressions: List of cron expression strings.
        count: Total number of upcoming run entries to collect.
        start: Reference datetime (defaults to now).

    Returns:
        MergedSchedule with combined next runs sorted chronologically.
    """
    if start is None:
        start = datetime.now().replace(second=0, microsecond=0)

    errors: dict = {}
    candidates: List[tuple] = []  # (datetime, expr)

    for expr in expressions:
        result = validate(expr)
        if not result:
            errors[expr] = result.error or "Invalid expression"
            continue

        try:
            sched = CronScheduler(expr)
            runs = sched.next_runs(count=count, start=start)
            for dt in runs:
                candidates.append((dt, expr))
        except Exception as exc:  # pragma: no cover
            errors[expr] = str(exc)

    candidates.sort(key=lambda pair: pair[0])
    top = candidates[:count]

    return MergedSchedule(
        expressions=expressions,
        errors=errors,
        next_runs=top,
        count=count,
    )
