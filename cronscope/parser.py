"""Cron expression parser and validator for cronscope."""

from dataclasses import dataclass
from typing import Optional

FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]
FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 6),
}

MONTH_ALIASES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

DOW_ALIASES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}


@dataclass
class CronExpression:
    raw: str
    minute: str
    hour: str
    day_of_month: str
    month: str
    day_of_week: str


class CronParseError(ValueError):
    pass


def _resolve_aliases(value: str, aliases: dict) -> str:
    for alias, num in aliases.items():
        value = value.lower().replace(alias, str(num))
    return value


def _validate_field(value: str, field: str) -> None:
    min_val, max_val = FIELD_RANGES[field]
    aliases = MONTH_ALIASES if field == "month" else (DOW_ALIASES if field == "day_of_week" else {})
    value = _resolve_aliases(value, aliases)

    if value == "*":
        return

    parts = value.split(",")
    for part in parts:
        if "/" in part:
            base, step = part.split("/", 1)
            if not step.isdigit():
                raise CronParseError(f"Invalid step in field '{field}': {part}")
            part = base

        if part == "*":
            continue

        if "-" in part:
            lo, hi = part.split("-", 1)
            if not (lo.isdigit() and hi.isdigit()):
                raise CronParseError(f"Invalid range in field '{field}': {part}")
            if not (min_val <= int(lo) <= max_val and min_val <= int(hi) <= max_val):
                raise CronParseError(
                    f"Range out of bounds in field '{field}': {part} (expected {min_val}-{max_val})"
                )
        elif part.isdigit():
            if not (min_val <= int(part) <= max_val):
                raise CronParseError(
                    f"Value out of bounds in field '{field}': {part} (expected {min_val}-{max_val})"
                )
        else:
            raise CronParseError(f"Invalid token in field '{field}': {part}")


def parse(expression: str) -> CronExpression:
    """Parse and validate a cron expression string."""
    parts = expression.strip().split()
    if len(parts) != 5:
        raise CronParseError(
            f"Expected 5 fields, got {len(parts)}. Format: minute hour dom month dow"
        )

    fields = dict(zip(FIELD_NAMES, parts))
    for field, value in fields.items():
        _validate_field(value, field)

    return CronExpression(raw=expression, **fields)
