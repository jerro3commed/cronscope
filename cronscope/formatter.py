"""Terminal formatting helpers for cronscope output."""

from datetime import datetime
from typing import List

TIMESTAMP_FMT = "%Y-%m-%d %H:%M"

# ANSI colour helpers
_RESET = "\033[0m"
_BOLD = "\033[1m"
_GREEN = "\033[32m"
_CYAN = "\033[36m"
_YELLOW = "\033[33m"


def _c(text: str, *codes: str) -> str:
    return "".join(codes) + text + _RESET


def format_next_runs(
    expression: str,
    runs: List[datetime],
    *,
    color: bool = True,
) -> str:
    """Return a formatted string listing upcoming run times."""
    lines: List[str] = []

    header = f"Upcoming runs for: {expression}"
    if color:
        header = _c(header, _BOLD, _CYAN)
    lines.append(header)
    lines.append("-" * 40)

    for i, dt in enumerate(runs, start=1):
        timestamp = dt.strftime(TIMESTAMP_FMT)
        label = f"  {i:>2}. {timestamp}"
        if color:
            label = _c(f"  {i:>2}.", _YELLOW) + " " + _c(timestamp, _GREEN)
        lines.append(label)

    if not runs:
        msg = "  (no upcoming runs found)"
        lines.append(_c(msg, _YELLOW) if color else msg)

    return "\n".join(lines)


def format_validation_error(expression: str, error: str, *, color: bool = True) -> str:
    """Return a formatted error message for an invalid expression."""
    prefix = "[ERROR]"
    msg = f"{prefix} Invalid cron expression '{expression}': {error}"
    if color:
        msg = _c(msg, "\033[31m")  # red
    return msg
