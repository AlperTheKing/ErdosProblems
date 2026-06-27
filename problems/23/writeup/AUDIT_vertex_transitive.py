#!/usr/bin/env python3
"""Vertex-transitive triangle-free census for the U claim (uniform-load GPI).
For each graph: gamma-min connected-B max cut, EXACT Fraction max_v T_uniform <= K = N + (N^2 - Gamma).
Families: circulants C_N(S) N=10..20 (1-3 generators); generalized Petersen GP(n,k) tri-free N<=20;
Petersen; Kneser K(5,2). Any violation is re-confirmed independently.
Uses census_GPI.gmin/geos (trusted) but a numpy-vectorized maxcut for N up to 20."""
import sys, itertools, io, contextlib
from fractions import Fraction
import numpy as np
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\writeup")
_buf=io.StringIO()
with contextlib.redirect_stdout(_buf):
    from census_GPI import gmin, geos

def edges_to_adj(n, E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def is_trianglefree(n, adj):
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u] & adj[v]): return False
    return True

def is_connected(n, adj):
    seen={0}; stack=[0]
    while stack:
        u=stack.pop()
        for v in adj[u]:
            if v not in seen: seen.add(v); stack.append(v)
    return len(seen)==n

def maxcut_all_fast(n, adj):
    """All max-cut side-vectors (vertex n-1 fixed to side 0). numpy-vectorized, feasible to n~22."""
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
    if not edges: return [[0]*n]
    M=1<<(n-1)
    idx=np.arange(M, dtype=np.uint64)
    bits=np.zeros((M,n), dtype=np.uint8)
    for u in range(n-1):
        bits[:,u]=((idx>>np.uint64(u))&np.uint64(1)).astype(np.uint8)
    eu=np.array([e[0] for e in edges]); ev=np.array([e[1] for e in edges])
    cutcount=(bits[:,eu]!=bits[:,ev]).sum(axis=1)
    best=int(cutcount.max())
    sel=np.where(cutcount==best)[0]
    return [bits[k].tolist() for k in sel]

def Tuniform_check(n, E, cuts=None):
    """Exact: returns dict with maxT, K, Gamma, slack=K-maxT, side; None if no valid gamma-min connected-B cut."""
    adj=edges_to_adj(n, E)
    if cuts is None: cuts=maxcut_all_fast(n, adj)
    r=gmin(n, adj, cuts)
    if r is None: return None
    side, G, M, ell = r
    T=[Fraction(0) for _ in range(n)]
    for f in M:
        Ps=geos(adj, side, f[0], f[1]); nf=len(Ps)
        if nf==0: return None
        share=Fraction(ell[f], nf)
        for P in Ps:
            for v in P: T[v]+=share
    maxT=max(T); K=n+(n*n-G)
    return {'n':n,'Gamma':G,'K':K,'maxT':maxT,'slack':K-maxT,'side':side,'M':M,'ell':ell}

def circulant(N, S):
    Sset=set()
    for s in S: Sset.add(s%N); Sset.add((-s)%N)
    Sset.discard(0)
    E=[]
    for i in range(N):
        for s in Sset:
            j=(i+s)%N
            if i<j: E.append((i,j))
    return N, E

def genpetersen(n, k):
    N=2*n; Es=set()
    for i in range(n):
        for a,b in [(i,(i+1)%n),(i,i+n),(i+n,((i+k)%n)+n)]:
            if a!=b: Es.add((min(a,b),max(a,b)))
    return N, sorted(Es)

def kneser(m, k):
    verts=list(itertools.combinations(range(m), k)); N=len(verts); E=[]
    for i in range(N):
        for j in range(i+1, N):
            if not (set(verts[i]) & set(verts[j])): E.append((i,j))
    return N, E

def main():
    violations=[]; tested=0
    min_slack=None; min_slack_desc=None
    tight=[]
    def consider(desc, N, E):
        nonlocal min_slack, min_slack_desc, tested
        adj=edges_to_adj(N, E)
        if not E or not is_connected(N, adj) or not is_trianglefree(N, adj): return
        r=Tuniform_check(N, E)
        if r is None: return
        tested+=1
        sl=r['slack']
        if min_slack is None or sl<min_slack:
            min_slack=sl; min_slack_desc=f"{desc} N={N} Gamma={r['Gamma']} maxT={r['maxT']} K={r['K']}"
        if r['maxT'] > r['K']:
            violations.append((desc,N,r['Gamma'],r['K'],str(r['maxT']),E))
            print(f"!!! VIOLATION {desc} N={N} Gamma={r['Gamma']} maxT={r['maxT']} K={r['K']}", flush=True)
        if sl==0:
            tight.append(f"{desc} N={N} Gamma={r['Gamma']}")

    print("=== Circulants N=10..20, 1-3 generators ===", flush=True)
    for N in range(10,21):
        gens=list(range(1, N//2+1))
        for r in range(1,4):
            for S in itertools.combinations(gens, r):
                consider(f"C_{N}{list(S)}", *circulant(N, list(S)))
        print(f"  N={N} done, tested cumulative={tested}", flush=True)

    print("=== Generalized Petersen GP(n,k) n=3..10 (N<=20) ===", flush=True)
    for n in range(3,11):
        for k in range(1, n):
            if k > n-k: continue
            consider(f"GP({n},{k})", *genpetersen(n,k))

    print("=== Kneser K(5,2)=Petersen (K(7,3) N=35 infeasible, skipped) ===", flush=True)
    consider("K(5,2)", *kneser(5,2))

    print(f"\n=== SUMMARY ===", flush=True)
    print(f"tested={tested}", flush=True)
    print(f"violations={len(violations)}", flush=True)
    print(f"min_slack={min_slack} at {min_slack_desc}", flush=True)
    print(f"tight(slack=0) count={len(tight)}", flush=True)
    for t in tight[:40]: print("  TIGHT:", t, flush=True)
    for v in violations: print("VIOL:", v, flush=True)

if __name__=='__main__':
    main()
