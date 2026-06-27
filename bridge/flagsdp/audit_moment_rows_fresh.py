#!/usr/bin/env python3
"""Confirm the 317 cp_cache MOMENT rows the LP uses are VALID on real graphons (do NOT cut off real graphs).
Each LP static row is  -(row).q9 <= 0  i.e. row.q9 >= 0.  q9 = real graphon's T_9 induced-subgraph distribution.
If any real tri-free graph has row.q9 < 0 for a 'moment'-typed row, that row is UNSOUND => could underestimate eta*
=> FALSE-closure risk.  We build q9 for the zoo + exhaustive n<=7 (i.i.d. 9-sampling of the blow-up graphon) and
check min over all moment rows.  Also reports how many rows are 'moment' vs other (localizer) types, confirming the
LP filters to moment-only.
"""
import time, pickle, itertools
from math import factorial
import numpy as np
from compute_U8 import popcount
from c5_lift_diag import key9
import flag_engine as fe

def cyc(m):
    A=[0]*m
    for i in range(m): A[i]|=1<<((i+1)%m); A[i]|=1<<((i-1)%m)
    return A
def petersen():
    A=[0]*10
    def e(u,v): A[u]|=1<<v; A[v]|=1<<u
    for i in range(5): e(i,(i+1)%5); e(5+i,5+((i+2)%5)); e(i,5+i)
    return A
def comps(total,parts):
    if parts==1: yield (total,); return
    for f in range(total+1):
        for rest in comps(total-f,parts-1): yield (f,)+rest
def blowup(counts,T):
    parts=[]
    for p,c in enumerate(counts): parts+=[p]*c
    n=len(parts); A=[0]*n
    for u in range(n):
        for w in range(u+1,n):
            if parts[u]!=parts[w] and (T[parts[u]]>>parts[w])&1: A[u]|=1<<w; A[w]|=1<<u
    return n,A

def q9_of_graph(n0,A0):
    """real graphon q over T_9 = i.i.d. 9-sample induced density of blow-up of (n0,A0), uniform weights."""
    ns=len(STATES); q=np.zeros(ns); m=n0; T=A0
    for counts in comps(9,m):
        w=factorial(9)
        for c in counts: w//=factorial(c)
        wt=w*((1.0/m)**9)
        if wt==0: continue
        n,A=blowup(counts,T)  # n=9
        hi=KEY.get(key9(9,A),-1)
        if hi<0: raise RuntimeError("T_9 miss")
        q[hi]+=wt
    return q

# load cache + T_9 states
C=pickle.load(open("cache_n9.pkl","rb")); STATES=C["states"]; KEY={key9(n,A):i for i,(n,A) in enumerate(STATES)}
assert len(KEY)==len(STATES)
ns,dedge,rows,provtypes,_=pickle.load(open("cp_cache.pkl","rb"))
def ptype(p): return p[0] if isinstance(p,(list,tuple)) else p
mom_idx=[i for i in range(len(rows)) if ptype(provtypes[i])=='moment']
other=[ptype(provtypes[i]) for i in range(len(rows)) if ptype(provtypes[i])!='moment']
from collections import Counter
print(f"cp_cache rows: total={len(rows)}  moment={len(mom_idx)}  non-moment(excluded)={len(other)} types={Counter(other)}")
M=np.array([np.asarray(rows[i],float) for i in mom_idx])  # (nmom, ns)

zoo=[("C5",5,cyc(5)),("C7",7,cyc(7)),("C9",9,cyc(9)),("C11",11,cyc(11)),("Petersen",10,petersen())]
worst=1e9; worstarg=None
for (nm,n,A) in zoo:
    q=q9_of_graph(n,A); vals=M@q; mn=float(vals.min())
    if mn<worst: worst=mn; worstarg=nm
    print(f"  {nm:9s} min moment-row.q9 = {mn:+.3e}  ({'OK' if mn>=-1e-9 else 'NEGATIVE!'})")
t0=time.time()
for nn in [6,7]:
    gs=fe.enumerate_graphs(nn,triangle_free=True); mn_all=1e9; viol=0
    for (k,A) in gs:
        q=q9_of_graph(nn,A); mn=float((M@q).min())
        if mn<-1e-9: viol+=1; print(f"  NEG n={nn} A={A} min={mn:.3e}")
        if mn<mn_all: mn_all=mn
        if mn<worst: worst=mn; worstarg=f"n{nn}"
    print(f"  n={nn}: {len(gs)} graphs, min moment-row.q9={mn_all:+.3e} viol={viol} [{time.time()-t0:.0f}s]")
print(f"\nWORST moment-row.q9 over all real tested = {worst:+.3e} at {worstarg}")
print(f"  MOMENT ROWS SOUND (>=0 on reals => do NOT cut off real graphons) ? {worst>=-1e-9}")
print("DONE")
