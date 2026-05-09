"""Annotate cron expressions with inline field-level comments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .parser import parse, CronParseError

_FIELD_NAMES = ["minute", "hour", "day-of-month", "month", "day-of-week"]

_DOW_NAMES = {
    "0": "Sun", "1": "Mon", "2": "Tue", "3": "Wed",
    "4": "Thu", "5": "Fri", "6": "Sat", "7": "Sun",
}

_MONTH_NAMES = {
    "1": "Jan", "2": "Feb", "3": "Mar", "4": "Apr",
    "5": "May", "6": "Jun", "7": "Jul", "8": "Aug",
    "9": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
}


@dataclass
class AnnotatedField:
    name: str
    raw: str
    note: str


@dataclass
class AnnotatedExpression:
    expression: str
    fields: List[AnnotatedField]
    error: Optional[str] = None

    def __bool__(self) -> bool:
        return self.error is None


def _annotate_field(name: str, raw: str) -> AnnotatedField:
    """Produce a short human note for a single cron field token."""
    if raw == "*":
        return AnnotatedField(name=name, raw=raw, note=f"every {name}")

    if raw.startswith("*/"):
        step = raw[2:]
        return AnnotatedField(name=name, raw=raw, note=f"every {step} {name}(s)")

    if "-" in raw and "/" not in raw:
        lo, hi = raw.split("-", 1)
        if name == "day-of-week":
            lo = _DOW_NAMES.get(lo, lo)
            hi = _DOW_NAMES.get(hi, hi)
        elif name == "month":
            lo = _MONTH_NAMES.get(lo, lo)
            hi = _MONTH_NAMES.get(hi, hi)
        return AnnotatedField(name=name, raw=raw, note=f"{lo} through {hi}")

    if "," in raw:
        parts = raw.split(",")
        if name == "day-of-week":
            parts = [_DOW_NAMES.get(p, p) for p in parts]
        elif name == "month":
            parts = [_MONTH_NAMES.get(p, p) for p in parts]
        return AnnotatedField(name=name, raw=raw, note=", ".join(parts))

    # plain numeric
    label = raw
    if name == "day-of-week":
        label = _DOW_NAMES.get(raw, raw)
    elif name == "month":
        label = _MONTH_NAMES.get(raw, raw)
    return AnnotatedField(name=name, raw=raw, note=f"at {name} {label}")


def annotate(expression: str) -> AnnotatedExpression:
    """Parse and annotate each field of a cron expression."""
    try:
        parsed = parse(expression)
    except CronParseError as exc:
        return AnnotatedExpression(expression=expression, fields=[], error=str(exc))

    raw_fields = [parsed.minute, parsed.hour, parsed.dom, parsed.month, parsed.dow]
    fields = [
        _annotate_field(name, raw)
        for name, raw in zip(_FIELD_NAMES, raw_fields)
    ]
    return AnnotatedExpression(expression=expression, fields=fields)
