#!/usr/bin/env python3
"""Vertex-transitive angle, trimmed to feasible N<=24 (brute maxcut 2^(n-1)).
Circulants, Kneser(5,2)=Petersen, Heawood, Mobius-Kantor GP(8,3), Desargues GP(10,3),
Pappus, Nauru GP(12,5), tensor C5xK2 / C5xC3 (N<=20), and larger even odd-cycle blow-ups
(the discovered tight family). Flag tight m>=2 safe_peel False as obstruction."""
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

def circulant(n,S):
    adj=empty(n)
    for i in range(n):
        for s in S: add(adj,i,(i+s)%n)
    return n,adj

def GP(n,k):
    N=2*n; adj=empty(N)
    for i in range(n):
        add(adj,i,(i+1)%n); add(adj,i,n+i); add(adj,n+i,n+((i+k)%n))
    return N,adj

def cycle(n):
    adj=empty(n)
    for i in range(n): add(adj,i,(i+1)%n)
    return n,adj

def tensor(a1,n1,a2,n2):
    N=n1*n2; adj=empty(N); vid=lambda a,b:a*n2+b
    for u1 in range(n1):
        for v1 in a1[u1]:
            for u2 in range(n2):
                for v2 in a2[u2]:
                    add(adj,vid(u1,u2),vid(v1,v2))
    return N,adj

print("=== Triangle-free circulants (N<=22) ===")
circ_tests=[(10,[2,3]),(11,[2,3]),(12,[2,3]),(13,[2,3]),(13,[1,5]),(14,[3,5]),
 (12,[1,5]),(13,[2,5]),(10,[1,4]),(11,[1,4]),(11,[1,5]),(13,[3,4]),(14,[1,6]),
 (15,[1,4]),(16,[1,7]),(17,[1,4]),(18,[1,8]),(20,[1,9]),(22,[1,10]),
 (13,[1,3,4]),(11,[2,3,5]),(13,[2,3,5])]
for (n,S) in circ_tests:
    N,adj=circulant(n,S); report(f"C_{n}({S})",N,adj)

print("\n=== Named cubic vertex-transitive (girth>=5) ===")
from itertools import combinations
verts=list(combinations(range(5),2)); idx={v:i for i,v in enumerate(verts)}
adjK=empty(len(verts))
for a in verts:
    for b in verts:
        if a<b and not(set(a)&set(b)): add(adjK,idx[a],idx[b])
report("Kneser(5,2)=Petersen",len(verts),adjK)
adjH=empty(14)
for i in range(14): add(adjH,i,(i+1)%14)
for i in range(0,14,2): add(adjH,i,(i+5)%14)
report("Heawood",14,adjH)
N,adj=GP(8,3); report("MobiusKantor GP(8,3)",N,adj)
N,adj=GP(10,3); report("Desargues GP(10,3)",N,adj)
N,adj=GP(12,5); report("Nauru GP(12,5)",N,adj)
# Pappus graph (bipartite cubic girth6, 18 vertices) LCF [5,7,-7,7,-7,-5]^3
def pappus():
    lcf=[5,7,-7,7,-7,-5]*3; n=18; adj=empty(n)
    for i in range(n): add(adj,i,(i+1)%n)
    for i in range(n): add(adj,i,(i+lcf[i])%n)
    return n,adj
N,adj=pappus(); report("Pappus",N,adj)

print("\n=== Tensor products (feasible) ===")
n1,a1=cycle(5)
for m in [2,3,4]:
    if m==2:
        a2=empty(2); add(a2,0,1); n2=2
    else:
        n2,a2=cycle(m)
    N,adj=tensor(a1,n1,a2,n2)
    report(f"C5 x C{m} (tensor)",N,adj)

print("\n=== Larger even blow-ups of odd cycles (the TIGHT family) ===")
def Codd_blowup(L,q):
    parts=[]; off=0
    for i in range(L):
        parts.append(list(range(off,off+q))); off+=q
    n=off; adj=empty(n)
    for i in range(L):
        for a in parts[i]:
            for b in parts[(i+1)%L]:
                add(adj,a,b)
    return n,adj
for (L,q) in [(5,4),(7,3),(9,2),(11,2)]:
    n,adj=Codd_blowup(L,q)
    if n<=24: report(f"C{L}[{q}] blowup",n,adj)
