"""ROOT-AGENT RE-GATE (Claude): re-certify R3-C18's integrality table with the COMPLETE odd-cycle
list of Gamma_11.

My earlier tool reported 451 odd cycles of lengths 5,7,9 for And(4).  The complete count is 596,
lengths 5,7,9,11 -- every odd HAMILTONIAN cycle was missing.  R3-C18's "psi = Lambda in 30/30" was
computed against the short list.

Direction of the error, stated before re-running so it cannot be rationalised afterwards: fewer
covering constraints => SMALLER Lambda.  Since Lambda <= psi always, an under-computed Lambda that
already equals psi forces the true Lambda to equal psi as well
        Lambda_short <= Lambda_true <= psi = Lambda_short,
so R3-C18's conclusion should SURVIVE.  This run checks that rather than assuming it, and upgrades
the evidence from a float LP to an exact rational PACKING certificate: a feasible packing z with
value exactly psi proves Lambda = psi outright, since packing <= Lambda <= psi.
"""
import sys
from fractions import Fraction as F
from itertools import combinations

import numpy as np
from scipy.optimize import linprog


def gamma(n):
    return [(u, v) for u in range(n) for v in range(u + 1, n)
            if 3 * min((u - v) % n, (v - u) % n) > n]


def odd_cycles(n, E):
    idx = {e: i for i, e in enumerate(E)}
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    out = set()
    for s in range(n):
        def dfs(u, seen, el):
            for v in sorted(A[u]):
                if v == s and len(seen) >= 3 and len(seen) % 2 == 1:
                    out.add(frozenset(el + [idx[tuple(sorted((u, v)))]]))
                elif v > s and v not in seen:
                    dfs(v, seen | {v}, el + [idx[tuple(sorted((u, v)))]])
        dfs(s, {s}, [])
    return sorted(out, key=lambda c: (len(c), sorted(c)))


def psi_exact(n, E, x):
    """min over ALL bipartitions of the monochromatic weight -- exact rationals."""
    best = None
    for m in range(1 << (n - 1)):
        S = (m << 1) | 1
        s = sum(x[u] * x[v] for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1))
        if best is None or s < best:
            best = s
    return best


def certify(n, E, oc, a):
    """Exact packing certificate that Lambda = psi, in INTEGER weights w_uv = a_u a_v.

    Both tau and tau* are homogeneous of degree 1 in the weight, so certifying the identity for the
    integer vector a certifies it for x = a / sum(a).  Working in integers keeps the packing LP's
    vertex denominators small, which is what makes exact rationalisation possible at all -- with
    x = a/T the capacities carry denominator T^2 and no fixed small denominator can ever match psi.
    """
    w = [F(int(a[u]) * int(a[v])) for (u, v) in E]
    psi = psi_exact(n, E, [F(int(t)) for t in a])
    Aub = np.zeros((len(E), len(oc)))
    for k, c in enumerate(oc):
        for i in c:
            Aub[i, k] = 1.0
    res = linprog(-np.ones(len(oc)), A_ub=Aub, b_ub=np.array([float(t) for t in w]),
                  bounds=[(0, None)] * len(oc), method='highs')
    if not res.success:
        return psi, None, None
    for D in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 24, 28, 30, 36, 40, 42,
              48, 60, 72, 84, 120, 168, 180, 210, 240, 360, 420, 840, 2520):
        z = [F(int(round(t * D)), D) for t in res.x]
        if any(t < 0 for t in z):
            continue
        if sum(z) != psi:
            continue
        load = [sum(z[k] for k, c in enumerate(oc) if i in c) for i in range(len(E))]
        if all(load[i] <= w[i] for i in range(len(E))):
            return psi, sum(z), D
    return psi, None, -res.fun


def main():
    n = 11
    E = gamma(n)
    oc = odd_cycles(n, E)
    by_len = {}
    for c in oc:
        by_len[len(c)] = by_len.get(len(c), 0) + 1
    print(f"Gamma_11 = And(4): |E| = {len(E)},  odd cycles by length {dict(sorted(by_len.items()))}, "
          f"total {len(oc)}")
    print(f"  earlier tool reported 451 of lengths 5,7,9; missing = {len(oc) - 451} "
          f"(= the {by_len.get(11, 0)} odd Hamiltonian cycles)"
          f"  -> {'consistent' if len(oc) - 451 == by_len.get(11, 0) else 'INCONSISTENT'}")

    tests = [("uniform", [1] * 11)]
    c5 = [0, 3, 7, 10, 4]                                   # an induced C5 inside Gamma_11
    xc = [0] * 11
    for v in c5:
        xc[v] = 1
    tests.append(("C5-concentration", xc))
    rng = np.random.default_rng(20260726)
    for t in range(30):
        a = rng.integers(0, 13, size=11)
        if a.sum() == 0:
            continue
        tests.append((f"random#{t}", [int(v) for v in a]))

    ok = 0
    shown = 0
    for name, x in tests:
        psi, val, D = certify(n, E, oc, x)
        good = val is not None and val == psi
        ok += good
        if shown < 6 or not good:
            print(f"  {name:18s} psi = {str(psi):14s} packing = "
                  f"{str(val) if val is not None else 'no exact cert':14s} "
                  f"{'CERTIFIED Lambda = psi' if good else 'not certified exactly'}"
                  + (f" (denominator 1/{D})" if good else ""))
            shown += 1
    print(f"\nexact packing certificates: {ok} of {len(tests)}")
    print("(psi is the exact minimum over all 1024 cuts; a feasible packing of value psi forces "
          "Lambda = psi because packing <= Lambda <= psi.)")

    # the induced C5 used above really is induced
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    ind = all(len(A[v] & set(c5)) == 2 for v in c5)
    print(f"the C5-concentration uses a genuine induced C5 {c5}: {ind}")


if __name__ == '__main__':
    main()
