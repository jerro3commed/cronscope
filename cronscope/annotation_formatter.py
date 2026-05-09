"""Format annotated cron expressions for terminal display."""

from __future__ import annotations

from .annotator import AnnotatedExpression
from .formatter import _c

_FIELD_COLOR = "\033[36m"   # cyan
_NOTE_COLOR  = "\033[33m"   # yellow
_RAW_COLOR   = "\033[97m"   # bright white
_ERR_COLOR   = "\033[31m"   # red
_RESET       = "\033[0m"


def format_annotation(ann: AnnotatedExpression, *, color: bool = True) -> str:
    """Render an AnnotatedExpression as a terminal-friendly string."""
    lines: list[str] = []

    header = _c(f"Annotation: {ann.expression}", "\033[1m", color)
    lines.append(header)
    lines.append(_c("-" * 40, "\033[90m", color))

    if ann.error:
        lines.append(_c(f"  Error: {ann.error}", _ERR_COLOR, color))
        return "\n".join(lines)

    col_w = max(len(f.name) for f in ann.fields) + 2

    for field in ann.fields:
        name_part = _c(field.name.ljust(col_w), _FIELD_COLOR, color)
        raw_part  = _c(field.raw.ljust(10), _RAW_COLOR, color)
        note_part = _c(field.note, _NOTE_COLOR, color)
        lines.append(f"  {name_part}{raw_part}  # {note_part}")

    return "\n".join(lines)
