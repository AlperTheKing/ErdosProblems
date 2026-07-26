"""ROOT-AGENT (Claude): extract the equality cases on Gamma_11 that Theorem F does NOT settle.

claude_thmF_residual.py found that at q = 10 the maximum of 25*psi/q^2 over the region Theorem F
leaves open is exactly 1 -- i.e. some weighting attains psi = 1/25 EXACTLY while having
x(C) < 21/25 for every one of the 33 induced pentagons, so Theorem F's hypothesis fails at every
pentagon simultaneously.

That kills a branch-and-bound closure (no margin off the settled region), and it says something
sharper: the EQUALITY SET of the conjecture on Gamma_11 is strictly larger than the 33
C5-concentrations. Whatever these extra extremal weightings are, an exactness ball centred on
pentagons cannot reach them. This prints them, with their support structure, so the shape of the
missing cases is on the record rather than inferred.
"""
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


q = 10
rows = np.fromiter((v for a in compositions(q, n) for v in a), dtype=np.int32)
P = rows.reshape(-1, n)
psi = np.empty(P.shape[0], dtype=np.int64)
CH = 100000
for s in range(0, P.shape[0], CH):
    blk = P[s:s + CH]
    pr = (blk[:, ue] * blk[:, ve]).astype(np.int32)
    psi[s:s + CH] = (pr @ MT).min(axis=1)
maxpc = (P @ PENT.T).max(axis=1)
hit = np.where((25 * psi == q * q) & (25 * maxpc.astype(np.int64) < 21 * q))[0]
print(f"q = {q}: weightings with psi EXACTLY q^2/25 and every pentagon under 21/25 of the mass: "
      f"{len(hit)}")
seen = set()
shown = 0
for j in hit:
    a = P[j].tolist()
    sup = tuple(v for v in range(n) if a[v] > 0)
    key = (tuple(sorted(a)), len(sup))
    if key in seen:
        continue
    seen.add(key)
    col = c5_colourable(set(sup))
    heaviest = int(maxpc[j])
    print(f"  a = {a}  support size {len(sup)} = {sup}")
    print(f"      psi = {F(int(psi[j]), q*q)} = 1/25 exactly;  heaviest pentagon carries "
          f"{heaviest}/{q};  support C5-colourable: {col}")
    shown += 1
    if shown >= 6:
        break
print("\nThese are equality cases of the conjecture on Gamma_11 that Theorem F cannot see:")
print("its hypothesis eta(C) <= 4/25 fails at EVERY induced pentagon simultaneously, yet psi = 1/25.")
print("An exactness ball centred on pentagons therefore cannot cover the extremal set; the balls")
print("would have to be centred on C5-BLOW-UP weightings inside Gamma_11.")
