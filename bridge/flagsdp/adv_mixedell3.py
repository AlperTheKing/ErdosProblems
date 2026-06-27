#!/usr/bin/env python3
"""Mixed-ell PART 3: diagnose the m=2 'no safe peel' cases + hunt near-tight mixed-ell.

Two questions:
 (1) The 'two odd cycles sharing a vertex/part' m=2 cases have NO safe peel but are FAR from
     tight. Are they actually disguised odd-cycle base cases (each bad edge = a whole odd
     geodesic, no shorter structure to peel)? Diagnose WHY no peel: which condition fails
     for each bad edge.
 (2) Can any MIXED-ell instance be near-tight? Build a C5[q] (tight) and perturb minimally
     to lengthen exactly ONE bad-edge geodesic to 7 while keeping deficit small. Sweep.

We need keep=N-|C|<=22 for the brute CD check; keep N<=24.
"""
from peel_check import (check_instance, maxcut_all, Bconnected, gamma_of,
                        has_safe_peel, shortest_path_B, bdistB, cut_dom)

def add_edge(adj,u,v):
    if u!=v: adj[u].add(v); adj[v].add(u)

def Ckq(k,q):
    n=k*q; vid=lambda i,j:i*q+j; adj=[set() for _ in range(n)]
    for i in range(k):
        for a in range(q):
            for b in range(q):
                add_edge(adj,vid(i,a),vid((i+1)%k,b))
    return n,adj,vid

def two_blowups_share_part(k1,k2,q):
    n=k1*q+(k2-1)*q
    adj=[set() for _ in range(n)]
    def a_(i,j): return i*q+j
    def b_(i,j):
        if i==0: return j
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

# ---- DIAGNOSTIC: for a given instance, show per-bad-edge why peel fails ----
def diagnose(name,n,adj):
    r=check_instance(n,adj)
    if not (r.get("ok") and r.get("B_connected")):
        print(f"{name}: skip (ok={r.get('ok')} Bconn={r.get('B_connected')})"); return
    sd=r["side"]; G,M=gamma_of(n,adj,sd); NN=n
    print(f"\n--- {name}: N={n} m={len(M)} gamma={G} n2={n*n} bad-edges={M} ---")
    for (u,v) in M:
        P=shortest_path_B(n,adj,sd,u,v)
        if P is None:
            print(f"  edge {(u,v)}: NO B-path?!"); continue
        C=set(P); s=len(C); keep=[x for x in range(n) if x not in C]
        Mp=[(a,b) for (a,b) in M if a in keep and b in keep]
        Gp=0; conn_ok=True; disc=None
        for (a,b) in Mp:
            d=bdistB(n,adj,sd,a,banned=C).get(b,-1)
            if d<0: conn_ok=False; disc=(a,b); break
            Gp+=(d+1)**2
        L=G-Gp if conn_ok else None
        bound=2*s*NN-s*s
        if not conn_ok:
            print(f"  edge {(u,v)} |C|={s} geo={P}: (ii) FAILS bad edge {disc} disconnected after peel")
            continue
        if L>bound:
            print(f"  edge {(u,v)} |C|={s}: (iii) FAILS L={L} > bound={bound}")
            continue
        keepN=len(keep)
        if keepN>22:
            print(f"  edge {(u,v)} |C|={s}: keep={keepN}>22, CD not brute-checkable"); continue
        cd=cut_dom(keep,n,adj,sd,Mp)
        if cd is True:
            print(f"  edge {(u,v)} |C|={s}: SAFE PEEL (L={L}<=bound={bound}, CD ok)")
        else:
            print(f"  edge {(u,v)} |C|={s}: (i) CD FAILS L={L}<=bound={bound}")

if __name__=="__main__":
    # Diagnose the no-peel m=2 share-part cases
    n,adj=two_blowups_share_part(5,7,1); diagnose("C5||C7 share-part q=1",n,adj)
    n,adj=two_blowups_share_part(5,9,1); diagnose("C5||C9 share-part q=1",n,adj)
    n,adj=two_blowups_share_part(7,9,1); diagnose("C7||C9 share-part q=1",n,adj)
    n,adj=two_blowups_share_part(5,7,2); diagnose("C5||C7 share-part q=2",n,adj)

    # Also diagnose the two-cycles-share-vertex C5+C7 (N=11)
    def two_cycles_share_vertex(k1,k2):
        n1=2*k1+1; n2=2*k2+1; n=n1+n2-1
        adj=[set() for _ in range(n)]
        A=list(range(n1))
        for i in range(n1): add_edge(adj,A[i],A[(i+1)%n1])
        B=[0]+list(range(n1,n1+n2-1))
        for i in range(n2): add_edge(adj,B[i],B[(i+1)%n2])
        return n,adj
    n,adj=two_cycles_share_vertex(2,3); diagnose("C5+C7 @vertex",n,adj)
