"""Inspect a cron expression and return a structured breakdown of its fields."""

from dataclasses import dataclass, field
from typing import List, Optional

from cronscope.parser import parse, CronParseError
from cronscope.explainer import explain
from cronscope.humanizer import humanize


@dataclass
class FieldInspection:
    name: str
    raw: str
    explanation: str
    is_wildcard: bool
    is_step: bool
    is_list: bool
    is_range: bool


@dataclass
class InspectionResult:
    expression: str
    error: Optional[str] = None
    fields: List[FieldInspection] = field(default_factory=list)
    human_summary: str = ""

    def __bool__(self) -> bool:
        return self.error is None


_FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]


def _inspect_field(name: str, raw: str, explanation: str) -> FieldInspection:
    return FieldInspection(
        name=name,
        raw=raw,
        explanation=explanation,
        is_wildcard=raw == "*",
        is_step="/" in raw,
        is_list="," in raw,
        is_range="-" in raw and "/" not in raw,
    )


def inspect(expression: str) -> InspectionResult:
    """Return a detailed inspection of each field in a cron expression."""
    try:
        parsed = parse(expression)
    except CronParseError as exc:
        return InspectionResult(expression=expression, error=str(exc))

    raw_fields = [
        parsed.minute,
        parsed.hour,
        parsed.day_of_month,
        parsed.month,
        parsed.day_of_week,
    ]

    explanations = explain(expression)

    field_inspections = [
        _inspect_field(name, raw, expl)
        for name, raw, expl in zip(_FIELD_NAMES, raw_fields, explanations)
    ]

    return InspectionResult(
        expression=expression,
        fields=field_inspections,
        human_summary=humanize(expression),
    )
