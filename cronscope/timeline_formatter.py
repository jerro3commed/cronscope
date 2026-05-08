"""Formatter for Timeline objects — renders a compact bar chart in the terminal."""

from __future__ import annotations

from cronscope.timeline import Timeline
from cronscope.formatter import _c

_BAR_CHAR = "█"
_EMPTY_CHAR = "░"
_MAX_BAR = 20


def _bar(count: int, max_count: int, use_color: bool) -> str:
    if max_count == 0:
        filled = 0
    else:
        filled = round((count / max_count) * _MAX_BAR)
    bar = _BAR_CHAR * filled + _EMPTY_CHAR * (_MAX_BAR - filled)
    if use_color and filled > 0:
        return _c(bar, "\033[32m", use_color)
    return bar


def format_timeline(timeline: Timeline, use_color: bool = True) -> str:
    """Render a Timeline as a terminal bar chart."""
    lines: list[str] = []

    header = _c(f"Timeline: {timeline.expression}", "\033[1m", use_color)
    lines.append(header)

    if not timeline:
        err = _c(f"  Error: {timeline.error}", "\033[31m", use_color)
        lines.append(err)
        return "\n".join(lines)

    if not timeline.windows:
        lines.append("  No windows to display.")
        return "\n".join(lines)

    max_count = max(w.count for w in timeline.windows)
    total = timeline.total_runs
    lines.append(
        _c(f"  Total runs: {total} across {len(timeline.windows)} windows", "\033[36m", use_color)
    )
    lines.append("")

    for window in timeline.windows:
        label = window.label.ljust(16)
        bar = _bar(window.count, max_count, use_color)
        count_str = _c(str(window.count).rjust(4), "\033[33m", use_color)
        lines.append(f"  {label} {bar} {count_str}")

    return "\n".join(lines)
