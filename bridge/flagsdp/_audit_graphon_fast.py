#!/usr/bin/env python3
"""Fast targeted GRAPHON audit of cp_cache 317 moment rows. Same count-vector (with-repetition blow-up) density
as g1_graphon_density.py, but canon_label is memoized on the induced-graph adjacency key so repeated blow-up
shapes are canonicalized once. Covers the strong real triangle-free candidates: cycles C5..C13, Petersen,
complete bipartite, and skewed C5 weights (the extremal direction)."""
import os
os.environ.setdefault("OMP_NUM_THREADS","8")
import pickle, time
import numpy as np
from math import factorial
import flag_engine as fe
from compute_U8 import canon_label

t0=time.time()
ns,dedge,rows,provtypes,_=pickle.load(open("cp_cache.pkl","rb"))
def pk(p): return p[0] if isinstance(p,(list,tuple)) else p
mom_idx=[i for i in range(len(rows)) if pk(provtypes[i])=='moment']
M=np.stack([np.asarray(rows[i],float) for i in mom_idx])
keymap=pickle.load(open("_audit_keymap_cl.pkl","rb"))
print(f"[{time.time()-t0:.1f}s] {M.shape[0]} moment rows",flush=True)

_canon_memo={}
def state_idx(adjtuple):
    """adjtuple = the canonical bit-string of the blow-up graph from blowup9 (already lex from canon? no). Memoize
    on the raw adjacency tuple; compute canon_label once."""
    v=_canon_memo.get(adjtuple)
    if v is not None: return v
    n=len(adjtuple)
    A=list(adjtuple)
    idx=keymap.get(canon_label(n,A)[0])
    _canon_memo[adjtuple]=idx
    return idx

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
    return tuple(A)

def graphon_p9(m,Tadj,alpha=None):
    if alpha is None: alpha=[1.0/m]*m
    p=np.zeros(ns); f9=factorial(9)
    for counts in compositions(9,m):
        A=blowup9(counts,Tadj)
        idx=state_idx(A)
        if idx is None: raise RuntimeError("blowup state missing")
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
        print("SKIP triangle:",name); return
    p=graphon_p9(m,Tadj,alpha)
    vals=M@p; j=int(np.argmin(vals)); mv=float(vals[j])
    nneg=int((vals<-1e-9).sum())
    results.append((mv,mom_idx[j],name,nneg))
    print(f"[{time.time()-t0:.1f}s] {name}(d_edge={float(p@dedge):.4f}): worst={mv:+.4e} row {mom_idx[j]} #<-1e-9:{nneg}",flush=True)
    return mv

for m in [5,7,9,11,13]:
    test(f"C{m}",m,cyc(m))
test("Petersen",10,petersen())
for (a,b) in [(1,4),(2,3),(3,3),(2,5),(4,4),(3,4),(4,5)]:
    n,A=kbipart(a,b); test(f"K_{a},{b}",n,A)
for w,tag in [([0.3,0.2,0.2,0.15,0.15],"C5_skew1"),([0.4,0.15,0.15,0.15,0.15],"C5_skew2"),
              ([0.22,0.22,0.22,0.17,0.17],"C5_skew3"),([0.5,0.125,0.125,0.125,0.125],"C5_skew4")]:
    test(tag,5,cyc(5),w)
# random triangle-free graphons via geng n0=6 (all), as equal step graphons
gs=fe.enumerate_graphs(6,triangle_free=True)
base=len(results)
for ci,(n,A) in enumerate(gs):
    if not fe.is_triangle_free(n,A): continue
    p=graphon_p9(n,A); vals=M@p; j=int(np.argmin(vals))
    results.append((float(vals[j]),mom_idx[j],f"g6#{ci}",int((vals<-1e-9).sum())))
tail=results[base:]
if tail:
    w=min(tail); print(f"[{time.time()-t0:.1f}s] geng6 ({len(gs)} as graphons): worst={w[0]:+.4e} row {w[1]} {w[2]}",flush=True)

results.sort()
print("\n=== WORST 15 (graphon test) ===")
for (mv,ri,nm,nn) in results[:15]:
    print(f"  value={mv:+.6e}  row={ri}  graphon={nm}  #rows<-1e-9:{nn}")
print(f"\nGLOBAL WORST MARGIN (graphon): {results[0][0]:+.6e} at row {results[0][1]} graphon {results[0][2]}")
print(f"[{time.time()-t0:.1f}s] DONE; tested {len(results)} graphons; memo size {len(_canon_memo)}")
pickle.dump(results,open("_audit_graphon_fast_results.pkl","wb"))
