"""Direct theorem test: compute a_1 exactly on many r=4 hive polytopes and
verify a_1>=0 (equiv. V<=3(c+i)). Box [0,N]^3, N=|nu|, analytic x3 interval.
Cross-checks 6a_1 = 3(c+i)-V. Exact integer/Fraction arithmetic."""
import random, sys
from fractions import Fraction
from math import ceil, floor
from hive import constraints, _partial

def count(cons, N, interior=False):
    """#integer (x1,x2,x3) in [0,N]^3 with all a*x1+b*x2+c*x3 >= r
       (strict > for interior)."""
    total=0
    for x1 in range(0,N+1):
        for x2 in range(0,N+1):
            x3lo, x3hi = 0, N
            ok=True
            for (a,b,c,r) in cons:
                R = r - a*x1 - b*x2   # need c*x3 >= R  (or > R interior)
                if c==0:
                    if interior:
                        if 0 <= R: ok=False;break
                    else:
                        if 0 < R: ok=False;break
                    continue
                if c>0:
                    if interior:
                        x3lo=max(x3lo, floor(Fraction(R,c))+1)
                    else:
                        x3lo=max(x3lo, ceil(Fraction(R,c)))
                else:
                    if interior:
                        x3hi=min(x3hi, ceil(Fraction(R,c))-1)
                    else:
                        x3hi=min(x3hi, floor(Fraction(R,c)))
            if ok and x3hi>=x3lo:
                total += x3hi-x3lo+1
    return total

def L_at(lam,mu,nu,t):
    lam=[t*a for a in lam]; mu=[t*a for a in mu]; nu=[t*a for a in nu]
    N=_partial(nu,4)
    if N==0: return 1  # all-zero border: single point
    return count(constraints(lam,mu,nu), N)

def interior_count(lam,mu,nu):
    N=_partial(nu,4)
    if N==0: return 0
    return count(constraints(lam,mu,nu), N, interior=True)

def coeffs(lam,mu,nu):
    Ls=[L_at(lam,mu,nu,t) for t in range(4)]
    L0,L1,L2,L3=Ls
    a0=Fraction(L0)
    a1=Fraction(-11*L0+18*L1-9*L2+2*L3,6)
    a2=Fraction(2*L0-5*L1+4*L2-L3,2)
    a3=Fraction(-L0+3*L1-3*L2+L3,6)
    return a0,a1,a2,a3,Ls

def main():
    random.seed(777)
    ntest=int(sys.argv[1]) if len(sys.argv)>1 else 3000
    maxpart=int(sys.argv[2]) if len(sys.argv)>2 else 30
    dim3=0; neg=0; minA1=None; ident_fail=0; lowdim_neg=0
    minL1_witness=None
    def rand_part(mp):
        L=random.randint(1,4)
        p=sorted([random.randint(0,mp) for _ in range(L)],reverse=True)
        while p and p[-1]==0:p.pop()
        return p or [1]
    def make_nu(lam,mu,mp):
        s=[(lam[k] if k<len(lam) else 0)+(mu[k] if k<len(mu) else 0) for k in range(4)]
        for _ in range(random.randint(0,10)):
            k=random.randint(0,2)
            if s[k]>s[k+1] and s[k]>0:
                s[k]-=1;s[k+1]+=1
            s=sorted(s,reverse=True)
        while s and s[-1]==0:s.pop()
        return s or [1]
    tested=0
    for _ in range(ntest):
        lam=rand_part(maxpart);mu=rand_part(maxpart);nu=make_nu(lam,mu,maxpart)
        if _partial(nu,4)!=_partial(lam,4)+_partial(mu,4): continue
        a0,a1,a2,a3,Ls=coeffs(lam,mu,nu)
        if Ls[1]==0: continue
        tested+=1
        assert a0==1, (lam,mu,nu,Ls)  # Ehrhart L(0)=1
        # every coefficient nonneg is the full theorem; track a1 (and lower)
        for cf in (a1,a2,a3):
            if cf<0:
                neg+=1
                print("NEGATIVE coeff",lam,mu,nu,"a=",a0,a1,a2,a3)
                break
        if a3>0:  # genuine dim 3: cross-check identity
            dim3+=1
            c=Ls[1]; i=interior_count(lam,mu,nu); V=6*a3
            if 6*a1 != 3*(c+i)-V:
                ident_fail+=1
                print("IDENTITY FAIL",lam,mu,nu,6*a1,3*(c+i)-V)
        if minA1 is None or a1<minA1:
            minA1=a1; minL1_witness=(lam,mu,nu,str(a1))
    print(f"tested_nonempty={tested} dim3={dim3} negative_coeff={neg} identity_fail={ident_fail}")
    print(f"min_a1={minA1} at {minL1_witness}")

if __name__=="__main__":
    main()
