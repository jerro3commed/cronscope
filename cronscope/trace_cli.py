"""CLI entry point for the trace sub-command."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from .tracer import trace
from .trace_formatter import format_trace


def build_trace_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    description = "Trace which fields of a cron expression match a specific datetime."
    if parent is not None:
        parser = parent.add_parser("trace", description=description, help=description)
    else:
        parser = argparse.ArgumentParser(prog="cronscope-trace", description=description)

    parser.add_argument("expression", help="Cron expression (quoted), e.g. '*/5 9-17 * * 1-5'")
    parser.add_argument(
        "datetime",
        metavar="DATETIME",
        help="Datetime to test against, format: YYYY-MM-DDTHH:MM or 'YYYY-MM-DD HH:MM'",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_trace_parser()
    args = parser.parse_args(argv)

    raw_dt = args.datetime.replace("T", " ")
    try:
        dt = datetime.strptime(raw_dt, "%Y-%m-%d %H:%M")
    except ValueError:
        print(f"Error: cannot parse datetime '{args.datetime}'. Use YYYY-MM-DDTHH:MM.", file=sys.stderr)
        return 2

    result = trace(args.expression, dt)
    print(format_trace(result, color=not args.no_color))
    return 0 if result.matched else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
