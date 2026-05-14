"""CLI entry point for cadence analysis."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from cronscope.cadence import analyze_cadence
from cronscope.cadence_formatter import format_cadence


def build_cadence_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronscope-cadence",
        description="Analyze the interval regularity of a cron expression.",
    )
    parser.add_argument("expression", help="Cron expression to analyze")
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=20,
        metavar="N",
        help="Number of runs to sample (default: 20)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI color output",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_cadence_parser()
    args = parser.parse_args(argv)

    result = analyze_cadence(
        expression=args.expression,
        count=args.count,
        start=datetime.now().replace(second=0, microsecond=0),
    )

    output = format_cadence(result, color=not args.no_color)
    print(output)

    if not result:
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
