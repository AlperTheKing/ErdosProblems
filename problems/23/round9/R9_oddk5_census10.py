"""R9: complete census check -- every triangle-free graph on 10 vertices, odd-K5 minor?"""
from R9_oddk5_lib import G, g6_decode
from R9_oddk5_minor import has_odd_k5_minor
import time, sys
src = r"E:/Projects/ErdosProblems/problems/23/round7/tf10.g6"
lines = [l.strip() for l in open(src) if l.strip()]
print(f"{len(lines)} graph6 words on 10 vertices")
t0 = time.time(); hits = []
for k, l in enumerate(lines):
    n, E = g6_decode(l)
    g = G(n, E)
    assert g.triangle_free() and n == 10
    if has_odd_k5_minor(g):
        hits.append((l, g.m))
        print(f"   HIT {l}  m={g.m}   ({time.time()-t0:.0f}s)"); sys.stdout.flush()
    if k % 500 == 0:
        print(f"   {k}/{len(lines)} ({time.time()-t0:.0f}s) hits={len(hits)}"); sys.stdout.flush()
print(f"DONE {len(lines)} graphs, hits = {len(hits)} : {hits}")
