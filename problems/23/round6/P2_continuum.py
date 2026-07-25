"""P2 / round 6 - the CLEAN falsifier: a 1/3-periodic absolutely continuous measure.

mu_eta = three uniform arcs  [0,eta], [1/3, 1/3+eta], [2/3, 2/3+eta], mass 1/3 on each
         (equivalently: any 1/3-periodic a.c. probability measure of "width" eta).

Everything below is computed symbolically in eta with sympy (exact rational function of eta), for
0 < eta <= 1/6 (so that every cross-cluster distance stays <= 1/2 and the elementary distance
formula d = 1/3 + (b-a) is valid).

RESULTS (proved here):

    g(x)      = 1/3   for EVERY x on the circle          (in particular Var_mu(g) = 0)
    W         = 1/6                                       (independent of eta!)
    T         = (1+eta)/18
    A = W-2T  = (1-2eta)/18
    m(b)      = 1/18  for every b                         (so every bound_k = 1/18)
    CRIT      = min(A, 1/18) = (1-2eta)/18  >  1/25   <=>   eta < 7/50
    ARCBOUND  <= 1/36  (exhibited arc: one whole cluster plus half of the next)

So every eta in (0, 7/50) gives a criterion falsifier, with CRIT -> 1/18 = 2.5/25 as eta -> 0.

Run:  python P2_continuum.py
"""
import sympy as sp

eta, a, b, s = sp.symbols('eta a b s', positive=True)
rho = sp.Rational(1, 3) / eta          # density inside each arc (mass 1/3 spread over length eta)
TARGET = sp.Rational(1, 25)

print("=" * 96)
print("mu_eta = three uniform arcs of length eta at 0, 1/3, 2/3, mass 1/3 each  (0 < eta <= 1/6)")
print("=" * 96)

# ---- adjacency inside the family: (cluster j, offset a) ~ (cluster j+1, offset b)  iff  b > a,
#      and then d = 1/3 + (b - a) <= 1/3 + eta <= 1/2.  Three ordered cluster pairs (0,1),(1,2),(2,0).
print("\n[1] far-mass g is constant:")
g_of_a = sp.simplify(rho * sp.integrate(1, (b, a, eta)) + rho * sp.integrate(1, (b, 0, a)))
print(f"    g(cluster j, offset a) = mu({{b in cluster j+1 : b > a}}) + mu({{c in cluster j-1 : c < a}})"
      f" = {sp.simplify(g_of_a)}")
assert sp.simplify(g_of_a - sp.Rational(1, 3)) == 0

print("\n[2] adjacent mass W and mean distance T:")
W = sp.simplify(3 * sp.integrate(sp.integrate(rho ** 2, (b, a, eta)), (a, 0, eta)))
T = sp.simplify(3 * sp.integrate(sp.integrate((sp.Rational(1, 3) + b - a) * rho ** 2, (b, a, eta)),
                                 (a, 0, eta)))
A = sp.simplify(W - 2 * T)
print(f"    W = {W}          T = {T}          T/W = {sp.simplify(T/W)}")
print(f"    A = W - 2T = {A}")
assert sp.simplify(W - sp.Rational(1, 6)) == 0
assert sp.simplify(T - (1 + eta) / 18) == 0
assert sp.simplify(A - (1 - 2 * eta) / 18) == 0

print("\n[3] neighbourhood cuts:  m(b) = W - int_{N(b)} g dmu = W - (1/3)*g(b)")
m_b = sp.simplify(W - sp.Rational(1, 3) * sp.Rational(1, 3))
print(f"    m(b) = {m_b} = 1/18 for every b   ==>   bound_k = 1/18 for every k >= 0")
assert m_b == sp.Rational(1, 18)

print("\n[4] the criterion value:")
CRIT = sp.simplify(sp.Min(A, m_b))
print(f"    CRIT(mu_eta) = min(A, bound_k) = {A}      (A <= 1/18 always)")
thr = sp.solve(sp.Eq(A, TARGET), eta)[0]
print(f"    CRIT > 1/25  <=>  eta < {thr} = {float(thr):.6f}")
assert thr == sp.Rational(7, 50)
for e in (sp.Rational(1, 100), sp.Rational(1, 20), sp.Rational(1, 10), sp.Rational(1, 8)):
    v = A.subs(eta, e)
    print(f"      eta = {e}:  CRIT = {v} = {float(v):.7f}   ratio to 1/25 = {float(v * 25):.4f}"
          f"   {'FALSIFIER' if v > TARGET else 'closed'}")

print("\n[5] the truth: an explicit arc cut whose value is 1/36 < 1/25")
# side = whole cluster 0 + the fraction [0, s*eta] of cluster 1.
# inside the side:  pairs (cluster0 offset a) - (cluster1 offset b) with a < b <= s*eta
inside = sp.integrate(sp.integrate(rho ** 2, (b, a, s * eta)), (a, 0, s * eta))
# inside the complement: pairs (cluster1 offset b > s*eta) - (cluster2 offset c > b)
outside = sp.integrate(sp.integrate(rho ** 2, (b, a, eta)), (a, s * eta, eta))
arcval = sp.simplify(inside + outside)
print(f"    value(s) = {sp.factor(arcval)}   (s = fraction of cluster 1 kept)")
best = sp.simplify(arcval.subs(s, sp.Rational(1, 2)))
print(f"    at s = 1/2:  {best} = {float(best):.7f}  <  1/25   ==>  ARCBOUND <= 1/36, "
      f"psi <= 1/36: NOT a counterexample to the arc-cut conjecture, NOT to Erdos 23")
assert best == sp.Rational(1, 36)
crit_pt = sp.solve(sp.diff(arcval, s), s)
print(f"    (stationary point of the arc family: s = {crit_pt})")

print("\n[6] why item 6 does not stop this:")
print("    mu_eta IS a purely 3-fold (1/3-periodic) measure, and its g IS constant - but it has")
print("    adjacent mass W = 1/6 > 0.  The claim 'a purely 3-fold measure has no adjacent pairs'")
print("    is true only for the 3-ATOM measure on a coset {a, a+1/3, a+2/3}: for that measure the")
print("    pairs sit at distance EXACTLY 1/3, which is not > 1/3.  Spreading each atom over an arc")
print("    of length eta makes half of those pairs strictly farther than 1/3 and creates W = 1/6.")
print("    Fourier check of A on the 1/3-periodic family (psihat(0) = 1/36, psihat(3k) = "
      "1/(9 pi^2 (2j+1)^2) for 3k = 3(2j+1), 0 for 6 | n):")
j = sp.symbols('j', integer=True, nonnegative=True)
# psihat(3k) = 0 for even k;  for 3k = 3(2j+1):  -(-1)^{3k} * (cos(pi k) - 1)/(2 pi^2 9 k^2)
#            = 1/(9 pi^2 (2j+1)^2)
tail = sp.summation(1 / (9 * sp.pi ** 2 * (2 * j + 1) ** 2), (j, 0, sp.oo))
A_fourier = sp.simplify(sp.Rational(1, 36) + 2 * tail)
print(f"      sum_{{k>=1}} psihat(3k) = {sp.simplify(tail)} = 1/72")
print(f"      A(eta -> 0) = psihat(0) + 2*sum_k psihat(3k) = 1/36 + 2*(1/72) = {A_fourier} "
      f"= {float(A_fourier):.8f}   (independent third derivation of 1/18)")
assert tail == sp.Rational(1, 72) and A_fourier == sp.Rational(1, 18)

print("\n[7] the universal ceiling:")
print("    T > W/3 (every adjacent pair has d > 1/3)  ==>  A = W - 2T < W/3")
print("    Cauchy-Schwarz                              ==>  bound_0 = W - 4W^2 - Var(g) <= W - 4W^2")
print("    so CRIT < min(W/3, W - 4W^2) <= 1/18, with equality of the two branches at W = 1/6.")
Wv = sp.symbols('W', positive=True)
sol = sp.solve(sp.Eq(Wv / 3, Wv - 4 * Wv ** 2), Wv)
print(f"    the two branches cross at W = {sol} and the common value is "
      f"{sp.simplify((Wv/3).subs(Wv, sol[-1]))} = 1/18 = {1/18:.7f} = {25/18:.4f} x (1/25)")
assert sol[-1] == sp.Rational(1, 6)
print("\nALL SYMBOLIC CHECKS PASSED.")
