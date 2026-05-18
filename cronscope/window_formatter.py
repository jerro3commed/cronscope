"""Format WindowAnalysis results for terminal display."""

from __future__ import annotations

from cronscope.window_analyzer import WindowAnalysis
from cronscope.formatter import _c

_BAR_CHARS = " ▏▎▍▌▋▊▉█"
_MAX_BAR_WIDTH = 30


def _bar(count: int, max_count: int) -> str:
    if max_count == 0:
        return " " * _MAX_BAR_WIDTH
    filled = int(round(_MAX_BAR_WIDTH * count / max_count))
    return "█" * filled + " " * (_MAX_BAR_WIDTH - filled)


def format_window_analysis(
    analysis: WindowAnalysis, color: bool = True
) -> str:
    lines: list[str] = []

    header = _c("Window Analysis", "1", color)
    expr_label = _c(analysis.expression, "36", color)
    lines.append(f"{header}: {expr_label}")
    lines.append("")

    if not analysis:
        lines.append(_c(f"  Error: {analysis.error}", "31", color))
        return "\n".join(lines)

    max_count = max((w.count for w in analysis.windows), default=0)

    for window in analysis.windows:
        bar = _bar(window.count, max_count)
        count_str = _c(str(window.count).rjust(4), "33", color)
        bar_str = _c(bar, "34", color)
        label = window.label.ljust(18)
        lines.append(f"  {label} {bar_str} {count_str}")

    lines.append("")
    total_str = _c(str(analysis.total), "32", color)
    lines.append(f"  Total runs : {total_str}")

    if analysis.busiest:
        b = analysis.busiest
        lines.append(
            f"  Busiest    : {b.label}  "
            + _c(f"({b.count} runs)", "33", color)
        )
    if analysis.quietest:
        q = analysis.quietest
        lines.append(
            f"  Quietest   : {q.label}  "
            + _c(f"({q.count} runs)", "36", color)
        )

    return "\n".join(lines)
