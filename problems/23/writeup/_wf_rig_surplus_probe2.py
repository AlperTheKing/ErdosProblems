"""PROBE 2 (exact): pin down the surplus route. Two questions:
 (A) Is Uplus <= C * S2 REFUTED?  Report configs with S2=0 & Uplus>0 (max Uplus there).
 (B) The REAL inequality. LOAD-PSC-5 LHS = sumT_TminN + (N/5)(TVcut-TVbad).
     Note sumT_TminN = sum_v T_v^2 - N*sum_v T_v = sum_v T_v^2 - N*Gamma  (handshake: sum_v T_v = Gamma).
     Define V2 = sum_v (T_v-N)^2 = sum T_v^2 - 2N*Gamma + N^2*N = sum T_v^2 - 2N Gamma + N^3.
     So sumT_TminN = V2 + 2N Gamma - N^3 - N Gamma = V2 + N Gamma - N^3 = V2 + N(Gamma - N^2).
     Hence LOAD-PSC-5 <=> V2 + N(Gamma-N^2) + (N/5)(TVcut-TVbad) <= Gamma(N^2/25 - beta).
     Rearranged with Gamma=25beta+S2: report each piece so we see what carries the Mycielskians.
 (C) Test the candidate combined surplus bound:
        V2 + (N/5)(TVcut-TVbad) <= Gamma*(N^2/25-beta) - N(Gamma-N^2)
     i.e. exactly LOAD-PSC-5. Confirm via direct margin (sanity vs _loadpsc_gate).
 (D) Measure ratio  V2 / (Gamma*(N^2/25-beta))  and  V2 / S2  to see whether V2 (load variance, the quadratic
     surplus that DOES survive Mycielskians) is the right pay-er, and at what constant.
"""
import subprocess
from fractions import Fraction as F
from _wf_rig_surplus_explore import full_battery
from _h import Bconn
from _satzmu_conn import struct_for_side

def measure(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    N=n; beta=len(M)
    Gamma=sum(ell[f]**2 for f in M)
    budget5=Gamma*(F(N*N,25)-beta)
    Uplus=sum((t-N) for t in T if t>N)
    sumT2=sum(t*t for t in T)
    sumT=sum(T)            # should equal Gamma (handshake)
    V2=sum((t-N)**2 for t in T)
    sumT_TminN=sum(t*(t-N) for t in T)
    badset=set((min(a,b),max(a,b)) for a,b in M)
    TVcut=F(0); TVbad=F(0)
    for u in range(n):
        for v in adj[u]:
            if v>u:
                d=abs(T[u]-T[v])
                if side[u]!=side[v]: TVcut+=d
                else: TVbad+=d
    S2=Gamma-25*beta
    lhs5=sumT_TminN + F(N,5)*(TVcut-TVbad)
    acc.append(dict(name=name,N=N,beta=beta,Gamma=Gamma,budget5=budget5,Uplus=Uplus,
                    sumT2=sumT2,sumT=sumT,V2=V2,sumT_TminN=sumT_TminN,TVcut=TVcut,TVbad=TVbad,
                    S2=S2,lhs5=lhs5))

if __name__=="__main__":
    acc=full_battery(measure)
    print("total configs =",len(acc),flush=True)
    # (handshake sanity)
    hs_bad=[r['name'] for r in acc if r['sumT']!=r['Gamma']]
    print("handshake sum_v T_v == Gamma failures:",len(hs_bad), hs_bad[:3],flush=True)
    # (A) S2=0 but Uplus>0
    s2z=[r for r in acc if r['S2']==0 and r['Uplus']>0]
    print("configs with S2=0 AND Uplus>0:",len(s2z),flush=True)
    if s2z:
        mx=max(s2z,key=lambda r:r['Uplus'])
        print("   max Uplus among them:",float(mx['Uplus']),"at",mx['name'],"N=",mx['N'],
              " => Uplus<=C*S2 REFUTED (denominator 0).",flush=True)
    # (B/C) LOAD-PSC-5 direct margin (should be >=0 everywhere = sanity)
    nviol=0; minmarg=None
    for r in acc:
        marg=r['budget5']-r['lhs5']
        if marg<0: nviol+=1
        if minmarg is None or marg<minmarg[0]: minmarg=(marg,r['name'],r['N'])
    print("LOAD-PSC-5 direct: violations=%d  min margin=%s at %s"%(nviol,float(minmarg[0]),minmarg[1:]),flush=True)
    # (D) V2 / budget5  and  V2 / S2 ; also identity check sumT_TminN == V2 + N*(Gamma-N^2)
    idfail=[r['name'] for r in acc if r['sumT_TminN']!=r['V2']+r['N']*(r['Gamma']-r['N']**2)]
    print("identity sumT_TminN==V2+N(Gamma-N^2) failures:",len(idfail),idfail[:3],flush=True)
    # max V2/budget5
    cand=[(F(r['V2'],r['budget5']),r['name'],r['N']) for r in acc if r['budget5']>0]
    if cand:
        mx=max(cand)
        print("max V2/budget5 = %s at %s"%(float(mx[0]),mx[1:]),flush=True)
    # configs where budget5==0 (beta=N^2/25) must have V2==0 (rigidity)
    rig=[r for r in acc if r['budget5']==0]
    rigbad=[r['name'] for r in rig if r['V2']!=0]
    print("rigidity: budget5=0 configs=%d  with V2!=0 =%d %s"%(len(rig),len(rigbad),rigbad[:3]),flush=True)
