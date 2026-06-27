#!/usr/bin/env python3
"""Adversarial Horn (C5) audit on ALL triangle-free graphs on n=8 (new coverage beyond n<=7 + zoo).
Uses the FAST vectorized EXHAUSTIVE per-root min (audit_horn_fast.audit), NO degree truncation.
Must report min H_R >= -1e-9 over every graph; tracks the global worst and its argmin graph.
"""
import time, os
import flag_engine as fe
from audit_horn_fast import audit

RF = open("res_n8.txt", "w")
def log(s):
    print(s, flush=True); RF.write(s + "\n"); RF.flush(); os.fsync(RF.fileno())

if __name__ == "__main__":
    gs = fe.enumerate_graphs(8, triangle_free=True)
    log("n=8 tri-free graphs: %d" % len(gs))
    t0 = time.time()
    gmin = 0.0; gargG = None; gargR = None
    worst5 = []
    for ci, (k, A) in enumerate(gs):
        h, arg = audit("g%d" % ci, 8, A, ALLPAIRS=True, verbose=False)
        worst5.append((h, ci, A))
        if h < gmin:
            gmin = h; gargG = (ci, A); gargR = arg
        if (ci + 1) % 25 == 0:
            log("  ...%d/%d done, running min=%+.3e  [%.0fs]"
                % (ci + 1, len(gs), gmin, time.time() - t0))
    worst5.sort()
    log("\nGLOBAL min H_R over all 410 n=8 tri-free (all-pairs, EXHAUSTIVE) = %+.6e" % gmin)
    log("  argmin graph index/A = %s ; root/subset = %s" % (gargG, gargR))
    log("  5 worst graphs (H_R, idx): %s" % [(round(w, 3 if w < -1e-6 else 12), i) for (w, i, _) in worst5[:5]])
    log("  SOUND on n=8 ? %s  [%.0fs]" % (gmin >= -1e-9, time.time() - t0))
    log("DONE")
