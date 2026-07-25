#!/usr/bin/env python3
"""Independent test of the central claim of the r=4 edge-local certificate:
for lattice 3-polytopes whose facet normals lie in the fixed 15-element r=4
normal set, a_1 is a LINEAR functional of the 99-vector Lambda of edge lattice
lengths indexed by unordered facet-normal pairs.

Test: sample many such polytopes, build M (rows Lambda) and a (their exact
a_1); check rank([M|a]) == rank(M).  A failure would refute the certificate.
Also: solve for the functional on the sampled span and report min/max of a_1.
"""
import random
from fractions import Fraction as F
from math import gcd
from itertools import combinations

NORMALS = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1),
           (1,-1,0),(-1,1,0),(1,0,-1),(-1,0,1),(0,1,-1),(0,-1,1),
           (1,-1,-1),(-1,1,-1),(-1,-1,1)]
PAIRS = [(i,j) for i in range(15) for j in range(i+1,15)]
PIDX = {p:k for k,p in enumerate(PAIRS)}

def det3(u,v,w):
    return (u[0]*(v[1]*w[2]-v[2]*w[1]) - u[1]*(v[0]*w[2]-v[2]*w[0])
            + u[2]*(v[0]*w[1]-v[1]*w[0]))

def solve3(rows,rhs):
    M=[[F(x) for x in r] for r in rows]; b=[F(x) for x in rhs]
    for c in range(3):
        p=None
        for r in range(c,3):
            if M[r][c]!=0: p=r; break
        if p is None: return None
        M[c],M[p]=M[p],M[c]; b[c],b[p]=b[p],b[c]
        pv=M[c][c]; M[c]=[x/pv for x in M[c]]; b[c]=b[c]/pv
        for r in range(3):
            if r!=c and M[r][c]!=0:
                f=M[r][c]; M[r]=[M[r][k]-f*M[c][k] for k in range(3)]; b[r]=b[r]-f*b[c]
    return (b[0],b[1],b[2])

def affrank(pts):
    if len(pts)<2: return 0
    base=pts[0]
    rows=[[x-y for x,y in zip(p,base)] for p in pts[1:]]
    return rowrank(rows)

def rowrank(rows,ncol=3):
    M=[[F(x) for x in r] for r in rows]; rk=0
    for c in range(ncol):
        p=None
        for r in range(rk,len(M)):
            if M[r][c]!=0: p=r; break
        if p is None: continue
        M[rk],M[p]=M[p],M[rk]; pv=M[rk][c]; M[rk]=[x/pv for x in M[rk]]
        for r in range(len(M)):
            if r!=rk and M[r][c]!=0:
                f=M[r][c]; M[r]=[M[r][k]-f*M[rk][k] for k in range(ncol)]
        rk+=1
    return rk

def sample(b):
    verts=set()
    for tri in combinations(range(15),3):
        rows=[NORMALS[i] for i in tri]
        if det3(*rows)==0: continue
        p=solve3(rows,[b[i] for i in tri])
        if p is None: continue
        if all(sum(NORMALS[i][k]*p[k] for k in range(3))<=b[i] for i in range(15)):
            verts.add(p)
    verts=sorted(verts)
    if len(verts)<4 or affrank(verts)!=3: return None
    if not all(x.denominator==1 for v in verts for x in v): return None
    verts=[tuple(int(x) for x in v) for v in verts]
    tightsets=[]
    for i in range(15):
        S=[k for k,v in enumerate(verts) if sum(NORMALS[i][t]*v[t] for t in range(3))==b[i]]
        tightsets.append(S)
    facets=[i for i in range(15) if len(tightsets[i])>=3
            and affrank([verts[k] for k in tightsets[i]])==2]
    Lam=[0]*len(PAIRS)
    for i,j in combinations(facets,2):
        S=sorted(set(tightsets[i]) & set(tightsets[j]))
        if len(S)!=2: continue
        p,q=verts[S[0]],verts[S[1]]
        d=[p[t]-q[t] for t in range(3)]
        g=0
        for x in d: g=gcd(g,abs(x))
        if g==0: continue
        Lam[PIDX[(i,j)]]+=g
    lo=[min(v[k] for v in verts) for k in range(3)]
    hi=[max(v[k] for v in verts) for k in range(3)]
    def count(t):
        c=0
        for x in range(lo[0]*t,hi[0]*t+1):
            for y in range(lo[1]*t,hi[1]*t+1):
                for z in range(lo[2]*t,hi[2]*t+1):
                    if all(n[0]*x+n[1]*y+n[2]*z<=b[i]*t for i,n in enumerate(NORMALS)): c+=1
        return c
    L=[count(t) for t in range(5)]
    if L[0]!=1: return None
    M=[[F(t)**k for k in range(4)]+[F(L[t])] for t in range(4)]
    for c in range(4):
        p=next(r for r in range(c,4) if M[r][c]!=0); M[c],M[p]=M[p],M[c]
        pv=M[c][c]; M[c]=[x/pv for x in M[c]]
        for r in range(4):
            if r!=c and M[r][c]!=0:
                f=M[r][c]; M[r]=[M[r][k]-f*M[c][k] for k in range(5)]
    a=[M[k][4] for k in range(4)]
    if sum(a[k]*F(4)**k for k in range(4))!=L[4]: return None
    return Lam,a[1]

random.seed(4242)
rows=[]; avals=[]
tries=0
while len(rows)<250 and tries<6000:
    tries+=1
    b=[random.randint(0,5) for _ in range(15)]
    r=sample(b)
    if r is None: continue
    rows.append(r[0]); avals.append(r[1])
print("samples:",len(rows))
rk_M   = rowrank(rows, ncol=len(PAIRS))
rk_Ma  = rowrank([rows[k]+[avals[k]] for k in range(len(rows))], ncol=len(PAIRS)+1)
print("rank(M) =",rk_M,"  rank([M|a]) =",rk_Ma,
      "  LINEARITY", "CONSISTENT" if rk_M==rk_Ma else "REFUTED")
print("min a_1 over samples =",min(avals)," (6a_1 =",6*min(avals),")")
print("max a_1 over samples =",max(avals))
print("number of distinct edge-pair types actually used:",
      sum(1 for k in range(len(PAIRS)) if any(r[k] for r in rows)))
