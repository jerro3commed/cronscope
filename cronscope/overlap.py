"""Detect and report time-slot overlaps across multiple cron expressions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from cronscope.scheduler import CronScheduler
from cronscope.parser import parse, CronParseError


@dataclass
class OverlapSlot:
    """A single datetime where two or more expressions fire simultaneously."""

    timestamp: datetime
    expressions: List[str]


@dataclass
class OverlapReport:
    """Result of an overlap analysis across a set of cron expressions."""

    expressions: List[str]
    slots: List[OverlapSlot]
    errors: Dict[str, str] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return not self.errors

    @property
    def has_overlaps(self) -> bool:
        return len(self.slots) > 0

    @property
    def overlap_count(self) -> int:
        return len(self.slots)


def find_overlaps(
    expressions: List[str],
    count: int = 50,
    start: Optional[datetime] = None,
) -> OverlapReport:
    """Find datetime slots where more than one expression fires at the same time.

    Args:
        expressions: List of cron expression strings to analyse.
        count: Number of upcoming runs to sample per expression.
        start: Reference start datetime (defaults to now).

    Returns:
        OverlapReport with all overlapping slots and any parse errors.
    """
    errors: Dict[str, str] = {}
    run_map: Dict[datetime, List[str]] = {}

    for expr in expressions:
        try:
            parsed = parse(expr)
        except CronParseError as exc:
            errors[expr] = str(exc)
            continue

        sched = CronScheduler(parsed)
        runs = sched.next_runs(count=count, start=start)
        for dt in runs:
            run_map.setdefault(dt, []).append(expr)

    slots = [
        OverlapSlot(timestamp=ts, expressions=exprs)
        for ts, exprs in sorted(run_map.items())
        if len(exprs) > 1
    ]

    return OverlapReport(expressions=expressions, slots=slots, errors=errors)
