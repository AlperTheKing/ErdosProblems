"""DECISIVE gate of Codex's traffic-mass E-atom candidate (could PROVE PATH-GAMMA for ell=5 in one inequality).
For each gamma-min connected-B max cut, bad edge f with ell=5, shortest blue geodesic P=(x0..x4):
  h_i = T[x_i]/n ; S = sum h_i.
  C_inc = S^2 - 25*min_{i mod 5}(h_i h_{i+1})   (>=0 by AM-GM/cyclic-min-product on h).
  C_exc = S^2 - 25*min_{i=0,1,2,3}(h_i h_{i+1}) (excludes bad gap (x4,x0)).
  F(P) = (5/25)(n^2 - Gamma) - sum_i (T[x_i]-n).
  (A) F(P) - C_inc/25 >= 0   (B) F(P) - C_exc/25 >= 0.   Either => PATH-GAMMA (ell=5).
CRITICAL: include the CORRIDOR/GLUED cases that broke the Farkas core cone (glued C5|C7 N=12 f=(0,4)) + Mycielskians N=23.
EXACT Fraction. Report A-viol, B-viol, worst margins, first failures, tight cases."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
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
    Gamma=sum(T)
    for f in M:
        if ell[f]!=5: continue
        for P in cyc[f]:
            if len(P)!=5: continue
            h=[F(T[P[i]],n) for i in range(5)]
            S=sum(h)
            prods=[h[i]*h[(i+1)%5] for i in range(5)]
            C_inc=S*S-25*min(prods)
            C_exc=S*S-25*min(prods[0],prods[1],prods[2],prods[3])  # exclude gap index 4 = (x4,x0)
            FP=F(5,25)*(F(n*n)-Gamma)-sum(T[P[i]]-F(n) for i in range(5))
            mA=FP-C_inc/25
            mB=FP-C_exc/25
            acc['rows']+=1
            if mA<0:
                acc['vA']+=1
                if acc['fA'] is None: acc['fA']=(name,n,str(f),str(P),str(FP),str(C_inc/25),str(mA))
            if mB<0:
                acc['vB']+=1
                if acc['fB'] is None: acc['fB']=(name,n,str(f),str(P),str(FP),str(C_exc/25),str(mB))
            if mA<acc['minA'][0]: acc['minA']=(mA,name,n)
            if mB<acc['minB'][0]: acc['minB']=(mB,name,n)

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
    acc=dict(rows=0,vA=0,vB=0,fA=None,fB=None,minA=(F(10**9),'',0),minB=(F(10**9),'',0))
    # CORRIDOR/GLUED witnesses first (the Farkas-core killers)
    for nm,(nn,E) in [("C5|C7",bridge_g((5,Cn(5)),(7,Cn(7)),0,0)),("C7|Grotzsch",bridge_g((7,Cn(7)),mycielski(5,Cn(5)),0,0)),
                      ("C5|C5",bridge_g((5,Cn(5)),(5,Cn(5)),0,0)),("C9|C9",bridge_g((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("Grotzsch",mycielski(5,Cn(5))),("Myc(Grotzsch)",mycielski(mycielski(5,Cn(5))[0],mycielski(5,Cn(5))[1])),
                      ("M(C7)",mycielski(7,Cn(7)))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:4]: chk(nm,nn,adj,s,acc)
    print("  after corridor/glued+Myc: rows=%d vA=%d vB=%d"%(acc['rows'],acc['vA'],acc['vB']),flush=True)
    for L in (8,12,16,20):
        n,E,side,bad=build_two_lane(L); chk("twolane%d"%L,n,adj_of(n,E),side,acc)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>28: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    for parts in ([2,1,2,1,2],[3,2,3,2,3],[3,1,3,1,3],[4,3,4,3,4],[3,9,1,9,3],[9,1,9,1,9]):
        n,E=blowup(parts)
        if n>28: continue
        adj,cuts=gmins(n,E)
        for s in cuts[:2]: chk("fan%s"%parts,n,adj,s,acc)
    for nn in range(5,12):
        outg=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (rows=%d vA=%d vB=%d)"%(nn,acc['rows'],acc['vA'],acc['vB']),flush=True)
    print("\n  E-MASS candidate (ell=5): rows=%d"%acc['rows'])
    print("  (A) F >= C_inc/25 : violations=%d  min margin=%s @ %s  %s"%(acc['vA'],str(acc['minA'][0]),acc['minA'][1:],acc['fA'] or ''))
    print("  (B) F >= C_exc/25 : violations=%d  min margin=%s @ %s  %s"%(acc['vB'],str(acc['minB'][0]),acc['minB'][1:],acc['fB'] or ''))
    if acc['vA']==0:
        print("  === (A) HOLDS => PATH-GAMMA PROVEN for ell=5 via single inequality F >= C_inc/25 (C_inc>=0 by AM-GM) ===")
    elif acc['vB']==0:
        print("  === (B) HOLDS => PATH-GAMMA PROVEN for ell=5 via F >= C_exc/25 ===")
    else:
        print("  === E-MASS candidate FAILS (both A,B have violations) -- still a sub-atom needing contamination generators ===")
