"""Format tagged cron expressions for terminal output."""

from typing import List

from cronscope.tagger import TaggedExpression
from cronscope.formatter import _c

_TAG_COLORS = {
    "every-minute": "\033[91m",   # bright red
    "high-frequency": "\033[93m", # bright yellow
    "frequent": "\033[33m",       # yellow
    "daily": "\033[32m",          # green
    "weekly": "\033[36m",         # cyan
    "rare": "\033[34m",           # blue
}
_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"


def _colorize_tag(tag: str, color: bool) -> str:
    color_code = _TAG_COLORS.get(tag, "\033[35m")
    return _c(f"[{tag}]", color_code, color)


def format_tags(
    tagged: List[TaggedExpression],
    color: bool = True,
) -> str:
    if not tagged:
        return _c("No expressions provided.", _DIM, color)

    lines: List[str] = []
    header = _c("Tagged Expressions", _BOLD, color)
    lines.append(header)
    lines.append(_c("-" * 40, _DIM, color))

    for item in tagged:
        expr_label = _c(item.expression, _BOLD, color)
        if not item:
            err = _c(f"  error: {item.error}", "\033[91m", color)
            lines.append(f"{expr_label}")
            lines.append(err)
        else:
            tag_str = "  " + "  ".join(
                _colorize_tag(t, color) for t in item.tags
            )
            lines.append(f"{expr_label}")
            lines.append(tag_str if item.tags else _c("  (no tags)", _DIM, color))

        lines.append("")

    return "\n".join(lines).rstrip()
