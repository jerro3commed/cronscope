"""Trace which fields caused a cron expression to match or miss a given datetime."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .parser import parse, CronParseError
from .scheduler import CronScheduler


@dataclass
class FieldTrace:
    name: str
    value: int
    pattern: str
    matched: bool
    reason: str


@dataclass
class TraceResult:
    expression: str
    dt: datetime
    matched: bool
    fields: list[FieldTrace] = field(default_factory=list)
    error: Optional[str] = None

    def __bool__(self) -> bool:
        return self.error is None


_FIELD_NAMES = ["minute", "hour", "day", "month", "weekday"]
_DT_ATTRS = ["minute", "hour", "day", "month", "isoweekday"]


def _trace_field(name: str, pattern: str, dt_value: int, expr_field) -> FieldTrace:
    """Determine whether a single field matches and explain why."""
    if pattern == "*":
        reason = f"{name} is wildcard — always matches"
        return FieldTrace(name=name, value=dt_value, pattern=pattern, matched=True, reason=reason)

    sched = CronScheduler(f"* * * * *")  # dummy; we only need _matches
    matched = sched._matches_field(expr_field, dt_value)
    if matched:
        reason = f"{name} value {dt_value} satisfies '{pattern}'"
    else:
        reason = f"{name} value {dt_value} does not satisfy '{pattern}'"
    return FieldTrace(name=name, value=dt_value, pattern=pattern, matched=matched, reason=reason)


def trace(expression: str, dt: datetime) -> TraceResult:
    """Trace a cron expression against a specific datetime."""
    try:
        cron = parse(expression)
    except CronParseError as exc:
        return TraceResult(expression=expression, dt=dt, matched=False, error=str(exc))

    patterns = [
        cron.minute, cron.hour, cron.day, cron.month, cron.weekday
    ]
    raw_fields = [cron.minute, cron.hour, cron.day, cron.month, cron.weekday]
    dt_values = [
        dt.minute, dt.hour, dt.day, dt.month, dt.isoweekday() % 7
    ]

    sched = CronScheduler(expression)
    traces = []
    for name, pattern, dt_val, expr_f in zip(_FIELD_NAMES, patterns, dt_values, raw_fields):
        ft = FieldTrace(
            name=name,
            value=dt_val,
            pattern=pattern,
            matched=sched._matches_field(expr_f, dt_val),
            reason="",
        )
        if pattern == "*":
            ft.reason = f"{name} is wildcard — always matches"
        elif ft.matched:
            ft.reason = f"{name} value {dt_val} satisfies '{pattern}'"
        else:
            ft.reason = f"{name} value {dt_val} does not satisfy '{pattern}'"
        traces.append(ft)

    all_matched = all(t.matched for t in traces)
    return TraceResult(expression=expression, dt=dt, matched=all_matched, fields=traces)
