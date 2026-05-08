"""Heatmap module: build an hour-of-day × day-of-week run frequency matrix."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from cronscope.parser import CronParseError, parse
from cronscope.scheduler import CronScheduler

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
HOURS = list(range(24))


@dataclass
class HeatmapCell:
    day: int   # 0=Monday … 6=Sunday
    hour: int  # 0-23
    count: int = 0


@dataclass
class Heatmap:
    expression: str
    error: Optional[str] = None
    # cells[day][hour] = count
    cells: Dict[int, Dict[int, int]] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return self.error is None

    @property
    def max_count(self) -> int:
        if not self.cells:
            return 0
        return max(
            count
            for day_map in self.cells.values()
            for count in day_map.values()
        )

    def get(self, day: int, hour: int) -> int:
        return self.cells.get(day, {}).get(hour, 0)


def build_heatmap(expression: str, weeks: int = 4, start: Optional[datetime] = None) -> Heatmap:
    """Return a Heatmap for *expression* covering *weeks* calendar weeks."""
    try:
        parse(expression)
    except CronParseError as exc:
        return Heatmap(expression=expression, error=str(exc))

    origin = start or datetime.now().replace(second=0, microsecond=0)
    end = origin + timedelta(weeks=weeks)

    scheduler = CronScheduler(expression, start=origin)
    cells: Dict[int, Dict[int, int]] = {d: {h: 0 for h in HOURS} for d in range(7)}

    for run in scheduler.iter_runs():
        if run >= end:
            break
        day_index = run.weekday()  # Monday=0
        cells[day_index][run.hour] += 1

    return Heatmap(expression=expression, cells=cells)
