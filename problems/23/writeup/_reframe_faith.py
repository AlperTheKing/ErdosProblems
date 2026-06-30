"""FAITHFULNESS: (Ff) over2<=N*D and (SMQ) must FAIL on graphs WITH triangles where Gamma>N^2,
else they are free structural facts (not using triangle-freeness/odd-girth>=5).
Use general connected graphs (geng without -t), keep those with connected-B max cut + bad edges + Gamma>N^2."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _reframe_test import Kdata

def metrics(info):
    n,T,K,ell,M,pf=Kdata(info)
    N=n; Gamma=sum(L*L for L in ell.values()); D=N*N-Gamma
    over2=sum((x-N)*(x-N) for x in T if x>N)
    under2=sum((N-x)*(N-x) for x in T if x<N)
    return dict(N=N,Gamma=Gamma,D=D,over2=float(over2),under2=float(under2),
        Ff=over2<=N*D, SMQ=(over2+under2)<=N*D, gbad=Gamma>N*N)

if __name__=="__main__":
    # general graphs (may have triangles), shorter B-geodesics possible (girth-3 odd cycles)
    for nn in range(5,9):
        out=subprocess.run([GENG,"-c",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0; gbad=0; ffv=0; smqv=0; ffv_when_gbad=0
        for g6 in out:
            info=loads(*dec(g6))
            if info is None: continue
            tot+=1; m=metrics(info)
            if m['gbad']:
                gbad+=1
                if not m['Ff']: ffv_when_gbad+=1
            if not m['Ff']: ffv+=1
            if not m['SMQ']: smqv+=1
        print(f"N={nn}(ALL graphs): tot={tot} Gamma>N^2:{gbad} | Ff_viol_total={ffv} SMQ_viol_total={smqv} | Ff_viol_among_gbad={ffv_when_gbad}")
