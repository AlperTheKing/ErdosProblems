"""ROOT-AGENT (Claude): is there a MARGIN on the region Theorem F leaves open, on Gamma_11?

Theorem F (gated, R3-C25): psi <= 1/25 whenever eta(C) <= 4/25 for SOME induced pentagon C, where
eta(C) = 1 - x(C) is the weight off C. So the region it does NOT settle is

        UNSETTLED_F = { x : eta(C) > 4/25 for EVERY induced pentagon C }
                    = { x : x(C) < 21/25 for every induced pentagon C }.

Every C5-concentration has eta = 0 and is therefore SETTLED, so the equality cases of the conjecture
are removed from the unsettled region. That is exactly what a branch-and-bound closure would need:
if max psi over UNSETTLED_F is bounded away from 1/25 by a definite margin, the rest of the simplex
can be closed with crude interval bounds and max_x psi(Gamma_11) <= 1/25 becomes provable, which is
what Codex's bridge needs (weaker than the arc form Codex is certifying).

This is the SAME question I got wrong before with a weaker notion of settled -- Codex showed the
unsettled maximum rises with grid refinement and no epsilon exists (R3-C25, my retraction). Theorem F
settles strictly more than that criterion did, so the question is genuinely reopened, and I check it
the way that retraction taught me to: EXHAUSTIVELY over integer weightings, watching whether the
maximum RISES with q rather than trusting any single grid.
"""
import sys
from fractions import Fraction as F
from itertools import combinations

import numpy as np


def gamma_g(m):
    return m, [(u, v) for u in range(m) for v in range(u + 1, m)
               if 3 * min((u - v) % m, (v - u) % m) > m]


n, E = gamma_g(11)
A = [set() for _ in range(n)]
for u, v in E:
    A[u].add(v)
    A[v].add(u)
pent = [T for T in combinations(range(n), 5) if all(len(A[v] & set(T)) == 2 for v in T)]
print(f"Gamma_11: |E| = {len(E)}, induced pentagons = {len(pent)}")

ue = np.array([e[0] for e in E])
ve = np.array([e[1] for e in E])
ncuts = 1 << (n - 1)
M = np.zeros((ncuts, len(E)), dtype=np.int32)
mm = np.arange(ncuts, dtype=np.int64)
Sb = (mm << 1) | 1
for k, (u, v) in enumerate(E):
    M[:, k] = (((Sb >> u) & 1) == ((Sb >> v) & 1)).astype(np.int32)
MT = np.ascontiguousarray(M.T)
PENT = np.zeros((len(pent), n), dtype=np.int32)
for i, T in enumerate(pent):
    for v in T:
        PENT[i, v] = 1


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


print(f"\n{'q':>4s} {'weightings':>12s} {'max 25psi/q^2 ALL':>19s} {'unsettled':>10s} "
      f"{'max 25psi/q^2 UNSETTLED_F':>27s}")
prev = None
for q in (8, 10, 12, 14):
    rows = np.fromiter((v for a in compositions(q, n) for v in a), dtype=np.int32)
    P = rows.reshape(-1, n)
    K = P.shape[0]
    psi = np.empty(K, dtype=np.int64)
    CH = 100000
    for s in range(0, K, CH):
        blk = P[s:s + CH]
        pr = (blk[:, ue] * blk[:, ve]).astype(np.int32)
        psi[s:s + CH] = (pr @ MT).min(axis=1)
    # x(C) < 21/25 for EVERY pentagon  <=>  25 * max_C (a . 1_C) < 21 q
    maxpc = (P @ PENT.T).max(axis=1)
    unsettled = 25 * maxpc.astype(np.int64) < 21 * q
    nu = int(unsettled.sum())
    allmax = F(25 * int(psi.max()), q * q)
    if nu:
        um = F(25 * int(psi[unsettled].max()), q * q)
    else:
        um = None
    print(f"{q:4d} {K:12d} {str(allmax) + ' = ' + f'{float(allmax):.6f}':>19s} {nu:10d} "
          f"{(str(um) + ' = ' + f'{float(um):.6f}') if um else '-':>27s}")
    if um is not None:
        if prev is not None and um > prev:
            print(f"      ^ RISES from {float(prev):.6f}: no margin is being established")
        prev = um
    sys.stdout.flush()

print("\nA maximum that stays bounded below 1 would make a branch-and-bound closure viable.")
print("A maximum that climbs toward 1 kills that idea, exactly as it killed the earlier A27 form.")
