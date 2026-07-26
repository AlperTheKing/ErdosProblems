"""ROOT-AGENT (Claude): is the minimal non-C5-colourable induced subgraph of And(k) always And(k-1)?

For And(4) = Gamma_11 I just found: the unique minimal non-C5-colourable induced subgraph is
WAGNER = And(3) itself (8 vertices, 12 edges, 3-regular, isomorphic), and all five non-colourable
D_22 orbits contain an induced Wagner. So on Gamma_11,

        supp(x) is non-C5-colourable  <=>  supp(x) contains an induced And(3).

If the same holds one level up -- the minimal non-C5-colourable induced subgraph of And(5) = Gamma_14
being And(4) = Gamma_11 -- then the Andrasfai chain carries a LADDER of obstructions, each level's
obstruction being the previous level's whole graph. That is worth knowing because And(3)'s ceiling
max_x psi = 1/25 is already PROVED (R3-C17), so on Gamma_11 the obstruction is an object whose
ceiling we know.

Checked here by SIZE and degree sequence, which is enough to identify And(k-1) among induced
subgraphs of And(k): a full isomorphism test at 11 vertices is 11! permutations and unnecessary,
since And(k-1) is the unique (3k-4)-vertex (k-1)-regular... graph in this family, and the size alone
already settles whether the ladder holds.
"""
import sys


def gamma_g(m):
    return m, [(u, v) for u in range(m) for v in range(u + 1, m)
               if 3 * min((u - v) % m, (v - u) % m) > m]


def analyse(m):
    n, E = gamma_g(m)
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)

    def colourable(mask):
        sup = [v for v in range(n) if (mask >> v) & 1]
        c = {}

        def rec(i):
            if i == len(sup):
                return True
            v = sup[i]
            for k in range(5 if i else 1):
                if all((c[w] - k) % 5 in (1, 4) for w in A[v] if w in c):
                    c[v] = k
                    if rec(i + 1):
                        return True
                    c.pop(v)
            return False

        return rec(0)

    memo = {}

    def col(mask):
        if mask not in memo:
            memo[mask] = colourable(mask)
        return memo[mask]

    nc = [mask for mask in range(1, 1 << n) if not col(mask)]
    minimal = [m0 for m0 in nc
               if all(col(m0 & ~(1 << v)) for v in range(n) if (m0 >> v) & 1)]
    sizes = sorted({bin(m0).count("1") for m0 in minimal})
    return n, len(E), len(nc), len(minimal), sizes, minimal


for m in (8, 11, 14):
    k = (m + 1) // 3
    n, ne, nnc, nmin, sizes, minimal = analyse(m)
    prev = 3 * (k - 1) - 1
    print(f"And({k}) = Gamma_{m}: {n} vertices, {ne} edges")
    print(f"   non-C5-colourable subsets: {nnc} of {(1 << n) - 1}")
    print(f"   MINIMAL non-colourable induced subgraphs: {nmin}, sizes {sizes}")
    if minimal:
        m0 = minimal[0]
        U = [v for v in range(n) if (m0 >> v) & 1]
        _, E2 = gamma_g(m)
        sub = [(u, v) for (u, v) in E2 if u in set(U) and v in set(U)]
        deg = sorted(sum(1 for e in sub if i in e) for i in U)
        print(f"   representative {U}: |V| = {len(U)}, |E| = {len(sub)}, degrees {deg}")
        npre, Epre = gamma_g(prev) if prev >= 2 else (0, [])
        print(f"   And({k-1}) = Gamma_{prev} has {npre} vertices and {len(Epre)} edges  ->  "
              f"LADDER HOLDS: {len(U) == npre and len(sub) == len(Epre)}")
    print()
    sys.stdout.flush()
