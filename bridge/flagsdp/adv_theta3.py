#!/usr/bin/env python3
"""Final broad sweep: ALL theta multisets (lengths in {2,3,4,5,6,7}, k=2..6), q=1..3, N<=18.
Goal: confirm NO tight (Gamma=N^2) m>=2 instance exists in the generalized-theta family,
and report the global max ratio + any near-tight no-peel cases. Counts instances checked."""
import itertools, sys
from peel_check import check_instance

def theta_graph(Ls):
    adj=[]
    def newv(): adj.append(set()); return len(adj)-1
    s=newv(); t=newv()
    for L in Ls:
        prev=s
        for i in range(L-1):
            v=newv(); adj[prev].add(v); adj[v].add(prev); prev=v
        adj[prev].add(t); adj[t].add(prev)
    return len(adj), adj

def blowup(n, adj, q):
    start=[0]*n; c=0
    for v in range(n): start[v]=c; c+=q
    N=c; A=[set() for _ in range(N)]
    for u in range(n):
        for v in adj[u]:
            if v>u:
                for a in range(q):
                    for b in range(q):
                        x=start[u]+a; y=start[v]+b; A[x].add(y); A[y].add(x)
    return N,A

if __name__=="__main__":
    Lvals=(2,3,4,5,6,7)
    checked=0; mixed_ell=False
    best_ratio=(-1,None); best_notpeel=(-1,None)
    tight_m2=[]; nopeel_count=0
    families=set()
    for k in range(2,7):
        for combo in itertools.combinations_with_replacement(Lvals,k):
            ls=list(combo)
            distinct=set(x%2 for x in ls)
            if len(set(ls))>=3: mixed_ell=True   # at least 3 distinct lengths -> mixed-ell
            for q in (1,2,3):
                n0,a0=theta_graph(ls)
                N,A=blowup(n0,a0,q)
                if N>18: continue
                r=check_instance(N,A)
                checked+=1
                families.add(tuple(sorted(ls)))
                if not (r.get("ok") and r.get("triangle_free") and r.get("B_connected")):
                    continue
                g=r.get("gamma"); n2=r.get("n2"); m=r.get("m") or 0
                if g is None or n2 is None: continue
                ratio=g/n2
                if ratio>best_ratio[0]: best_ratio=(ratio,f"theta{ls}_q{q} N={N} m={m} g={g}")
                # obstruction check
                if m>=2 and r.get("ge_n2") and r.get("has_safe_peel")==False:
                    tight_m2.append((ls,q,N,m,g,n2))
                if m>=2 and r.get("has_safe_peel")==False:
                    nopeel_count+=1
                    if ratio>best_notpeel[0]: best_notpeel=(ratio,f"theta{ls}_q{q} N={N} m={m} g={g}/{n2}")
                # also record any TIGHT with m>=2 regardless of peel
                if m>=2 and r.get("tight"):
                    tight_m2.append(("TIGHT",ls,q,N,m,g,n2,r.get("has_safe_peel")))
    print(f"INSTANCES CHECKED = {checked}")
    print(f"DISTINCT length-multiset families = {len(families)}")
    print(f"mixed-ell (>=3 distinct lengths) tested = {mixed_ell}")
    print(f"GLOBAL max ratio gamma/n2 = {best_ratio}")
    print(f"max-ratio among m>=2 NO-safe-peel = {best_notpeel}")
    print(f"count of m>=2 no-safe-peel (all NON-tight = not obstructions unless tight) = {nopeel_count}")
    print(f"TIGHT m>=2 instances (OBSTRUCTION CANDIDATES) = {tight_m2}")
