"""Formatter for snapshot entries and deltas."""

from __future__ import annotations

from cronscope.snapshot import SnapshotEntry, SnapshotDelta
from cronscope.formatter import _c

_DATE_FMT = "%Y-%m-%d %H:%M:%S"


def format_snapshot(entry: SnapshotEntry, color: bool = True) -> str:
    """Render a SnapshotEntry as a human-readable string."""
    lines: list[str] = []
    header = _c(f"Snapshot: {entry.expression}", "cyan", color)
    lines.append(header)
    lines.append(_c(f"Captured at: {entry.captured_at.strftime(_DATE_FMT)}", "white", color))

    if not entry:
        lines.append(_c(f"  Error: {entry.error}", "red", color))
        return "\n".join(lines)

    if not entry.next_runs:
        lines.append(_c("  No upcoming runs found.", "yellow", color))
    else:
        for run in entry.next_runs:
            lines.append("  " + _c(run.strftime(_DATE_FMT), "green", color))
    return "\n".join(lines)


def format_snapshot_delta(delta: SnapshotDelta, color: bool = True) -> str:
    """Render a SnapshotDelta showing added, removed and unchanged runs."""
    lines: list[str] = []
    lines.append(_c(f"Snapshot Delta: {delta.expression}", "cyan", color))
    lines.append(
        _c(
            f"  Before: {delta.before.captured_at.strftime(_DATE_FMT)}  "
            f"After: {delta.after.captured_at.strftime(_DATE_FMT)}",
            "white",
            color,
        )
    )

    if not delta.has_changes:
        lines.append(_c("  No changes detected.", "green", color))
    else:
        for run in delta.added:
            lines.append("  " + _c(f"+ {run.strftime(_DATE_FMT)}", "green", color))
        for run in delta.removed:
            lines.append("  " + _c(f"- {run.strftime(_DATE_FMT)}", "red", color))

    if delta.unchanged:
        lines.append(_c(f"  Unchanged: {len(delta.unchanged)} run(s)", "white", color))

    return "\n".join(lines)
