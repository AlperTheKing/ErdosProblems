from fractions import Fraction as F
from _h import Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _verify_two_lane import build_two_lane
def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    G=sum(T)
    for f in M:
        if ell[f]!=5: continue
        for P in cyc[f]:
            if len(P)!=5: continue
            h=[F(T[P[i]],n) for i in range(5)]; S=sum(h)
            pr=[h[i]*h[(i+1)%5] for i in range(5)]
            Cinc=S*S-25*min(pr); Cexc=S*S-25*min(pr[0],pr[1],pr[2],pr[3])
            FP=F(5,25)*(F(n*n)-G)-sum(T[P[i]]-F(n) for i in range(5))
            acc[0]+=1
            if FP-Cinc/25<0: acc[1]+=1
            if FP-Cexc/25<0: acc[2]+=1
def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a
def blowup(parts):
    off=[0]
    for s in parts: off.append(off[-1]+s)
    nn=off[-1]; EE=[]; L=len(parts)
    for i in range(L):
        j=(i+1)%L
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
acc=[0,0,0]
for Ltl in (8,12,16,20,24):
    n,E,side,bad=build_two_lane(Ltl); chk("tl",n,adj_of(n,E),side,acc)
for parts in ([2,1,2,1,2],[3,2,3,2,3],[3,1,3,1,3],[4,3,4,3,4],[3,9,1,9,3],[9,1,9,1,9],[2,10,1,10,2],[5,1,5,1,5]):
    n,E=blowup(parts)
    if n>30: continue
    adj,cuts=gmins(n,E)
    for s in cuts[:2]: chk("fan",n,adj,s,acc)
for cyc in (5,7,9):
    for t in range(1,7):
        n,E=blowup([t]*cyc)
        if n>30: continue
        adj,cuts=gmins(n,E)
        for s in cuts[:2]: chk("uni",n,adj,s,acc)
print("two-lane+fans+uniform blowups: rows=%d  (A)F>=Cinc/25 viol=%d  (B)F>=Cexc/25 viol=%d"%(acc[0],acc[1],acc[2]))
