"""CLI entry-point for the profiler feature."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from .profiler import profile
from .profile_formatter import format_profile


def build_profile_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronscope-profile",
        description="Profile a cron expression's run distribution.",
    )
    parser.add_argument("expression", help="Cron expression to profile")
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        metavar="N",
        help="Number of days to sample (default: 7)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_profile_parser()
    args = parser.parse_args(argv)

    start = datetime.now().replace(second=0, microsecond=0)
    result = profile(args.expression, start=start, sample_days=args.days)
    output = format_profile(result, color=not args.no_color)
    print(output)

    if not result:
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
