"""CLI entry point for the snapshot sub-command."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta

from cronscope.snapshot import take_snapshot, diff_snapshots
from cronscope.snapshot_formatter import format_snapshot, format_snapshot_delta


def build_snapshot_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[name-defined]
    kwargs = dict(description="Capture and compare cron schedule snapshots.")
    parser = (
        parent.add_parser("snapshot", **kwargs)  # type: ignore[arg-type]
        if parent is not None
        else argparse.ArgumentParser(**kwargs)
    )
    parser.add_argument("expression", help="Cron expression to snapshot.")
    parser.add_argument("-n", "--count", type=int, default=5, help="Number of next runs (default: 5).")
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Simulate a delta by shifting the reference time forward by one hour.",
    )
    parser.add_argument("--no-color", action="store_true", help="Disable colored output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_snapshot_parser()
    args = parser.parse_args(argv)
    color = not args.no_color
    now = datetime.now()

    before = take_snapshot(args.expression, count=args.count, now=now)

    if args.diff:
        after = take_snapshot(args.expression, count=args.count, now=now + timedelta(hours=1))
        delta = diff_snapshots(before, after)
        print(format_snapshot_delta(delta, color=color))
    else:
        print(format_snapshot(before, color=color))

    return 0 if bool(before) else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
