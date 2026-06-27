#!/usr/bin/env python3
"""FAST vectorized EXHAUSTIVE Horn (C5) audit on the ALL-PAIRS matrix P_R.
For each root, enumerate ALL 5-subsets of profiles (NO degree truncation), and for each subset
evaluate H = totalsum - 4*cyclesum minimized over all distinct 5-necklaces.  Vectorized with numpy
over batches of subsets so roots with up to ~90 profiles are tractable.

H_R = sum_{i,j in S} P[i,j] - 4 * sum_k P[c_k, c_{k+1}]  for cyclic order c.
Per fixed 5-set, totalsum is constant; minimizing H == maximizing cyclesum over the 12 necklaces.
We compute, for every subset, max over 12 necklace patterns of the cyclesum, then H_min(subset).
Global min over all subsets and roots is the audit number; must be >= -1e-9.
"""
import sys, time, itertools
import numpy as np
from horn_soundness import buildW

# The 12 distinct directed 5-cycles on positions (0,1,2,3,4) up to rotation+reflection.
# Fix position 0; the other 4 positions get the (4-1)!/... we just take perms of (1,2,3,4)
# and dedupe by cyclic rotation + reflection of the resulting necklace.  Enumerate edge-pair
# index lists: for each necklace, the 5 directed edges (a,b) as index pairs into the 5-subset.
def _necklaces():
    seen = set(); pats = []
    for perm in itertools.permutations([1, 2, 3, 4]):
        cyc = (0,) + perm
        edges = frozenset(frozenset((cyc[i], cyc[(i + 1) % 5])) for i in range(5))
        if edges in seen:
            continue
        seen.add(edges)
        pairs = [(cyc[i], cyc[(i + 1) % 5]) for i in range(5)]
        pats.append(pairs)
    return pats  # 12 necklaces, each a list of 5 (i,j) position-pairs

NECK = _necklaces()  # len 12

def root_min(P, batch=20000):
    """Min H over all 5-subsets of the m x m symmetric P. Returns (minH, argsubset_or_None)."""
    m = P.shape[0]
    if m < 5:
        return 0.0, None
    it = itertools.combinations(range(m), 5)              # LAZY -- do not materialize all subsets
    worst = 0.0; worstArg = None
    # precompute necklace edge position arrays
    npat = len(NECK)
    ei = np.array([[p[0] for p in pat] for pat in NECK])  # (12,5)
    ej = np.array([[p[1] for p in pat] for pat in NECK])  # (12,5)
    while True:
        chunk = list(itertools.islice(it, batch))
        if not chunk:
            break
        blk = np.array(chunk)                               # (B,5)
        B = blk.shape[0]
        # gather 5x5 submatrices: P[blk[:,a], blk[:,b]]
        ia = blk[:, :, None]                                # (B,5,1)
        ib = blk[:, None, :]                                # (B,1,5)
        sub5 = P[ia, ib]                                    # (B,5,5)
        totalsum = sub5.sum(axis=(1, 2))                    # (B,)
        # cyclesum for each necklace: sum over k of sub5[:, ei[t,k], ej[t,k]]
        # build index arrays for advanced indexing
        cyclesums = np.empty((B, npat))
        for t in range(npat):
            cyclesums[:, t] = sub5[:, ei[t], ej[t]].sum(axis=1)
        maxcyc = cyclesums.max(axis=1)                      # (B,)
        Hmin_blk = totalsum - 4.0 * maxcyc                  # (B,)
        j = int(np.argmin(Hmin_blk))
        if Hmin_blk[j] < worst:
            worst = float(Hmin_blk[j]); worstArg = tuple(int(x) for x in blk[j])
    return worst, worstArg

def audit(name, n, A, ALLPAIRS=True, verbose=True):
    t0 = time.time()
    W = buildW(n, A, ALLPAIRS=ALLPAIRS)
    gw = 0.0; garg = None
    for key, ed in W.items():
        profs = sorted(set(a for (a, b) in ed) | set(b for (a, b) in ed),
                       key=lambda s: (len(s), sorted(s)))
        idx = {p: i for i, p in enumerate(profs)}; mm = len(profs)
        if mm < 5:
            continue
        P = np.zeros((mm, mm))
        for (a, b), w in ed.items():
            P[idx[a], idx[b]] += w
        P = 0.5 * (P + P.T)
        h, arg = root_min(P)
        if h < gw:
            gw = h; garg = (key, arg)
    if verbose:
        print("%-10s %s: min H_R=%+.6e  %s  [%.1fs]"
              % (name, "ALLPAIRS" if ALLPAIRS else "EDGEONLY", gw,
                 "<<< NEGATIVE!" if gw < -1e-9 else "OK", time.time() - t0), flush=True)
    return gw, garg

def cyc_graph(n):
    A = [0] * n
    for i in range(n):
        A[i] |= 1 << ((i + 1) % n); A[(i + 1) % n] |= 1 << i
    return A

if __name__ == "__main__":
    targets = sys.argv[1:] or ["C5", "C7", "C9", "C11", "C13", "C15"]
    nmap = {"C5": 5, "C7": 7, "C9": 9, "C11": 11, "C13": 13, "C15": 15}
    g = 0.0
    for nm in targets:
        n = nmap[nm]
        h, arg = audit(nm, n, cyc_graph(n))
        if h < g:
            g = h
        print("    arg=%s" % (arg,), flush=True)
    # cross-check edge-only C5 must be negative
    he, _ = audit("C5", 5, cyc_graph(5), ALLPAIRS=False)
    print("\nGLOBAL min H_R (all-pairs, exhaustive) over odd cycles = %+.6e -> %s"
          % (g, "SOUND" if g >= -1e-9 else "UNSOUND"), flush=True)
    print("DONE", flush=True)
