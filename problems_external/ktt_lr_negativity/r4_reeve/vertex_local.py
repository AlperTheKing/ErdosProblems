#!/usr/bin/env python3
"""
vertex_local.py -- local (vertex-cone) structure of actually-occurring r=4 hive
polytopes, over the gap moduli space.

For each dim-3 Q it reports
  * whether every vertex is a lattice point (max denominator),
  * for every SIMPLE vertex (exactly 3 facet rows tight, independent) the lattice
    multiplicity m of its tangent cone,
  * the number of non-simple vertices.
The abstract bound from cone_atlas.py is m <= 4; this measures which values are
actually realised by hive data.
"""
import itertools
import sys
from fractions import Fraction

sys.path.insert(0, ".")
from hive4 import build_hive4, analyze, vertices, _det3, _dot, _affine_rank
from cone_atlas import cone_generators
from gap_moduli import triple_from_gaps


def main():
    G = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    step = int(sys.argv[2]) if len(sys.argv) > 2 else 13
    mhist = {}
    nonsimple = 0
    maxden = 1
    n3 = 0
    seen = 0
    examples = {}
    for g in itertools.product(range(G + 1), repeat=9):
        t = triple_from_gaps(g[0:3], g[3:6], g[6:9])
        if t is None:
            continue
        seen += 1
        if seen % step:
            continue
        H = build_hive4(*t)
        if not H["ok"]:
            continue
        A, b = H["A"], H["b"]
        V = vertices(A, b)
        if len(V) < 4 or _affine_rank(V) < 3:
            continue
        n3 += 1
        for v in V:
            for co in v:
                maxden = max(maxden, co.denominator)
            tight = [i for i, (row, rhs) in enumerate(zip(A, b)) if _dot(row, v) == rhs]
            dirs = sorted({tuple(A[i]) for i in tight})
            # keep only an independent facet-defining triple: a vertex is simple iff
            # the tight rows span a simplicial cone with exactly 3 facets
            if len(dirs) == 3 and _det3([list(x) for x in dirs]) != 0:
                gen = cone_generators([list(x) for x in dirs])
                if gen is None:
                    continue
                m = abs(_det3([list(x) for x in gen]))
                mhist[m] = mhist.get(m, 0) + 1
                if m not in examples:
                    examples[m] = (t, dirs, [str(c) for c in v])
            else:
                nonsimple += 1
    print("dim-3 hive polytopes examined : %d  (every %dth realisable gap vector, G=%d)" % (n3, step, G))
    print("max vertex denominator        : %d   (1 == every Q is a LATTICE polytope)" % maxden)
    print("simple-vertex multiplicities  : %s" % dict(sorted(mhist.items())))
    print("non-simple vertices           : %d" % nonsimple)
    for m in sorted(examples):
        print("   m=%d first example: triple=%s tight rows=%s vertex=%s" % (m, examples[m][0], examples[m][1], examples[m][2]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
