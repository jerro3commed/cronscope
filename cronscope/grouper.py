"""Group and cluster cron expressions by shared schedule characteristics."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from cronscope.validator import validate
from cronscope.tagger import tag, TaggedExpression


@dataclass
class ExpressionGroup:
    """A group of cron expressions sharing a common tag or trait."""
    label: str
    expressions: List[str] = field(default_factory=list)
    errors: Dict[str, str] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return len(self.expressions) > 0

    @property
    def count(self) -> int:
        return len(self.expressions)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0


@dataclass
class GroupedSchedule:
    """Result of grouping multiple cron expressions."""
    groups: Dict[str, ExpressionGroup] = field(default_factory=dict)
    ungrouped: List[str] = field(default_factory=list)

    @property
    def group_labels(self) -> List[str]:
        return sorted(self.groups.keys())

    @property
    def total_expressions(self) -> int:
        return sum(g.count for g in self.groups.values()) + len(self.ungrouped)


def group(expressions: List[str], by: str = "frequency") -> GroupedSchedule:
    """Group expressions by a given strategy: 'frequency', 'hour', or 'day'."""
    result = GroupedSchedule()

    for expr in expressions:
        validation = validate(expr)
        if not validation:
            label = "invalid"
            grp = result.groups.setdefault(label, ExpressionGroup(label=label))
            grp.errors[expr] = validation.error or "Invalid expression"
            continue

        tagged_list = tag([expr])
        tagged: Optional[TaggedExpression] = tagged_list[0] if tagged_list else None

        if by == "frequency" and tagged and tagged.frequency_tag:
            label = tagged.frequency_tag
        elif by == "hour":
            parts = expr.split()
            hour_field = parts[1] if len(parts) > 1 else "*"
            label = f"hour:{hour_field}"
        elif by == "day":
            parts = expr.split()
            dow_field = parts[4] if len(parts) > 4 else "*"
            label = f"dow:{dow_field}"
        else:
            result.ungrouped.append(expr)
            continue

        grp = result.groups.setdefault(label, ExpressionGroup(label=label))
        grp.expressions.append(expr)

    return result
