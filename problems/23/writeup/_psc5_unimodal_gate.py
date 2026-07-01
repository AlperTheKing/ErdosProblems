"""Test unimodality of the LOAD-PSC-5 prefix Phi.

I(s) = 5(L-2s)|H_s| - N*sigma_s  (integrand, piecewise-constant on H_s bands,
       but actually AFFINE in s within each band since only the 5(L-2s) factor
       depends on s continuously; |H_s|,sigma_s constant on band).

Claim to test: the sign pattern of I over the sweep is (nonneg)*(neg)* i.e. a
SINGLE sign change from + to -.  If so Phi is unimodal (up then down), so
  min_tau Phi(tau) = min(Phi(0), Phi(maxT)) = min(0, Phi(maxT)),
and PREFIX-LOAD-PSC-5 <=> endpoint LOAD-PSC-5.

We record: does the sign of I ever go - then + (a violation of single crossing)?
We evaluate I at both endpoints of each band (I is affine decreasing in s on a
band, so within a band sign goes + -> - at most once; the concern is ACROSS
bands: |H| drops and sigma drops at a jump, which can flip I back positive).
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _stark1 import gmins
from _satzmu_conn import struct_for_side
from _codex_psc50_scout import adj_of, build_two_lane, greedy_chords
from _wf_lrsbreak_0 import build_k_lane


def integrand_signs(n, edges, side):
    adj = adj_of(n, edges)
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, _mu, _cyc = st
    if not M:
        return None
    T = [F(t) for t in T]
    m = len(M)
    L = F(n) + F(n * n, 25) - m
    cut = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
    bad = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    levels = sorted(set([F(0)] + T))
    seq = []  # list of I values at sample points across sweep in order
    for a, b in zip(levels, levels[1:]):
        H = {i for i, t in enumerate(T) if t > a}
        dB = sum(1 for u, v in cut if (u in H) ^ (v in H))
        dM = sum(1 for u, v in bad if (u in H) ^ (v in H))
        sigma = dB - dM
        hs = len(H)
        # I(s) affine decreasing on [a,b]; sample at a and just below b
        Ia = 5 * (L - 2 * a) * hs - F(n) * sigma
        Ib = 5 * (L - 2 * b) * hs - F(n) * sigma
        seq.append((Ia, Ib))
    return seq


def sign_changes(seq):
    """Flatten to sign sequence (skip zeros), count +->- and -->+ transitions."""
    flat = []
    for Ia, Ib in seq:
        for x in (Ia, Ib):
            if x > 0:
                flat.append(1)
            elif x < 0:
                flat.append(-1)
    pp = mm = 0
    for i in range(1, len(flat)):
        if flat[i - 1] == 1 and flat[i] == -1:
            pp += 1
        if flat[i - 1] == -1 and flat[i] == 1:
            mm += 1  # a re-cross upward = potential non-unimodality
    return pp, mm


def check(name, n, edges, side, acc):
    seq = integrand_signs(n, edges, side)
    if seq is None:
        return
    pp, mm = sign_changes(seq)
    acc["count"] += 1
    if mm > 0:
        acc["upcross"].append((name, n, mm, pp))


def census(nmin, nmax, acc):
    for nn in range(nmin, nmax + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in out:
            n, edges = dec(g6)
            adj, cuts = gmins(n, edges)
            for side in cuts:
                check(f"cen{g6}", n, edges, side, acc)
        print(f"census N={nn} done; upcross so far {len(acc['upcross'])}", flush=True)


def main():
    acc = {"count": 0, "upcross": []}
    for L in range(8, 22, 2):
        n, edges, side, _ = build_two_lane(L)
        check(f"two-lane-L{L}", n, edges, side, acc)
    for Ll, k, gap in ((12, 4, 6), (14, 4, 8), (16, 5, 8), (18, 5, 10), (20, 6, 10)):
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _ = build_k_lane(Ll, k, bad)
        check(f"k-lane-L{Ll}-k{k}", n, edges, side, acc)
    census(7, 11, acc)
    print("=== unimodality (single + -> - sign change) test ===")
    print(f"cuts checked = {acc['count']}")
    print(f"cuts with an UPCROSS (- then +, breaks unimodality) = {len(acc['upcross'])}")
    if acc["upcross"]:
        print("examples:", acc["upcross"][:10])


if __name__ == "__main__":
    main()
