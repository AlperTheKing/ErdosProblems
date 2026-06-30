"""SURPLUS ROUTE -- exact Fraction gate on the FULL standing battery.

CENTRAL INEQUALITY (SURPLUS-PSC-5), in the load-variance ("surplus") form:
    V2 + N*(Gamma - N^2) + (N/5)*(TVcut - TVbad)  <=  Gamma*(N^2/25 - beta)
  where V2 = sum_v (T_v - N)^2  (load variance),  Gamma = sum_f ell_f^2,  beta = |M|.

This is EXACTLY LOAD-PSC-5: by the handshake (sum_v T_v = Gamma) one has the EXACT identity
    sum_v T_v(T_v - N) = sum_v T_v^2 - N*Gamma = [V2 - 2N Gamma + N^3] + ... = V2 + N*(Gamma - N^2),
  so SURPLUS-PSC-5 <=> sum_v T_v(T_v-N) + (N/5)(TVcut-TVbad) <= Gamma(N^2/25-beta) = LOAD-PSC-5.
LOAD-PSC-5 => beta <= N^2/25 (the Erdos bound). So SURPLUS-PSC-5, if true, IMPLIES the target.

WHY THE *LITERAL* PER-BAD-EDGE ell-SURPLUS ROUTE IS DEAD (also gated below):
  the per-edge surplus is S1 = sum_f (ell_f - 5) (linear) and S2 = sum_f (ell_f^2 - 25) = Gamma - 25*beta
  (quadratic). Any bound "Uplus = sum_v (T_v-N)_+ <= C * S1" or "<= C * S2" is REFUTED: there are configs
  with S1 = S2 = 0 (every bad edge has ell=5) yet Uplus > 0 (e.g. Myc(Grotzsch) N=23, Uplus = 20581/819).
  The over-load is paid NON-LOCALLY by the global load variance V2, not by any per-edge ell-surplus.
  So: ell-5 (linear) does NOT suffice; ell^2-25 (quadratic per-edge) does NOT suffice either.

This gate reports, for SURPLUS-PSC-5: #violations, min margin, binding config, AND the extremal constant
  K* = max over battery of  V2 / (Gamma*(N^2/25-beta))   (the load-variance certificate constant; the prompt's
  V2 <= K*Gamma(N^2/25-beta) with K<=151/16).  Plus the ell-surplus refutation counters.
ALL arithmetic is exact fractions.Fraction. Battery = the full standing battery.
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

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    N=n; beta=len(M)
    Gamma=sum(ell[f]**2 for f in M)
    sumT=sum(T)                       # handshake: == Gamma
    assert sumT==Gamma, ("HANDSHAKE FAIL",name)
    V2=sum((t-N)**2 for t in T)
    sumT_TminN=sum(t*(t-N) for t in T)
    # exact identity check (load-bearing): sum_v T_v(T_v-N) == V2 + N*(Gamma-N^2)
    assert sumT_TminN==V2+N*(Gamma-N*N), ("IDENTITY FAIL",name)
    Uplus=sum((t-N) for t in T if t>N)
    badset=set((min(a,b),max(a,b)) for a,b in M)
    TVcut=F(0); TVbad=F(0)
    for u in range(n):
        for v in adj[u]:
            if v>u:
                d=abs(T[u]-T[v])
                if side[u]!=side[v]: TVcut+=d
                else: TVbad+=d
    budget5=Gamma*(F(N*N,25)-beta)    # Gamma*(N^2/25 - beta)
    # CENTRAL INEQUALITY (surplus/variance form of LOAD-PSC-5):
    lhs = V2 + N*(Gamma - N*N) + F(N,5)*(TVcut-TVbad)
    margin = budget5 - lhs
    acc['n']+=1
    if margin<acc['minmarg'][0]: acc['minmarg']=(margin,name,N,beta)
    if margin<0:
        acc['viol']+=1
        if acc['first'] is None: acc['first']=(name,N,beta,float(margin))
    # extremal constant K* = V2 / budget5  (only where budget5>0)
    if budget5>0:
        rK=F(V2,budget5)
        if rK>acc['Kstar'][0]: acc['Kstar']=(rK,name,N,beta)
    else:
        # rigidity: budget5==0 must force V2==0
        if V2!=0: acc['rigfail']+=1
    # ell-surplus refutation counters
    S1=sum((ell[f]-5) for f in M); S2=Gamma-25*beta
    if S2==0 and Uplus>0:
        acc['S2zero_Uplus']+=1
        if Uplus>acc['S2zero_maxUplus'][0]: acc['S2zero_maxUplus']=(Uplus,name,N)
    if S1==0 and Uplus>0:
        acc['S1zero_Uplus']+=1

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
    acc=dict(n=0,viol=0,first=None,minmarg=(F(10**18),'','',''),
             Kstar=(F(0),'','',''),rigfail=0,
             S2zero_Uplus=0,S2zero_maxUplus=(F(0),'',''),S1zero_Uplus=0)
    print("=== SURPLUS-PSC-5 EXACT gate: V2 + N(Gamma-N^2) + (N/5)(TVcut-TVbad) <= Gamma(N^2/25-beta) ===",flush=True)
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane done: viol=%d minmarg=%s"%(acc['viol'],float(acc['minmarg'][0])),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        a0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (viol+%d)"%(nn,acc['viol']-a0),flush=True)
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
    print("\n  total configs = %d"%acc['n'],flush=True)
    print("  SURPLUS-PSC-5 violations = %d"%acc['viol'],flush=True)
    print("  min margin = %s at %s"%(str(acc['minmarg'][0]),acc['minmarg'][1:]),flush=True)
    if acc['first']: print("  FIRST violation: %s"%(acc['first'],),flush=True)
    print("  extremal constant K* = V2/(Gamma(N^2/25-beta)) max = %s = %s at %s"%(
        str(acc['Kstar'][0]),float(acc['Kstar'][0]),acc['Kstar'][1:]),flush=True)
    print("  rigidity failures (budget5=0 but V2!=0) = %d"%acc['rigfail'],flush=True)
    print("  --- ell-surplus REFUTATION ---",flush=True)
    print("  configs with S2=Gamma-25beta=0 AND Uplus>0 : %d  (=> Uplus<=C*S2 FALSE)"%acc['S2zero_Uplus'],flush=True)
    print("     max Uplus among them = %s = %s at %s"%(str(acc['S2zero_maxUplus'][0]),float(acc['S2zero_maxUplus'][0]),acc['S2zero_maxUplus'][1:]),flush=True)
    print("  configs with S1=sum(ell-5)=0 AND Uplus>0 : %d  (=> Uplus<=C*S1 FALSE)"%acc['S1zero_Uplus'],flush=True)
    print("  === SURPLUS-PSC-5 %s ==="%("HOLDS" if not acc['viol'] else "FAILS"),flush=True)
