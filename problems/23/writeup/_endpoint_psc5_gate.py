"""ENDPOINT LOAD-PSC-5 (the theorem-sufficient statement; NO sweep needed):

  5 * sum_v T(v)(L-T(v))  >=  N*(TV_B(T)-TV_M(T)).

Equivalently  5(L*Gamma - sum T^2) >= N*(TV_B(T)-TV_M(T)).

Test exactly; report min margin and the ratio Pr/Cap at the endpoint only.
Also test candidate PROVABLE decompositions:
  * per-B-edge charge: for uv in B, |T(u)-T(v)| <= (5/N)*(cap share)?  We test
    the aggregate only here.
  * Handshake: sum_{e in B at v} mu(e) relation to T(v).
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _stark1 import gmins
from _satzmu_conn import struct_for_side
from _codex_psc50_scout import adj_of, build_two_lane, greedy_chords
from _wf_lrsbreak_0 import build_k_lane


def check(name, n, edges, side, acc):
    adj = adj_of(n, edges)
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, _cyc = st
    if not M:
        return
    T = [F(t) for t in T]
    m = len(M)
    L = F(n) + F(n * n, 25) - m
    cut = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
    bad = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    cap = sum(t * (L - t) for t in T)
    tvB = sum(abs(T[u] - T[v]) for u, v in cut)
    tvM = sum(abs(T[u] - T[v]) for u, v in bad)
    pr = F(n) * (tvB - tvM)
    margin = 5 * cap - pr
    acc["count"] += 1
    if margin < acc["min"][0]:
        acc["min"] = (margin, name, n, str(5 * cap), str(pr))
    if margin < 0:
        acc["viol"].append((name, n, str(margin)))
    if cap > 0:
        r = pr / (5 * cap)
        if r > acc["maxr"][0]:
            acc["maxr"] = (r, name)


def census(nmin, nmax, acc):
    for nn in range(nmin, nmax + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in out:
            n, edges = dec(g6)
            adj, cuts = gmins(n, edges)
            for side in cuts:
                check(f"cen{g6}", n, edges, side, acc)
        print(f"N={nn} viol={len(acc['viol'])}", flush=True)


def main():
    acc = {"count": 0, "viol": [], "min": (F(10) ** 30, "", 0, "", ""), "maxr": (F(0), "")}
    for L in range(8, 22, 2):
        n, edges, side, _ = build_two_lane(L)
        check(f"two-lane-L{L}", n, edges, side, acc)
    for Ll, k, gap in ((12, 4, 6), (14, 4, 8), (16, 5, 8), (18, 5, 10), (20, 6, 10)):
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _ = build_k_lane(Ll, k, bad)
        check(f"k-lane-L{Ll}-k{k}", n, edges, side, acc)
    census(7, 11, acc)
    print("=== ENDPOINT LOAD-PSC-5 ===")
    print(f"cuts={acc['count']} viol={len(acc['viol'])}")
    print(f"min margin = {acc['min']}")
    print(f"max endpoint ratio Pr/(5Cap) = {float(acc['maxr'][0]):.6f} at {acc['maxr'][1]}")


if __name__ == "__main__":
    main()
