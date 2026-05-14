"""Terminal formatter for CadenceResult."""

from __future__ import annotations

from datetime import timedelta
from typing import Optional

from cronscope.cadence import CadenceResult
from cronscope.formatter import _c


def _fmt_td(td: Optional[timedelta]) -> str:
    if td is None:
        return "n/a"
    total = int(td.total_seconds())
    hours, rem = divmod(total, 3600)
    minutes, seconds = divmod(rem, 60)
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)


def format_cadence(result: CadenceResult, color: bool = True) -> str:
    lines = []

    header = _c("Cadence Analysis", "1;36", color)
    expr = _c(result.expression, "1;33", color)
    lines.append(f"{header}: {expr}")
    lines.append("")

    if not result:
        label = _c("Error", "1;31", color)
        lines.append(f"  {label}: {result.error}")
        return "\n".join(lines)

    if not result.intervals_seconds:
        lines.append("  No intervals available.")
        return "\n".join(lines)

    regularity = (
        _c("regular", "1;32", color)
        if result.is_regular
        else _c("irregular", "1;33", color)
    )
    lines.append(f"  Cadence : {regularity}")
    lines.append(f"  Samples : {len(result.intervals_seconds)} intervals")
    lines.append(f"  Min gap : {_fmt_td(result.min_interval)}")
    lines.append(f"  Max gap : {_fmt_td(result.max_interval)}")
    lines.append(f"  Avg gap : {_fmt_td(result.avg_interval)}")

    return "\n".join(lines)
