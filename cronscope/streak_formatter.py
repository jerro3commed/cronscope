"""Format StreakResult objects for terminal display."""

from __future__ import annotations

from cronscope.streaker import StreakResult
from cronscope.formatter import _c

_DATE_FMT = "%Y-%m-%d"


def format_streak(result: StreakResult, color: bool = True) -> str:
    """Return a human-readable terminal string for a StreakResult."""
    lines: list[str] = []

    header = _c(f"Streak analysis for: {result.expression}", "1", color)
    lines.append(header)
    lines.append(_c("-" * 44, "90", color))

    if result.error:
        lines.append(_c(f"  Error: {result.error}", "31", color))
        return "\n".join(lines)

    longest_label = _c("Longest streak:", "36", color)
    lines.append(f"  {longest_label} {result.longest_streak} day(s)")

    if result.streak_start and result.streak_end:
        start_str = result.streak_start.strftime(_DATE_FMT)
        end_str = result.streak_end.strftime(_DATE_FMT)
        range_label = _c("  Period:        ", "90", color)
        lines.append(f"{range_label}{start_str} → {end_str}")

    current_label = _c("Current streak: ", "36", color)
    current_val = _c(str(result.current_streak), "32" if result.current_streak > 0 else "90", color)
    lines.append(f"  {current_label}{current_val} day(s)")

    active_days = len(result._days_checked)
    days_label = _c("Active days:    ", "90", color)
    lines.append(f"  {days_label}{active_days}")

    return "\n".join(lines)
