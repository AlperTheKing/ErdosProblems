#!/usr/bin/env python3
"""Necklace BLOW-UPS and tight-targeting constructions for the safe-peel lemma.

Sparse necklaces have Gamma << N^2 (Gamma ~ 25*#cycles, N ~ 4*#cycles).
Tightness (Gamma=N^2) requires blow-up. Here we blow up necklace structures and
also build the canonical tight C5[q] and perturbations, plus C5[q] necklaces.
"""
import sys
sys.path.insert(0, '/e/Projects/ErdosProblems/bridge/flagsdp')
from peel_check import check_instance

def report(name, n, adj):
    if n>26:
        print(f"{name}: SKIP N={n}>26 (brute maxcut/CD too big)")
        return None, False
    r=check_instance(n,adj)
    obstruction = (r.get("ok") and r.get("triangle_free") and r.get("B_connected")
                   and r.get("ge_n2") and r.get("m",0)>=2 and r.get("has_safe_peel") is False)
    flag = "  <<< OBSTRUCTION" if obstruction else ""
    near=""
    if r.get("ok") and r.get("gamma") is not None and r.get("n2"):
        ratio=r["gamma"]/r["n2"]
        if 0.85<=ratio<1.0 and r.get("m",0)>=2:
            near=f"  [NEAR-TIGHT {ratio:.4f} sp={r.get('has_safe_peel')}]"
    print(f"{name}: N={r.get('N')} m={r.get('m')} gamma={r.get('gamma')} n2={r.get('n2')} "
          f"ratio={ (r['gamma']/r['n2']) if (r.get('gamma') and r.get('n2')) else None } "
          f"tight={r.get('tight')} sp={r.get('has_safe_peel')} "
          f"Bconn={r.get('B_connected')} tf={r.get('triangle_free')} | {r.get('detail')}{flag}{near}")
    return r, obstruction

def blowup(n0, adj0, mult):
    """blow up: replace each vertex by mult[v] copies; copies of u,v adjacent iff u~v. triangle-free preserved iff orig triangle-free AND no vertex has a self-loop (it doesn't)."""
    parts=[]; start=0
    for v in range(n0):
        parts.append(list(range(start, start+mult[v]))); start+=mult[v]
    N=start
    adj=[set() for _ in range(N)]
    for u in range(n0):
        for v in adj0[u]:
            if v>u:
                for a in parts[u]:
                    for b in parts[v]:
                        adj[a].add(b); adj[b].add(a)
    return N, adj

# base C5 cycle
def C5():
    adj=[set() for _ in range(5)]
    for i in range(5): adj[i].add((i+1)%5); adj[(i+1)%5].add(i)
    return 5,adj

def C7():
    adj=[set() for _ in range(7)]
    for i in range(7): adj[i].add((i+1)%7); adj[(i+1)%7].add(i)
    return 7,adj

# vertex-path of 2 C5 (the 9-vertex bowtie-ish), then blow up
def vpath_C5_2():
    # cycle0: 0-1-2-3-4-0 ; cycle1 shares vertex 4: 4-5-6-7-8-4
    edges=[(0,1),(1,2),(2,3),(3,4),(4,0),(4,5),(5,6),(6,7),(7,8),(8,4)]
    n=9; adj=[set() for _ in range(n)]
    for u,v in edges: adj[u].add(v); adj[v].add(u)
    return n,adj

# edge-path of 2 C5 sharing one edge (8 vertices, m might be 1)
def epath_C5_3():
    # 3 C5 sharing edges in a path -> from earlier this gave m=2 N=11
    edges=[]
    nxt=0; prev=None
    for c in range(3):
        if prev is None:
            verts=[0,1,2,3,4]; nxt=5
        else:
            a,b=prev; verts=[a,b,nxt,nxt+1,nxt+2]; nxt+=3
        L=len(verts)
        for i in range(L): edges.append((verts[i],verts[(i+1)%L]))
        prev=(verts[-1],verts[0])
    vs=sorted({x for e in edges for x in e}); idx={v:i for i,v in enumerate(vs)}
    n=len(vs); adj=[set() for _ in range(n)]
    for u,v in edges:
        a,b=idx[u],idx[v]
        if a!=b: adj[a].add(b); adj[b].add(a)
    return n,adj

if __name__=="__main__":
    print("=== canonical tight C5[q] sanity ===")
    for q in (2,3,4,5):
        n,adj=blowup(*C5(), [q]*5); report(f"C5[{q}]", n, adj)

    print("=== UNBALANCED C5 blow-ups (perturb part sizes; near-tight) ===")
    import itertools
    n0,a0=C5()
    for mult in [(3,3,3,3,2),(4,4,4,4,3),(4,4,4,3,3),(5,5,5,4,4),(5,5,4,4,4),
                 (4,3,4,3,4),(5,4,5,4,4),(3,2,3,2,3),(4,4,3,3,2),(5,5,5,5,3)]:
        n,adj=blowup(n0,a0,list(mult)); report(f"C5{mult}", n, adj)

    print("=== C7 blow-ups (odd cycle, less tight) ===")
    n0,a0=C7()
    for q in (2,3):
        n,adj=blowup(n0,a0,[q]*7); report(f"C7[{q}]", n, adj)

    print("=== vertex-path 2xC5 BLOW-UPS ===")
    n0,a0=vpath_C5_2()  # shared vertex is index 4
    for base in (2,3):
        mult=[base]*9; report(f"vpath2_blow{base}", *blowup(n0,a0,mult))
    # blow up only the two cycles' free verts more, keep shared small
    report("vpath2_mixA", *blowup(n0,a0,[2,2,2,2,1,2,2,2,2]))
    report("vpath2_mixB", *blowup(n0,a0,[3,3,3,3,2,3,3,3,3]))
    report("vpath2_mixC", *blowup(n0,a0,[2,3,3,2,1,2,3,3,2]))

    print("=== edge-path 3xC5 BLOW-UPS ===")
    n0,a0=epath_C5_3()
    print(f"  (base epath_C5_3 N={n0})")
    for base in (2,):
        report(f"epath3_blow{base}", *blowup(n0,a0,[base]*n0))
