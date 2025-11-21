from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def absolute(value):
    """
    Returns the absolute value of the input
    """
    try:
        return abs(value)
    except (TypeError, AttributeError):
        return value


@register.filter
def floatformat_default(value, arg=2):
    """
    Format a number with a specified number of decimal places, handling various data types
    """
    try:
        # Convert to float for consistent formatting
        if isinstance(value, Decimal):
            value = float(value)
        elif value is None:
            value = 0.0

        return f"{value:.{arg}f}"
    except (TypeError, ValueError):
        return value