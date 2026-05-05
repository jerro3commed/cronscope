"""Next-run calculation for cron expressions."""

from datetime import datetime, timedelta
from typing import Iterator, List

from .parser import CronExpression


class CronScheduler:
    """Computes next scheduled run times for a parsed cron expression."""

    def __init__(self, expr: CronExpression, base_time: datetime | None = None):
        self.expr = expr
        self.base_time = base_time or datetime.now().replace(second=0, microsecond=0)

    def _matches(self, dt: datetime) -> bool:
        """Return True if *dt* satisfies every field of the cron expression."""
        checks = [
            (self.expr.minute, dt.minute),
            (self.expr.hour, dt.hour),
            (self.expr.day, dt.day),
            (self.expr.month, dt.month),
            (self.expr.weekday, dt.weekday() + 1),  # cron: 1=Mon … 7=Sun
        ]
        for allowed, value in checks:
            if allowed is not None and value not in allowed:
                return False
        return True

    def next_runs(self, count: int = 10) -> List[datetime]:
        """Return the next *count* run datetimes after base_time."""
        results: List[datetime] = []
        candidate = self.base_time + timedelta(minutes=1)
        # Guard: stop searching after 4 years to avoid infinite loops
        limit = candidate + timedelta(days=4 * 365)
        while len(results) < count and candidate < limit:
            if self._matches(candidate):
                results.append(candidate)
            candidate += timedelta(minutes=1)
        return results

    def iter_runs(self) -> Iterator[datetime]:
        """Infinite iterator of future run datetimes."""
        candidate = self.base_time + timedelta(minutes=1)
        limit = candidate + timedelta(days=4 * 365)
        while candidate < limit:
            if self._matches(candidate):
                yield candidate
            candidate += timedelta(minutes=1)
