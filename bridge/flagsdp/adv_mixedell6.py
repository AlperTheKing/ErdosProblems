#!/usr/bin/env python3
"""Mixed-ell PART 6: the CRUX. Start from EXACTLY tight C5[q] (gamma=N^2). Inject mixed ell by
the smallest possible local edit. Measure resulting deficit and whether the SHORTEST-ell bad
edge still admits a safe peel (the lemma's worry: short geodesic entangled with longer ones).

Edits tested:
 (E1) subdivide ONE cross edge of C5[q] (adds 1 vertex, lengthens geodesics through it).
 (E2) attach a pendant C7-ear between two parts at cyclic-distance-2 (forces an ell=7 bad edge).
 (E3) within C5[q], reroute a single bad-edge endpoint through a length-2 detour.
For each: print exact gamma, n2, deficit, m, distinct geodesic lengths present, safe_peel.
"""
import sys
from peel_check import check_instance, gamma_of, bdistB, shortest_path_B

def add_edge(adj,u,v):
    if u!=v: adj[u].add(v); adj[v].add(u)
def del_edge(adj,u,v):
    adj[u].discard(v); adj[v].discard(u)

def C5q(q):
    n=5*q; vid=lambda i,j:i*q+j; adj=[set() for _ in range(n)]
    for i in range(5):
        for a in range(q):
            for b in range(q):
                add_edge(adj,vid(i,a),vid((i+1)%5,b))
    return n,adj,vid

def report(name,n,adj):
    r=check_instance(n,adj)
    ell_set=None
    if r.get("ok") and r.get("B_connected") and r.get("side") is not None:
        sd=r["side"]; G,M=gamma_of(n,adj,sd)
        ells=set()
        for (u,v) in M:
            P=shortest_path_B(n,adj,sd,u,v)
            if P: ells.add(len(P))
        ell_set=sorted(ells)
    G=r.get("gamma"); n2=r.get("n2")
    defc=(n2-G) if (G is not None and n2) else None
    print(f"{name}: N={r.get('N')} m={r.get('m')} gamma={G} n2={n2} deficit={defc} "
          f"tight={r.get('tight')} ells={ell_set} safe_peel={r.get('has_safe_peel')} | {r.get('detail','')[:50]}",flush=True)
    if r.get('tight') and r.get('has_safe_peel')==False:
        print("  *** OBSTRUCTION (tight + no peel) ***",flush=True)
    if not r.get("triangle_free"): print("  NOT TF",flush=True)
    return r

# E1: subdivide one cross edge (i0,a0)-(i0+1,b0) -> insert vertex w
def C5q_subdivide(q, i0=0,a0=0,b0=0):
    n,adj,vid=C5q(q)
    u=vid(i0,a0); v=vid((i0+1)%5,b0)
    if v not in adj[u]: return None
    del_edge(adj,u,v)
    w=len(adj); adj.append(set())
    add_edge(adj,u,w); add_edge(adj,w,v)
    return len(adj),adj

# E2: attach an ear of length earlen between part i0 and part i0+2 (cyclic distance 2)
def C5q_ear(q, earlen, i0=0):
    n,adj,vid=C5q(q)
    a=vid(i0,0); b=vid((i0+2)%5,0)
    prev=a; news=[]
    for _ in range(earlen-1):
        w=len(adj); adj.append(set()); add_edge(adj,prev,w); prev=w; news.append(w)
    add_edge(adj,prev,b)
    return len(adj),adj

# E3: reroute one part-0 vertex's links to part1 through a length-2 detour (2 new verts)
def C5q_detour(q):
    n,adj,vid=C5q(q)
    if q<1: return None
    w=vid(0,0); nb=[vid(1,b) for b in range(q)]
    for u in nb: del_edge(adj,w,u)
    x,y=len(adj),len(adj)+1; adj.append(set()); adj.append(set())
    add_edge(adj,w,x); add_edge(adj,x,y)
    for u in nb: add_edge(adj,y,u)
    return len(adj),adj

if __name__=="__main__":
    print("=== pure tight C5[q] baseline ===")
    for q in [2,3,4]:
        n,adj,_=C5q(q); report(f"C5[{q}] (pure tight)",n,adj)

    print("\n=== E1: subdivide ONE cross edge (minimal mixed-ell edit) ===")
    for q in [2,3,4]:
        res=C5q_subdivide(q)
        if res:
            n,adj=res
            if n<=24: report(f"C5[{q}] subdivide-1",n,adj)

    print("\n=== E2: C5[q] + ear length L between dist-2 parts ===")
    for q in [2,3]:
        for L in [3,4,5,6,7]:
            res=C5q_ear(q,L)
            if res:
                n,adj=res
                if n<=24: report(f"C5[{q}] ear(L={L})",n,adj)

    print("\n=== E3: C5[q] detour (reroute one vertex) ===")
    for q in [2,3,4]:
        res=C5q_detour(q)
        if res:
            n,adj=res
            if n<=24: report(f"C5[{q}] detour",n,adj)
