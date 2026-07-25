#!/usr/bin/env python3
"""Extend the e_4 certificate to a full basis of ker(B) = 222.

The hive witnesses span only a 198-dimensional subspace of ker(B) (a genuine
structural fact: hives satisfy 24 linear relations beyond facet balancing).
To exhibit witnesses spanning ALL of ker(B) -- as in the r=4 template -- we add
general LATTICE polytopes with the 27 normals.

Reliable lattice-polytope generator (q-dilation trick): a random integer-b
polytope P = {N x <= b} that is bounded and full-dimensional has rational
vertices with denominator lcm q; then qP = {N x <= q b} has integral vertices,
so it is a lattice polytope whose Ehrhart function is a genuine polynomial and
whose Lambda-vector still lies in ker(B).

Reads e4_certificate.json (198 hive witnesses), tops up to 222, re-verifies
everything, and rewrites the certificate.
"""
import hashlib
import json
import os
import random
import sys
import time
from fractions import Fraction
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hive5 import lattice_count, NORMALS5  # noqa: E402
from polytope5 import vertices, affine_rank, lambda_vector, PAIR_TYPES  # noqa
from alpha5 import alpha_vector  # noqa: E402
from balance5 import build_B  # noqa: E402
from exactlin import interpolate, solve_nonneg, rank as exrank  # noqa: E402
from build_certificate import IncBasis  # noqa: E402

ALPHA = alpha_vector()
NCOL = len(PAIR_TYPES)
FACT4 = 24


def main():
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    cert = json.load(open(os.path.join(HERE, 'e4_certificate.json')))
    wit = cert['witnesses']
    basis = IncBasis(NCOL)
    for w in wit:
        basis.add([Fraction(x) for x in w['volz']])
    print('loaded %d witnesses, starting rank=%d' % (len(wit), basis.rank),
          flush=True)

    B, _ = build_B()
    kerdim = NCOL - exrank(B)
    rng = random.Random(2024)
    t0 = time.time()
    added = 0
    tries = 0
    while basis.rank < kerdim and time.time() - t0 < budget:
        tries += 1
        span = rng.randint(3, 12)
        b = [rng.randint(-span, span) for _ in range(len(NORMALS5))]
        try:
            V = vertices(b)
        except Exception:
            continue
        if not V or affine_rank(V) != 6:
            continue
        q = 1
        for v in V:
            for x in v:
                q = q * x.denominator // gcd(q, x.denominator)
        bq = [q * x for x in b]
        Vq = vertices(bq)
        if any(x.denominator != 1 for v in Vq for x in v):
            continue                       # safety: qP must be lattice
        try:
            volz, V2, T, F, Rg = lambda_vector(bq, Vq)
        except Exception:
            continue
        volz = [x / FACT4 for x in volz]
        if basis.add(volz):
            counts = [lattice_count(list(NORMALS5), [n * x for x in bq])
                      for n in range(8)]
            co = interpolate([Fraction(v) for v in counts])
            wit.append({'kind': 'lattice', 'b': list(bq), 'a4': str(co[4]),
                        'ehrhart': [str(c) for c in co], 'counts': counts,
                        'nverts': len(Vq), 'nridges': len(Rg),
                        'local_matches': (sum(ALPHA[k] * volz[k]
                                              for k in range(NCOL)) == co[4]),
                        'volz': [str(x) for x in volz]})
            added += 1
            if basis.rank % 4 == 0 or basis.rank >= kerdim:
                print('  rank=%d/%d added=%d tries=%d t=%.0fs'
                      % (basis.rank, kerdim, added, tries, time.time() - t0),
                      flush=True)

    # ---- full re-verification ----
    def matvec(M, x):
        return [sum(M[r][c] * x[c] for c in range(len(x))) for r in range(len(M))]
    Mrows = [[Fraction(x) for x in w['volz']] for w in wit]
    a = [Fraction(w['a4']) for w in wit]
    all_in_ker = all(all(y == 0 for y in matvec(B, v)) for v in Mrows)
    all_local = all(sum(ALPHA[k] * Mrows[i][k] for k in range(NCOL)) == a[i]
                    for i in range(len(wit)))
    Mrank = exrank(Mrows)
    cols = [[Mrows[r][c] for r in range(len(Mrows))] for c in range(NCOL)]
    mu = solve_nonneg(cols, a)
    mu_ok = None
    if mu is not None:
        chk = [sum(cols[c][r] * mu[c] for c in range(NCOL))
               for r in range(len(Mrows))]
        mu_ok = all(x >= 0 for x in mu) and all(chk[r] == a[r]
                                                for r in range(len(Mrows)))

    out = {
        'rank_B': NCOL - kerdim, 'ker_dim': kerdim,
        'n_witnesses': len(wit),
        'n_hive_witnesses': sum(1 for w in wit if w['kind'] == 'hive'),
        'n_lattice_witnesses': sum(1 for w in wit if w['kind'] == 'lattice'),
        'hive_span_rank': cert['summary'].get('hive_span_rank', 198),
        'witness_matrix_rank': Mrank,
        'rowspan_M_equals_kerB': (Mrank == kerdim and all_in_ker),
        'all_witness_lambda_in_kerB': all_in_ker,
        'all_local_identities_hold': all_local,
        'alpha_min': str(min(ALPHA)), 'alpha_all_nonneg': all(x > 0 for x in ALPHA),
        'lp_nonneg_mu_feasible': mu is not None,
        'mu_min': str(min(mu)) if mu is not None else None,
        'mu_verified': mu_ok,
    }
    cert['summary'] = out
    cert['mu'] = [str(x) for x in mu] if mu is not None else None
    txt = json.dumps({k: v for k, v in cert.items() if k != 'summary'},
                     sort_keys=True)
    out['certificate_sha256'] = hashlib.sha256(txt.encode()).hexdigest()
    with open(os.path.join(HERE, 'e4_certificate.json'), 'w') as f:
        json.dump(cert, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
