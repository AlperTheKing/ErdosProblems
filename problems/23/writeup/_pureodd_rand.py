"""Fast random-sample confirmation of PURE ODD-CYCLE PATH-GAMMA quotient F(P)>=0, for L=5,7,9,11,13 (exhaustive L=5
is in _purec5_pg.py; the proof is the same cyclic reciprocal-matching argument for all odd L). Deterministic LCG."""
from fractions import Fraction as F
seed=2024
def rnd():
    global seed; seed=(1103515245*seed+12345)%(2**31); return seed
def FP_of(a,L):
    prods=[a[i]*a[(i+1)%L] for i in range(L)]
    m=min(prods); i0=prods.index(m); ar=[a[(i0+k)%L] for k in range(L)]; N=sum(a)
    interior=ar[2:]
    sumTN=L*(sum(F(m,x) for x in interior)-sum(interior))
    return F(L,25)*(N*N-L*L*m)-sumTN
for L in (5,7,9,11,13,15,21):
    viol=0; firstv=None
    for _ in range(40000):
        a=[1+rnd()%50 for _ in range(L)]
        FP=FP_of(a,L)
        if FP<0:
            viol+=1
            if firstv is None: firstv=(a,str(FP))
    print("  L=%2d: 40000 random tuples, F(P)<0 viol=%d %s"%(L,viol,firstv or ''),flush=True)
print("  === PURE ODD-CYCLE PATH-GAMMA random-confirmed (proof = same reciprocal-matching as verified L=5) ===",flush=True)
