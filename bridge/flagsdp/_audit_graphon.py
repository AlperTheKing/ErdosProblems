#!/usr/bin/env python3
"""AUDIT v2 (GRAPHON normalization - the CORRECT object per the documented finite-vs-limit trap).
For a finite triangle-free template T (C5,C7,..., or any real triangle-free graph as a step-graphon with equal
parts), the GRAPHON order-9 density is computed EXACTLY via COUNT-VECTORS: compositions (n_0..n_{m-1}) of 9 into
m parts, weight = multinomial(9;n)*prod alpha_i^{n_i}; induced 9-graph = T-blow-up with those part sizes (same-part
points non-adjacent). This is the i.i.d.-with-repetition (blow-up limit) density. We then test the cp_cache.pkl
317 'moment' rows: value = row . p_W. If a row goes materially negative (< ~-1e-9) on a real triangle-free graphon
it is UNSOUND. We sweep many real triangle-free templates (cycles C5..C13, Petersen, complete bipartite,
random triangle-free, and the geng-enumerated small graphs as equal-weight step graphons)."""
import os
os.environ.setdefault("OMP_NUM_THREADS","8")
import pickle, itertools, time
import numpy as np
from math import comb, factorial
import flag_engine as fe
from compute_U8 import canon_label

t0=time.time()
ns,dedge,rows,provtypes,_=pickle.load(open("cp_cache.pkl","rb"))
def pk(p): return p[0] if isinstance(p,(list,tuple)) else p
mom_idx=[i for i in range(len(rows)) if pk(provtypes[i])=='moment']
M=np.stack([np.asarray(rows[i],float) for i in mom_idx])
keymap=pickle.load(open("_audit_keymap_cl.pkl","rb"))
print(f"[{time.time()-t0:.1f}s] {M.shape[0]} moment rows",flush=True)

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

def graphon_p9(m,Tadj,alpha=None):
    """equal-part step graphon on template T (m parts). p_W over the 1897 states (float)."""
    if alpha is None: alpha=[1.0/m]*m
    p=np.zeros(ns)
    f9=factorial(9)
    for counts in compositions(9,m):
        n,A=blowup9(counts,Tadj)
        idx=keymap.get(canon_label(9,A)[0])
        if idx is None: raise RuntimeError("blowup state missing (not tri-free?)")
        w=f9
        for c in counts: w//=factorial(c)
        wt=float(w)
        for pidx,c in enumerate(counts): wt*=alpha[pidx]**c
        p[idx]+=wt
    return p

def cyc(m):
    A=[0]*m
    for i in range(m): A[i]|=1<<((i+1)%m); A[i]|=1<<((i-1)%m)
    return A
def petersen():
    n=10; A=[0]*n
    def e(a,b): A[a]|=1<<b; A[b]|=1<<a
    for i in range(5):
        e(i,(i+1)%5); e(5+i,5+((i+2)%5)); e(i,5+i)
    return A
def kbipart(a,b):
    n=a+b; A=[0]*n
    for i in range(a):
        for j in range(a,n): A[i]|=1<<j; A[j]|=1<<i
    return n,A

results=[]
def test(name,m,Tadj,alpha=None):
    if not fe.is_triangle_free(m,Tadj):
        print("SKIP (has triangle):",name); return
    p=graphon_p9(m,Tadj,alpha)
    vals=M@p
    j=int(np.argmin(vals)); mv=float(vals[j])
    nneg=int((vals< -1e-9).sum())
    results.append((mv,mom_idx[j],name,nneg))
    print(f"[{time.time()-t0:.1f}s] {name}: worst row-value={mv:+.6e} at row {mom_idx[j]}  (#rows<-1e-9: {nneg})",flush=True)
    return mv

# cycles
for m in [5,7,9,11,13,15,17]:
    test(f"C{m}",m,cyc(m))
# Petersen
test("Petersen",10,petersen())
# complete bipartite (triangle-free)
for (a,b) in [(1,4),(2,3),(3,3),(2,5),(4,4),(3,6),(5,5)]:
    n,A=kbipart(a,b); test(f"K_{a},{b}",n,A)
# unbalanced C5 weights (the extremal direction)
for w,tag in [([0.3,0.2,0.2,0.15,0.15],"C5_skew1"),([0.4,0.15,0.15,0.15,0.15],"C5_skew2"),
              ([0.25,0.25,0.2,0.15,0.15],"C5_skew3")]:
    test(tag,5,cyc(5),w)
# small geng triangle-free graphs as equal-part step graphons (n=5,6,7)
for n0 in [5,6,7]:
    gs=fe.enumerate_graphs(n0,triangle_free=True)
    base=len(results)
    for ci,(n,A) in enumerate(gs):
        if not fe.is_triangle_free(n,A): continue
        p=graphon_p9(n,A)
        vals=M@p; j=int(np.argmin(vals))
        results.append((float(vals[j]),mom_idx[j],f"g{n0}#{ci}",int((vals<-1e-9).sum())))
    tail=results[base:]
    if tail:
        w=min(tail)
        print(f"[{time.time()-t0:.1f}s] geng n0={n0} ({len(gs)} graphs as step-graphons): worst={w[0]:+.6e} at row {w[1]} graph {w[2]}",flush=True)

results.sort()
print("\n=== WORST 20 (row, graphon) pairs ===")
for (mv,ri,nm,nn) in results[:20]:
    print(f"  value={mv:+.9e}  row={ri}  graphon={nm}  (#rows<-1e-9 for that graphon: {nn})")
print(f"\nGLOBAL WORST MARGIN (graphon test): {results[0][0]:+.9e} at row {results[0][1]} graphon {results[0][2]}")
print(f"[{time.time()-t0:.1f}s] DONE")
pickle.dump(results,open("_audit_graphon_results.pkl","wb"))
