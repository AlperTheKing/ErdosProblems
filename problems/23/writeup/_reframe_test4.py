"""Light, fast: census N<=10 + N=22 killer. Ff/Gg/SMQ split. (SMQ <=> SM exactly.)"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _reframe_test import Kdata, from_g6

def metrics(info):
    n,T,K,ell,M,pf=Kdata(info)
    N=n; Gamma=sum(L*L for L in ell.values()); D=N*N-Gamma
    over2=sum((x-N)*(x-N) for x in T if x>N)
    under2=sum((N-x)*(N-x) for x in T if x<N)
    return dict(N=N,Gamma=Gamma,D=D,over2=over2,under2=under2,
        Ff=over2<=N*D, Gg=under2<=N*D, SMQ=(over2+under2)<=N*D)

if __name__=="__main__":
    for g6,t in [("J???E?pNu\\?",2)]:
        info=from_g6(g6,t); m=metrics(info)
        print(f"N22-killer: Ff={m['Ff']} Gg={m['Gg']} SMQ={m['SMQ']} over2={float(m['over2']):.1f} under2={float(m['under2']):.1f} NxD={m['N']*m['D']}")
    for nn in range(5,11):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0;v={'Ff':0,'Gg':0,'SMQ':0}; mff=F(0)
        for g6 in out:
            info=loads(*dec(g6))
            if info is None: continue
            tot+=1; m=metrics(info)
            for k in v:
                if not m[k]: v[k]+=1
            slack=F(m['N'])*m['D']-m['over2']
            if slack<mff or mff==0: mff=slack
        print(f"N={nn}: tot={tot} Ff_viol={v['Ff']} Gg_viol={v['Gg']} SMQ_viol={v['SMQ']} minFf_slack={float(mff):.2f}")
