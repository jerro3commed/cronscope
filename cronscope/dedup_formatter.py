"""Formatter for DeduplicationResult output."""

from __future__ import annotations

from .deduplicator import DeduplicationResult


def format_dedup(result: DeduplicationResult, color: bool = True) -> str:
    """Render a DeduplicationResult as a human-readable string.

    Args:
        result: The DeduplicationResult to format.
        color:  Whether to emit ANSI color codes.

    Returns:
        A formatted string suitable for terminal output.
    """

    def _c(text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if color else text

    lines: list[str] = []

    header = _c("Deduplication Report", "1;36")
    lines.append(header)
    lines.append(
        f"  Total : {result.total_expressions}  "
        f"Unique : {result.unique_count}  "
        f"Duplicates : {result.duplicate_count}  "
        f"Invalid : {len(result.invalid)}"
    )
    lines.append("")

    if result.groups:
        lines.append(_c("Unique Schedules", "1;33"))
        for group in result.groups:
            canonical_label = _c(group.canonical, "32" if not group.is_duplicate else "33")
            dup_tag = _c(" [duplicate]", "33") if group.is_duplicate else ""
            lines.append(f"  {canonical_label}{dup_tag}")
            for expr in group.expressions:
                marker = "  →" if expr != group.canonical else "  ="
                lines.append(f"    {_c(marker, '90')} {expr}")
        lines.append("")

    if result.invalid:
        lines.append(_c("Invalid Expressions", "1;31"))
        for expr, err in result.invalid:
            lines.append(f"  {_c(expr, '31')}  — {err}")
        lines.append("")

    return "\n".join(lines).rstrip()
