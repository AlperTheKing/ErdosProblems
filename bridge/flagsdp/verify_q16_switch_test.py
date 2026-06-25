#!/usr/bin/env python3
"""
Decisive test of GPT Q16's claim: does an UNMARKED exact binary switch (k=1,2,3) DETECT the
bad-cut-colored Clebsch graph as non-optimal? The max-cut switching constraint is
  g_sigma(H) = sum over rooted embeddings, over edges uv, chi(uv)(p_u+p_v-2p_up_v),  <= 0  for max cuts.
If for the bad-cut coloring some unmarked rooted switch gives g>0, that coloring is DETECTABLY
non-optimal -> exact separation in the SDP excludes it (plateau breaks). GPT: unmarked k<=2 can't
(this blow-up satisfies every unmarked [0,1] k<=2 switch); k=3 detects it. We test directly on the
16-vertex Clebsch with the bad cut (densities = its blow-up's).
"""
import flag_engine as fe, flag_engine_col as fc, flag_separation as fs, flag_switch as sw
import numpy as np

labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]
adj = [[1 if (i!=j and bin(labels[i]^labels[j]).count('1')==4) else 0 for j in range(16)] for i in range(16)]
A = [0]*16
for i in range(16):
    for j in range(16):
        if adj[i][j]: A[i] |= 1<<j
lab2idx = {labels[i]: i for i in range(16)}
def sub(*vs):
    m=0
    for v in vs: m |= 1<<(v-1)
    return lab2idx[m]
A0 = {sub(), sub(1,2), sub(1,3), sub(2,3), sub(1,4), sub(2,4), sub(1,5), sub(2,5)}
col = [0 if v in A0 else 1 for v in range(16)]
state = (16, A, col)
_E = fe.edges_of(16, A)
_mono = sum(1 for (i, j) in _E if col[i] == col[j])
print(f"bad-cut Clebsch: 16 vtx, e={len(_E)}, mono={_mono}, mono-frac={_mono/len(_E):.3f}")

# for each colored type sigma at k=0,1,2,3, exact-binary max switch violation on this single state
print("Max EXACT-BINARY unmarked switch violation g(badcut) by root order k:")
for k in range(0, 4):
    bestk = 0.0; bestinfo = None
    for (kk, At, ct) in fc.enumerate_colored(k, triangle_free=True):
        sigma = (k, At, tuple(ct))
        classes, Ms = fs.precompute_M([state], sigma)
        Ubar = Ms[0]                     # single state, x*=1
        if Ubar.shape[0] == 0: continue
        v, p = fs.best_switch(Ubar, (0.0,0.5,1.0))
        if v > bestk:
            bestk = v; bestinfo = (sigma[2], classes, p)
    flag = " <== DETECTED (violation>0): unmarked k-switch excludes the bad cut!" if bestk > 1e-6 else " (not detected: <=0)"
    print(f"  k={k}: max violation = {bestk:.4f}{flag}")

print()
print("Interpretation: if k<=2 gives ~0 but k=3 gives >0 -> exact k=3 separation breaks the plateau")
print("(no margin colors needed). If ALL unmarked k<=3 give ~0 -> margin colors ARE essential.")
print("DONE")
