"""Test 'reservoir' per-level inequalities that would prove the sweep by
comparing the running pressure integral to the running capacity, using
sigma_s>=0 and the load mass above level s.

Define at level s (H=H_s={T>s}):
  P(s) = N*sigma_s                       (pressure demand rate)
  above(s) = sum_{v in H}(T(v)-s)        (load mass strictly above level s)
  R(s) = 5*(L-2s)*|H_s|                   (capacity supply rate, PSC-5)

Candidate reservoir bounds (each would give the sweep if true for all s<=maxT):
  (R1) N*sigma_s <= 5*(L)*|H_s|                (drop the -2s; crude)
  (R2) N*sigma_s <= 5*|H_s|*(L - 2s) + 10*above(s)   (reservoir refund)
  (R3) cumulative: int_0^tau N sigma <= int_0^tau 5(L-2s)|H|   (= the target itself)

We MAINLY want a bound of the form  N*sigma_s <= C1*|H_s| + C2*above(s)/w?  No.
Instead test the clean two-sided:  is  N*sigma_s <= 5*(L)*|H_s| - 10*s*|H_s| + K
false anywhere?  Just report, for each level, the slack
  R(s) - P(s) = 5(L-2s)|H_s| - N sigma_s
and the running min of its integral (already known >=0). Plus test (R1),(R2).
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
    M, ell, T, _mu, _cyc = st
    if not M:
        return
    T = [F(t) for t in T]
    m = len(M)
    L = F(n) + F(n * n, 25) - m
    cut = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
    bad = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    for s in sorted(set([F(0)] + T)):
        H = frozenset(i for i, t in enumerate(T) if t > s)
        if not H:
            continue
        dB = sum(1 for u, v in cut if (u in H) ^ (v in H))
        dM = sum(1 for u, v in bad if (u in H) ^ (v in H))
        sigma = dB - dM
        hs = len(H)
        above = sum(T[i] - s for i in H)
        P = F(n) * sigma
        # (R1) N sigma <= 5 L H
        if P > 5 * L * hs:
            acc["r1"] += 1
        # (R2) N sigma <= 5(L-2s)H + 10 above
        if P > 5 * (L - 2 * s) * hs + 10 * above:
            acc["r2"].append((name, str(s), hs, sigma, str(above)))
        # (R2') N sigma <= 5(L-2s)H + 5 above
        if P > 5 * (L - 2 * s) * hs + 5 * above:
            acc["r2b"].append((name, str(s), hs, sigma, str(above)))
        acc["count"] += 1


def census(nmin, nmax, acc):
    for nn in range(nmin, nmax + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in out:
            n, edges = dec(g6)
            adj, cuts = gmins(n, edges)
            for side in cuts:
                check(f"cen{g6}", n, edges, side, acc)
        print(f"N={nn} r1={acc['r1']} r2={len(acc['r2'])} r2b={len(acc['r2b'])}", flush=True)


def main():
    acc = {"count": 0, "r1": 0, "r2": [], "r2b": []}
    for L in range(8, 22, 2):
        n, edges, side, _ = build_two_lane(L)
        check(f"two-lane-L{L}", n, edges, side, acc)
    for Ll, k, gap in ((12, 4, 6), (14, 4, 8), (16, 5, 8), (18, 5, 10), (20, 6, 10)):
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _ = build_k_lane(Ll, k, bad)
        check(f"k-lane-L{Ll}-k{k}", n, edges, side, acc)
    census(7, 11, acc)
    print("=== reservoir per-level tests ===")
    print(f"levels = {acc['count']}")
    print(f"(R1) N sigma <= 5 L H  failures = {acc['r1']}")
    print(f"(R2) N sigma <= 5(L-2s)H + 10 above  failures = {len(acc['r2'])}")
    print(f"(R2b) N sigma <= 5(L-2s)H + 5 above  failures = {len(acc['r2b'])}")
    if acc["r2"]:
        print("R2 ex:", acc["r2"][:5])
    if acc["r2b"]:
        print("R2b ex:", acc["r2b"][:5])


if __name__ == "__main__":
    main()
