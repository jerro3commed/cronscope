"""Diff two cron expressions, highlighting field-level differences."""

from dataclasses import dataclass
from typing import List, Optional
from cronscope.parser import parse, CronParseError

FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]


@dataclass
class FieldDiff:
    name: str
    left: str
    right: str
    changed: bool


@dataclass
class CronDiff:
    left_expr: str
    right_expr: str
    fields: List[FieldDiff]
    left_error: Optional[str] = None
    right_error: Optional[str] = None

    @property
    def has_errors(self) -> bool:
        return self.left_error is not None or self.right_error is not None

    @property
    def changed_fields(self) -> List[FieldDiff]:
        return [f for f in self.fields if f.changed]

    @property
    def is_identical(self) -> bool:
        return not self.has_errors and len(self.changed_fields) == 0


def diff(left: str, right: str) -> CronDiff:
    """Compare two cron expressions field by field.

    Args:
        left: First cron expression string.
        right: Second cron expression string.

    Returns:
        A CronDiff describing which fields differ.
    """
    left_error: Optional[str] = None
    right_error: Optional[str] = None
    left_parts: List[str] = []
    right_parts: List[str] = []

    try:
        left_parsed = parse(left)
        left_parts = [
            left_parsed.minute,
            left_parsed.hour,
            left_parsed.day_of_month,
            left_parsed.month,
            left_parsed.day_of_week,
        ]
    except CronParseError as exc:
        left_error = str(exc)
        left_parts = left.split() if left.strip() else []

    try:
        right_parsed = parse(right)
        right_parts = [
            right_parsed.minute,
            right_parsed.hour,
            right_parsed.day_of_month,
            right_parsed.month,
            right_parsed.day_of_week,
        ]
    except CronParseError as exc:
        right_error = str(exc)
        right_parts = right.split() if right.strip() else []

    fields: List[FieldDiff] = []
    for i, name in enumerate(FIELD_NAMES):
        l_val = left_parts[i] if i < len(left_parts) else "?"
        r_val = right_parts[i] if i < len(right_parts) else "?"
        fields.append(FieldDiff(name=name, left=l_val, right=r_val, changed=(l_val != r_val)))

    return CronDiff(
        left_expr=left,
        right_expr=right,
        fields=fields,
        left_error=left_error,
        right_error=right_error,
    )
