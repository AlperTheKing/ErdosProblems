"""Dump prefix max-cut surplus along selected shortest bad-edge paths."""

from fractions import Fraction as F

from _h import dec
from _stark1 import gmins
from _satzmu_conn import struct_for_side
from _codex_psc50_scout import adj_of, greedy_chords
from _wf_lrsbreak_0 import build_k_lane


def dump(name, n, adj, side, choose="first"):
    M, ell, T, _mu, cyc = struct_for_side(n, adj, side)
    B = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
    Bad = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    m = len(M)
    rhs = F(n) + F(n * n, 25) - m
    rows = []
    for f in M:
        for P in cyc[f]:
            avg = sum(T[v] for v in P) / ell[f]
            rows.append((rhs - avg, f, tuple(P), avg))
    rows.sort(key=lambda r: r[0])
    margin, f, P, avg = rows[0 if choose == "first" else -1]
    print("==", name, "N", n, "m", m, "f", f, "ell", ell[f], "avg", avg, "margin", margin, "P", P)
    print("Tpath", [T[v] for v in P], "sum", sum(T[v] for v in P))
    total_sigma = 0
    weighted = 0
    for i in range(len(P) - 1):
        S = set(P[: i + 1])
        db = sum(1 for u, v in B if (u in S) ^ (v in S))
        dm = sum(1 for u, v in Bad if (u in S) ^ (v in S))
        sig = db - dm
        total_sigma += sig
        weighted += sig * (i + 1) * (len(P) - i - 1)
        print(" prefix", i, "Slast", P[i], "db", db, "dm", dm, "sigma", sig)
    print("sum_sigma", total_sigma, "weighted_sigma", weighted)


def main():
    g6 = "I?rFf_{N?"
    n, E = dec(g6)
    adj, cuts = gmins(n, E)
    dump("C5[2]-census", n, adj, cuts[0])

    bad = greedy_chords(16, 5, 8)
    n, E, side, _ = build_k_lane(16, 5, bad)
    dump("k-lane-L16-k5-g8", n, adj_of(n, E), side)


if __name__ == "__main__":
    main()
