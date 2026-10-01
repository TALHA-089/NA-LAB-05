"""Forward difference table: build it and print it."""
from .helpers import fmt


def build_difference_table(f):
    """table[k][i] = k-th forward difference starting at row i.
    table[0] is f(x) itself, table[1] is Df, table[2] is D2f, ..."""
    table = [list(f)]
    while len(table[-1]) > 1:
        previous = table[-1]
        table.append([previous[i + 1] - previous[i] for i in range(len(previous) - 1)])
    return table


def column_name(k):
    return "f(x)" if k == 0 else ("Df" if k == 1 else f"D{k}f")


def visible_columns(table):
    """How many columns to print: stop after the last column that has a
    non-zero value (always show at least f(x) and Df)."""
    last = 0
    for k, column in enumerate(table):
        if any(v != 0 for v in column):
            last = k
    return max(last + 1, 2)


def format_table(x, table):
    """Return the table as a list of text lines."""
    cols = visible_columns(table)
    header = ["x"] + [column_name(k) for k in range(cols)]
    rows = []
    for i in range(len(x)):
        row = [fmt(x[i])]
        row += [fmt(table[k][i]) for k in range(cols) if i < len(table[k])]
        rows.append(row)
    width = max(len(cell) for line in [header] + rows for cell in line) + 2
    return ["  " + "".join(cell.rjust(width) for cell in line) for line in [header] + rows]
