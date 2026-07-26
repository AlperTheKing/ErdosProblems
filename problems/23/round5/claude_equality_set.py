"""ROOT-AGENT (Claude): enumerate the FULL equality set of the Gamma_11 arc certificate.

R3-C34 showed Codex's face is incomplete: it is built from the 33 pentagon indicators 1_C, but the
arc certificate is also TIGHT at blow-up weightings such as a = (2,1,1,0,2,0,1,1,2,0,0). The correct
face is cut out by the whole equality set

        EQ = { a integer >= 0 : 25 * ARCBOUND(a) = (sum a)^2 },

since T(a) = 0 at every such point, forcing nu_S(a) = 0 for every non-tight cut S and giving a Gram
kernel vector in each parity block. This enumerates EQ so the face can be built from all of it.

ARITHMETIC OBSERVATION that makes the enumeration cheap: equality needs 25 | q^2, hence 5 | q. So EQ
lives only on grids with q divisible by 5, and every other grid can be skipped outright.

Reported per grid: the size of EQ, its D_22 orbits, the support sizes, whether each support is
C5-colourable, and how many of the 56 arc cuts are tight -- the last being exactly the number of
multiplier orbits NOT forced to zero at that point.
"""
import sys
from itertools import combinations

import numpy as np


def gamma_g(m):
    return m, [(u, v) for u in range(m) for v in range(u + 1, m)
               if 3 * min((u - v) % m, (v - u) % m) > m]


def arc_cuts(n):
    seen = {}
    for s in range(n):
        for L in range(1, n):
            S = frozenset((s + t) % n for t in range(L))
            key = min(tuple(sorted(S)), tuple(sorted(set(range(n)) - S)))
            seen[key] = S
    return [frozenset()] + list(seen.values())


n, E = gamma_g(11)
A = [set() for _ in range(n)]
for u, v in E:
    A[u].add(v)
    A[v].add(u)
arcs = arc_cuts(n)
pent = {frozenset(T) for T in combinations(range(n), 5)
        if all(len(A[v] & set(T)) == 2 for v in T)}
ue = np.array([e[0] for e in E])
ve = np.array([e[1] for e in E])
Marc = np.zeros((len(arcs), len(E)), dtype=np.int32)
for i, S in enumerate(arcs):
    for k, (u, v) in enumerate(E):
        Marc[i, k] = 1 if ((u in S) == (v in S)) else 0
MarcT = np.ascontiguousarray(Marc.T)


def c5_colourable(sup):
    sup = sorted(sup)
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


def orbit(a):
    out = set()
    t = tuple(a)
    for k in range(n):
        out.add(tuple(t[(i - k) % n] for i in range(n)))
        out.add(tuple(t[(-i - k) % n] for i in range(n)))
    return frozenset(out)


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


print(f"Gamma_11: {len(arcs)} arc cuts, {len(pent)} induced pentagons")
print("equality 25*ARCBOUND = q^2 requires 5 | q, so only those grids are scanned\n")
for q in (5, 10, 15):
    rows = np.fromiter((v for a in compositions(q, n) for v in a), dtype=np.int32)
    P = rows.reshape(-1, n)
    K = P.shape[0]
    ab = np.empty(K, dtype=np.int64)
    CH = 100000
    for s in range(0, K, CH):
        blk = P[s:s + CH]
        pr = (blk[:, ue] * blk[:, ve]).astype(np.int32)
        ab[s:s + CH] = (pr @ MarcT).min(axis=1)
    hit = np.where(25 * ab == q * q)[0]
    seen, orbs = set(), []
    for j in hit:
        t = tuple(P[j].tolist())
        if t in seen:
            continue
        o = orbit(t)
        seen |= o
        orbs.append(t)
    print(f"q = {q:3d}: {K:9d} weightings, |EQ| = {len(hit):5d}, D_22 orbits = {len(orbs)}")
    for t in orbs:
        a = list(t)
        sup = frozenset(v for v in range(n) if a[v] > 0)
        pr = (np.array([a])[:, ue] * np.array([a])[:, ve]).astype(np.int32)
        vals = (pr @ MarcT)[0]
        tight = int((vals == vals.min()).sum())
        kind = ("pentagon indicator" if (sup in pent and max(a) == 1)
                else ("C5-colourable support" if c5_colourable(sup) else "NOT C5-colourable"))
        print(f"      {a}  support {sorted(sup)} (size {len(sup)}), tight arc cuts {tight}/56, "
              f"{kind}")
    sys.stdout.flush()

print("\nEvery point above forces nu_S = 0 for each NON-tight cut S and contributes a Gram kernel")
print("vector in every parity block. A face built from the 33 pentagon indicators alone omits the")
print("orbits whose support is larger than 5 -- those are the ones Codex is missing.")
