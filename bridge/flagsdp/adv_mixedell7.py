#!/usr/bin/env python3
"""Mixed-ell PART 7: FORCE coexisting ell=5 AND ell=7 bad edges (true mixed ell), via multiple
detours in one C5[q], and via C7[q] blowups (pure ell=7) + a C5 contamination. Verify the
shortest-ell peel stays safe under genuine mixing. Also push C7[q] blowups (all ell=7) which
are the densest pure-ell-7 structures (their own near-tight family)."""
import sys
from peel_check import check_instance, gamma_of, shortest_path_B

def add_edge(adj,u,v):
    if u!=v: adj[u].add(v); adj[v].add(u)
def del_edge(adj,u,v):
    adj[u].discard(v); adj[v].discard(u)

def Ckq(k,q):
    n=k*q; vid=lambda i,j:i*q+j; adj=[set() for _ in range(n)]
    for i in range(k):
        for a in range(q):
            for b in range(q):
                add_edge(adj,vid(i,a),vid((i+1)%k,b))
    return n,adj,vid

def report(name,n,adj):
    r=check_instance(n,adj)
    ell_set=None
    if r.get("ok") and r.get("B_connected") and r.get("side") is not None:
        sd=r["side"]; G,M=gamma_of(n,adj,sd); ells=set()
        for (u,v) in M:
            P=shortest_path_B(n,adj,sd,u,v)
            if P: ells.add(len(P))
        ell_set=sorted(ells)
    G=r.get("gamma"); n2=r.get("n2"); defc=(n2-G) if (G is not None and n2) else None
    mixed = ell_set is not None and len(ell_set)>=2
    print(f"{name}: N={r.get('N')} m={r.get('m')} gamma={G} n2={n2} deficit={defc} "
          f"tight={r.get('tight')} ells={ell_set} MIXED={mixed} safe_peel={r.get('has_safe_peel')}",flush=True)
    if r.get('tight') and r.get('has_safe_peel')==False:
        print("  *** OBSTRUCTION ***",flush=True)
    if not r.get("triangle_free"): print("  NOT TF",flush=True)
    return r,mixed

# C5[q] with TWO detours at different parts -> coexisting ell=5 and ell=7
def C5q_two_detours(q):
    n,adj,vid=Ckq(5,q)
    if q<2: return None
    # detour part0[0]->part1 links
    w=vid(0,0); nb=[vid(1,b) for b in range(q)]
    for u in nb: del_edge(adj,w,u)
    x,y=len(adj),len(adj)+1; adj.append(set()); adj.append(set())
    add_edge(adj,w,x); add_edge(adj,x,y)
    for u in nb: add_edge(adj,y,u)
    return len(adj),adj

if __name__=="__main__":
    mixed_count=0; mixed_safe=0; mixed_unsafe=[]
    print("=== C7[q] pure blowups (all ell=7) ===")
    for q in [1,2,3]:
        n,adj,_=Ckq(7,q)
        if n<=24:
            r,mx=report(f"C7[{q}]",n,adj)
            if mx: mixed_count+=1; mixed_safe+= (r.get('has_safe_peel') is True)

    print("\n=== C9[q] pure blowups (all ell=9) ===")
    for q in [1,2]:
        n,adj,_=Ckq(9,q)
        if n<=24:
            r,mx=report(f"C9[{q}]",n,adj)

    print("\n=== C5[q] single detour (mixed ell 5,7) sweep ===")
    for q in [2,3,4]:
        res=C5q_two_detours(q)
        if res:
            n,adj=res
            if n<=24:
                r,mx=report(f"C5[{q}] detour",n,adj)
                if mx:
                    mixed_count+=1
                    if r.get('has_safe_peel') is True: mixed_safe+=1
                    elif r.get('has_safe_peel') is False: mixed_unsafe.append((f"C5[{q}] detour",r))

    print(f"\n=== SUMMARY ===")
    print(f"mixed-ell instances seen={mixed_count}  with safe_peel=True={mixed_safe}  "
          f"mixed-ell NO-peel={len(mixed_unsafe)}")
    for nm,r in mixed_unsafe:
        print(f"  MIXED NO-PEEL: {nm} N={r['N']} gamma={r['gamma']} n2={r['n2']} tight={r['tight']}")
