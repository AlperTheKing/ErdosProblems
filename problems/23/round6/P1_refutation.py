"""SELF-CONTAINED refutation of item 7 (and of every bound built from 1/3-arcs alone).

THE WITNESS   mu = uniform weight 1/8 on the eight points
              {0, 1, 6, 7, 12, 13, 14, 19} / 20   of the circle R/Z.

Everything below is recomputed from the definitions with Fractions and no imports from the
rest of round6, so that it can be audited on its own.
"""
from fractions import Fraction as F
from itertools import combinations

POS = [F(k, 20) for k in (0, 1, 6, 7, 12, 13, 14, 19)]
X = [F(1, 8)] * 8
n = 8
THIRD, HALF, TARGET = F(1, 3), F(1, 2), F(1, 25)


def d(p, q):
    t = abs(p - q) % 1
    return min(t, 1 - t)


adj = [[i != j and d(POS[i], POS[j]) > THIRD for j in range(n)] for i in range(n)]
E = [(i, j, d(POS[i], POS[j])) for i, j in combinations(range(n), 2) if adj[i][j]]

g = [sum(X[j] for j in range(n) if adj[i][j]) for i in range(n)]
W = sum(X[i] * X[j] for i, j, _ in E)
T = sum(X[i] * X[j] * dd for i, j, dd in E)
Eg2 = sum(X[i] * g[i] ** 2 for i in range(n))
Varg = Eg2 - 4 * W ** 2
m = [W - sum(X[j] * g[j] for j in range(n) if adj[i][j]) for i in range(n)]


def bound(k):
    return (sum(X[i] * g[i] ** k * m[i] for i in range(n))
            / sum(X[i] * g[i] ** k for i in range(n)))


print("WITNESS: weight 1/8 at {0,1,6,7,12,13,14,19}/20   (Wagner graph V8, unequal spacing)")
print(f"  |E| = {len(E)} edges, degrees g = {[str(x) for x in g]}  (3-regular: g == 3/8)")
print(f"  W        = {W} = {float(W):.6f}")
print(f"  T        = {T} = {float(T):.6f}")
print(f"  Var(g)   = {Varg}")
print()
print("HYPOTHESES OF ITEM 7")
print(f"  (i)   W in (0.12, 0.2)                : {float(W):.6f}          -> "
      f"{F(3,25) < W < F(1,5)}")
print(f"  (ii)  2T < W - 1/25                   : {2*T} < {W - TARGET}   -> {2*T < W - TARGET}")
print(f"  (iii) 4W^2 + Var(g) < W - 1/25        : {4*W**2 + Varg} < {W - TARGET}   -> "
      f"{4*W**2 + Varg < W - TARGET}")
print()
print("CONCLUSION OF ITEM 7 (some bound_k <= 1/25) -- FAILS:")
print(f"  m(b) = {m[0]} for EVERY b  (g is constant, so m = W - g*g is constant)")
for k in (0, 1, 2, 3, 5, 10, 50, 200):
    b = bound(k)
    print(f"  bound_{k:<3d} = {b} = {float(b):.6f}   > 1/25 = 0.04 : {b > TARGET}")
print()
print("also killed by the same witness (each is an average/min of the SAME constant m):")
print(f"  min_b m(b)              = {min(m)} = {float(min(m)):.6f}")
print(f"  harmonic mean 1/E[1/m]  = {1/sum(X[i]/m[i] for i in range(n))} "
      f"= {float(1/sum(X[i]/m[i] for i in range(n))):.6f}")
print(f"  A = W - 2T (half-arcs)  = {W - 2*T} = {float(W-2*T):.6f}")
best13 = max(sum(X[j] * g[j] for j in range(n) if (POS[j] - POS[i]) % 1 <= THIRD)
             for i in range(n))
print(f"  B = min over ALL 1/3-arcs= {W - best13} = {float(W-best13):.6f}")
print()

# ---- ground truth: the conjecture itself is NOT violated ---------------------------------
best, arg = None, None
for i in range(n):
    inI = [False] * n
    for L in range(n + 1):
        if L:
            inI[(i + L - 1) % n] = True
        v = sum(X[a] * X[b] for a, b, _ in E if inI[a] == inI[b])
        if best is None or v < best:
            best, arg = v, (i, L)
print(f"ARCBOUND (min over all arc cuts) = {best} = {float(best):.6f} <= 1/25   "
      f"[arc = {arg[1]} consecutive atoms starting at index {arg[0]}]")
allcuts = None
for mask in range(1 << (n - 1)):
    S = [(mask >> i) & 1 for i in range(n - 1)] + [0]
    v = sum(X[a] * X[b] for a, b, _ in E if S[a] == S[b])
    allcuts = v if allcuts is None or v < allcuts else allcuts
print(f"psi (min over ALL 2^7 cuts)      = {allcuts} = {float(allcuts):.6f} <= 1/25   "
      f"(so the conjecture is untouched; only the CERTIFICATE family is refuted)")
print()
print("WHY: the optimal cut is an arc of 4 atoms spanning length 7/20 > 1/3, with one edge")
print("inside each side.  It is neither a 1/3-arc (bound_k, B) nor caught by the uniform")
print("average over half-arcs (A).  The arc-cut LENGTH parameter cannot be fixed.")
print()
gaps = sorted({d(POS[i], POS[j]) for i in range(n) for j in range(i + 1, n)})
print("ROBUSTNESS: the pairwise distances are", [str(g_) for g_ in gaps])
print("none equals 1/3, so the witness does not depend on the strict/non-strict convention,")
print("and it survives any perturbation of the eight positions smaller than",
      f"{float(min(abs(g_ - THIRD) for g_ in gaps)) / 2:.5f}.")
