"""Validation utilities for cron expressions with detailed error reporting."""

from typing import List, Optional
from dataclasses import dataclass
from cronscope.parser import parse, CronParseError


@dataclass
class ValidationResult:
    """Result of validating a cron expression."""

    expression: str
    valid: bool
    error: Optional[str] = None
    fields: Optional[dict] = None

    def __bool__(self) -> bool:
        return self.valid


def validate(expression: str) -> ValidationResult:
    """Validate a cron expression and return a structured result.

    Args:
        expression: A cron expression string (5 fields).

    Returns:
        ValidationResult with valid flag and optional error message.
    """
    try:
        cron = parse(expression)
        fields = {
            "minute": cron.minute,
            "hour": cron.hour,
            "day_of_month": cron.day_of_month,
            "month": cron.month,
            "day_of_week": cron.day_of_week,
        }
        return ValidationResult(
            expression=expression,
            valid=True,
            fields=fields,
        )
    except CronParseError as exc:
        return ValidationResult(
            expression=expression,
            valid=False,
            error=str(exc),
        )


def validate_many(expressions: List[str]) -> List[ValidationResult]:
    """Validate multiple cron expressions.

    Args:
        expressions: List of cron expression strings.

    Returns:
        List of ValidationResult objects in the same order.
    """
    return [validate(expr) for expr in expressions]


def is_valid(expression: str) -> bool:
    """Quick check whether a cron expression is valid.

    Args:
        expression: A cron expression string.

    Returns:
        True if the expression is valid, False otherwise.
    """
    return validate(expression).valid
