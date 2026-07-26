"""ROOT-AGENT (Claude): identify the Letzter-Snyder target family, and close piece (i) above n/5.

Letzter and Snyder, "The homomorphism threshold of {C3,C5}-free graphs" (J. Graph Theory 2019;
arXiv:1610.04932): every {C3,C5}-free graph on n vertices with minimum degree > n/5 is HOMOMORPHIC
to the graph obtained from a (5k-3)-cycle by adding all chords of length 1 mod 5, for some k; and the
homomorphism threshold of the class is exactly 1/5.

That is precisely the missing lemma named in R3-C47. If their target family is the odd-girth-7
circular-clique family I measured -- on which max_x psi = 1/49 -- then by accepted base (2)
(G -> H implies bip(G) <= N^2 max_x psi(H)) piece (i) closes for delta > n/5:

        {C3,C5}-free, delta > n/5  ==>  hom to L_k  ==>  bip <= N^2 * (1/49)  <=  N^2/25.

Checked here: build L_k = C_{5k-3} plus all chords of length 1 mod 5, confirm it is triangle- and
pentagon-free, confirm it is ISOMORPHIC to the circular clique I tested, and recompute max_x psi.
"""
import sys
from fractions import Fraction as F
from itertools import combinations

import numpy as np


def L_k(k):
    """C_{5k-3} plus all chords of length 1 mod 5"""
    n = 5 * k - 3
    lens = [d for d in range(1, n // 2 + 1) if d % 5 == 1 or (n - d) % 5 == 1]
    E = []
    for u in range(n):
        for d in lens:
            v = (u + d) % n
            if u < v:
                E.append((u, v))
            elif v < u:
                E.append((v, u))
    return n, sorted(set(E))


def circ_clique(p, q):
    return p, [(u, v) for u in range(p) for v in range(u + 1, p)
               if min((u - v) % p, (v - u) % p) >= q]


def cycles_of_len(n, E, L):
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    for s in range(n):
        stack = [(s, {s}, 1)]
        while stack:
            u, seen, d = stack.pop()
            if d == L:
                if s in A[u]:
                    return True
                continue
            for v in A[u]:
                if v > s and v not in seen:
                    stack.append((v, seen | {v}, d + 1))
    return False


def iso_circulant(n, E1, E2):
    """both are circulants on Z_n; test isomorphism by index multiplication"""
    s1 = {tuple(sorted(e)) for e in E1}
    for a in range(1, n):
        if np.gcd(a, n) != 1:
            continue
        s2 = {tuple(sorted(((a * u) % n, (a * v) % n))) for (u, v) in E2}
        if s1 == s2:
            return a
    return None


def psi_max(n, E, starts=16, seed=17):
    ncuts = 1 << (n - 1)
    if ncuts > (1 << 22):
        return None
    M = np.zeros((ncuts, len(E)), dtype=np.int8)
    mm = np.arange(ncuts, dtype=np.int64)
    S = (mm << 1) | 1
    for k, (u, v) in enumerate(E):
        M[:, k] = (((S >> u) & 1) == ((S >> v) & 1))
    ue = np.array([e[0] for e in E])
    ve = np.array([e[1] for e in E])
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    X0 = []
    for T in combinations(range(n), 7):
        if all(len(A[v] & set(T)) == 2 for v in T):
            x = np.zeros(n)
            for v in T:
                x[v] = 1.0 / 7
            X0.append(x)
            if len(X0) >= 5:
                break
    X0.append(np.ones(n) / n)
    rng = np.random.default_rng(seed)
    for _ in range(starts):
        X0.append(rng.dirichlet(np.ones(n)))
    best = 0.0
    for x in X0:
        for _ in range(30):
            p = x[ue] * x[ve]
            b = (M @ p).min()
            improved = False
            for i in range(n):
                for step in (0.05, 0.02, 0.006):
                    for sgn in (1, -1):
                        y = x.copy()
                        y[i] = max(0.0, y[i] + sgn * step)
                        if y.sum() <= 0:
                            continue
                        y = y / y.sum()
                        b2 = (M @ (y[ue] * y[ve])).min()
                        if b2 > b + 1e-13:
                            x, b, improved = y, b2, True
                            break
                    if improved:
                        break
                if improved:
                    break
            if not improved:
                break
        best = max(best, (M @ (x[ue] * x[ve])).min())
    return best


print("Letzter-Snyder target family L_k = C_{5k-3} + chords of length 1 mod 5\n")
print(f"{'k':>3s} {'n=5k-3':>7s} {'|E|':>5s} {'delta':>6s} {'C3?':>5s} {'C5?':>5s} "
      f"{'= K_{p/q}':>12s} {'max psi':>12s} {'1/49':>10s}")
for k in (2, 3, 4, 5):
    n, E = L_k(k)
    deg = [0] * n
    for u, v in E:
        deg[u] += 1
        deg[v] += 1
    t3 = cycles_of_len(n, E, 3)
    t5 = cycles_of_len(n, E, 5)
    # find the matching circular clique on the same vertex count
    match = None
    for q in range(2, n // 2 + 1):
        _, E2 = circ_clique(n, q)
        if len(E2) == len(E) and iso_circulant(n, E, E2) is not None:
            match = F(n, q)
            break
    ps = psi_max(n, E)
    print(f"{k:3d} {n:7d} {len(E):5d} {min(deg):6d} {str(t3):>5s} {str(t5):>5s} "
          f"{str(match) if match else '-':>12s} "
          f"{(f'{ps:.8f}' if ps is not None else 'too large'):>12s} {1/49:10.8f}")
    sys.stdout.flush()

print("\nIf every L_k is triangle- and pentagon-free with max_x psi = 1/49, then by accepted base (2)")
print("  {C3,C5}-free with delta > n/5  ==>  hom to some L_k  ==>  bip <= N^2/49 <= N^2/25,")
print("closing piece (i) ABOVE n/5. The residual band is (4N-2)/25 < delta <= N/5,")
print(f"  i.e. {4/25:.4f} N < delta <= {1/5:.4f} N -- and Letzter-Snyder show 1/5 is SHARP,")
print("  so below it the class genuinely contains graphs with no bounded homomorphic image.")
