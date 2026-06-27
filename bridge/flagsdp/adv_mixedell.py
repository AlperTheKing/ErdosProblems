#!/usr/bin/env python3
"""Adversarial angle: MIXED-ELL-GLUE for Erdos #23 safe-peel lemma.

Build triangle-free max-cut configs where bad edges have DIFFERENT geodesic lengths ell.
Glue C5-type blocks (ell=5) with C7 / C9 blocks (ell=7,9) sharing vertices / transversal paths.
Test whether peeling the SHORTEST-ell bad edge stays safe (CD + (iii) bound + connectivity).

Reports every instance that is ok+triangle_free+B_connected+m>=2 and either:
  - tight (gamma==n2) with has_safe_peel False  => OBSTRUCTION
  - near-tight (gamma close to n2) where peel conditions strain
"""
from peel_check import check_instance, maxcut_all, Bconnected, gamma_of, has_safe_peel

RESULTS=[]
def run(name, n, adj, side=None):
    r=check_instance(n,adj,side=side)
    tag=""
    if r.get("ok") and r.get("triangle_free") and r.get("B_connected") and r.get("m",0)>=2:
        if r.get("tight") and r.get("has_safe_peel")==False:
            tag=" <<< OBSTRUCTION (tight, no safe peel)"
        elif r.get("has_safe_peel")==False:
            tag=" <<< NO SAFE PEEL (not tight)"
        elif r.get("gamma") is not None and r.get("n2"):
            defc=r["n2"]-r["gamma"]
            if defc<=2*r["N"]:  # near tight
                tag=f" [near-tight deficit={defc}]"
    print(f"{name}: N={r.get('N')} m={r.get('m')} gamma={r.get('gamma')} n2={r.get('n2')} "
          f"tight={r.get('tight')} B_conn={r.get('B_connected')} tf={r.get('triangle_free')} "
          f"safe_peel={r.get('has_safe_peel')}{tag}")
    if not r.get("triangle_free"): print("    NOT TF:",r.get("detail"))
    if r.get("ok") and not r.get("B_connected"): print("    detail:",r.get("detail"))
    RESULTS.append((name,r,tag))
    return r

# ---- building blocks ----------------------------------------------------
# An odd cycle C_{2k+1} as a graph (the canonical bad-edge: one mono edge after maxcut)
def odd_cycle(k):  # C_{2k+1}, vertices 0..2k
    n=2*k+1; adj=[set() for _ in range(n)]
    for i in range(n):
        adj[i].add((i+1)%n); adj[(i+1)%n].add(i)
    return n,adj

def add_edge(adj,u,v):
    adj[u].add(v); adj[v].add(u)

# ---- 1. Two odd cycles sharing a single vertex (figure-eight) ----------
# C5 and C7 sharing vertex 0. Bad edges: ell=5 (from C5) and ell=7 (from C7)?
def two_cycles_share_vertex(k1,k2):
    n1=2*k1+1; n2=2*k2+1
    # cycle A on 0..n1-1 ; cycle B reuses vertex 0 then n1..n1+n2-2
    n=n1+n2-1
    adj=[set() for _ in range(n)]
    # cycle A
    A=list(range(n1))
    for i in range(n1):
        add_edge(adj,A[i],A[(i+1)%n1])
    # cycle B: vertex 0 shared, rest fresh
    B=[0]+list(range(n1,n1+n2-1))
    for i in range(n2):
        add_edge(adj,B[i],B[(i+1)%n2])
    return n,adj

# ---- 2. Two odd cycles sharing a PATH (an edge or a short shared path) ---
def two_cycles_share_path(k1,k2,sharelen):
    # shared path has sharelen edges (sharelen+1 vertices: 0..sharelen)
    # cycle A length 2k1+1, cycle B length 2k2+1, they overlap on path 0..sharelen
    n1=2*k1+1; n2=2*k2+1
    sh=sharelen
    # vertices 0..sh shared. cycle A: 0..sh then aux a-verts back to 0
    auxA=n1-(sh+1)+1-1   # edges in A outside shared = n1 - sh ; vertices = n1 - sh -1? compute carefully
    # Build A as a cycle: shared path p0..p_sh, then chain back p_sh -> x1 -> ... -> p0, with total cycle length n1
    extraA = n1 - sh          # number of edges outside the shared path in A
    extraB = n2 - sh
    vA = extraA - 1           # internal aux vertices for A
    vB = extraB - 1
    if vA<0 or vB<0: return None
    n = (sh+1) + vA + vB
    adj=[set() for _ in range(n)]
    shared=list(range(sh+1))
    for i in range(sh): add_edge(adj,shared[i],shared[i+1])
    # A back-path: p_sh -> aA0..aA(vA-1) -> p0
    aA=list(range(sh+1, sh+1+vA))
    chainA=[shared[sh]]+aA+[shared[0]]
    for i in range(len(chainA)-1): add_edge(adj,chainA[i],chainA[i+1])
    # B back-path
    aB=list(range(sh+1+vA, sh+1+vA+vB))
    chainB=[shared[sh]]+aB+[shared[0]]
    for i in range(len(chainB)-1): add_edge(adj,chainB[i],chainB[i+1])
    return n,adj

# ---- 3. C5[q] blowup with an extra odd cycle attached -------------------
def C5q(q):
    n=5*q; vid=lambda i,j:i*q+j; adj=[set() for _ in range(n)]
    for i in range(5):
        for a in range(q):
            for b in range(q):
                u=vid(i,a); v=vid((i+1)%5,b); add_edge(adj,u,v)
    return n,adj,vid

# C5[q] with a long odd-cycle "ear" attached spanning two parts (adds an ell=7+ bad edge)
def C5q_with_ear(q,earlen):
    # earlen = number of new vertices forming a path between two C5[q] vertices in the SAME part-distance
    n0,adj,vid=C5q(q)
    # attach a path of length L (earlen edges) between vid(0,0) and vid(2,0).
    # In C5, parts 0 and 2 are at cyclic distance 2; a path of even length keeps bipartite-ish?
    # We just append fresh vertices; bad edges emerge after maxcut.
    base=len(adj)
    new=[base+i for i in range(earlen-1)]
    for x in new: adj.append(set())
    chain=[vid(0,0)]+new+[vid(2,0)]
    for i in range(len(chain)-1): add_edge(adj,chain[i],chain[i+1])
    return len(adj),adj

if __name__=="__main__":
    print("=== two odd cycles sharing ONE vertex (mixed ell) ===")
    for k1,k2 in [(2,3),(2,4),(3,4),(2,5),(3,5),(4,5)]:
        n,adj=two_cycles_share_vertex(k1,k2)
        run(f"C{2*k1+1}+C{2*k2+1} @vertex",n,adj)

    print("\n=== two odd cycles sharing a PATH (edge / short path) ===")
    for k1,k2,sh in [(2,3,1),(2,3,2),(3,4,1),(3,4,2),(2,4,1),(2,4,2),(2,4,3),
                     (3,5,1),(3,5,2),(4,5,2),(2,5,1),(2,5,3)]:
        res=two_cycles_share_path(k1,k2,sh)
        if res is None: continue
        n,adj=res
        run(f"C{2*k1+1}+C{2*k2+1} sharePath(sh={sh})",n,adj)

    print("\n=== C5[q] blowup + odd-cycle ear (mixed ell, B large) ===")
    for q in [2,3]:
        for earlen in [4,5,6,7,8]:
            res=C5q_with_ear(q,earlen)
            if res is None: continue
            n,adj=res
            if n>26: continue
            run(f"C5[{q}]+ear(len={earlen})",n,adj)

    print("\n=== SUMMARY ===")
    obstr=[x for x in RESULTS if "OBSTRUCTION" in x[2]]
    nopeel=[x for x in RESULTS if x[2] and "NO SAFE PEEL" in x[2]]
    print(f"tested={len(RESULTS)}  obstructions(tight,no-peel)={len(obstr)}  no-peel(any)={len(nopeel)}")
    for nm,r,tg in obstr: print("  OBSTR:",nm,r.get("N"),r.get("m"),r.get("gamma"),r.get("n2"))
    for nm,r,tg in nopeel: print("  NOPEEL:",nm,r.get("N"),r.get("m"),r.get("gamma"),r.get("n2"))
