"""EXACT gate of PATH-LRS (per shortest geodesic path P) at coefficients 1 and 2/3 (Codex blocks 219/220):
  A_{f,P} = (1/ell(f)) * sum_{v in P} T(v).
  (c1)   A_{f,P} + |M| <= N + N^2/25                       [PATH-LRS, theorem-sufficient]
  (c23)  A_{f,P}      <= N + (2/3)*(N^2/25 - |M|)          [sharper, => c1 when deficit>=0]
Battery: census gamma-min N<=11 + two-lane + blow-ups + Mycielskians + detours. EXACT. Report min margins +
first violation of each; note equality cases."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn
from _verify_two_lane import build_two_lane
from _tail_positive_extra_counterexample import add_cut_path, adj_from_edges
from _M_tailswitch_gate import build_pd

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    m=len(M); rhs1=F(n)+F(n*n,25); defi=F(n*n,25)-m; rhs23=F(n)+F(2,3)*defi
    for f in M:
        for P in cyc[f]:
            avg=sum(T[v] for v in P)/ell[f]
            mar1=rhs1-(avg+m); mar23=rhs23-avg
            acc['paths']+=1
            if mar1<acc['min1'][0]: acc['min1']=(mar1,name,n,m,f)
            if mar23<acc['min23'][0]: acc['min23']=(mar23,name,n,m,f,str(defi))
            if mar1<0:
                acc['v1']+=1
                if acc['f1'] is None: acc['f1']=(name,n,m,f,ell[f],str(avg),str(rhs1))
            if mar23<0:
                acc['v23']+=1
                if acc['f23'] is None: acc['f23']=(name,n,m,f,str(avg),str(rhs23))

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a

if __name__=="__main__":
    acc={'paths':0,'v1':0,'v23':0,'f1':None,'f23':None,'min1':(F(10**9),'','','',''),'min23':(F(10**9),'','','','','')}
    print("=== PATH-LRS exact gate (coeff 1 and 2/3) ===",flush=True)
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    print("  two-lane done (min-c1=%s min-c23=%s)"%(float(acc['min1'][0]),float(acc['min23'][0])),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        a0=acc['v1']; b0=acc['v23']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (c1-viol=%d c23-viol=%d)"%(nn,acc['v1']-a0,acc['v23']-b0),flush=True)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:1] if cuts else []): chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:1] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7)))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: chk(name,nn,adj,s,acc)
    for tag,wm in [("full-detour",False),("merged-detour",True)]:
        n,E=build_pd(12,[(0,8),(2,6)]); side=[v%2 for v in range(n)]; n,E,side=add_cut_path(n,list(E),side,0,12,14)
        E=sorted(set(E+[(13,27)])) if wm else sorted(set(E)); chk(tag,n,adj_of(n,E),side,acc)
    print("\n  total paths=%d  PATH-LRS(c1) viol=%d  PATH-LRS-2/3(c23) viol=%d"%(acc['paths'],acc['v1'],acc['v23']),flush=True)
    print("  MIN c1 margin=%s at %s ; MIN c23 margin=%s at %s"%(float(acc['min1'][0]),acc['min1'][1:],float(acc['min23'][0]),acc['min23'][1:]),flush=True)
    if acc['f1']: print("  first c1 viol: %s"%(acc['f1'],),flush=True)
    if acc['f23']: print("  first c23 viol: %s"%(acc['f23'],),flush=True)
    print("  === PATH-LRS(c1) %s ; 2/3-sharpening %s ==="%("HOLDS" if not acc['v1'] else "FAILS","HOLDS" if not acc['v23'] else "FAILS"),flush=True)
