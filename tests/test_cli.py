"""Tests for the cronscope CLI."""

import pytest
from unittest.mock import patch

from cronscope.cli import main, build_parser


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["* * * * *"])
    assert args.expression == "* * * * *"
    assert args.count == 5
    assert args.validate is False
    assert args.no_color is False


def test_build_parser_custom_count():
    parser = build_parser()
    args = parser.parse_args(["* * * * *", "-n", "10"])
    assert args.count == 10


def test_main_valid_expression(capsys):
    ret = main(["*/5 * * * *"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "*/5 * * * *" in captured.out


def test_main_valid_expression_no_color(capsys):
    ret = main(["*/5 * * * *", "--no-color"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "*/5 * * * *" in captured.out
    # No ANSI escape codes
    assert "\033[" not in captured.out


def test_main_custom_count(capsys):
    ret = main(["0 * * * *", "-n", "3"])
    assert ret == 0
    captured = capsys.readouterr()
    # Should contain 3 run entries
    assert captured.out.count("202") >= 3  # year digits in timestamps


def test_main_validate_valid(capsys):
    ret = main(["0 9 * * 1", "--validate"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "valid" in captured.out.lower()


def test_main_validate_invalid(capsys):
    ret = main(["99 * * * *", "--validate"])
    assert ret == 1
    captured = capsys.readouterr()
    assert captured.err  # error message goes to stderr


def test_main_invalid_expression_returns_1(capsys):
    ret = main(["not_a_cron"])
    assert ret == 1
    captured = capsys.readouterr()
    assert captured.err


def test_main_validate_no_color(capsys):
    ret = main(["* * * * *", "--validate", "--no-color"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "\033[" not in captured.out
