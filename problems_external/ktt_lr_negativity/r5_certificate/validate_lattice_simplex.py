#!/usr/bin/env python3
"""Validate the codim-2 local Ehrhart formula on LATTICE SIMPLICES.

The certificate completes ker(B) with lattice simplices carrying the 27 hive
normals; their a_4 is recorded via the local formula.  This script confirms,
on small lattice simplices where the exact Ehrhart lattice counts are cheap,
that the local-formula a_4 equals the a_4 obtained by interpolating exact
lattice-point counts -- i.e. the same identity proved for hives holds for these
lattice witnesses too.

    a_4(lattice counts, n=0..7)  ==  sum_k alpha_k * vol_Z(ridge_k).
"""
import itertools
import os
import random
import sys
import time
from fractions import Fraction
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hive5 import NORMALS5, lattice_count  # noqa: E402
from polytope5 import vertices, affine_rank, lambda_vector  # noqa: E402
from alpha5 import alpha_vector  # noqa: E402
from exactlin import rank as exrank, kernel_basis, interpolate  # noqa: E402
from balance5 import build_B  # noqa: E402

ALPHA = alpha_vector()
N = NORMALS5
FACT4 = 24


def simplex_subsets(limit_s):
    out = []
    t0 = time.time()
    combos = list(itertools.combinations(range(27), 7))
    random.Random(3).shuffle(combos)
    for sub in combos:
        if time.time() - t0 > limit_s:
            break
        rows = [N[i] for i in sub]
        if exrank(rows) != 6:
            continue
        K = kernel_basis([[rows[i][t] for i in range(7)] for t in range(6)], 7)
        if len(K) == 1 and (all(x > 0 for x in K[0]) or all(x < 0 for x in K[0])):
            out.append(sub)
    return out


def main():
    want = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    B, _ = build_B()
    simp = simplex_subsets(12)
    rng = random.Random(99)

    def mv(M, x):
        return [sum(M[r][c] * x[c] for c in range(len(x))) for r in range(len(M))]

    checked = 0
    ker_ok = 0
    local_ok = 0
    bad = []
    t0 = time.time()
    while checked < want and time.time() - t0 < 180 and simp:
        sub = simp[rng.randrange(len(simp))]
        x0 = [rng.randint(-1, 1) for _ in range(6)]
        b = [sum(N[i][t] * x0[t] for t in range(6))
             + (1 if i in sub else 12) for i in range(27)]
        V = vertices(b)
        if not V or affine_rank(V) != 6 or len(V) != 7:
            continue
        q = 1
        for v in V:
            for x in v:
                q = q * x.denominator // gcd(q, x.denominator)
        if q > 3:                     # keep lattice counts cheap
            continue
        bq = [q * x for x in b]
        Vq = [tuple(q * x for x in v) for v in V]
        volz, _V, _T, _F, Rg = lambda_vector(bq, Vq)
        volz = [x / FACT4 for x in volz]
        if all(y == 0 for y in mv(B, volz)):
            ker_ok += 1
        counts = [lattice_count(list(N), [n * x for x in bq]) for n in range(8)]
        co = interpolate([Fraction(v) for v in counts])
        e4 = co[4]
        local = sum(ALPHA[k] * volz[k] for k in range(len(ALPHA)))
        checked += 1
        if local == e4:
            local_ok += 1
        else:
            bad.append({'b': bq, 'e4': str(e4), 'local': str(local)})
    import json
    res = {'lattice_simplices_checked': checked,
           'lambda_in_kerB': ker_ok,
           'local_formula_matches_lattice_counts': local_ok,
           'failures': bad,
           'status': 'PASS' if not bad and checked > 0 and ker_ok == checked
                     and local_ok == checked else 'FAIL'}
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
