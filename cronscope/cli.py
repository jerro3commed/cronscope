"""Command-line interface for cronscope."""

import argparse
import sys
from cronscope.preview import preview
from cronscope.validator import validate
from cronscope.formatter import format_validation_error


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="cronscope",
        description="Visualize and validate cron expressions with next-run previews.",
    )
    parser.add_argument(
        "expression",
        help="Cron expression to evaluate (e.g. '*/5 * * * *')",
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of next runs to display (default: 5)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        default=False,
        help="Only validate the expression without showing next runs",
    )
    return parser


def main(argv=None) -> int:
    """Entry point for the cronscope CLI.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    use_color = not args.no_color

    if args.validate:
        result = validate(args.expression)
        if result.valid:
            msg = "OK" if not use_color else "\033[32mOK\033[0m"
            print(f"Expression '{args.expression}' is valid. {msg}")
            return 0
        else:
            print(
                format_validation_error(args.expression, result.error, color=use_color),
                file=sys.stderr,
            )
            return 1

    output = preview(
        args.expression,
        count=args.count,
        color=use_color,
    )

    if output is None:
        print(f"Error: invalid cron expression '{args.expression}'", file=sys.stderr)
        return 1

    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
