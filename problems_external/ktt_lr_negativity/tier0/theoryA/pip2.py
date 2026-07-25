# Search rational TRIANGLES with Ehrhart PERIOD 1 for h*_2 > h*_1.
# Exact: vertices are Fractions; counting by exact rational containment.
from fractions import Fraction as F
import itertools, random, math

def count(verts, n):
    # count lattice points in n*conv(verts), exact
    xs=[v[0]*n for v in verts]; ys=[v[1]*n for v in verts]
    x0=math.floor(min(xs)); x1=math.ceil(max(xs))
    y0=math.floor(min(ys)); y1=math.ceil(max(ys))
    # half-plane form for triangle
    A=[]
    for i in range(3):
        (ax,ay)=(verts[i][0]*n,verts[i][1]*n); (bx,by)=(verts[(i+1)%3][0]*n,verts[(i+1)%3][1]*n)
        (cx,cy)=(verts[(i+2)%3][0]*n,verts[(i+2)%3][1]*n)
        nx=by-ay; ny=-(bx-ax)
        s=nx*(cx-ax)+ny*(cy-ay)
        if s<0: nx,ny=-nx,-ny
        A.append((nx,ny,nx*ax+ny*ay))
    c=0
    for X in range(x0,x1+1):
        for Y in range(y0,y1+1):
            if all(nx*X+ny*Y>=d for nx,ny,d in A): c+=1
    return c

def hstar_from(P,d):
    from math import comb
    return [sum((-1)**i*comb(d+1,i)*P[j-i] for i in range(j+1)) for j in range(d+1)]

def poly2(P):  # fit degree 2 through n=0,1,2
    a0=P[0]; a2=F(P[2]-2*P[1]+P[0],2); a1=P[1]-P[0]-a2
    return lambda n: a0+a1*n+a2*n*n

rng=random.Random(5)
found=[]; tested=0
for trial in range(200000):
    q=rng.choice([2,2,3,3,4,5])
    V=[]
    for _ in range(3):
        V.append((F(rng.randint(-3*q,3*q),q), F(rng.randint(-3*q,3*q),q)))
    # nondegenerate
    ar=(V[1][0]-V[0][0])*(V[2][1]-V[0][1])-(V[2][0]-V[0][0])*(V[1][1]-V[0][1])
    if ar==0: continue
    tested+=1
    P=[count(V,n) for n in range(0,9)]
    if P[0]!=1: continue
    f=poly2(P)
    if any(f(n)!=P[n] for n in range(3,9)): continue   # period 1 (checked to n=8)
    hs=hstar_from(P,2)
    if hs[2]>hs[1]:
        found.append((V,P,hs))
        if len(found)<=6: print("HIT", V, P, hs)
    if len(found)>=6: break
print("tested",tested,"period-1 hits with h*_2>h*_1:",len(found))
