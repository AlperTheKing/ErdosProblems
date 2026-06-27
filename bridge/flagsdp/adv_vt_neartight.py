#!/usr/bin/env python3
"""Adversarial angle (vertex-transitive, part 2): NEAR-TIGHT structured graphs.
Since C5[q] is the unique extremal (Gamma=N^2) family, any obstruction must be ON or very
near it. Test:
  - unbalanced C5[q1..q5] blow-ups (still vertex-edge structured, Gamma can be close to N^2)
  - C5[q] with one part split / one extra vertex (Mycielski-like) keeping triangle-free
  - C5[q] PLUS sparse extra bad edges inside a structured pattern
  - vertex-transitive Cayley graphs on Z_n that ARE the C5 blow-up in disguise
  - blow-ups of C7, C9 (odd cycles) which are sub-tight but structured
Report ratio gamma/N^2 and safe_peel; flag any tight (ratio=1) m>=2 with safe_peel False.
"""
from peel_check import check_instance

def empty(n): return [set() for _ in range(n)]
def add(adj,u,v):
    if u!=v: adj[u].add(v); adj[v].add(u)

def report(name,n,adj,side=None):
    r=check_instance(n,adj,side=side)
    tag=""
    if r.get("ok") and r.get("triangle_free") and r.get("B_connected") and r.get("ge_n2") and (r.get("m") or 0)>=2 and r.get("has_safe_peel") is False:
        tag="  <<< OBSTRUCTION!!!"
    g=r.get("gamma"); n2=r.get("n2")
    ratio=(g/n2) if (g and n2) else float('nan')
    print(f"{name}: ok={r.get('ok')} tf={r.get('triangle_free')} N={r.get('N')} Bconn={r.get('B_connected')} "
          f"m={r.get('m')} gamma={g} n2={n2} ratio={ratio:.4f} tight={r.get('tight')} "
          f"safe_peel={r.get('has_safe_peel')} | {r.get('detail')}{tag}",flush=True)
    return r

# unbalanced blow-up of C5 with part sizes q[0..4]
def C5_blowup(q):
    parts=[]; off=0
    for i in range(5):
        parts.append(list(range(off,off+q[i]))); off+=q[i]
    n=off; adj=empty(n)
    for i in range(5):
        for a in parts[i]:
            for b in parts[(i+1)%5]:
                add(adj,a,b)
    return n,adj,parts

# blow-up of odd cycle C_{2k+1} with part sizes q
def Codd_blowup(L,q):
    parts=[]; off=0
    for i in range(L):
        parts.append(list(range(off,off+q[i]))); off+=q[i]
    n=off; adj=empty(n)
    for i in range(L):
        for a in parts[i]:
            for b in parts[(i+1)%L]:
                add(adj,a,b)
    return n,adj,parts

print("=== Unbalanced C5 blow-ups (vertex-transitive-ish, near tight) ===")
import itertools
configs=[
 [3,2,2,2,2],[3,3,2,2,2],[4,2,2,2,2],[3,3,3,2,2],[4,3,2,2,2],
 [2,2,2,2,3],[3,2,3,2,2],[2,3,2,3,2],[4,4,2,2,2],[3,3,3,3,2],
 [5,2,2,2,2],[3,3,2,3,2],[2,2,3,3,2],[4,3,3,2,2],[3,4,2,3,2],
]
for q in configs:
    n,adj,parts=C5_blowup(q)
    report(f"C5{q}",n,adj)

print("\n=== Balanced C5[q] sanity (must be tight + safe_peel True) ===")
for q in [2,3,4]:
    n,adj,parts=C5_blowup([q]*5)
    report(f"C5[{q}]",n,adj)

print("\n=== Odd-cycle C7,C9 blow-ups (structured, sub-tight) ===")
for q in [[2]*7,[3]+[2]*6,[2,2,2,2,2,2,3]]:
    n,adj,parts=Codd_blowup(7,q); report(f"C7{q}",n,adj)
for q in [[2]*9,[2,2,2,2,2,2,2,2,2]]:
    n,adj,parts=Codd_blowup(9,q); report(f"C9{q}",n,adj)

print("\n=== C5[2] with one extra structured bad edge inside a part-pair (perturbation) ===")
# Take balanced C5[2], then ADD an edge between two vertices in non-adjacent parts to create
# a controlled extra bad edge while staying triangle-free; check if it can break the peel.
def C5q_plus(q, extra_edges):
    n,adj,parts=C5_blowup([q]*5)
    for (i,a,j,b) in extra_edges:
        u=parts[i][a]; v=parts[j][b]; add(adj,u,v)
    return n,adj
# add edges between part 0 and part 2 (non-adjacent in C5 => these would be cross or bad depending on cut)
for ee in [[(0,0,2,0)],[(0,0,2,0),(1,0,3,0)],[(0,0,2,0),(0,1,3,0)]]:
    n,adj=C5q_plus(2,ee); report(f"C5[2]+{ee}",n,adj)
