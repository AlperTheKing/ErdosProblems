#!/usr/bin/env python3
"""Diagnostic: for a given instance, report PER-BAD-EDGE which safe-peel condition fails.
Targets the 'cut-tight pocket' danger: can (i) CD-on-remainder ever be the binding failure
at a near-tight ratio? Replays peel logic with condition tracing."""
from peel_check import (check_instance, gamma_of, Bconnected, maxcut_all,
                        bdistB, shortest_path_B, cut_dom)

def add(adj,u,v):
    adj[u].add(v); adj[v].add(u)

def trace_peels(n, adj, side):
    G,M = gamma_of(n,adj,side)
    print(f"  Gamma={G} N^2={n*n} m={len(M)} bad edges M={M}")
    for (u,v) in M:
        P=shortest_path_B(n,adj,side,u,v)
        if P is None:
            print(f"    edge {(u,v)}: NO B-path"); continue
        C=set(P); s=len(C); keep=[x for x in range(n) if x not in C]
        if not keep:
            print(f"    edge {(u,v)}: |C|={s} peels everything"); continue
        Mp=[(a,b) for (a,b) in M if a in keep and b in keep]
        Gp=0; conn_ok=True
        for (a,b) in Mp:
            d=bdistB(n,adj,side,a,banned=C).get(b,-1)
            if d<0: conn_ok=False; break
            Gp+=(d+1)**2
        cond=[]
        if not conn_ok: cond.append("(ii)DISC")
        else:
            L=G-Gp; bound=2*s*n-s*s
            if L>bound: cond.append(f"(iii)L={L}>bound={bound}")
            cd=cut_dom(keep,n,adj,side,Mp)
            if cd is None: cond.append("(keep>22)")
            elif cd is False: cond.append("(i)CDfail")
            if not cond: cond.append(f"SAFE L={L}<=bound={bound}")
        print(f"    edge {(u,v)}: |C|={s} path={P} -> {' '.join(cond)}")

def diag(tag,n,adj,side=None):
    r=check_instance(n,adj,side=side)
    print(f"{tag}: N={r.get('N')} m={r.get('m')} g={r.get('gamma')} ratio="
          f"{(r.get('gamma')/r.get('n2')) if r.get('gamma') else None} sp={r.get('has_safe_peel')} ge_n2={r.get('ge_n2')}")
    if r.get('ok') and r.get('B_connected') and r.get('m',0)>=2:
        trace_peels(n,adj,r['side'])
    return r

# C5q
def C5q(q):
    n=5*q; adj=[set() for _ in range(n)]
    def V(i,a): return i*q+a
    for i in range(5):
        for a in range(q):
            for b in range(q):
                add(adj,V(i,a),V((i+1)%5,b))
    return n,adj

def oddcycle_blowup(sizes):
    k=len(sizes); starts=[0]
    for s in sizes: starts.append(starts[-1]+s)
    n=starts[-1]; adj=[set() for _ in range(n)]
    def part(i): return range(starts[i], starts[i+1])
    for i in range(k):
        j=(i+1)%k
        for u in part(i):
            for v in part(j):
                add(adj,u,v)
    return n,adj

if __name__=="__main__":
    print("### tight C5[3] -- confirm L=bound exactly on every peel ###")
    n,adj=C5q(3); diag("C5[3]",n,adj)
    print("### tight C7[2] ###")
    n,adj=oddcycle_blowup([2]*7); diag("C7[2]",n,adj)
    print("### tight C9[2] ###")
    n,adj=oddcycle_blowup([2]*9); diag("C9[2]",n,adj)
    print("### near-tight C5[4]-minus-one-cross-edge ###")
    n,adj=C5q(4)
    # delete one cross edge in link part0-part1
    adj[0].discard(4); adj[4].discard(0)  # V(0,0)=0, V(1,0)=4 with q=4
    diag("C5[4]-del1",n,adj)
