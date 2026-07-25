"""AUDIT of G8 section 7: the (m,c) identity and the TERMINAL LEMMA.

(1) verify the five forms q1..q5 are monochromatic sets of genuine cuts of And(3);
(2) verify the reduced-coordinate identity SYMBOLICALLY with sympy (the target
    verified it only on 400 random rational points);
(3) attack the terminal lemma  q1q2q3q4q5 <= (sum a)^10 / 5^10  directly in the
    ORIGINAL a-coordinates (the target searched only the reduced (m,c) form),
    with SLSQP + many restarts, and exactly on rational tight points;
(4) attack max_x min_j q_j(x) the same way;
(5) recheck the three recorded failed AM-GM attacks.
"""
import sys, itertools
from fractions import Fraction
import numpy as np

Q = [((0, 7), (3, 4)), ((1, 2), (5, 6)), ((0, 1), (4, 5)), ((2, 3), (6, 7)),
     ((0, 4), (1, 5), (2, 6), (3, 7))]
WAG = [(i, (i + 1) % 8) for i in range(8)] + [(i, i + 4) for i in range(4)]
WAG = sorted(tuple(sorted(e)) for e in WAG)


def check_cuts():
    ok = True
    for j, pairs in enumerate(Q):
        target = sorted(tuple(sorted(e)) for e in pairs)
        found = None
        for mask in range(1 << 7):
            side = [0] + [(mask >> (v - 1)) & 1 for v in range(1, 8)]
            mono = sorted(e for e in WAG if side[e[0]] == side[e[1]])
            if mono == target:
                found = side
                break
        print(f"   q{j+1} mono={target}  cut={found}")
        ok &= found is not None
    return ok


def qvals(a):
    return [sum(a[u] * a[v] for (u, v) in pairs) for pairs in Q]


def symbolic_identity():
    import sympy as sp
    m = sp.symbols('m0 m1 m2 m3', nonnegative=True)
    c = sp.symbols('c0 c1 c2 c3')
    a = [None] * 8
    for i in range(4):
        a[i] = m[i] * (1 + c[i]) / 2
        a[i + 4] = m[i] * (1 - c[i]) / 2
    prod = sp.expand(sp.prod([sum(a[u] * a[v] for (u, v) in pairs) for pairs in Q]))
    P = (1 + c[0]*c[1]) * (1 + c[1]*c[2]) * (1 + c[2]*c[3]) * (1 - c[3]*c[0])
    S = sum(m[i]**2 * (1 - c[i]**2) for i in range(4))
    rhs = sp.expand((m[0]*m[1]*m[2]*m[3])**2 * P * S / 64)
    return sp.simplify(sp.expand(prod - rhs)) == 0


def numeric_max(fun, ntrial=4000, seed=20260725):
    from scipy.optimize import minimize
    rng = np.random.default_rng(seed)
    best = (-1.0, None)
    cons = [{'type': 'eq', 'fun': lambda z: float(np.sum(z) - 1.0)}]
    for t in range(ntrial):
        if t == 0:
            x0 = np.array([0.2, 0, 0, 0.2, 0.2, 0.2, 0.2, 0.0])
        elif t == 1:
            x0 = np.ones(8) / 8
        else:
            alp = rng.uniform(0.05, 2.0)
            x0 = rng.dirichlet(np.ones(8) * alp)
            if t % 3 == 0:                     # sparsify
                z = rng.integers(0, 2, 8)
                if z.sum() >= 4:
                    x0 = x0 * z
                    if x0.sum() > 0:
                        x0 = x0 / x0.sum()
        r = minimize(lambda z: -fun(np.clip(z, 0, None)), x0, method='SLSQP',
                     bounds=[(0, 1)] * 8, constraints=cons,
                     options={'maxiter': 400, 'ftol': 1e-16})
        x = np.clip(r.x, 0, None)
        s = x.sum()
        if s <= 0:
            continue
        x = x / s
        v = fun(x)
        if v > best[0]:
            best = (v, x.copy())
    return best


if __name__ == "__main__":
    print("(1) the five forms are cuts of And(3) = C8(1,4):")
    print("    all five realised as cuts:", check_cuts())
    print()

    print("(2) symbolic identity  q1q2q3q4q5 == (m0m1m2m3)^2 P(c) S / 64 :",
          symbolic_identity())
    print()

    print("(3) max of q1q2q3q4q5 over the simplex (a-coordinates, SLSQP):")
    f = lambda x: float(np.prod([sum(x[u] * x[v] for (u, v) in p) for p in Q]))
    v, x = numeric_max(f)
    tgt = 5.0 ** -10
    print(f"    max = {v:.12e}   5^-10 = {tgt:.12e}   ratio = {v/tgt:.10f}")
    print(f"    argmax = {np.round(x,6)}")
    print()

    print("(4) max of min_j q_j over the simplex:")
    g = lambda x: float(min(sum(x[u] * x[v] for (u, v) in p) for p in Q))
    v2, x2 = numeric_max(g, ntrial=3000)
    print(f"    max = {v2:.12f}   1/25 = 0.04   ratio = {v2/0.04:.10f}")
    print(f"    argmax = {np.round(x2,6)}")
    print()

    print("(5) exact rational check of the recorded tight points and failed splits:")
    # tight point (m,c) = ((2/5,1/5,1/5,1/5),(0,1,1,1)) -> a
    m = [Fraction(2, 5), Fraction(1, 5), Fraction(1, 5), Fraction(1, 5)]
    c = [Fraction(0), Fraction(1), Fraction(1), Fraction(1)]
    a = [None] * 8
    for i in range(4):
        a[i] = m[i] * (1 + c[i]) / 2
        a[i + 4] = m[i] * (1 - c[i]) / 2
    qs = qvals(a)
    print(f"    a = {[str(t) for t in a]}")
    print(f"    q = {[str(t) for t in qs]}   prod = {np.prod([float(t) for t in qs]):.6e}"
          f"   exact prod = { (qs[0]*qs[1]*qs[2]*qs[3]*qs[4]) }  5^-10 = {Fraction(1,5**10)}")
    print(f"    equality: {qs[0]*qs[1]*qs[2]*qs[3]*qs[4] == Fraction(1,5**10)}")
    # failed split witness c_i = sqrt(1/5)
    import sympy as sp
    cc = sp.sqrt(sp.Rational(1, 5))
    P = (1 + cc**2)**3 * (1 - cc**2)
    Ssum = 4 * (1 - cc**2)
    print(f"    P*Sum(1-c^2) at c_i=sqrt(1/5): {sp.nsimplify(P*Ssum)} = {float(P*Ssum):.6f}  (report: 4.424, needs <= 4)")
    # antipodal folding bound
    print(f"    antipodal folding bound 1/1048576 = {1/1048576:.6e} vs needed {tgt:.6e}"
          f"  ratio {1/1048576/tgt:.4f}")
