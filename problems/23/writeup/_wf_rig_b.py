"""ROUTE (b) GRAM/SOS gate -- EXACT Fraction, FULL standing battery.

We decompose the LOAD-PSC slack into two interpretable pieces and gate each, plus the
genuine SOS/Gram inequality that does the work.

Centered load x_v = T_v - N.  Handshake: sum_v T_v = Gamma => sum_v x_v = Gamma - N^2.
LOAD-PSC-5 slack:
   S = Gamma*(N^2/25 - beta) - sum_v T_v(T_v-N) - (N/5)(TVcut - TVbad)
     = Q1 - nx2 - N*sum(x) - (N/5)(TVcut-TVbad)            [since sum_v T(T-N)=nx2+N sum x]
     = (Q1 - nx2) + (RES - PEN)
   where  Q1  = Gamma*(N^2/25 - beta)       (the budget)
          nx2 = ||x||^2 = sum_v (T_v-N)^2   (= V2)
          RES = -N*sum(x) = N*(N^2 - Gamma) = N*sum_v(N - T_v)     (under-load reservoir)
          PEN = (N/5)(TVcut - TVbad).

GATED INEQUALITIES (all exact):
  (LOAD-PSC-5)  S >= 0                                   [the target]
  (B-RES)       RES >= PEN   <=>  5*sum_v(N-T_v) >= TVcut - TVbad   [standalone, Gram-clean]
  (B-V2K)       nx2 <= K*Q1   with K = 151/16            [rigidity, given]
  (B-SOS)       the COMBINED certificate that proves S>=0 from B-RES + a V2 bound:
        S = (RES - PEN) + (Q1 - nx2) >= 0.
        If B-RES holds, S>=0 whenever Q1 - nx2 >= -(RES-PEN), i.e. nx2 <= Q1 + (RES-PEN).
        So we ALSO gate (B-COMBINED): nx2 <= Q1 + (RES - PEN)   [which is literally S>=0; tautology check].

We additionally measure the GRAM eigen-structure:  the matrix whose PSD-ness would give a
homogeneous SOS is impossible (slack is concave in x); instead we report the exact constants
needed for the reduction "B-RES + V2-bound => LOAD-PSC":
   Need:  Q1 + (RES - PEN) - nx2 >= 0.  Using nx2 <= Kbound*Q1 is NOT enough (Kbound>1);
   the binding object is RES-PEN vs nx2-Q1.  We track max of (nx2-Q1)/(RES-PEN) over battery
   (must be <= 1 for S>=0, and that ratio's sup is the true tightness of the reduction).
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

KBOUND=F(151,16)

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    N=n; m=len(M); Gamma=sum(ell[f]**2 for f in M)
    x=[T[v]-N for v in range(n)]
    nx2=sum(xi*xi for xi in x)
    TVcut=TVbad=F(0)
    for u in range(n):
        for v in adj[u]:
            if v>u:
                ad=abs(T[u]-T[v])
                if side[u]!=side[v]: TVcut+=ad
                else: TVbad+=ad
    Q1=Gamma*(F(N*N,25)-m)
    RES=N*(N*N-Gamma)
    PEN=F(N,5)*(TVcut-TVbad)
    S=Q1-nx2-N*sum(x)-PEN   # == (Q1-nx2)+(RES-PEN)
    acc['n']+=1
    # (LOAD-PSC-5)
    if S<acc['mS'][0]: acc['mS']=(S,name,N,m)
    if S<0:
        acc['vS']+=1
        if acc['fS'] is None: acc['fS']=(name,N,m,float(S))
    # (B-RES)
    bres=RES-PEN
    if bres<acc['mres'][0]: acc['mres']=(bres,name,N,m)
    if bres<0:
        acc['vres']+=1
        if acc['fres'] is None: acc['fres']=(name,N,m,float(bres))
    # (B-V2K): nx2 <= KBOUND*Q1
    if Q1>0:
        Krat=F(nx2,Q1)
        if Krat>acc['maxK'][0]: acc['maxK']=(Krat,name,N,m)
        if nx2>KBOUND*Q1:
            acc['vK']+=1
            if acc['fK'] is None: acc['fK']=(name,N,m,float(Krat))
    # tightness of reduction: (nx2-Q1)/(RES-PEN) when RES-PEN>0
    defi=nx2-Q1
    if bres>0:
        rr=F(defi,bres)
        if rr>acc['maxR'][0]: acc['maxR']=(rr,name,N,m)
    elif bres==0:
        # then need defi<=0 for S>=0
        if defi>0:
            acc['vR0']+=1

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
    BIG=F(10**18)
    acc=dict(n=0,vS=0,vres=0,vK=0,vR0=0,fS=None,fres=None,fK=None,
             mS=(BIG,'','',''),mres=(BIG,'','',''),maxK=(F(-1),'','',''),maxR=(F(-1),'','',''))
    print("=== ROUTE (b) Gram/SOS gate: LOAD-PSC-5 decomposed S=(Q1-nx2)+(RES-PEN) ===",flush=True)
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad)
        chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane done: vS=%d vres=%d"%(acc['vS'],acc['vres']),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        a0=acc['vS']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (vS+%d, configs=%d)"%(nn,acc['vS']-a0,acc['n']),flush=True)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:1] if cuts else []): chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3],[1,6,2,2,6]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:1] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    def bridge(b1,b2,u,v):
        nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u, n1+v)]
    extra=[("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
           ("C7|brg|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|brg|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0))]
    for name,(nn,E) in extra:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: chk(name,nn,adj,s,acc)
    print("  blow-ups + Mycielskians + glued done",flush=True)
    print("\n  total configs=%d"%acc['n'],flush=True)
    print("  (LOAD-PSC-5)  S>=0 : violations=%d  min S=%s at %s"%(acc['vS'],float(acc['mS'][0]),acc['mS'][1:]),flush=True)
    if acc['fS']: print("       first S<0: %s"%(acc['fS'],),flush=True)
    print("  (B-RES) RES>=PEN [5*sum(N-T) >= TVcut-TVbad] : violations=%d  min(RES-PEN)=%s at %s"%(
        acc['vres'],float(acc['mres'][0]),acc['mres'][1:]),flush=True)
    if acc['fres']: print("       first B-RES<0: %s"%(acc['fres'],),flush=True)
    print("  (B-V2K) nx2<=(151/16)Q1 : violations=%d  max nx2/Q1=%s=%.5f at %s"%(
        acc['vK'],acc['maxK'][0],float(acc['maxK'][0]),acc['maxK'][1:]),flush=True)
    print("  REDUCTION tightness max (nx2-Q1)/(RES-PEN) [must be <=1] = %s = %.5f at %s ; RES-PEN==0&deficit>0 count=%d"%(
        acc['maxR'][0],float(acc['maxR'][0]),acc['maxR'][1:],acc['vR0']),flush=True)
    print("  === LOAD-PSC-5 %s ; B-RES %s ==="%(
        "FAILS" if acc['vS'] else "HOLDS","FAILS" if acc['vres'] else "HOLDS"),flush=True)
