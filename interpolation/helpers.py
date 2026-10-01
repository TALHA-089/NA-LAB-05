"""Small helpers: number formatting and safe keyboard input."""
from fractions import Fraction


def fmt(value):
    """Show a number nicely: 27 (not 27/1), 0.086 (not 43/500)."""
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    text = f"{float(value):.10f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def read_int(prompt, low, high):
    """Keep asking until the user types a whole number from low to high."""
    while True:
        try:
            value = int(input(prompt).strip())
        except ValueError:
            print("  Please type a whole number, for example 6.")
            continue
        if low <= value <= high:
            return value
        print(f"  The number must be between {low} and {high}.")


def read_numbers(prompt, count):
    """Keep asking until the user types exactly `count` numbers on one line.
    Fraction("0.1") keeps the value exact (no 0.1000000000000001 noise)."""
    while True:
        parts = input(prompt).replace(",", " ").split()
        try:
            values = [Fraction(part) for part in parts]
        except (ValueError, ZeroDivisionError):
            print("  Use numbers only, separated by spaces.")
            continue
        if len(values) != count:
            print(f"  Expected {count} values but got {len(values)}. Try again.")
            continue
        return values


def step_size(x):
    """Return h if x increases with one constant step, otherwise None."""
    h = x[1] - x[0]
    if h <= 0:
        return None
    for i in range(len(x) - 1):
        if x[i + 1] - x[i] != h:
            return None
    return h
