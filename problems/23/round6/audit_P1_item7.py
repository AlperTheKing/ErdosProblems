"""AUDIT of claim C1/C2 of round6/P1.md: item 7 of the chain is FALSE.

Everything recomputed from the definitions by the auditor's own engine (audit_P1_engine.M),
plus:
  * B over ALL closed 1/3-arcs -- BOTH endpoint families ([p,p+1/3] and [p-1/3,p]).
    P1_refutation.py / P1_engine.best_window only slide the LEFT endpoint over atoms, which is
    not obviously exhaustive; this version is.
  * ARCBOUND by two independent enumerations.
  * an isomorphism check of the far-graph against the Wagner graph V8 = C8(1,4).
  * an exhaustive search for OTHER flat item-7 counterexamples (uniform weights on subsets of
    Z_q, q <= 24) -- to decide whether the witness is isolated or an open family.
"""
from fractions import Fraction as F
from itertools import combinations, permutations
from audit_P1_engine import M, TARGET, CE

THIRD = F(1, 3)


def item7_data(mu):
    W, T = mu.W, mu.T
    g = mu.g
    return dict(W=W, T=T, twoT=2 * T, Varg=mu.Varg, Eg2=4 * W ** 2 + mu.Varg,
                A=W - 2 * T, thr=W - TARGET, g=g)


def B_all_third_arcs(mu):
    """min over ALL closed 1/3-arc cuts.  Candidate arcs: [p, p+1/3] and [p-1/3, p] for every
    atom p (the mass of a sliding closed 1/3-window is a sum of indicators of closed intervals
    of length 1/3 in the start coordinate, so its max is attained at such an endpoint)."""
    q = mu.q
    nu = [mu.x[i] * mu.g[i] for i in range(mu.n)]
    starts = []
    for ki in mu.k:
        starts.append(F(ki, q))                 # [p, p+1/3]
        starts.append(F(ki, q) - THIRD)         # [p-1/3, p]
    best = None
    for a in starts:
        v = F(0)
        ins = []
        for i, ki in enumerate(mu.k):
            off = (F(ki, q) - a) % 1
            if off <= THIRD:
                v += nu[i]
                ins.append(i)
        # a closed 1/3-arc must be independent -- verify, else the formula W - nu(I) is wrong
        for p, r in combinations(ins, 2):
            assert not mu.adj[p][r], "closed 1/3-arc carries an edge!"
        if best is None or v > best:
            best = v
    return mu.W - best


def wagner_iso(mu):
    """is the far-graph isomorphic to C8(1,4) (Wagner graph V8)?"""
    n = mu.n
    if n != 8:
        return None
    tgt = [[False] * 8 for _ in range(8)]
    for i in range(8):
        for dd in (1, 4):
            tgt[i][(i + dd) % 8] = tgt[(i + dd) % 8][i] = True
    for p in permutations(range(8)):
        if all(mu.adj[i][j] == tgt[p[i]][p[j]] for i in range(8) for j in range(i + 1, 8)):
            return p
    return False


print("=== the item-7 witness: mu = 1/8 on {0,1,6,7,12,13,14,19}/20 ===")
D = item7_data(CE)
print("  degrees g =", [str(t) for t in D['g']], " (flat:", len(set(D['g'])) == 1, ")")
print(f"  W        = {D['W']} = {float(D['W']):.6f}")
print(f"  T        = {D['T']} = {float(D['T']):.6f}")
print(f"  Var(g)   = {D['Varg']}")
print(f"  hyp (i)   0.12 < W < 0.2                 : {F(3,25) < D['W'] < F(1,5)}")
print(f"  hyp (ii)  2T < W - 1/25 : {D['twoT']} < {D['thr']} : {D['twoT'] < D['thr']}")
print(f"  hyp (iii) 4W^2+Var(g) < W - 1/25 : {D['Eg2']} < {D['thr']} : {D['Eg2'] < D['thr']}")
bs = {k: CE.bound(k) for k in (0, 1, 2, 3, 4, 5, 7, 10, 20, 50, 100, 300)}
print(f"  bound_k for k in {sorted(bs)}: all equal {bs[0]} = {float(bs[0]):.6f}, "
      f"all > 1/25: {all(v > TARGET for v in bs.values())}")
mm = [CE.m(b) for b in range(CE.n)]
harm = 1 / sum(CE.x[i] / mm[i] for i in range(CE.n))
print(f"  min_b m(b) = {min(mm)}   harmonic mean 1/E[1/m] = {harm}")
print(f"  A = W-2T   = {D['A']} = {float(D['A']):.6f}")
Ball = B_all_third_arcs(CE)
print(f"  B over ALL closed 1/3-arcs (both endpoint families) = {Ball} = {float(Ball):.6f}")
arc, arg = CE.arcbound(with_arg=True)
arc2 = CE.arcbound_continuous()
psi = CE.psi()
print(f"  ARCBOUND   = {arc} = {float(arc):.6f}  (second enumeration agrees: {arc == arc2})")
print(f"  psi        = {psi} = {float(psi):.6f}   <= 1/25: {psi <= TARGET}")
print(f"  optimal arc bitmask {bin(arg)} = atoms "
      f"{[CE.k[i] for i in range(CE.n) if (arg >> i) & 1]} /20")
print(f"  far-graph isomorphic to Wagner V8 = C8(1,4): {wagner_iso(CE) is not False}")
print(f"  ITEM 7 REFUTED BY THIS WITNESS: "
      f"{F(3,25) < D['W'] < F(1,5) and D['twoT'] < D['thr'] and D['Eg2'] < D['thr'] and min(bs.values()) > TARGET}")

print()
print("=== is the witness isolated?  exhaustive search over FLAT uniform-weight measures ===")
print("    (uniform weights on a subset S of Z_q, far-graph regular => bound_k = W-4W^2 for all k)")
found = []
for q in range(5, 23):
    thr = q                                  # positions are k/q, all tests done in integers
    for size in range(5, min(q, 10) + 1):
        n2 = size * size
        for S in combinations(range(1, q), size - 1):
            S = (0,) + S                     # fix the rotation: atom 0 always present
            deg = [0] * size
            nE = 0
            sumk = 0
            for a in range(size):
                for b in range(a + 1, size):
                    dk = abs(S[a] - S[b])
                    dk = min(dk, q - dk)
                    if 3 * dk > q:
                        deg[a] += 1
                        deg[b] += 1
                        nE += 1
                        sumk += dk
            if nE == 0 or len(set(deg)) != 1:
                continue                     # flat only
            # W = nE/size^2 in (3/25, 1/5)
            if not (25 * nE > 3 * n2 and 5 * nE < n2):
                continue
            # 2T < W - 1/25   <=>   50*sumk < 25*q*nE - q*n2
            if not (50 * sumk < 25 * q * nE - q * n2):
                continue
            mu = M(q, [(k, 1) for k in S])
            assert mu.bound(0) > TARGET and mu.bound(3) == mu.bound(0)
            found.append((q, S, mu.W, mu.bound(0), mu.arcbound(), mu.psi()))
print(f"    flat counterexamples to item 7 with q <= 22, |S| <= 10, first atom 0: {len(found)}")
seen = set()
for q, S, W, b0, arc, psi in found:
    key = (q, len(S))
    if key in seen:
        continue
    seen.add(key)
    print(f"      q={q:2d} S={list(S)}  W={W}={float(W):.5f}  bound_k={b0}={float(b0):.6f}"
          f"  ARC={float(arc):.6f} psi={float(psi):.6f}"
          f"  psi<=1/25:{psi <= TARGET}")
if found:
    bad = [t for t in found if t[5] > TARGET]
    print(f"    of these, ones whose psi EXCEEDS 1/25 (would refute Erdos 23): {len(bad)}")
