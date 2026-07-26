"""ROOT-AGENT (Claude): on Gamma_11, is the optimal odd-cycle PACKING always supported on PENTAGONS?

A5b showed psi = Lambda at 10000 top-psi product weightings on Gamma_11, with exact packing
certificates and no gaps. If the packing can moreover always be taken on the 33 induced C5s alone,
then for product weights
        psi(Gamma_11,x) = Lambda_pent(Gamma_11,x) := max { sum_C z_C : sum_{C ∋ e} z_C <= x_u x_v },
a finite LP in 33 variables and 22 constraints. That would reduce Codex's frontier lemma to
        max over x on the simplex of Lambda_pent(Gamma_11,x)  <=  1/25,
a bilinear problem over an explicit 33-variable polytope -- no SDP, no cut family.

IMPORTANT: this is a PACKING family, not a cut family, so the rainbow-1 obstruction that killed every
fixed-CUT-family certificate (R3-C21) does not apply to it. The obstruction is about aggregating cut
values; this is the dual side.

Three quantities per weighting, all exact where it counts:
        psi          = integer min over all 1024 cuts,
        Lambda       = LP over all 596 odd cycles,
        Lambda_pent  = LP over the 33 induced pentagons only.
Always Lambda_pent <= Lambda <= psi. The question is whether the first inequality is ever strict.
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
pent = [c for c in odd if len(c) == 5]
print(f"Gamma_11: odd cycles {len(odd)}, induced pentagons {len(pent)}")

Aall = np.zeros((len(E), len(odd)))
for k, c in enumerate(odd):
    for i in c:
        Aall[i, k] = 1.0
Apen = np.zeros((len(E), len(pent)))
for k, c in enumerate(pent):
    for i in c:
        Apen[i, k] = 1.0


def pack(Amat, ncol, a):
    w = np.array([float(a[u] * a[v]) for (u, v) in E])
    r = linprog(-np.ones(ncol), A_ub=Amat, b_ub=w, bounds=[(0, None)] * ncol, method='highs')
    return (-r.fun, r.x) if r.success else (None, None)


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


TOP = 1500
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
    strict, cert_pent, examined = 0, 0, 0
    worst = None
    for j in order:
        a = P[j].tolist()
        ps = int(psi[j])
        if ps == 0:
            continue
        examined += 1
        lp, zp = pack(Apen, len(pent), a)
        if lp is None:
            continue
        if lp < ps - 1e-6:
            strict += 1
            if worst is None or ps - lp > worst[0]:
                worst = (ps - lp, ps, lp, a)
        else:
            w = [F(int(a[u]) * int(a[v])) for (u, v) in E]
            for D in (1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 24, 30, 60):
                zz = [F(int(round(t * D)), D) for t in zp]
                if any(t < 0 for t in zz) or sum(zz) != ps:
                    continue
                load = [sum(zz[k] for k, c in enumerate(pent) if i in c) for i in range(len(E))]
                if all(load[i] <= w[i] for i in range(len(E))):
                    cert_pent += 1
                    break
    print(f"q = {q:3d}: examined {examined:5d} top-psi weightings;  "
          f"Lambda_pent < psi in {strict:5d};  exact pentagon-packing certificates: {cert_pent}")
    if worst:
        print(f"    largest shortfall: psi = {worst[1]}, Lambda_pent ~ {worst[2]:.4f}, a = {worst[3]}")
    sys.stdout.flush()

print("\nIf Lambda_pent = psi always, the frontier lemma reduces to a 33-variable bilinear problem.")
print("If Lambda_pent < psi somewhere, pentagons alone do not suffice and the longer odd cycles")
print("are genuinely needed -- which is itself worth knowing before anyone builds on pentagons.")
