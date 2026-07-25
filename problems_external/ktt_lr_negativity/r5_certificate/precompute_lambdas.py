#!/usr/bin/env python3
"""Precompute, in parallel, the exact vol_Z ridge vector and Ehrhart a_4 of
every hive in the seed pools. Saves _hive_lambdas.json for fast certificate
assembly. Exact arithmetic throughout.
"""
import json
import os
import sys
import time
from fractions import Fraction
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hive5 import build_hive5, lattice_count  # noqa: E402
from polytope5 import reduce_rhs, vertices, affine_rank, lambda_vector, PAIR_TYPES  # noqa
from exactlin import interpolate  # noqa: E402

FACT4 = 24


def work(triple):
    lam, mu, nu = triple
    H = build_hive5(lam, mu, nu)
    if not H['ok']:
        return None
    cc = reduce_rhs(H['b'])
    try:
        V = vertices(cc)
    except Exception:
        return None
    if not V or affine_rank(V) != 6:
        return None
    volz, V2, T, F, Rg = lambda_vector(cc, V)
    volz = [x / FACT4 for x in volz]
    counts = [1]
    for n in range(1, 8):
        Hn = build_hive5([n * x for x in lam], [n * x for x in mu],
                         [n * x for x in nu])
        counts.append(lattice_count(Hn['A'], Hn['b']))
    co = interpolate([Fraction(v) for v in counts])
    return {'lam': list(lam), 'mu': list(mu), 'nu': list(nu),
            'volz': [str(x) for x in volz], 'a4': str(co[4]),
            'counts': counts, 'ehrhart': [str(c) for c in co],
            'nverts': len(V), 'nridges': len(Rg)}


def main():
    triples = []
    seen = set()
    for fn in ('_pool_dim6.json', '_dim6_seeds.json', '_pool_big.json'):
        p = os.path.join(HERE, fn)
        if os.path.exists(p):
            for r in json.load(open(p)):
                key = (tuple(r[0]), tuple(r[1]), tuple(r[2]))
                if key not in seen:
                    seen.add(key)
                    triples.append((r[0], r[1], r[2]))
    print('hives to process:', len(triples), flush=True)
    t0 = time.time()
    with Pool(16) as pool:
        res = pool.map(work, triples, chunksize=8)
    recs = [r for r in res if r is not None]
    json.dump(recs, open(os.path.join(HERE, '_hive_lambdas.json'), 'w'))
    print('computed %d hive Lambda-vectors in %.0fs' % (len(recs), time.time() - t0),
          flush=True)


if __name__ == '__main__':
    main()
