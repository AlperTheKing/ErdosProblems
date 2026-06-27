#!/usr/bin/env python3
"""Bridge probe: does the band d_mono-MAXIMIZER (n=8, g6=G?`F`w) realize Step-2's
'non-parallel shortest-odd-cycle OVERLAP => Gamma-deficit' picture? Count distinct shortest
odd cycles (bad edge + shortest B-geodesic) and their pairwise vertex overlaps, alongside the
master slack N^2-Gamma. If the band maximizer has overlapping (non-parallel) shortest cycles
and slack>0, that is the finite witness shared by both delta=0 routes."""
import sys
from collections import deque
sys.path.insert(0, "E:/Projects/ErdosProblems/problems/23/writeup")
try:
    from r2_check_ref import master_check
    HAVE_REF = True
except Exception as e:
    HAVE_REF = False; print("(r2_check_ref unavailable:", e, ")")

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

def maxcut_all(n,edges):
    best=-1; cuts=[]
    for mask in range(1<<(n-1)):
        side=[(mask>>u)&1 for u in range(n)]
        c=sum(1 for (u,v) in edges if side[u]!=side[v])
        if c>best: best=c; cuts=[side[:]]
        elif c==best: cuts.append(side[:])
    return best,cuts

def Bconn(n,adj,side):
    seen={0}; q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in seen: seen.add(v); q.append(v)
    return len(seen)==n

def bdist(n,adj,side,s,t):
    d={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in d: d[v]=d[u]+1; q.append(v)
    return d.get(t,-1)

def shortest_geos(n,adj,side,s,t):
    dist={s:0}; pred={s:[]}; layer=[s]
    while layer:
        nxt=[]
        for u in layer:
            for v in adj[u]:
                if side[u]!=side[v]:
                    if v not in dist: dist[v]=dist[u]+1; pred[v]=[u]; nxt.append(v)
                    elif dist[v]==dist[u]+1: pred[v].append(u)
        layer=nxt
    if t not in dist: return []
    paths=[]
    def rec(v,acc):
        if v==s: paths.append(tuple([s]+acc[::-1])); return
        for p in pred[v]: rec(p,acc+[v])
    rec(t,[]); return paths

def gamma_min_cut(n,adj,cuts):
    best=None
    for side in cuts:
        if not Bconn(n,adj,side): continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        G=0; ok=True
        for (u,v) in M:
            d=bdist(n,adj,side,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok and (best is None or G<best[1]): best=(side,G,M)
    return best

g6="G?`F`w"
n,edges=decode_g6(g6)
adj=[set() for _ in range(n)]
for a,b in edges: adj[a].add(b); adj[b].add(a)
print(f"graph {g6}: n={n}, e={len(edges)}, edges={edges}")
mc,cuts=maxcut_all(n,edges)
side,G,M=gamma_min_cut(n,adj,cuts)
print(f"maxcut={mc}, beta={len(edges)-mc}, Gamma={G}, N^2={n*n}, master/Gamma slack N^2-Gamma={n*n-G}")
print(f"chosen cut side={side}; bad edges M={M}")
# shortest odd cycles per bad edge
cycles=[]
for (u,v) in M:
    geos=shortest_geos(n,adj,side,u,v)
    for path in geos:
        cyc=frozenset(path)  # vertex set of the odd cycle (bad edge u-v closes the B-path)
        cycles.append((u,v,len(path)+0, cyc, path))
print(f"\n#shortest-odd-cycle instances (bad edge x shortest geodesic) = {len(cycles)}")
distinct=set(c[3] for c in cycles)
print(f"#distinct cycle vertex-sets = {len(distinct)}")
for (u,v,L,cyc,path) in cycles:
    print(f"  bad edge ({u},{v}) ell={L} cycle verts={sorted(cyc)} path={path}")
# pairwise overlaps (shared vertices >=2) among distinct cycles
dl=sorted(distinct,key=lambda s:sorted(s))
print("\npairwise vertex-overlaps among distinct shortest odd cycles:")
maxov=0
for i in range(len(dl)):
    for j in range(i+1,len(dl)):
        ov=len(dl[i]&dl[j]); maxov=max(maxov,ov)
        print(f"  {sorted(dl[i])} & {sorted(dl[j])} -> shared {ov} vertices{'  <== NON-PARALLEL OVERLAP (>=2)' if ov>=2 else ''}")
print(f"\nmax pairwise overlap = {maxov}")
if HAVE_REF:
    res=master_check(n,edges)
    print("\nr2_check_ref.master_check:", res)
print("\nREAD: band MAXIMIZER has slack N^2-Gamma =", n*n-G,
      "; Step-2's 'overlap=>deficit' predicts non-parallel overlap (>=2 shared) present iff slack>0.")
