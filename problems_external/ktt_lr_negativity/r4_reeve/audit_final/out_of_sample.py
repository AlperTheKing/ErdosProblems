"""End-to-end out-of-sample test of the certificate route on FRESH hive polytopes.
For each: independent a1 (interpolation) and independent Lambda (edge extractor);
check B.Lambda=0, Lambda.mu==a1, a1>=0. mu and normals from the certificate only."""
import json, random, sys
from fractions import Fraction as F
from math import gcd
from hive import constraints, _partial, INTERIOR
from scan import coeffs
from edges import NORMALS, IDXPAIRS, lambda_vec, _rank_rows
from cert_verify import cross

c=json.load(open("E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/r4_reeve/q2_basis_witness_certificate.json"))
MU=[F(s) for s in c['mu']]
# natural-sign B
def redgcd(v):
    g=0
    for x in v: g=gcd(g,abs(x))
    return tuple(x//g for x in v) if g else tuple(v)
NP=len(IDXPAIRS)
B=[[0]*NP for _ in range(45)]
for k,(i,j) in enumerate(IDXPAIRS):
    u=redgcd(cross(NORMALS[i],NORMALS[j]))
    for t in range(3):
        B[3*i+t][k]+=u[t]; B[3*j+t][k]-=u[t]
NIDX={n:k for k,n in enumerate(NORMALS)}

def hive_to_nb(lam,mu,nu):
    cons=constraints(lam,mu,nu)
    b=[None]*15
    for (a0,a1,a2,rhs) in cons:
        coef=(a0,a1,a2)
        g=0
        for x in coef: g=gcd(g,abs(x))
        if g==0:  # constant constraint 0>=rhs ; feasibility only
            if 0 < rhs: return None  # infeasible
            continue
        n=tuple(-x//1 for x in coef)  # -coef
        npr=tuple(F(-x,g) for x in coef)
        npr=tuple(int(y) for y in npr)
        bb=F(-rhs,g)
        if npr not in NIDX: return "BADNORMAL"
        k=NIDX[npr]
        b[k]=bb if b[k] is None else min(b[k],bb)
    # any missing normal -> loose bound
    BIG=F(10**9)
    b=[bb if bb is not None else BIG for bb in b]
    return b

def main():
    random.seed(4242)
    ntest=int(sys.argv[1]) if len(sys.argv)>1 else 400
    maxpart=int(sys.argv[2]) if len(sys.argv)>2 else 25
    def rp(mp):
        p=sorted([random.randint(1,mp) for _ in range(4)],reverse=True);return p
    def mk(lam,mu):
        s=[lam[k]+mu[k] for k in range(4)]
        for _ in range(random.randint(0,12)):
            k=random.randint(0,2)
            if s[k]>s[k+1] and s[k]>0: s[k]-=1;s[k+1]+=1
            s=sorted(s,reverse=True)
        return s
    dim3=0; bad_bal=0; bad_mu=0; neg=0; nonint=0; minmu=None; checked=0
    for _ in range(ntest):
        lam=rp(maxpart);mu=rp(maxpart);nu=mk(lam,mu)
        if _partial(nu,4)!=_partial(lam,4)+_partial(mu,4): continue
        a0,a1,a2,a3,Ls=coeffs(lam,mu,nu)
        if Ls[1]==0 or a3<=0: continue  # need genuine dim-3
        b=hive_to_nb([t for t in lam],[t for t in mu],[t for t in nu])
        if b in (None,"BADNORMAL"):
            print("REP-FAIL",lam,mu,nu,b); continue
        try:
            Lam,verts=lambda_vec(NORMALS,b)
        except AssertionError as e:
            nonint+=1; continue
        dim3+=1; checked+=1
        # B.Lambda==0
        if any(sum(br[t]*Lam[t] for t in range(NP))!=0 for br in B):
            bad_bal+=1; print("BALANCE FAIL",lam,mu,nu)
        # Lambda.mu == a1
        val=sum(F(Lam[t])*MU[t] for t in range(NP))
        if val!=a1:
            bad_mu+=1; print("Lambda.mu != a1",lam,mu,nu,val,a1)
        if a1<0: neg+=1
        if minmu is None or a1<minmu: minmu=a1
    print(f"fresh_dim3_checked={checked} nonintegral_skipped={nonint}")
    print(f"balance_fails={bad_bal} lambda.mu!=a1_fails={bad_mu} negative_a1={neg} min_a1={minmu}")

if __name__=="__main__":
    main()
