"""Rank and compare multiple cron expressions by frequency of execution."""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from cronscope.validator import validate
from cronscope.scheduler import CronScheduler


@dataclass
class RankedExpression:
    expression: str
    runs_per_day: float
    rank: int
    label: Optional[str] = None
    error: Optional[str] = None

    def __bool__(self) -> bool:
        return self.error is None


def _estimate_runs_per_day(expression: str, sample_days: int = 7) -> float:
    """Estimate average runs per day by sampling the next `sample_days` days."""
    now = datetime(2024, 1, 1, 0, 0, 0)
    scheduler = CronScheduler(expression)
    runs = list(scheduler.next_runs(count=sample_days * 24 * 60, after=now))
    if not runs:
        return 0.0
    if len(runs) < 2:
        return 1.0
    span_days = (runs[-1] - runs[0]).total_seconds() / 86400
    if span_days == 0:
        return float(len(runs))
    return len(runs) / span_days


def rank(
    expressions: List[str],
    labels: Optional[List[str]] = None,
    sample_days: int = 7,
) -> List[RankedExpression]:
    """Rank a list of cron expressions from most to least frequent.

    Args:
        expressions: List of cron expression strings.
        labels: Optional list of labels corresponding to each expression.
        sample_days: Number of days to sample for frequency estimation.

    Returns:
        List of RankedExpression sorted by descending frequency (rank 1 = most frequent).
    """
    if labels is None:
        labels = [None] * len(expressions)

    results = []
    for expr, label in zip(expressions, labels):
        result = validate(expr)
        if not result:
            results.append(
                RankedExpression(
                    expression=expr,
                    runs_per_day=0.0,
                    rank=0,
                    label=label,
                    error=result.error,
                )
            )
        else:
            rpd = _estimate_runs_per_day(expr, sample_days=sample_days)
            results.append(
                RankedExpression(
                    expression=expr,
                    runs_per_day=rpd,
                    rank=0,
                    label=label,
                )
            )

    valid = sorted(
        [r for r in results if r.error is None],
        key=lambda r: r.runs_per_day,
        reverse=True,
    )
    for i, r in enumerate(valid, start=1):
        r.rank = i

    invalid = [r for r in results if r.error is not None]
    for r in invalid:
        r.rank = len(valid) + 1

    ordered = valid + invalid
    return ordered
