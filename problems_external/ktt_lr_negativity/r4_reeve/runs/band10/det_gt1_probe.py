#!/usr/bin/env python3
"""
det_gt1_probe.py -- BAND 10 diagnostic on the ONE hypothesis the c=4 bound needs.

The band-10 bound "c = 4  =>  V = 1" assumes Q is a LATTICE polytope.  A vertex
of Q solves M x = b_T for a triple T of rows; its denominator divides |det M|.
Over the 18 rhombus rows there are 517 non-singular triples with
    |det| = 1 : 468,  |det| = 2 : 48,  |det| = 4 : 1
(lattice_certificate.py).  Only the 49 triples with |det| > 1 can ever produce a
non-integral vertex, and the identical congruence FAILS for them (510 violations)
-- i.e. non-integral Cramer solutions do exist as points; the question is whether
any of them is ever FEASIBLE (A x <= b).

This probe measures exactly that on random gap vectors:
  * how often a |det|>1 triple gives a FEASIBLE point at all;
  * of those, how many are non-integral.
All arithmetic exact (integers / Fraction).
"""
import itertools
import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
from hive4 import build_hive4, _det3  # noqa: E402


def adjugate3(M):
    def minor(r, c):
        rs = [x for x in range(3) if x != r]
        cs = [x for x in range(3) if x != c]
        return M[rs[0]][cs[0]] * M[rs[1]][cs[1]] - M[rs[0]][cs[1]] * M[rs[1]][cs[0]]
    return [[(-1) ** (r + c) * minor(c, r) for c in range(3)] for r in range(3)]


def gaps_to_triple(g):
    Aw = 3 * g[2] + 2 * g[1] + g[0]
    Bw = 3 * g[5] + 2 * g[4] + g[3]
    Cw = 3 * g[8] + 2 * g[7] + g[6]
    D = Cw - Aw - Bw
    if D % 4 != 0:
        return None
    k = D // 4
    l4 = k if k >= 0 else 0
    n4 = 0 if k >= 0 else -k
    return ([l4 + g[2] + g[1] + g[0], l4 + g[2] + g[1], l4 + g[2], l4],
            [g[5] + g[4] + g[3], g[5] + g[4], g[5], 0],
            [n4 + g[8] + g[7] + g[6], n4 + g[8] + g[7], n4 + g[8], n4])


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    ntrial = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
    kmax = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    rng = random.Random(seed)

    H = build_hive4([5, 3, 1], [6, 4, 2], [9, 6, 4, 2])
    A = H["A"]
    big = []
    for T in itertools.combinations(range(len(A)), 3):
        M = [A[T[0]], A[T[1]], A[T[2]]]
        D = _det3(M)
        if D == 0 or abs(D) == 1:
            continue
        adj = adjugate3(M)
        if D < 0:
            D = -D
            adj = [[-x for x in r] for r in adj]
        big.append((T, D, adj))

    tested = 0
    feas_big = 0
    feas_big_nonint = 0
    per_det = {}
    while tested < ntrial:
        g = [rng.randint(0, kmax) for _ in range(9)]
        t = gaps_to_triple(g)
        if t is None:
            continue
        Hh = build_hive4(*t)
        if not Hh["ok"]:
            continue
        tested += 1
        b = Hh["b"]
        AA = Hh["A"]
        for T, D, adj in big:
            bt = (b[T[0]], b[T[1]], b[T[2]])
            num = [sum(adj[r][k] * bt[k] for k in range(3)) for r in range(3)]
            ok = True
            for row, rhs in zip(AA, b):
                if row[0] * num[0] + row[1] * num[1] + row[2] * num[2] > rhs * D:
                    ok = False
                    break
            if not ok:
                continue
            feas_big += 1
            per_det[D] = per_det.get(D, 0) + 1
            if any(n % D != 0 for n in num):
                feas_big_nonint += 1
    out = {
        "seed": seed, "gap_kmax": kmax, "gap_vectors_tested": tested,
        "n_row_triples_with_|det|>1": len(big),
        "feasible_points_from_|det|>1_triples": feas_big,
        "per_det_feasible_counts": {str(k): v for k, v in sorted(per_det.items())},
        "of_those_NON_INTEGRAL": feas_big_nonint,
        "reading": (
            "feasible_points_from_|det|>1_triples = 0 would mean the singular-index triples "
            "are never tight at a feasible point, so every vertex comes from a |det|=1 triple "
            "and Q is ALWAYS a lattice polytope.  A positive count with 0 non-integral means "
            "they are feasible but the numerators always happen to be divisible."
        ),
    }
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
