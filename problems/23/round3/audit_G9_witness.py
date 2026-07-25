"""audit_G9_witness.py -- independent re-derivation of every W_t number in G9.md,
plus the TRUE set-deletion drop (not the greedy cost) for every part-wise S.

Run: python audit_G9_witness.py
"""
from fractions import Fraction
from itertools import product
from functools import lru_cache
import sys

sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round3")
from audit_G9_core import (C5, blowup_bip_exact, build_blowup, bip_exhaustive,
                           triangle_free, maximal_triangle_free, deg_list,
                           edge_list, delete_set)

OK = True


def chk(cond, msg):
    global OK
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond:
        OK = False


# ---------------------------------------------------------------- 0. calibrate
print("=== 0. calibrate blow-up bip against explicit brute force ===")
for a in [(1, 1, 1, 1, 1), (2, 2, 2, 2, 2), (3, 2, 1, 2, 3), (1, 3, 2, 2, 1),
          (2, 1, 3, 1, 2), (0, 2, 3, 1, 2), (4, 1, 1, 1, 1), (3, 3, 1, 1, 3)]:
    f = blowup_bip_exact(5, C5, a)
    n, M, off, part = build_blowup(5, C5, a)
    b = bip_exhaustive(n, M) if n <= 20 else None
    mini = min(a[i] * a[(i + 1) % 5] for i in range(5))
    chk(f == b and f == mini,
        "a=%s  cutformula=%s  explicit=%s  min_i a_i a_{i+1}=%s" % (a, f, b, mini))

print()
print("=== 1. W_t data (independent) ===")
for t in range(1, 9):
    a = [7 * t, 2 * t, 7 * t, 7 * t, 2 * t]
    N = sum(a)
    m = sum(a[u] * a[v] for u, v in C5)
    deg = [a[(i - 1) % 5] + a[(i + 1) % 5] for i in range(5)]
    delta = min(deg)
    b = blowup_bip_exact(5, C5, a)
    drops = []
    for i in range(5):
        a2 = list(a); a2[i] -= 1
        drops.append(b - blowup_bip_exact(5, C5, a2))
    bud = Fraction(2 * N - 1, 25)
    print("t=%d N=%d m=%d deg=%s delta=%d bip=%d N^2/25=%s drops=%s min=%d budget=%s"
          % (t, N, m, deg, delta, b, Fraction(N * N, 25), drops, min(drops), bud))
    chk(N == 25 * t and m == 105 * t * t, "N=25t, m=105t^2")
    chk(deg == [4 * t, 14 * t, 9 * t, 9 * t, 14 * t], "degrees (4t,14t,9t,9t,14t)")
    chk(25 * delta == 4 * N, "delta = 4N/25 exactly")
    chk(b == 14 * t * t, "bip(W_t) = 14 t^2")
    chk(drops == [2 * t, 7 * t, 2 * t, 2 * t, 7 * t], "drops (2t,7t,2t,2t,7t)")
    chk(min(drops) == delta // 2, "min drop = floor(delta/2) = 2t")
    chk(Fraction(min(drops)) > bud, "min drop > (2N-1)/25  (single-vertex defeated)")
    chk(25 * b < N * N, "bip(W_t) < N^2/25  (W_t is NOT a counterexample)")

print()
print("=== 2. W_1 explicit graph: triangle-free / maximal / degrees ===")
a = [7, 2, 7, 7, 2]
n, M, off, part = build_blowup(5, C5, a)
chk(n == 25, "N=25")
chk(triangle_free(n, M), "triangle-free")
chk(maximal_triangle_free(n, M), "MAXIMAL triangle-free")
d = deg_list(n, M)
chk(len(edge_list(n, M)) == 105, "m=105")
chk(min(d) == 4 and sorted(set(d)) == [4, 9, 14], "degree set {4,9,14}, delta=4")

print()
print("=== 3. TRUE set-deletion drop for every part-wise S in W_t (t=1,2,3) ===")
print("    budget(s) = (N^2-(N-s)^2)/25 = (2Ns-s^2)/25 ;  FIRES iff true drop <= budget")


def exact_cost_dp(a, s):
    """greedy re-insertion cost: min over orderings of sum floor(backdeg/2).
    Independent re-implementation (iterative over states, part-wise)."""
    a = tuple(a); s = tuple(s)
    out = tuple(a[i] - s[i] for i in range(5))

    @lru_cache(maxsize=None)
    def f(c):
        if c == s:
            return 0
        best = None
        for i in range(5):
            if c[i] < s[i]:
                b = out[(i - 1) % 5] + c[(i - 1) % 5] + out[(i + 1) % 5] + c[(i + 1) % 5]
                nc = list(c); nc[i] += 1
                val = b // 2 + f(tuple(nc))
                if best is None or val < best:
                    best = val
        return best
    return f((0, 0, 0, 0, 0))


for t in (1, 2, 3):
    a = [7 * t, 2 * t, 7 * t, 7 * t, 2 * t]
    N = sum(a)
    b = blowup_bip_exact(5, C5, a)
    fire_true, fire_cost, worst_true = [], [], None
    for s in product(*[range(x + 1) for x in a]):
        ssz = sum(s)
        if ssz == 0:
            continue
        rest = [a[i] - s[i] for i in range(5)]
        drop = b - blowup_bip_exact(5, C5, rest)
        bud = Fraction(2 * N * ssz - ssz * ssz, 25)
        if drop <= bud:
            fire_true.append((s, ssz, drop, bud))
        if worst_true is None or Fraction(drop) - bud < worst_true[0]:
            worst_true = (Fraction(drop) - bud, s, ssz, drop, bud)
    print("t=%d: TRUE-drop mechanism fires on %d of the %d nonempty part-wise S"
          % (t, len(fire_true), -1 + len(list(product(*[range(x + 1) for x in a])))))
    if fire_true:
        fire_true.sort(key=lambda z: z[2] - z[3])
        for z in fire_true[:6]:
            print("    FIRES  s=%s |S|=%d  true drop=%d  budget=%s = %.4f"
                  % (z[0], z[1], z[2], z[3], float(z[3])))
    print("    most negative (drop-budget): %s at s=%s" % (worst_true[0], worst_true[1]))
    # Theorem E literal statement: greedy cost(S) > budget for every S
    viol = []
    for s in product(*[range(x + 1) for x in a]):
        ssz = sum(s)
        if ssz == 0:
            continue
        rest = [a[i] - s[i] for i in range(5)]
        ES = sum(a[u] * a[v] for u, v in C5) - sum(rest[u] * rest[v] for u, v in C5)
        crude = Fraction(ES - ssz, 2)
        bud = Fraction(2 * N * ssz - ssz * ssz, 25)
        if crude <= bud:                       # crude insufficient -> exact DP
            c = exact_cost_dp(a, s)
            if Fraction(c) <= bud:
                viol.append((s, ssz, c, bud))
    print("    Theorem E literal (greedy cost(S) > budget for all S): violations = %d"
          % len(viol))
    chk(len(viol) == 0, "t=%d: greedy-cost form of Theorem E holds" % t)

print()
print("=== 4. explicit falsifier for 'arbitrary-set deletion is defeated' ===")
for t in (1, 2, 3, 4):
    a = [7 * t, 2 * t, 7 * t, 7 * t, 2 * t]
    N = sum(a)
    b = blowup_bip_exact(5, C5, a)
    rest = [7 * t, 2 * t, 0, 0, 2 * t]          # S = P_2 u P_3
    s = 14 * t
    b2 = blowup_bip_exact(5, C5, rest)
    bud = Fraction(2 * N * s - s * s, 25)
    print("t=%d  S=P2 u P3  |S|=%d  bip(W_t)=%d  bip(W_t-S)=%d  drop=%d  budget=%s=%.4f  FIRES=%s"
          % (t, s, b, b2, b - b2, bud, float(bud), b - b2 <= bud))
    chk(b - b2 <= bud, "t=%d: set-deletion step SUCCEEDS at S=P2 u P3" % t)
    # and greedy cost is far above
    ES = sum(a[u] * a[v] for u, v in C5) - sum(rest[u] * rest[v] for u, v in C5)
    print("      greedy cost lower bound (E(S)-s)/2 = %s ; exact greedy cost = %s"
          % (Fraction(ES - s, 2), exact_cost_dp(a, [0, 0, 7 * t, 7 * t, 0])))

# double-check with the fully explicit 11-vertex graph for t=1
n, M, off, part = build_blowup(5, C5, [7, 2, 7, 7, 2])
S = [v for v in range(n) if part[v] in (2, 3)]
n2, M2 = delete_set(n, M, S)
print("  explicit W_1 - (P2 u P3): N'=%d  bip=%d" % (n2, bip_exhaustive(n2, M2)))
chk(n2 == 11 and bip_exhaustive(n2, M2) == 0, "explicit bip(W_1 - P2 - P3) = 0")

print()
print("ALL CHECKS PASSED" if OK else "SOME CHECKS FAILED")
