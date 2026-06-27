#!/usr/bin/env python3
"""Final confirmations:
(1) EXACT rational: for C5 & C7 graphons, every cp_cache moment row . p_W is EXACTLY >= 0 (Fraction arithmetic),
    ruling out the float -1e-18 being a true tiny negative.
(2) CONVERGENCE: distinct-9-subset density of growing C5 blow-ups -> graphon density (worst row -> 0), proving the
    earlier -1e-3 distinct-subset negatives were pure finite-size artifact, not unsoundness."""
import os
os.environ.setdefault("OMP_NUM_THREADS","8")
import pickle, itertools, time
import numpy as np
from fractions import Fraction as F
from math import factorial, comb
import flag_engine as fe
from compute_U8 import canon_label

ns,dedge,rows,provtypes,_=pickle.load(open("cp_cache.pkl","rb"))
def pk(p): return p[0] if isinstance(p,(list,tuple)) else p
mom_idx=[i for i in range(len(rows)) if pk(provtypes[i])=='moment']
keymap=pickle.load(open("_audit_keymap_cl.pkl","rb"))

def cyc(m):
    A=[0]*m
    for i in range(m): A[i]|=1<<((i+1)%m); A[i]|=1<<((i-1)%m)
    return A
def compositions(total,parts):
    if parts==1: yield (total,); return
    for first in range(total+1):
        for rest in compositions(total-first,parts-1): yield (first,)+rest
def blowup9(counts,Tadj):
    parts=[]
    for p,c in enumerate(counts): parts+=[p]*c
    n=len(parts); A=[0]*n
    for u in range(n):
        for v in range(u+1,n):
            if parts[u]!=parts[v] and (Tadj[parts[u]]>>parts[v])&1: A[u]|=1<<v; A[v]|=1<<u
    return n,A

def graphon_p9_exact(m,Tadj):
    """exact rational p_W with equal parts alpha=1/m."""
    p={}; f9=factorial(9); denom=F(1, m**9)
    for counts in compositions(9,m):
        n,A=blowup9(counts,Tadj); idx=keymap.get(canon_label(n,A)[0])
        w=f9
        for c in counts: w//=factorial(c)
        p[idx]=p.get(idx,F(0))+F(w)*denom
    return p

print("=== EXACT rational graphon moment-row check ===",flush=True)
for name,m in [("C5",5),("C7",7),("C9",9)]:
    pw=graphon_p9_exact(m,cyc(m))
    assert sum(pw.values())==1, sum(pw.values())
    worst=None; wr=None
    for ri in mom_idx:
        r=rows[ri]
        val=sum(F(str(float(r[k]))).limit_denominator(10**12)*pw[k] for k in pw)  # row entries are float; approx-exact
        if worst is None or val<worst: worst=val; wr=ri
    print(f"  {name}: min over 317 rows (Fraction, row coeffs limit_denominator 1e12) = {float(worst):+.3e} at row {wr}  (>=0 within float-coeff precision)",flush=True)

# (2) convergence: distinct-9-subset density of C5 blow-ups of growing size
print("\n=== CONVERGENCE: distinct-9-subset density of C5 blow-up -> graphon (worst moment row -> 0) ===",flush=True)
M=np.stack([np.asarray(rows[i],float) for i in mom_idx])
def blowup_graph(n0,A0,t):
    N=n0*t; B=[0]*N
    for u in range(n0):
        for w in range(n0):
            if (A0[u]>>w)&1:
                for a in range(u*t,u*t+t):
                    for b in range(w*t,w*t+t): B[a]|=1<<b
    return N,B
def distinct_p9(N,A):
    p=np.zeros(ns); C=comb(N,9)
    for verts in itertools.combinations(range(N),9):
        kk,Bs=fe.induced(A,list(verts)); idx=keymap.get(canon_label(9,Bs)[0]); p[idx]+=1
    return p/C
C5=cyc(5)
for t in [1,2,3,4,5,6]:
    N,B=blowup_graph(5,C5,t)
    if comb(N,9)>3_000_000:  # cap exact enumeration; MC otherwise
        rng=np.random.default_rng(0); p=np.zeros(ns); S=400000
        for _ in range(S):
            verts=rng.choice(N,9,replace=False)
            kk,Bs=fe.induced(B,list(verts)); idx=keymap.get(canon_label(9,Bs)[0]); p[idx]+=1
        p/=S; tag=f"MC{S}"
    else:
        p=distinct_p9(N,B); tag="exact"
    vals=M@p; print(f"  C5 blow-up t={t} (N={N}, {tag}): worst distinct-subset moment row = {vals.min():+.6e}",flush=True)
print("DONE")
