"""List quotient max-cut flip constraints for a fixed seed side.

For the selected side, every subset S gives the inequality

    delta_B(S) - delta_M(S) >= 0

as a quadratic form in quotient weights.  This script prints canonical
constraints sorted by slack at a chosen integer weight vector.
"""

from __future__ import annotations

import argparse

from _codex_c5lift_weighted_quotient_gate import EQ, SIB, edges_of


def parse_weights(s: str, n: int) -> tuple[int, ...]:
    if s == "ones":
        return (1,) * n
    vals = tuple(int(x) for x in s.replace(",", " ").split())
    if len(vals) != n:
        raise ValueError(f"expected {n} weights, got {len(vals)}")
    return vals


def constraint(g6: str, side: tuple[int, ...], mask: int):
    _n, E = edges_of(g6)
    out = {}
    has_bad = False
    for a, b in sorted(E):
        if ((mask >> a) & 1) ^ ((mask >> b) & 1):
            sign = 1 if side[a] != side[b] else -1
            out[(a, b)] = sign
            has_bad |= sign < 0
    return out if has_bad else None


def value(c, weights):
    return sum(sign * weights[a] * weights[b] for (a, b), sign in c.items())


def fmt(c):
    plus = []
    minus = []
    for (a, b), sign in sorted(c.items()):
        term = f"w{a}w{b}"
        if sign > 0:
            plus.append(term)
        else:
            minus.append(term)
    return f"{' + '.join(plus) if plus else '0'} >= {' + '.join(minus) if minus else '0'}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", choices=["eq", "sib"], required=True)
    ap.add_argument("--side", required=True)
    ap.add_argument("--weights", default="ones")
    ap.add_argument("--limit", type=int, default=80)
    args = ap.parse_args()

    g6 = EQ if args.graph == "eq" else SIB
    n, _E = edges_of(g6)
    side = tuple(int(c) for c in args.side)
    weights = parse_weights(args.weights, n)

    rows = []
    for mask in range(1, (1 << n) - 1):
        # Quotient by complement.
        if not (mask & 1):
            continue
        c = constraint(g6, side, mask)
        if c is None:
            continue
        rows.append((value(c, weights), mask, c))
    rows.sort(key=lambda item: (item[0], bin(item[1]).count("1"), item[1]))

    print("graph", args.graph)
    print("side", args.side)
    print("weights", weights)
    print("constraints", len(rows))
    print("tight_count", sum(1 for slack, _mask, _c in rows if slack == 0))
    for slack, mask, c in rows[: args.limit]:
        subset = tuple(i for i in range(n) if (mask >> i) & 1)
        print(f"slack={slack:4d} S={subset}: {fmt(c)}")


if __name__ == "__main__":
    main()
