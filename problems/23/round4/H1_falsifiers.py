"""H1: isolate and certify the exact falsifiers found by the battery.

(1) 5-block route (sub-target (c)):  uniform Gamma_8 (Wagner graph).
(2) balanced-arc rule (arc of mass closest to 1/2):  random measures.
Everything exact.
"""
import random
import sys
from fractions import Fraction as F
from itertools import combinations

sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round4")
from H1_core import Meas, uniform_gamma, THIRD

ONE25 = F(1, 25)


def fiveblock_detail(M):
    """min over 5 cut points of W+4P0+2P1, with the certificate data."""
    n = M.n
    best = None
    for cuts in combinations(range(n), 5):
        blocks = []
        for i in range(5):
            a, b = cuts[i], cuts[(i + 1) % 5]
            idx = []
            j = a
            while j != b:
                idx.append(j)
                j = (j + 1) % n
            blocks.append(idx)
        P0 = F(0); P1 = F(0); P2 = F(0)
        for i in range(5):
            B = blocks[i]
            for u in range(len(B)):
                for v in range(u + 1, len(B)):
                    if M.adj[B[u]][B[v]]:
                        P0 += M.w[B[u]] * M.w[B[v]]
            for d, P in ((1, 'P1'), (2, 'P2')):
                C = blocks[(i + d) % 5]
                s = F(0)
                for u in B:
                    for v in C:
                        if M.adj[u][v]:
                            s += M.w[u] * M.w[v]
                if d == 1:
                    P1 += s
                else:
                    P2 += s
        assert P0 + P1 + P2 == M.W, (P0, P1, P2, M.W)
        val = M.W + 4 * P0 + 2 * P1
        if best is None or val < best[0]:
            best = (val, cuts, P0, P1, P2)
    return best


def check_fiveblock_by_direct_arc_average(M, cuts):
    """independent recomputation: the 5-block bound is (1/5) * sum of mono over the
    five arcs [c_i, c_{i+2}).  Verify sum_i mono(A_i) = W + 4P0 + 2P1 ... times?"""
    n = M.n
    tot = F(0)
    vals = []
    for i in range(5):
        a = cuts[i]
        b = cuts[(i + 2) % 5]
        mem = [False] * n
        j = a
        while j != b:
            mem[j] = True
            j = (j + 1) % n
        v = M.mono_of(tuple(mem))
        vals.append(v)
        tot += v
    return tot, vals


def main():
    print("=== (1) 5-BLOCK ROUTE FALSIFIER: uniform Gamma_8 (Wagner) ===")
    M = uniform_gamma(8)
    val, cuts, P0, P1, P2 = fiveblock_detail(M)
    ab, args = M.arcbound()
    print("  W        =", M.W, "=", float(M.W))
    print("  ARCBOUND =", ab, "=", float(ab), "  (<= 1/25 OK)")
    print("  min over ALL 5-cut-point choices of W+4P0+2P1 =", val, "=", float(val))
    print("  attained at cuts", cuts, " P0=", P0, "P1=", P1, "P2=", P2)
    print("  => best 5-block bound on mono =", val / 5, "=", float(val / 5),
          " vs 1/25 =", float(ONE25), " EXCEEDS:", val / 5 > ONE25)
    tot, vals = check_fiveblock_by_direct_arc_average(M, cuts)
    print("  independent check: sum of the five arc monos =", tot, "== W+4P0+2P1?", tot == val)
    print("  the five arc mono values:", [str(v) for v in vals])
    # exhaustive: EVERY choice of 5 cut points
    worst = None
    allvals = []
    for c in combinations(range(8), 5):
        blocks = []
        for i in range(5):
            a, b = c[i], c[(i + 1) % 5]
            idx = []
            j = a
            while j != b:
                idx.append(j); j = (j + 1) % 8
            blocks.append(idx)
        t, _ = check_fiveblock_by_direct_arc_average(M, c)
        allvals.append(t)
    print("  min over all C(8,5)=56 cut choices of sum-of-5-monos =", min(allvals),
          "=", float(min(allvals)), "  (must be <= 5/25 = 1/5 to certify)")
    print("  1/5 =", F(1, 5), " -> 5-block route BLOCKED on Gamma_8:", min(allvals) > F(1, 5))

    print()
    print("=== same test on the other uniform Gamma_m that fail ===")
    for m in (11, 14, 17, 23):
        Mm = uniform_gamma(m)
        v, c, p0, p1, p2 = fiveblock_detail(Mm)
        print(f"  Gamma_{m}: W={Mm.W} min(W+4P0+2P1)={v}={float(v):.6f}  bound={float(v/5):.6f} > 1/25:{v/5>ONE25}"
              f"   ARCBOUND={Mm.arcbound()[0]}")

    print()
    print("=== (2) BALANCED-ARC RULE FALSIFIERS ===")
    random.seed(20260725)
    found = 0
    for t in range(200):
        n = random.randint(3, 11)
        den = random.choice([30, 36, 42, 60, 72, 90, 105, 120])
        pts = random.sample(range(den), n)
        pos = [F(p, den) for p in pts]
        w = [F(random.randint(1, 9)) for _ in range(n)]
        Mr = Meas(pos, w)
        bvals = []
        for lo, hi in Mr.balanced_arcs():
            bvals.append(Mr.mono_of(Mr.arc_mem(*lo)))
            if hi is not None:
                bvals.append(Mr.mono_of(Mr.arc_mem(*hi)))
        bmin = min(bvals)
        if bmin > Mr.W * Mr.W:
            found += 1
            ab, _ = Mr.arcbound()
            print(f"  #{t}: pos={[str(x) for x in Mr.pos]}")
            print(f"       w  ={[str(x) for x in Mr.w]}")
            print(f"       W={Mr.W} W^2={Mr.W*Mr.W}={float(Mr.W*Mr.W):.6f}"
                  f"  balanced-min={bmin}={float(bmin):.6f}  true ARCBOUND={ab}={float(ab):.6f}")
    print("  total balanced-arc falsifiers:", found)


if __name__ == "__main__":
    main()
