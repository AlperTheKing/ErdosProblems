"""Dump load-threshold coarea data for LRS proof work."""

from fractions import Fraction as F

from _codex_psc50_scout import adj_of, build_two_lane, greedy_chords
from _wf_lrsbreak_0 import build_k_lane
from _satzmu_conn import struct_for_side


def asF(x):
    if isinstance(x, F):
        return x
    return F(x)


def dump_case(name, n, edges, side):
    adj = adj_of(n, edges)
    st = struct_for_side(n, adj, side)
    M, ell, T, _mu, _cyc = st
    T = [asF(v) for v in T]
    gamma = sum(F(v) * F(v) for v in ell.values())
    m = len(M)
    deficit = F(n * n, 25) - m
    lhs = sum(t * (t - n) for t in T)
    rhs = gamma * deficit
    B = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
    Bad = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    levels = sorted(set([F(0)] + T))
    print("==", name, "N", n, "m", m, "Gamma", gamma, "def", deficit, "LHS", lhs, "RHS", rhs, "margin", rhs - lhs)
    total = F(0)
    for a, b in zip(levels, levels[1:]):
        if a == b:
            continue
        H = {i for i, t in enumerate(T) if t > a}
        if not H:
            continue
        db = sum(1 for u, v in B if (u in H) ^ (v in H))
        dm = sum(1 for u, v in Bad if (u in H) ^ (v in H))
        sigma = db - dm
        contrib = (b - a) * (2 * a + (b - a) - n) * len(H)
        # Integral of (2s-N)|H| from a to b.
        total += contrib
        if contrib or sigma or a >= n:
            print(
                " interval",
                a,
                b,
                "|H|",
                len(H),
                "sigma",
                sigma,
                "db",
                db,
                "dm",
                dm,
                "contrib",
                contrib,
                "H",
                sorted(H)[:20],
            )
    print(" layer_total", total)


def main():
    for L in (12, 20):
        n, edges, side, _ = build_two_lane(L)
        dump_case(f"two-lane-{L}", n, edges, side)
    for L, k, gap in ((12, 4, 6), (16, 5, 8)):
        bad = greedy_chords(L, k, gap)
        n, edges, side, _ = build_k_lane(L, k, bad)
        dump_case(f"k-lane-L{L}-k{k}-g{gap}", n, edges, side)


if __name__ == "__main__":
    main()
