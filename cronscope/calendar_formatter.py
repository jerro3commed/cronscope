"""Formatter for CalendarMonth objects."""

from __future__ import annotations

import calendar

from .calendar_view import CalendarMonth
from .formatter import _c

_HEADER_COLOR = "\033[1;36m"
_DAY_COLOR = "\033[1;32m"
_EMPTY_COLOR = "\033[2m"
_RESET = "\033[0m"


def format_calendar(cal: CalendarMonth, color: bool = True) -> str:
    """Render a CalendarMonth as a text calendar grid."""
    lines: list[str] = []

    header = f"{cal.month_name} {cal.year}  —  {cal.expression}"
    lines.append(_c(header, _HEADER_COLOR, color))

    if not cal:
        lines.append(_c(f"  Error: {cal.error}", "\033[1;31m", color))
        return "\n".join(lines)

    # Weekday header
    lines.append("  " + "  ".join(day[:2] for day in calendar.day_abbr))

    _, days_in_month = calendar.monthrange(cal.year, cal.month)
    first_weekday, _ = calendar.monthrange(cal.year, cal.month)

    week: list[str] = ["   "] * first_weekday
    for day in range(1, days_in_month + 1):
        count = cal.fire_days.get(day, 0)
        if count > 0:
            label = f"{day:2d}*"
            cell = _c(label, _DAY_COLOR, color)
        else:
            label = f"{day:2d} "
            cell = _c(label, _EMPTY_COLOR, color)
        week.append(cell)
        if len(week) == 7:
            lines.append(" ".join(week))
            week = []

    if week:
        week += ["   "] * (7 - len(week))
        lines.append(" ".join(week))

    total_label = f"Total runs: {cal.total_runs}"
    lines.append(_c(total_label, _HEADER_COLOR, color))

    return "\n".join(lines)
