#!/usr/bin/env python3
"""Cross-check: for a real triangle-free graph G, does D @ q_G (LP pipeline order-9 vector) equal my directly
computed order-9 induced distribution p_G in the cp_cache state basis? D = order-10->9 vertex-deletion marginal.
q_G = G's order-10 induced distribution over T_10 (the c5lift J-basis). If they match, then rows.p_G is EXACTLY
the LP constraint mom_q.q evaluated on the real graph G, validating the audit."""
import numpy as np, pickle, itertools
from math import comb
from scipy.sparse import csr_matrix
import flag_engine as fe
from compute_U8 import canon_label
# rebuild the SAME key9 perfect hash and g10 ordering c5_lift_diag uses for D's columns
from c5_lift_diag import key9

ns,dedge,rows,provtypes,_=pickle.load(open("cp_cache.pkl","rb"))
C=pickle.load(open("cache_n9.pkl","rb")); states9=C["states"]
d=np.load("c5lift_cache.npz",allow_pickle=True)
nJ=int(d["nJ"]); D=csr_matrix((d["Dval"],(d["Drow"],d["Dcol"])),shape=(ns,nJ))

# g10 in the SAME order build() used (enumerate_graphs(10) order = column order of D)
g10=fe.enumerate_graphs(10,triangle_free=True)
assert len(g10)==nJ, f"{len(g10)} vs {nJ}"
# column j of D = g10[j]; identify T_10 subgraphs by canon_label (injective on T_10, verified)
key10={ canon_label(n,A)[0]: j for j,(n,A) in enumerate(g10) }
assert len(key10)==nJ

# my order-9 state basis map (canon_label)
keymap9=pickle.load(open("_audit_keymap_cl.pkl","rb"))

def q10_of_graph(n0,A):
    """order-10 induced distribution of G over the g10 column basis (via key9 perfect hash)."""
    q=np.zeros(nJ); C10=comb(n0,10)
    for verts in itertools.combinations(range(n0),10):
        kk,B=fe.induced(A,list(verts))
        j=key10.get(canon_label(10,B)[0])
        if j is None: raise RuntimeError("order-10 subgraph not found in T_10")
        q[j]+=1
    return q/C10

def p9_of_graph(n0,A):
    p=np.zeros(ns); C9=comb(n0,9)
    for verts in itertools.combinations(range(n0),9):
        kk,B=fe.induced(A,list(verts))
        idx=keymap9.get(canon_label(9,B)[0]); p[idx]+=1
    return p/C9

def cyc(n):
    A=[0]*n
    for i in range(n):
        j=(i+1)%n; A[i]|=1<<j; A[j]|=1<<i
    return n,A
def blowup(n0,A0,mult):
    off=[];c=0
    for v in range(n0): off.append(c); c+=mult[v]
    N=c;B=[0]*N
    for u in range(n0):
        for w in range(n0):
            if (A0[u]>>w)&1:
                for a in range(off[u],off[u]+mult[u]):
                    for b in range(off[w],off[w]+mult[w]): B[a]|=1<<b
    return N,B

tests=[("C11",)+cyc(11), ("C5x2_n10",)+blowup(5,cyc(5)[1],[2,2,2,2,2]),
       ("C5_33222_n12",)+blowup(5,cyc(5)[1],[3,3,2,2,2])]
for (name,n0,A) in tests:
    q=q10_of_graph(n0,A)
    pdir=p9_of_graph(n0,A)
    pviaD=np.asarray(D@q).ravel()
    err=np.abs(pdir-pviaD).max()
    print(f"{name}: ||p_direct - D q_G||_inf = {err:.3e}  (sum p_dir={pdir.sum():.6f}, sum Dq={pviaD.sum():.6f})")
    # row-value comparison on the worst row 64/126
    def pk(p): return p[0] if isinstance(p,(list,tuple)) else p
    momset=[i for i in range(len(rows)) if pk(provtypes[i])=='moment']
    for ri in [64,126,91,398]:
        r=np.asarray(rows[ri],float)
        print(f"    row{ri}: r.p_dir={r@pdir:+.6e}  r.(Dq)={r@pviaD:+.6e}")
print("DONE")
