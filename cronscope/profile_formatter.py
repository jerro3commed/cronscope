"""Formatter for ProfileResult objects."""

from __future__ import annotations

from .profiler import ProfileResult, WEEKDAY_NAMES
from .formatter import _c

_SHADES = " ▁▂▃▄▅▆▇█"


def _bar(count: int, max_count: int, width: int = 8) -> str:
    if max_count == 0:
        return " " * width
    ratio = count / max_count
    filled = round(ratio * width)
    shade_idx = min(len(_SHADES) - 1, max(0, round(ratio * (len(_SHADES) - 1))))
    return _SHADES[shade_idx] * filled + " " * (width - filled)


def format_profile(result: ProfileResult, color: bool = True) -> str:
    lines: list[str] = []

    header = _c(f"Profile: {result.expression}", "1", color)
    lines.append(header)
    lines.append("")

    if not result:
        lines.append(_c(f"  Error: {result.error}", "31", color))
        return "\n".join(lines)

    lines.append(_c(f"  Sample window : {result.sample_days} day(s)", "2", color))
    lines.append(_c(f"  Total runs    : {result.total_runs}", "2", color))
    lines.append("")

    max_hour = max(result.runs_per_hour.values(), default=0)
    lines.append(_c("  Runs by hour:", "33", color))
    for h in range(24):
        cnt = result.runs_per_hour.get(h, 0)
        bar = _bar(cnt, max_hour)
        marker = " ◄" if h == result.busiest_hour else ""
        lines.append(f"    {h:02d}:00  [{bar}] {cnt:>4}{marker}")

    lines.append("")

    max_day = max(result.runs_per_weekday.values(), default=0)
    lines.append(_c("  Runs by weekday:", "33", color))
    for d in range(7):
        cnt = result.runs_per_weekday.get(d, 0)
        bar = _bar(cnt, max_day)
        marker = " ◄" if d == result.busiest_weekday else ""
        lines.append(f"    {WEEKDAY_NAMES[d]}  [{bar}] {cnt:>4}{marker}")

    return "\n".join(lines)
