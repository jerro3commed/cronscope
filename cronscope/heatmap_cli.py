"""CLI entry-point for the heatmap sub-command."""

from __future__ import annotations

import argparse
import sys

from cronscope.heatmap import build_heatmap
from cronscope.heatmap_formatter import format_heatmap


def build_heatmap_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronscope-heatmap",
        description="Display an hour-of-day × day-of-week heatmap for a cron expression.",
    )
    parser.add_argument("expression", help="Cron expression (5 fields, quoted)")
    parser.add_argument(
        "--weeks",
        type=int,
        default=4,
        metavar="N",
        help="Number of weeks to simulate (default: 4)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_heatmap_parser()
    args = parser.parse_args(argv)

    heatmap = build_heatmap(args.expression, weeks=args.weeks)
    output = format_heatmap(heatmap, color=not args.no_color)
    print(output)
    return 0 if bool(heatmap) else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
