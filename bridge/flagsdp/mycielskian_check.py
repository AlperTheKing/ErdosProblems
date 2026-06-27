#!/usr/bin/env python3
"""Step-1's [15:11Z] action: verify the R2 master inequality Gamma+D*<=N^2 (and local D(C)<=N^2-Gamma) on the
high-chromatic band extremizers M(Petersen) [N=21] and M(Grotzsch) [N=23] (beta/e>1/5, the graphs that kill
GPT's (Q) a=1/5), and report whether my mass bound L<=2|C|N-|C|^2 is TIGHT or strictly SLACK on them.
If slack on these high-chromatic graphs while tight on C5[q] => the d_edge=2/5 pinning the graphon a-term lacks."""
import sys
from collections import deque

def bdistB(n,adj,side,src,banned=None):
    banned=banned or set(); d={src:0}; q=deque([src])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in banned and v not in d: d[v]=d[u]+1; q.append(v)
    return d

def Bconnected(n,adj,side):
    seen={0}; q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in seen: seen.add(v); q.append(v)
    return len(seen)==n

def mycielskian(n, edges):
    """M(G): 0..n-1 originals, n..2n-1 shadows (shadow n+u ~ neighbors of u), 2n apex ~ all shadows."""
    N=2*n+1; adj=[set() for _ in range(N)]
    nbr=[set() for _ in range(n)]
    for (u,v) in edges: nbr[u].add(v); nbr[v].add(u); adj[u].add(v); adj[v].add(u)
    for u in range(n):
        for v in nbr[u]:
            adj[n+u].add(v); adj[v].add(n+u)   # shadow u ~ each neighbor v of u
    for u in range(n):
        adj[2*n].add(n+u); adj[n+u].add(2*n)   # apex ~ all shadows
    return N, adj

def edges_of(adj):
    n=len(adj); return [(u,v) for u in range(n) for v in adj[u] if v>u]

def maxcut_value(n, E):
    best=-1
    for mask in range(1<<(n-1)):
        c=0
        for (u,v) in E:
            if ((mask>>u)&1)!=((mask>>v)&1): c+=1
        if c>best: best=c
    return best

def gamma_of(n,adj,side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    G=0
    for (u,v) in M:
        d=bdistB(n,adj,side,u).get(v,-1)
        if d<0: return None,M
        G+=(d+1)**2
    return G,M

def gamma_min_cut(n, adj, E, cap=4000):
    mc=maxcut_value(n,E); best=None; cnt=0
    for mask in range(1<<(n-1)):
        c=0
        for (u,v) in E:
            if ((mask>>u)&1)!=((mask>>v)&1): c+=1
        if c!=mc: continue
        side=[(mask>>u)&1 for u in range(n)]
        if not Bconnected(n,adj,side): continue
        G,M=gamma_of(n,adj,side)
        if G is None: continue
        cnt+=1
        if best is None or G<best[1]: best=(side,G,M)
        if cnt>=cap: break
    return best,mc

def all_shortest_geos(n,adj,side,s,t):
    dist={s:0}; pred={s:[]}; layer=[s]
    while layer:
        nxt=[]
        for u in layer:
            for v in adj[u]:
                if side[u]!=side[v]:
                    if v not in dist: dist[v]=dist[u]+1; pred[v]=[u]; nxt.append(v)
                    elif dist[v]==dist[u]+1: pred[v].append(u)
        layer=nxt
    if t not in dist: return []
    out=[]
    def rec(v,acc):
        if v==s: out.append([s]+acc[::-1]); return
        for p in pred[v]: rec(p,acc+[v])
    rec(t,[]); return out

def D_of(n,adj,side,M,C):
    Cset=set(C); K=[v for v in range(n) if v not in Cset]; idx={v:i for i,v in enumerate(K)}; m=len(K); kset=set(K)
    if m>24: return None
    Be=[(u,v) for u in K for v in adj[u] if v>u and v in kset and side[u]!=side[v]]
    Mp=[(a,b) for (a,b) in M if a in kset and b in kset]
    best=0
    for mask in range(1<<m):
        dM=sum(1 for (u,v) in Mp if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        dB=sum(1 for (u,v) in Be if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        if dM-dB>best: best=dM-dB
    return best

def analyze(name, N, adj):
    E=edges_of(adj); e=len(E)
    res,mc=gamma_min_cut(N,adj,E)
    if res is None: print(f"{name}: no connected-B max cut w/ finite Gamma"); return
    side,G,M=res; beta=len(M)
    print(f"\n=== {name}: N={N} e={e} maxcut={mc} beta={beta} Gamma={G} N^2={N*N} deficit={N*N-G} "
          f"d_edge={2*e/(N*N):.4f} F=2beta/N^2={2*beta/(N*N):.4f} beta/e={beta/e:.4f} ===",flush=True)
    # D* and local, plus mass-bound tightness
    Dstar=None; worst_local=-10**9; maxL_minus_bound=None; n_geo=0
    for (u,v) in M:
        for C in all_shortest_geos(N,adj,side,u,v):
            n_geo+=1
            d=D_of(N,adj,side,M,C)
            if d is None: continue
            if Dstar is None or d<Dstar: Dstar=d
            worst_local=max(worst_local, G+d-N*N)
            # mass bound: L=Gamma-Gamma'
            Cset=set(C); keep=set(x for x in range(N) if x not in Cset)
            Mp=[(a,b) for (a,b) in M if a in keep and b in keep]; Gp=0; ok=True
            for (a,b) in Mp:
                dd=bdistB(N,adj,side,a,banned=Cset).get(b,-1)
                if dd<0: ok=False; break
                Gp+=(dd+1)**2
            if ok:
                L=G-Gp; bound=2*len(C)*N-len(C)**2
                if maxL_minus_bound is None or L-bound>maxL_minus_bound: maxL_minus_bound=L-bound
    print(f"    D*={Dstar} ; master Gamma+D*<=N^2: {G}+{Dstar}={G+(Dstar or 0)} <= {N*N} ? {G+(Dstar or 0)<=N*N}",flush=True)
    print(f"    local D(C)<=N^2-Gamma for ALL {n_geo} shortest geodesics: {worst_local<=0} (worst Gamma+D(C)-N^2={worst_local})",flush=True)
    print(f"    mass bound L<=2|C|N-|C|^2: max(L-bound)={maxL_minus_bound} => "
          f"{'TIGHT somewhere' if maxL_minus_bound==0 else ('STRICTLY SLACK (L<bound) everywhere' if (maxL_minus_bound is not None and maxL_minus_bound<0) else 'n/a')}",flush=True)

if __name__=="__main__":
    C5=[(i,(i+1)%5) for i in range(5)]
    grot_N, grot_adj = mycielskian(5, C5)            # Grotzsch = M(C5), 11 verts
    grot_edges=edges_of(grot_adj)
    pet_adj=[set() for _ in range(10)]
    for i in range(5):
        for (a,b) in [(i,(i+1)%5),(5+i,5+(i+2)%5),(i,5+i)]: pet_adj[a].add(b); pet_adj[b].add(a)
    pet_edges=edges_of(pet_adj)
    which = sys.argv[1] if len(sys.argv)>1 else "both"
    if which in ("pet","both"):
        N,adj = mycielskian(10, pet_edges); analyze("M(Petersen)", N, adj)
    if which in ("grot","both"):
        N,adj = mycielskian(11, grot_edges); analyze("M(Grotzsch)", N, adj)
    print("\nDONE",flush=True)
