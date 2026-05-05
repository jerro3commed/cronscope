"""Command-line interface for cronscope."""

import argparse
import sys

from cronscope.parser import CronParseError
from cronscope.preview import next_runs
from cronscope.formatter import format_next_runs, format_validation_error


DEFAULT_COUNT = 5


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronscope",
        description="Visualize and validate cron expressions with next-run previews.",
    )
    parser.add_argument(
        "expression",
        help='Cron expression in quotes, e.g. "*/5 * * * *"',
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=DEFAULT_COUNT,
        metavar="N",
        help=f"Number of next runs to display (default: {DEFAULT_COUNT})",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Only validate the expression and exit (no preview)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    use_color = not args.no_color

    try:
        if args.validate:
            # Import here to trigger parse validation
            from cronscope.parser import parse
            parse(args.expression)
            msg = "OK" if not use_color else "\033[32mOK\033[0m"
            print(f"Expression is valid: {msg}")
            return 0

        runs = next_runs(args.expression, count=args.count)
        output = format_next_runs(args.expression, runs, color=use_color)
        print(output)
        return 0

    except CronParseError as exc:
        output = format_validation_error(args.expression, exc, color=use_color)
        print(output, file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
