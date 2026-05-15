"""Field-level matching utility: checks whether a given datetime satisfies each
cron field independently and reports which fields matched or failed."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from .parser import CronParseError, parse


FIELD_NAMES = ("minute", "hour", "day", "month", "weekday")


@dataclass
class FieldMatchResult:
    name: str
    pattern: str
    value: int
    matched: bool

    def __bool__(self) -> bool:  # noqa: D105
        return self.matched


@dataclass
class MatchResult:
    expression: str
    dt: datetime
    error: Optional[str] = None
    fields: List[FieldMatchResult] = field(default_factory=list)

    def __bool__(self) -> bool:  # noqa: D105
        return self.error is None and all(f.matched for f in self.fields)

    @property
    def matched(self) -> bool:
        return bool(self)

    @property
    def failed_fields(self) -> List[FieldMatchResult]:
        return [f for f in self.fields if not f.matched]


def _field_matches(pattern: str, value: int, min_val: int, max_val: int) -> bool:
    """Return True if *value* satisfies *pattern* for the given range."""
    if pattern == "*":
        return True
    for part in pattern.split(","):
        if "/" in part:
            base, step_str = part.split("/", 1)
            step = int(step_str)
            start = min_val if base == "*" else int(base)
            if value >= start and (value - start) % step == 0:
                return True
        elif "-" in part:
            lo, hi = part.split("-", 1)
            if int(lo) <= value <= int(hi):
                return True
        else:
            if int(part) == value:
                return True
    return False


def match(expression: str, dt: datetime) -> MatchResult:
    """Check whether *dt* matches *expression* and return a detailed report."""
    try:
        cron = parse(expression)
    except CronParseError as exc:
        return MatchResult(expression=expression, dt=dt, error=str(exc))

    raw_fields = [
        cron.minute,
        cron.hour,
        cron.day,
        cron.month,
        cron.weekday,
    ]
    ranges = [
        (0, 59),
        (0, 23),
        (1, 31),
        (1, 12),
        (0, 6),
    ]
    actual_values = [
        dt.minute,
        dt.hour,
        dt.day,
        dt.month,
        dt.weekday() % 7,  # Python Monday=0 → cron Sunday=0
    ]

    results: List[FieldMatchResult] = []
    for name, pattern, value, (lo, hi) in zip(FIELD_NAMES, raw_fields, actual_values, ranges):
        results.append(
            FieldMatchResult(
                name=name,
                pattern=pattern,
                value=value,
                matched=_field_matches(pattern, value, lo, hi),
            )
        )

    return MatchResult(expression=expression, dt=dt, fields=results)
