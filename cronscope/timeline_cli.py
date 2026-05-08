"""CLI entry point for the timeline subcommand."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from cronscope.timeline import build_timeline
from cronscope.timeline_formatter import format_timeline


def build_timeline_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronscope-timeline",
        description="Visualize cron expression runs as a timeline bar chart.",
    )
    parser.add_argument("expression", help="Cron expression (5 fields)")
    parser.add_argument(
        "--periods",
        type=int,
        default=24,
        help="Number of time windows to display (default: 24)",
    )
    parser.add_argument(
        "--granularity",
        choices=["hour", "day"],
        default="hour",
        help="Window size: 'hour' or 'day' (default: hour)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_timeline_parser()
    args = parser.parse_args(argv)

    try:
        timeline = build_timeline(
            expression=args.expression,
            periods=args.periods,
            granularity=args.granularity,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output = format_timeline(timeline, use_color=not args.no_color)
    print(output)

    if not timeline:
        sys.exit(1)


if __name__ == "__main__":
    main()
