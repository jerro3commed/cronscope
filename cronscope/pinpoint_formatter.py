"""Formatter for PinpointResult output."""

from __future__ import annotations

from cronscope.pinpointer import PinpointResult

_DATE_FMT = "%Y-%m-%d %H:%M"


def _c(text: str, code: str, color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if color else text


def format_pinpoint(result: PinpointResult, color: bool = True) -> str:
    """Render a :class:`PinpointResult` as a human-readable string."""
    lines: list[str] = []

    header = _c("Pinpoint", "1;36", color)
    expr = _c(result.expression, "1;33", color)
    lines.append(f"{header}: {expr}")
    lines.append(_c("-" * 40, "2", color))

    if not result:
        label = _c("Error", "1;31", color)
        lines.append(f"  {label}: {result.error}")
        return "\n".join(lines)

    target_str = result.target.strftime(_DATE_FMT)
    lines.append(f"  {'Reference':<16} {_c(target_str, '36', color)}")

    if result.has_next:
        next_str = result.next_run.strftime(_DATE_FMT)  # type: ignore[union-attr]
        delta = f"(+{result.delta_minutes} min)" if result.delta_minutes is not None else ""
        lines.append(
            f"  {'Next run':<16} {_c(next_str, '1;32', color)}  {_c(delta, '2', color)}"
        )
    else:
        lines.append(f"  {'Next run':<16} {_c('none found', '2', color)}")

    if result.has_previous:
        prev_str = result.previous_run.strftime(_DATE_FMT)  # type: ignore[union-attr]
        lines.append(f"  {'Previous run':<16} {_c(prev_str, '33', color)}")
    else:
        lines.append(f"  {'Previous run':<16} {_c('none found', '2', color)}")

    return "\n".join(lines)
