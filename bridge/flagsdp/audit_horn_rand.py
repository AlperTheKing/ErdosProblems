#!/usr/bin/env python3
"""Adversarial Horn (C5) audit on RANDOM SPARSE triangle-free graphs, n=9..14.
Generate random graphs by adding random edges that keep the graph triangle-free (greedy reject),
targeting the BCL medium band edge density d_edge in [0.2486,0.3197] where the proof must hold, plus
some sparser/denser ones.  For each, run the FAST vectorized EXHAUSTIVE per-root Horn min (no
truncation).  Report the global worst H_R; any materially-negative value on a real graph => UNSOUND.
"""
import sys, time, random
import flag_engine as fe
from audit_horn_fast import audit

def rand_trifree(n, p, rng):
    """Random triangle-free graph: shuffle all pairs, add edge with prob p if it keeps tri-free."""
    A = [0] * n
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rng.shuffle(pairs)
    for (i, j) in pairs:
        if rng.random() < p and not (A[i] & A[j]):  # common neighbor => triangle
            A[i] |= 1 << j; A[j] |= 1 << i
    return A

def edens(n, A):
    e = sum(bin(A[v]).count('1') for v in range(n)) // 2
    return e, e / (n * (n - 1) / 2)

if __name__ == "__main__":
    rng = random.Random(20260626)
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    # spread across n=9..14 and densities aimed at / around the medium band
    plan = []
    ns = [9, 10, 11, 12, 13, 14]
    ps = [0.18, 0.24, 0.28, 0.32, 0.38]  # band d_edge ~0.25-0.32 sits in the middle here
    while len(plan) < N:
        for n in ns:
            for p in ps:
                if len(plan) < N:
                    plan.append((n, p))
    t0 = time.time()
    gmin = 0.0; garg = None
    seen = set()
    done = 0
    for (n, p) in plan:
        A = rand_trifree(n, p, rng)
        assert fe.is_triangle_free(n, A), "generated graph not triangle-free!"
        e, d = edens(n, A)
        key = (n, tuple(A))
        if key in seen:
            continue
        seen.add(key)
        h, arg = audit("n%d_d%.2f" % (n, d), n, A, ALLPAIRS=True, verbose=False)
        done += 1
        flag = "<<<NEG" if h < -1e-9 else ""
        if h < gmin:
            gmin = h; garg = (n, A, arg)
        print("  [%3d] n=%d e=%2d d_edge=%.3f  min H_R=%+.3e %s  band=%s"
              % (done, n, e, d, h, flag, "YES" if 0.2486 <= d <= 0.3197 else "no"), flush=True)
    print("\nGLOBAL min H_R over %d random sparse tri-free n=9..14 (all-pairs, EXHAUSTIVE) = %+.6e"
          % (done, gmin), flush=True)
    if garg:
        print("  argmin: n=%d A=%s root/subset=%s" % (garg[0], garg[1], garg[2]), flush=True)
    print("  SOUND ? %s  [%.0fs]" % (gmin >= -1e-9, time.time() - t0), flush=True)
    print("DONE", flush=True)
