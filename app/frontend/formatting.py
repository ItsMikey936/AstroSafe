"""Turns raw numbers from the backend into text for the screens."""

EMPTY = "--"


def format_number(value: float | None, decimals: int = 1) -> str:
    """37.25 -> '37.2'; 30.0 -> '30'; None -> '--'."""
    if value is None:
        return EMPTY
    text = f"{value:.{decimals}f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def format_with_unit(value: float | None, unit: str,
                     decimals: int = 1) -> str:
    """(37.2, '°C') -> '37.2 °C'; (10, '/100') -> '10/100'."""
    number = format_number(value, decimals)
    if value is None or not unit:
        return number
    if unit.startswith("/"):
        return f"{number}{unit}"
    return f"{number} {unit}"


def format_hours(hours: float | None) -> str:
    """7.5 -> '7:30 hr'."""
    if hours is None:
        return EMPTY
    total_minutes = round(hours * 60)
    return f"{total_minutes // 60}:{total_minutes % 60:02d} hr"
