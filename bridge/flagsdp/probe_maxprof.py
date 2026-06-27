#!/usr/bin/env python3
"""Max profiles-per-root over all n=8 tri-free graphs -> sizes C(m,5) for the exhaustive min."""
import os, time
from math import comb
import flag_engine as fe
from horn_soundness import buildW

out = open("res_maxprof.txt", "w")
def log(s):
    out.write(s + "\n"); out.flush(); os.fsync(out.fileno()); print(s, flush=True)

gs = fe.enumerate_graphs(8, triangle_free=True)
gmax = 0; gC = 0; arg = None
t0 = time.time()
for ci, (k, A) in enumerate(gs):
    W = buildW(8, A, ALLPAIRS=True)
    for key, ed in W.items():
        m = len(set(a for (a, b) in ed) | set(b for (a, b) in ed))
        if m > gmax:
            gmax = m; gC = comb(m, 5); arg = (ci, A)
    if (ci + 1) % 50 == 0:
        log("  ...%d/410  running maxprof=%d C(m,5)=%d  [%.0fs]" % (ci + 1, gmax, gC, time.time() - t0))
log("MAX profiles/root over n=8 = %d -> C(m,5)=%d  arg idx=%s" % (gmax, gC, arg[0]))
log("PROBEDONE")
