"""H1 THEOREM 1 (half-arc first moment):

   ARCBOUND(mu)  <=  W - 2T   =   \iint_{d(x,y)>1/3} (1/2 - d(x,y)) dmu dmu ,

where W = sum over unordered adjacent pairs of w_p and T = sum w_p * d_p.

PROOF.  For a in R/Z let A_a = [a, a+1/2).  For an adjacent pair p = {x,y} with
circular distance d_p = delta <= 1/2, the set of a with x,y both in A_a has
measure 1/2 - delta, and so does the set with neither in A_a; hence A_a
separates p for a set of a of measure exactly 2*delta.  Therefore
   E_a[ mono(A_a) ] = sum_p w_p (1 - 2 delta_p) = W - 2T,
and the minimum over arcs is at most the mean.                             QED

This script (i) checks the inequality exactly on the whole battery, (ii) records
where it is an EQUALITY, (iii) checks the two competing bounds W/3 and W^2.
"""
import random
import sys
from fractions import Fraction as F

sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round4")
from H1_core import Meas, uniform_gamma, three_atom_path, two_antipodal, THIRD

ONE25 = F(1, 25)


def halfarc_mean(M):
    """W - 2T computed directly, and independently by exact integration over a."""
    return M.W - 2 * M.T


def halfarc_mean_by_integration(M):
    """Second implementation: integrate mono([a,a+1/2)) over a in [0,1) exactly.
    mono is piecewise constant in a; breakpoints are the atoms and their antipodes."""
    n = M.n
    bps = sorted(set([p for p in M.pos] + [(p + F(1, 2)) % 1 for p in M.pos]))
    total = F(0)
    for i in range(len(bps)):
        lo = bps[i]
        hi = bps[(i + 1) % len(bps)] if i + 1 < len(bps) else bps[0] + 1
        a = (lo + hi) / 2            # interior sample point
        mem = tuple(((M.pos[j] - a) % 1) < F(1, 2) for j in range(n))
        total += M.mono_of(mem) * (hi - lo)
    return total


def check(name, M, verbose=True):
    ab, _ = M.arcbound()
    hm = halfarc_mean(M)
    hi = halfarc_mean_by_integration(M)
    assert hm == hi, (name, hm, hi)
    ok = ab <= hm
    eq = ab == hm
    if verbose:
        print(f"{name:26s} W={str(M.W):>10s} ARCBOUND={str(ab):>10s}={float(ab):.7f}  "
              f"W-2T={str(hm):>12s}={float(hm):.7f}  thm1={ok}  EQUALITY={eq}  "
              f"W/3={float(M.W/3):.7f}  W^2={float(M.W*M.W):.7f}  W^2ok={ab<=M.W*M.W}")
    return ok, eq, ab, hm


def main():
    print("=== THEOREM 1 check: ARCBOUND <= W - 2T ===")
    fails = 0
    eqs = []
    for m in range(3, 26):
        ok, eq, ab, hm = check(f"uniform Gamma_{m}", uniform_gamma(m))
        fails += (not ok)
        if eq:
            eqs.append(f"Gamma_{m}")
    for nm, M in (("three-atom near-path", three_atom_path()),
                  ("two antipodal", two_antipodal())):
        ok, eq, ab, hm = check(nm, M)
        fails += (not ok)
    # the four W-square falsifiers
    print()
    for wt in ([0, 0, 1, 0, 1, 2, 3, 3, 2, 1, 1], [0, 1, 0, 1, 0, 1, 3, 3, 0, 4, 1],
               [0, 1, 2, 3, 0, 2, 2, 0, 2, 0, 2]):
        pos = [F(j, 11) for j in range(11) if wt[j] > 0]
        w = [F(wt[j]) for j in range(11) if wt[j] > 0]
        ok, eq, ab, hm = check(f"Wsq-falsifier {sum(wt)}", Meas(pos, w))
        fails += (not ok)
    print()
    print("equality cases among uniform Gamma_m:", eqs)

    print()
    print("=== random exact measures ===")
    random.seed(7)
    nf = 0
    neq = 0
    tight = []
    for t in range(400):
        n = random.randint(3, 12)
        den = random.choice([30, 36, 42, 60, 72, 90, 105, 120, 121])
        pts = random.sample(range(den), n)
        M = Meas([F(p, den) for p in pts], [F(random.randint(1, 9)) for _ in range(n)])
        ab, _ = M.arcbound()
        hm = halfarc_mean(M)
        if ab > hm:
            nf += 1
            print("  THEOREM 1 VIOLATION", [str(x) for x in M.pos], [str(x) for x in M.w], ab, hm)
        if ab == hm:
            neq += 1
        if hm > 0:
            tight.append(ab / hm)
    print(f"  400 random: violations={nf}  equalities={neq}  "
          f"mean tightness={float(sum(tight)/len(tight)):.4f}  max={float(max(tight))}")
    print()
    print("TOTAL THEOREM-1 VIOLATIONS:", fails + nf)


if __name__ == "__main__":
    main()
