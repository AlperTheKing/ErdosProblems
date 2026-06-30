"""Small diagnostics for the CYCLE-HARDY PSD target.

This is not a proof gate.  It prints row sums, T-overloads, and float
eigenvectors for named small examples so we can see what a proof of
H = diag(N-T)+Lstar >= 0 has to explain.
"""
from fractions import Fraction as F

import numpy as np

from _h import dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _hardy_gate import build_H, BETA, float_min_eig


def adj_of(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def frac_float_matrix(mat):
    return np.array([[float(x) for x in row] for row in mat], dtype=float)


def report(g6, side_bits=None, max_cuts=3):
    n, edges = dec(g6)
    adj = adj_of(n, edges)
    if side_bits is None:
        _, cuts = gmins(n, edges)
        cuts = cuts[:max_cuts]
    else:
        cuts = [[int(c) for c in side_bits]]

    for idx, side in enumerate(cuts):
        st = struct_for_side(n, adj, side)
        if st is None:
            print(g6, idx, "struct_for_side=None")
            continue
        M, ell, T, cyc = st[0], st[1], st[2], st[4]
        H = build_H(n, M, ell, T, cyc, BETA)
        Hf = frac_float_matrix(H)
        vals, vecs = np.linalg.eigh(Hf)
        row_sums = [sum(row) for row in H]
        print("=" * 80)
        print("g6", g6, "cut", idx, "side", "".join(map(str, side)))
        print("n", n, "|M|", len(M), "Gamma", sum(ell[f] ** 2 for f in M))
        print("M", M, "ell", {f: ell[f] for f in M})
        print("T", [str(x) for x in T])
        print("N-T", [str(F(n) - x) for x in T])
        print("row_sums H*1", [str(x) for x in row_sums])
        print("float min eig true beta", float_min_eig(n, M, ell, T, cyc))
        print("float eigvals beta'", [round(float(v), 10) for v in vals[:5]])
        for j in range(min(2, len(vals))):
            v = vecs[:, j]
            print("eigvec", j, "eig", vals[j], "vec", [round(float(x), 4) for x in v])


def main():
    report("FCp`_")       # C5
    report("H?AFBo]", "111110000")
    report("I?BD@g]Qo", "0001111000")


if __name__ == "__main__":
    main()
