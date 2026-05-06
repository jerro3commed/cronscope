"""Format ranked cron expressions for terminal display."""

from typing import List

from cronscope.ranker import RankedExpression
from cronscope.formatter import _c


def format_rank(
    ranked: List[RankedExpression],
    color: bool = True,
) -> str:
    """Render a ranked list of cron expressions as a formatted table string.

    Args:
        ranked: List of RankedExpression objects (already sorted by rank).
        color: Whether to emit ANSI color codes.

    Returns:
        A multi-line string suitable for printing to the terminal.
    """
    if not ranked:
        return _c("No expressions to rank.", "33", color)

    lines = []
    header = "{:<5} {:<30} {:<18} {}".format("Rank", "Expression", "Runs/Day", "Label")
    lines.append(_c(header, "1", color))
    lines.append(_c("-" * 65, "90", color))

    for r in ranked:
        rank_str = f"#{r.rank}"
        expr_str = r.expression
        label_str = r.label or ""

        if r.error:
            rpd_str = _c("ERROR", "31", color)
            expr_colored = _c(expr_str, "31", color)
            lines.append(
                "{:<5} {:<30} {:<18} {}".format(
                    _c(rank_str, "31", color),
                    expr_colored,
                    rpd_str,
                    _c(f"{label_str} ({r.error})", "90", color),
                )
            )
        else:
            rpd_display = f"{r.runs_per_day:.2f}"
            if r.runs_per_day >= 60:
                rpd_colored = _c(rpd_display, "31", color)
            elif r.runs_per_day >= 10:
                rpd_colored = _c(rpd_display, "33", color)
            else:
                rpd_colored = _c(rpd_display, "32", color)

            lines.append(
                "{:<5} {:<30} {:<18} {}".format(
                    _c(rank_str, "36", color),
                    _c(expr_str, "97", color),
                    rpd_colored,
                    _c(label_str, "90", color),
                )
            )

    return "\n".join(lines)
