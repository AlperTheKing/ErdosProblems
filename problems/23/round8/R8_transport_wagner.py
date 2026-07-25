"""Does the multiplicative transport certificate actually PROVE max_x psi <= 1/25
for a graph that is NOT C5-colourable?   Test case: Wagner = And(3) (chi_c = 8/3 > 5/2).

Its 5 C5-perfect cuts are
    A_j = {j,j+1,j+2,j+3}   (j = 0..3)     mono(A_j) = { (j,j+3), (j+4,j+7) }
    ALT = {0,2,4,6}                        mono(ALT) = the four diameters (i,i+4)

Step 1 (weights are forced).  Restricted to the support of the induced 5-cycle
(0,3,6,1,4) the five quadratics become exactly the five edge-products of that C5,
so  max_x prod nu^lambda = exp(-2H(p)),  p = (half the incidence vector of lambda),
which is <= 1/25 iff p is uniform iff lambda is uniform on the five cuts.

Step 2 (verify the resulting certificate) by mirror ascent from many random starts
+ exact rational evaluation at the best point found.
"""
import sys
from fractions import Fraction
import numpy as np

sys.path.insert(0, ".")
from R8_transport_lib import *   # noqa
from R8_transport_geomval import perfect_cuts   # noqa


def certificate_max(G, cuts, lam, tries=3000, iters=600, seed=7):
    n, k = G.n, len(cuts)
    lam = np.array(lam, dtype=float)
    M = []
    for S in cuts:
        A = np.zeros((n, n))
        for u, v in G.edges:
            if ((S >> u) & 1) == ((S >> v) & 1):
                A[u, v] = A[v, u] = 0.5
        M.append(A)

    def logF(x):
        t = 0.0
        for w, A in zip(lam, M):
            q = x @ A @ x
            if q <= 1e-300:
                return -1e18
            t += w * np.log(q)
        return t

    rng = np.random.default_rng(seed)
    best, bx = -1e18, None
    for _ in range(tries):
        x = rng.random(n) ** rng.choice([0.25, 1.0, 4.0])
        x = x * (rng.random(n) > 0.25)
        if x.sum() == 0:
            continue
        x /= x.sum()
        cur, step = logF(x), 0.5
        for _ in range(iters):
            g = np.zeros(n)
            ok = True
            for w, A in zip(lam, M):
                q = x @ A @ x
                if q <= 1e-300:
                    ok = False
                    break
                g += w * 2 * (A @ x) / q
            if not ok:
                break
            y = x * np.exp(step * g)
            y /= y.sum()
            v = logF(y)
            if v > cur:
                cur, x = v, y
            else:
                step *= 0.6
                if step < 1e-12:
                    break
        if cur > best:
            best, bx = cur, x.copy()
    return np.exp(best), bx


def exact_check(G, cuts, lam_num, lam_den, x):
    """exact: compare prod nu_i^{lam_i} with (1/25) by clearing denominators.

    lam_i = lam_num[i]/lam_den ;  test  prod nu_i^{lam_num[i]}  vs  (1/25)^{lam_den}."""
    lhs = Fraction(1)
    vals = []
    for S, e in zip(cuts, lam_num):
        nu = sum(x[u] * x[v] for u, v in G.edges
                 if ((S >> u) & 1) == ((S >> v) & 1))
        vals.append(nu)
        lhs *= nu ** e
    rhs = Fraction(1, 25) ** lam_den
    return lhs, rhs, vals


if __name__ == "__main__":
    for G in [wagner(), petersen(), grotzsch(), blowup(cycle(5), [2] * 5)]:
        cuts, cyc = perfect_cuts(G)
        k = len(cuts)
        lam = [1.0 / k] * k
        val, bx = certificate_max(G, cuts, lam)
        print("%-12s #perfect=%d  max_x prod nu^(1/%d) = %.9f   1/25 = 0.04   -> %s"
              % (G.name, k, k, val, "CERTIFICATE HOLDS" if val <= 0.04 + 2e-7 else "FAILS"),
              flush=True)
        print("     argmax x ~ %s" % np.round(bx, 5), flush=True)
        # exact test at the rationalised argmax
        for D in (5, 8, 10, 16, 20, 24, 25, 40, 100):
            num = [int(round(t * D)) for t in bx]
            s = sum(num)
            if s == 0:
                continue
            xq = [Fraction(t, s) for t in num]
            lhs, rhs, vals = exact_check(G, cuts, [1] * k, k, xq)
            if lhs > rhs:
                print("     EXACT VIOLATION at x=%s  (nu = %s)"
                      % ([str(t) for t in xq], [str(v) for v in vals]), flush=True)
                break
