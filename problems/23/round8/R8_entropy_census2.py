"""Census over the relevant class: connected triangle-free graphs of min degree
>= 4 (a minimal counterexample to Erdos 23 has delta > (4N-2)/25 and N >= 41, so
delta >= 7; delta >= 4 is a generous superset for small n).

For each graph decide the fate of every AVERAGING certificate (fixed
distribution over cuts aggregated by any strictly monotone mean -- arithmetic,
geometric, power, Gibbs free energy at any beta):

    DEAD-0      R(H) = empty
    DEAD-star   some vertex meets every S in R and |R| <= 6  (THEOREM R8-4)
    DEAD-w      an explicit integer weighting a with min_{S in R} m_S(a) >
                (sum a)^2/25 is found by search (verified exactly)
    ALIVE       none of the above

Reads graph6 on stdin.
"""

import sys
from fractions import Fraction
from itertools import combinations
import numpy as np


def g6(s):
    d = [ord(c) - 63 for c in s.strip()]
    n = d[0]
    bits = []
    for x in d[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    E, i = [], 0
    for j in range(1, n):
        for u in range(j):
            if bits[i]:
                E.append((u, j))
            i += 1
    return n, E


def rainbow(n, E):
    m = len(E)
    eidx = {e: i for i, e in enumerate(E)}
    adj = [[False] * n for _ in range(n)]
    for u, v in E:
        adj[u][v] = adj[v][u] = True
    for (u, v) in E:
        for w in range(n):
            if adj[u][w] and adj[v][w]:
                return None                      # triangle
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
    if not pm:
        return None
    R = []
    for mask in range(1 << (n - 1)):
        side = [(mask >> v) & 1 if v < n - 1 else 0 for v in range(n)]
        mono = 0
        for i, (u, v) in enumerate(E):
            if side[u] == side[v]:
                mono |= 1 << i
        if all(bin(mono & p).count("1") == 1 for p in pm):
            R.append(mono)
    return pm, sorted(set(R))


def star_kill(n, E, cls):
    k = len(cls)
    if k > 6:
        return None
    for v in range(n):
        pick = {}
        for j, F in enumerate(cls):
            for (x, y) in F:
                if x == v or y == v:
                    pick[j] = x + y - v
                    break
        if len(pick) == k:
            a = [0] * n
            a[v] = k
            for j in pick:
                a[pick[j]] += 1
            return v, a
    return None


def search_kill(n, E, cls, tries=4000, seed=7):
    """random + local search for an integer weighting with 25 min_j q_j > (sum a)^2"""
    rng = np.random.default_rng(seed)
    best = Fraction(0)
    barg = None
    for _ in range(tries):
        a = list(rng.integers(0, 6, n))
        if sum(a) == 0:
            continue
        cur = ratio(a, cls)
        improved = True
        while improved:
            improved = False
            for v in range(n):
                for d in (-1, 1):
                    b = list(a)
                    b[v] += d
                    if b[v] < 0 or sum(b) == 0:
                        continue
                    r = ratio(b, cls)
                    if r > cur:
                        a, cur, improved = b, r, True
        if cur > best:
            best, barg = cur, tuple(a)
    return best, barg


def ratio(a, cls):
    q = sum(a)
    if q == 0:
        return Fraction(0)
    return Fraction(25 * min(sum(a[u] * a[v] for (u, v) in F) for F in cls),
                    q * q)


if __name__ == "__main__":
    tot = d0 = dstar = dw = alive = 0
    alive_list = []
    for line in sys.stdin:
        if not line.strip():
            continue
        n, E = g6(line)
        res = rainbow(n, E)
        if res is None:
            continue
        pm, R = res
        tot += 1
        cls = [[E[i] for i in range(len(E)) if (msk >> i) & 1] for msk in R]
        if not R:
            d0 += 1
            continue
        sk = star_kill(n, E, cls)
        if sk:
            dstar += 1
            continue
        r, arg = search_kill(n, E, cls, tries=300)
        if r > 1:
            dw += 1
            continue
        alive += 1
        deg = [sum(1 for e in E if v in e) for v in range(n)]
        alive_list.append((line.strip(), n, len(E), len(R),
                           min(deg), max(deg), str(r)))
    print(f"graphs with an induced C5   : {tot}")
    print(f"  DEAD-0    (R empty)       : {d0}")
    print(f"  DEAD-star (THEOREM R8-4)  : {dstar}")
    print(f"  DEAD-w    (search witness): {dw}")
    print(f"  ALIVE                     : {alive}")
    for e in alive_list[:30]:
        print("    ALIVE:", e)
