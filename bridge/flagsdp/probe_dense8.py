#!/usr/bin/env python3
"""Profile-count + root_min timing for the DENSEST n=8 tri-free graphs (most edges => most profiles)."""
import os, time
from math import comb
import numpy as np
import flag_engine as fe
from horn_soundness import buildW
from audit_horn_fast import root_min

out = open("res_dense8.txt", "w")
def log(s):
    out.write(s + "\n"); out.flush(); os.fsync(out.fileno()); print(s, flush=True)

gs = fe.enumerate_graphs(8, triangle_free=True)
# sort by edge count desc, take top 12 densest
def ne(A): return sum(bin(x).count('1') for x in A) // 2
gs2 = sorted(gs, key=lambda kA: -ne(kA[1]))[:12]
for (k, A) in gs2:
    e = ne(A)
    t0 = time.time(); W = buildW(8, A, ALLPAIRS=True); tb = time.time() - t0
    mp = 0; gw = 0.0; t1 = time.time()
    for key, ed in W.items():
        profs = sorted(set(a for (a, b) in ed) | set(b for (a, b) in ed), key=lambda s: (len(s), sorted(s)))
        m = len(profs); mp = max(mp, m)
        if m < 5:
            continue
        idx = {p: i for i, p in enumerate(profs)}
        P = np.zeros((m, m))
        for (a, b), w in ed.items():
            P[idx[a], idx[b]] += w
        P = 0.5 * (P + P.T)
        h, _ = root_min(P)
        if h < gw:
            gw = h
    log("e=%2d roots=%3d maxprof=%2d C(m,5)=%d buildW=%.1fs rootmin=%.1fs minH=%+.2e"
        % (e, len(W), mp, comb(mp, 5), tb, time.time() - t1, gw))
log("DENSE8DONE")
