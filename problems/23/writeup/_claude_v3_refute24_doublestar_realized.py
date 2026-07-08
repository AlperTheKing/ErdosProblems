"""V3 refutation attempt: 24-vertex realization of the m=9 double-star Hall violator.
Core: l=0,1,2; r=3,4,5; u=6,w=7,v=8. Cluster K3,3 (l,r) intended bad.
Web: aL=9,10,11; zL=12,13,14; m=15,16,17; zR=18,19,20; aR=21,22,23,
complete 3x3 between consecutive layers l-aL-zL-m-zR-aR-r.
Intended cut: Y = {u,v,aL,m,aR}; every edge blue except the 9 cluster edges.
Check exactly: triangle-free; intended cut value; TRUE max cut (2^23 numpy);
whether intended is a max cut; Gamma-min; atoms/footprint/Hall at intended.
"""
import numpy as np
from collections import deque

def build():
    E=[]
    L=(0,1,2); R=(3,4,5); u,w,v=6,7,8
    aL=(9,10,11); zL=(12,13,14); M=(15,16,17); zR=(18,19,20); aR=(21,22,23)
    for l in L:
        for r in R: E.append((l,r))
    for l in L: E.append((l,u))
    E += [(u,w),(w,v)]
    for r in R: E.append((v,r))
    def K33(A,B):
        for a in A:
            for b in B: E.append((min(a,b),max(a,b)))
    K33(L,aL); K33(aL,zL); K33(zL,M); K33(M,zR); K33(zR,aR); K33(aR,R)
    return 24, E

def tri_free(n,E):
    adj=[set() for _ in range(n)]
    for (i,j) in E: adj[i].add(j); adj[j].add(i)
    return all(not (adj[i]&adj[j]) for (i,j) in E)

def bfs(adjB,n,s):
    d=[-1]*n; d[s]=0; q=deque([s])
    while q:
        x=q.popleft()
        for y in adjB[x]:
            if d[y]<0: d[y]=d[x]+1; q.append(y)
    return d

def analyze(n,E,mask):
    adjB=[[] for _ in range(n)]; bad=[]; blue=[]
    for (i,j) in E:
        if ((mask>>i)^(mask>>j))&1: adjB[i].append(j); adjB[j].append(i); blue.append((i,j))
        else: bad.append((i,j))
    dist=[bfs(adjB,n,s) for s in range(n)]
    gamma=0; inf=False; atoms=[]
    for (uu,vv) in bad:
        d=dist[uu][vv]
        if d<0: inf=True; continue
        gamma+=(d+1)**2
        if d==4: atoms.append((uu,vv))
    sups=[]
    for (uu,vv) in atoms:
        S=set()
        for (a,b) in blue:
            for (x,y) in ((a,b),(b,a)):
                if dist[uu][x]>=0 and dist[y][vv]>=0 and dist[uu][x]+1+dist[y][vv]==4:
                    S.add((a,b)); break
        sups.append(frozenset(S))
    return gamma,inf,bad,atoms,sups

n,E = build()
print("n =",n,"|E| =",len(E),"triangle-free:",tri_free(n,E))
Y = [6,8,9,10,11,15,16,17,21,22,23]
intended = 0
for x in Y: intended |= 1<<x
ic = sum(((intended>>i)^(intended>>j))&1 for (i,j) in E)
print("intended cut value =", ic, "(expect |E|-9 =", len(E)-9, ")")
g,inf,bad,atoms,sups = analyze(n,E,intended)
print("intended: bad =",sorted(bad)," Gamma =",g," ell5 atoms =",len(atoms))
foot=set().union(*sups) if sups else set()
print("footprint size =",len(foot),"footprint =",sorted(foot))
print("HALL at intended: |S| =",len(atoms)," |E_short(S)| =",len(foot),
      " VIOLATION" if len(atoms)>len(foot) else " ok")
sup_sizes=[len(s) for s in sups]
print("support sizes:",sup_sizes)

# exact max cut, vertex 23 fixed side 0, chunked numpy
best=-1; bestmasks=[]
CH=1<<20
for base in range(0, 1<<23, CH):
    masks=np.arange(base, base+CH, dtype=np.uint32)
    cut=np.zeros(CH, dtype=np.int8)
    for (i,j) in E:
        cut += ((masks>>np.uint32(i))^(masks>>np.uint32(j))).astype(np.int8)&1
    mx=int(cut.max())
    if mx>best:
        best=mx; bestmasks=[int(x) for x in masks[cut==mx]]
    elif mx==best:
        bestmasks += [int(x) for x in masks[cut==mx]]
print("TRUE MAX CUT =",best," #max-cut masks (v23 side 0) =",len(bestmasks))
norm_int = intended if not (intended>>23)&1 else intended ^ ((1<<24)-1)
print("intended is a max cut:", norm_int in bestmasks)
gmin=None; details=[]
for mask in bestmasks:
    g2,inf2,bad2,at2,su2 = analyze(n,E,mask)
    details.append((mask,g2,inf2,bad2,at2,su2))
    if not inf2 and (gmin is None or g2<gmin): gmin=g2
print("Gamma-min over max cuts =",gmin)
for (mask,g2,inf2,bad2,at2,su2) in details:
    if g2==gmin and not inf2:
        foot2=set().union(*su2) if su2 else set()
        print("gmin max cut:",mask,"bad:",sorted(bad2),"atoms:",len(at2),
              "|E_short(all)|:",len(foot2),
              "HALL VIOLATION" if len(at2)>len(foot2) else "hall ok")
