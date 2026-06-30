"""Gate Codex UNIF-c (first-moment target): max_v T(v) <= N + c*(N^2 - Gamma), candidate c=1/7. Gamma=sum(T)=sum ell^2.
Implication (any c>0): if Gamma>N^2 then avg=Gamma/N>N but UNIF-c gives maxT <= N+c(N^2-Gamma)<N, contra => Gamma<=N^2.
Report worst R=(maxT-N)/(N^2-Gamma) over D>0 cases + tight cases. Full battery incl Mycielskians+glued+nonuniform fans.
EXACT Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane

def chk(name,n,adj,side,acc,c=F(1,7)):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    Gamma=sum(T); D=F(n*n)-Gamma; maxT=max(T)
    acc['cuts']+=1
    # UNIF-c: maxT <= n + c*D
    if maxT> F(n)+c*D:
        acc['viol']+=1
        if acc['fviol'] is None: acc['fviol']=(name,n,str(maxT),str(D),str((maxT-n)/D) if D!=0 else 'D=0')
    if D>0 and maxT>F(n):
        R=(maxT-F(n))/D
        if R>acc['maxR'][0]: acc['maxR']=(R,name,n,str(maxT),str(Gamma),str(D))
    if maxT>F(n): acc['overload']+=1

def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a
def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def bridge_g(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

if __name__=="__main__":
    acc=dict(cuts=0,viol=0,fviol=None,overload=0,maxR=(F(-1),'',0,'','',''))
    for L in (8,12,16,20,24):
        n,E,side,bad=build_two_lane(L); chk("twolane%d"%L,n,adj_of(n,E),side,acc)
    for cyc in (5,7,9,11):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>30: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    for parts in ([2,1,2,1,2],[3,2,3,2,3],[3,1,3,1,3],[4,3,4,3,4],[3,9,1,9,3],[9,1,9,1,9],[2,10,1,10,2]):
        n,E=blowup(parts)
        if n>30: continue
        adj,cuts=gmins(n,E)
        for s in cuts[:2]: chk("fan%s"%parts,n,adj,s,acc)
    for nm,(nn,E) in [("Grotzsch",mycielski(5,Cn(5))),("Myc(Grotzsch)",mycielski(mycielski(5,Cn(5))[0],mycielski(5,Cn(5))[1])),
                      ("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge_g((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C5|C7",bridge_g((5,Cn(5)),(7,Cn(7)),0,0)),
                      ("C9|C9",bridge_g((9,Cn(9)),(9,Cn(9)),0,0)),("C5|C5",bridge_g((5,Cn(5)),(5,Cn(5)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: chk(nm,nn,adj,s,acc)
    for nn in range(5,12):
        outg=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (cuts=%d viol=%d maxR=%s)"%(nn,acc['cuts'],acc['viol'],str(acc['maxR'][0])),flush=True)
    print("\n  UNIF-1/7 (maxT <= N + (N^2-Gamma)/7): cuts=%d overload-cuts=%d violations=%d %s"%(
        acc['cuts'],acc['overload'],acc['viol'],acc['fviol'] or ''),flush=True)
    mR=acc['maxR']
    print("  worst R=(maxT-N)/(N^2-Gamma) = %s = %s  @ %s N=%d maxT=%s Gamma=%s D=%s"%(
        str(mR[0]),str(float(mR[0]))[:8],mR[1],mR[2],mR[3],mR[4],mR[5]),flush=True)
    print("  === UNIF-1/7 %s (c=1/7 %s) ==="%("HOLDS" if acc['viol']==0 else "FAILS",
        "is the sharp constant" if acc['viol']==0 and abs(float(mR[0])-1/7)<1e-9 else "needs adjustment"),flush=True)
