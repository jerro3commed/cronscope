"""Format grouped cron expressions for terminal display."""

from cronscope.grouper import GroupedSchedule
from cronscope.formatter import _c


def format_group(grouped: GroupedSchedule, color: bool = True) -> str:
    """Render a GroupedSchedule as a human-readable terminal string."""
    lines = []

    header = _c("Grouped Cron Expressions", "1;36", color)
    lines.append(header)
    lines.append(_c("-" * 40, "90", color))

    if not grouped.groups and not grouped.ungrouped:
        lines.append(_c("No expressions to display.", "33", color))
        return "\n".join(lines)

    for label in grouped.group_labels:
        grp = grouped.groups[label]
        label_str = _c(f"[{label}]", "1;33", color)
        count_str = _c(f"({grp.count} expression{'s' if grp.count != 1 else ''})", "90", color)
        lines.append(f"  {label_str} {count_str}")

        for expr in grp.expressions:
            lines.append(f"    {_c(expr, '32', color)}")

        for expr, err in grp.errors.items():
            lines.append(f"    {_c(expr, '31', color)}  {_c('! ' + err, '90', color)}")

    if grouped.ungrouped:
        ug_label = _c("[ungrouped]", "1;35", color)
        lines.append(f"  {ug_label}")
        for expr in grouped.ungrouped:
            lines.append(f"    {_c(expr, '37', color)}")

    total = _c(f"Total: {grouped.total_expressions} expression(s) across {len(grouped.groups)} group(s)", "90", color)
    lines.append(_c("-" * 40, "90", color))
    lines.append(total)

    return "\n".join(lines)
