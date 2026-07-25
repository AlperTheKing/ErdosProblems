"""H1: independent EXACT verification (Python/Fraction) of the candidate
W-SQUARE falsifiers produced by the C++ scanner H1_scan.cpp.

Also re-derives ARCBOUND by a THIRD, deliberately naive method: enumerate all
2^n subsets, keep those that are cyclic intervals, take the min.
"""
import sys
from fractions import Fraction as F
from itertools import product

sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round4")
from H1_core import Meas, THIRD


def naive_arcbound(M):
    """brute force over all 2^n subsets, filtered to cyclic intervals."""
    n = M.n
    best = None
    for bits in product([0, 1], repeat=n):
        # cyclic interval test: number of 0->1 transitions around the cycle <= 1
        trans = sum(1 for i in range(n) if bits[i] == 0 and bits[(i + 1) % n] == 1)
        if trans > 1:
            continue
        mem = tuple(bool(b) for b in bits)
        v = M.mono_of(mem)
        if best is None or v < best:
            best = v
    return best


def from_gamma(m, weights):
    pos = [F(j, m) for j in range(m) if weights[j] > 0]
    w = [F(weights[j]) for j in range(m) if weights[j] > 0]
    return Meas(pos, w)


CANDIDATES = [
    (11, [0, 0, 1, 0, 1, 2, 3, 3, 2, 1, 1]),   # claimed max ratio 1.47
    (11, [0, 1, 0, 1, 0, 1, 3, 3, 0, 4, 1]),
    (11, [0, 1, 2, 3, 0, 2, 2, 0, 2, 0, 2]),
    (11, [0, 1, 1, 1, 2, 0, 3, 2, 2, 0, 2]),
]


def main():
    for m, wt in CANDIDATES:
        M = from_gamma(m, wt)
        ab, args = M.arcbound()
        nb = naive_arcbound(M)
        q = sum(wt)
        assert ab == nb, ("two implementations disagree", ab, nb)
        W = M.W
        print(f"Gamma_{m} w={wt} q={q}")
        print(f"   support positions {[str(p) for p in M.pos]}")
        print(f"   W        = {W} = {float(W):.8f}")
        print(f"   W^2      = {W*W} = {float(W*W):.8f}")
        print(f"   ARCBOUND = {ab} = {float(ab):.8f}   (2 independent Python impls agree)")
        print(f"   integer form: A*q^2 = {ab*q*q*1} vs E^2 = {(W*q*q)**2}")
        print(f"   ARCBOUND <= W^2 ?  {ab <= W*W}     ratio = {ab/(W*W)} = {float(ab/(W*W)):.6f}")
        print(f"   ARCBOUND <= 1/25 ? {ab <= F(1,25)}  (arc-cut conjecture)")
        print(f"   minimising arcs (start,len): {args[:6]}")
        print()


if __name__ == "__main__":
    main()
