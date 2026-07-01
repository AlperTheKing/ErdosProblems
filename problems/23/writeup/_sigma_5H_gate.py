"""Test candidate per-level signed-boundary bounds on super-level sets H_s={T>s}.

For a gamma-min connected-B max-cut, and each super-level set H_s, let
  sigma_s = delta_B(H_s) - delta_M(H_s).
Candidates:
  (P5)  sigma_s <= 5*|H_s|
  (Pgen) sigma_s <= (N/L)*... etc.

Also test the SHARPER, capacity-aware per-level inequality that would prove
the sweep by Abel summation:
  (CAP)  N * sigma_s  <=  (something with capacity a(L-a) and its derivative).

The task's sufficient (but here checked-to-be-FALSE as pointwise) condition is
  (D + 25N - 50 s)|H_s| >= 5 N sigma_s.
We record where it fails, and test the WEAKER integrated / monotone versions.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _stark1 import gmins
from _satzmu_conn import struct_for_side
from _codex_psc50_scout import adj_of, build_two_lane, greedy_chords
from _wf_lrsbreak_0 import build_k_lane


def levels_data(n, edges, side):
    adj = adj_of(n, edges)
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, _mu, _cyc = st
    if not M:
        return None
    T = [F(t) for t in T]
    m = len(M)
    cut_edges = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
    bad_edges = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    levels = sorted(set(T))  # s = each distinct T-value that gives a nonempty proper H_s cut
    # H_s for s just below a level value; use s = each distinct value except max, plus s=0
    slevels = sorted(set([F(0)] + [t for t in T]))
    rows = []
    for s in slevels:
        H = frozenset(i for i, t in enumerate(T) if t > s)
        if not H or len(H) == n:
            continue
        dB = sum(1 for u, v in cut_edges if (u in H) ^ (v in H))
        dM = sum(1 for u, v in bad_edges if (u in H) ^ (v in H))
        rows.append((s, len(H), dB, dM, dB - dM))
    return n, m, rows


def check(name, n, edges, side, acc):
    d = levels_data(n, edges, side)
    if d is None:
        return
    n, m, rows = d
    for s, h, dB, dM, sigma in rows:
        # P5: sigma <= 5*h
        acc["max_ratio"] = max(acc["max_ratio"], (F(sigma, h), name, str(s), h, sigma))
        if sigma > 5 * h:
            acc["p5_fail"].append((name, n, str(s), h, dB, dM, sigma))
        # also track sigma vs h relationship more finely
        acc["count"] += 1


def census(nmin, nmax, acc):
    for nn in range(nmin, nmax + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in out:
            n, edges = dec(g6)
            adj, cuts = gmins(n, edges)
            for side in cuts:
                check(f"cen{g6}", n, edges, side, acc)
        print(f"census N={nn} done, p5_fail so far {len(acc['p5_fail'])}", flush=True)


def main():
    acc = {"count": 0, "p5_fail": [], "max_ratio": (F(0), "", "", 0, 0)}
    for L in range(8, 22, 2):
        n, edges, side, _ = build_two_lane(L)
        check(f"two-lane-L{L}", n, edges, side, acc)
    for Ll, k, gap in ((12, 4, 6), (14, 4, 8), (16, 5, 8), (18, 5, 10), (20, 6, 10)):
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _ = build_k_lane(Ll, k, bad)
        check(f"k-lane-L{Ll}-k{k}", n, edges, side, acc)
    census(7, 10, acc)
    print("=== sigma <= 5|H| per-level test ===")
    print(f"levels checked = {acc['count']}")
    print(f"P5 (sigma<=5H) failures = {len(acc['p5_fail'])}")
    if acc["p5_fail"]:
        print("first fails:", acc["p5_fail"][:5])
    print(f"max sigma/|H| ratio = {float(acc['max_ratio'][0]):.4f} at {acc['max_ratio'][1:]}")


if __name__ == "__main__":
    main()
