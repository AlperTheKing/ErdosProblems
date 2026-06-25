import itertools, math
from collections import deque
from scipy.optimize import linprog
import numpy as np

def maxcut(adj,n):
    best=-1;allbest=[]
    for mask in range(1<<n):
        Xs=frozenset(i for i in range(n) if mask&(1<<i)); c=0
        for u in range(n):
            for v in range(u+1,n):
                if adj[u][v] and ((u in Xs)!=(v in Xs)): c+=1
        if c>best: best=c;allbest=[Xs]
        elif c==best: allbest.append(Xs)
    return best,allbest

def all_odd_cycles(adj,n):
    seen=set(); out=[]
    def dfs(start,u,path,ps):
        for w in range(n):
            if not adj[u][w]: continue
            if w==start and len(path)>=3 and len(path)%2==1:
                es=frozenset(frozenset((path[i],path[(i+1)%len(path)])) for i in range(len(path)))
                if es not in seen: seen.add(es); out.append((tuple(path),es))
            elif w not in ps and w>start and len(path)<n:
                path.append(w); ps.add(w); dfs(start,w,path,ps); path.pop(); ps.discard(w)
    for s in range(n): dfs(s,s,[s],{s})
    return out

def edges_of(adj,n):
    return [(u,v) for u in range(n) for v in range(u+1,n) if adj[u][v]]

def nu_int_max_over_cuts(adj,n):
    """max INTEGRAL edge-disjoint odd cycle packing (independent of max-cut choice)"""
    E=edges_of(adj,n); cyc=all_odd_cycles(adj,n)
    if not cyc: return 0
    eidx={frozenset(e):i for i,e in enumerate(E)}; nC=len(cyc); nE=len(E)
    Aub=np.zeros((nE,nC))
    for j,(_,es) in enumerate(cyc):
        for e in es: Aub[eidx[e],j]=1.0
    res=linprog(-np.ones(nC),A_ub=Aub,b_ub=np.ones(nE),bounds=[(0,1)]*nC,method="highs",integrality=np.ones(nC))
    return int(round(-res.fun))

def gpt_k23():
    N=13; adj=[[0]*N for _ in range(N)]
    def add(u,v): adj[u][v]=adj[v][u]=1
    for i in (0,1):
        for j in (2,3,4): add(i,j)
    nxt=5
    for (x,y) in [(0,1),(2,3),(2,4),(3,4)]:
        a,b=nxt,nxt+1; nxt+=2; add(x,a); add(a,b); add(b,y)
    return adj,N

adj,N=gpt_k23()
mc,cuts=maxcut(adj,N)
print("K23-N13: N=%d, MaxCut=%d, #max-cut bipartitions=%d"%(N,mc,len(cuts)))
# tau is the same for all max cuts (= e - mc)
e=sum(1 for u in range(N) for v in range(u+1,N) if adj[u][v])
print("  e=%d, tau=e-MaxCut=%d  (independent of which max cut)"%(e,e-mc))
m=e-mc
print("  STRATEGY claims an INTEGRAL packing p with p >= 25*tau^2/N^2 = %.4f"%(25*m*m/(N*N)))
nui=nu_int_max_over_cuts(adj,N)
print("  TRUE maximum integral edge-disjoint odd-cycle packing nu_int = %d"%nui)
print("  => any integral packing has size <= %d < %.4f"%(nui,25*m*m/(N*N)))
print("  => 'exhibit p edge-disjoint odd cycles with p >= 25tau^2/N^2' is IMPOSSIBLE here.")
print()
# Now the fractional value, which IS >= target, but is not an integral packing
E=edges_of(adj,N); cyc=all_odd_cycles(adj,N)
eidx={frozenset(ee):i for i,ee in enumerate(E)}; nC=len(cyc); nE=len(E)
Aub=np.zeros((nE,nC))
for j,(_,es) in enumerate(cyc):
    for ee in es: Aub[eidx[ee],j]=1.0
res=linprog(-np.ones(nC),A_ub=Aub,b_ub=np.ones(nE),bounds=[(0,None)]*nC,method="highs")
print("  nu*(fractional) = %.4f  >= %.4f  (holds, but it is FRACTIONAL, not p edge-disjoint cycles)"%(-res.fun,25*m*m/(N*N)))
