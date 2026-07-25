"""(1) second-implementation check of the Grotzsch and Clebsch star kills,
   (2) how much room is left on the two survivors, Wagner and Petersen.

For a survivor the fixed-certificate route is exactly the assertion
        max_a  min_{S in R(H)} m_S(a)  <=  (sum a)^2 / 25 ,
and its geometric-mean (entropy) relaxation is the sharper polynomial statement
        prod_{S in R(H)} m_S(a)  <=  (sum a)^10 / 5^10 .
Both are swept here in exact integer arithmetic, and by continuous search.
"""

import numpy as np
from fractions import Fraction
from itertools import combinations

from R8_entropy_verify import (G_grotzsch, G_petersen, G_wagner, bipartite,
                               triangle_free, all_induced_c5, rainbow1,
                               psi_all_cuts)


def clebsch():
    E = [(u, v) for u in range(16) for v in range(u + 1, 16)
         if bin(u ^ v).count("1") in (1, 4)]
    return 16, sorted(E)


def rainbow1_fast(n, E):
    """bitmask version, independent of R8_entropy_targets."""
    eidx = {e: i for i, e in enumerate(E)}
    adj = [[False] * n for _ in range(n)]
    for u, v in E:
        adj[u][v] = adj[v][u] = True
    pm = []
    for S in combinations(range(n), 5):
        if any(sum(1 for u in S if adj[v][u]) != 2 for v in S):
            continue
        seen, st = {S[0]}, [S[0]]
        while st:
            v = st.pop()
            for u in S:
                if adj[v][u] and u not in seen:
                    seen.add(u)
                    st.append(u)
        if len(seen) != 5:
            continue
        msk = 0
        for (u, v) in combinations(S, 2):
            if adj[u][v]:
                msk |= 1 << eidx[(u, v)]
        pm.append(msk)
    out = []
    for mask in range(1 << (n - 1)):
        side = [(mask >> v) & 1 if v < n - 1 else 0 for v in range(n)]
        mono = 0
        for i, (u, v) in enumerate(E):
            if side[u] == side[v]:
                mono |= 1 << i
        if all(bin(mono & p).count("1") == 1 for p in pm):
            out.append(mono)
    return pm, sorted(set(out))


def bip_exact(n, E):
    best = None
    for mask in range(1 << (n - 1)):
        side = [(mask >> v) & 1 if v < n - 1 else 0 for v in range(n)]
        t = sum(1 for (u, v) in E if side[u] == side[v])
        best = t if best is None else min(best, t)
    return best


def classes_of(E, R):
    return [[E[i] for i in range(len(E)) if (msk >> i) & 1] for msk in R]


def maxmin_int(n, E, cls, qmax):
    """exhaustive exact integer sweep of  max_a 25*min_j q_j(a) / (sum a)^2
    and of  max_a 5^10 prod_j q_j(a) / (sum a)^10 ."""
    bestmin = Fraction(0)
    bestprod = Fraction(0)
    argmin = argprod = None

    def rec(i, left, a):
        nonlocal bestmin, bestprod, argmin, argprod
        if i == n:
            if left:
                return
            q = sum(a)
            if q == 0:
                return
            vals = [sum(a[u] * a[v] for (u, v) in F) for F in cls]
            r1 = Fraction(25 * min(vals), q * q)
            if r1 > bestmin:
                bestmin, argmin = r1, tuple(a)
            p = 1
            for t in vals:
                p *= t
            r2 = Fraction(5 ** 10 * p, q ** 10)
            if r2 > bestprod:
                bestprod, argprod = r2, tuple(a)
            return
        for x in range(left + 1):
            a.append(x)
            rec(i + 1, left - x, a)
            a.pop()

    for q in range(1, qmax + 1):
        rec(0, q, [])
    return (bestmin, argmin), (bestprod, argprod)


def maxmin_cont(n, E, cls, restarts=300, seed=1):
    rng = np.random.default_rng(seed)
    idx = [np.array(F, dtype=int) for F in cls]

    def f(a):
        a = np.maximum(a, 0.0)
        s = a.sum()
        if s <= 0:
            return 0.0
        return 25.0 * min(float((a[F[:, 0]] * a[F[:, 1]]).sum())
                          for F in idx) / s ** 2
    best, arg = 0.0, None
    for _ in range(restarts):
        a = rng.random(n)
        if rng.random() < 0.5:
            a *= (rng.random(n) < 0.6)
        cur, step = f(a), 0.25
        for _ in range(6000):
            b = np.maximum(a + rng.normal(0, step, n), 0)
            v = f(b)
            if v > cur:
                a, cur = b, v
            step *= 0.9995
        if cur > best:
            best, arg = cur, a / max(a.sum(), 1e-300)
    return best, arg


if __name__ == "__main__":
    print("=== second implementation: star kills ===")
    for name, (n, E) in [("Grotzsch", G_grotzsch()), ("Clebsch", clebsch())]:
        assert triangle_free(n, E)
        pm, R = rainbow1_fast(n, E)
        cls = classes_of(E, R)
        cover = {}
        for F in cls:
            for e in F:
                cover[e] = cover.get(e, 0) + 1
        deg = [sum(1 for e in E if v in e) for v in range(n)]
        print(f"\n{name}: n={n} |E|={len(E)} bip={bip_exact(n,E)} "
              f"N^2/25={Fraction(n*n,25)} indC5={len(pm)} |R|={len(R)} "
              f"partition={sorted(cover)==sorted(E) and set(cover.values())=={1}} "
              f"deg=[{min(deg)},{max(deg)}]")
        for j, F in enumerate(cls):
            rest = [e for e in E if e not in set(F)]
            print(f"   F_{j+1} ({len(F)} edges) E\\F bipartite="
                  f"{bipartite(n, rest)[0]}  {F if len(F)<=8 else F[:8]}")
        # star witness
        for v in range(n):
            pick = {}
            for j, F in enumerate(cls):
                for (x, y) in F:
                    if x == v or y == v:
                        pick[j] = x + y - v
                        break
            if len(pick) == len(cls):
                k = len(cls)
                a = [0] * n
                a[v] = k
                for j in pick:
                    a[pick[j]] += 1
                q = sum(a)
                vals = [sum(a[x] * a[y] for (x, y) in F) for F in cls]
                sup = [w for w in range(n) if a[w] > 0]
                subE = [(x, y) for (x, y) in E if a[x] > 0 and a[y] > 0]
                print(f"   centre v={v}: a={a}, sum={q}, support induces "
                      f"{len(subE)} edges, bipartite={bipartite(n,subE)[0]}")
                print(f"   m_S(a) = {vals}; min/(sum a)^2 = "
                      f"{Fraction(min(vals), q*q)} > 1/25 = "
                      f"{Fraction(min(vals), q*q) > Fraction(1,25)}")
                print(f"   true psi(a)*(sum a)^2 = {psi_all_cuts(n,E,a)}")
                break

    print("\n=== survivors: how tight is the route ===")
    for name, (n, E), qmax in [("Wagner", G_wagner(), 22),
                               ("Petersen", G_petersen(), 20)]:
        pm, R = rainbow1_fast(n, E)
        cls = classes_of(E, R)
        (bm, am), (bp, ap) = maxmin_int(n, E, cls, qmax)
        cm, ac = maxmin_cont(n, E, cls)
        print(f"\n{name}: |R|={len(R)}  classes={[len(F) for F in cls]}")
        print(f"  exact integer sweep sum a <= {qmax}:")
        print(f"    max 25*min_j q_j/(sum a)^2   = {bm} = {float(bm):.9f} at {am}")
        print(f"    max 5^10*prod q_j/(sum a)^10 = {bp} = {float(bp):.9f} at {ap}")
        print(f"  continuous max of 25*min_j q_j/(sum a)^2 = {cm:.9f}")
        print(f"    at a ~ {None if ac is None else [round(t,4) for t in ac]}")
