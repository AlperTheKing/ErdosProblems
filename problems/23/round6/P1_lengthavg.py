"""Exact check of section 3 of P1.md:  averaging arc cuts of a FIXED length l over uniform
position gives

    V(l) = W (1 - 2l) + 2 * sum_e w_e (l - d_e)_+ ,      V'(l) = -2W + 2 mu_pair([1/3,l)) <= 0,

so V is non-increasing on [1/3,1/2]: V(1/3) = W/3 (the 1/3-arc average) and V(1/2) = A = W-2T
is the best of them.  Any repaired certificate must therefore vary the arc LENGTH.

Two independent computations are compared, both exact:
  (i) the closed form above;
  (ii) a direct integration of a -> value(arc [a,a+l)) over a in [0,1), by splitting [0,1) at
      every breakpoint (each atom position and each atom position - l).
"""
from fractions import Fraction as F
from itertools import combinations
from P1_engine import Meas, gamma, WITNESSES

THIRD, HALF = F(1, 3), F(1, 2)


def V_closed(mu, l):
    tot = F(0)
    for i in range(mu.n):
        for j in range(i + 1, mu.n):
            if mu.adj[i][j]:
                d = mu.d[i][j]
                tot += mu.wt[i] * mu.wt[j] * (1 - 2 * l + 2 * max(F(0), l - d))
    return tot


def V_direct(mu, l):
    """exact integral over a of the value of the arc cut [a, a+l)"""
    bps = sorted(set([p % 1 for p in mu.pos] + [(p - l) % 1 for p in mu.pos]))
    tot = F(0)
    for k in range(len(bps)):
        a0, a1 = bps[k], bps[(k + 1) % len(bps)]
        length = (a1 - a0) % 1
        if length == 0:
            continue
        a = a0 + length / 2                     # a generic point of the cell
        inI = [((mu.pos[i] - a) % 1) < l for i in range(mu.n)]
        val = sum(mu.wt[i] * mu.wt[j] for i, j in combinations(range(mu.n), 2)
                  if mu.adj[i][j] and inI[i] == inI[j])
        tot += length * val
    return tot


if __name__ == '__main__':
    tests = [("W2 C5", gamma(5, [1] * 5)),
             ("W3 uniform G18", gamma(18, [1] * 18)),
             ("W7 unequal five-atom", gamma(20, [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1, 3, 0, 0,
                                                 0, 0, 0, 1, 3])),
             ("CE Wagner on G20", Meas([F(k, 20) for k in (0, 1, 6, 7, 12, 13, 14, 19)],
                                       [F(1, 8)] * 8))]
    ls = [F(1, 3), F(3, 8), F(2, 5), F(5, 12), F(9, 20), F(7, 15), F(1, 2)]
    for tag, mu in tests:
        print(f"{tag}:  W={mu.W}  A=W-2T={mu.A}")
        prev = None
        for l in ls:
            vc, vd = V_closed(mu, l), V_direct(mu, l)
            assert vc == vd, (tag, l, vc, vd)          # the two computations must agree exactly
            mono = '' if prev is None else ('  (decreasing OK)' if vc <= prev
                                            else '  *** V INCREASED ***')
            assert prev is None or vc <= prev, "V is not non-increasing!"
            print(f"    l={str(l):5s}  V(l)={str(vc):>12s} = {float(vc):.6f}{mono}")
            prev = vc
        assert V_closed(mu, THIRD) == mu.W / 3, "V(1/3) != W/3"
        assert V_closed(mu, HALF) == mu.A, "V(1/2) != A"
        print(f"    checks: V(1/3) = W/3 = {float(mu.W/3):.6f} and V(1/2) = A = "
              f"{float(mu.A):.6f}  [both exact]\n")
    print("all length-averages verified exactly by two independent computations;")
    print("V is non-increasing in l on [1/3,1/2] in every case, so l = 1/2 (i.e. A) is the best")
    print("fixed-length uniform average -- and A fails on the Wagner witness (3/64 > 1/25).")
