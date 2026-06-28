"""Is SPEC (rho(K)=sum_i P_i <= N) universal on odd-cycle blow-ups, or does it also fail where Gamma<=N^2 holds?
   This decides the target: SPEC (rho(K)<=N) vs Gamma<=N^2 directly. Quotient exact, large N."""
import random
from fractions import Fraction as F

def spec(m, n):
    N=sum(n)
    prods=[(n[i]*n[(i+1)%m],i) for i in range(m)]; pmin,a=min(prods); b=(a+1)%m; nbad=n[a]*n[b]
    def Pi(i):
        if i==a: return F(n[b])
        if i==b: return F(n[a])
        return F(nbad,n[i])
    rhoK=sum(Pi(i) for i in range(m))
    Gamma=m*m*nbad
    return rhoK, F(N), Gamma, F(N)*F(N)

if __name__=="__main__":
    print("=== SPEC (rho(K)=sum Pi <= N) on large odd-cycle blow-ups ===",flush=True)
    rng=random.Random(7777)
    for m in (5,7,9,11,13):
        spec_fail=0; gam_fail=0; tot=0; spec_fail_gam_ok=0; worst=None
        for _ in range(120000):
            n=[rng.choice([1,2,3,5,7,12,30,100,300,700,1500]) for _ in range(m)]
            if sum(n)>4000 or sum(n)<m: continue
            rhoK,N,Gamma,N2=spec(m,n)
            tot+=1
            sfail = rhoK>N; gfail = Gamma>N2
            if sfail:
                spec_fail+=1
                r=rhoK/N
                if worst is None or r>worst: worst=r
            if gfail: gam_fail+=1
            if sfail and not gfail: spec_fail_gam_ok+=1
        ws=f" worst rho/N={float(worst):.4f}" if worst is not None else ""
        print(f"  C{m}: tested={tot} SPEC-FAILS(rho>N)={spec_fail}{ws} Gamma>N^2 fails={gam_fail} (SPEC-fail-but-Gamma-ok={spec_fail_gam_ok})",flush=True)
