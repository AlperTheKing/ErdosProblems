"""Symbolic active-5 seed quotient margin for a fixed side and row.

For a weighted quotient seed, this prints the semi-factored expression for

    2*(N^2 - 25*m) - 75*(I(row)-N),

where I(row) is the row-overlap sum over all weighted bad quotient edges.  The
nonnegativity of this numerator is exactly the active-all-five stability
`I(row)-N <= (2/3)eta`.
"""

from __future__ import annotations

import argparse
import contextlib
import io

import sympy as sp

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_c5lift_weighted_quotient_gate import (
        EQ,
        SIB,
        b_edges,
        edges_of,
        m_edges,
        shortest_paths,
    )


def parse_row(s: str) -> tuple[int, ...]:
    return tuple(int(x) for x in s.replace(",", " ").split())


def path_weight(path, w):
    out = sp.Integer(1)
    for v in path[1:-1]:
        out *= w[v]
    return out


def symbolic_margin(g6: str, side_s: str, row: tuple[int, ...]):
    n, E = edges_of(g6)
    side = tuple(int(c) for c in side_s)
    B = b_edges(E, side)
    M = sorted(m_edges(E, side))
    w = sp.symbols(f"w0:{n}", positive=True)
    row_set = set(row)

    terms = []
    I = sp.Integer(0)
    for a, b in M:
        paths = shortest_paths(n, B, a, b)
        if not paths:
            raise RuntimeError((a, b, "no shortest paths"))
        Z = sp.Integer(0)
        inner = sp.Integer(0)
        for p in paths:
            wp = path_weight(p, w)
            Z += wp
            for v in p[1:-1]:
                if v in row_set:
                    inner += wp / w[v]
        endpoint = sp.Integer(0)
        if a in row_set:
            endpoint += w[b]
        if b in row_set:
            endpoint += w[a]
        term = endpoint + w[a] * w[b] * inner / Z
        terms.append(((a, b), sp.factor(Z), sp.factor(inner), sp.factor(term)))
        I += term

    N = sum(w)
    m = sum(w[a] * w[b] for a, b in M)
    margin = sp.factor(2 * (N * N - 25 * m) - 75 * (I - N))
    numer, denom = sp.together(margin).as_numer_denom()
    numer = sp.factor(numer)
    denom = sp.factor(denom)
    poly = sp.Poly(numer, *w)
    return w, n, M, terms, sp.factor(I), m, margin, numer, denom, poly


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", choices=["eq", "sib"], required=True)
    ap.add_argument("--side", required=True)
    ap.add_argument("--row", required=True, help="comma or space separated row vertices")
    ap.add_argument("--show-terms", action="store_true")
    ap.add_argument("--stats-only", action="store_true")
    ap.add_argument("--shift-stats", action="store_true")
    args = ap.parse_args()

    g6 = EQ if args.graph == "eq" else SIB
    row = parse_row(args.row)
    w, n, M, terms, I, m, margin, numer, denom, poly = symbolic_margin(g6, args.side, row)

    print("graph", args.graph)
    print("side", args.side)
    print("row", row)
    print("bad_edges", M)
    if args.show_terms:
        for edge, Z, inner, term in terms:
            print(f"BAD {edge}")
            print("  Z =", Z)
            print("  inner =", inner)
            print("  term =", term)
    if not args.stats_only:
        print("I =", sp.factor(I))
        print("m =", m)
    print("margin = 2*(N^2-25m)-75*(I-N)")
    print("denom =", denom)
    print("numer_total_degree =", poly.total_degree())
    print("numer_terms =", len(poly.terms()))
    coeffs = [c for _monom, c in poly.terms()]
    print("raw_negative_coeffs =", sum(1 for c in coeffs if c < 0))
    print("raw_min_coeff =", min(coeffs))
    if args.shift_stats:
        xs = sp.symbols(f"x0:{n}", nonnegative=True)
        shifted = sp.expand(numer.subs({w[i]: xs[i] + 1 for i in range(n)}))
        spoly = sp.Poly(shifted, *xs)
        scoeffs = [c for _monom, c in spoly.terms()]
        print("shift_terms =", len(spoly.terms()))
        print("shift_negative_coeffs =", sum(1 for c in scoeffs if c < 0))
        print("shift_min_coeff =", min(scoeffs))
    if not args.stats_only:
        print("numer_factor =", numer)


if __name__ == "__main__":
    main()
