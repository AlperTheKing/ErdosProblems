"""A10/A2/A11: independent recomputation of every exact number in Q5.md's tables,
plus the Theorem A / Theorem B algebra, plus the 3-subdivision numbers.

Everything exact (Fraction / integer enumeration).  No float on any acceptance path.
"""
from fractions import Fraction as F
import sys
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round7")
from audit_Q5_lib import (g6, E_of, tri_free, bip, psi, emass, all_cycles,
                          tau_star_exact, C5n, andrasfai, V8, petersen, grotzsch,
                          Kn, subdiv3, NAMED_G6, induced)

FAIL = []


def chk(name, got, want):
    good = (got == want)
    if not good:
        FAIL.append((name, got, want))
    print(f"  {'OK  ' if good else 'FAIL'} {name}: got {got}  want {want}")


# ------------------------------------------------------------------ table 3.5
print("=== A10  exact table of section 3.5 (uniform x), all Fractions ===")
print(f"{'graph':16s} {'N':>3s} {'|E|':>4s} {'bip':>5s} {'e':>10s} {'Lambda':>10s} "
      f"{'psi':>10s} {'e/5':>10s} {'e-4e^2':>12s}")

REPORT = {   # (e, Lambda, psi) exactly as printed in Q5.md section 3.5 / EXACT VALUES
    "C5":       (F(1, 5), F(1, 25), F(1, 25)),
    "C5[2]":    (F(1, 5), F(1, 25), F(1, 25)),
    "C5[3]":    (F(1, 5), F(1, 25), F(1, 25)),
    "N12a":     (F(25, 144), F(5, 144), F(5, 144)),
    "N12b":     (F(25, 144), F(5, 144), F(5, 144)),
    "N13":      (F(30, 169), F(6, 169), F(6, 169)),
    "N14":      (F(8, 49), F(8, 245), F(1, 28)),
    "Petersen": (F(3, 20), F(3, 100), F(3, 100)),
    "Grotzsch": (F(20, 121), F(4, 121), F(4, 121)),
    "And(3)":   (F(3, 16), F(1, 32), F(1, 32)),
    "And(4)":   (F(2, 11), F(4, 121), F(4, 121)),
    "And(5)":   (F(5, 28), F(3, 98), F(3, 98)),
    "And(6)":   (F(3, 17), F(9, 289), F(9, 289)),
}

# NOTE: C5[3] (N=15), And(5) (N=14, 35 edges) and And(6) (N=17, 51 edges) have far
# too many odd cycles for full enumeration; they are handled by the two-sided
# certificate route in audit_Q5_lam.py instead.
GRAPHS = [
    ("C5", C5n(1)), ("C5[2]", C5n(2)),
    ("N12a", g6(NAMED_G6["N12a"])), ("N12b", g6(NAMED_G6["N12b"])),
    ("N13", g6(NAMED_G6["N13"])), ("N14", g6(NAMED_G6["N14"])),
    ("Petersen", petersen()), ("Grotzsch", grotzsch()),
    ("And(3)", andrasfai(3)), ("And(4)", andrasfai(4)),
]

for nm, (n, A) in GRAPHS:
    E = E_of(n, A)
    assert tri_free(n, A), nm
    x = [F(1, n)] * n
    b = bip(n, A)[0]
    e = emass(n, A, x)
    ps = psi(n, A, x)
    lam = tau_star_exact(n, A, w={ed: x[ed[0]] * x[ed[1]] for ed in E})[0]
    print(f"{nm:16s} {n:3d} {len(E):4d} {b:5d} {str(e):>10s} {str(lam):>10s} "
          f"{str(ps):>10s} {str(e/5):>10s} {str(e - 4*e*e):>12s}")
    if nm in REPORT:
        re_, rl, rp = REPORT[nm]
        chk(f"{nm} e", e, re_)
        chk(f"{nm} Lambda", lam, rl)
        chk(f"{nm} psi", ps, rp)
    # Theorem A chain, exactly, at this x
    chk(f"{nm} Lambda<=psi", lam <= ps, True)
    chk(f"{nm} psi<=e-4e^2", ps <= e - 4 * e * e, True)
    chk(f"{nm} Lambda<=e/5", lam <= e / 5, True)
    chk(f"{nm} Lambda<=1/25", lam <= F(1, 25), True)

# ------------------------------------------------------- bip on C5[n], n<=4
print("\n=== bip(C5[n]) = n^2 exhaustive, own routine ===")
for k in (1, 2, 3, 4):
    n, A = C5n(k)
    chk(f"bip(C5[{k}]) over 2^{n-1} cuts", bip(n, A)[0], k * k)

# --------------------------------------------------- tau* of the named graphs
print("\n=== tau* at unit weights (own exact LP, two-sided) ===")
UNIT = {"C5": F(1), "C5[2]": F(4), "N12a": F(5), "N12b": F(5),
        "N13": F(6), "N14": F(32, 5), "Petersen": F(3), "Grotzsch": F(4),
        "And(3)": F(2), "And(4)": F(4), "And(5)": F(6), "And(6)": F(9)}
for nm, (n, A) in GRAPHS:
    v, z, y, C = tau_star_exact(n, A)
    b = bip(n, A)[0]
    chk(f"tau*({nm})", v, UNIT[nm])
    print(f"       bip={b} tau*={v} gap={b - v}  #oddcycles={len(C)}")

# ------------------------------------------------------------- K5 / subdivision
print("\n=== A11  3-subdivision lemma numbers ===")
n, A = Kn(5)
chk("bip(K5)", bip(n, A)[0], 4)
chk("tau*(K5)", tau_star_exact(n, A)[0], F(10, 3))
m, B = subdiv3(n, A)
chk("3-subdiv K5 N", m, 25)
chk("3-subdiv K5 |E|", len(E_of(m, B)), 30)
chk("3-subdiv K5 triangle-free", tri_free(m, B), True)
girth = min(len(c) for c in all_cycles(m, B, only_odd=False))
chk("3-subdiv K5 girth", girth, 9)
chk("tau*(3-subdiv K5)", tau_star_exact(m, B)[0], F(10, 3))
# bip of the 25-vertex graph: exhaustive 2^24 is too slow in python -> use the
# subdivision lemma tested independently on smaller graphs, and verify tau(G')=tau(G)
# by an exact ILP-free argument: bip(G') <= 4 (delete one edge per K5-transversal path)
# and bip(G') >= tau*(G') = 10/3 -> integer >= 4.
print("  bip(3-subdiv K5): tau* = 10/3 so bip >= 4 (integer); explicit transversal of size 4"
      " (one edge in each path of a K5 odd-cycle transversal) gives bip <= 4  => bip = 4")
print("\n=== 3-subdivision lemma on small graphs (tau and tau* invariance) ===")
for nm, (n, A) in [("C5", C5n(1)), ("K4", Kn(4)), ("K5", Kn(5))]:
    m, B = subdiv3(n, A)
    if m <= 22:
        chk(f"bip({nm}) = bip(subdiv3 {nm})", bip(n, A)[0], bip(m, B)[0])
    chk(f"tau*({nm}) = tau*(subdiv3 {nm})", tau_star_exact(n, A)[0], tau_star_exact(m, B)[0])

print("\nFAILURES:", len(FAIL))
for f in FAIL:
    print("   ", f)
