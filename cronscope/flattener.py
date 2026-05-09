"""Flatten multiple cron expressions into a unified sorted run list."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from cronscope.scheduler import CronScheduler
from cronscope.parser import CronParseError, parse


@dataclass
class FlatRun:
    """A single scheduled run with its source expression."""
    dt: datetime
    expression: str

    def __lt__(self, other: "FlatRun") -> bool:
        return self.dt < other.dt


@dataclass
class FlattenedSchedule:
    """Result of flattening multiple cron expressions."""
    runs: List[FlatRun] = field(default_factory=list)
    errors: dict = field(default_factory=dict)  # expr -> error message

    def __bool__(self) -> bool:
        return not self.errors

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    @property
    def valid_expressions(self) -> List[str]:
        return [r.expression for r in self.runs]


def flatten(
    expressions: List[str],
    count: int = 10,
    start: Optional[datetime] = None,
) -> FlattenedSchedule:
    """Collect and sort the next *count* runs across all valid expressions.

    Each expression contributes up to *count* runs; the combined list is then
    sorted chronologically and trimmed to *count* entries.

    Args:
        expressions: List of cron expression strings.
        count: Number of upcoming runs to return in total.
        start: Reference datetime (defaults to now).

    Returns:
        A :class:`FlattenedSchedule` with sorted runs and any parse errors.
    """
    if start is None:
        start = datetime.now()

    result = FlattenedSchedule()
    all_runs: List[FlatRun] = []

    for expr in expressions:
        try:
            parse(expr)  # validate first
        except CronParseError as exc:
            result.errors[expr] = str(exc)
            continue

        sched = CronScheduler(expr)
        for dt in sched.next_runs(count=count, start=start):
            all_runs.append(FlatRun(dt=dt, expression=expr))

    all_runs.sort()
    result.runs = all_runs[:count]
    return result
