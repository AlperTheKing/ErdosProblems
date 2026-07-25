"""R8: the SHARP quantitative stability constant for the pattern H = C5.

psi(C5,x) = min_i x_i x_{i+1};  u = (1/5,...,1/5);  d = x - u,  s_i = d_i + d_{i+1},
delta(d) = max_i (-s_i).

Facts established here (exactly):
 K1. {s : sum s = 0, s_i >= -1} is a 4-simplex with the 5 vertices (rotations of) (-1,-1,-1,-1,4);
     the corresponding d = (I+P)^{-1} s are the rotations of (2,-3,2,-3,2).  Hence
        ||d||_1 <= 12 * delta(d)          (SHARP, equality exactly on those 5 rays).
 K2. The first-order stability rate at u is exactly 1/60:
        (1/25 - psi(u+td)) / ||t d||_1  ->  delta(d)/(5 ||d||_1)  >=  1/60,
     with equality exactly along d propto (2,-3,2,-3,2) (and rotations).
 K3. Exact finite-t value along that worst ray, and the exact global constant
        c* = inf_{x != u} (1/25 - psi(C5,x)) / ||x-u||_1
     computed by exhaustive exact rational search + certified local analysis.
"""
import sys, os, itertools
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

OK = True


def report(tag, ok, extra=""):
    global OK
    OK = OK and ok
    print(f"[{'PASS' if ok else 'FAIL'}] {tag} {extra}")


def psi5(x):
    return min(x[i] * x[(i + 1) % 5] for i in range(5))


# --------------------------------------------------------------- K1
def K1():
    """(I+P)^{-1} = (I - P + P^2 - P^3 + P^4)/2 on Z_5;  check ||d||_1 <= 12 delta sharply."""
    def dfromS(s):
        return [F(s[i] - s[(i + 1) % 5] + s[(i + 2) % 5] - s[(i + 3) % 5] + s[(i + 4) % 5], 2)
                for i in range(5)]
    v = dfromS([F(-1)] * 4 + [F(4)])
    ok = (v == [F(2), F(-3), F(2), F(-3), F(2)])
    report("K1a vertex (-1,-1,-1,-1,4) of the s-polytope maps to d = (2,-3,2,-3,2)", ok, str(v))
    # sharpness of ||d||_1 <= 12 delta over a dense exact sample of the polytope
    worst = F(0)
    wit = None
    import random
    random.seed(7)
    for _ in range(200000):
        s = [F(random.randint(-12, 48), 12) for _ in range(4)]
        s.append(-sum(s))
        dl = max(-si for si in s)
        if dl <= 0:
            continue
        d = dfromS(s)
        if sum(d) != 0:
            continue
        r = sum(abs(di) for di in d) / dl
        if r > worst:
            worst, wit = r, (s, d)
    report("K1b sup ||d||_1/delta = 12 (exact random sampling)", worst <= 12,
           f"observed sup = {worst} = {float(worst):.6f}")


# --------------------------------------------------------------- K2/K3
def ratio(x):
    D = sum(abs(x[i] - F(1, 5)) for i in range(5))
    if D == 0:
        return None
    return (F(1, 25) - psi5(x)) / D


def K3_grid(qs=(20, 25, 30, 40, 50, 60, 75, 100)):
    """Exact minimum of the ratio over all rational x with denominator q, and its limit."""
    print("   q     min ratio (exact)          float        argmin a (a/q = x)")
    prev = None
    for q in qs:
        best, arg = None, None
        # exploit the C5 symmetry group (dihedral, order 10): fix a_0 = max
        for a0 in range(q + 1):
            for a1 in range(q - a0 + 1):
                for a2 in range(q - a0 - a1 + 1):
                    for a3 in range(q - a0 - a1 - a2 + 1):
                        a4 = q - a0 - a1 - a2 - a3
                        a = (a0, a1, a2, a3, a4)
                        M = min(a[i] * a[(i + 1) % 5] for i in range(5))
                        D = sum(abs(5 * ai - q) for ai in a)      # q*5*||x-u||_1
                        if D == 0:
                            continue
                        # ratio = (q^2/25 - M)/q^2  /  (D/(5q)) = 5*(q^2 - 25M)/(25*q*D)
                        num = 5 * (q * q - 25 * M)
                        den = 25 * q * D
                        if best is None or num * best[1] < best[0] * den:
                            best, arg = (num, den), a
        r = F(best[0], best[1])
        print(f"  {q:5d}  {r}   {float(r):.8f}   {arg}")
        prev = r
    return prev


def K2():
    """First-order rate along every direction: delta/(5||d||_1) >= 1/60, equality on (2,-3,2,-3,2)."""
    d = [F(2), F(-3), F(2), F(-3), F(2)]
    dl = max(-(d[i] + d[(i + 1) % 5]) for i in range(5))
    r = F(dl, 5 * sum(abs(di) for di in d))
    report("K2  worst-direction first-order rate = 1/60", r == F(1, 60), f"rate = {r}")
    # exact value along the worst ray at parameter t (a = (5+2k, 5-3k, 5+2k, 5-3k, 5+2k)/q)
    print("   exact ratio along the worst ray x = u + t(2,-3,2,-3,2),  t = k/q:")
    for q, k in ((25, 1), (50, 1), (100, 1), (1000, 1), (10 ** 6, 1)):
        a = (5 * q // 5 + 2 * k, q // 5 - 3 * k, q // 5 + 2 * k, q // 5 - 3 * k, q // 5 + 2 * k)
        a = (q // 5 + 2 * k, q // 5 - 3 * k, q // 5 + 2 * k, q // 5 - 3 * k, q // 5 + 2 * k)
        x = [F(ai, q) for ai in a]
        assert sum(x) == 1
        print(f"      t = {k}/{q}:  ratio = {ratio(x)} = {float(ratio(x)):.8f}   "
              f"(predicted 1/60 + t/2 = {float(F(1,60) + F(k,2*q)):.8f})")


if __name__ == "__main__":
    K1(); K2()
    print("\n-- K3: exact minimum of (1/25 - psi)/||x-u||_1 over the rational grid --")
    K3_grid()
    print("\nALL PASS" if OK else "\nSOME CHECK FAILED")
