#!/usr/bin/env python3
"""Adversarial angle: VERTEX-TRANSITIVE / structured triangle-free graphs & blow-ups.
Tests Petersen (Kneser K(5,2)), generalized Petersen GP(n,k), triangle-free circulants,
Mobius-Kantor, Heawood, Desargues, Pappus, tensor/lexicographic products of C5, etc.
For each: report N, m, gamma/N^2, tight?, has_safe_peel.
"""
from peel_check import check_instance

def report(name, n, adj, side=None):
    r = check_instance(n, adj, side=side)
    tag = ""
    if r.get("ok") and r.get("triangle_free") and r.get("B_connected") and r.get("ge_n2") and (r.get("m") or 0) >= 2 and r.get("has_safe_peel") is False:
        tag = "  <<< OBSTRUCTION!!!"
    g = r.get("gamma"); n2 = r.get("n2")
    ratio = (g / n2) if (g and n2) else float('nan')
    print(f"{name}: ok={r.get('ok')} tf={r.get('triangle_free')} N={r.get('N')} maxcut={r.get('maxcut')} "
          f"Bconn={r.get('B_connected')} m={r.get('m')} gamma={g} n2={n2} ratio={ratio:.4f} "
          f"tight={r.get('tight')} ge_n2={r.get('ge_n2')} safe_peel={r.get('has_safe_peel')} | {r.get('detail')}{tag}",
          flush=True)
    return r

def empty(n): return [set() for _ in range(n)]
def add(adj,u,v):
    if u!=v: adj[u].add(v); adj[v].add(u)

# ---- Generalized Petersen GP(n,k): outer cycle 0..n-1, inner 0'..(n-1)' with step k ----
def GP(n,k):
    N=2*n; adj=empty(N)
    out=lambda i:i; inn=lambda i:n+i
    for i in range(n):
        add(adj,out(i),out((i+1)%n))      # outer cycle
        add(adj,out(i),inn(i))            # spokes
        add(adj,inn(i),inn((i+k)%n))      # inner
    return N,adj

# ---- Circulant C_n(S) ----
def circulant(n,S):
    adj=empty(n)
    for i in range(n):
        for s in S:
            add(adj,i,(i+s)%n)
    return n,adj

# ---- Kneser K(5,2) = Petersen ----
def kneser52():
    from itertools import combinations
    verts=list(combinations(range(5),2))
    idx={v:i for i,v in enumerate(verts)}
    N=len(verts); adj=empty(N)
    for a in verts:
        for b in verts:
            if a<b and not (set(a)&set(b)):
                add(adj,idx[a],idx[b])
    return N,adj

# ---- C5 lexicographic (blow-up already = C5[q]); tensor product C5 x K2, C5 x Cm ----
def tensor(adjs1, n1, adjs2, n2):
    # tensor (categorical) product: (u1,u2)~(v1,v2) iff u1~v1 and u2~v2
    N=n1*n2; adj=empty(N); vid=lambda a,b:a*n2+b
    for u1 in range(n1):
        for v1 in adjs1[u1]:
            for u2 in range(n2):
                for v2 in adjs2[u2]:
                    add(adj,vid(u1,u2),vid(v1,v2))
    return N,adj

def cycle(n):
    adj=empty(n)
    for i in range(n): add(adj,i,(i+1)%n)
    return n,adj

print("=== Generalized Petersen GP(n,k) ===")
for (n,k) in [(5,2),(7,2),(8,3),(9,2),(10,2),(10,3),(11,2),(12,5),(13,5)]:
    N,adj=GP(n,k)
    report(f"GP({n},{k})",N,adj)

print("\n=== Kneser K(5,2)=Petersen ===")
N,adj=kneser52(); report("Kneser(5,2)",N,adj)

print("\n=== Triangle-free circulants ===")
# choose S with no a+b=c mod n among +-S to stay triangle free (we let harness verify)
circ_tests=[
 (10,[2,3]),(11,[2,3]),(12,[2,3]),(13,[2,3]),(13,[1,5]),(14,[3,5]),
 (12,[1,5]),(15,[1,4]),(16,[1,7]),(13,[2,5]),(17,[1,4]),(18,[1,8]),
 (10,[1,4]),(11,[1,4]),(11,[1,5]),(13,[3,4]),(14,[1,6]),
]
for (n,S) in circ_tests:
    N,adj=circulant(n,S); report(f"C_{n}({S})",N,adj)

print("\n=== Heawood (incidence Fano) GP(7,2)-like / bipartite cubic girth6 ===")
# Heawood graph: bipartite, C14 with chords i ~ i+5 alternation; standard: vertices 0..13
adj=empty(14)
for i in range(14): add(adj,i,(i+1)%14)
for i in range(0,14,2): add(adj,i,(i+5)%14)
report("Heawood",14,adj)

print("\n=== Tensor products ===")
n1,a1=cycle(5)
for m in [3,4,5,6,7]:
    n2,a2=cycle(m)
    N,adj=tensor(a1,n1,a2,n2)
    report(f"C5 x C{m} (tensor)",N,adj)
