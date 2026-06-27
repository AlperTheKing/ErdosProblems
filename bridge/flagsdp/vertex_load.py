#!/usr/bin/env python3
"""Compute the VERTEX-LOAD traces GPT needs for the OVD proof (the missing multicommodity/flow theorem).
For each bad edge e=xy, a shortest B-geodesic cycle C_e (vertex set = shortest B-path x..y); h_e=ell(e)=|C_e|.
T(v) = sum_{e: v in C_e} h_e. Identity: sum_v T(v) = sum_e h_e^2 = Gamma. C5[q]: T(v)=N for all v.
VERTEX-LOAD THEOREM (to test): exists a choice of one shortest cycle per bad edge with
   max_v T(v) <= N + (N^2 - Gamma).
Compare CANONICAL (first BFS path) vs GREEDY-BALANCED (assign each e's cycle to minimize running max T(v))."""
import sys
from collections import deque
from mycielskian_check import mycielskian, edges_of, gamma_min_cut, all_shortest_geos

def trace(name, N, adj, side, G, M):
    NN=N; bound=NN+(NN*NN-G)
    # all shortest cycles per bad edge
    cyc={}
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v)
        cyc[(u,v)]=geos   # each is a vertex list (the path = cycle vertex set)
    h={e:len(geos[0]) for e,geos in cyc.items()}
    # CANONICAL: first geodesic
    Tc=[0]*N
    for e,geos in cyc.items():
        for w in geos[0]: Tc[w]+=h[e]
    # GREEDY-BALANCED: process bad edges (longest h first), pick the geodesic minimizing the resulting max load
    Tg=[0]*N
    for e in sorted(cyc, key=lambda e:-h[e]):
        best=None
        for C in cyc[e]:
            mx=max(Tg[w]+h[e] for w in C)
            if best is None or mx<best[0]: best=(mx,C)
        for w in best[1]: Tg[w]+=h[e]
    sumT=sum(Tc)
    print(f"\n=== {name}: N={N} beta={len(M)} Gamma={G} N^2={NN*NN} deficit={NN*NN-G} | bound N+(N^2-Gamma)={bound} ===")
    print(f"    identity sum_v T(v)={sumT} == Gamma={G}? {sumT==G}")
    print(f"    CANONICAL: max_v T(v)={max(Tc)}  (<= bound {bound}? {max(Tc)<=bound})   load distn min/max=({min(Tc)},{max(Tc)})")
    print(f"    GREEDY-BAL: max_v T(v)={max(Tg)}  (<= bound {bound}? {max(Tg)<=bound})   load distn min/max=({min(Tg)},{max(Tg)})")

def run_C5q(q):
    n=5*q; vid=lambda i,j:i*q+j; side=[0]*n; adj=[set() for _ in range(n)]
    for i in range(5):
        for j in range(q): side[vid(i,j)]=(0 if i in (0,2,4) else 1)
    for i in range(5):
        for a in range(q):
            for b in range(q):
                u=vid(i,a); v=vid((i+1)%5,b); adj[u].add(v); adj[v].add(u)
    M=[(vid(4,a),vid(0,b)) for a in range(q) for b in range(q)]
    G=sum(25 for _ in M)
    trace(f"C5[{q}]", n, adj, side, M and G, M) if False else trace(f"C5[{q}]", n, adj, side, G, M)

def decode_g6(s):
    data=[ord(c)-63 for c in s]; n=data[0]; bits=[]
    for d in data[1:]:
        for k in range(5,-1,-1): bits.append((d>>k)&1)
    adj=[set() for _ in range(n)]; idx=0
    for j in range(1,n):
        for i in range(j):
            if idx<len(bits) and bits[idx]: adj[i].add(j); adj[j].add(i)
            idx+=1
    return n,adj

if __name__=="__main__":
    w=sys.argv[1] if len(sys.argv)>1 else "small"
    if w in ("small","all"):
        for q in (2,3,4): run_C5q(q)
        n,adj=decode_g6("G?`F`w"); res,mc=gamma_min_cut(n,[set(a) for a in adj],edges_of([set(a) for a in adj]))
        side,G,M=res; trace("n8 band-max", n,[set(a) for a in adj],side,G,M)
    if w in ("pet","all"):
        pet=[set() for _ in range(10)]
        for i in range(5):
            for (a,b) in [(i,(i+1)%5),(5+i,5+(i+2)%5),(i,5+i)]: pet[a].add(b); pet[b].add(a)
        N,adj=mycielskian(10,edges_of(pet)); res,mc=gamma_min_cut(N,adj,edges_of(adj)); side,G,M=res
        trace("M(Petersen)", N,adj,side,G,M)
    if w in ("grot","all"):
        C5e=[(i,(i+1)%5) for i in range(5)]; gN,gadj=mycielskian(5,C5e)
        N,adj=mycielskian(11,edges_of(gadj)); res,mc=gamma_min_cut(N,adj,edges_of(adj)); side,G,M=res
        trace("M(Grotzsch)", N,adj,side,G,M)
    print("\nDONE")
