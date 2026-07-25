"""R8: exact regression gate for every inequality claimed in R8_stability.md.

V1  psi(C5,x) <= 1/25 - D/60 + D^2/576          (D = ||x-u||_1)          [Prop. 1]
V2  psi(C5,x) <= 1/25 - D/72                                              [Prop. 1 cor.]
V3  psi(C7,x) = min_i x_i x_{i+1},  max = 1/49                            [Prop. 6]
V4  psi(C5[y]) = min_i y_i y_{i+1} incl. UNBALANCED and ZERO parts        [Thm B]
V5  D_d psi(u) <= -(1/60) * dist_1(d, FlatCone)                           [Thm C(iv)]
V6  Theorem A over every induced C5 of the whole test suite               [Thm D]
"""
import sys, os, random, itertools
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R8_stability_core import (Graph, C, blowup_C5, blowup_classes, petersen, grotzsch, wagner,
                               circle_graph, K, psi_exact, cut_mono_masks)
from R8_stability_local import C5_point, active_cuts, dir_deriv_bruteforce, formula_deriv
from R8_stability_secondorder import classify_C5, thmA_bound, build_twin_graph

random.seed(31337)
OK = True


def report(tag, ok, extra=""):
    global OK
    OK = OK and ok
    print(f"[{'PASS' if ok else 'FAIL'}] {tag} {extra}")


def V12():
    u = F(1, 5)
    bad1 = bad2 = None
    worst_ratio = None
    for q in (20, 25, 30, 36, 40, 45, 50, 60):
        for a0 in range(q + 1):
            for a1 in range(q - a0 + 1):
                for a2 in range(q - a0 - a1 + 1):
                    for a3 in range(q - a0 - a1 - a2 + 1):
                        a4 = q - a0 - a1 - a2 - a3
                        a = (a0, a1, a2, a3, a4)
                        x = [F(t, q) for t in a]
                        psi = min(x[i] * x[(i + 1) % 5] for i in range(5))
                        D = sum(abs(xi - u) for xi in x)
                        if D == 0:
                            continue
                        if psi > F(1, 25) - D / 60 + D * D / 576:
                            bad1 = (q, a, psi)
                        if psi > F(1, 25) - D / 72:
                            bad2 = (q, a, psi)
                        r = (F(1, 25) - psi) / D
                        if worst_ratio is None or r < worst_ratio[0]:
                            worst_ratio = (r, q, a)
    report("V1  psi(C5,x) <= 1/25 - D/60 + D^2/576  (grids q<=60)", bad1 is None, str(bad1 or ""))
    report("V2  psi(C5,x) <= 1/25 - D/72            (grids q<=60)", bad2 is None, str(bad2 or ""))
    print(f"     smallest observed (1/25-psi)/D over those grids: {worst_ratio[0]} "
          f"= {float(worst_ratio[0]):.8f} at q={worst_ratio[1]} a={worst_ratio[2]}   (inf = 1/60)")


def V3():
    g = C(7)
    cuts = cut_mono_masks(g)
    ok = True
    for _ in range(400):
        raw = [F(random.randint(0, 10), 1) for _ in range(7)]
        s = sum(raw)
        if s == 0:
            continue
        x = [r / s for r in raw]
        v, _ = psi_exact(g, x, cuts)
        if v != min(x[i] * x[(i + 1) % 7] for i in range(7)):
            ok = False
    x = [F(1, 7)] * 7
    v, _ = psi_exact(g, x, cuts)
    report("V3  psi(C7,x) = min_i x_i x_{i+1}; psi(C7,uniform) = 1/49", ok and v == F(1, 49),
           f"psi(C7,unif) = {v}  (= {float(F(25,49)):.4f} x 1/25)")


def V4():
    ok = True
    for sizes in [(2, 2, 2, 2, 2), (3, 1, 2, 2, 1), (2, 0, 2, 2, 2), (1, 1, 1, 1, 1),
                  (3, 1, 1, 1, 1), (2, 2, 1, 1, 2)]:
        g = blowup_C5(list(sizes))
        if g.n == 0:
            continue
        cls = blowup_classes(list(sizes))
        cuts = cut_mono_masks(g)
        for _ in range(150):
            raw = [F(random.randint(0, 8), 1) for _ in range(g.n)]
            s = sum(raw)
            if s == 0:
                continue
            x = [r / s for r in raw]
            y = [sum(x[v] for v in range(g.n) if cls[v] == i) for i in range(5)]
            v, _ = psi_exact(g, x, cuts)
            if v != min(y[i] * y[(i + 1) % 5] for i in range(5)) or v > F(1, 25):
                ok = False
                print("   V4 fail", sizes, x, v)
                break
    report("V4  psi(C5[y]) = min_i y_i y_{i+1} <= 1/25 (unbalanced and zero parts included)", ok)


def dist_to_flatcone(g, cyc, d):
    """||d - dtilde||_1 for the canonical projection dtilde onto the flat cone."""
    _, a, W, Wp = formula_deriv(g, cyc, d)
    return Wp + sum(abs(ai) for ai in a), a, Wp


def V5():
    ok = True
    for g in [petersen(), grotzsch(), wagner(), circle_graph(11), blowup_C5([2, 2, 2, 2, 2]),
              blowup_C5([3, 1, 2, 2, 1]), C(5), build_twin_graph(set()), build_twin_graph({(5, 6)})]:
        cycs = g.induced_C5s()
        if not cycs:
            continue
        cyc = cycs[0]
        x = C5_point(g, cyc)
        cuts = cut_mono_masks(g)
        val, _ = psi_exact(g, x, cuts)
        Cset = set(cyc)
        for _ in range(120):
            d = [F(0)] * g.n
            for v in range(g.n):
                d[v] = F(random.randint(-6, 6), 30) if v in Cset else F(random.randint(0, 6), 30)
            d[cyc[0]] -= sum(d)
            bf = dir_deriv_bruteforce(g, x, d, cuts, val)
            dist, a, Wp = dist_to_flatcone(g, cyc, d)
            if bf > -F(1, 60) * dist:
                ok = False
                print("   V5 fail", g.name, d, bf, -F(1, 60) * dist)
                break
    report("V5  D_d psi(u) <= -(1/60) * dist_1(d, FlatCone)", ok)


def V6():
    ok = ok2 = True
    ncheck = 0
    for g in [C(5), blowup_C5([2, 2, 2, 2, 2]), blowup_C5([3, 1, 2, 2, 1]), blowup_C5([3, 3, 3, 3, 2]),
              petersen(), grotzsch(), wagner(), circle_graph(11), C(7), K(3, 3),
              build_twin_graph(set()), build_twin_graph({(5, 6)})]:
        if g.n > 11:
            continue
        cycs = g.induced_C5s()
        if not cycs:
            continue
        cuts = cut_mono_masks(g)
        for cyc in cycs:
            for trial in range(120):
                x = [F(0)] * g.n
                for v in range(g.n):
                    x[v] = F(random.randint(3, 12), 1) if v in set(cyc) else \
                        F(random.randint(0, [1, 2, 4, 10][trial % 4]), 1)
                s = sum(x)
                x = [xi / s for xi in x]
                val, _ = psi_exact(g, x, cuts)
                bnd, rho, eta = thmA_bound(g, cyc, x)
                ncheck += 1
                if val > bnd:
                    ok = False
                if 25 * eta <= 2 - rho and val > F(1, 25):
                    ok2 = False
                if rho == 0 and val > F(1, 25):
                    ok2 = False
    report(f"V6  Theorem A + corollaries over {ncheck} exact instances", ok and ok2)


if __name__ == "__main__":
    V12(); V3(); V4(); V5(); V6()
    print("\nALL PASS" if OK else "\nSOME CHECK FAILED")
