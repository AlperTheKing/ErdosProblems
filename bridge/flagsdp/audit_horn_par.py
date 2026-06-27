#!/usr/bin/env python3
"""PARALLEL adversarial Horn (C5) audit on the ALL-PAIRS matrix P_R.
buildW dominates cost (~7s/graph), so fan out over graphs with joblib. Each worker computes the
FAST vectorized EXHAUSTIVE per-root Horn min (NO degree truncation). Writes incremental results to
a result file with fsync so progress is visible.

Usage:
  python audit_horn_par.py n8           # all 410 tri-free graphs on n=8
  python audit_horn_par.py rand <N>     # N random sparse tri-free graphs n=9..14
  python audit_horn_par.py cyc C11 C13 C15
"""
import sys, os, time, random
import numpy as np
from joblib import Parallel, delayed
import flag_engine as fe
from horn_soundness import buildW
from audit_horn_fast import root_min

def graph_min(n, A):
    """Min H_R over all roots of one graph, EXHAUSTIVE per-root. Returns (minH, (rootkey, subset))."""
    W = buildW(n, A, ALLPAIRS=True)
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
    return gw, garg

def cyc_graph(n):
    A = [0] * n
    for i in range(n):
        A[i] |= 1 << ((i + 1) % n); A[(i + 1) % n] |= 1 << i
    return A

def rand_trifree(n, p, rng):
    A = [0] * n
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rng.shuffle(pairs)
    for (i, j) in pairs:
        if rng.random() < p and not (A[i] & A[j]):
            A[i] |= 1 << j; A[j] |= 1 << i
    return A

def edens(n, A):
    e = sum(bin(A[v]).count('1') for v in range(n)) // 2
    return e, e / (n * (n - 1) / 2)

if __name__ == "__main__":
    mode = sys.argv[1]
    RF = open("res_%s.txt" % mode, "w")
    def log(s):
        print(s, flush=True); RF.write(s + "\n"); RF.flush(); os.fsync(RF.fileno())
    NJ = 16
    t0 = time.time()

    if mode == "n8":
        gs = fe.enumerate_graphs(8, triangle_free=True)
        items = [(8, A) for (k, A) in gs]
        log("n=8 tri-free graphs: %d  (NJ=%d)" % (len(items), NJ))
    elif mode == "rand":
        N = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        rng = random.Random(20260626)
        ns = [9, 10, 11, 12, 13, 14]; ps = [0.18, 0.24, 0.28, 0.32, 0.38]
        items = []; seen = set()
        while len(items) < N:
            for n in ns:
                for p in ps:
                    if len(items) >= N:
                        break
                    A = rand_trifree(n, p, rng)
                    assert fe.is_triangle_free(n, A)
                    key = (n, tuple(A))
                    if key in seen:
                        continue
                    seen.add(key); items.append((n, A))
        log("random sparse tri-free graphs n=9..14: %d  (NJ=%d)" % (len(items), NJ))
    elif mode == "cyc":
        names = sys.argv[2:]
        nmap = {("C%d" % k): k for k in range(5, 30, 2)}
        items = [(nmap[nm], cyc_graph(nmap[nm])) for nm in names]
        log("odd cycles: %s  (NJ=%d)" % (names, min(NJ, len(items))))
    else:
        raise SystemExit("unknown mode")

    res = Parallel(n_jobs=min(NJ, len(items)), backend="loky")(
        delayed(graph_min)(n, A) for (n, A) in items)

    gmin = 0.0; gi = None
    worst = []
    for i, (h, arg) in enumerate(res):
        n, A = items[i]
        e, d = edens(n, A)
        worst.append((h, i, n, A, arg))
        if h < gmin:
            gmin = h; gi = (i, n, A, arg)
        if h < -1e-9:
            log("  <<<NEG  item %d n=%d d_edge=%.3f H_R=%+.3e A=%s root/sub=%s" % (i, n, d, h, A, arg))
    worst.sort()
    log("\nworst 6 (H_R, item, n, d_edge): %s"
        % [(round(w, 4 if w < -1e-6 else 13), i, nn, round(edens(nn, AA)[1], 3))
           for (w, i, nn, AA, _) in worst[:6]])
    log("GLOBAL min H_R (%s, all-pairs, EXHAUSTIVE) = %+.6e over %d graphs" % (mode, gmin, len(items)))
    log("  argmin = %s" % (gi,))
    log("  SOUND ? %s  [%.0fs]" % (gmin >= -1e-9, time.time() - t0))
    log("DONE")
