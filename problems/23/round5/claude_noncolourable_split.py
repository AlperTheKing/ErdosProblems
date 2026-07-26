"""ROOT-AGENT (Claude): split max_x psi(Gamma_11) by C5-colourability of the support.

The bridge in Codex's R10 route needs only  max_x psi(Gamma_11) <= 1/25  (weaker than the arc form).
Split the simplex by whether supp(x) is C5-colourable:

  * C5-COLOURABLE support: PROVED already. If supp(x) is C5-colourable then Gamma_11[supp(x)] is a
    subgraph of a complete C5 blow-up B, so psi(Gamma_11,x) <= psi(B,x) = min_i y_i y_{i+1} by
    Theorem B (gated, R3-C20), and AM-GM gives min_i y_i y_{i+1} <= (sum x)^2/25. Nothing to do.

  * NON-C5-COLOURABLE support: open. This is exactly the hard core.

R3-C35 showed EVERY equality point of the arc certificate has C5-colourable support. If the same
holds for psi -- i.e. every weighting attaining psi = (sum x)^2/25 is C5-colourable-supported -- then
the non-colourable region carries a strict MARGIN, and a margin is precisely what makes a finite
branch-and-bound closure viable where the sharp problem is hopeless.

So: measure max psi over non-C5-colourable supports, exhaustively, and watch whether it RISES with
grid refinement (the test my A27 retraction taught me to run) or stays bounded below 1/25.
"""
import sys
from itertools import product

import numpy as np


def gamma_g(m):
    return m, [(u, v) for u in range(m) for v in range(u + 1, m)
               if 3 * min((u - v) % m, (v - u) % m) > m]


n, E = gamma_g(11)
A = [set() for _ in range(n)]
for u, v in E:
    A[u].add(v)
    A[v].add(u)
ue = np.array([e[0] for e in E])
ve = np.array([e[1] for e in E])
ncuts = 1 << (n - 1)
M = np.zeros((ncuts, len(E)), dtype=np.int32)
mm = np.arange(ncuts, dtype=np.int64)
Sb = (mm << 1) | 1
for k, (u, v) in enumerate(E):
    M[:, k] = (((Sb >> u) & 1) == ((Sb >> v) & 1)).astype(np.int32)
MT = np.ascontiguousarray(M.T)


def colourable(mask):
    sup = [v for v in range(n) if (mask >> v) & 1]
    col = {}

    def rec(i):
        if i == len(sup):
            return True
        v = sup[i]
        for c in range(5 if i else 1):
            if all((col[w] - c) % 5 in (1, 4) for w in A[v] if w in col):
                col[v] = c
                if rec(i + 1):
                    return True
                del col[v]
        return False

    return rec(0)


COLOURABLE = np.zeros(1 << n, dtype=bool)
for mask in range(1, 1 << n):
    COLOURABLE[mask] = colourable(mask)
nc = [mask for mask in range(1, 1 << n) if not COLOURABLE[mask]]
print(f"Gamma_11: subsets {(1 << n) - 1};  C5-colourable {int(COLOURABLE.sum())};  "
      f"NOT colourable {len(nc)}")
minimal = [m0 for m0 in nc
           if all(COLOURABLE[m0 & ~(1 << v)] for v in range(n) if (m0 >> v) & 1)]
print(f"  minimal non-C5-colourable induced subgraphs: {len(minimal)}, sizes "
      f"{sorted({bin(m0).count('1') for m0 in minimal})}")
for m0 in minimal[:4]:
    print(f"    e.g. {[v for v in range(n) if (m0 >> v) & 1]}")


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


print(f"\n{'q':>4s} {'weightings':>10s} {'non-col supports':>17s} "
      f"{'max 25psi/q^2 COLOURABLE':>26s} {'max 25psi/q^2 NON-COLOURABLE':>30s}")
prev = None
for q in (8, 10, 12, 14, 15):
    rows = np.fromiter((v for a in compositions(q, n) for v in a), dtype=np.int32)
    P = rows.reshape(-1, n)
    K = P.shape[0]
    psi = np.empty(K, dtype=np.int64)
    CH = 60000
    for s in range(0, K, CH):
        blk = P[s:s + CH]
        pr = (blk[:, ue] * blk[:, ve]).astype(np.int32)
        psi[s:s + CH] = (pr @ MT).min(axis=1)
    masks = np.zeros(K, dtype=np.int64)
    for v in range(n):
        masks |= ((P[:, v] > 0).astype(np.int64) << v)
    col = COLOURABLE[masks]
    a1 = 25 * int(psi[col].max()) / (q * q) if col.any() else 0.0
    a2 = 25 * int(psi[~col].max()) / (q * q) if (~col).any() else 0.0
    print(f"{q:4d} {K:10d} {int((~col).sum()):17d} {a1:26.6f} {a2:30.6f}")
    if prev is not None and a2 > prev + 1e-12:
        print(f"      ^ the non-colourable maximum ROSE from {prev:.6f}")
    prev = a2
    sys.stdout.flush()

print("\nIf the non-colourable column stays bounded below 1, then combined with the PROVED")
print("colourable case the frontier splits into a settled half and a NON-SHARP half -- and a")
print("non-sharp target is finitely checkable, unlike the sharp one.")
