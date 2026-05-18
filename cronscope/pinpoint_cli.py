"""CLI entry point for the pinpoint sub-command."""

from __future__ import annotations

import argparse
from datetime import datetime

from cronscope.pinpointer import pinpoint
from cronscope.pinpoint_formatter import format_pinpoint

_DT_FMT = "%Y-%m-%dT%H:%M"


def build_pinpoint_parser(
    parser: argparse.ArgumentParser | None = None,
) -> argparse.ArgumentParser:
    if parser is None:
        parser = argparse.ArgumentParser(
            prog="cronscope-pinpoint",
            description="Find the next/previous run relative to a target datetime.",
        )
    parser.add_argument("expression", help="Cron expression (quoted)")
    parser.add_argument(
        "--at",
        metavar="DATETIME",
        default=None,
        help=f"Reference datetime in {_DT_FMT!r} format (default: now)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI color output",
    )
    parser.add_argument(
        "--look-back",
        type=int,
        default=5,
        metavar="N",
        help="Number of previous-run candidates to scan (default: 5)",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_pinpoint_parser()
    args = parser.parse_args(argv)

    target: datetime | None = None
    if args.at:
        try:
            target = datetime.strptime(args.at, _DT_FMT)
        except ValueError:
            parser.error(f"--at must be in format {_DT_FMT!r}")

    result = pinpoint(args.expression, target=target, look_back=args.look_back)
    print(format_pinpoint(result, color=not args.no_color))


if __name__ == "__main__":  # pragma: no cover
    main()
