import sys
from beta import *

def neighbors(adj,n,v):
    return [u for u in range(n) if (adj[v]>>u)&1]

def e_between(adj, S, T):
    # count edges with one endpoint in S, other in T (S,T disjoint)
    Sset=set(S); c=0
    for s in S:
        for t in T:
            if (adj[s]>>t)&1: c+=1
    return c

def e_within(adj,S):
    c=0
    Sl=list(S)
    for i in range(len(Sl)):
        for j in range(i+1,len(Sl)):
            if (adj[Sl[i]]>>Sl[j])&1: c+=1
    return c

def cut3(adj,n,u,v):
    assert not (adj[u]>>v)&1, "uv must be nonedge"
    Nu=set(neighbors(adj,n,u)); Nv=set(neighbors(adj,n,v))
    C=Nu&Nv
    A=Nu-C
    B=Nv-C
    R=set(range(n))-{u,v}-Nu-Nv
    t=len(C)
    p=e_between(adj,A,B)
    q=e_within(adj,R)
    x=e_between(adj,A,R)
    y=e_between(adj,B,R)
    return dict(t=t,p=p,q=q,x=x,y=y,
                bound=min(p+q, t+q+x, t+q+y),
                A=len(A),B=len(B),C=t,R=len(R))

if __name__=="__main__":
    for m in [2,3,4]:
        adj,n=c5_blowup([m]*5)
        b=beta(adj,n)
        # natural nonedge: u in block0, v in block2 (distance 2)
        # blocks: 0:[0..m-1],1:[m..2m-1],2:[2m..3m-1]...
        u=0; v=2*m
        info=cut3(adj,n,u,v)
        # also nonedge within same block (block0): u=0, v=1
        info2=cut3(adj,n,0,1)
        print(f"C5[{m}] N={n} beta={b} n^2={m*m}")
        print(f"  nonedge across (blk0,blk2): {info}")
        print(f"  nonedge within blk0      : {info2}")
