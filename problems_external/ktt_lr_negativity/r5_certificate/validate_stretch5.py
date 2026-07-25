#!/usr/bin/env python3
"""GATE 2: stretched profiles.

For each sampled triple with c > 0 this checks, exactly,
  * lattice_count(Q(n lam, n mu, n nu)) == engine A == engine B for n = 0..NMAX,
  * the Lagrange interpolation of n = 0..deg reproduces every held-out value,
so the Ehrhart polynomial extracted downstream from lattice counts is the
stretched Littlewood--Richardson polynomial of both engines.

Usage: python validate_stretch5.py [ntriples] [nmax] [seed]
"""
import json
import os
import sys
import random
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hive5 import build_hive5, lattice_count  # noqa: E402
from exactlin import interpolate  # noqa: E402
from validate_hive5 import run_batch, gen  # noqa: E402


def polyval(co, x):
    return sum(c * Fraction(x) ** i for i, c in enumerate(co))


def main():
    nt = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 4242
    rng = random.Random(seed)
    t0 = time.time()
    nonzero, _ = gen(rng, nt, 0, 26, 6)
    triples = [t for t, _ in nonzero]
    stretched = []
    for lam, mu, nu in triples:
        for n in range(1, nmax + 1):
            stretched.append(([n * x for x in lam], [n * x for x in mu],
                              [n * x for x in nu]))
    va = run_batch('A', stretched)
    vb = run_batch('B', stretched)
    recs = []
    bad = []
    for ti, (lam, mu, nu) in enumerate(triples):
        vals = [1]
        for n in range(1, nmax + 1):
            H = build_hive5([n * x for x in lam], [n * x for x in mu],
                            [n * x for x in nu])
            vals.append(lattice_count(H['A'], H['b']) if H['ok'] else 0)
        ea = [1] + va[ti * nmax:(ti + 1) * nmax]
        eb = [1] + vb[ti * nmax:(ti + 1) * nmax]
        agree = (vals == ea == eb)
        co = interpolate([Fraction(v) for v in vals[:7]])
        held = all(polyval(co, n) == vals[n] for n in range(7, nmax + 1))
        deg = max([i for i, c in enumerate(co) if c != 0] or [0])
        neg = [i for i, c in enumerate(co) if c < 0]
        ok = agree and held
        recs.append({'lam': lam, 'mu': mu, 'nu': nu, 'counts': vals,
                     'engineA': ea, 'engineB': eb, 'agree': agree,
                     'heldout_ok': held, 'degree': deg,
                     'coeffs': [str(c) for c in co],
                     'negative_coeff_positions': neg})
        if not ok:
            bad.append(recs[-1])
    res = {'n_triples': len(recs), 'nmax': nmax,
           'degrees': sorted(set(r['degree'] for r in recs)),
           'any_negative_coefficient':
               sorted(set(tuple(r['negative_coeff_positions']) for r in recs)),
           'failures': bad, 'seed': seed,
           'status': 'PASS' if not bad else 'FAIL',
           'seconds': round(time.time() - t0, 1)}
    with open(os.path.join(HERE, 'validation_stretch5.json'), 'w') as f:
        json.dump({'summary': res, 'records': recs}, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
