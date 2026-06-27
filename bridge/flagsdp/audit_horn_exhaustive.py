#!/usr/bin/env python3
"""ADVERSARIAL audit of the rooted Horn (C5) cut on the ALL-PAIRS second-moment matrix P_R.
H_R(A0..A4) = sum_{i,j} P(A_i,A_j) - 4 sum_i P(A_i,A_{i+1 mod 5}) >= 0  must hold for ALL real
triangle-free graphons.  This script REPLACES the degree-heuristic min in horn_min_W with an
EXHAUSTIVE min over ALL ordered 5-tuples (i0..i4) of profiles per root (no top-MAXP truncation),
so we cannot miss a negative tuple hidden among low-degree profiles.

Note H_R is invariant under cyclic rotation and reflection of (A0..A4); the quadratic-form value
only depends on the cyclic sequence. We enumerate ordered 5-tuples but cut cost via the
necklace structure: for a fixed 5-SET we evaluate every distinct cyclic order (the (5-1)!/2 = 12
necklaces) -- same set as horn_min_W's permutation loop, but over ALL 5-subsets, not just top-14.
"""
import sys, time, itertools
import numpy as np
from horn_soundness import buildW

def horn_min_exhaustive(W):
    """Exhaustive min of H_R over ALL roots and ALL 5-subsets (every necklace). Returns (minH, minNorm, arg)."""
    worstH = 0.0; worstN = 0.0; worstArg = None
    for key, ed in W.items():
        profs = sorted(set(a for (a, b) in ed) | set(b for (a, b) in ed),
                       key=lambda s: (len(s), sorted(s)))
        idx = {p: i for i, p in enumerate(profs)}; m = len(profs)
        if m < 5:
            continue
        P = np.zeros((m, m))
        for (A, B), w in ed.items():
            P[idx[A], idx[B]] += w
        P = 0.5 * (P + P.T)
        pr = float(P.sum())
        for sub in itertools.combinations(range(m), 5):
            s = list(sub)
            tot = P[np.ix_(s, s)].sum()
            # all distinct cyclic orders of the 5-set (fix s[0], permute rest)
            for perm in itertools.permutations(s[1:]):
                cyc = [s[0]] + list(perm)
                cs = sum(P[cyc[i], cyc[(i + 1) % 5]] for i in range(5))
                H = tot - 4 * cs
                if H < worstH:
                    worstH = H; worstN = H / pr if pr > 1e-13 else 0.0
                    worstArg = (key, tuple(cyc))
    return worstH, worstN, worstArg

def cyc_graph(n):
    A = [0] * n
    for i in range(n):
        A[i] |= 1 << ((i + 1) % n); A[(i + 1) % n] |= 1 << i
    return A

if __name__ == "__main__":
    # quick self-test on small cycles where m per root is modest -> exhaustive is feasible
    for nm, n in [("C5", 5), ("C7", 7), ("C9", 9)]:
        t0 = time.time()
        W = buildW(n, cyc_graph(n), ALLPAIRS=True)
        h, hn, arg = horn_min_exhaustive(W)
        print("%-5s EXHAUSTIVE all-pairs: min H_R=%+.6e (norm %+.6e)  %s  [%.1fs] arg=%s"
              % (nm, h, hn, "<<<NEG" if h < -1e-9 else "OK", time.time() - t0, arg), flush=True)
