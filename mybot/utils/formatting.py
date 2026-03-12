"""Number formatting translated from _NumberFormat.au3."""

from __future__ import annotations


def number_format(number: int | float | str, null_to_zero: bool = False) -> str:
    """Format a number with space thousand separators.

    Translates AutoIt _NumberFormat():
        1234567 -> "1 234 567"
        -1234   -> "-1 234"
        ""      -> "" (or "0" if null_to_zero)

    Args:
        number: Number to format.
        null_to_zero: If True, return "0" for empty/None input.

    Returns:
        Formatted number string with space separators.
    """
    if number == "" or number is None:
        return "0" if null_to_zero else ""

    try:
        n = int(float(str(number)))
    except (ValueError, TypeError):
        return "0" if null_to_zero else ""

    if n < 0:
        return "-" + number_format(-n)

    # Format with space as thousand separator
    s = str(n)
    result = []
    for i, digit in enumerate(reversed(s)):
        if i > 0 and i % 3 == 0:
            result.append(" ")
        result.append(digit)

    return "".join(reversed(result))
