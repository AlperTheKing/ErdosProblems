#!/usr/bin/env python3
"""Stress-test the claim U (max_v T_uniform <= K = N+(N^2-Gamma)) in the TIGHT regime:
odd-cycle blow-ups and perturbations where Gamma is near N^2.
EXACT Fractions only. Re-confirm any violation independently."""
import sys
from fractions import Fraction as Fr
from census_GPI import dec, maxcut_all, gmin, geos

def build_adj(n, E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def T_uniform(n, adj, side, M, ell):
    """exact T_uniform vector using Fractions."""
    T=[Fr(0)]*n
    for f in M:
        Ps=geos(adj,side,f[0],f[1])
        nf=len(Ps)
        if nf==0: return None  # should not happen for valid bad geodesic
        share=Fr(ell[f], nf)
        for P in Ps:
            for v in P:
                T[v]+=share
    return T

def cyclic_blowup(k, sizes):
    """C_k blow-up (k odd) with given group sizes (len k). Complete bipartite between consecutive groups cyclically."""
    assert len(sizes)==k
    offs=[0]
    for s in sizes: offs.append(offs[-1]+s)
    n=offs[-1]
    E=[]
    for i in range(k):
        j=(i+1)%k
        for a in range(sizes[i]):
            for b in range(sizes[j]):
                E.append((offs[i]+a, offs[j]+b))
    return n,E

def check(label, n, E, brute=True):
    adj=build_adj(n,E)
    cuts=maxcut_all(n,adj)
    r=gmin(n,adj,cuts)
    if r is None:
        print(f"  {label}: N={n} no connected-B max cut with bad edges (Gamma undefined)")
        return None
    side,G,M,ell=r
    K=n + (n*n - G)
    T=T_uniform(n,adj,side,M,ell)
    if T is None:
        print(f"  {label}: N={n} T_uniform geodesic-count zero (bug?)")
        return None
    maxT=max(T)
    slack=Fr(K)-maxT
    viol = maxT > K
    print(f"  {label}: N={n} Gamma={G} K={K} maxT={maxT}({float(maxT):.4f}) slack(K-maxT)={slack}({float(slack):.4f}) VIOL={viol}")
    return dict(label=label,n=n,G=G,K=K,maxT=maxT,slack=slack,viol=viol,side=side,M=M,ell=ell)

results=[]

print("=== C5[t] t=2..8 ===")
def blow5(t): return cyclic_blowup(5,[t]*5)
for t in range(2,9):
    n,E=blow5(t)
    if n<=20:
        results.append(check(f"C5[{t}]",n,E))
    else:
        print(f"  C5[{t}]: N={n} >20 skip brute")

print("=== C7[t],C9[t],C11[t] t=1..4 (N<=20) ===")
for k in (7,9,11):
    for t in range(1,5):
        n,E=cyclic_blowup(k,[t]*k)
        if n<=20:
            results.append(check(f"C{k}[{t}]",n,E))
        else:
            print(f"  C{k}[{t}]: N={n} >20 skip")

print("=== Unbalanced C5 blow-ups (N<=20) ===")
unbal=[(3,2,2,2,1),(4,1,1,1,1),(2,2,2,2,1),(3,3,2,2,1),(4,4,4,4,1),
       (4,3,3,3,1),(5,5,5,5,1),(3,3,3,3,2),(4,4,3,3,2),(5,4,3,2,1),
       (2,2,2,2,2),(3,3,3,3,3),(4,4,4,4,4),(2,3,2,3,2),(1,1,1,1,1),
       (6,1,1,1,1),(3,2,3,2,3),(4,4,4,1,1),(5,5,4,4,2)]
for sizes in unbal:
    n=sum(sizes)
    if n>20:
        print(f"  C5{sizes}: N={n} >20 skip"); continue
    nn,E=cyclic_blowup(5,list(sizes))
    results.append(check(f"C5{sizes}",nn,E))

print("=== C7/C9 unbalanced (N<=20) ===")
for sizes in [(2,1,1,1,1,1,1),(2,2,1,1,1,1,1),(2,2,2,1,1,1,1),(3,2,2,1,1,1,1),
              (2,2,2,2,1,1,1),(2,2,2,2,2,1,1),(3,1,1,1,1,1,1)]:
    nn,E=cyclic_blowup(7,list(sizes))
    if nn<=20: results.append(check(f"C7{sizes}",nn,E))
for sizes in [(2,1,1,1,1,1,1,1,1),(2,2,1,1,1,1,1,1,1),(2,2,2,1,1,1,1,1,1),
              (2,2,2,2,1,1,1,1,1),(2,2,2,2,2,1,1,1,1)]:
    nn,E=cyclic_blowup(9,list(sizes))
    if nn<=20: results.append(check(f"C9{sizes}",nn,E))

print("=== Blow-ups with one EXTRA edge (must stay triangle-free) ===")
# Add an edge between two groups two apart (chord). For C5[t], groups i and i+2 are at B-distance 2,
# adding an edge between them: vertex in group i and group i+2. Need to keep triangle-free.
# In C5[t], group i connects to i-1,i+1. group i+2 connects to i+1,i+3. Common neighbor group i+1 =>
# adding edge (i-group, i+2-group) creates triangle with any vertex in i+1? No: triangle needs all 3 pairwise.
# i and i+2 both adjacent to i+1; pick u in i, w in i+2, x in i+1: u-x edge, w-x edge, u-w new edge => triangle. So unsafe.
# Instead add an edge within structure that keeps tri-free: add a pendant or an edge between same-parity far groups in larger cycle.
# For C7[t]: groups i and i+3 are at distance 3, no common neighbor => safe to add chord.
for t in (2,3):
    nn,E=cyclic_blowup(7,[t]*7)
    if nn>20: continue
    offs=[i*t for i in range(7)]
    Ex=E+[(offs[0]+0, offs[3]+0)]  # chord groups 0 and 3 (dist 3, tri-free)
    results.append(check(f"C7[{t}]+chord(0,3)",nn,Ex))

print("=== Blow-ups with one MISSING edge ===")
for t in (2,3,4):
    nn,E=cyclic_blowup(5,[t]*5)
    if nn>20: continue
    Em=E[1:]  # drop first edge
    results.append(check(f"C5[{t}]-edge",nn,Em))
for t in (1,2):
    nn,E=cyclic_blowup(7,[t]*7)
    if nn>20: continue
    Em=E[1:]
    results.append(check(f"C7[{t}]-edge",nn,Em))

results=[r for r in results if r is not None]
viols=[r for r in results if r['viol']]
minslack=min((r['slack'] for r in results), default=None)
ms=min(results,key=lambda r:r['slack']) if results else None
print("\n=== SUMMARY ===")
print(f"tested={len(results)} violations={len(viols)}")
if ms: print(f"min slack (K-maxT) = {ms['slack']} ({float(ms['slack']):.6f}) at {ms['label']} N={ms['n']} Gamma={ms['G']} K={ms['K']} maxT={ms['maxT']}")
for r in viols:
    print(f"  VIOLATION {r['label']} N={r['n']} Gamma={r['G']} K={r['K']} maxT={r['maxT']}")
