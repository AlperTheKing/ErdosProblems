"""ROOT-AGENT GATE (Claude): test Codex's R10 FRONTIER LEMMA before it spends more compute on it.

Codex's Round 10 direct route claims an unconditional band-shrinking theorem
        bip(G) <= N^2/25  for every triangle-free G with delta(G) > 5N/14,
resting on ONE missing item: the frontier lemma

        ARCBOUND_{Gamma_11}(x)  <=  (sum x)^2 / 25   for every nonnegative weighting x,

where ARCBOUND is the minimum of the monochromatic weight over the CYCLIC-INTERVAL cuts only. Since
every arc is a cut, ARCBOUND >= psi, so the lemma implies max_x psi(Gamma_11) <= 1/25 -- and it is
strictly stronger than that, because it restricts the cut family. That is exactly what makes it worth
falsifying first: a restricted-family bound is far easier to break than psi itself.

If some integer weighting has 25 * ARCBOUND(x) > (sum x)^2, the R10 route dies at its only open step
and Codex should stop the D_22-invariant degree-4 Positivstellensatz immediately.

Exhaustive over ALL integer weightings with sum = q, ZERO ENTRIES ALLOWED (mandatory here: a previous
engine in this campaign forbade zeros and produced retracted tables). Exact integer arithmetic
throughout -- 25 * ARCBOUND and q^2 are both integers, so the comparison is exact.
"""
import sys

import numpy as np


def gamma_g(m):
    return m, [(u, v) for u in range(m) for v in range(u + 1, m)
               if 3 * min((u - v) % m, (v - u) % m) > m]


def arc_cuts(n):
    """every cyclic interval, deduplicated by complementation; plus the trivial all-on-one-side cut"""
    seen = {}
    for s in range(n):
        for L in range(1, n):
            S = frozenset((s + t) % n for t in range(L))
            key = min(tuple(sorted(S)), tuple(sorted(set(range(n)) - S)))
            seen[key] = S
    out = [frozenset()] + list(seen.values())
    return out


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


n, E = gamma_g(11)
arcs = arc_cuts(n)
ue = np.array([e[0] for e in E])
ve = np.array([e[1] for e in E])
Marc = np.zeros((len(arcs), len(E)), dtype=np.int32)
for i, S in enumerate(arcs):
    for k, (u, v) in enumerate(E):
        Marc[i, k] = 1 if ((u in S) == (v in S)) else 0
MarcT = np.ascontiguousarray(Marc.T)

ncuts = 1 << (n - 1)
Mall = np.zeros((ncuts, len(E)), dtype=np.int32)
mm = np.arange(ncuts, dtype=np.int64)
Sb = (mm << 1) | 1
for k, (u, v) in enumerate(E):
    Mall[:, k] = (((Sb >> u) & 1) == ((Sb >> v) & 1)).astype(np.int32)
MallT = np.ascontiguousarray(Mall.T)

print(f"Gamma_11 = And(4): |E| = {len(E)}, arc cuts = {len(arcs)}, all cuts = {ncuts}")
print(f"mandatory sanity: a C5-concentration must give psi = 1/25 exactly")
c5 = [0, 3, 7, 10, 4]
a0 = np.zeros((1, n), dtype=np.int32)
for v in c5:
    a0[0, v] = 1
p0 = (a0[:, ue] * a0[:, ve]).astype(np.int32)
print(f"  x = 1/5 on the induced C5 {c5}: 25*psi = {25 * int((p0 @ MallT).min())}, "
      f"q^2 = {25}  -> equality: {25 * int((p0 @ MallT).min()) == 25}")

print(f"\n{'q':>4s} {'weightings':>12s} {'max 25*ARCBOUND/q^2':>22s} {'max 25*psi/q^2':>17s} "
      f"{'ARC violations':>15s}")
worst = None
for q in (8, 10, 12, 14):
    rows = np.fromiter((v for a in compositions(q, n) for v in a), dtype=np.int32)
    P = rows.reshape(-1, n)
    K = P.shape[0]
    CH = 100000
    best_arc = np.empty(K, dtype=np.int64)
    best_all = np.empty(K, dtype=np.int64)
    for s in range(0, K, CH):
        blk = P[s:s + CH]
        prod = (blk[:, ue] * blk[:, ve]).astype(np.int32)
        best_arc[s:s + CH] = (prod @ MarcT).min(axis=1)
        best_all[s:s + CH] = (prod @ MallT).min(axis=1)
    viol = np.where(25 * best_arc > q * q)[0]
    ia = int(np.argmax(best_arc))
    ip = int(np.argmax(best_all))
    if len(viol):
        j = int(viol[np.argmax(best_arc[viol])])
        if worst is None or 25 * int(best_arc[j]) - q * q > worst[0]:
            worst = (25 * int(best_arc[j]) - q * q, q, P[j].tolist(), int(best_arc[j]))
    print(f"{q:4d} {K:12d} {f'{25 * int(best_arc[ia])}/{q*q} = {25 * best_arc[ia] / (q*q):.6f}':>22s} "
          f"{f'{25 * best_all[ip] / (q*q):.6f}':>17s} {len(viol):15d}")
    sys.stdout.flush()

print()
if worst:
    excess, q, a, ab = worst
    print(f"*** FRONTIER LEMMA FALSIFIED: q = {q}, a = {a}")
    print(f"    ARCBOUND = {ab}/{q*q}, and 25*{ab} = {25*ab} > {q*q} = q^2 (excess {excess})")
    print(f"    -> Codex's R10 route dies at its only open step; stop the degree-4 SDP.")
else:
    print("no violation of the frontier lemma at these grids: the R10 route survives this test,")
    print("and the lemma remains the single open item. Note this is a finite check, so it can only")
    print("ever FALSIFY -- it is not a proof of the lemma.")
