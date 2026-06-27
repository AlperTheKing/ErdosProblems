#!/usr/bin/env python3
"""Mixed-ell-glue PART 2: push toward TIGHT (gamma=N^2) with mixed geodesic lengths.

The tight extremal family is C5[q] (all ell=5). To get gamma close to N^2 we need DENSE
blow-up structure, not sparse cycles. Strategy: take a C5[q] blow-up (tight) and locally
PERTURB it to inject a longer bad edge (ell=7) while keeping most of the dense block tight.
Also: C7[q] blow-ups (all ell=7) glued to C5[q'] sharing a transversal.

Diagnose the share-vertex 'no safe peel' cases too.
"""
from peel_check import (check_instance, maxcut_all, Bconnected, gamma_of,
                        has_safe_peel, shortest_path_B, bdistB, cut_dom)

RESULTS=[]
def run(name,n,adj,side=None,verbose=False):
    r=check_instance(n,adj,side=side)
    tag=""
    if r.get("ok") and r.get("triangle_free") and r.get("B_connected") and r.get("m",0)>=2:
        if r.get("tight") and r.get("has_safe_peel")==False:
            tag=" <<< OBSTRUCTION (tight,no-peel)"
        elif r.get("gamma") is not None and r.get("n2"):
            defc=r["n2"]-r["gamma"]
            if r.get("has_safe_peel")==False:
                tag=f" <<< NO SAFE PEEL deficit={defc}"
            elif defc<=3*r["N"]:
                tag=f" [near-tight deficit={defc} safe={r.get('has_safe_peel')}]"
    print(f"{name}: N={r.get('N')} m={r.get('m')} gamma={r.get('gamma')} n2={r.get('n2')} "
          f"tight={r.get('tight')} safe_peel={r.get('has_safe_peel')}{tag}")
    if not r.get("triangle_free"): print("    NOT TF")
    RESULTS.append((name,r,tag))
    return r

def add_edge(adj,u,v):
    if u!=v: adj[u].add(v); adj[v].add(u)

def C5q(q):
    n=5*q; vid=lambda i,j:i*q+j; adj=[set() for _ in range(n)]
    for i in range(5):
        for a in range(q):
            for b in range(q):
                add_edge(adj,vid(i,a),vid((i+1)%5,b))
    return n,adj,vid

def Ckq(k,q):
    """C_k[q] blow-up: k parts of size q in a k-cycle of complete bipartite links."""
    n=k*q; vid=lambda i,j:i*q+j; adj=[set() for _ in range(n)]
    for i in range(k):
        for a in range(q):
            for b in range(q):
                add_edge(adj,vid(i,a),vid((i+1)%k,b))
    return n,adj,vid

# ---- A. C5[q] with one DENSE part split to inject a longer bad edge -----
# Take C5[q]; add a single extra vertex w attached so that it creates a bad edge of ell=7
# routed the long way around, while the dense block stays tight.
def C5q_extra_longchord(q):
    n0,adj,vid=C5q(q)
    # add 2 fresh vertices forming a detour between part0 and part0 (a longer mono path)
    base=len(adj)
    w1,w2=base,base+1
    adj.append(set()); adj.append(set())
    # connect w1-w2-... to two part-0 vertices via a length-going-the-long-way path
    # attach w1 to a part-1 vertex and w2 to a part-4 vertex (both neighbors of part0)
    add_edge(adj,w1,vid(1,0))
    add_edge(adj,w1,w2)
    add_edge(adj,w2,vid(4,0))
    return len(adj),adj

# ---- B. C7[q] blow-ups (all ell=7) and gluing C5[q]||C7[q'] on transversal ----
# Glue: identify one part of C5[q] with one part of C7[q] (shared q vertices), keeping TF.
def glue_C5_C7_share_part(q):
    # C5 parts 0..4 (each size q), C7 parts 0..6 (each size q).
    # Identify C5.part0 == C7.part0 (the shared q vertices). Need triangle-free:
    # shared part's neighbors are C5.part1,C5.part4,C7.part1,C7.part6. Triangle iff two of
    # those neighbor-sets are adjacent. They're separate parts => no edges among them => TF ok
    # provided we don't create odd short links. Bipartite-consistency: shared part must be one
    # color; its 4 neighbor-parts the other color; fine.
    q5,adj5,v5=Ckq(5,q)
    q7,adj7,v7=Ckq(7,q)
    # relabel: shared part = 0..q-1. C5 other parts: q..5q-1. C7 other parts: 5q..
    n=5*q+6*q  # shared(q) + C5 parts1-4 (4q) + C7 parts1-6 (6q) = q+4q+6q=11q
    adj=[set() for _ in range(n)]
    # index maps
    def c5(i,j):
        if i==0: return j
        return q + (i-1)*q + j     # parts1..4 -> q..5q-1
    def c7(i,j):
        if i==0: return j
        return 5*q + (i-1)*q + j   # parts1..6 -> 5q..11q-1
    for i in range(5):
        for a in range(q):
            for b in range(q):
                add_edge(adj,c5(i,a),c5((i+1)%5,b))
    for i in range(7):
        for a in range(q):
            for b in range(q):
                add_edge(adj,c7(i,a),c7((i+1)%7,b))
    return n,adj

# ---- C. share an EDGE/transversal path between C5[q] and C7[q] ----------
# Two blow-ups sharing a single transversal edge's endpoints (two adjacent parts overlap by 1 each)
def glue_C5_C7_share_two_verts(q):
    # share C5.part0[0] and C5.part1[0] with C7.part0[0],C7.part1[0]
    q5,adj5,v5=Ckq(5,q); q7,adj7,v7=Ckq(7,q)
    off=5*q
    n=5*q+7*q
    adj=[set() for _ in range(n)]
    for i in range(5):
        for a in range(q):
            for b in range(q):
                add_edge(adj,v5(i,a),v5((i+1)%5,b))
    for i in range(7):
        for a in range(q):
            for b in range(q):
                add_edge(adj,off+v7(i,a),off+v7((i+1)%7,b))
    # identify by merging: redirect C7.part0[0]->C5.part0[0], C7.part1[0]->C5.part1[0]
    merges={off+v7(0,0):v5(0,0), off+v7(1,0):v5(1,0)}
    # rebuild with merges
    def m(x): return merges.get(x,x)
    adj2=[set() for _ in range(n)]
    for u in range(n):
        for w in adj[u]:
            add_edge(adj2,m(u),m(w))
    # remove now-isolated merged-away vertices by leaving them isolated (harness handles? they break B_conn)
    # Instead compress: drop the two dead vertices
    dead=set(merges.keys())
    keep=[x for x in range(n) if x not in dead]
    idx={x:i for i,x in enumerate(keep)}
    adj3=[set() for _ in keep]
    for u in keep:
        for w in adj2[u]:
            if w in idx: add_edge(adj3,idx[u],idx[w])
    return len(keep),adj3

# ---- D. odd cycles sharing a vertex but BLOWN UP (dense -> tight-ish) ----
def two_blowups_share_part(k1,k2,q):
    qa,adja,va=Ckq(k1,q); qb,adjb,vb=Ckq(k2,q)
    # identify part0 of each (q shared verts)
    n=k1*q+ (k2-1)*q
    adj=[set() for _ in range(n)]
    def a_(i,j): return i*q+j                      # k1 blowup uses 0..k1*q-1
    def b_(i,j):
        if i==0: return j                          # shared part
        return k1*q+(i-1)*q+j
    for i in range(k1):
        for a in range(q):
            for b in range(q):
                add_edge(adj,a_(i,a),a_((i+1)%k1,b))
    for i in range(k2):
        for a in range(q):
            for b in range(q):
                add_edge(adj,b_(i,a),b_((i+1)%k2,b))
    return n,adj

if __name__=="__main__":
    print("=== A. C5[q] + long-chord detour (inject ell=7 into tight block) ===")
    for q in [2,3,4]:
        n,adj=C5q_extra_longchord(q)
        if n<=26: run(f"C5[{q}]+longchord",n,adj)

    print("\n=== B. C5[q] || C7[q] sharing a full part (mixed ell, both dense) ===")
    for q in [1,2]:
        n,adj=glue_C5_C7_share_part(q)
        if n<=26: run(f"C5||C7 share-part q={q}",n,adj)

    print("\n=== C. C5[q] || C7[q] sharing two transversal verts ===")
    for q in [1,2]:
        n,adj=glue_C5_C7_share_two_verts(q)
        if n<=26: run(f"C5||C7 share-2v q={q}",n,adj)

    print("\n=== D. C_{k1}[q] || C_{k2}[q] sharing a part (blown-up figure-eight) ===")
    for (k1,k2) in [(5,7),(5,9),(7,9),(3,5),(3,7)]:
        for q in [1,2]:
            n,adj=two_blowups_share_part(k1,k2,q)
            if n<=26: run(f"C{k1}[q]||C{k2}[q] share-part q={q}",n,adj)

    print("\n=== SUMMARY ===")
    obstr=[x for x in RESULTS if "OBSTRUCTION" in x[2]]
    nopeel=[x for x in RESULTS if "NO SAFE PEEL" in x[2]]
    print(f"tested={len(RESULTS)} obstructions={len(obstr)} no-peel={len(nopeel)}")
    for nm,r,tg in obstr: print("  OBSTR:",nm,r.get("N"),r.get("m"),r.get("gamma"),r.get("n2"))
    for nm,r,tg in nopeel: print("  NOPEEL:",nm,r.get("N"),r.get("m"),"gamma",r.get("gamma"),"n2",r.get("n2"))
