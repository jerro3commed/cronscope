"""CLI entry point for the overlap detection feature."""

from __future__ import annotations

import argparse
import sys

from cronscope.overlap import find_overlaps
from cronscope.overlap_formatter import format_overlap


def build_overlap_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronscope-overlap",
        description="Detect time-slot overlaps across multiple cron expressions.",
    )
    parser.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="Two or more cron expressions to compare.",
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=50,
        metavar="N",
        help="Number of upcoming runs to sample per expression (default: 50).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable terminal colour output.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_overlap_parser()
    args = parser.parse_args(argv)

    if len(args.expressions) < 2:
        parser.error("At least two cron expressions are required.")

    report = find_overlaps(args.expressions, count=args.count)
    output = format_overlap(report, color=not args.no_color)
    print(output)

    if not report:
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
