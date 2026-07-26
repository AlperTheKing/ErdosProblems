"""ROOT-AGENT (Claude): characterise the equality set of the Gamma_11 arc certificate exactly.

claude_equality_set.py found |EQ| = 33, 121, 264 at q = 5, 10, 15, in 3, 9, 16 D_22 orbits, with
EVERY support C5-colourable and of size 5, 6 or 7. The orbit count grows with q, so EQ is infinite --
but the pattern suggests a finite description.

CONJECTURED CHARACTERISATION:
        25 * ARCBOUND(a) = (sum a)^2   <=>   supp(a) is C5-colourable AND some C5-colouring of it
                                             makes all five class sums equal (a BALANCED blow-up).

Why it should hold: if supp(a) is C5-colourable with classes V_1..V_5, Theorem B (gated, R3-C20)
gives psi = min_i y_i y_{i+1} with y_i = a(V_i), so balanced gives psi = q^2/25 exactly.

Why it matters: it turns an INFINITE tight set into FINITELY many linear conditions. For each
C5-colouring phi of an induced subgraph of Gamma_11 the face contains the entire subspace
        { a : supp(a) subset dom(phi),  a(phi^-1(1)) = ... = a(phi^-1(5)) },
so the complete certificate face can be generated from the COLOURINGS rather than from sampled tight
points -- which is what Codex needs, since its current face uses only the 33 pentagon indicators.

Both directions tested exactly. Colourings are precomputed once per subset (2048 subsets) rather
than re-enumerated per weighting.
"""
from itertools import product

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
ue = np.array([e[0] for e in E])
ve = np.array([e[1] for e in E])
Marc = np.zeros((len(arcs), len(E)), dtype=np.int32)
for i, S in enumerate(arcs):
    for k, (u, v) in enumerate(E):
        Marc[i, k] = 1 if ((u in S) == (v in S)) else 0
MarcT = np.ascontiguousarray(Marc.T)

# ---- precompute, once, every C5-colouring of every subset
COL = {}
for mask in range(1, 1 << n):
    sup = [v for v in range(n) if (mask >> v) & 1]
    if len(sup) > 8:
        COL[mask] = []
        continue
    good = []
    for col in product(range(5), repeat=len(sup)):
        c = dict(zip(sup, col))
        ok = True
        for u in sup:
            for v in A[u] & set(sup):
                if u < v and (c[u] - c[v]) % 5 not in (1, 4):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            good.append(tuple(col))
    COL[mask] = good
ncolourable = sum(1 for m in COL if COL[m])
print(f"Gamma_11: subsets of size <= 8 that are C5-colourable: {ncolourable} of {(1 << n) - 1}")


def balanced(a):
    q = sum(a)
    if q % 5:
        return False
    mask = 0
    sup = []
    for v in range(n):
        if a[v] > 0:
            mask |= 1 << v
            sup.append(v)
    for col in COL.get(mask, []):
        cls = [0] * 5
        for idx, v in enumerate(sup):
            cls[col[idx]] += a[v]
        if all(t == q // 5 for t in cls):
            return True
    return False


def compositions(total, parts):
    a = [0] * parts
    a[0] = total
    while True:
        yield a
        if a[parts - 1] == total:
            return
        if a[0] == total:
            pass
        if a[0] > 0:
            a[0] -= 1
            a[1] += 1
        else:
            j = next(i for i in range(1, parts) if a[i] > 0)
            a[0] = a[j] - 1
            a[j] = 0
            a[j + 1] += 1


for q in (5, 10, 15):
    rows = np.fromiter((v for a in compositions(q, n) for v in a), dtype=np.int32)
    P = rows.reshape(-1, n)
    K = P.shape[0]
    ab = np.empty(K, dtype=np.int64)
    CH = 60000
    for s in range(0, K, CH):
        blk = P[s:s + CH]
        pp = (blk[:, ue] * blk[:, ve]).astype(np.int32)
        ab[s:s + CH] = (pp @ MarcT).min(axis=1)
    eq = (25 * ab == q * q)
    bal = np.zeros(K, dtype=bool)
    for j in range(K):
        if P[j].max() * 5 >= 0:
            bal[j] = balanced(P[j].tolist())
    n_eq = int(eq.sum())
    n_bal = int(bal.sum())
    eq_not_bal = int((eq & ~bal).sum())
    bal_not_eq = int((bal & ~eq).sum())
    print(f"q = {q:3d}: |EQ| = {n_eq:5d}   |balanced blow-ups| = {n_bal:5d}   "
          f"EQ but not balanced: {eq_not_bal}   balanced but not EQ: {bal_not_eq}")
    if eq_not_bal:
        j = int(np.where(eq & ~bal)[0][0])
        print(f"      e.g. equality but not balanced: {P[j].tolist()}")
    if bal_not_eq:
        j = int(np.where(bal & ~eq)[0][0])
        print(f"      e.g. balanced but not equality: {P[j].tolist()}, "
              f"25*ARCBOUND = {25*int(ab[j])} vs q^2 = {q*q}")

print("\nIf both mismatch columns are zero, the equality set is EXACTLY the balanced C5-blow-up")
print("weightings, so the certificate face is generated by the C5-colourings of induced subgraphs")
print("of Gamma_11: finitely many linear conditions describing an infinite tight set.")
