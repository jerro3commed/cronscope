"""High-level preview API combining parsing, scheduling, and formatting."""

from datetime import datetime
from typing import List, Optional

from .parser import parse, CronParseError
from .scheduler import CronScheduler
from .formatter import format_next_runs, format_validation_error


def preview(
    expression: str,
    count: int = 10,
    base_time: Optional[datetime] = None,
    *,
    color: bool = True,
) -> str:
    """Parse *expression* and return a formatted preview of the next *count* runs.

    If the expression is invalid the returned string describes the error.
    """
    try:
        cron_expr = parse(expression)
    except CronParseError as exc:
        return format_validation_error(expression, str(exc), color=color)

    scheduler = CronScheduler(cron_expr, base_time=base_time)
    runs: List[datetime] = scheduler.next_runs(count)
    return format_next_runs(expression, runs, color=color)


def next_runs(
    expression: str,
    count: int = 10,
    base_time: Optional[datetime] = None,
) -> List[datetime]:
    """Return a list of the next *count* datetimes for *expression*.

    Raises CronParseError if the expression is invalid.
    """
    cron_expr = parse(expression)
    scheduler = CronScheduler(cron_expr, base_time=base_time)
    return scheduler.next_runs(count)
