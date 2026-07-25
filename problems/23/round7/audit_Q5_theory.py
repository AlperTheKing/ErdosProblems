"""A1/A2/A3/A9/A12: the algebra of Theorems A and B, the round5 witness regression,
C5[n] tightness, and the And(4) -> And(k) induced-subgraph scope claim.

All symbolic (sympy) or exact rational.  Nothing here uses floating point.
"""
from fractions import Fraction as F
from itertools import combinations
import sys
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round7")
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round5")
import sympy as sp
from audit_Q5_lib import (E_of, bip, psi, emass, tau_star_exact, andrasfai, C5n,
                          induced, all_cycles, tri_free)

FAIL = []


def chk(name, got, want=True):
    good = (got == want)
    if not good:
        FAIL.append((name, got, want))
    print(f"  {'OK  ' if good else 'FAIL'} {name}: {got}" + ("" if good else f" (want {want})"))


# ------------------------------------------------------------------ Theorem A
print("=== A1  Theorem A: the algebra, symbolically ===")
e, s, eta = sp.symbols('e s eta', real=True)
chk("4e^2 - e + 1/25 == 4(e-1/20)(e-1/5)",
    sp.simplify(4 * e**2 - e + sp.Rational(1, 25) - 4 * (e - sp.Rational(1, 20)) * (e - sp.Rational(1, 5))) == 0)
chk("e - 4e^2 at e=1/5 equals 1/25",
    sp.Rational(1, 5) - 4 * sp.Rational(1, 5)**2 == sp.Rational(1, 25))
chk("e/5 at e=1/5 equals 1/25", sp.Rational(1, 5) / 5 == sp.Rational(1, 25))
# max over e of min(e/5, e-4e^2): the two branches cross at e=1/5 and 1/20
crit = sp.solve(sp.Eq(e / 5, e - 4 * e**2), e)
chk("e/5 = e-4e^2 exactly at e in {0, 1/5}", sorted(crit) == [0, sp.Rational(1, 5)])
mx = sp.Rational(0)
for cand in [sp.Rational(1, 5), sp.Rational(1, 8), sp.Rational(1, 4), sp.Rational(1, 20)]:
    mx = max(mx, min(cand / 5, cand - 4 * cand**2))
chk("max_e min(e/5, e-4e^2) attained at e=1/5 with value 1/25", mx == sp.Rational(1, 25))
print("  NOTE the case split is exactly accepted base 5 in weighted form:")
print("       e > 1/5  =>  psi <= e-4e^2 < 1/25  (the conjecture is TRUE at such x);")
print("       e <= 1/5 =>  Lambda <= e/5 <= 1/25 (uniform cover z=1/5, odd girth >= 5).")

print("=== A2  Theorem B: the quantitative form, symbolically ===")
lhs = sp.expand((sp.Rational(1, 5) - s) - 4 * (sp.Rational(1, 5) - s)**2)
chk("e-4e^2 = 1/25 + (3/5)s - 4s^2 with s = 1/5-e",
    sp.simplify(lhs - (sp.Rational(1, 25) + sp.Rational(3, 5) * s - 4 * s**2)) == 0)
print("  (3/5)s - 4s^2 >= eta with s>0  =>  (3/5)s >= eta + 4s^2 >= eta  =>  s >= 5eta/3   [valid]")
print("  Lambda <= e/5 = (1/5-s)/5 = 1/25 - s/5 <= 1/25 - eta/3                        [valid]")
print("  psi - Lambda >= (1/25+eta) - (1/25-eta/3) = 4eta/3                            [valid]")
chk("psi-Lambda bound arithmetic",
    sp.simplify((sp.Rational(1, 25) + eta) - (sp.Rational(1, 25) - eta / 3) - sp.Rational(4, 3) * eta) == 0)

# ------------------------------------------------- the missing half of "exactly when"
print("=== A3  Theorem C's 'exactly when G has an induced C5' -- the converse ===")
print("  Q5.md proves only '>= 1/25 if there is an induced C5' (the plateau).")
print("  The converse is NOT proved in Q5.md.  It is however true and one line:")
print("  odd girth >= 7 => z = 1/7 is feasible => Lambda <= e/7 <= (1/4)/7 = 1/28 < 1/25")
print("  (e <= 1/4 on triangle-free graphs by Motzkin-Straus, omega = 2).")
for k in (7, 9, 11):
    n = k
    A = [0] * n
    for i in range(n):
        A[i] |= 1 << ((i + 1) % n)
        A[(i + 1) % n] |= 1 << i
    x = [F(1, n)] * n
    print(f"    C{k}: e={emass(n,A,x)} psi={psi(n,A,x)} <= 1/28 ? "
          f"{psi(n,A,x) <= F(1,28)}")

# ------------------------------------------------------------ A12 regression
print("\n=== A12  round5 witness regression (10 witnesses) ===")
from claude_witness_regression import WITNESSES, gamma, arcbound, mono


def build(m):
    A = [0] * m
    for u in range(m):
        for v in range(u + 1, m):
            if 3 * min((u - v) % m, (v - u) % m) > m:
                A[u] |= 1 << v
                A[v] |= 1 << u
    return m, A


print(f"{'witness':28s} {'m':>3s} {'|supp|':>6s} {'e':>10s} {'psi':>12s} {'e-4e^2':>12s} "
      f"{'Lambda':>10s} {'ARCBOUND':>10s}")
for wname, m, w, why in WITNESSES:
    n, A = build(m)
    q = sum(w)
    x = [F(wi, q) for wi in w]
    supp = [i for i in range(m) if w[i]]
    ns, As = induced(n, A, supp)
    xs = [x[i] for i in supp]
    e_ = emass(ns, As, xs)
    ps = psi(ns, As, xs)
    ab = arcbound(m, gamma(m), x)
    lam = None
    if ns <= 10:
        lam = tau_star_exact(ns, As, w={ed: xs[ed[0]] * xs[ed[1]] for ed in E_of(ns, As)})[0]
    print(f"{wname:28s} {m:3d} {len(supp):6d} {str(e_):>10s} {str(ps):>12s} "
          f"{str(e_-4*e_*e_):>12s} {str(lam) if lam is not None else '   (skip)':>10s} {str(ab):>10s}")
    chk(f"  {wname}: psi <= 1/25", ps <= F(1, 25))
    chk(f"  {wname}: psi <= e-4e^2 (Thm A step 2)", ps <= e_ - 4 * e_ * e_)
    chk(f"  {wname}: psi <= ARCBOUND (sanity: arc cuts are cuts)", ps <= ab)
    if lam is not None:
        chk(f"  {wname}: Lambda <= psi", lam <= ps)
        chk(f"  {wname}: Lambda <= 1/25 (Thm A)", lam <= F(1, 25))
        chk(f"  {wname}: Lambda <= e/5", lam <= e_ / 5)

print("\n=== A12b  EXACT tightness on C5[n] (a bound that is not tight here is wrong) ===")
for k in (1, 2, 3):
    n, A = C5n(k)
    x = [F(1, n)] * n
    e_ = emass(n, A, x)
    ps = psi(n, A, x)
    lam = tau_star_exact(n, A, w={ed: x[ed[0]] * x[ed[1]] for ed in E_of(n, A)})[0]
    chk(f"C5[{k}]: e = 1/5", e_ == F(1, 5))
    chk(f"C5[{k}]: psi = 1/25 EXACTLY", ps == F(1, 25))
    chk(f"C5[{k}]: Lambda = 1/25 EXACTLY (relaxation tight)", lam == F(1, 25))
    chk(f"C5[{k}]: e-4e^2 = 1/25 EXACTLY (Thm A step 2 tight)", e_ - 4 * e_ * e_ == F(1, 25))
    chk(f"C5[{k}]: e/5 = 1/25 EXACTLY (uniform cover tight)", e_ / 5 == F(1, 25))

print("\n=== A12c  Prop 6 closed form on C5[n]: cover z=1/5 and packing y=n^-3 ===")
for k in (1, 2, 3, 4):
    n, A = C5n(k)
    E = E_of(n, A)
    chk(f"C5[{k}]: |E| = 5n^2", len(E) == 5 * k * k)
    # packing on all n^5 transversal 5-cycles with y = n^-3: load per edge
    # = (# transversal 5-cycles through e) * n^-3 = n^3 * n^-3 = 1
    cnt = {ed: 0 for ed in E}
    from itertools import product as iproduct
    for tup in iproduct(range(k), repeat=5):
        vs = [p * k + tup[p] for p in range(5)]
        for p in range(5):
            u, v = vs[p], vs[(p + 1) % 5]
            cnt[(min(u, v), max(u, v))] += 1
    chk(f"C5[{k}]: every edge is in exactly n^3 = {k**3} transversal 5-cycles",
        set(cnt.values()) == {k ** 3})
    chk(f"C5[{k}]: packing value n^5*n^-3 = n^2", F(k ** 5, k ** 3) == k * k)

# ------------------------------------------------------------------ A9 scope
print("\n=== A9  'And(4) is an induced subgraph of And(k)' -- Q5.md verifies k=5,6,7,8 only ===")
n4, A4 = andrasfai(4)
allok = True
for k in range(5, 61):
    n, A = andrasfai(k)
    S = list(range(0, 4)) + list(range(k, k + 4)) + [2 * k, 2 * k + 1, 2 * k + 2]
    m, B = induced(n, A, S)
    same = (m == n4 and all(B[i] == A4[i] for i in range(m)))
    if not same:
        allok = False
        print(f"    k={k}: NOT the claimed induced copy")
chk("claimed image is an induced And(4) for every k in 5..60 (I checked to 60, "
    "Q5.md only to 8)", allok)
print("  GENERAL PROOF (supplied by the auditor, absent from Q5.md):")
print("   place the three arcs {0..3},{k..k+3},{2k..2k+2} and send the j-th element in")
print("   cyclic order to j in Z_11.  A vertex is a*k+p (a=0,1,2; p the offset) and its")
print("   image is a*4+p.  For u=ak+p, v=bk+q with b-a in {0,1,2} and |q-p| <= 3:")
print("     b-a=0: index difference q-p in (-4,4) -> non-adjacent in Gamma_11, and")
print("            q-p in (-k,k) -> non-adjacent in Gamma_{3k-1};")
print("     b-a=1: adjacency in both is exactly 'q >= p' (4+(q-p) in [4,7] resp.")
print("            k+(q-p) in [k,2k-1], using 3 <= k-1);")
print("     b-a=2: adjacency in both is exactly 'q < p'.")
print("   So the induced copy exists for EVERY k >= 5, hence every And(k), k >= 4, has")
print("   the odd-K5 minor.  The statement is true; Q5.md's stated evidence (k<=8) is not")
print("   sufficient for it.")

print("\nFAILURES:", len(FAIL))
for f in FAIL:
    print("   ", f)
