"""Terminal formatting helpers for cronscope output."""

from typing import List
from datetime import datetime

COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_CYAN = "\033[36m"
COLOR_RED = "\033[31m"
COLOR_BOLD = "\033[1m"


def _c(text: str, color: str, use_color: bool = True) -> str:
    """Wrap text in ANSI color codes if use_color is True."""
    if not use_color:
        return text
    return f"{color}{text}{COLOR_RESET}"


def format_next_runs(
    expression: str,
    runs: List[datetime],
    use_color: bool = True,
    explanation: str = None,
) -> str:
    """Format a list of next-run datetimes for terminal display."""
    lines = []
    header = _c(f"Cron expression: ", COLOR_BOLD, use_color) + \
             _c(expression, COLOR_CYAN, use_color)
    lines.append(header)

    if explanation:
        lines.append(_c(explanation, COLOR_YELLOW, use_color))

    lines.append(_c(f"Next {len(runs)} run(s):", COLOR_BOLD, use_color))

    for i, dt in enumerate(runs, start=1):
        formatted_dt = dt.strftime("%Y-%m-%d %H:%M")
        line = f"  {_c(str(i).rjust(2), COLOR_YELLOW, use_color)}. " \
               f"{_c(formatted_dt, COLOR_GREEN, use_color)}"
        lines.append(line)

    return "\n".join(lines)


def format_validation_error(expression: str, error: str, use_color: bool = True) -> str:
    """Format a validation error message for terminal display."""
    lines = [
        _c("Invalid cron expression:", COLOR_RED, use_color) +
        f" {_c(expression, COLOR_BOLD, use_color)}",
        _c(f"Error: {error}", COLOR_RED, use_color),
    ]
    return "\n".join(lines)
