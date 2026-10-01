"""Newton forward / backward interpolation with automatic method choice."""
from dataclasses import dataclass
from fractions import Fraction

from .helpers import fmt


@dataclass
class Result:
    method: str            # "FORWARD" or "BACKWARD"
    origin: int            # index of x0 in the x list
    x0: Fraction
    p: Fraction
    value: Fraction
    where: str             # text: where the target sits in the table
    extrapolation: bool


def choose_method(x, target):
    """Pick the method and an initial origin index near the target.
    first half  -> FORWARD,  origin = point just BEFORE target
    second half -> BACKWARD, origin = point just AFTER  target

    For an in-table target, ``interpolate`` shifts a right-side origin left
    when that initial choice would make p negative. Extrapolation may still
    have p outside the 0 < p < 1 interpolation range.
    """
    n = len(x)
    if target < x[0]:
        return "FORWARD", 0, "below the table", True
    if target > x[-1]:
        return "BACKWARD", n - 1, "above the table", True

    i = 0
    while not (x[i] <= target <= x[i + 1]):      # find the interval [x_i, x_i+1]
        i += 1
    where = f"in [{fmt(x[i])}, {fmt(x[i + 1])}]"

    middle = (x[0] + x[-1]) / 2
    if target <= middle:
        return "FORWARD", i, where, False
    return "BACKWARD", i + 1, where, False


def newton_forward(table, origin, p):
    """f0 + p*Df0 + p(p-1)/2! * D2f0 + ...  (differences go DOWN from origin)."""
    total = Fraction(0)
    coeff = Fraction(1)
    for k in range(len(table) - origin):
        if k > 0:
            coeff = coeff * (p - (k - 1)) / k
        total += coeff * table[k][origin]
    return total


def newton_backward(table, origin, p):
    """f0 + p*Nf0 + p(p+1)/2! * N2f0 + ...  (differences go UP from origin)."""
    total = Fraction(0)
    coeff = Fraction(1)
    for k in range(origin + 1):
        if k > 0:
            coeff = coeff * (p + (k - 1)) / k
        total += coeff * table[k][origin - k]
    return total


def interpolate(x, table, h, target):
    method, origin, where, extrapolation = choose_method(x, target)
    p = (target - x[origin]) / h
    if not extrapolation and p < 0:
        origin -= 1
        p = (target - x[origin]) / h
    if method == "FORWARD":
        value = newton_forward(table, origin, p)
    else:
        value = newton_backward(table, origin, p)
    return Result(method, origin, x[origin], p, value, where, extrapolation)
