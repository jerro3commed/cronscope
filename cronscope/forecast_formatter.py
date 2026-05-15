"""Terminal formatter for :class:`~cronscope.forecaster.ForecastResult`."""

from __future__ import annotations

from cronscope.forecaster import ForecastResult
from cronscope.formatter import _c

_BAR_WIDTH = 30


def _bar(count: int, max_count: int, *, color: bool = True) -> str:
    """Return a proportional ASCII bar for *count* relative to *max_count*."""
    if max_count == 0:
        filled = 0
    else:
        filled = round(_BAR_WIDTH * count / max_count)
    bar = "█" * filled + "░" * (_BAR_WIDTH - filled)
    return _c(bar, "cyan", color=color)


def format_forecast(result: ForecastResult, *, color: bool = True) -> str:
    """Render a :class:`ForecastResult` as a human-readable string.

    Parameters
    ----------
    result:
        The forecast result to render.
    color:
        Whether to emit ANSI colour codes.
    """
    lines: list[str] = []

    header = _c("Forecast", "bold", color=color)
    expr = _c(result.expression, "yellow", color=color)
    lines.append(f"{header}: {expr}")
    lines.append("")

    if not result:
        lines.append(_c(f"  Error: {result.error}", "red", color=color))
        return "\n".join(lines)

    max_count = max((w.run_count for w in result.windows), default=0)

    label_width = max((len(w.label) for w in result.windows), default=10)

    for window in result.windows:
        label = window.label.ljust(label_width)
        bar = _bar(window.run_count, max_count, color=color)
        count_str = _c(str(window.run_count).rjust(5), "green", color=color)
        lines.append(f"  {label}  {bar}  {count_str} run(s)")

    lines.append("")
    total_label = _c("Total", "bold", color=color)
    total_val = _c(str(result.total_runs), "green", color=color)
    lines.append(f"  {total_label}: {total_val} run(s) across {len(result.windows)} window(s)")

    return "\n".join(lines)
