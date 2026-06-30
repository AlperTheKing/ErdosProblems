from fractions import Fraction as F
from collections import deque
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
def bridge_g(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]
nn,E=bridge_g((7,Cn(7)),mycielski(5,Cn(5)),0,0)
adjc,cuts=gmins(nn,E)
for side in cuts:
    st=struct_for_side(nn,adjc,side)
    if st is None: continue
    M,ell,T,mu,cyc=st
    if (0,6) not in M: continue
    f=(0,6); P=cyc[f][0]; L=ell[f]; m=len(M)
    def bbfs(s):
        d=[-1]*nn; d[s]=0; q=deque([s])
        while q:
            u=q.popleft()
            for w in adjc[u]:
                if side[w]!=side[u] and d[w]<0: d[w]=d[u]+1; q.append(w)
        return d
    d0=bbfs(P[0]); dL=bbfs(P[-1])
    print("path P=%s L=%d m=%d  cap=n+n^2/25=%s"%(P,L,m,F(nn)+F(nn*nn,25)))
    Coh=F(0)
    for i,xi in enumerate(P):
        if i==0 or i==len(P)-1:
            dm=sum(1 for w in adjc[xi] if side[w]==side[xi]); g=F(dm); lab="dM=%d"%dm
        else:
            Lam=sum(1 for v in range(nn) if d0[v]==i and dL[v]==L-1-i); g=F(m,Lam); lab="m/|Lam=%d|"%Lam
        Coh+=g; print("  i=%d v=%d gamma=%s (%s) T=%s"%(i,xi,g,lab,T[xi]))
    cap=F(nn)+F(nn*nn,25)
    print("  Coh=%s  Coh+m=%s  cap=%s -> %s (margin %s)"%(Coh,Coh+m,cap,"FAILS" if Coh+m>cap else "ok",cap-(Coh+m)))
    break
