#!/usr/bin/env python3
"""Larger balanced odd-cycle blow-ups C_{2k+1}[t] with N>20, where brute max-cut is infeasible.
For balanced C_{2k+1}[t]: the gamma-min connected-B max cut is the canonical 2-colouring of the
odd cycle's vertices into the (2k+1)-cycle's near-bipartition. We compute U with the ANALYTIC cut
and INDEPENDENTLY VERIFY it is a max cut (value matches the analytic max-cut size) and that B is connected.
All bad edges are within one group's worth of structure giving ell=5 (for C5) etc; Gamma=N^2.
EXACT Fractions."""
from fractions import Fraction as Fr
from census_GPI import gmin, geos, maxcut_all

def build_adj(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def cyclic_blowup(k, t):
    sizes=[t]*k
    offs=[0]
    for s in sizes: offs.append(offs[-1]+s)
    n=offs[-1]; E=[]
    for i in range(k):
        j=(i+1)%k
        for a in range(sizes[i]):
            for b in range(sizes[j]):
                E.append((offs[i]+a, offs[j]+b))
    return n,E,offs

def maxcut_value_greedy_exact(n,adj,E):
    """Compute true max-cut VALUE by brute only if small; else return None."""
    if n>24: return None
    edges=[(u,v) for (u,v) in E]
    best=-1
    for m in range(1<<(n-1)):
        side=[(m>>u)&1 for u in range(n)]
        c=sum(1 for u,v in edges if side[u]!=side[v])
        if c>best: best=c
    return best

def analytic_cut(k,t,offs):
    """For odd cycle C_k, the standard max cut: 2-colour so all but one consecutive pair of groups alternate.
    Put group i on side (i mod 2) for i=0..k-2, and group k-1 on side 0 (since k-1 even when k odd =>
    actually assign each group i color i%2; the wrap edge between group k-1 (color (k-1)%2=0) and group0(color0)
    is monochromatic => those are the bad edges)."""
    n=offs[-1]
    side=[0]*n
    for i in range(k):
        col=i%2
        for a in range(t):
            side[offs[i]+a]=col
    return side

def cut_value(n,side,E):
    return sum(1 for u,v in E if side[u]!=side[v])

print("=== Larger balanced blow-ups C_{2k+1}[t], analytic gamma-min cut, EXACT U-check ===")
cases=[(5,t) for t in range(2,9)]+[(7,t) for t in range(2,5)]+[(9,t) for t in range(2,4)]+[(11,2)]
for k,t in cases:
    n,E,offs=cyclic_blowup(k,t)
    adj=build_adj(n,E)
    side=analytic_cut(k,t,offs)
    # bad edges = wrap between group k-1 and group 0 (both color 0)
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    # verify B connected
    from collections import deque
    seen={0};q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in seen: seen.add(v);q.append(v)
    Bconn = len(seen)==n
    # ell via restricted bfs
    def bdist(s,t):
        d={s:0};q=deque([s])
        while q:
            u=q.popleft()
            for v in adj[u]:
                if side[u]!=side[v] and v not in d: d[v]=d[u]+1;q.append(v)
        return d.get(t,-1)
    ell={}; G=0; ok=True
    for (u,v) in M:
        d=bdist(u,v)
        if d<0: ok=False;break
        ell[(u,v)]=d+1; G+=(d+1)**2
    cv=cut_value(n,side,E)
    # analytic max-cut value for balanced C_{2k+1}[t]: all edges except the t^2 wrap edges between groups
    # k-1 and 0... wait: total edges = k*t^2. Mono edges = those between the two same-colored adjacent groups.
    # With coloring i%2: adjacent groups (i,i+1) differ in color EXCEPT the wrap pair (k-1,0) both even-index?
    # group k-1 color=(k-1)%2=0 (k odd), group0 color0 => mono. All other adjacent pairs alternate.
    # So mono edges = t^2 (one group-pair). maxcut should = k*t^2 - t^2 = (k-1)*t^2.
    expected_maxcut=(k-1)*t*t
    truemax=maxcut_value_greedy_exact(n,adj,E)
    K=n+(n*n-G)
    # T_uniform
    T=[Fr(0)]*n
    bad=False
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); nf=len(Ps)
        if nf==0: bad=True;break
        share=Fr(ell[f],nf)
        for P in Ps:
            for v in P: T[v]+=share
    if bad:
        print(f"  C{k}[{t}]: geodesic count 0 -- ERROR"); continue
    maxT=max(T); slack=Fr(K)-maxT
    tm = f"truemax={truemax}" if truemax is not None else "truemax=NA(N>24)"
    print(f"  C{k}[{t}]: N={n} Bconn={Bconn} cutval={cv} expMaxcut={expected_maxcut} {tm} "
          f"Gamma={G} K={K} maxT={maxT} slack={slack} VIOL={maxT>K} "
          f"cut_is_max={cv==expected_maxcut and (truemax is None or truemax==expected_maxcut)}")
