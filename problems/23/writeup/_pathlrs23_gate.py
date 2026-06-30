"""INDEPENDENT exact gate of Codex PATH-LRS-2/3 (theorem-sufficient per the D>=0/D<0 implication):
  for every bad edge f and every shortest B-geodesic P in cyc[f]:
     (1/ell_f) * sum_{v in P} T[v]  <=  N + (2/3)*D,   D = N^2/25 - |M|.
Decisive test: survive the TWO-LANE family (killed raw rho(O)<=N). Full battery + two-lane + blowups +
Mycielskians + glued islands. EXACT Fraction. Report total paths, violations, min margin, equality cases."""
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
    m=len(M); D=F(n*n,25)-m; bound=F(n)+F(2,3)*D
    for f in M:
        Lf=ell[f]
        for P in cyc[f]:
            avg=sum(T[v] for v in P)/Lf
            acc['paths']+=1
            margin=bound-avg
            if margin<acc['minm'][0]:
                acc['minm']=(margin,name,n,m,str(f),str(D),[str(T[v]) for v in P],str(avg))
            if avg>bound:
                acc['viol']+=1
                if acc['fviol'] is None: acc['fviol']=(name,n,m,str(f),str(avg),str(bound))

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
    acc=dict(paths=0,viol=0,fviol=None,minm=(F(10**9),'',0,0,'','',[],''))
    # TWO-LANE (decisive)
    for L in (8,12,16,20,24):
        n,E,side,bad=build_two_lane(L); chk("twolane%d"%L,n,adj_of(n,E),side,acc)
    # blow-ups (overloaded, near-extremal)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    # nonuniform fans (the net_H killer family)
    for sizes in [[3,9,1,9,3],[9,1,9,1,9],[2,10,1,10,2],[4,4,1,4,4,4,4]]:
        n,E=blowup(sizes)
        if n<=26:
            adj,cuts=gmins(n,E)
            for s in cuts[:2]: chk("fan%s"%sizes,n,adj,s,acc)
    # Mycielskians + glued islands
    for nm,(nn,E) in [("Grotzsch",mycielski(5,Cn(5))),("Myc(Grotzsch)",mycielski(mycielski(5,Cn(5))[0],mycielski(5,Cn(5))[1])),
                      ("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge_g((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C5|C7",bridge_g((5,Cn(5)),(7,Cn(7)),0,0)),
                      ("C9|C9",bridge_g((9,Cn(9)),(9,Cn(9)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: chk(nm,nn,adj,s,acc)
    # census N<=11 all gamma-min cuts
    for nn in range(5,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (paths=%d viol=%d)"%(nn,acc['paths'],acc['viol']),flush=True)
    mm=acc['minm']
    print("\n  PATH-LRS-2/3: (1/ell)sum_P T <= N+(2/3)(N^2/25-m).  total paths=%d  violations=%d  %s"%(
        acc['paths'],acc['viol'],acc['fviol'] or ''),flush=True)
    print("  min margin = %s = %s  @ %s N=%d m=%d f=%s D=%s"%(str(mm[0]),str(float(mm[0]))[:8],mm[1],mm[2],mm[3],mm[4],mm[5]),flush=True)
    print("    equality path loads=%s avg=%s"%(mm[6],mm[7]),flush=True)
    print("  === PATH-LRS-2/3 %s ==="%("HOLDS on full battery + TWO-LANE" if acc['viol']==0 else "*** FAILS ***"),flush=True)
