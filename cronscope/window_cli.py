"""CLI entry point for the window-analysis sub-command."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from cronscope.window_analyzer import analyze_windows
from cronscope.window_formatter import format_window_analysis


def build_window_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        prog="cronscope-window",
        description="Analyze cron firing frequency across time windows.",
    )
    if parent is not None:
        parser = parent.add_parser("window", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument("expression", help="Cron expression to analyze")
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        metavar="N",
        help="Number of days to analyze (default: 7)",
    )
    parser.add_argument(
        "--window-hours",
        type=int,
        default=6,
        dest="window_hours",
        metavar="H",
        help="Size of each window in hours (default: 6)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_window_parser()
    args = parser.parse_args(argv)

    analysis = analyze_windows(
        expression=args.expression,
        now=datetime.now().replace(second=0, microsecond=0),
        days=args.days,
        window_hours=args.window_hours,
    )
    output = format_window_analysis(analysis, color=not args.no_color)
    print(output)
    if not analysis:
        sys.exit(1)


if __name__ == "__main__":
    main()
