"""Build the polynomial that passes through ALL the data points.

Newton form:  P(x) = sum_k  [ D^k f0 / (k! * h^k) ] * (x-x0)(x-x1)...(x-x_{k-1})
We multiply the (x - root) factors one by one and collect the coefficients.
Coefficients are stored from the lowest power to the highest."""
from fractions import Fraction

from .helpers import fmt


def multiply_by_linear(poly, root):
    """Return poly * (x - root)."""
    result = [Fraction(0)] * (len(poly) + 1)
    for power, c in enumerate(poly):
        result[power + 1] += c
        result[power] -= c * root
    return result


def build_polynomial(x, table, h):
    n = len(x)
    coeffs = [Fraction(0)] * n
    basis = [Fraction(1)]                 # (x-x0)...(x-x_{k-1}), starts as 1
    factorial = 1
    for k in range(n):
        if k > 0:
            basis = multiply_by_linear(basis, x[k - 1])
            factorial *= k
        scale = table[k][0] / (factorial * h ** k)
        for power, c in enumerate(basis):
            coeffs[power] += scale * c
    while len(coeffs) > 1 and coeffs[-1] == 0:      # drop unused top powers
        coeffs.pop()
    return coeffs


def evaluate(coeffs, value):
    """Horner's method."""
    total = Fraction(0)
    for c in reversed(coeffs):
        total = total * value + c
    return total


def polynomial_to_text(coeffs):
    terms = []
    for power in range(len(coeffs) - 1, -1, -1):
        c = coeffs[power]
        if c == 0:
            continue
        magnitude = abs(c)
        if power == 0:
            body = fmt(magnitude)
        else:
            number = "" if magnitude == 1 else fmt(magnitude)
            body = number + ("x" if power == 1 else f"x^{power}")
        terms.append(("-" if c < 0 else "+", body))
    if not terms:
        return "0"
    sign, body = terms[0]
    text = ("-" if sign == "-" else "") + body
    for sign, body in terms[1:]:
        text += f" {sign} {body}"
    return text
