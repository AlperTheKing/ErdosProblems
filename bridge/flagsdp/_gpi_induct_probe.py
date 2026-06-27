#!/usr/bin/env python3
"""
GPI-by-INDUCTION probe. Test whether GPI(G) follows from GPI(G-C) plus a boundary term.

GPI(G): sum_{e in M} h_e m_phi(e) <= (N + N^2 - Gamma) sum_v phi(v),  all phi>=0.

We TEST the cleanest inductive inequality (BND):
   LHS_full(phi) - LHS_sub(phi)  <=  (K - K') sum_{v in V'} phi  +  K sum_{v in C} phi
where LHS_sub uses M' = bad edges of G-C with geodesics avoiding C, K=N+N^2-Gamma, K'=N'+N'^2-Gamma'.
If BND holds AND GPI(G-C) holds, then GPI(G) follows (add them).
"""
import sys, random
from collections import deque
from mycielskian_check import gamma_min_cut, all_shortest_geos, edges_of, mycielskian

def Bcomp_dist(n, adj, side, banned, s):
    d={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in banned and v not in d:
                d[v]=d[u]+1; q.append(v)
    return d

def all_geos_banned(n,adj,side,banned,s,t):
    dist={s:0}; pred={s:[]}; layer=[s]
    while layer:
        nxt=[]
        for u in layer:
            for v in adj[u]:
                if side[u]!=side[v] and v not in banned:
                    if v not in dist: dist[v]=dist[u]+1; pred[v]=[u]; nxt.append(v)
                    elif dist[v]==dist[u]+1: pred[v].append(u)
        layer=nxt
    if t not in dist: return []
    out=[]
    def rec(v,acc):
        if v==s: out.append([s]+acc[::-1]); return
        for p in pred[v]: rec(p,acc+[v])
    rec(t,[]); return out

def m_phi(geos, phi):
    return min(sum(phi[v] for v in P) for P in geos)

def gpi_lhs(N,adj,side,M,phi,banned):
    s=0.0
    for (u,v) in M:
        geos=all_geos_banned(N,adj,side,banned,u,v)
        if not geos: return None
        h=len(geos[0])
        s+=h*m_phi(geos,phi)
    return s

def test_graph(name,N,adj):
    E=edges_of(adj)
    res,mc=gamma_min_cut(N,adj,E)
    if res is None:
        print("%s: no connected-B max cut"%name); return
    side,G,M=res
    if len(M)<2:
        print("%s: beta=%d <2, base case"%(name,len(M))); return
    K=N+N*N-G
    worst_bnd=-1e9; worst_info=None
    rng=random.Random(12345)
    phis=[]
    for _ in range(150): phis.append([rng.random() for _ in range(N)])
    for _ in range(150):
        S=set(rng.sample(range(N), rng.randint(1,N)))
        phis.append([1.0 if v in S else 0.0 for v in range(N)])
    for (bu,bv) in M:
        for C in all_shortest_geos(N,adj,side,bu,bv):
            Cset=set(C); h=len(C)
            keep=[v for v in range(N) if v not in Cset]
            if len(keep)<1: continue
            Mp=[(a,b) for (a,b) in M if a not in Cset and b not in Cset]
            ok=True; Gp=0
            for (a,b) in Mp:
                d=Bcomp_dist(N,adj,side,Cset,a).get(b,-1)
                if d<0: ok=False; break
                Gp+=(d+1)**2
            if not ok: continue
            Np=N-h; Kp=Np+Np*Np-Gp
            for phi in phis:
                lhs_full=gpi_lhs(N,adj,side,M,phi,set())
                lhs_sub =gpi_lhs(N,adj,side,Mp,phi,Cset)
                if lhs_full is None or lhs_sub is None: continue
                sumV=sum(phi); sumC=sum(phi[v] for v in C); sumVp=sumV-sumC
                bnd_rhs=(K-Kp)*sumVp + K*sumC
                viol=(lhs_full-lhs_sub)-bnd_rhs
                if viol>worst_bnd:
                    worst_bnd=viol; worst_info=(bu,bv,h,G,Gp,K,Kp)
    print("%s: N=%d beta=%d Gamma=%d K=%d | worst BND violation = %.4f (>0 => BND FAILS) info=%s"
          %(name,N,len(M),G,K,worst_bnd,worst_info))

if __name__=="__main__":
    def C5q(q):
        n=5*q
        def vid(i,j): return i*q+j
        side=[0]*n
        for i in range(5):
            for j in range(q): side[vid(i,j)]=(0 if i in (0,2,4) else 1)
        adj=[set() for _ in range(n)]
        for i in range(5):
            for a in range(q):
                for b in range(q):
                    u=vid(i,a); v=vid((i+1)%5,b); adj[u].add(v); adj[v].add(u)
        return n,adj
    for q in (2,3):
        n,adj=C5q(q); test_graph("C5[%d]"%q,n,adj)
