"""Format a TraceResult for terminal output."""

from __future__ import annotations

from .tracer import TraceResult
from .formatter import _c

_CHECK = "\u2713"
_CROSS = "\u2717"


def format_trace(result: TraceResult, color: bool = True) -> str:
    lines: list[str] = []

    expr_label = _c(result.expression, "cyan", color)
    dt_label = _c(result.dt.strftime("%Y-%m-%d %H:%M"), "yellow", color)
    lines.append(f"Trace: {expr_label}  @  {dt_label}")
    lines.append("")

    if not result:
        lines.append(_c(f"  Error: {result.error}", "red", color))
        return "\n".join(lines)

    for ft in result.fields:
        if ft.matched:
            icon = _c(_CHECK, "green", color)
            name_col = _c(ft.name.ljust(8), "green", color)
        else:
            icon = _c(_CROSS, "red", color)
            name_col = _c(ft.name.ljust(8), "red", color)
        pattern_col = _c(f"'{ft.pattern}'", "magenta", color)
        lines.append(f"  {icon} {name_col}  pattern={pattern_col:20}  value={ft.value:<4}  {ft.reason}")

    lines.append("")
    if result.matched:
        verdict = _c("MATCH", "green", color)
    else:
        verdict = _c("NO MATCH", "red", color)

    first_miss = next((f.name for f in result.fields if not f.matched), None)
    if first_miss and not result.matched:
        note = _c(f"(first failing field: {first_miss})", "yellow", color)
        lines.append(f"  Result: {verdict}  {note}")
    else:
        lines.append(f"  Result: {verdict}")

    return "\n".join(lines)
