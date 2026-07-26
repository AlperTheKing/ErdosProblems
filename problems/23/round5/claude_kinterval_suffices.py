"""ROOT-AGENT (Claude): do the 11 length-k interval cuts ALONE suffice for the Gamma_11 frontier?

R3-C30 established that any proof of Codex's frontier lemma must select the ROTATION from x, since
averaging over rotations is exhausted. That makes the following question the natural next one, and it
is decisive either way.

The R3-C29 family is the m interval cuts A_i = {i, ..., i+k-1} of length exactly k. These are
independent sets, so their monochromatic weight is entirely inside the complementary (2k-1)-interval:
        e(B_i) = sum over edges with both ends in B_i of x_u x_v.
So define  KBOUND(x) = min over the m rotations of e(B_i).  Always ARCBOUND <= KBOUND, since the
length-k intervals are 11 of the 56 arc cuts.

QUESTION: is KBOUND(x) <= (sum x)^2 / 25 for every x >= 0 on Gamma_11?

If YES, Codex's frontier lemma reduces from 56 cuts to ELEVEN, each with a clean description ("the
weight of the edges inside a 7-interval"), and the whole D_22 degree-4 Positivstellensatz could be
re-aimed at a far smaller object. If NO, the extra arc lengths are genuinely needed and that is worth
knowing before more compute goes into the arc family.

Evidence it might hold: at a C5-concentration in Gamma_11 the length-4 interval {0,1,2,3} already
attains exactly 1/25 -- its complement {4,...,10} meets the support in {4,7,10}, which carries the
single monochromatic edge 4-10.

Exhaustive over all integer weightings with sum q, zeros allowed, exact integers throughout.
"""
import sys

import numpy as np


def gamma_k(k):
    m = 3 * k - 1
    E = [(u, v) for u in range(m) for v in range(u + 1, m)
         if min((u - v) % m, (v - u) % m) >= k]
    return m, E


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


for k in (2, 3, 4):
    m, E = gamma_k(k)
    ue = np.array([e[0] for e in E])
    ve = np.array([e[1] for e in E])
    # the m length-k interval cuts
    Mk = np.zeros((m, len(E)), dtype=np.int32)
    for i in range(m):
        S = {(i + t) % m for t in range(k)}
        for j, (u, v) in enumerate(E):
            Mk[i, j] = 1 if ((u in S) == (v in S)) else 0
    MkT = np.ascontiguousarray(Mk.T)
    # all 2^(m-1) cuts, for reference
    nc = 1 << (m - 1)
    Ma = np.zeros((nc, len(E)), dtype=np.int32)
    mm = np.arange(nc, dtype=np.int64)
    Sb = (mm << 1) | 1
    for j, (u, v) in enumerate(E):
        Ma[:, j] = (((Sb >> u) & 1) == ((Sb >> v) & 1)).astype(np.int32)
    MaT = np.ascontiguousarray(Ma.T)

    print(f"\n=== And({k}) = Gamma_{m}: {m} length-{k} interval cuts vs all {nc} cuts ===")
    qs = {2: (6, 8, 10, 12, 15), 3: (6, 8, 10, 12), 4: (8, 10, 12, 14)}[k]
    for q in qs:
        rows = np.fromiter((v for a in compositions(q, m) for v in a), dtype=np.int32)
        P = rows.reshape(-1, m)
        K = P.shape[0]
        kb = np.empty(K, dtype=np.int64)
        ps = np.empty(K, dtype=np.int64)
        CH = 100000
        for s in range(0, K, CH):
            blk = P[s:s + CH]
            pr = (blk[:, ue] * blk[:, ve]).astype(np.int32)
            kb[s:s + CH] = (pr @ MkT).min(axis=1)
            ps[s:s + CH] = (pr @ MaT).min(axis=1)
        bad = np.where(25 * kb > q * q)[0]
        j = int(np.argmax(kb))
        print(f"  q = {q:3d}: {K:8d} weightings;  max 25*KBOUND/q^2 = "
              f"{25 * int(kb[j])}/{q*q} = {25 * kb[j] / (q*q):.6f};  "
              f"violations of KBOUND <= q^2/25: {len(bad)}")
        if len(bad):
            b = int(bad[np.argmax(kb[bad])])
            print(f"      WITNESS a = {P[b].tolist()}: KBOUND = {int(kb[b])}, q^2/25 = "
                  f"{q*q}/25 = {q*q/25:.4f}, but true psi = {int(ps[b])} "
                  f"(psi <= q^2/25: {25 * int(ps[b]) <= q * q})")
        sys.stdout.flush()

print("\nA violation means the length-k intervals alone are NOT enough and the other arc lengths")
print("are genuinely needed. No violation would shrink the frontier lemma from 56 cuts to m.")
