"""Summarize multiple cron expressions into a compact comparison table."""

from typing import List, Optional
from cronscope.validator import validate
from cronscope.humanizer import humanize
from cronscope.scheduler import CronScheduler


def summarize(expressions: List[str], count: int = 3, label_prefix: str = "expr") -> List[dict]:
    """Return a list of summary dicts for each cron expression.

    Each dict contains:
      - expression: the raw cron string
      - label: auto-generated label
      - valid: bool
      - error: error message or None
      - human: human-readable description or None
      - next_runs: list of ISO-formatted next run timestamps
    """
    results = []
    for i, expr in enumerate(expressions):
        label = f"{label_prefix}_{i + 1}"
        result = validate(expr)
        if not result:
            results.append({
                "expression": expr,
                "label": label,
                "valid": False,
                "error": result.error,
                "human": None,
                "next_runs": [],
            })
            continue

        try:
            human = humanize(expr)
        except Exception:
            human = None

        try:
            sched = CronScheduler(expr)
            runs = [dt.isoformat() for dt in sched.next_runs(count)]
        except Exception:
            runs = []

        results.append({
            "expression": expr,
            "label": label,
            "valid": True,
            "error": None,
            "human": human,
            "next_runs": runs,
        })

    return results


def summarize_table(expressions: List[str], count: int = 3) -> str:
    """Return a plain-text table summarising multiple cron expressions."""
    rows = summarize(expressions, count=count)
    lines = []
    col_w = 28

    header = f"{'Expression':<{col_w}} {'Valid':<6} {'Human Description':<40} Next Runs"
    lines.append(header)
    lines.append("-" * len(header))

    for row in rows:
        valid_str = "yes" if row["valid"] else "no"
        human_str = (row["human"] or row["error"] or "")[:38]
        runs_str = ", ".join(row["next_runs"][:2]) if row["next_runs"] else "—"
        lines.append(
            f"{row['expression']:<{col_w}} {valid_str:<6} {human_str:<40} {runs_str}"
        )

    return "\n".join(lines)
