"""R8: an EXACT spurious (non-global) local maximum of psi on the Petersen graph.

x* = (1/8, 1/8, 1/8, 0, 1/8, 0, 1/4, 1/8, 0, 1/8)   (Petersen labelled: outer 0-1-2-3-4-0,
spokes i ~ i+5, inner 5-7-9-6-8-5).   psi(Petersen, x*) = 1/32 EXACTLY, while
Psi(Petersen) = 1/25 (attained only at the 12 C5-concentrations).

Certificates produced here:
  (a) psi(x*) = 1/32 exactly;
  (b) x* is a FIRST-ORDER local maximum: the LP  max t s.t. <grad q_S(x*),d> >= t over all
      ACTIVE cuts, sum d = 0, d_v >= 0 where x*_v = 0, has optimum t* = 0 (rigorous: no
      direction of ascent exists);
  (c) no improvement among ALL grid points within 2 unit transfers at q = 40, 200, 1000,
      nor among 6000 random exact rational perturbations;
  (d) the L1 distance from x* to the nearest global maximiser is 3/5 -- it is not a boundary
      effect of a nearby extremal point;
  (e) the support of x* induces the theta-graph Theta(2,3,3), whose two odd cycles (both C5s)
      share the length-2 path; the cheapest odd-cycle transversal is one edge of that path,
      of weight (1/8)(1/4) = 1/32, which explains the value.

CONSEQUENCE: "every local maximum of psi is global" is FALSE.  Any stability argument that
promotes local certificates to global ones must handle this family.
"""
import sys, os, random, itertools
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R8_stability_core import petersen, psi_exact, cut_mono_masks
from R8_stability_localmax import ascent_direction

random.seed(99)
XSTAR = [F(1, 8), F(1, 8), F(1, 8), F(0), F(1, 8), F(0), F(1, 4), F(1, 8), F(0), F(1, 8)]
BASE40 = [5, 5, 5, 0, 5, 0, 10, 5, 0, 5]


def main():
    g = petersen()
    cuts = cut_mono_masks(g)
    val, _ = psi_exact(g, XSTAR, cuts)
    print(f"(a) psi(Petersen, x*) = {val} = {float(val):.8f}   (1/25 = {float(F(1,25)):.8f})")
    assert val == F(1, 32)

    t, d, _, nact = ascent_direction(g, XSTAR, cuts)
    print(f"(b) active cuts = {nact};  LP optimum t* = {t:.3e}  ->  "
          f"{'first-order LOCAL MAX' if t <= 1e-9 else 'ASCENT EXISTS'}")

    ok = True
    for q, sc in ((40, 1), (200, 5), (1000, 25)):
        a = [b * sc for b in BASE40]
        cand = set()
        mv = [(i, j) for i in range(10) for j in range(10) if i != j]
        for (i, j) in mv:
            b = list(a); b[i] -= 1; b[j] += 1
            if min(b) < 0:
                continue
            cand.add(tuple(b))
            for (k, l) in mv:
                c = list(b); c[k] -= 1; c[l] += 1
                if min(c) >= 0:
                    cand.add(tuple(c))
        best = val
        for c in cand:
            v, _ = psi_exact(g, [F(z, q) for z in c], cuts)
            if v > best:
                best, ok = v, False
        print(f"(c1) q={q}: best over {len(cand)} grid points within 2 unit transfers = {best}"
              f"   (L1 radius {F(4,q)})")
    best = val
    for _ in range(6000):
        dd = [F(random.randint(-9, 9)) if XSTAR[i] > 0 else F(random.randint(0, 9)) for i in range(10)]
        s = sum(dd)
        k = max(range(10), key=lambda i: (XSTAR[i] > 0, abs(dd[i])))
        dd[k] -= s
        for eps in (F(1, 20), F(1, 60), F(1, 200), F(1, 1000)):
            y = [XSTAR[i] + eps * dd[i] for i in range(10)]
            if any(z < 0 for z in y):
                continue
            v, _ = psi_exact(g, y, cuts)
            if v > best:
                best, ok = v, False
    print(f"(c2) best over 6000 random exact rational perturbations = {best}")
    print(f"     ==> {'VERIFIED LOCAL MAXIMUM' if ok else 'NOT A LOCAL MAXIMUM'}")

    dmin = None
    for cyc in g.induced_C5s():
        y = [F(0)] * 10
        for v in cyc:
            y[v] = F(1, 5)
        dd = sum(abs(XSTAR[i] - y[i]) for i in range(10))
        if dmin is None or dd < dmin:
            dmin = dd
    print(f"(d) L1 distance from x* to the nearest global maximiser = {dmin} = {float(dmin)}")

    supp = [v for v in range(10) if XSTAR[v] > 0]
    ed = [(u, v) for (u, v) in g.edges if u in supp and v in supp]
    deg = {v: sum(1 for e in ed if v in e) for v in supp}
    print(f"(e) support {supp}: {len(ed)} induced edges {ed}")
    print(f"    degrees {deg}  ->  theta-graph with branch vertices "
          f"{[v for v in supp if deg[v]==3]} and path lengths 2,3,3")


if __name__ == "__main__":
    main()
