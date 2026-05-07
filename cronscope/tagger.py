"""Tag cron expressions with human-friendly category labels."""

from dataclasses import dataclass, field
from typing import List, Optional

from cronscope.validator import validate
from cronscope.ranker import _estimate_runs_per_day


@dataclass
class TaggedExpression:
    expression: str
    tags: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def __bool__(self) -> bool:
        return self.error is None


def _frequency_tag(runs_per_day: float) -> str:
    if runs_per_day >= 1440:
        return "every-minute"
    if runs_per_day >= 60:
        return "high-frequency"
    if runs_per_day >= 24:
        return "frequent"
    if runs_per_day >= 1:
        return "daily"
    if runs_per_day >= 1 / 7:
        return "weekly"
    return "rare"


def _schedule_tags(expr_str: str) -> List[str]:
    """Derive descriptive tags from a parsed cron expression."""
    from cronscope.parser import parse

    expr = parse(expr_str)
    tags: List[str] = []

    runs_per_day = _estimate_runs_per_day(expr)
    tags.append(_frequency_tag(runs_per_day))

    if expr.day_of_week != "*":
        tags.append("weekday-specific")
    if expr.day_of_month != "*":
        tags.append("monthday-specific")
    if expr.month != "*":
        tags.append("month-specific")
    if "/" in expr.minute or "/" in expr.hour:
        tags.append("stepped")
    if "," in expr.minute or "," in expr.hour:
        tags.append("multi-value")

    return tags


def tag(expressions: List[str]) -> List[TaggedExpression]:
    """Return a TaggedExpression for each cron expression string."""
    results: List[TaggedExpression] = []
    for expr_str in expressions:
        result = validate(expr_str)
        if not result:
            results.append(
                TaggedExpression(expression=expr_str, error=result.error)
            )
        else:
            try:
                tags = _schedule_tags(expr_str)
            except Exception as exc:  # pragma: no cover
                tags = []
            results.append(TaggedExpression(expression=expr_str, tags=tags))
    return results
