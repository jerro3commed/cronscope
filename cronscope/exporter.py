"""Export cron schedule previews to plain text or JSON formats."""

import json
from datetime import datetime
from typing import List, Optional

from cronscope.validator import validate
from cronscope.scheduler import CronScheduler


def export_text(
    expression: str,
    count: int = 5,
    start: Optional[datetime] = None,
    label: Optional[str] = None,
) -> str:
    """Export next run times as a plain-text block.

    Args:
        expression: A valid 5-field cron expression.
        count: Number of upcoming run times to include.
        start: Datetime to start from (defaults to now).
        label: Optional title line for the output block.

    Returns:
        A formatted multi-line string.

    Raises:
        ValueError: If the expression is invalid.
    """
    result = validate(expression)
    if not result:
        raise ValueError(f"Invalid cron expression: {result.error}")

    sched = CronScheduler(expression)
    runs: List[datetime] = sched.next_runs(count, start=start)

    lines: List[str] = []
    if label:
        lines.append(label)
        lines.append("-" * len(label))
    lines.append(f"Expression : {expression}")
    lines.append(f"Next {count} run(s):")
    for i, dt in enumerate(runs, 1):
        lines.append(f"  {i:>2}. {dt.strftime('%Y-%m-%d %H:%M')}")
    return "\n".join(lines)


def export_json(
    expression: str,
    count: int = 5,
    start: Optional[datetime] = None,
    label: Optional[str] = None,
    indent: int = 2,
) -> str:
    """Export next run times as a JSON string.

    Args:
        expression: A valid 5-field cron expression.
        count: Number of upcoming run times to include.
        start: Datetime to start from (defaults to now).
        label: Optional label stored in the JSON payload.
        indent: JSON indentation level.

    Returns:
        A JSON-encoded string.

    Raises:
        ValueError: If the expression is invalid.
    """
    result = validate(expression)
    if not result:
        raise ValueError(f"Invalid cron expression: {result.error}")

    sched = CronScheduler(expression)
    runs: List[datetime] = sched.next_runs(count, start=start)

    payload = {
        "expression": expression,
        "count": count,
        "next_runs": [dt.strftime("%Y-%m-%dT%H:%M:00") for dt in runs],
    }
    if label is not None:
        payload["label"] = label

    return json.dumps(payload, indent=indent)
