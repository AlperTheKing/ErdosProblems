"""R9: the gap a counterexample would have to have.

Theorem A (accepted base, weighted form) gives, with e = sum_{uv in E} x_u x_v ,
        Lambda(H,x) <= min( e/5 , e - 4e^2 )        (both branches meet at e = 1/5, value 1/25)
Since psi = gap * Lambda, ANY (H,x) with psi > 1/25 must satisfy
        gap  >  (1/25) / min(e/5, e-4e^2)  =  max( 1/(5e) , 1/(25 e (1-4e)) ).
This is a NECESSARY condition on a counterexample, not an equivalent of the conjecture: it
uses only the proved upper bound on Lambda.  It says a counterexample that is not at the
extremal edge density e = 1/5 must have a LARGE odd-cycle integrality gap -- and the largest
gap exhibited anywhere in this round at odd girth 5 is 35/22 = 1.5909 (Higman-Sims).
"""
from fractions import Fraction as F
import R9_oddk5_srg as S
from R9_oddk5_lib import *

def edens(g, x):
    return sum(x[a]*x[b] for (a,b) in g.E)

print("required gap for a counterexample, as a function of the weighted edge density e:")
print(f"{'e':>10} {'Lambda <=':>14} {'gap must exceed':>18}")
for num, den in [(1,20),(1,12),(1,10),(1,8),(1,6),(3,20),(9,50),(1,5),(11,50),(1,4),(3,10)]:
    e = F(num,den)
    bound = min(e/5, e-4*e*e)
    if bound <= 0:
        print(f"{str(e):>10} {str(bound):>14} {'no counterexample possible at this density':>18}")
    else:
        print(f"{str(e):>10} {str(bound):>14} {str(F(1,25)/bound):>18} = {float(F(1,25)/bound):.4f}")

print()
print("where the exact witnesses of this round actually sit (uniform x):")
rows = [("C5", Cn(5), 1), ("Petersen", S.petersen(), 3), ("Clebsch", S.clebsch(), 8),
        ("Hoffman-Singleton", S.hoffman_singleton(), 50), ("Gewirtz", S.gewirtz(), 84),
        ("Higman-Sims", S.higman_sims(), 350)]
print(f"{'graph':>18} {'N':>5} {'e':>12} {'psi':>12} {'Lambda':>12} {'gap':>10} {'needed if CE':>14}")
for nm, g, b in rows:
    N = g.n
    x = [F(1,N)]*N
    e = edens(g, x)
    ps = F(b, N*N)
    lam = F(g.m, 5*N*N)
    bd = min(e/5, e-4*e*e)
    need = F(1,25)/bd if bd > 0 else None
    print(f"{nm:>18} {N:>5} {str(e):>12} {str(ps):>12} {str(lam):>12} {str(ps/lam):>10} {(f'{float(need):.4f}' if need else 'impossible'):>14}")
    assert lam <= min(e/5, e-4*e*e), "Theorem A violated!"
    assert ps <= F(1,25), "conjecture violated!"
print()
print("Theorem A holds on every row (asserted exactly); no row is a counterexample.")

print()
print("=" * 78)
print("STRONGER: accepted base gives psi <= e - 4e^2 directly (not only Lambda).")
print("4e^2 - e + 1/25 = 4(e-1/20)(e-1/5), so psi > 1/25 FORCES e in (1/20, 1/5).")
print("On that interval Lambda <= e/5 < 1/25, so the gap must exceed 1/(5e) in (1,4).")
print("=" * 78)
print(f"{'e':>8} {'psi <= e-4e^2':>16} {'Lambda <= e/5':>14} {'gap must exceed 1/(5e)':>24}")
for num, den in [(1,20),(3,50),(1,15),(1,12),(1,10),(1,8),(1,6),(9,50),(19,100),(1,5)]:
    e = F(num,den)
    print(f"{str(e):>8} {str(e-4*e*e):>16} {str(e/5):>14} {str(F(1,5)/e):>24} = {float(F(1,5)/e):.4f}")
print()
print("check psi <= e-4e^2 on the round's witnesses:")
for nm, g, b in rows:
    N = g.n; x=[F(1,N)]*N; e = edens(g,x); ps = F(b,N*N)
    print(f"  {nm:>18}  e={str(e):>8}  psi={str(ps):>10}  e-4e^2={str(e-4*e*e):>12}  "
          f"{'OK' if ps <= e-4*e*e else '*** VIOLATION ***'}  "
          f"{'e in (1/20,1/5)' if F(1,20)<e<F(1,5) else 'e outside (1/20,1/5)'}")
