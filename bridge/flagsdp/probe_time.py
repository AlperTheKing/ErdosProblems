#!/usr/bin/env python3
import time, os
import flag_engine as fe
from horn_soundness import buildW
from audit_horn_fast import root_min
import numpy as np

gs = fe.enumerate_graphs(8, triangle_free=True)
out = open("res_probe.txt", "w")
def log(s):
    out.write(s + "\n"); out.flush(); os.fsync(out.fileno()); print(s, flush=True)

# time first 8 graphs, report buildW time, max profiles/root, root_min time
for ci in range(8):
    k, A = gs[ci]
    t0 = time.time(); W = buildW(8, A, ALLPAIRS=True); tb = time.time() - t0
    mp = 0
    t1 = time.time(); gw = 0.0
    for key, ed in W.items():
        profs = set(a for (a, b) in ed) | set(b for (a, b) in ed)
        mp = max(mp, len(profs))
        idx = {p: i for i, p in enumerate(sorted(profs, key=lambda s: (len(s), sorted(s))))}
        mm = len(profs)
        if mm < 5:
            continue
        P = np.zeros((mm, mm))
        for (a, b), w in ed.items():
            P[idx[a], idx[b]] += w
        P = 0.5 * (P + P.T)
        h, _ = root_min(P)
        if h < gw:
            gw = h
    tr = time.time() - t1
    log("g%d: buildW=%.2fs roots=%d maxprof=%d root_min=%.2fs minH=%+.2e" % (ci, tb, len(W), mp, tr, gw))
log("PROBEDONE")
