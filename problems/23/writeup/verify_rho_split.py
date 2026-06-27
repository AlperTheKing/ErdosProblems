#!/usr/bin/env python3
"""EXACT check of GPT-Pro round-3's reduction before adopting it (#23 delta=0, cut-pressure NRS).
Claim: at a fixed-density KKT maximizer, edge-slack S_ij=A_ij(P_ij-alpha)>=0, weight-stationarity
forces sum_j w_j S_ij = rho (weighted-regular), and F = alpha*D + rho; High-F no-slack <=> rho=0.

We verify the ALGEBRA at the exact C5 anchor and illustrate the band rho>0 mechanism.
Uniform weights w_i=1/n (the step graphon of a simple graph). P = same-side prob over ALL max cuts.
alpha* := min over edges of P_ij  (the MAXIMAL alpha keeping S>=0 on the edge support).
rho_i := sum_{j~i} (1/n)(P_ij - alpha*).   F = 2 beta/n^2,  D = 2 e/n^2 = sum_i (1/n) deg_i /n ... (graphon).
Energy split to test:  F ?= alpha* * D + rho_avg, with rho_avg = (1/n) sum_i rho_i = sum_edges 2 w_i w_j S_ij.
"""
from fractions import Fraction as F
import itertools

def maxcut_opt(n, edges):
    best=-1; opt=[]
    for m in range(1<<n):
        c=sum(1 for (u,v) in edges if ((m>>u)&1)!=((m>>v)&1))
        if c>best: best=c; opt=[m]
        elif c==best: opt.append(m)
    return best,opt

def analyze(name,n,edges):
    adj=[set() for _ in range(n)]
    for a,b in edges: adj[a].add(b); adj[b].add(a)
    mc,opt=maxcut_opt(n,edges); beta=len(edges)-mc; K=len(opt)
    w=F(1,n)
    Pe={}
    for (u,v) in edges:
        same=sum(1 for m in opt if ((m>>u)&1)==((m>>v)&1))
        Pe[(u,v)]=F(same,K)
    alpha=min(Pe.values())                      # maximal alpha keeping S>=0 on edges
    # rho_i = sum_{j~i} w (P_ij - alpha)
    rho=[F(0)]*n
    for (u,v) in edges:
        s=Pe[(u,v)]-alpha
        rho[u]+=w*s; rho[v]+=w*s
    regular = len(set(rho))==1
    rho_avg=sum(rho)*w                          # (1/n) sum_i rho_i
    Fval=F(2*beta,n*n)
    D=F(2*len(edges),n*n)
    # energy split: alpha*D + rho_avg
    split=alpha*D+rho_avg
    print(f"{name:10} n={n} e={len(edges)} beta={beta} #maxcuts={K}")
    print(f"   edge-pressures P_ij distinct: {sorted(str(x) for x in set(Pe.values()))}")
    print(f"   alpha* (min edge P) = {alpha} = {float(alpha):.4f}")
    print(f"   rho_i = {[str(r) for r in rho]}")
    print(f"   weighted-regular (all rho_i equal)? {regular}   rho_avg = {rho_avg} = {float(rho_avg):.5f}")
    print(f"   F=2beta/n^2 = {Fval}={float(Fval):.5f}   alpha*D+rho_avg = {split}={float(split):.5f}   split holds? {Fval==split}")
    print(f"   => rho_avg {'== 0 (NO slack: C5-type)' if rho_avg==0 else '> 0 (slack kernel present)' if rho_avg>0 else '< 0 (?!)'}")
    print()
    return rho_avg, Fval

def cyc(n): return n,[(i,(i+1)%n) for i in range(n)]
def blowupC5(t):
    n=5*t; E=[]
    for i in range(5):
        for a in range(t):
            for b in range(t):
                E.append((i*t+a,((i+1)%5)*t+b))
    return n,E
def petersen():
    out=[(i,(i+1)%5) for i in range(5)]; inn=[(5+i,5+((i+2)%5)) for i in range(5)]
    return 10,out+inn+[(i,5+i) for i in range(5)]
def g6dec(s):
    b=[ord(c)-63 for c in s]; n=b[0]; bits=[]
    for x in b[1:]:
        for k in range(5,-1,-1): bits.append((x>>k)&1)
    E=[];idx=0
    for j in range(1,n):
        for i in range(j):
            if idx<len(bits) and bits[idx]: E.append((i,j))
            idx+=1
    return n,E

print("=== EXACT C5 ANCHOR (the extremal; expect rho=0 at alpha*=1/5) ===")
analyze("C5",*cyc(5))
print("=== band/other triangle-free graphs (expect rho_avg>0 => slack kernel) ===")
analyze("C7",*cyc(7))
analyze("Petersen",*petersen())
analyze("band-max-n8",*g6dec("G?`F`w"))
print("NOTE: F=alpha*D+rho_avg is checked as an exact identity; rho_avg=0 iff every edge has P_ij=alpha*")
print("(flat pressure on the support). C5: all edges P=1/5=alpha* => rho=0. A graph with edges at two")
print("pressure levels has alpha*=min level and rho_avg>0 = GPT's nonzero weighted-regular slack kernel.")
