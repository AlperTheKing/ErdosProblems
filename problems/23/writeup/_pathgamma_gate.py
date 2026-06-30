"""Gate Codex PATH-GAMMA (deficit/coarea form, stronger than PATH-LRS, NOT a static |M|-credit):
  for every bad edge f and shortest B-geodesic P, L=ell[f], Gamma=sum_g ell[g]^2 = sum_v T[v]:
     Ex(P) := sum_{v in P}(T[v] - n)  <=  L*(n^2 - Gamma)/25.
  Equivalently sum_{v in P} T[v] <= L*n + L*(n^2-Gamma)/25.  (=> PATH-LRS(c1) since Gamma>=25m.)
Deficit reading: sum_{v in P}(T[v]-n) <= (L/25) sum_u (n - T[u]).
EXACT Fraction. Full battery incl Mycielskians + glued islands (where credit certs died) + two-lane.
Also test at ALL max cuts on a small range (maxcut_all)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    Gamma=sum(T)  # = sum_g ell^2
    slack_glob=F(n*n)-Gamma   # n^2 - Gamma
    for f in M:
        L=ell[f]
        rhs_extra=F(L)*slack_glob/25
        for P in cyc[f]:
            Ex=sum(T[v]-F(n) for v in P)
            margin=rhs_extra-Ex
            acc['paths']+=1
            if margin<0:
                acc['viol']+=1
                if acc['fviol'] is None: acc['fviol']=(name,n,str(f),str(Ex),str(rhs_extra),str(Gamma))
            if margin<acc['minm'][0]:
                acc['minm']=(margin,name,n,len(M),L,str(Ex),str(Gamma),str(rhs_extra))

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
    acc=dict(paths=0,viol=0,fviol=None,minm=(F(10**9),'',0,0,0,'','',''))
    # ALL max cuts on H?AFBo] + small census (Gamma-min not assumed)
    accall=dict(paths=0,viol=0,fviol=None,minm=(F(10**9),'',0,0,0,'','',''))
    n,E=dec('H?AFBo]'); adjh=adj_of(n,E)
    for side in maxcut_all(n,adjh): chk('H?AFBo]-allcut',n,adjh,side,accall)
    # battery (gamma-min cuts)
    for L in (8,12,16,20,24):
        n,E,side,bad=build_two_lane(L); chk("twolane%d"%L,n,adj_of(n,E),side,acc)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    for parts in ([2,1,2,1,2],[3,2,3,2,3],[3,1,3,1,3],[4,3,4,3,4],[3,9,1,9,3]):
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in cuts[:2]: chk("C5%s"%parts,n,adj,s,acc)
    for nm,(nn,E) in [("Grotzsch",mycielski(5,Cn(5))),("Myc(Grotzsch)",mycielski(mycielski(5,Cn(5))[0],mycielski(5,Cn(5))[1])),
                      ("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge_g((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C5|C7",bridge_g((5,Cn(5)),(7,Cn(7)),0,0)),
                      ("C9|C9",bridge_g((9,Cn(9)),(9,Cn(9)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: chk(nm,nn,adj,s,acc)
    # all max cuts census N<=9
    for nn in range(5,10):
        outg=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adjg=adj_of(n,E)
            for s in maxcut_all(n,adjg): chk('cen%s-all'%g6,n,adjg,s,accall)
        print("  ALLCUT census N=%d done (paths=%d viol=%d)"%(nn,accall['paths'],accall['viol']),flush=True)
    # gamma-min census N<=11
    for nn in range(5,12):
        outg=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  GMIN census N=%d done (paths=%d viol=%d)"%(nn,acc['paths'],acc['viol']),flush=True)
    print("\n  PATH-GAMMA (gamma-min battery): paths=%d violations=%d %s"%(acc['paths'],acc['viol'],acc['fviol'] or ''),flush=True)
    mm=acc['minm']; print("  min margin=%s @ %s N=%d m=%d L=%d Ex=%s Gamma=%s rhs_extra=%s"%(str(mm[0]),mm[1],mm[2],mm[3],mm[4],mm[5],mm[6],mm[7]),flush=True)
    print("  PATH-GAMMA (ALL max cuts, census N<=9 + H?AFBo]): paths=%d violations=%d %s"%(accall['paths'],accall['viol'],accall['fviol'] or ''),flush=True)
    ok = acc['viol']==0 and accall['viol']==0
    print("  === PATH-GAMMA %s ==="%("HOLDS on full battery AND all max cuts" if ok else "*** FAILS ***"),flush=True)
