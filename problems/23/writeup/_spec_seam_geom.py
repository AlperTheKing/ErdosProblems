"""Understand the geometry of the descending switch W={0,6} on the H?AFBo] N=9 cut.
Print, before and after the flip: side, which edges are B vs M, ell of each bad edge, T, Gamma.
Goal: identify the DETERMINISTIC rule producing W from (cut, violating vertex)."""
from fractions import Fraction as F
from _h import Bconn, bdist_restr, geos
from _satzmu_conn import struct_for_side
from _csmspec import build_K2

E=[(0,5),(0,6),(1,6),(2,6),(1,7),(2,7),(3,7),(4,7),(3,8),(4,8),(5,8),(6,8)]
n=9; adj=[set() for _ in range(n)]
for a,b in E: adj[a].add(b); adj[b].add(a)

def describe(side,tag):
    print("==== %s side=%s ===="%(tag,''.join(map(str,side))))
    Bset=[(u,v) for u,v in E if side[u]!=side[v]]
    Mset=[(u,v) for u,v in E if side[u]==side[v]]
    print(" B edges:",Bset)
    print(" M edges:",Mset)
    G=0
    for (u,v) in Mset:
        d=bdist_restr(adj,side,u,v)
        print("   bad",(u,v),"ell=",d+1 if d>=0 else "INF")
        if d>=0: G+=(d+1)**2
    print(" Gamma=",G," Bconn=",Bconn(n,adj,side))
    st=struct_for_side(n,adj,side)
    if st:
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        print(" T=",[str(T[v]) for v in range(n)])
    print()

side=[1,1,1,1,1,1,0,0,0]
describe(side,"BEFORE")
for W in [{0,6},{5,8}]:
    s2=side[:]
    for v in W: s2[v]^=1
    describe(s2,"AFTER flip W=%s"%sorted(W))
