from fractions import Fraction as F
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn

n=5; E=Cn(5)
adj,cuts=gmins(n,E)
print("C5: n=%d  #gamma-min cuts=%d"%(n,len(cuts)))
for side in cuts[:1]:
    st=struct_for_side(n,adj,side)
    M,ell,T,mu,cyc=st
    print(" side=",side," bad edges M=",list(M))
    P={}
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        P[f]={v:F(c,nf) for v,c in cnt.items()}
        print("  f=%s |geos|=%d ell=%s geos=%s"%(f,nf,ell[f],Ps))
    s=[F(0)]*n
    for f in M:
        for v,pv in P[f].items(): s[v]+=pv
    print("  s(v)=",[str(x) for x in s])
    print("  T(v)=",[str(x) for x in T])
    for f in M:
        rs=sum(pv*s[v] for v,pv in P[f].items())
        print("  rowsum_O(%s)=%s  (N=%d)"%(f,rs,n))
