from fractions import Fraction

from interpolation.helpers import fmt, read_int, read_numbers, step_size
from interpolation.newton import interpolate
from interpolation.polynomial import build_polynomial, evaluate, polynomial_to_text
from interpolation.table import build_difference_table, format_table


def answer_query(x, f, table, h, target):
    """Return the output lines for one query value."""
    if target in x:                                   # already in the table
        value = f[x.index(target)]
        return [f"  x = {fmt(target)} is a tabulated point -> f({fmt(target)}) = {fmt(value)}"]

    r = interpolate(x, table, h, target)
    lines = [
        f"  target lies {r.where} -> method : NEWTON {r.method}",
        f"  origin x0 = {fmt(r.x0)}, h = {fmt(h)}, p = {fmt(r.p)}",
    ]
    if r.extrapolation:
        lines.append(
            "  note : outside the table, so this is EXTRAPOLATION (less reliable)")
    lines.append(f"  f({fmt(target)}) = {fmt(r.value)}")
    return lines


def main():
    n = read_int("Enter number of data points : ", 2, 50)

    while True:
        x = read_numbers("x values : ", n)
        h = step_size(x)
        if h is not None:
            break
        print("  The x values must increase with a constant step h. Enter them again.")
    f = read_numbers("f(x) values : ", n)

    table = build_difference_table(f)
    print("\nDifference table (forward differences)")
    print("\n".join(format_table(x, table)))

    while True:
        raw = input("\nQuery x (blank to stop) : ").strip()
        if raw == "":
            break
        try:
            target = Fraction(raw)
        except (ValueError, ZeroDivisionError):
            print("  Invalid query - type a number, or press Enter to stop.")
            continue
        print("\n".join(answer_query(x, f, table, h, target)))

    coeffs = build_polynomial(x, table, h)
    print(f"\nMaximum degree under the given data : {len(coeffs) - 1}")
    print(f"  P(x) = {polynomial_to_text(coeffs)}")
    print(f"  (with {n} points the highest possible degree would be {n - 1})")
    ok = all(evaluate(coeffs, x[i]) == f[i] for i in range(n))
    print(
        f"  check : P(x) {'reproduces all ' + str(n) + ' data points' if ok else 'MISMATCH'}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nStopped.")
