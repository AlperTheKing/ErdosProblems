#!/usr/bin/env python3
"""
Cheap pre-test for the N=6 margin SDP: does the bad-cut Clebsch BLOW-UP's order-6 colored
density actually VIOLATE the margin-switch constraint (gsw@x > 0)?  If yes, the full N=6
4-color SDP can exclude the bad cut -> worth running. If gsw@x <= 0 even with honest order-6
marks, order 6 is too low (need N=7 or PSD localizers).
"""
import numpy as np, random
import flag_engine as fe, flag_engine_col as fc, flag_engine_kcol as kc, flag_margin_sdp as ms

# --- bad-cut Clebsch (16 vtx) with honest 4-colors (same construction as the unit test) ---
labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]
A = [0]*16
for i in range(16):
    for j in range(16):
        if i != j and bin(labels[i] ^ labels[j]).count('1') == 4:
            A[i] |= 1 << j
lab2idx = {labels[i]: i for i in range(16)}
def sub(*vs):
    m = 0
    for v in vs: m |= 1 << (v-1)
    return lab2idx[m]
A0 = {sub(), sub(1,2), sub(1,3), sub(2,3), sub(1,4), sub(2,4), sub(1,5), sub(2,5)}
def sd(v): return 0 if v in A0 else 1
col = [0]*16
for v in range(16):
    dC = sum(1 for w in range(16) if (A[v] >> w) & 1 and sd(w) != sd(v))
    dM = sum(1 for w in range(16) if (A[v] >> w) & 1 and sd(w) == sd(v))
    h = dC - dM
    col[v] = 2*sd(v) + (0 if h <= 2 else 1)

N = 6
print(f"enumerating N={N} 4-colored triangle-free states ...", flush=True)
states = kc.enumerate_kcolored(N, 4, triangle_free=True)
print(f"  states={len(states)}; building canonical-key index ...", flush=True)
key2idx = {}
for idx, (n, Ag, cg) in enumerate(states):
    key2idx[fc.canonical_col(n, Ag, cg, roots=0)] = idx

gsw = ms.margin_switch_vec(states)
locs = ms.localizer_vecs(states)
dmono = ms.d_mono_vec(states); dedge = ms.d_edge_vec(states)
basic0 = 2*dmono - dedge

random.seed(12345)
SAMP = 300000
x = np.zeros(len(states))
miss = 0
print(f"sampling {SAMP} order-6 blow-up shadows ...", flush=True)
for s in range(SAMP):
    pts = [random.randrange(16) for _ in range(6)]
    Asub = [0]*6
    csub = [col[pts[i]] for i in range(6)]
    for i in range(6):
        for j in range(i+1, 6):
            if pts[i] != pts[j] and (A[pts[i]] >> pts[j]) & 1:
                Asub[i] |= 1 << j; Asub[j] |= 1 << i
    k = fc.canonical_col(6, Asub, csub, roots=0)
    j = key2idx.get(k)
    if j is None:
        miss += 1; continue
    x[j] += 1
tot = x.sum()
x /= tot
gswx = float(gsw @ x)
print(f"samples={SAMP} miss={miss} (miss should be ~0)")
print(f"  d_mono(bad-cut order6) = {dmono@x:.5f}   d_edge = {dedge@x:.5f}")
print(f"  basic side-sw0 (2*dmono-dedge) = {basic0@x:+.5f}   (<=0 ok)")
verdict = "VIOLATED >0  -> N=6 EXCLUDES bad cut!" if gswx > 1e-6 else "<=0 : order-6 too low to exclude"
print(f"  MARGIN SWITCH gsw@x = {gswx:+.6f}   [{verdict}]")
for c in range(4):
    lv = float(locs[c] @ x)
    tag = "OK<=0" if lv <= 1e-6 else "VIOLATED (order-6 marks inconsistent)"
    print(f"  localizer color {c}: {lv:+.6f}  [{tag}]")
print("DONE")
