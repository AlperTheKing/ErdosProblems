"""Verify Codex's PURE ODD-CYCLE PATH-GAMMA quotient (generalizes pure-C5). Odd L; cyclic blow-up weights a_0..a_{L-1};
bad gap = argmin adjacent product = V_0V_1, m=a_0a_1. Gamma=L^2 m. T: V_0,V_1 -> L a_1, L a_0; interior V_j -> L m/a_j.
sum_P(T-N) = L*(m/a_2+...+m/a_{L-1} - a_2-...-a_{L-1}) <= 0 (cyclic reciprocal matching). F(P)=(L/25)(N^2-Gamma)-sum_P(T-N)>=0
needs L^2 m <= N^2 (cyclic min-product). Verify EXACT over integer tuples for L=5,7,9."""
from fractions import Fraction as F
from itertools import product

def check_tuple(a,L):
    prods=[a[i]*a[(i+1)%L] for i in range(L)]
    m=min(prods); i0=prods.index(m)
    ar=[a[(i0+k)%L] for k in range(L)]   # bad gap = (0,1)
    N=sum(a)
    interior=ar[2:]                       # V_2..V_{L-1}
    sumTN=L*(sum(F(m,x) for x in interior) - sum(interior))
    FP=F(L,25)*(N*N-L*L*m) - sumTN
    return FP

def run(L,Nmax):
    viol=0; firstv=None; tested=0; eqbal=0
    for N in range(L,Nmax+1):
        for t in product(range(1,N),repeat=L-1):
            s=sum(t)
            if s>=N: continue
            a=list(t)+[N-s]
            if a[-1]<=0: continue
            tested+=1
            FP=check_tuple(a,L)
            if FP<0:
                viol+=1
                if firstv is None: firstv=(N,a,str(FP))
            elif FP==0 and len(set(a))==1: eqbal+=1
    print("  L=%d: tested=%d  F(P)<0 viol=%d %s  (balanced-equality cases=%d)"%(L,tested,viol,firstv or '',eqbal))
    return viol

if __name__=="__main__":
    tot=0
    tot+=run(5,28)
    tot+=run(7,21)
    tot+=run(9,18)
    print("  === PURE ODD-CYCLE PATH-GAMMA %s ==="%("VERIFIED (F>=0 all odd L tested, eq at balanced)" if tot==0 else "FAILS"))
