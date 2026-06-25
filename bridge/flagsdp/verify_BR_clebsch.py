#!/usr/bin/env python3
"""
Audit GPT Q17 Section 9-10: the bipartite-block recoloring (BR) inequality and the order-5
monochromatic-P3 cut that excludes the bad Clebsch cut WITHOUT margin colors.

BR (valid for a GLOBAL max cut, U with G[U] bipartite):  m(U) + m(U,Ubar) <= (1/2) e(U,Ubar).
Here m(U)=mono edges inside U, m(U,Ubar)=mono boundary edges, e(U,Ubar)=all boundary edges (mono=same side).

Order-5 cut: root a monochromatic P3  1-3-2  (13,23 in E, 12 notin E, all 3 same side); U = N(1) symdiff N(2).
Claim: on the bad 28-edge Clebsch cut every such embedding VIOLATES BR by exactly +1; on a genuine max
cut BR holds (<=0). We check both, plus C5[n] (expect: no mono-P3 embeddings -> vacuous -> sound).
"""
import itertools

# --- Clebsch graph on 16 even-weight vertices, adjacency = Hamming distance 4 ---
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
A0 = {sub(), sub(1,2), sub(1,3), sub(2,3), sub(1,4), sub(2,4), sub(1,5), sub(2,5)}   # bad 28-edge cut side A

def nbrs(v): return [w for w in range(16) if (A[v] >> w) & 1]

def br_value(side, n, adj, idxs):
    """For a 2-coloring `side` (dict v->0/1) of graph on `n` vertices with adjacency adj(u,v),
       enumerate mono-P3 (1-3-2) over the given vertex set idxs; for each U=N(1)^N(2) return
       lhs - rhs = m(U)+m(U,Ubar) - e(U,Ubar)/2 (the BR slack; >0 = violated)."""
    out = []
    Nset = {v: set(w for w in idxs if w != v and adj(v, w)) for v in idxs}
    for c in idxs:                       # center 3
        for a, b in itertools.combinations(sorted(Nset[c]), 2):  # ends 1,2 both adjacent to center
            if adj(a, b):                # need 12 notin E
                continue
            if not (side[a] == side[b] == side[c]):   # mono P3: all same side
                continue
            U = Nset[a] ^ Nset[b]        # symmetric difference N(1) ^ N(2)
            if not U:
                continue
            Ulist = sorted(U)
            mU = 0       # mono edges inside U
            for x, y in itertools.combinations(Ulist, 2):
                if adj(x, y) and side[x] == side[y]:
                    mU += 1
            mUb = 0      # mono boundary edges
            eUb = 0      # all boundary edges
            for x in Ulist:
                for y in idxs:
                    if y in U or y == x: continue
                    if adj(x, y):
                        eUb += 1
                        if side[x] == side[y]: mUb += 1
            slack = mU + mUb - eUb/2.0
            out.append((a, c, b, len(U), mU, mUb, eUb, slack))
    return out

def adjC(u, v): return bool((A[u] >> v) & 1)

# (1) bad cut
sideBad = {v: (0 if v in A0 else 1) for v in range(16)}
resBad = br_value(sideBad, 16, adjC, list(range(16)))
viol = [r for r in resBad if r[7] > 1e-9]
print(f"=== bad 28-edge Clebsch cut ===  mono-P3 embeddings={len(resBad)}, BR-violations={len(viol)}")
slacks = sorted(set(round(r[7],3) for r in resBad))
print(f"  distinct BR slacks (lhs-rhs) = {slacks}   (GPT: every embedding violates by exactly +1)")
if resBad:
    a,c,b,uu,mU,mUb,eUb,s = resBad[0]
    print(f"  sample P3 ({a}-{c}-{b}): |U|={uu} m(U)={mU} m(U,Ubar)={mUb} e(U,Ubar)={eUb} -> slack={s}")

# (2) a genuine MAX cut of Clebsch (value 32). Find one by simple search over balanced-ish cuts via greedy+local.
import random
def cutval(side):
    return sum(1 for u in range(16) for v in range(u+1,16) if adjC(u,v) and side[u]!=side[v])
best=None; bestv=-1
# brute-ish: Clebsch maxcut known =32; try many random + local opt (deterministic seed via fixed perms)
for seed in range(4000):
    s={}
    r=seed
    for v in range(16):
        r=(r*1103515245+12345)&0x7fffffff
        s[v]=r&1
    improved=True
    while improved:
        improved=False
        for v in range(16):
            d_same=sum(1 for w in nbrs(v) if s[w]==s[v])
            d_diff=sum(1 for w in nbrs(v) if s[w]!=s[v])
            if d_same>d_diff:
                s[v]^=1; improved=True
    cv=cutval(s)
    if cv>bestv: bestv=cv; best=dict(s)
print(f"\n=== genuine Clebsch max cut found (value={bestv}, max=32) ===")
resMax = br_value(best, 16, adjC, list(range(16)))
violMax = [r for r in resMax if r[7] > 1e-9]
print(f"  mono-P3 embeddings={len(resMax)}, BR-violations={len(violMax)}  (sound iff 0 violations)")

# (3) C5[n] extremal (use blow-up factor t per part; check mono-P3 existence under max-cut coloring)
t=3
parts=[[5*p+i for i in range(t)] for p in range(5)]  # 5 parts size t, vertices 0..5t-1
nn=5*t
def adj5(u,v):
    pu,pv=u//t,v//t
    return pu!=pv and (abs(pu-pv)==1 or abs(pu-pv)==4)
# max-cut coloring: sideA = parts {0,2,4}, sideB = parts {1,3}
side5={v:(0 if (v//t) in (0,2,4) else 1) for v in range(nn)}
res5 = br_value(side5, nn, adj5, list(range(nn)))
viol5=[r for r in res5 if r[7]>1e-9]
print(f"\n=== C5[{t}] extremal max cut ===  mono-P3 embeddings={len(res5)}, BR-violations={len(viol5)}")
print(f"  (expect 0 embeddings or 0 violations -> sound; mono super-edge 4-0 gives <=1 mono-nbr per vtx)")

print("\nVERDICT:",
      "BR cut EXCLUDES bad Clebsch cut" if viol else "bad cut NOT excluded",
      "| SOUND on Clebsch max cut" if not violMax else "| *** UNSOUND on max cut ***",
      "| SOUND on C5[n]" if not viol5 else "| *** UNSOUND on C5 ***")
print("DONE")
