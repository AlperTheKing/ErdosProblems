"""H1 mandated test battery (EXACT).  Reports ARCBOUND, W, W^2 for the six
required reference measures plus 200 random measures, and checks:
  L1  ARCBOUND <= W^2
  L2  min over 'balanced' arcs (mass closest to 1/2 from each side) <= W^2
  L3  ARCBOUND <= 1/25
  L5  fiveblock: min over 5 cut points of (W+4P0+2P1) <= 1/5
"""
import random
import sys
from fractions import Fraction as F

sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round4")
from H1_core import (Meas, uniform_gamma, three_atom_path, two_antipodal, THIRD)

ONE25 = F(1, 25)


def report(name, M, do5=True):
    ab, args = M.arcbound()
    W = M.W
    bal = M.balanced_arcs()
    bvals = []
    for lo, hi in bal:
        bvals.append(M.mono_of(M.arc_mem(*lo)))
        if hi is not None:
            bvals.append(M.mono_of(M.arc_mem(*hi)))
    bmin = min(bvals) if bvals else W
    fb = M.fiveblock_min()[0] if (do5 and M.n >= 5) else None
    rec = dict(name=name, n=M.n, W=W, W2=W * W, AB=ab, BAL=bmin, FB=fb,
               L1=(ab <= W * W), L2=(bmin <= W * W), L3=(ab <= ONE25),
               L5=(None if fb is None else fb <= F(1, 5)))
    return rec


def show(rec):
    def f(x):
        return "None" if x is None else f"{x}={float(x):.6f}"
    print(f"{rec['name']:28s} n={rec['n']:3d}  W={rec['W']} ({float(rec['W']):.6f})"
          f"  AB={rec['AB']} ({float(rec['AB']):.6f})  W^2={float(rec['W2']):.6f}"
          f"  BAL={float(rec['BAL']):.6f}  FB={None if rec['FB'] is None else float(rec['FB']):}"
          f"  L1={rec['L1']} L2={rec['L2']} L3={rec['L3']} L5={rec['L5']}")


def main():
    recs = []
    # --- mandated reference measures --------------------------------
    recs.append(report("five-atom (Gamma_5=C5)", uniform_gamma(5)))
    recs.append(report("seven-atom (Gamma_7)", uniform_gamma(7)))
    recs.append(report("three-atom near-path", three_atom_path()))
    recs.append(report("two antipodal atoms", two_antipodal(), do5=False))
    for m in list(range(4, 26)):
        recs.append(report(f"uniform Gamma_{m}", uniform_gamma(m)))
    for r in recs:
        show(r)

    # --- 200 random exact measures ----------------------------------
    random.seed(20260725)
    bad1 = bad2 = bad3 = bad5 = 0
    worst1 = None
    worst5 = None
    stats = []
    for t in range(200):
        n = random.randint(3, 11)
        den = random.choice([30, 36, 42, 60, 72, 90, 105, 120])
        pts = random.sample(range(den), n)
        pos = [F(p, den) for p in pts]
        w = [F(random.randint(1, 9)) for _ in range(n)]
        M = Meas(pos, w)
        ab, _ = M.arcbound()
        W = M.W
        bal = M.balanced_arcs()
        bvals = []
        for lo, hi in bal:
            bvals.append(M.mono_of(M.arc_mem(*lo)))
            if hi is not None:
                bvals.append(M.mono_of(M.arc_mem(*hi)))
        bmin = min(bvals)
        stats.append((W, ab))
        if ab > W * W:
            bad1 += 1
            print("  L1 VIOLATION", [str(x) for x in M.pos], [str(x) for x in M.w],
                  "AB=", ab, "W^2=", W * W)
        if bmin > W * W:
            bad2 += 1
        if ab > ONE25:
            bad3 += 1
            print("  L3 VIOLATION", [str(x) for x in M.pos], [str(x) for x in M.w])
        if M.n >= 5:
            fb, _ = M.fiveblock_min()
            if fb > F(1, 5):
                bad5 += 1
                if worst5 is None or fb > worst5[0]:
                    worst5 = (fb, M)
        r = ab / (W * W) if W > 0 else F(0)
        if worst1 is None or r > worst1[0]:
            worst1 = (r, M)
    print(f"\nrandom 200: L1 fails={bad1}  L2 fails={bad2}  L3 fails={bad3}  L5 fails={bad5}")
    print("worst AB/W^2 ratio:", worst1[0], float(worst1[0]),
          [str(x) for x in worst1[1].pos], [str(x) for x in worst1[1].w])
    if worst5:
        print("worst fiveblock value:", worst5[0], float(worst5[0]),
              [str(x) for x in worst5[1].pos], [str(x) for x in worst5[1].w])


if __name__ == "__main__":
    main()
