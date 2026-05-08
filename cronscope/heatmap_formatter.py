"""Render a Heatmap as a colour-coded terminal table."""

from __future__ import annotations

from cronscope.formatter import _c
from cronscope.heatmap import DAYS, HOURS, Heatmap

_SHADES = [" ", "░", "▒", "▓", "█"]


def _shade(count: int, max_count: int) -> str:
    if max_count == 0 or count == 0:
        return _SHADES[0]
    ratio = count / max_count
    idx = max(1, min(len(_SHADES) - 1, int(ratio * (len(_SHADES) - 1)) + 1))
    return _SHADES[idx]


def _cell_color(count: int, max_count: int, color: bool) -> str:
    if not color or max_count == 0 or count == 0:
        return _shade(count, max_count)
    ratio = count / max_count
    if ratio >= 0.75:
        code = "\033[91m"  # bright red
    elif ratio >= 0.4:
        code = "\033[93m"  # yellow
    else:
        code = "\033[92m"  # green
    return f"{code}{_shade(count, max_count)}\033[0m"


def format_heatmap(heatmap: Heatmap, color: bool = True) -> str:
    if not heatmap:
        return _c(f"Error: {heatmap.error}", "\033[91m", color)

    lines: list[str] = []
    expr_label = _c(heatmap.expression, "\033[96m", color)
    lines.append(f"Heatmap for {expr_label}")
    lines.append("")

    # Header row: hours 0-23 abbreviated to 2-char columns
    hour_header = "     " + "".join(f"{h:2d}".ljust(2) for h in HOURS)
    lines.append(_c(hour_header, "\033[90m", color))

    max_c = heatmap.max_count
    for d, day_name in enumerate(DAYS):
        row = f"{day_name} │"
        for h in HOURS:
            cnt = heatmap.get(d, h)
            cell = _cell_color(cnt, max_c, color)
            row += f" {cell}"
        lines.append(row)

    lines.append("")
    legend = "Legend: " + "  ".join(
        f"{_SHADES[i]} ={'low' if i==1 else 'mid' if i==2 else 'high' if i==3 else 'max' if i==4 else 'none'}"
        for i in range(len(_SHADES))
    )
    lines.append(_c(legend, "\033[90m", color))
    return "\n".join(lines)
