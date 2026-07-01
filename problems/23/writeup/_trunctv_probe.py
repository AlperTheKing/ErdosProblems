"""Probe the two proven cumulative TV caps and their per-level (coarea) meaning.

For u = min(T, tau):  S = sum_v u_v.
  TRUNC-TV-LOW : Xi(u) = TV_B(u)-TV_M(u) <= 5 * S.
  TRUNC-BRES   : Xi(u) <= 5*(N^2 - S).

By coarea, Xi(u) = int_0^tau sigma_s ds,  S = int_0^tau |H_s| ds  (H_s={T>s}).
So TRUNC-TV-LOW in per-level coarea form is:
  int_0^tau sigma_s ds <= 5 * int_0^tau |H_s| ds.
This is IMPLIED by (but strictly weaker than) the termwise sigma_s <= 5|H_s|, which is FALSE.
So the prefix cap int sigma <= 5 int |H| holds even though termwise fails => genuine Abel/amortization.

GOAL: understand the amortization. Define running slack
  R(tau) = 5*S(tau) - Xi(tau) = int_0^tau (5|H_s| - sigma_s) ds.
Print, per band, the *increment* (5|H_s|-sigma_s)*width and cumulative R.
Where does the increment go negative (termwise), and does R stay >=0?

Also test the SHARPER per-vertex handle that could drive a proof:
For each s, decompose sigma_s = delta_B(H_s) - delta_M(H_s). At a MAX cut, for the
super-level set boundary, we expect delta_B(H_s) <= 2*(edges within cut incident to H_s)...
We instead measure, per level:
  delta_B(H_s), delta_M(H_s), and the quantity  5|H_s| - sigma_s  split as
  5|H_s| - delta_B(H_s) + delta_M(H_s).
And we test candidate  delta_B(H_s) <= 5|H_s| + delta_M(H_s) + (bank)  amortized.
"""
from fractions import Fraction as F
from _satzmu_conn import struct_for_side
from _h import Bconn
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords


def adj_of(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    return adj


def boundary(n, adj, side, Hset):
    dB = 0; dM = 0
    for u in Hset:
        for v in adj[u]:
            if v in Hset:
                continue
            if side[u] != side[v]:
                dB += 1
            else:
                dM += 1
    return dB, dM


def probe(name, n, adj, side, verbose=True):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    if not M:
        return None
    N = F(n)
    levs = sorted(set([F(0)] + [t for t in T]))
    R = F(0)  # running slack for TRUNC-TV-LOW: 5 int|H| - int sigma
    minR = F(0)
    if verbose:
        print(f"\n=== {name} N={n} m={len(M)} ===")
        print("  s | h | dB dM sig | 5h-sig (termwise) | R=cum(5h-sig)*w")
    for k in range(len(levs) - 1):
        s = levs[k]; w = levs[k + 1] - levs[k]
        Hset = set(v for v in range(n) if T[v] > s)
        if not Hset:
            continue
        h = len(Hset)
        dB, dM = boundary(n, adj, side, Hset)
        sig = dB - dM
        inc = 5 * h - sig
        R += inc * w
        if R < minR:
            minR = R
        if verbose:
            flag = " <-- 5h-sig<0" if inc < 0 else ""
            print(f"  {str(s):>5} | {h:3} | {dB:3} {dM:3} {str(sig):>4} | {str(inc):>6} | {str(R):>8}{flag}")
    if verbose:
        print(f"  min running R = {minR}  (TRUNC-TV-LOW prefix slack; must be >=0)")
    return minR


def main():
    for L in (8, 12):
        n, edges, side, _ = build_two_lane(L)
        probe(f"two-lane-L{L}", n, adj_of(n, edges), side)
    for Ll, k, gap in [(12, 4, 6), (14, 4, 8)]:
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _bad = build_k_lane(Ll, k, bad)
        probe(f"klane-L{Ll}k{k}", n, adj_of(n, edges), side)


if __name__ == "__main__":
    main()
