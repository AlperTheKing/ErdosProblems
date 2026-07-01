"""Exact R_local computation for the stretched nested L/(L+2) core.

The canonical deficient-cap 5/7 core has:

  short f0: s -- A(2 choices) -- shared chain -- B(2 choices) -- t
  long  f1: u -- a_fixed -- shared chain -- B(2 choices) -- t -- x -- v

For odd L>=5, the short edge has ell=L and the long edge has ell=L+2.
This script lengthens the shared chain while keeping the two branching gadgets
and computes

  R_local(z) = |V_core| * T(z) - (K2*T)(z)

with the same K2 convention as _csmspec.py:

  K2[a,b] = sum_f Pr_{Q in cyc[f]}[a,b in Q].
"""

import argparse
from fractions import Fraction as F


def build_core(L):
    if L < 5 or L % 2 == 0:
        raise ValueError("L must be odd and >=5")

    names = []

    def add(name):
        names.append(name)
        return len(names) - 1

    s = add("s")
    t = add("t")
    u = add("u")
    x = add("x")
    v = add("v")
    a0 = add("a0")
    a1 = add("a1")
    b0 = add("b0")
    b1 = add("b1")

    # The shared path from a_i to b_j has length L-3 edges.  Thus it has
    # L-4 internal vertices.
    chain = [add("c%d" % i) for i in range(L - 4)]

    def short_path(a, b):
        return tuple([s, a] + chain + [b, t])

    def long_path(b):
        return tuple([u, a1] + chain + [b, t, x, v])

    f0 = ("f0", L)
    f1 = ("f1", L + 2)
    paths = {
        f0: [short_path(a, b) for a in (a0, a1) for b in (b0, b1)],
        f1: [long_path(b) for b in (b0, b1)],
    }
    return names, paths


def compute(L):
    names, paths = build_core(L)
    n = len(names)
    T = [F(0) for _ in range(n)]
    K2 = [[F(0) for _ in range(n)] for _ in range(n)]

    for (_label, ell), rows in paths.items():
        w = F(1, len(rows))
        for row in rows:
            for z in set(row):
                T[z] += F(ell) * w
            for a in set(row):
                for b in set(row):
                    K2[a][b] += w

    K2T = [sum(K2[i][j] * T[j] for j in range(n)) for i in range(n)]
    R = [F(n) * T[i] - K2T[i] for i in range(n)]
    return names, T, K2T, R, paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-L", type=int, default=21)
    ap.add_argument("--detail", action="store_true")
    args = ap.parse_args()

    for L in range(5, args.max_L + 1, 2):
        names, T, K2T, R, paths = compute(L)
        mn = min(R)
        arg = [names[i] for i, x in enumerate(R) if x == mn]
        print("L", L, "n", len(names), "minR", mn, "arg", arg)
        if args.detail:
            for i, name in enumerate(names):
                print(" ", name, "T", T[i], "K2T", K2T[i], "R", R[i])
            print(" rows:")
            for key, rows in paths.items():
                print(" ", key, [[names[z] for z in row] for row in rows])


if __name__ == "__main__":
    main()
