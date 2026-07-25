"""Value of the multiplicative (geometric-mean) transport certificate on the graphs
that PASS the necessary condition (i.e. that do have C5-perfect cuts).

By the obstruction lemma the support of lambda must consist of C5-perfect cuts;
and averaging lambda over Aut(H) never increases  max_x prod_S nu_S^{lambda_S}
(Hoelder), so if the C5-perfect cuts form a single Aut-orbit the certificate value is

        cert(H) = max_{x in simplex} prod_{S perfect} nu_S(x)^{1/#perfect}.

We maximise log cert numerically from many random starts and then re-evaluate the
best point in exact rational arithmetic.  cert(H) > 1/25 kills the certificate for H.
"""
import sys
from fractions import Fraction
from itertools import combinations
import numpy as np

sys.path.insert(0, ".")
from R8_transport_lib import *   # noqa


def induced_c5s(G):
    out = []
    for verts in combinations(range(G.n), 5):
        mask = 0
        for v in verts:
            mask |= 1 << v
        e = G.induced_edges(mask)
        if len(e) != 5:
            continue
        deg = {v: 0 for v in verts}
        for u, v in e:
            deg[u] += 1
            deg[v] += 1
        if all(d == 2 for d in deg.values()):
            out.append((verts, e))
    return out


def perfect_cuts(G):
    cyc = induced_c5s(G)
    out = []
    for S in G.all_cuts():
        if all(sum(1 for u, v in es if ((S >> u) & 1) == ((S >> v) & 1)) == 1
               for vs, es in cyc):
            out.append(S)
    return out, cyc


def nu(G, S, x):
    return sum(x[u] * x[v] for u, v in G.edges
               if ((S >> u) & 1) == ((S >> v) & 1))


def cert_value(G, tries=4000, seed=1):
    cuts, cyc = perfect_cuts(G)
    if not cuts:
        print("%-14s no C5-perfect cut -> certificate impossible" % G.name)
        return None
    k = len(cuts)
    rng = np.random.default_rng(seed)
    n = G.n
    mono = []
    for S in cuts:
        M = np.zeros((n, n))
        for u, v in G.edges:
            if ((S >> u) & 1) == ((S >> v) & 1):
                M[u, v] = M[v, u] = 0.5
        mono.append(M)

    def logF(x):
        tot = 0.0
        for M in mono:
            q = x @ M @ x
            if q <= 0:
                return -1e18
            tot += np.log(q)
        return tot / k

    best, bestx = -1e18, None
    for t in range(tries):
        x = rng.random(n) ** rng.choice([0.3, 1.0, 3.0])
        x /= x.sum()
        step = 0.25
        cur = logF(x)
        for it in range(400):
            g = np.zeros(n)
            for M in mono:
                q = x @ M @ x
                if q <= 0:
                    g = None
                    break
                g += 2 * (M @ x) / q
            if g is None:
                break
            g /= k
            y = x * np.exp(step * g)          # mirror ascent on the simplex
            y = np.maximum(y, 0)
            y /= y.sum()
            v = logF(y)
            if v > cur:
                cur, x = v, y
            else:
                step *= 0.6
                if step < 1e-10:
                    break
        if cur > best:
            best, bestx = cur, x.copy()
    val = np.exp(best)
    # exact re-evaluation at a rationalisation of the best point
    for D in (5, 10, 20, 25, 50, 100, 1000, 10000):
        num = [int(round(t * D)) for t in bestx]
        s = sum(num)
        if s == 0:
            continue
        xq = [Fraction(t, s) for t in num]
        prod = Fraction(1)
        vals = [nu(G, S, xq) for S in cuts]
        if any(v == 0 for v in vals):
            continue
        # compare geometric mean with 1/25 exactly:  prod vals  vs (1/25)^k
        lhs = Fraction(1)
        for v in vals:
            lhs *= v
        rhs = Fraction(1, 25) ** k
        if lhs > rhs:
            print("%-14s #perfect=%d  numeric cert=%.6f  EXACT VIOLATION at x=%s : "
                  "prod nu = %s > (1/25)^%d ; geo-mean = %.6f > 0.04"
                  % (G.name, k, val, [str(t) for t in xq], lhs, k, float(lhs) ** (1.0 / k)))
            return ("KILL", xq, vals)
    print("%-14s #perfect=%d  numeric cert value = %.8f   (1/25 = 0.04)   %s"
          % (G.name, k, val, "OK <= 1/25" if val <= 0.04 + 1e-9 else "FAILS > 1/25"))
    return val, bestx, cuts


if __name__ == "__main__":
    for G in [cycle(5), blowup(cycle(5), [2] * 5), blowup(cycle(5), [3, 1, 2, 2, 1]),
              wagner(), petersen(), grotzsch()]:
        cert_value(G)
