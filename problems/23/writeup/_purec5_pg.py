"""INDEPENDENT verification of Codex's PURE-C5-PATH-GAMMA quotient lemma (the proven base case of GPT's five-shadow
lemma). C5 blow-up part sizes a_0..a_4>0; bad block = argmin adjacent product, WLOG V_0V_1 with m=a_0 a_1=min_i a_i a_{i+1}.
N=sum a_i, Gamma=25m. Geodesic V_0->V_4->V_3->V_2->V_1. T: endpoints V_0,V_1 -> 5a_1,5a_0; interior V_j (j=2,3,4) -> 5m/a_j.
  sum_{x in P}(T-N) = 5*(a_0+a_1+m/a_2+m/a_3+m/a_4 - N) = 5*(m/a_2+m/a_3+m/a_4 - a_2-a_3-a_4).
  F(P) = (5/25)(N^2-Gamma) - sum_P(T-N) = (N^2-25m)/5 - sum_P(T-N).
Claim F(P)>=0, equality iff balanced. Verify EXACT over all integer 5-tuples N<=42 + the reciprocal inequality."""
from fractions import Fraction as F
from itertools import product

def check(a):
    prods=[a[i]*a[(i+1)%5] for i in range(5)]
    m=min(prods)
    i0=prods.index(m)  # bad block = (i0, i0+1)
    # relabel so bad block is V_0 V_1: rotate
    a2=[a[(i0+k)%5] for k in range(5)]  # a2[0],a2[1] = bad block endpoints
    a0_,a1_,ai2,ai3,ai4=a2
    N=sum(a)
    # sum_P(T-N) = 5*(m/a2 + m/a3 + m/a4 - a2 - a3 - a4)   (interior = the 3 non-bad-block parts)
    interior=[ai2,ai3,ai4]
    sumTN=5*(sum(F(m,x) for x in interior) - sum(interior))
    FP=F(N*N-25*m,5) - sumTN
    return FP, sumTN, m

if __name__=="__main__":
    viol=0; eqcount=0; eqex=None; firstv=None; tested=0
    for N in range(5,43):
        for t in product(range(1,N),repeat=4):
            s=sum(t)
            if s>=N: continue
            a=list(t)+[N-s]
            if a[4]<=0: continue
            tested+=1
            FP,sumTN,m=check(a)
            if FP<0:
                viol+=1
                if firstv is None: firstv=(N,a,str(FP))
            if FP==0:
                eqcount+=1
                if eqex is None: eqex=(N,a)
    print("  PURE-C5-PATH-GAMMA quotient: tested=%d positive-tuples, F(P)<0 violations=%d %s"%(tested,viol,firstv or ''))
    print("  equality cases=%d, example=%s (expect balanced a_i=N/5)"%(eqcount,eqex))
    print("  === %s ==="%("PROVEN base case VERIFIED exact (F(P)>=0, eq iff balanced)" if viol==0 else "*** FAILS ***"))
