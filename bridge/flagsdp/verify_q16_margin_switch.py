#!/usr/bin/env python3
"""
GPT Q16 UNIT TEST: does the margin-conditioned switch (with honest margin marks) EXCLUDE the
bad-cut Clebsch? Build the 16-vtx Clebsch with the bad cut A0 + honest 4-colors (A_L/A_H/B_L/B_H by
side and margin h: h=1->Low, h=5->High), then evaluate margin_switch_vec and localizer_vecs on it.
If margin switch functional > 0 (max-cut constraint SW<=0 VIOLATED) and localizers are satisfied,
the margin SDP excludes this pseudo-solution -> the plateau breaks.
"""
import flag_engine as fe, flag_margin_sdp as ms
import numpy as np

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

# honest 4-color: side (A0->A=0, else B=1) x margin mark (h<=t -> Low, else High)
def sd(v): return 0 if v in A0 else 1
col = [0]*16
for v in range(16):
    dC = sum(1 for w in range(16) if (A[v] >> w) & 1 and sd(w) != sd(v))
    dM = sum(1 for w in range(16) if (A[v] >> w) & 1 and sd(w) == sd(v))
    h = dC - dM                       # 1 or 5
    mark = 0 if h <= 2 else 1         # Low if h=1, High if h=5 (threshold between)
    col[v] = 2*sd(v) + mark           # 0=A_L,1=A_H,2=B_L,3=B_H

from collections import Counter
print("4-color distribution (0=A_L,1=A_H,2=B_L,3=B_H):", dict(Counter(col)))
state = (16, A, col)

# margin-conditioned switch functional
gsw = ms.margin_switch_vec([state])[0]
print(f"margin-conditioned switch functional on bad cut = {gsw}")
print(f"  (max-cut constraint is  switch <= 0; >0 means VIOLATED -> bad cut EXCLUDED): "
      f"{'EXCLUDED (>0)!' if gsw > 1e-9 else 'NOT excluded (<=0)'}")

# localizers (should be satisfied by honest marks): g_c <= 0 for each
locs = ms.localizer_vecs([state])
print("localizer values g_c (each should be <= 0 if marks honest):")
for c, g in enumerate(locs):
    print(f"  color {c} ({'A_L A_H B_L B_H'.split()[c]}): g={g[0]:+.5f}  {'OK<=0' if g[0] <= 1e-9 else 'VIOLATED'}")

# also: side-based SW1 and sw0 on the bad cut (the plateau's own constraints) — should be ~satisfied
import flag_margin_sdp as m2
dmono = m2.d_mono_vec([state]); dedge = m2.d_edge_vec([state])
print(f"\nside sw0 (2*d_mono - d_edge) = {(2*dmono - dedge)[0]:.4f} (<=0 ok)")
print(f"side SW1 (root_side 0) = {m2.side_sw1_vec([state],0)[0]}, (root_side 1) = {m2.side_sw1_vec([state],1)[0]}")
print("DONE")
