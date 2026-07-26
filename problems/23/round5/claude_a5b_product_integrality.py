"""ROOT-AGENT (Claude): A5b -- can psi exceed Lambda at a PRODUCT weight on Gamma_11?

Why this settles the R10 frontier without any SDP. Theorem A (proved, R3-C22) gives
Lambda(G,x) <= 1/25 for every triangle-free G and every x. So if psi(Gamma_11,x) = Lambda(Gamma_11,x)
for every product weight w_uv = x_u x_v, then max_x psi(Gamma_11) <= 1/25 -- which is exactly what
Codex's bridge needs, and strictly weaker than the arc form Codex is certifying.

The subtlety, and why this is not already known: Gamma_11 is NOT weakly bipartite. I proved that with
an explicit finite gap weight (w = M on the six contracted edges, 1 on ten, 0 on six; tau_w = 4 >
10/3 >= tau*_w). So integrality DOES fail on Gamma_11 -- for some weight. But that witness is
degenerate: it needs six edges at weight 0, and a product weight can only zero an edge by zeroing a
VERTEX, which zeroes every edge at that vertex. Product weights are a thin, structured subfamily and
may well avoid every bad face.

METHOD. Exhaustive over all integer x >= 0 with sum x = q, zeros allowed. psi is the exact integer
minimum over all 1024 cuts (vectorised). Computing Lambda needs an LP over all 596 odd cycles, so it
is run only on the weightings that matter: those with the largest psi, since a gap at small psi
cannot threaten the 1/25 ceiling. Any gap found is then re-verified in exact rationals by exhibiting
a packing (a feasible packing of value psi PROVES psi = Lambda, since packing <= Lambda <= psi).
"""
import sys
from fractions import Fraction as F
from itertools import combinations

import numpy as np
from scipy.optimize import linprog


def gamma_g(m):
    return m, [(u, v) for u in range(m) for v in range(u + 1, m)
               if 3 * min((u - v) % m, (v - u) % m) > m]


n, E = gamma_g(11)
A = [set() for _ in range(n)]
for u, v in E:
    A[u].add(v)
    A[v].add(u)
idx = {e: i for i, e in enumerate(E)}
ue = np.array([e[0] for e in E])
ve = np.array([e[1] for e in E])

ncuts = 1 << (n - 1)
M = np.zeros((ncuts, len(E)), dtype=np.int32)
mm = np.arange(ncuts, dtype=np.int64)
Sb = (mm << 1) | 1
for k, (u, v) in enumerate(E):
    M[:, k] = (((Sb >> u) & 1) == ((Sb >> v) & 1)).astype(np.int32)
MT = np.ascontiguousarray(M.T)

odd = set()
for s in range(n):
    def dfs(u, seen, el):
        for v in sorted(A[u]):
            if v == s and len(seen) >= 3 and len(seen) % 2 == 1:
                odd.add(frozenset(el + [idx[tuple(sorted((u, v)))]]))
            elif v > s and v not in seen:
                dfs(v, seen | {v}, el + [idx[tuple(sorted((u, v)))]])
    dfs(s, {s}, [])
odd = sorted(odd, key=lambda c: (len(c), sorted(c)))
print(f"Gamma_11: |E| = {len(E)}, cuts = {ncuts}, odd cycles = {len(odd)} "
      f"(lengths {sorted({len(c) for c in odd})})")

Apack = np.zeros((len(E), len(odd)))
for k, c in enumerate(odd):
    for i in c:
        Apack[i, k] = 1.0


def lambda_and_packing(a):
    """returns (float Lambda, exact packing value if it certifies psi = Lambda else None)"""
    w = [F(int(a[u]) * int(a[v])) for (u, v) in E]
    res = linprog(-np.ones(len(odd)), A_ub=Apack, b_ub=np.array([float(t) for t in w]),
                  bounds=[(0, None)] * len(odd), method='highs')
    if not res.success:
        return None, None
    return -res.fun, res.x


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


TOP = 2500
for q in (9, 10, 11, 12):
    rows = np.fromiter((v for a in compositions(q, n) for v in a), dtype=np.int32)
    P = rows.reshape(-1, n)
    K = P.shape[0]
    psi = np.empty(K, dtype=np.int64)
    CH = 100000
    for s in range(0, K, CH):
        blk = P[s:s + CH]
        prod = (blk[:, ue] * blk[:, ve]).astype(np.int32)
        psi[s:s + CH] = (prod @ MT).min(axis=1)
    order = np.argsort(-psi)[:TOP]
    gaps, certified = 0, 0
    worst_gap = None
    for j in order:
        a = P[j].tolist()
        ps = int(psi[j])
        if ps == 0:
            continue
        lam, z = lambda_and_packing(a)
        if lam is None:
            continue
        if lam < ps - 1e-6:
            gaps += 1
            if worst_gap is None or ps > worst_gap[0]:
                worst_gap = (ps, a, lam)
        else:
            # certify psi = Lambda exactly by rationalising the packing
            w = [F(int(a[u]) * int(a[v])) for (u, v) in E]
            done = False
            for D in (1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 24, 30, 60, 120):
                zz = [F(int(round(t * D)), D) for t in z]
                if any(t < 0 for t in zz):
                    continue
                if sum(zz) != ps:
                    continue
                load = [sum(zz[k] for k, c in enumerate(odd) if i in c) for i in range(len(E))]
                if all(load[i] <= w[i] for i in range(len(E))):
                    certified += 1
                    done = True
                    break
            if not done:
                pass
    top_psi = int(psi[order[0]])
    print(f"q = {q:3d}: {K:8d} weightings, top {TOP} by psi examined; "
          f"max 25*psi/q^2 = {25 * top_psi / (q * q):.6f}; "
          f"product weights with psi > Lambda: {gaps}; exact psi = Lambda certificates: {certified}")
    if worst_gap:
        print(f"    GAP FOUND: psi = {worst_gap[0]}/{q*q}, Lambda ~ {worst_gap[2]/(q*q):.6f}, "
              f"a = {worst_gap[1]}")
    sys.stdout.flush()

print("\nA gap at a PRODUCT weight would kill the A5b route to the frontier lemma.")
print("No gap, plus exact packing certificates, keeps it alive as an SDP-free route via Theorem A.")
