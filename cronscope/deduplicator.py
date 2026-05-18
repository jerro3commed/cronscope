"""Deduplicate a list of cron expressions, grouping identical schedules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .normalizer import normalize


@dataclass
class DeduplicatedGroup:
    """A group of expressions that resolve to the same normalized form."""

    canonical: str
    expressions: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def __bool__(self) -> bool:
        return self.error is None

    @property
    def count(self) -> int:
        return len(self.expressions)

    @property
    def is_duplicate(self) -> bool:
        return self.count > 1


@dataclass
class DeduplicationResult:
    """Result of a deduplication pass over a list of cron expressions."""

    groups: List[DeduplicatedGroup] = field(default_factory=list)
    invalid: List[tuple] = field(default_factory=list)  # (expr, error_msg)

    @property
    def unique_count(self) -> int:
        return len(self.groups)

    @property
    def duplicate_count(self) -> int:
        return sum(1 for g in self.groups if g.is_duplicate)

    @property
    def total_expressions(self) -> int:
        return sum(g.count for g in self.groups) + len(self.invalid)


def deduplicate(expressions: List[str]) -> DeduplicationResult:
    """Group cron expressions that normalize to the same canonical form.

    Args:
        expressions: A list of cron expression strings.

    Returns:
        A DeduplicationResult with grouped unique schedules and any invalid entries.
    """
    seen: Dict[str, DeduplicatedGroup] = {}
    invalid: List[tuple] = []

    for expr in expressions:
        result = normalize(expr)
        if not result:
            invalid.append((expr, result.error or "invalid expression"))
            continue

        canonical = result.normalized
        if canonical not in seen:
            seen[canonical] = DeduplicatedGroup(canonical=canonical)
        seen[canonical].expressions.append(expr)

    return DeduplicationResult(
        groups=list(seen.values()),
        invalid=invalid,
    )
