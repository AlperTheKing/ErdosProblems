"""Abel/sweep structure probe for LOAD-PSC-5.

Key question: the prefix integral Phi5(tau) = int_0^tau I5(s) ds >= 0.
I5(s) = 5(L-2s)|H_s| - N*sigma_s.

Abel-summation reformulation. Write Phi5(tau) = int_0^tau [5(L-2s)|H_s| - N sigma_s] ds.
Since H_s is nested decreasing, and both |H_s|, sigma_s are step functions in s, we test
several *pointwise-after-reweighting* candidate lemmas and an integrated bound.

CANDIDATE PER-LEVEL LEMMA (the target for the writeup): for every super-level s,
   N * sigma_s  <=  5 * (2L - ... ) ???
We instead EMPIRICALLY fit: on each cut, find the smallest constant kappa with
   sigma_s <= kappa * |H_s|   for all s   (per-vertex signed-boundary bound)
and check whether kappa <= (something like 2, or 5(L)/N-ish).

Also test the ENERGY form that is the real target:
   int_0^tau N*sigma_s ds  <=  int_0^tau 5(L-2s)|H_s| ds   for all tau.
Equivalently  N*(TVB(a)-TVM(a)) <= 5*sum_v a(L-a).   [that's LOAD-PSC-5 itself]

The productive per-level statement to try to PROVE:
   N * sigma_s  <=  5 * |H_s| * (L - 2s)  +  [a nonneg "bank" carried from lower levels].
We measure the *deficit* def(s) = N*sigma_s - 5(L-2s)|H_s| = -I5(s) and the *surplus*
carried, and print, per level:
   sigma_s, |H_s|, sigma_s/|H_s|,  (L-2s),  5(L-2s)|H_s|/N,  and cumulative bank.
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


def probe(name, n, adj, side):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, cyc = st
    if not M:
        return
    m = len(M); N = F(n)
    D = F(n * n) - 25 * m
    L = N + D / 25
    levs = sorted(set([F(0)] + [t for t in T]))
    print(f"\n=== {name} N={n} m={m} L={L} (N+eta), theta=(N+eta)/2={(N+L-N)/2 + N/2} ===")
    print("  s | h=|H_s| | sigma | sig/h | (L-2s) | 5(L-2s)h/N | deficit=Nsig-5(L-2s)h | bank")
    bank = F(0)  # cumulative Phi5 (should stay >=0)
    for k in range(len(levs) - 1):
        s = levs[k]; width = levs[k + 1] - levs[k]
        Hset = set(v for v in range(n) if T[v] > s)
        if not Hset:
            continue
        h = len(Hset)
        dB, dM = boundary(n, adj, side, Hset)
        sigma = dB - dM
        cap = 5 * (L - 2 * s) * h
        deficit = N * sigma - cap  # = -I5
        bank += (-deficit) * width  # Phi5 accumulation
        sigh = F(sigma, h) if h else F(0)
        print(f"  {str(s):>5} | {h:5} | {str(sigma):>4} | {str(sigh):>6} | {str(L-2*s):>8} | "
              f"{str(cap/N):>10} | {str(deficit):>10} | {str(bank):>8}")
    print(f"  final bank (Phi5 top) = {bank}   min-should-be >=0")


def main():
    for L in (8, 12):
        n, edges, side, _ = build_two_lane(L)
        probe(f"two-lane-L{L}", n, adj_of(n, edges), side)
    for Ll, k, gap in [(12, 4, 6)]:
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _bad = build_k_lane(Ll, k, bad)
        probe(f"klane-L{Ll}k{k}", n, adj_of(n, edges), side)


if __name__ == "__main__":
    main()
