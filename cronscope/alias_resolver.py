"""Resolve common cron aliases and macro expressions to standard 5-field cron strings."""

from typing import Dict, Tuple

# Standard cron macros mapped to their 5-field equivalents
_MACROS: Dict[str, str] = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
    "@every_minute": "* * * * *",
}

# Human-readable descriptions for each macro
_MACRO_DESCRIPTIONS: Dict[str, str] = {
    "@yearly": "Once a year, at midnight on January 1st",
    "@annually": "Once a year, at midnight on January 1st",
    "@monthly": "Once a month, at midnight on the 1st",
    "@weekly": "Once a week, at midnight on Sunday",
    "@daily": "Once a day, at midnight",
    "@midnight": "Once a day, at midnight",
    "@hourly": "Once an hour, at the start of the hour",
    "@every_minute": "Every minute",
}


class AliasResolutionError(ValueError):
    """Raised when an alias or macro cannot be resolved."""


class ResolvedAlias:
    """Result of resolving a cron alias or macro."""

    def __init__(self, original: str, resolved: str, description: str, is_macro: bool):
        self.original = original
        self.resolved = resolved
        self.description = description
        self.is_macro = is_macro

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ResolvedAlias(original={self.original!r}, "
            f"resolved={self.resolved!r}, is_macro={self.is_macro})"
        )


def is_macro(expression: str) -> bool:
    """Return True if the expression is a recognised macro like @daily."""
    return expression.strip().lower() in _MACROS


def resolve(expression: str) -> ResolvedAlias:
    """Resolve a cron macro or return the expression unchanged.

    Parameters
    ----------
    expression:
        A cron expression or macro string (e.g. ``@daily`` or ``0 0 * * *``).

    Returns
    -------
    ResolvedAlias
        Object containing the original expression, the resolved 5-field string,
        a human-readable description, and whether it was a macro.

    Raises
    ------
    AliasResolutionError
        If the expression starts with ``@`` but is not a known macro.
    """
    stripped = expression.strip()
    lower = stripped.lower()

    if lower in _MACROS:
        return ResolvedAlias(
            original=stripped,
            resolved=_MACROS[lower],
            description=_MACRO_DESCRIPTIONS[lower],
            is_macro=True,
        )

    if stripped.startswith("@"):
        raise AliasResolutionError(
            f"Unknown cron macro: {stripped!r}. "
            f"Known macros: {', '.join(sorted(_MACROS))}"
        )

    return ResolvedAlias(
        original=stripped,
        resolved=stripped,
        description="",
        is_macro=False,
    )


def list_macros() -> Tuple[Tuple[str, str, str], ...]:
    """Return all known macros as tuples of (macro, expression, description)."""
    return tuple(
        (macro, _MACROS[macro], _MACRO_DESCRIPTIONS[macro])
        for macro in sorted(_MACROS)
    )
