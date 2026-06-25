#!/usr/bin/env python3
# Is QFC25 (rho <= max{1, N^2/(25m)}) equivalent to the theorem, or strictly stronger?
# The routing chain: nu* >= m/kappa, kappa=max{1,rho}. Combined with nu*<=N^2/25 (PROVED unconditionally):
#   - if m<=N^2/25: need rho<=N^2/(25m). Then nu*>=m/(N^2/(25m))=25m^2/N^2.
#   - if m>N^2/25:  QFC25 forces rho<=1 => nu*>=m>N^2/25, contradicting nu*<=N^2/25 => m<=N^2/25.
# So QFC25 => theorem. Question: on the K_{2,3} N=13 obstruction (nu*<tau), what is rho? If rho > N^2/(25m)
# would FALSIFY QFC25 -- but the bound has slack there. We confirm rho values and the implication structure.
#
# DEEPER: the routing gives nu*_routed = m/kappa, a LOWER bound on the true nu*. Is rho actually controlling
# the SAME nu* that <=N^2/25 caps? Check: routed packing value vs true nu* (LP).

import itertools, math
import numpy as np
from scipy.optimize import linprog

def adjset(N, A): return [set(v for v in range(N) if (A[u] >> v) & 1) for u in range(N)]

def maxcut(N, adj):
    best=-1; bs=None
    for mask in range(1<<(N-1)):
        side=[(mask>>u)&1 for u in range(N)]
        c=sum(1 for u in range(N) for v in adj[u] if v>u and side[u]!=side[v])
        if c>best: best=c; bs=side
    return best, bs

def all_odd_cycles(N, adj):
    seen=set(); out=[]
    def dfs(start,u,path,ps):
        for w in adj[u]:
            if w==start and len(path)>=3 and len(path)%2==1:
                es=frozenset(frozenset((path[i],path[(i+1)%len(path)])) for i in range(len(path)))
                if es not in seen: seen.add(es); out.append((tuple(path),es))
            elif w not in ps and w>start and len(path)<N:
                path.append(w); ps.add(w); dfs(start,w,path,ps); path.pop(); ps.discard(w)
    for s in range(N): dfs(s,s,[s],{s})
    return out

def nu_star(N, adj):
    edges=[frozenset((u,v)) for u in range(N) for v in adj[u] if v>u]
    cyc=all_odd_cycles(N,adj)
    if not cyc: return 0.0
    eidx={e:i for i,e in enumerate(edges)}; nC=len(cyc); nE=len(edges)
    Aub=np.zeros((nE,nC))
    for j,(_,es) in enumerate(cyc):
        for e in es: Aub[eidx[e],j]=1.0
    res=linprog(-np.ones(nC),A_ub=Aub,b_ub=np.ones(nE),bounds=[(0,None)]*nC,method="highs")
    return -res.fun

def rho_mcf(N, adjB, demands):
    Bedges=sorted(set(frozenset((u,v)) for u in range(N) for v in adjB[u] if v>u),key=lambda e:tuple(sorted(e)))
    Be=[tuple(sorted(e)) for e in Bedges]; nB=len(Be); K=len(demands)
    arcs=[]
    for (x,y) in Be: arcs.append((x,y)); arcs.append((y,x))
    nA=len(arcs); arc_idx={a:i for i,a in enumerate(arcs)}
    nf=K*nA; nvar=nf+1
    def fvar(k,ai): return k*nA+ai
    KAP=nf
    c=np.zeros(nvar); c[KAP]=1.0
    A_eq=[]; b_eq=[]
    for k,(s,t) in enumerate(demands):
        for v in range(N):
            row=np.zeros(nvar)
            for ai,(a,b) in enumerate(arcs):
                if a==v: row[fvar(k,ai)]+=1.0
                if b==v: row[fvar(k,ai)]-=1.0
            A_eq.append(row); b_eq.append(1.0 if v==s else (-1.0 if v==t else 0.0))
    A_ub=[]; b_ub=[]
    for ei,(x,y) in enumerate(Be):
        row=np.zeros(nvar)
        a1=arc_idx[(x,y)]; a2=arc_idx[(y,x)]
        for k in range(K): row[fvar(k,a1)]+=1.0; row[fvar(k,a2)]+=1.0
        row[KAP]=-1.0
        A_ub.append(row); b_ub.append(0.0)
    res=linprog(c,A_ub=np.array(A_ub),b_ub=np.array(b_ub),A_eq=np.array(A_eq),b_eq=np.array(b_eq),
                bounds=[(0,None)]*nf+[(0,None)],method="highs")
    return res.fun

def gpt_k23():
    N=13; A=[0]*N
    def add(u,v): A[u]|=1<<v; A[v]|=1<<u
    for i in (0,1):
        for j in (2,3,4): add(i,j)
    nxt=5
    for (x,y) in [(0,1),(2,3),(2,4),(3,4)]:
        a,b=nxt,nxt+1; nxt+=2; add(x,a); add(a,b); add(b,y)
    return N,A

def analyze(N,A,label):
    adj=adjset(N,A); edges=[(u,v) for u in range(N) for v in adj[u] if v>u]
    mc,side=maxcut(N,adj); tau=len(edges)-mc
    M=[tuple(sorted((u,v))) for (u,v) in edges if side[u]==side[v]]
    adjB=[set() for _ in range(N)]
    for (u,v) in edges:
        if side[u]!=side[v]: adjB[u].add(v); adjB[v].add(u)
    m=len(M)
    nu=nu_star(N,adj)
    rho=rho_mcf(N,adjB,M) if m>0 else 0.0
    bound=max(1.0,N*N/(25.0*m)) if m>0 else 1.0
    kappa=max(1.0,rho)
    routed=m/kappa
    print(f"{label}: N={N} tau={tau} m={m} nu*={nu:.4f} rho={rho:.4f} max(1,N^2/25m)={bound:.4f} "
          f"QFC25_ok={rho<=bound+1e-7} | routed nu*>=m/kappa={routed:.4f} (true nu*={nu:.4f}) "
          f"25m={25*m} N^2={N*N} thm_ok={25*m<=N*N}", flush=True)

if __name__=="__main__":
    analyze(*gpt_k23(),"K23-N13")
