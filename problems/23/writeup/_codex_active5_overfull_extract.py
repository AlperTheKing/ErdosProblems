"""Extract active-all-five overfull rows in the two C5 quotient seeds.

This is a proof-diagnostic script, not a gate.  It lists the qmax all-ones
rows satisfying active=5 and row_sum>N, the only rows that survive the OHDX
localization in the seed quotient picture.
"""

from __future__ import annotations

import contextlib
import io
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_c5lift_active_size_quotient_fast import (
        EQ,
        SIB,
        loads_for,
        side_data,
    )
    from _codex_c5lift_weighted_quotient_gate import (
        qcut_value,
        qmaxcut_value,
        sides_to_scan,
    )


def fmt(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(x)


def run(name, g6):
    n = 10
    weights = [1] * n
    best = qmaxcut_value(g6, weights)
    rows_out = []

    for side in sides_to_scan(g6):
        if qcut_value(g6, side, weights) != best:
            continue
        sn, _E, M, paths, rows = side_data(g6, side)
        N = sum(weights)
        m = sum(weights[a] * weights[b] for a, b in M)
        eta = F(N * N, 25) - m
        tau = F(5 * m, N)
        loads = loads_for(sn, M, paths, weights)
        for f, row in rows:
            if len(row) != 5:
                continue
            s = [loads[v] for v in row]
            active = [i for i, x in enumerate(s) if x > tau]
            row_sum = sum(s, F(0))
            if len(active) == 5 and row_sum > N:
                rows_out.append((side, f, tuple(row), row_sum, row_sum - N, tuple(s)))

    print(f"## {name}")
    print(f"N={n} qmax={best} active5_over_rows={len(rows_out)}")
    for side, f, row, row_sum, debt, s in rows_out:
        print(
            "side={side} f={f} Q={row} row_sum={row_sum} debt={debt} s={s}".format(
                side=side,
                f=f,
                row=row,
                row_sum=fmt(row_sum),
                debt=fmt(debt),
                s="[" + ",".join(fmt(x) for x in s) + "]",
            )
        )


def main():
    run("eq", EQ)
    run("sib", SIB)


if __name__ == "__main__":
    main()
