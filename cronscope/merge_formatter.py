"""Format a MergedSchedule for terminal display."""

from cronscope.merger import MergedSchedule
from cronscope.formatter import _c

_DATE_FMT = "%Y-%m-%d %H:%M"


def format_merge(schedule: MergedSchedule, color: bool = True) -> str:
    """Render a MergedSchedule as a human-readable terminal string.

    Args:
        schedule: The merged schedule to format.
        color: Whether to include ANSI colour codes.

    Returns:
        Formatted string ready for printing.
    """
    lines: list[str] = []

    header_label = _c("Merged Schedule", "1", color)
    expr_count = len(schedule.expressions)
    lines.append(f"{header_label} — {expr_count} expression(s)")
    lines.append("")

    if schedule.errors:
        lines.append(_c("Invalid expressions:", "31", color))
        for expr, msg in schedule.errors.items():
            lines.append(f"  {_c(expr, '33', color)}: {msg}")
        lines.append("")

    valid = schedule.valid_expressions()
    if valid:
        lines.append(_c("Valid expressions:", "32", color))
        for expr in valid:
            lines.append(f"  {_c(expr, '36', color)}")
        lines.append("")

    if schedule.next_runs:
        lines.append(
            _c(f"Next {len(schedule.next_runs)} run(s):", "1", color)
        )
        for dt, expr in schedule.next_runs:
            dt_str = _c(dt.strftime(_DATE_FMT), "36", color)
            expr_str = _c(expr, "33", color)
            lines.append(f"  {dt_str}  ← {expr_str}")
    else:
        lines.append(_c("No upcoming runs found.", "31", color))

    return "\n".join(lines)
