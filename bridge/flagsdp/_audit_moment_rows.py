#!/usr/bin/env python3
"""AUDIT (corrected): the 317 'moment' rows R of cp_cache.pkl impose R.(D q)>=0 in the LP, where D is the
order-10 -> order-9 vertex-deletion marginal and q ranges over the order-10 triangle-free simplex. So the
SOUND condition is: for every real triangle-free graphon W, its order-9 induced density p_W (which must be
order-10-extendable) satisfies R.p_W >= 0. A real triangle-free graph on n0>=10 vertices yields an order-9
density p_G = (#9-subsets canon==state k)/C(n0,9) that is automatically order-10-extendable (it is the 9-marginal
of G's own order-10 distribution). We test such graphs (exhaustive n0=10,11; named C11,C13,Petersen+blowups)
and report R.p_G for all 317 rows; the single most-negative (row,graph) pair is the worst margin.
A materially negative value => that moment row is UNSOUND (cuts off a real triangle-free graph)."""
import os
os.environ.setdefault("OMP_NUM_THREADS","8")
import pickle, itertools, time, sys
import numpy as np
import flag_engine as fe
from compute_U8 import canon_label
from math import comb

t0=time.time()
ns,dedge,rows,provtypes,_=pickle.load(open("cp_cache.pkl","rb"))
def pkind(p): return p[0] if isinstance(p,(list,tuple)) else p
mom_idx=[i for i in range(len(rows)) if pkind(provtypes[i])=='moment']
M=np.stack([np.asarray(rows[i],dtype=float) for i in mom_idx])   # (317, 1897)
NS=ns
keymap=pickle.load(open("_audit_keymap_cl.pkl","rb"))
print(f"[{time.time()-t0:.1f}s] {M.shape[0]} moment rows, dim {M.shape[1]}",flush=True)

def order9_dist_exact(n0,A):
    p=np.zeros(NS)
    C=comb(n0,9)
    for verts in itertools.combinations(range(n0),9):
        kk,B=fe.induced(A,list(verts))
        idx=keymap.get(canon_label(9,B)[0])
        if idx is None:
            raise RuntimeError("subgraph state missing")
        p[idx]+=1
    return p/C

results=[]
def test(name,n0,A):
    if n0<9 or not fe.is_triangle_free(n0,A): return
    p=order9_dist_exact(n0,A)
    vals=M@p
    j=int(np.argmin(vals))
    results.append((float(vals[j]),mom_idx[j],name))

# named graphs (>=10 vertices) + cycle blowups
def cycle(n):
    A=[0]*n
    for i in range(n):
        j=(i+1)%n; A[i]|=1<<j; A[j]|=1<<i
    return n,A
def petersen():
    n=10; A=[0]*n
    def e(a,b): A[a]|=1<<b; A[b]|=1<<a
    for i in range(5):
        e(i,(i+1)%5); e(5+i,5+((i+2)%5)); e(i,5+i)
    return n,A
def blowup(n0,A0,mult):
    """replace each vertex by `mult[v]` independent copies (independent set, same external adjacency)."""
    parts=[]; off=[]; c=0
    for v in range(n0):
        off.append(c); c+=mult[v]
    N=c; B=[0]*N
    for u in range(n0):
        for w in range(n0):
            if (A0[u]>>w)&1:
                for a in range(off[u],off[u]+mult[u]):
                    for b in range(off[w],off[w]+mult[w]):
                        B[a]|=1<<b
    return N,B

named=[("C11",)+cycle(11),("C13",)+cycle(13),("Petersen",)+petersen()]
# blow-ups of C5 (the tight extremal) to 10,11,12,13,15 vertices, balanced & skewed
for mult,tag in [([2,2,2,2,2],"C5x2_n10"),([3,2,2,2,2],"C5_32222_n11"),
                 ([3,3,2,2,2],"C5_33222_n12"),([3,3,3,2,2],"C5_33322_n13"),
                 ([3,3,3,3,3],"C5x3_n15"),([4,3,3,3,2],"C5_43332_n15")]:
    named.append((tag,)+blowup(5,cycle(5)[1],mult))
# blow-ups of C7
for mult,tag in [([2,2,2,2,2,1,1],"C7bl_n11"),([2,2,2,1,1,1,1],"C7bl_n10")]:
    named.append((tag,)+blowup(7,cycle(7)[1],mult))
# Petersen with one doubled vertex (n=11)
pn,pA=petersen()
named.append(("Petersen+1",)+blowup(10,pA,[2,1,1,1,1,1,1,1,1,1]))

for (name,n0,A) in named:
    test(name,n0,A)
    if results:
        m,ri,nm=results[-1]
        print(f"[{time.time()-t0:.1f}s] {name} (n0={n0}) worst row-value={m:+.6e} at row {ri}",flush=True)

# exhaustive n0=10 then n0=11 (geng -t)
for n0 in [10,11]:
    gs=fe.enumerate_graphs(n0,triangle_free=True)
    print(f"[{time.time()-t0:.1f}s] n0={n0}: {len(gs)} triangle-free graphs to test...",flush=True)
    base=len(results)
    for ci,(n,A) in enumerate(gs):
        test(f"n{n0}#{ci}",n0,A)
    tail=results[base:]
    if tail:
        w=min(tail)
        print(f"[{time.time()-t0:.1f}s] n0={n0} DONE: worst over class = {w[0]:+.6e} at row {w[1]} graph {w[2]}",flush=True)

results.sort()
print("\n=== WORST 20 (row,graph) pairs (most negative first) ===")
for (m,ri,nm) in results[:20]:
    print(f"  value={m:+.9e}  moment_row_idx={ri}  graph={nm}")
print(f"\nGLOBAL WORST MARGIN: {results[0][0]:+.9e} at moment_row_idx={results[0][1]} graph={results[0][2]}")
print(f"[{time.time()-t0:.1f}s] DONE; tested {len(results)} graphs")
pickle.dump(results, open("_audit_moment_results.pkl","wb"))
