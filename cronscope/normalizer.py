"""Normalize cron expressions to a canonical form."""

from dataclasses import dataclass, field
from typing import Optional

from .parser import parse, CronParseError
from .alias_resolver import AliasResolutionError, resolve


@dataclass
class NormalizeResult:
    """Result of normalizing a cron expression."""

    original: str
    normalized: Optional[str]
    fields: list  # list of normalized field strings
    error: Optional[str] = None
    was_macro: bool = False

    def __bool__(self) -> bool:
        return self.error is None


def _normalize_field(raw: str) -> str:
    """Return a consistently formatted version of a single cron field."""
    # Lowercase for alias tokens, strip whitespace
    raw = raw.strip().lower()

    # Expand step over wildcard: */1 -> *
    if raw == "*/1":
        return "*"

    # Sort comma-separated lists numerically where possible
    if "," in raw:
        parts = [p.strip() for p in raw.split(",")]
        try:
            parts_sorted = sorted(parts, key=lambda x: int(x))
            return ",".join(parts_sorted)
        except ValueError:
            return ",".join(parts)

    return raw


def normalize(expression: str) -> NormalizeResult:
    """Normalize a cron expression to a canonical string.

    Handles:
    - Macro expansion (e.g. @daily -> 0 0 * * *)
    - Redundant step removal (*/1 -> *)
    - Sorted comma lists
    - Consistent lowercase aliases
    """
    original = expression.strip()
    was_macro = False
    expanded = original

    # Attempt macro resolution first
    try:
        resolved = resolve(original)
        if resolved.is_macro:
            expanded = resolved.expression
            was_macro = True
    except (AliasResolutionError, Exception):
        pass

    # Validate by parsing
    try:
        parsed = parse(expanded)
    except CronParseError as exc:
        return NormalizeResult(
            original=original,
            normalized=None,
            fields=[],
            error=str(exc),
            was_macro=was_macro,
        )

    raw_fields = expanded.split()
    normalized_fields = [_normalize_field(f) for f in raw_fields]
    normalized_expr = " ".join(normalized_fields)

    return NormalizeResult(
        original=original,
        normalized=normalized_expr,
        fields=normalized_fields,
        error=None,
        was_macro=was_macro,
    )
