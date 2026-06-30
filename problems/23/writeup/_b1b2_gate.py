"""EXACT gate of Codex block-217 split bounds for LRS:
  (B1) R_load = (sum_v T^2)/Gamma <= 2N    [<=> sum T^2 <= 2 N Gamma, the dead SM with double room]
  (B2) Tmax = max_v T(v) <= 2N             [B2 => B1 since sum T^2 <= Tmax*sum T = Tmax*Gamma]
B1 + LRS-RHS gives LRS whenever |M| <= N^2/25 - N (R_load+|M| <= 2N+|M| <= N+N^2/25). Report max R_load/N,
max Tmax/N, and first violation. Battery: census gamma-min N<=11 + blow-ups + two-lane L=8..20 + Mycielskians
+ full/merged detour + stacked adversarial. EXACT Fraction."""
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
    Gamma=sum(ell[f]**2 for f in M)
    sumT2=sum(t*t for t in T)
    Rload=F(sumT2,Gamma) if Gamma else F(0)
    Tmax=max(T)
    acc['n']+=1
    if Rload>acc['maxR'][0]: acc['maxR']=(Rload,name,n,float(Rload/n))
    if Tmax>acc['maxT'][0]: acc['maxT']=(Tmax,name,n,float(Tmax/n))
    if Rload>2*n:
        acc['b1_fail']+=1
        if acc['first1'] is None: acc['first1']=(name,n,len(M),Gamma,str(Rload))
    if Tmax>2*n:
        acc['b2_fail']+=1
        if acc['first2'] is None: acc['first2']=(name,n,len(M),str(Tmax))

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
    acc={'n':0,'b1_fail':0,'b2_fail':0,'first1':None,'first2':None,
         'maxR':(F(0),'','',0.0),'maxT':(F(0),'','',0.0)}
    print("=== B1 (R_load<=2N) / B2 (Tmax<=2N) exact gate ===",flush=True)
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    print("  two-lane done maxR=%.4f maxT=%.4f"%(acc['maxR'][3],acc['maxT'][3]),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        b0=acc['b1_fail']; c0=acc['b2_fail']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (B1fail=%d B2fail=%d) maxR/N=%.4f maxT/N=%.4f"%(nn,acc['b1_fail']-b0,acc['b2_fail']-c0,acc['maxR'][3],acc['maxT'][3]),flush=True)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:1] if cuts else []): chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:1] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9)))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: chk(name,nn,adj,s,acc)
    for tag,wm in [("full-detour",False),("merged-detour",True)]:
        n,E=build_pd(12,[(0,8),(2,6)]); side=[v%2 for v in range(n)]; n,E,side=add_cut_path(n,list(E),side,0,12,14)
        E=sorted(set(E+[(13,27)])) if wm else sorted(set(E)); chk(tag,n,adj_of(n,E),side,acc)
    for L in (10,12,14):
        n1,E1,s1,_=build_two_lane(L); n2,E2,s2,_=build_two_lane(L)
        E2s=[(a+n1,b+n1) for a,b in E2]; br=[(0,n1)] if s1[0]!=s2[0] else [(0,n1+1)]
        chk("stack2-L%d"%L,n1+n2,adj_of(n1+n2,sorted(set(E1+E2s+br))),s1+s2,acc)
    print("\n  total configs=%d  B1 failures=%d  B2 failures=%d"%(acc['n'],acc['b1_fail'],acc['b2_fail']),flush=True)
    print("  MAX R_load/N = %.4f at %s"%(acc['maxR'][3],acc['maxR'][1:3]),flush=True)
    print("  MAX Tmax/N   = %.4f at %s"%(acc['maxT'][3],acc['maxT'][1:3]),flush=True)
    if acc['first1']: print("  first B1 violation: %s"%(acc['first1'],),flush=True)
    if acc['first2']: print("  first B2 violation: %s"%(acc['first2'],),flush=True)
    print("  === B1 %s ; B2 %s ==="%("HOLDS" if not acc['b1_fail'] else "FAILS","HOLDS" if not acc['b2_fail'] else "FAILS"),flush=True)
