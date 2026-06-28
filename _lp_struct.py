import numpy as np
from fractions import Fraction as F
from _h import dec, loads
from _layerprice_verify import get_prices
from _layerprice import layers_of
# For overloaded graphs, dump optimal b_{f,i} vs layer stats: does b correlate with a clean quantity?
def Svec(info):
    S={}
    for f in info['M']:
        Ps=info['cyc'][f]; nf=len(Ps); cnt={}
        for P in Ps:
            for v in P: cnt[v]=cnt.get(v,0)+1
        for v,c in cnt.items(): S[v]=S.get(v,0.0)+c/nf
    return S
for g6 in ["I?BD@g]Qo","I?ABCc]}?"]:
    n,E=dec(g6); info=loads(n,E); N=n; S=Svec(info); T=info['T']
    b,idx,perf,Ls,M,tstar=get_prices(info)
    print(f"\n=== {g6} N={n} t*={tstar:.3f} ===")
    for fi,f in enumerate(M):
        lay,pf,h=Ls[fi]
        print(f" edge {f} ell={info['ell'][f]}: harmonic sum 1/b = {sum(1/b[(f,i)] for i in range(h+1)):.3f}")
        for i in range(h+1):
            vs=lay[i]
            sumS=sum(S[v] for v in vs); sumT=sum(float(T[v]) for v in vs); maxS=max((S[v] for v in vs),default=0)
            sump=sum(pf[v] for v in vs)
            print(f"   layer {i}: b={b[(f,i)]:.3f} | |I|={len(vs)} sum_p={sump:.3f} sumS={sumS:.3f} maxS={maxS:.3f} sumT={sumT:.3f} | b*sqrt? N/sumT={N/sumT if sumT else 0:.3f}")
