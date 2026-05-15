"""Tests for cronscope.forecaster and cronscope.forecast_formatter."""

from datetime import datetime, timedelta

import pytest

from cronscope.forecaster import ForecastResult, ForecastWindow, forecast
from cronscope.forecast_formatter import format_forecast


_START = datetime(2024, 1, 15, 0, 0, 0)


# ---------------------------------------------------------------------------
# ForecastResult helpers
# ---------------------------------------------------------------------------

def test_forecast_result_bool_true_when_no_error():
    r = ForecastResult(expression="* * * * *")
    assert bool(r) is True


def test_forecast_result_bool_false_when_error():
    r = ForecastResult(expression="bad", error="parse error")
    assert bool(r) is False


def test_forecast_window_bool_true_when_runs():
    w = ForecastWindow(label="x", start=_START, end=_START + timedelta(days=1), run_count=5)
    assert bool(w) is True


def test_forecast_window_bool_false_when_no_runs():
    w = ForecastWindow(label="x", start=_START, end=_START + timedelta(days=1), run_count=0)
    assert bool(w) is False


# ---------------------------------------------------------------------------
# forecast()
# ---------------------------------------------------------------------------

def test_forecast_returns_forecast_result():
    result = forecast("* * * * *", start=_START, windows=3, granularity="day")
    assert isinstance(result, ForecastResult)


def test_forecast_invalid_expression_sets_error():
    result = forecast("not a cron", start=_START)
    assert not result
    assert result.error is not None


def test_forecast_correct_number_of_windows():
    result = forecast("* * * * *", start=_START, windows=5, granularity="day")
    assert len(result.windows) == 5


def test_forecast_every_minute_fills_day_windows():
    result = forecast("* * * * *", start=_START, windows=2, granularity="day")
    for window in result.windows:
        assert window.run_count == 60 * 24


def test_forecast_total_runs_is_sum_of_windows():
    result = forecast("* * * * *", start=_START, windows=3, granularity="day")
    assert result.total_runs == sum(w.run_count for w in result.windows)


def test_forecast_daily_at_midnight_one_run_per_day():
    result = forecast("0 0 * * *", start=_START, windows=4, granularity="day")
    for window in result.windows:
        assert window.run_count == 1


def test_forecast_hourly_granularity():
    result = forecast("0 * * * *", start=_START, windows=3, granularity="hour")
    assert len(result.windows) == 3
    for window in result.windows:
        assert window.run_count == 1


def test_forecast_invalid_granularity_raises():
    with pytest.raises(ValueError, match="granularity"):
        forecast("* * * * *", start=_START, granularity="month")


# ---------------------------------------------------------------------------
# format_forecast()
# ---------------------------------------------------------------------------

def test_format_forecast_returns_string():
    result = forecast("0 0 * * *", start=_START, windows=3)
    assert isinstance(format_forecast(result), str)


def test_format_forecast_contains_expression():
    result = forecast("0 0 * * *", start=_START, windows=3)
    assert "0 0 * * *" in format_forecast(result, color=False)


def test_format_forecast_shows_total_runs():
    result = forecast("0 0 * * *", start=_START, windows=3)
    output = format_forecast(result, color=False)
    assert "Total" in output
    assert "3" in output


def test_format_forecast_invalid_shows_error():
    result = ForecastResult(expression="bad expr", error="invalid")
    output = format_forecast(result, color=False)
    assert "Error" in output
    assert "invalid" in output


def test_format_forecast_no_color_has_no_ansi():
    result = forecast("* * * * *", start=_START, windows=2)
    output = format_forecast(result, color=False)
    assert "\x1b[" not in output
