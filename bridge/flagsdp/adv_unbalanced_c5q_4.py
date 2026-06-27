#!/usr/bin/env python3
"""Angle 4 (lean, unbuffered): C9[q] + exhaustive asymmetric C5 blow-ups sizes 1..5 (N<=20)
using the harness auto-pick (fast). Confirm NO unbalanced blow-up reaches Gamma>=N^2 with m>=2,
and ALL m>=2 tight balanced cases have safe peels."""
import sys, itertools
from peel_check import check_instance

def Ck_blowup(k, sizes):
    n=sum(sizes); off=[0]*k
    for i in range(1,k): off[i]=off[i-1]+sizes[i-1]
    adj=[set() for _ in range(n)]
    def pv(i): return range(off[i],off[i]+sizes[i])
    for i in range(k):
        j=(i+1)%k
        for u in pv(i):
            for v in pv(j): adj[u].add(v); adj[v].add(u)
    return n,adj

def fmt(tag,r):
    return (f"{tag} N={r.get('N')} m={r.get('m')} gamma={r.get('gamma')} n2={r.get('n2')} "
            f"tight={r.get('tight')} safe={r.get('has_safe_peel')} | {r['detail']}")

obstructions=[]; tested=0; unbalanced_tight=0; balanced_tight_safe=0

print("=== C9[q] ===", flush=True)
for q in (1,2):
    n=9*q
    if n>20: continue
    nn,adj=Ck_blowup(9,(q,)*9); r=check_instance(nn,adj); tested+=1
    print(fmt(f"C9[{q}]",r), flush=True)
    if r.get('ge_n2') and (r.get('m') or 0)>=2 and r.get('has_safe_peel') is False:
        obstructions.append((f"C9[{q}]",r))

print("=== asymmetric C5 sizes 1..5, N<=20, non-uniform (auto max-cut) ===", flush=True)
for sizes in itertools.product(range(1,6),repeat=5):
    if len(set(sizes))==1: continue
    n=sum(sizes)
    if n<10 or n>20: continue
    rots=[tuple(sizes[i:]+sizes[:i]) for i in range(5)]
    rev=tuple(reversed(sizes)); rots+=[tuple(rev[i:]+rev[:i]) for i in range(5)]
    if sizes!=min(rots): continue
    nn,adj=Ck_blowup(5,sizes); r=check_instance(nn,adj); tested+=1
    if r.get('ge_n2') and r.get('B_connected') and (r.get('m') or 0)>=2:
        unbalanced_tight+=1
        print("UNBALANCED ge_n2:",fmt(str(sizes),r), flush=True)
        if r.get('has_safe_peel') is False:
            obstructions.append((str(sizes),r))
            print("  <<< OBSTRUCTION", flush=True)

print(f"=== SUMMARY === tested={tested} unbalanced_ge_n2(m>=2)={unbalanced_tight} obstructions={len(obstructions)}", flush=True)
for tag,r in obstructions: print("OBSTRUCTION:",fmt(tag,r), flush=True)
print("DONE", flush=True)
