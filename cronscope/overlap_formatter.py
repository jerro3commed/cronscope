"""Format OverlapReport instances for terminal display."""

from __future__ import annotations

from cronscope.overlap import OverlapReport
from cronscope.formatter import _c

_DATE_FMT = "%Y-%m-%d %H:%M"


def format_overlap(report: OverlapReport, color: bool = True) -> str:
    """Render an OverlapReport as a human-readable terminal string."""
    lines: list[str] = []

    header = _c("Overlap Analysis", "1;36", color)
    lines.append(header)
    lines.append(_c("-" * 40, "90", color))

    if report.errors:
        lines.append(_c("Parse errors:", "1;31", color))
        for expr, msg in report.errors.items():
            lines.append(f"  {_c(expr, '33', color)}: {msg}")
        lines.append("")

    valid_exprs = [e for e in report.expressions if e not in report.errors]
    lines.append(
        f"Expressions checked: {_c(str(len(valid_exprs)), '1', color)}"
    )

    if not report.has_overlaps:
        lines.append(_c("No overlapping slots found.", "32", color))
        return "\n".join(lines)

    lines.append(
        f"Overlapping slots:   {_c(str(report.overlap_count), '1;33', color)}"
    )
    lines.append("")

    for slot in report.slots:
        ts_str = _c(slot.timestamp.strftime(_DATE_FMT), "36", color)
        lines.append(f"  {ts_str}")
        for expr in slot.expressions:
            lines.append(f"    {_c(expr, '33', color)}")

    return "\n".join(lines)
