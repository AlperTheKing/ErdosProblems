#!/usr/bin/env python3
"""Independent probe of the band d_mono-maximizer + its cut-pressure flatness (#23 delta=0).

Tests the conclusion of the High-F no-slack lemma at the ACTUAL band maximizer:
  over all triangle-free graphs with d_edge in [0.2486, 0.3197], find the one(s)
  maximizing d_mono = 2*beta/N^2 (beta = e - MaxCut), then compute the cut-pressure
  kernel P (over ALL maximum cuts) and ask: is P constant on the edge support?
  is the maximizer a weighted-C5-blowup structure? (Cross-checks both delta=0 routes:
  my 'F>=2/25 => weighted-C5' graphon rigidity and Step-2's 'tight => C5[q]'.)
geng (-t = triangle-free) enumerates; we re-verify triangle-freeness in Python.
"""
import subprocess, numpy as np
from fractions import Fraction as F

GENG = "E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"
BAND_LO, BAND_HI = F(2486,10000), F(3197,10000)

def decode_g6(s):
    b=[ord(c)-63 for c in s]; n=b[0]; bits=[]
    for x in b[1:]:
        for k in range(5,-1,-1): bits.append((x>>k)&1)
    edges=[]; idx=0
    for j in range(1,n):
        for i in range(j):
            if idx<len(bits) and bits[idx]: edges.append((i,j))
            idx+=1
    return n,edges

def has_tri(n,edges):
    adj=[set() for _ in range(n)]
    for a,b in edges: adj[a].add(b); adj[b].add(a)
    return any(adj[a]&adj[b] for a,b in edges)

def maxcut(n,edges):
    masks=np.arange(1<<(n-1),dtype=np.int64)   # fix vertex 0 side 0
    cut=np.zeros(len(masks),dtype=np.int64)
    for (u,v) in edges:
        bu=(masks>>u)&1; bv=(masks>>v)&1
        cut+=(bu^bv)
    return int(cut.max())

def opt_cuts(n,edges):
    masks=np.arange(1<<n,dtype=np.int64)
    cut=np.zeros(len(masks),dtype=np.int64)
    for (u,v) in edges:
        cut+=(((masks>>u)&1)^((masks>>v)&1))
    mx=int(cut.max()); opt=masks[cut==mx]
    return mx,opt

def band_e(n):
    lo=int(np.ceil(float(BAND_LO)*n*n/2)); hi=int(np.floor(float(BAND_HI)*n*n/2))
    return lo,hi

best=(F(0),None,None)   # (d_mono, n, g6)
per_n={}
for n in range(5,12):
    lo,hi=band_e(n)
    if lo>hi: continue
    out=subprocess.run([GENG,"-t",str(n),f"{lo}:{hi}"],capture_output=True,text=True).stdout.split()
    bn=(F(0),None)
    for g6 in out:
        nn,edges=decode_g6(g6)
        if has_tri(nn,edges): continue   # safety (geng -t should already exclude)
        e=len(edges); de=F(2*e,n*n)
        if not (BAND_LO<=de<=BAND_HI): continue
        mc=maxcut(n,edges); beta=e-mc; dm=F(2*beta,n*n)
        if dm>bn[0]: bn=(dm,g6,e,beta,mc,de)
        if dm>best[0]: best=(dm,n,g6,e,beta,mc,de)
    if bn[1] is not None:
        per_n[n]=bn
        print(f"n={n:2d}  in-band graphs scanned={len(out):7d}  max d_mono={float(bn[0]):.5f} "
              f"(={bn[0]})  e={bn[2]} beta={bn[3]} maxcut={bn[4]} d_edge={float(bn[5]):.4f}  g6={bn[1]}")

print("\n=== GLOBAL band maximizer ===")
dm,n,g6,e,beta,mc,de=best
print(f"n={n} g6={g6}  d_mono={float(dm):.5f} (={dm})  d_edge={float(de):.4f}  e={e} beta={beta} maxcut={mc}")
print(f"  2/25 = {float(F(2,25)):.5f}; band slack = {float(F(2,25)-dm):.5f}")

# --- pressure flatness on the maximizer ---
nn,edges=decode_g6(g6)
mx,opt=opt_cuts(nn,edges)
K=len(opt)
adj=[set() for _ in range(nn)]
for a,b in edges: adj[a].add(b); adj[b].add(a)
def P(i,j):
    same=int(np.sum(((opt>>i)&1)==((opt>>j)&1))); return F(same,K)
def C(i,j): return F(len(adj[i]&adj[j]),nn)   # common-neighbour kernel (graphon norm /N)
print(f"\n#maximum cuts = {K}")
edgeP=sorted({P(i,j) for (i,j) in edges})
print("distinct cut-pressure P on EDGE support:", [str(x) for x in edgeP])
print("  P flat on edges (no-slack conclusion)?", len(edgeP)==1)
# C_W values on edges (should be 0 for triangle-free) and overall structure
edgeC=sorted({C(i,j) for (i,j) in edges})
print("distinct C_W on edges (tri-free => {0}):", [str(x) for x in edgeC])
# P = 1/5 + 2 C_W check across ALL pairs (the C5-rigidity signature)
dev=[]
for i in range(nn):
    for j in range(i+1,nn):
        dev.append(P(i,j)-(F(1,5)+2*C(i,j)))
maxdev=max(abs(x) for x in dev)
print(f"max |P - (1/5 + 2 C_W)| over all pairs = {float(maxdev):.4f} (=0 iff exact C5-type)")
# degree sequence + is it a weighted-C5 blow-up (5 classes, complete bipartite consecutive)?
deg=sorted(len(adj[v]) for v in range(nn))
print("degree sequence:", deg)
