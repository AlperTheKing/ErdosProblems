#!/usr/bin/env python3
"""Fast, exact assembly of the r=5 codim-2 (e_4) certificate.

Uses precomputed hive Lambda-vectors (_hive_lambdas.json) plus, if requested,
general lattice-polytope witnesses (q-dilation trick) to reach a chosen target
rank. The nonnegative certificate is mu = alpha itself (alpha >= 0), whose
validity is exactly the per-witness local identity a_4 = alpha . Lambda; no LP
is needed for this coefficient. Everything is exact.
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
from exactlin import interpolate, rank as exrank, rank_mod  # noqa: E402
from build_certificate import IncBasis  # noqa: E402

ALPHA = alpha_vector()
NCOL = len(PAIR_TYPES)
FACT4 = 24


def matvec(M, x):
    return [sum(M[r][c] * x[c] for c in range(len(x))) for r in range(len(M))]


def _simplex_subsets(limit_s):
    """7-subsets of the 27 normals that are the facet normals of a simplex:
    rank 6 and a strictly positive (Minkowski) dependence among the 7."""
    import itertools
    from exactlin import kernel_basis
    N = NORMALS5
    out = []
    t0 = time.time()
    combos = list(itertools.combinations(range(27), 7))
    random.Random(11).shuffle(combos)
    for sub in combos:
        if time.time() - t0 > limit_s:
            break
        rows = [N[i] for i in sub]
        if exrank(rows) != 6:
            continue
        K = kernel_basis([[rows[i][t] for i in range(7)] for t in range(6)], 7)
        if len(K) != 1:
            continue
        v = K[0]
        if all(x > 0 for x in v) or all(x < 0 for x in v):
            out.append(sub)
    return out


def gen_lattice_witnesses(basis, wit, target, budget):
    """Complete the basis with small LATTICE SIMPLICES.

    A simplex is defined by 7 of the 27 normals having a strictly positive
    dependence (Minkowski); the other 20 half-spaces are kept loose.  Small
    slacks around a small integer center keep the simplex tiny, so both the
    exact relative-volume triangulation and the Ehrhart lattice counts are
    fast; the q-dilation trick makes each a genuine lattice polytope.
    """
    rng = random.Random(2024)
    t0 = time.time()
    added = 0
    N = NORMALS5
    simplices = _simplex_subsets(90)
    print('  simplex normal-subsets available:', len(simplices), flush=True)
    attempt = 0
    stale = 0
    while basis.rank < target and time.time() - t0 < budget and stale < 8000:
        attempt += 1
        sub = list(simplices[rng.randrange(len(simplices))])
        # combinatorially enrich: with prob 1/2 make one extra normal tight too,
        # cutting corners (8-14 vertex polytopes -> more Lambda directions).
        extra = []
        if rng.random() < 0.6:
            extra = rng.sample([i for i in range(len(N)) if i not in sub],
                               rng.randint(1, 4))
        tight = set(sub) | set(extra)
        span = rng.randint(2, 7)
        x0 = [rng.randint(-span, span) for _ in range(6)]
        b = [sum(N[i][t] * x0[t] for t in range(6))
             + (rng.randint(1, 6) if i in tight else 60) for i in range(len(N))]
        try:
            V = vertices(b)
        except Exception:
            continue
        if not V or affine_rank(V) != 6 or len(V) > 18:
            continue
        q = 1
        for v in V:
            for x in v:
                q = q * x.denominator // gcd(q, x.denominator)
        bq = [q * x for x in b]
        Vq = [tuple(q * x for x in v) for v in V]
        try:
            volz, _V, _T, _F, Rg = lambda_vector(bq, Vq)
        except Exception:
            continue
        volz = [x / FACT4 for x in volz]
        if basis.add(volz):
            # a_4 for these auxiliary basis-completing lattice simplices is the
            # local-formula value; the local formula itself is validated on
            # lattice simplices (independently, from lattice counts) in
            # validate_lattice_simplex.py.
            a4 = sum(ALPHA[k] * volz[k] for k in range(NCOL))
            wit.append({'kind': 'lattice', 'b': list(bq), 'a4': str(a4),
                        'a4_source': 'local_formula',
                        'nverts': len(Vq), 'nridges': len(Rg),
                        'volz': [str(x) for x in volz]})
            added += 1
            stale = 0
            if basis.rank % 4 == 0 or basis.rank >= target:
                print('  lattice rank=%d/%d added=%d attempts=%d t=%.0fs'
                      % (basis.rank, target, added, attempt, time.time() - t0),
                      flush=True)
        else:
            stale += 1
    return added


def main():
    want_full = '--full' in sys.argv
    lat_budget = 900
    B, _ = build_B()
    kerdim = NCOL - exrank(B)
    print('dim ker(B) =', kerdim, flush=True)

    hl = json.load(open(os.path.join(HERE, '_hive_lambdas.json')))
    basis = IncBasis(NCOL)
    wit = []
    for h in hl:
        volz = [Fraction(x) for x in h['volz']]
        if basis.add(volz):
            wit.append({'kind': 'hive', 'lam': h['lam'], 'mu': h['mu'],
                        'nu': h['nu'], 'a4': h['a4'], 'ehrhart': h['ehrhart'],
                        'counts': h['counts'], 'nverts': h['nverts'],
                        'nridges': h['nridges'],
                        'volz': [str(x) for x in volz]})
    hive_span = basis.rank
    print('hive witnesses = %d, hive span rank = %d' % (len(wit), hive_span),
          flush=True)

    if want_full and basis.rank < kerdim:
        gen_lattice_witnesses(basis, wit, kerdim, lat_budget)
        print('after lattice: rank = %d, total witnesses = %d'
              % (basis.rank, len(wit)), flush=True)

    # save witnesses immediately (before verification) so they are never lost
    with open(os.path.join(HERE, '_witnesses_raw.json'), 'w') as f:
        json.dump(wit, f)

    # ---- exact verification ----
    Mrows = [[Fraction(x) for x in w['volz']] for w in wit]
    a = [Fraction(w['a4']) for w in wit]
    all_in_ker = all(all(y == 0 for y in matvec(B, v)) for v in Mrows)
    print('  B.Lambda=0 on all witnesses:', all_in_ker, flush=True)
    all_local = all(sum(ALPHA[k] * Mrows[i][k] for k in range(NCOL)) == a[i]
                    for i in range(len(wit)))
    print('  local identities hold:', all_local, flush=True)
    # Fast rank certificate: modular rank == r proves rational rank >= r; and
    # rational rank <= kerdim since every row lies in ker(B).  So == kerdim.
    Mrank = rank_mod(Mrows)
    # mu = alpha is a valid nonnegative certificate: M alpha = a is exactly the
    # local identities, already checked; alpha >= 0.
    mu = list(ALPHA)
    mu_ok = all_local and all(x >= 0 for x in mu)

    out = {
        'rank_B': NCOL - kerdim, 'ker_dim': kerdim,
        'n_witnesses': len(wit),
        'n_hive_witnesses': sum(1 for w in wit if w['kind'] == 'hive'),
        'n_lattice_witnesses': sum(1 for w in wit if w['kind'] == 'lattice'),
        'hive_span_rank': hive_span,
        'witness_matrix_rank': Mrank,
        'rowspan_M_equals_kerB': (Mrank == kerdim and all_in_ker),
        'all_witness_lambda_in_kerB': all_in_ker,
        'all_local_identities_hold': all_local,
        'alpha_min': str(min(ALPHA)), 'alpha_all_positive': all(x > 0 for x in ALPHA),
        'certificate_mu': 'alpha',
        'mu_min': str(min(mu)), 'mu_nonneg_and_reproduces_a': mu_ok,
    }
    cert = {'summary': out, 'alpha': [str(x) for x in ALPHA],
            'mu': [str(x) for x in mu],
            'pair_types': [list(p) for p in PAIR_TYPES], 'witnesses': wit}
    txt = json.dumps({k: v for k, v in cert.items() if k != 'summary'},
                     sort_keys=True)
    out['certificate_sha256'] = hashlib.sha256(txt.encode()).hexdigest()
    with open(os.path.join(HERE, 'e4_certificate.json'), 'w') as f:
        json.dump(cert, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
