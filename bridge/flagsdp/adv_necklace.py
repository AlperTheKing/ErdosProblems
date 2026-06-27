#!/usr/bin/env python3
"""Adversarial necklace-chain tester for the Erdos #23 safe-peel lemma.

Builds odd-cycle chains (C5/C7) sharing single vertices or single edges, in paths
and rings, plus small blow-ups, and runs each through check_instance.
"""
import sys, itertools
sys.path.insert(0, '/e/Projects/ErdosProblems/bridge/flagsdp')
from peel_check import check_instance

def cycle(verts):
    """edge list of a cycle through given vertex sequence."""
    e=[]
    L=len(verts)
    for i in range(L):
        e.append((verts[i], verts[(i+1)%L]))
    return e

def build(edges):
    """vertex-relabel to 0..n-1, return (n, adj)."""
    vs=sorted({x for e in edges for x in e})
    idx={v:i for i,v in enumerate(vs)}
    n=len(vs)
    adj=[set() for _ in range(n)]
    for (u,v) in edges:
        a,b=idx[u],idx[v]
        if a!=b:
            adj[a].add(b); adj[b].add(a)
    return n,adj

def report(name, n, adj):
    r=check_instance(n,adj)
    obstruction = (r.get("ok") and r.get("triangle_free") and r.get("B_connected")
                   and r.get("ge_n2") and r.get("m",0)>=2 and r.get("has_safe_peel") is False)
    flag = "  <<< OBSTRUCTION" if obstruction else ""
    near = ""
    if r.get("ok") and r.get("gamma") is not None and r.get("n2"):
        ratio = r["gamma"]/r["n2"]
        if 0.90 <= ratio < 1.0 and r.get("m",0)>=2:
            near = f"  [near-tight {ratio:.4f}]"
    print(f"{name}: N={r.get('N')} m={r.get('m')} gamma={r.get('gamma')} n2={r.get('n2')} "
          f"tight={r.get('tight')} ge_n2={r.get('ge_n2')} safe_peel={r.get('has_safe_peel')} "
          f"Bconn={r.get('B_connected')} tf={r.get('triangle_free')} | {r.get('detail')}{flag}{near}")
    return r, obstruction

# ---- FAMILY 1: chain of k C5's sharing a single VERTEX between consecutive cycles (path) ----
def vertex_path_C5(k):
    """k C5's; cycle i uses 5 new verts except shares its first vertex with prev cycle's last."""
    edges=[]
    nxt=0
    prev_last=None
    for c in range(k):
        if prev_last is None:
            verts=[nxt+j for j in range(5)]; nxt+=5
        else:
            verts=[prev_last]+[nxt+j for j in range(4)]; nxt+=4
        edges+=cycle(verts)
        prev_last=verts[-1]   # share last vertex of this cycle as first of next
    return build(edges)

# ---- FAMILY 2: ring of k C5's sharing single vertices (necklace) ----
def vertex_ring_C5(k):
    """k C5's arranged in a ring; consecutive cycles share one vertex, and last shares with first."""
    # shared vertices s_0..s_{k-1}; cycle c connects s_c -> 3 fresh -> s_{c+1}
    edges=[]
    shared=list(range(k))   # 0..k-1
    nxt=k
    for c in range(k):
        a=shared[c]; b=shared[(c+1)%k]
        mid=[nxt,nxt+1,nxt+2]; nxt+=3
        verts=[a]+mid+[b]
        edges+=cycle(verts)   # 5-cycle a-m0-m1-m2-b-a
    return build(edges)

# ---- FAMILY 3: chain of k C5's sharing a single EDGE between consecutive cycles (path) ----
def edge_path_C5(k):
    """k C5's; consecutive cycles share one edge (2 vertices)."""
    edges=[]
    nxt=0
    prev_edge=None
    for c in range(k):
        if prev_edge is None:
            verts=[nxt+j for j in range(5)]; nxt+=5
        else:
            # share edge (prev_edge[0], prev_edge[1]); add 3 fresh between
            a,b=prev_edge
            mid=[nxt,nxt+1,nxt+2]; nxt+=3
            verts=[a,b]+mid     # 5-cycle a-b-m0-m1-m2-a   (a-b is the shared edge)
        edges+=cycle(verts)
        prev_edge=(verts[-1], verts[0])  # share the closing edge
    return build(edges)

# ---- FAMILY 4: ring of k C5's sharing single edges ----
def edge_ring_C5(k):
    edges=[]
    # shared edges e_c = (a_c, b_c); but simpler: shared vertices in pairs
    # Build: 2k 'rim' vertices forming the shared edges, plus 3 fresh per cycle
    nxt=0
    rim=[]
    for c in range(k):
        rim.append((nxt,nxt+1)); nxt+=2
    for c in range(k):
        a,b=rim[c]
        a2,b2=rim[(c+1)%k]
        mid=[nxt]; nxt+=1
        # 5-cycle: a-b-mid-? need length 5; use a-b shared edge then b-mid- a2-?
        # Simpler 5-cycle sharing edge (a,b) and edge (a2,b2): a-b-x-a2-b2? that's 5 verts if x fresh
        verts=[a,b,mid[0],a2,b2]
        edges+=cycle(verts)
    return build(edges)

# ---- FAMILY 5: mixed C5/C7 vertex path ----
def vertex_path_mixed(pattern):
    """pattern e.g. [5,7,5]; consecutive cycles share one vertex."""
    edges=[]; nxt=0; prev_last=None
    for L in pattern:
        if prev_last is None:
            verts=[nxt+j for j in range(L)]; nxt+=L
        else:
            verts=[prev_last]+[nxt+j for j in range(L-1)]; nxt+=L-1
        edges+=cycle(verts)
        prev_last=verts[-1]
    return build(edges)

def vertex_ring_mixed(pattern):
    edges=[]
    k=len(pattern)
    shared=list(range(k)); nxt=k
    for c,L in enumerate(pattern):
        a=shared[c]; b=shared[(c+1)%k]
        mid=[nxt+j for j in range(L-2)]; nxt+=L-2
        verts=[a]+mid+[b]
        edges+=cycle(verts)
    return build(edges)

if __name__=="__main__":
    print("=== FAMILY 1: vertex-path C5 chains ===")
    for k in range(2,7):
        n,adj=vertex_path_C5(k); report(f"vpath_C5^{k}", n, adj)
    print("=== FAMILY 2: vertex-ring C5 necklaces ===")
    for k in range(3,8):
        n,adj=vertex_ring_C5(k); report(f"vring_C5^{k}", n, adj)
    print("=== FAMILY 3: edge-path C5 chains ===")
    for k in range(2,7):
        n,adj=edge_path_C5(k); report(f"epath_C5^{k}", n, adj)
    print("=== FAMILY 4: edge-ring C5 necklaces ===")
    for k in range(3,8):
        n,adj=edge_ring_C5(k); report(f"ering_C5^{k}", n, adj)
    print("=== FAMILY 5: mixed C5/C7 vertex paths ===")
    for pat in ([5,7],[7,5],[5,7,5],[7,5,7],[5,5,7],[5,7,7],[7,7,5],[5,7,5,7]):
        n,adj=vertex_path_mixed(pat); report(f"vpath_mix_{pat}", n, adj)
    print("=== FAMILY 6: mixed C5/C7 vertex rings ===")
    for pat in ([5,5,5],[5,5,7],[5,7,7],[7,7,7],[5,5,5,5],[5,5,7,7]):
        n,adj=vertex_ring_mixed(pat); report(f"vring_mix_{pat}", n, adj)
