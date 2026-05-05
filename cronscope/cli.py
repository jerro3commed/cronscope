"""Command-line interface for cronscope."""

import argparse
import sys

from cronscope.parser import parse, CronParseError
from cronscope.formatter import format_next_runs, format_validation_error
from cronscope.humanizer import humanize
from cronscope.preview import next_runs as get_next_runs


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cronscope",
        description="Visualize and validate cron expressions.",
    )
    p.add_argument("expression", nargs="?", help="Cron expression (5 fields)")
    p.add_argument(
        "-n", "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of next-run times to display (default: 5)",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI color output",
    )
    p.add_argument(
        "--explain",
        action="store_true",
        default=False,
        help="Show field-level explanation of the expression",
    )
    p.add_argument(
        "--humanize",
        action="store_true",
        default=False,
        help="Show a human-readable summary of the schedule",
    )
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.expression:
        parser.print_help()
        return 0

    color = not args.no_color

    try:
        expr = parse(args.expression)
    except CronParseError as exc:
        print(format_validation_error(str(exc), color=color))
        return 1

    if args.humanize:
        print(humanize(expr))

    if args.explain:
        from cronscope.explainer import explain
        print(explain(expr))

    runs = get_next_runs(args.expression, count=args.count)
    print(format_next_runs(args.expression, runs, color=color))

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
