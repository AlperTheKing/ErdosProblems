#!/usr/bin/env python3
"""
AUDIT GPT Q16's bad-Clebsch-cut fingerprint (the plateau explanation).
GPT claims: A0 = {emptyset,12,13,23,14,24,15,25} in Clebsch K gives e=40, cut=28, mono=12,
a strict 1-vertex local max with 12 vtx (d_C,d_M,h)=(3,2,1) and 4 vtx (5,0,5); max cut=32;
the switch S={13,23,45,1245} flips to gain 4 (28->32); the general switch identity
Sum_{v in S} H(v) + 2 e_M(S) - 2 e_C(S) >= 0 holds for MAX cuts but = -4 for this bad cut.
"""
labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]
adjset = [set(j for j in range(16) if i != j and bin(labels[i] ^ labels[j]).count('1') == 4) for i in range(16)]
lab2idx = {labels[i]: i for i in range(16)}
def sub(*vs):  # 1-indexed subset -> Clebsch vertex index
    m = 0
    for v in vs: m |= 1 << (v-1)
    return lab2idx[m]

A0 = [sub(), sub(1,2), sub(1,3), sub(2,3), sub(1,4), sub(2,4), sub(1,5), sub(2,5)]
A0set = set(A0); B0set = set(range(16)) - A0set
E = [(i, j) for i in range(16) for j in adjset[i] if j > i]
e = len(E)
cut = sum(1 for (i, j) in E if (i in A0set) != (j in A0set))
mono = e - cut
print(f"A0 = {sorted(A0)} (labels {sorted(labels[v] for v in A0)})")
print(f"e_K={e}  cut(A0,B0)={cut}  mono={mono}   (GPT: 40, 28, 12)  {'OK' if (e,cut,mono)==(40,28,12) else 'MISMATCH'}")

# per-vertex (d_C, d_M, h)
def side(v): return 0 if v in A0set else 1
prof = {}
for v in range(16):
    dC = sum(1 for w in adjset[v] if side(w) != side(v))
    dM = sum(1 for w in adjset[v] if side(w) == side(v))
    prof[v] = (dC, dM, dC - dM)
from collections import Counter
pc = Counter(prof.values())
print(f"margin profile (d_C,d_M,h) counts: {dict(pc)}   (GPT: (3,2,1)x12, (5,0,5)x4)")
strict_localmax = all(p[1] <= p[0] for p in prof.values()) and all(p[2] >= 1 for p in prof.values())
print(f"strict 1-vertex local max (every flip loses >=1 cut edge, h>=1 all): {strict_localmax}")

# exact max cut over 2^16
best = 0
for bits in range(1 << 16):
    c = sum(1 for (i, j) in E if ((bits >> i) ^ (bits >> j)) & 1)
    if c > best: best = c
print(f"exact MAX cut = {best}   (GPT: 32)  {'OK' if best==32 else 'MISMATCH'}")

# the improving switch S = {13,23,45,1245}
S = [sub(1,3), sub(2,3), sub(4,5), sub(1,2,4,5)]
Sset = set(S)
newside = lambda v: side(v) ^ (1 if v in Sset else 0)
cut2 = sum(1 for (i, j) in E if newside(i) != newside(j))
print(f"switch S={sorted(labels[v] for v in S)}: cut after flip = {cut2}  (GPT: 32, gain 4)  {'OK' if cut2==32 else 'MISMATCH'}")

# general identity value for S on the bad cut
sumH = sum(prof[v][2] for v in S)
eM_S = sum(1 for (i, j) in E if i in Sset and j in Sset and side(i) == side(j))
eC_S = sum(1 for (i, j) in E if i in Sset and j in Sset and side(i) != side(j))
val = sumH + 2*eM_S - 2*eC_S
print(f"identity Sum_H(S)+2e_M(S)-2e_C(S) = {sumH}+2*{eM_S}-2*{eC_S} = {val}  (GPT: -4, exposes non-opt)  {'OK' if val==-4 else 'MISMATCH'}")
print(f"  (= -(cut gain) = -(32-28) = -4: {val == -(cut2-cut)})")

# verify identity >= 0 holds for a GENUINE max cut (sanity)
# find a max cut coloring
maxbits = None
for bits in range(1 << 16):
    c = sum(1 for (i, j) in E if ((bits >> i) ^ (bits >> j)) & 1)
    if c == best: maxbits = bits; break
def sideM(v): return (maxbits >> v) & 1
viol = 0
import itertools
for ssz in (1, 2, 3, 4):
    for Scand in itertools.combinations(range(16), ssz):
        Ss = set(Scand)
        sH = sum((sum(1 for w in adjset[v] if sideM(w) != sideM(v)) - sum(1 for w in adjset[v] if sideM(w) == sideM(v))) for v in Scand)
        eM = sum(1 for (i, j) in E if i in Ss and j in Ss and sideM(i) == sideM(j))
        eC = sum(1 for (i, j) in E if i in Ss and j in Ss and sideM(i) != sideM(j))
        if sH + 2*eM - 2*eC < 0: viol += 1
print(f"identity >=0 on a genuine MAX cut for all |S|<=4: violations = {viol} (expect 0)")
print("DONE")
