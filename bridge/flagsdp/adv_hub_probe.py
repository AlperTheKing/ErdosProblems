"""Adversarial: try to over-concentrate uniform betweenness on a single hub vertex.
Strategy: long odd-cycle blowups C9[q], C11[q] (h=9,11) + asymmetric blowups where
one part is fat (acts as a hub many geodesics pass through). Check T<=K under the
min-Gamma max cut. Also test the 'bowtie of odd cycles' sharing a vertex."""
import numpy as np
from mycielskian_check import all_shortest_geos, gamma_of, Bconnected, edges_of, maxcut_value

def load_uniform(N,adj,side,M):
    T=np.zeros(N)
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v)
        if not geos: return None
        w=1.0/len(geos); h=len(geos[0])
        for P in geos:
            for x in P: T[x]+=h*w
    return T

def Cm_blowup(m, sizes):
    parts=[]; off=0
    for s in sizes: parts.append(list(range(off,off+s))); off+=s
    n=off; adj=[set() for _ in range(n)]
    for i in range(m):
        for a in parts[i]:
            for b in parts[(i+1)%m]:
                adj[a].add(b); adj[b].add(a)
    return n,adj,parts

def best_cut(n,adj,cap=20000):
    E=edges_of(adj); mc=maxcut_value(n,E); best=None; cnt=0
    for mask in range(1<<(n-1)):
        c=sum(1 for (u,v) in E if ((mask>>u)&1)!=((mask>>v)&1))
        if c!=mc: continue
        side=[(mask>>u)&1 for u in range(n)]
        if not Bconnected(n,adj,side): continue
        G,M=gamma_of(n,adj,side)
        if G is None or not M: continue
        cnt+=1
        if best is None or G<best[1]: best=(side,G,M)
        if cnt>=cap: break
    return best

def report(name,n,adj):
    r=best_cut(n,adj)
    if r is None: print(f"{name} N={n}: no valid cut"); return
    side,G,M=r; T=load_uniform(n,adj,side,M)
    if T is None: print(f"{name} N={n}: routing failed"); return
    K=n+(n*n-G); gap=T.max()-K
    flag="VIOLATION!!!" if gap>1e-9 else ("TIGHT" if abs(gap)<1e-9 else "ok")
    print(f"{name} N={n} Gamma={G} beta={len(M)} K={K} maxT={T.max():.4f} gap={gap:+.4f} {flag}")

print("=== long odd cycle blowups (h>=9): equal parts ===")
for m in (9,11):
    for q in (1,2):
        if m*q>20: continue
        n,adj,_=Cm_blowup(m,[q]*m); report(f"C{m}[{q}]",n,adj)

print("=== asymmetric C9/C7: one fat hub part ===")
for m,sizes in [(7,[3,1,1,1,1,1,1]),(7,[1,1,1,3,1,1,1]),(9,[2,1,1,1,1,1,1,1,1]),(9,[1,1,1,1,2,1,1,1,1]),(7,[2,2,1,1,1,1,1])]:
    n,adj,_=Cm_blowup(m,sizes); report(f"C{m}{sizes}",n,adj)
