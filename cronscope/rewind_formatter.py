"""Formatter for RewindResult objects."""

from __future__ import annotations

from cronscope.rewinder import RewindResult

_DATE_FMT = "%Y-%m-%d %H:%M"
_HEADER = "\033[1;36m"
_RESET = "\033[0m"
_DIM = "\033[2m"
_RED = "\033[31m"
_GREEN = "\033[32m"


def _c(text: str, code: str, color: bool) -> str:
    return f"{code}{text}{_RESET}" if color else text


def format_rewind(result: RewindResult, color: bool = True) -> str:
    lines: list[str] = []

    header = _c(f"Rewind: {result.expression}", _HEADER, color)
    window = (
        f"{result.since.strftime(_DATE_FMT)} "
        f"→ {result.until.strftime(_DATE_FMT)}"
    )
    lines.append(header)
    lines.append(_c(f"Window : {window}", _DIM, color))

    if not result:
        lines.append(_c(f"Error  : {result.error}", _RED, color))
        return "\n".join(lines)

    count_label = f"{result.count} run{'s' if result.count != 1 else ''} found"
    lines.append(_c(count_label, _GREEN, color))

    if result.runs:
        lines.append("")
        for i, run in enumerate(result.runs, 1):
            label = f"  {i:>3}. {run.strftime(_DATE_FMT)}"
            lines.append(label)
    else:
        lines.append(_c("  (no runs in this window)", _DIM, color))

    return "\n".join(lines)
