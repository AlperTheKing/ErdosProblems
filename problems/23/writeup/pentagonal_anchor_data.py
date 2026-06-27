#!/usr/bin/env python3
"""Exact R=1-P cut-metric + pentagonal-form data at the anchors, to AUDIT GPT-Pro round-4's
NRS pentagonal inequality the moment it lands (#23 delta=0).
R_ij = Pr[i,j separated over ALL max cuts] = 1 - P_ij  (a cut metric => hypermetric).
Pentagonal/negative-type form for integer b, sum b_i = 1:  Q_b = sum_{i<j} b_i b_j R_ij <= 0.
C5-pattern b has three +1 and two -1 on a 5-subset.  Tight (=0) <=> the C5 cut-metric direction."""
from fractions import Fraction as F
from itertools import combinations, permutations

def maxcut_opt(n, edges):
    best=-1; opt=[]
    for m in range(1<<n):
        c=sum(1 for (u,v) in edges if ((m>>u)&1)!=((m>>v)&1))
        if c>best: best=c; opt=[m]
        elif c==best: opt.append(m)
    return best,opt

def Rmatrix(n,edges):
    mc,opt=maxcut_opt(n,edges); K=len(opt)
    R=[[F(0)]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i!=j:
                sep=sum(1 for m in opt if ((m>>i)&1)!=((m>>j)&1))
                R[i][j]=F(sep,K)
    return R,K,len(edges)-mc

def pent_form(R, sub, b):
    # Q_b = sum_{i<j in sub} b_i b_j R_ij
    s=F(0)
    for a in range(len(sub)):
        for c in range(a+1,len(sub)):
            s+=b[a]*b[c]*R[sub[a]][sub[c]]
    return s

def min_pent_over_5subsets(R,n):
    """min over 5-subsets and C5-pattern sign assignments (three +1, two -1) of Q_b."""
    best=None; arg=None
    pats=set()
    base=[1,1,1,-1,-1]
    for p in set(permutations(base)): pats.add(p)
    for sub in combinations(range(n),5):
        for b in pats:
            q=pent_form(R,list(sub),list(b))
            if best is None or q<best: best=q; arg=(sub,b)
    return best,arg

def cyc(n): return n,[(i,(i+1)%n) for i in range(n)]
def petersen():
    out=[(i,(i+1)%5) for i in range(5)]; inn=[(5+i,5+((i+2)%5)) for i in range(5)]
    return 10,out+inn+[(i,5+i) for i in range(5)]
def g6dec(s):
    b=[ord(c)-63 for c in s]; n=b[0]; bits=[]
    for x in b[1:]:
        for k in range(5,-1,-1): bits.append((x>>k)&1)
    E=[];idx=0
    for j in range(1,n):
        for i in range(j):
            if idx<len(bits) and bits[idx]: E.append((i,j));
            idx+=1
    return n,E

print("=== C5 R-metric (THE anchor) ===")
R,K,beta=Rmatrix(*cyc(5))
print(f"  #maxcuts={K}, beta={beta}")
print("  R (edges adjacent should be 4/5, dist-2 should be 2/5):")
for i in range(5): print("   ",[str(R[i][j]) for j in range(5)])
q,arg=min_pent_over_5subsets(R,5)
print(f"  min C5-pattern pentagonal Q_b over 5-subsets = {q} (={float(q):.4f}); arg sub/b={arg}")
print(f"  pentagonal TIGHT at C5? {q==0}  (the natural cyclic b=(1,-1,1,-1,1)-type pattern)")

for name,(n,E) in [("C7",cyc(7)),("Petersen",petersen()),("band-max-n8",g6dec("G?`F`w"))]:
    R,K,beta=Rmatrix(n,E)
    q,arg=min_pent_over_5subsets(R,n)
    print(f"\n=== {name}: n={n} beta={beta} #maxcuts={K} ===")
    print(f"  min C5-pattern pentagonal Q_b = {q} (={float(q):.4f})  arg={arg}")
    print(f"  strictly negative (C5-direction not realizable)? {q<0}")
print("\nAUDIT USE: GPT round-4 should give an inequality F <= L(d_edge) + (pentagonal slack), tight at")
print("C5 (Q=0, F=2/25, d_edge=2/5). Check its constants reproduce C5's R=4/5(edge)/2/5(dist2) and Q=0.")
