"""Human-readable descriptions of cron schedule frequency."""

from cronscope.parser import CronExpression


def _field_summary(values: list, unit: str, singular: str) -> str:
    """Return a short summary string for a single cron field."""
    if values is None:
        return f"every {unit}"
    if len(values) == 1:
        return f"at {singular} {values[0]}"
    if len(values) <= 4:
        joined = ", ".join(str(v) for v in values[:-1])
        return f"at {unit}s {joined} and {values[-1]}"
    return f"at {len(values)} specific {unit}s"


def humanize(expr: CronExpression) -> str:
    """Return a human-readable description of a CronExpression.

    Examples
    --------
    >>> from cronscope.parser import parse
    >>> humanize(parse("* * * * *"))
    'every minute'
    >>> humanize(parse("0 9 * * 1"))
    'at minute 0, at hour 9, on weekday 1'
    """
    parts = []

    minute = expr.minute
    hour = expr.hour
    dom = expr.day_of_month
    month = expr.month
    dow = expr.day_of_week

    if minute is None and hour is None and dom is None and month is None and dow is None:
        return "every minute"

    parts.append(_field_summary(minute, "minute", "minute"))

    if hour is not None:
        parts.append(_field_summary(hour, "hour", "hour"))

    if dom is not None:
        parts.append(_field_summary(dom, "day-of-month", "day"))

    if month is not None:
        month_names = [
            None, "January", "February", "March", "April",
            "May", "June", "July", "August", "September",
            "October", "November", "December",
        ]
        named = [month_names[m] if 1 <= m <= 12 else str(m) for m in month]
        if len(named) == 1:
            parts.append(f"in {named[0]}")
        else:
            parts.append("in " + ", ".join(named[:-1]) + f" and {named[-1]}")

    if dow is not None:
        day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        named = [day_names[d] if 0 <= d <= 6 else str(d) for d in dow]
        if len(named) == 1:
            parts.append(f"on {named[0]}")
        else:
            parts.append("on " + ", ".join(named[:-1]) + f" and {named[-1]}")

    return ", ".join(parts)
