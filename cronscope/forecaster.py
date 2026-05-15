"""Forecast how many times a cron expression fires within a future time window."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from cronscope.scheduler import CronScheduler
from cronscope.parser import CronParseError


@dataclass
class ForecastWindow:
    """A labelled slice of time with a run count."""

    label: str
    start: datetime
    end: datetime
    run_count: int

    def __bool__(self) -> bool:  # noqa: D105
        return self.run_count > 0


@dataclass
class ForecastResult:
    """Result of forecasting runs for a cron expression."""

    expression: str
    windows: List[ForecastWindow] = field(default_factory=list)
    total_runs: int = 0
    error: Optional[str] = None

    def __bool__(self) -> bool:  # noqa: D105
        return self.error is None


_GRANULARITY_DELTA = {
    "hour": timedelta(hours=1),
    "day": timedelta(days=1),
    "week": timedelta(weeks=1),
}

_GRANULARITY_FMT = {
    "hour": "%Y-%m-%d %H:00",
    "day": "%Y-%m-%d",
    "week": "Week of %Y-%m-%d",
}


def forecast(
    expression: str,
    *,
    start: Optional[datetime] = None,
    windows: int = 7,
    granularity: str = "day",
) -> ForecastResult:
    """Return a :class:`ForecastResult` for *expression* over *windows* periods.

    Parameters
    ----------
    expression:
        A standard five-field cron expression.
    start:
        Beginning of the forecast horizon (defaults to *now*).
    windows:
        Number of time windows to forecast.
    granularity:
        One of ``"hour"``, ``"day"``, or ``"week"``.
    """
    if granularity not in _GRANULARITY_DELTA:
        raise ValueError(f"granularity must be one of {list(_GRANULARITY_DELTA)}")

    if start is None:
        start = datetime.now().replace(second=0, microsecond=0)

    try:
        scheduler = CronScheduler(expression)
    except CronParseError as exc:
        return ForecastResult(expression=expression, error=str(exc))

    delta = _GRANULARITY_DELTA[granularity]
    fmt = _GRANULARITY_FMT[granularity]
    result_windows: List[ForecastWindow] = []
    total = 0

    for i in range(windows):
        win_start = start + delta * i
        win_end = win_start + delta
        count = sum(1 for _ in scheduler.iter_runs(after=win_start, before=win_end))
        result_windows.append(
            ForecastWindow(
                label=win_start.strftime(fmt),
                start=win_start,
                end=win_end,
                run_count=count,
            )
        )
        total += count

    return ForecastResult(expression=expression, windows=result_windows, total_runs=total)
