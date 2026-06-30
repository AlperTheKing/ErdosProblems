"""Test the DIRICHLET / minimality reframe of SM (sum_v T^2 <= N*Gamma).

Setup recap: K=PP^T (V x V), K_vw=sum_f p_f(v)p_f(w), K1=T, B=diag(T)-K is a weighted
graph Laplacian (PSD, B1=0) with edge weights K_vw and degrees T(v). So for ANY z:
   z^T B z = (1/2) sum_{v,w} K_vw (z_v - z_w)^2.

SM <=> sum_v T(v)^2 <= N*sum_v T(v) <=> sum_v T(v)(T(v)-N) <= 0  [coup].

REFRAME CANDIDATE (Dirichlet identity):  apply the Laplacian quadratic form to z=T.
   T^T B T = (1/2) sum_{v,w} K_vw (T_v - T_w)^2  >= 0  (call it Dir).
Also T^T B T = T^T diag(T) T - T^T K T = sum_v T_v^3 - sum_v T_v (KT)_v.
Define R(v) := (K T)_v / T(v)  (the geodesic-averaged neighbor load, a 'Rayleigh local mean').
The KEY identity to use: ROWSUM-O said (KT)_v <= N*T(v) i.e. R(v)<=N pointwise (Collatz-Wielandt).

NEW CANDIDATE INEQUALITY (the actual proposal): a *Dirichlet drop* bound
   (D2)  sum_v (T_v - N)_+^2  <=  (1/2) sum_{v,w} K_vw (T_v - T_w)^2  =  T^T B T.
If (D2) holds, combine with B PSD ... test whether D2 even holds, and whether it implies SM.

Also test the cleaner spectral-comparison candidate:
   (LAPCOMP) N*I - K  >=  c * L_B   for the cut-graph (B-edge) Laplacian L_B and some c>0 fixed,
   ON THE SUBSPACE orthogonal to 1?  -- we test via: is (N*I-K) - L_Bnorm PSD where L_Bnorm scaled.
We just compute eigen-data numerically to GUIDE, plus exact coup test.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads

def Kdata(info):
    n=info['n']; M=info['M']; cyc=info['cyc']
    pf=[]
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for P in Ps:
            for v in P: cnt[v]=cnt.get(v,0)+1
        pf.append({v: F(cnt[v],nf) for v in cnt})
    ell={fi:len(cyc[f][0]) for fi,f in enumerate(M)}
    T=[F(0)]*n
    for fi in range(len(M)):
        L=ell[fi]
        for v,val in pf[fi].items(): T[v]+=val*L
    # K as dict
    K={}
    for fi in range(len(M)):
        items=list(pf[fi].items())
        for (v,a) in items:
            for (w,b) in items:
                K[(v,w)]=K.get((v,w),F(0))+a*b
    return n,T,K,ell,M,pf

def from_g6(g6,t=1):
    n0,E0=dec(g6)
    if t>1:
        n=n0*t; E=[]
        for (a,b) in E0:
            for i in range(t):
                for j in range(t): E.append((a*t+i,b*t+j))
    else:
        n,E=n0,E0
    return loads(n,E)

def metrics(info):
    n,T,K,ell,M,pf=Kdata(info)
    N=n
    Gamma=sum(L*L for L in ell.values())
    sumT=sum(T); sumT2=sum(x*x for x in T)
    SM = sumT2 <= N*Gamma
    coup = sum(x*(x-N) for x in T)            # <=0 <=> SM
    # Dirichlet T^T B T = sum_v T_v^3 - sum_{v,w} K_vw T_v T_w
    KT=[F(0)]*n
    for (v,w),val in K.items(): KT[v]+=val*T[w]
    TBT = sum(T[v]*(T[v]*T[v]) for v in range(n)) - sum(T[v]*KT[v] for v in range(n))
    over2 = sum((x-N)*(x-N) for x in T if x>N)
    D2 = over2 <= TBT
    # also: does pointwise R(v)=(KT)_v/T(v) <= N hold? (ROWSUM-O Collatz form)
    cw_ok = all(KT[v] <= N*T[v] for v in range(n) if T[v]>0)
    return dict(N=N,Gamma=Gamma,sumT=sumT,sumT2=sumT2,SM=SM,coup=coup,coup_le0=coup<=0,
                TBT=TBT,over2=over2,D2=D2,cw_ok=cw_ok)

if __name__=="__main__":
    print("=== witnesses ===")
    for g6,t in [("J???E?pNu\\?",2),("J?AEB?oE?W?",2),("H?bB@_W",2)]:
        info=from_g6(g6,t)
        if info is None: print(g6,t,"skip"); continue
        m=metrics(info)
        print(f"{g6}[{t}] N={m['N']} SM={m['SM']} D2={m['D2']} cw={m['cw_ok']} coup={float(m['coup']):.1f} TBT={float(m['TBT']):.1f} over2={float(m['over2']):.1f}")
    print("=== census ===")
    for nn in range(5,11):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0;vSM=0;vD2=0;vcw=0
        for g6 in out:
            info=loads(*dec(g6))
            if info is None: continue
            tot+=1; m=metrics(info)
            if not m['SM']: vSM+=1
            if not m['D2']: vD2+=1
            if not m['cw_ok']: vcw+=1
        print(f"N={nn}: tot={tot} SM_viol={vSM} D2_viol={vD2} cw_viol={vcw}")
