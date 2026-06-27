#!/usr/bin/env python3
"""Focused near-tight probe for generalized-theta family.

1. Re-examine the highest no-peel-ratio theta (theta[3,3,2,2]) and dump WHY no peel (which condition).
2. Try to PUSH toward tight Gamma=N^2 with m>=2: theta graphs where every bad edge has long B-geodesic.
   The tight family is C5[q] (5-cycle blow-up). A theta that contains C5 as 'spine' plus extra odd paths
   between the same hub pair can raise Gamma. Build 'C5 + extra odd ear' configs and blow up.
3. Generalized theta with k odd paths ALL length 5 between two hubs = a bipartite graph (no bad edges
   for the natural cut) -> blow up and check whether forcing a different max cut creates bad edges with
   large geodesics. Loop q, k.
"""
import sys
from peel_check import (check_instance, maxcut_all, Bconnected, gamma_of,
                        shortest_path_B, has_safe_peel as _hsp, cut_dom, bdistB)

def theta_graph(Ls):
    adj=[]
    def newv():
        adj.append(set()); return len(adj)-1
    s=newv(); t=newv()
    for L in Ls:
        prev=s
        for i in range(L-1):
            v=newv(); adj[prev].add(v); adj[v].add(prev); prev=v
        adj[prev].add(t); adj[t].add(prev)
    return len(adj), adj

def blowup(n, adj, q):
    size=[q]*n; start=[0]*n; c=0
    for v in range(n): start[v]=c; c+=size[v]
    N=c; A=[set() for _ in range(N)]
    for u in range(n):
        for v in adj[u]:
            if v>u:
                for a in range(size[u]):
                    for b in range(size[v]):
                        x=start[u]+a; y=start[v]+b; A[x].add(y); A[y].add(x)
    return N,A

def diagnose(label, n, adj):
    r=check_instance(n,adj)
    print(f"\n### {label}: N={r.get('N')} m={r.get('m')} gamma={r.get('gamma')} "
          f"n2={r.get('n2')} ratio={(r.get('gamma')/r.get('n2')) if r.get('gamma') else None} "
          f"tight={r.get('tight')} safe_peel={r.get('has_safe_peel')}")
    if r.get("has_safe_peel")==False:
        # dump per-bad-edge failure reason
        sd=r["side"]; N=r["N"]; A=[set(a) for a in adj]
        for u in range(N): A[u].discard(u)
        G,M=gamma_of(N,A,sd)
        print(f"   side={sd}")
        print(f"   M={M}")
        for (u,v) in M:
            P=shortest_path_B(N,A,sd,u,v)
            if P is None: print(f"   edge ({u},{v}): no B-path?!"); continue
            C=set(P); s=len(C); keep=[x for x in range(N) if x not in C]
            Mp=[(a,b) for (a,b) in M if a in keep and b in keep]
            Gp=0; conn_ok=True; bad=None
            for (a,b) in Mp:
                d=bdistB(N,A,sd,a,banned=C).get(b,-1)
                if d<0: conn_ok=False; bad=(a,b); break
                Gp+=(d+1)**2
            if not conn_ok:
                print(f"   edge ({u},{v}) |C|={s} P={P}: FAIL(ii) bad edge {bad} disconnected"); continue
            L=G-Gp; bound=2*s*N-s*s
            if L>bound:
                print(f"   edge ({u},{v}) |C|={s} P={P}: FAIL(iii) L={L}>bound={bound}"); continue
            cd=cut_dom(keep,N,A,sd,Mp)
            if cd is True:
                print(f"   edge ({u},{v}) |C|={s} P={P}: would be SAFE?! (i)ok (ii)ok (iii)ok"); continue
            print(f"   edge ({u},{v}) |C|={s} P={P}: FAIL(i) cut-domination broken on keep (L={L}<=bound={bound})")
    sys.stdout.flush()
    return r

if __name__=="__main__":
    # 1. dump the high-ratio no-peel theta
    for ls,q in [([3,3,2,2],1),([3,3,2,2],2),([5,5,4,4],1),([7,7,2,2],1),([3,3,4,4],1)]:
        n0,a0=theta_graph(ls); N,A=blowup(n0,a0,q)
        if N<=22: diagnose(f"theta{ls}_q{q}", N, A)

    # 2. push toward tight: many odd paths length 5 (C5-like) PLUS extra ears
    print("\n\n=== PUSH-TO-TIGHT scan (k length-5 odd paths between hubs, blow up) ===")
    best=(-1,None)
    for k in (2,3,4):
        for q in (1,2,3):
            ls=[5]*k
            n0,a0=theta_graph(ls); N,A=blowup(n0,a0,q)
            if N>18: continue
            r=check_instance(N,A)
            ratio=(r.get('gamma')/r.get('n2')) if r.get('gamma') else 0
            print(f"theta{ls}_q{q}: N={N} m={r.get('m')} gamma={r.get('gamma')} "
                  f"ratio={ratio} tight={r.get('tight')} safe_peel={r.get('has_safe_peel')}")
            if ratio>best[0]: best=(ratio,f"theta{ls}_q{q}")
            sys.stdout.flush()
    # also mix 3 and 5 evenly
    for ls in [[3,5],[5,5,5],[3,3,5],[3,5,5],[5,5,5,5],[3,5,3,5]]:
        for q in (1,2):
            n0,a0=theta_graph(ls); N,A=blowup(n0,a0,q)
            if N>18: continue
            r=check_instance(N,A)
            ratio=(r.get('gamma')/r.get('n2')) if r.get('gamma') else 0
            print(f"theta{ls}_q{q}: N={N} m={r.get('m')} gamma={r.get('gamma')} "
                  f"ratio={ratio} tight={r.get('tight')} safe_peel={r.get('has_safe_peel')}")
            if ratio>best[0]: best=(ratio,f"theta{ls}_q{q}")
            sys.stdout.flush()
    print(f"\nPUSH-TO-TIGHT best ratio = {best}")
