"""CLI entry point for cron expression grouping via cronscope."""

import argparse
import sys
from typing import List, Optional

from cronscope.grouper import group
from cronscope.group_formatter import format_group


VALID_STRATEGIES = ("frequency", "hour", "day")


def build_group_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronscope-group",
        description="Group cron expressions by a shared schedule characteristic.",
    )
    parser.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="One or more cron expressions to group.",
    )
    parser.add_argument(
        "--by",
        choices=VALID_STRATEGIES,
        default="frequency",
        help="Grouping strategy (default: frequency).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_group_parser()
    args = parser.parse_args(argv)

    grouped = group(args.expressions, by=args.by)
    output = format_group(grouped, color=not args.no_color)
    print(output)

    if grouped.groups.get("invalid") and grouped.groups["invalid"].has_errors:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
