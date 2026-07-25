"""AUDIT part 4: (i) locate the falsifier with the largest ARCBOUND (P2 claims 'every witness has
ARCBOUND <= 1/32'); (ii) check that the R5-K9 Chebyshev term and harmonic mean really do fail on a
witness where they are WELL DEFINED (on the far-regular witnesses they are 0/0); (iii) 3-atom bound."""
import sys, os, functools
print = functools.partial(print, flush=True)
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_P2_core import Measure, gamma_measure

TARGET = F(1, 25)
here = os.path.dirname(os.path.abspath(__file__))

print("=" * 100)
print("(i) the falsifier with the LARGEST ARCBOUND in the 1790")
print("=" * 100)
best = None
for l in open(os.path.join(here, 'audit_sweep_falsifiers.txt')):
    r = l.split()
    m, q, w = int(r[0]), int(r[1]), [int(t) for t in r[2:]]
    mu = gamma_measure(m, w)
    ab = mu.arcbound()
    if best is None or ab > best[0]:
        best = (ab, m, q, w, mu.psi(), mu.A(), mu.min_m_supp())
ab, m, q, w, ps, A, mm = best
print(f"  Gamma_{m}, q={q}, w={w}")
print(f"  ARCBOUND = {ab} = {float(ab):.7f}   psi = {ps} = {float(ps):.7f}")
print(f"  1/32 = {F(1,32)} = {1/32:.7f}   1/25 = 0.04")
print(f"  => ARCBOUND {'>' if ab > F(1,32) else '<='} 1/32 ;  "
      f"{'<= 1/25 (arc-cut conjecture safe)' if ab <= TARGET else '*** EXCEEDS 1/25 ***'}")
print(f"  (its criterion value: A={A}={float(A):.7f}, min_b m(b)={mm}={float(mm):.7f})")

print()
print("=" * 100)
print("(ii) the R5-K9 companion forms on a witness where they are well defined")
print("     Chebyshev  E - Var_mu(m)/(max m - E)      harmonic  H = 1/E_mu[1/m]")
print("=" * 100)


def forms(mu, name):
    mvals = mu.m_formula()
    E = sum(mu.x[b] * mvals[b] for b in range(mu.n))
    V = sum(mu.x[b] * mvals[b] ** 2 for b in range(mu.n)) - E ** 2
    mx = max(mvals)
    cheb = None if mx == E else E - V / (mx - E)
    H = None if any(v == 0 for v in mvals) else 1 / sum(mu.x[b] / mvals[b] for b in range(mu.n))
    print(f"  {name}")
    print(f"     m values = {sorted(set(mvals))}   E = {E} = {float(E):.7f}   Var = {float(V):.3e}")
    print(f"     Chebyshev term = {'0/0 (m constant, undefined)' if cheb is None else f'{cheb} = {float(cheb):.7f}'}"
          + ("" if cheb is None else f"  {'> 1/25 -> FAILS' if cheb > TARGET else '<= 1/25 -> closes'}"))
    print(f"     harmonic mean  = {'undefined' if H is None else f'{H} = {float(H):.7f}'}"
          + ("" if H is None else f"  {'> 1/25 -> FAILS' if H > TARGET else '<= 1/25 -> closes'}"))
    print(f"     A = {mu.A()} = {float(mu.A()):.7f}  {'> 1/25 -> FAILS' if mu.A() > TARGET else '<= 1/25'}")


forms(Measure(1800000, [0, 9, 600006, 1200003], [169, 239, 169, 239]),
      "4-atom optimal (169,239,169,239): m takes TWO values, so both forms are well defined")
forms(gamma_measure(14, [1 if i in (0, 3, 4, 7, 8, 9, 12, 13) else 0 for i in range(14)]),
      "Wagner on Gamma_14 (far-regular: m constant)")
forms(gamma_measure(11, [3, 0, 1, 3, 0, 1, 3, 3, 0, 1, 3]), "Gamma_11 (3,0,1,3,0,1,3,3,0,1,3)")

print()
print("=" * 100)
print("(iii) P2 section 4 'four atoms is the exact minimum': the 3-atom bound")
print("=" * 100)
print("  path a-b-c : bound_0 = W - int g^2 = x_b(x_a+x_c)[1 - x_b - (x_a+x_c)] = 0")
print("  edge+isolated: bound_0 = x_a x_b x_c <= 1/27 = %.7f < 1/25" % (1 / 27))
worst = F(0)
N = 60
for i in range(1, N):
    for j in range(1, N - i):
        k = N - i - j
        if k <= 0:
            continue
        v = F(i, N) * F(j, N) * F(k, N)
        worst = max(worst, v)
print(f"  numeric max of x_a x_b x_c over a 1/{N} grid = {worst} = {float(worst):.7f}  (1/27 = {1/27:.7f})")
print("  => no 3-atom measure can be an item-7 falsifier.  CONFIRMED.")
