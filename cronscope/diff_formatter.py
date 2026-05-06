"""Format a CronDiff for terminal output."""

from cronscope.differ import CronDiff
from cronscope.formatter import _c


def format_diff(diff: CronDiff, color: bool = True) -> str:
    """Render a CronDiff as a human-readable terminal string.

    Args:
        diff: The CronDiff to render.
        color: Whether to use ANSI colour codes.

    Returns:
        A formatted multi-line string.
    """
    lines = []

    header = _c("bold", "Cron Diff", color)
    lines.append(header)
    lines.append(
        f"  {_c('cyan', 'A', color)}: {diff.left_expr}"
        f"  {_c('cyan', 'B', color)}: {diff.right_expr}"
    )
    lines.append("")

    if diff.left_error:
        lines.append(_c("red", f"  Error in A: {diff.left_error}", color))
    if diff.right_error:
        lines.append(_c("red", f"  Error in B: {diff.right_error}", color))
    if diff.has_errors:
        return "\n".join(lines)

    col_w = 14
    header_row = (
        _c("bold", f"  {'Field':<{col_w}}", color)
        + _c("bold", f"{'A':<{col_w}}", color)
        + _c("bold", f"{'B':<{col_w}}", color)
        + _c("bold", "Status", color)
    )
    lines.append(header_row)
    lines.append("  " + "-" * (col_w * 3 + 8))

    for field in diff.fields:
        if field.changed:
            status = _c("yellow", "changed", color)
            left_val = _c("red", field.left, color)
            right_val = _c("green", field.right, color)
        else:
            status = _c("green", "same", color)
            left_val = field.left
            right_val = field.right

        lines.append(
            f"  {field.name:<{col_w}}{left_val:<{col_w}}{right_val:<{col_w}}{status}"
        )

    lines.append("")
    if diff.is_identical:
        lines.append(_c("green", "  Expressions are identical.", color))
    else:
        count = len(diff.changed_fields)
        noun = "field" if count == 1 else "fields"
        lines.append(_c("yellow", f"  {count} {noun} differ.", color))

    return "\n".join(lines)
