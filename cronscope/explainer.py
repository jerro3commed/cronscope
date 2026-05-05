"""Human-readable explanation of cron expressions."""

from .parser import CronExpression, parse, CronParseError

_MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

_DOW_NAMES = [
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday"
]


def _explain_field(value: str, field: str) -> str:
    """Return a human-readable description of a single cron field."""
    if value == "*":
        return None

    if "/" in value:
        base, step = value.split("/", 1)
        base_str = "every value" if base == "*" else f"starting at {base}"
        return f"every {step} {field}(s) ({base_str})"

    if "," in value:
        parts = value.split(",")
        if field == "month":
            named = [_MONTH_NAMES[int(p)] for p in parts]
        elif field == "weekday":
            named = [_DOW_NAMES[int(p)] for p in parts]
        else:
            named = parts
        return f"on {field}(s): {', '.join(named)}"

    if "-" in value:
        start, end = value.split("-", 1)
        return f"{field} {start} through {end}"

    if field == "month":
        return f"in {_MONTH_NAMES[int(value)]}"
    if field == "weekday":
        return f"on {_DOW_NAMES[int(value)]}"
    return f"{field} {value}"


def explain(expression: str) -> str:
    """Return a human-readable explanation of a cron expression string."""
    expr: CronExpression = parse(expression)

    parts = []
    minute = _explain_field(expr.minute, "minute")
    hour = _explain_field(expr.hour, "hour")
    dom = _explain_field(expr.day_of_month, "day-of-month")
    month = _explain_field(expr.month, "month")
    dow = _explain_field(expr.day_of_week, "weekday")

    if minute is None and hour is None:
        parts.append("every minute")
    else:
        if minute:
            parts.append(minute)
        if hour:
            parts.append(hour)
        else:
            if minute is None:
                parts.append("every minute")

    if dom:
        parts.append(dom)
    if month:
        parts.append(month)
    if dow:
        parts.append(dow)

    if not parts:
        parts.append("every minute")

    return "Runs " + ", ".join(parts) + "."
