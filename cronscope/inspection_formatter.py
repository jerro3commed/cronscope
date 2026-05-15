"""Format an InspectionResult for terminal output."""

from cronscope.inspector import InspectionResult
from cronscope.formatter import _c

_LABEL_WIDTH = 14


def format_inspection(result: InspectionResult, color: bool = True) -> str:
    """Render a structured inspection of a cron expression as a string."""
    lines: list[str] = []

    header = _c("Inspection: ", "cyan", color) + _c(result.expression, "white", color)
    lines.append(header)
    lines.append(_c("-" * 44, "cyan", color))

    if not result:
        lines.append(_c(f"  Error: {result.error}", "red", color))
        return "\n".join(lines)

    lines.append(
        _c("  Summary : ", "yellow", color) + result.human_summary
    )
    lines.append("")

    for fi in result.fields:
        label = (fi.name.replace("_", " ") + ":").ljust(_LABEL_WIDTH)
        flags = []
        if fi.is_wildcard:
            flags.append(_c("wildcard", "green", color))
        if fi.is_step:
            flags.append(_c("step", "magenta", color))
        if fi.is_list:
            flags.append(_c("list", "blue", color))
        if fi.is_range:
            flags.append(_c("range", "cyan", color))

        flag_str = ("  [" + ", ".join(flags) + "]") if flags else ""
        raw_part = _c(fi.raw.ljust(10), "white", color)
        expl_part = fi.explanation

        lines.append(
            f"  {_c(label, 'yellow', color)} {raw_part}  {expl_part}{flag_str}"
        )

    return "\n".join(lines)
