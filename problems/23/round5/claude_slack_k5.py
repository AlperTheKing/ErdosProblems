"""ROOT-AGENT (Claude): does the R3-C37 slack persist at k = 5?

R3-C38 gave a reduction uniform in k: a support of And(k) is C5-colourable iff it contains no induced
Wagner, and on colourable supports psi <= (sum x)^2/25 is PROVED (Theorem B + AM-GM). So the whole
Andrasfai side reduces to WAGNER-CONTAINING supports.

R3-C37 measured roughly 17% slack there at k = 4 (max 25*psi/q^2 = 100/121 = 0.826 over
non-colourable supports of Gamma_11). I explicitly did NOT claim it persists in k. This measures
k = 5 on Gamma_14, which is the first real test of that.

If the non-colourable maximum at k = 5 is comparable (~0.8), the reduction has uniform value and the
remaining work is to prove an epsilon. If it climbs toward 1, the reduction still holds as a
statement but stops being useful, and I will record that rather than let the previous entry stand
unqualified.

Both halves are reported so the contrast is visible: the colourable half must reach exactly 1 at
grids divisible by 5, since that is where the equality cases live.
"""
import sys

import numpy as np


def gamma_g(m):
    return m, [(u, v) for u in range(m) for v in range(u + 1, m)
               if 3 * min((u - v) % m, (v - u) % m) > m]


for m in (14,):
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

    COL = np.zeros(1 << n, dtype=bool)
    for mask in range(1, 1 << n):
        COL[mask] = colourable(mask)

    ue = np.array([e[0] for e in E])
    ve = np.array([e[1] for e in E])
    ncuts = 1 << (n - 1)
    M = np.zeros((ncuts, len(E)), dtype=np.int32)
    mm = np.arange(ncuts, dtype=np.int64)
    Sb = (mm << 1) | 1
    for k, (u, v) in enumerate(E):
        M[:, k] = (((Sb >> u) & 1) == ((Sb >> v) & 1)).astype(np.int32)
    MT = np.ascontiguousarray(M.T)

    def compositions(total, parts):
        a = [0] * parts
        a[0] = total
        while True:
            yield a
            if a[parts - 1] == total:
                return
            if a[0] > 0:
                a[0] -= 1
                a[1] += 1
            else:
                j = next(i for i in range(1, parts) if a[i] > 0)
                a[0] = a[j] - 1
                a[j] = 0
                a[j + 1] += 1

    k = (m + 1) // 3
    print(f"\n=== And({k}) = Gamma_{m}: {n} vertices, {len(E)} edges, "
          f"{int((~COL[1:]).sum())} non-colourable supports of {(1 << n) - 1} ===")
    print(f"{'q':>4s} {'weightings':>11s} {'max 25psi/q^2 COLOURABLE':>26s} "
          f"{'max 25psi/q^2 WAGNER-CONTAINING':>32s}")
    qs = (10, 12) if m == 14 else (10, 12, 15)
    for q in qs:
        rows = np.fromiter((v for a in compositions(q, n) for v in a), dtype=np.int32)
        P = rows.reshape(-1, n)
        K = P.shape[0]
        psi = np.empty(K, dtype=np.int64)
        CH = max(1000, 150_000_000 // (ncuts * 4))
        for s in range(0, K, CH):
            blk = P[s:s + CH]
            pr = (blk[:, ue] * blk[:, ve]).astype(np.int32)
            psi[s:s + CH] = (pr @ MT).min(axis=1)
        masks = np.zeros(K, dtype=np.int64)
        for v in range(n):
            masks |= ((P[:, v] > 0).astype(np.int64) << v)
        col = COL[masks]
        c1 = 25 * int(psi[col].max()) / (q * q) if col.any() else 0.0
        c2 = 25 * int(psi[~col].max()) / (q * q) if (~col).any() else 0.0
        print(f"{q:4d} {K:11d} {c1:26.6f} {c2:32.6f}")
        sys.stdout.flush()

print("\nComparable non-colourable maxima at k = 4 and k = 5 would mean the R3-C38 reduction has")
print("uniform value: one epsilon to prove, on Wagner-containing supports, for the whole family.")
