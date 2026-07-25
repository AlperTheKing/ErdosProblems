#!/usr/bin/env python3
"""Assemble the r=5 codimension-two (e_4 / a_4) certificate.

Steps
  1. collect hive witnesses, tracking the exact rational rank of the span of
     their vol_Z ridge vectors, until the rank plateaus or reaches dim ker(B);
  2. if hives do not span ker(B), top up with general integer-b lattice-polytope
     witnesses (r=4 style);
  3. verify M B^T = 0 exactly (every witness Lambda lies in ker(B));
  4. verify rowspan(M) = ker(B) via rank(M) == dim ker(B);
  5. verify the local witness identities a_4(P) = Lambda(P) . alpha;
  6. solve the exact LP for a nonnegative mu with M mu = a on the basis, i.e.
     alpha + rowspace(B) contains a nonnegative vector -> a_4 >= 0 for all
     lattice polytopes with these normals.
Everything exact.
"""
import hashlib
import json
import os
import random
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hive5 import build_hive5, lattice_count, NORMALS5  # noqa: E402
from polytope5 import (reduce_rhs, vertices, affine_rank, lambda_vector,  # noqa
                       PAIR_TYPES)
from alpha5 import alpha_vector  # noqa: E402
from balance5 import build_B  # noqa: E402
from exactlin import interpolate, solve_nonneg  # noqa: E402

ALPHA = alpha_vector()
NCOL = len(PAIR_TYPES)          # 342
FACT4 = 24


class IncBasis:
    """Maintain an exact reduced row-echelon basis; add vectors that grow rank."""
    def __init__(self, n):
        self.n = n
        self.rows = []          # reduced rows
        self.pivots = []        # pivot column of each row

    def add(self, v):
        w = [Fraction(x) for x in v]
        for r, p in zip(self.rows, self.pivots):
            if w[p] != 0:
                f = w[p]
                w = [w[k] - f * r[k] for k in range(self.n)]
        piv = next((k for k in range(self.n) if w[k] != 0), None)
        if piv is None:
            return False
        f = w[piv]
        w = [x / f for x in w]
        for i in range(len(self.rows)):
            if self.rows[i][piv] != 0:
                g = self.rows[i][piv]
                self.rows[i] = [self.rows[i][k] - g * w[k] for k in range(self.n)]
        self.rows.append(w)
        self.pivots.append(piv)
        return True

    @property
    def rank(self):
        return len(self.rows)


def ehrhart_a4(lam, mu, nu, nmax=7):
    counts = [1]
    for n in range(1, nmax + 1):
        H = build_hive5([n * x for x in lam], [n * x for x in mu],
                        [n * x for x in nu])
        counts.append(lattice_count(H['A'], H['b']))
    co = interpolate([Fraction(v) for v in counts])
    return co[4], counts, co


def collect_hive_witnesses(target, timebudget, seedpools):
    basis = IncBasis(NCOL)
    wit = []
    seen = set()
    t0 = time.time()
    rng = random.Random(1234567)
    # first drain the explicit seed pools
    for lam, mu, nu in seedpools:
        key = (tuple(lam), tuple(mu), tuple(nu))
        if key in seen:
            continue
        seen.add(key)
        H = build_hive5(lam, mu, nu)
        if not H['ok']:
            continue
        cc = reduce_rhs(H['b'])
        volz, V, T, F, Rg = lambda_vector(cc)
        if affine_rank(V) != 6:
            continue
        volz = [x / FACT4 for x in volz]
        if basis.add(volz):
            a4, counts, co = ehrhart_a4(lam, mu, nu)
            wit.append({'kind': 'hive', 'lam': list(lam), 'mu': list(mu),
                        'nu': list(nu), 'volz': volz, 'a4': a4,
                        'counts': counts,
                        'ehrhart': [str(c) for c in co],
                        'nverts': len(V), 'nridges': len(Rg)})
            print('  [seed] rank=%d/%d witnesses=%d' % (basis.rank, target, len(wit)),
                  flush=True)
            if basis.rank >= target:
                return basis, wit, 'reached'
    # then random search
    stale = 0
    while time.time() - t0 < timebudget and basis.rank < target and stale < 4000:
        lam = sorted((rng.randint(1, 18) for _ in range(5)), reverse=True)
        mu = sorted((rng.randint(1, 18) for _ in range(5)), reverse=True)
        N = sum(lam) + sum(mu)
        nu = [lam[i] + mu[i] for i in range(5)]
        for _ in range(rng.randint(0, 10)):
            i, j = rng.randint(0, 4), rng.randint(0, 4)
            if i == j:
                continue
            a, bq = min(i, j), max(i, j)
            n2 = nu[:]
            n2[a] -= 1
            n2[bq] += 1
            if sorted(n2, reverse=True) == n2 and all(x >= 0 for x in n2):
                nu = n2
        nu = sorted(nu, reverse=True)
        key = (tuple(lam), tuple(mu), tuple(nu))
        if key in seen or sum(nu) != N:
            continue
        seen.add(key)
        H = build_hive5(lam, mu, nu)
        if not H['ok']:
            continue
        cc = reduce_rhs(H['b'])
        try:
            volz, V, T, F, Rg = lambda_vector(cc)
        except Exception:
            continue
        if affine_rank(V) != 6:
            continue
        volz = [x / FACT4 for x in volz]
        if basis.add(volz):
            a4, counts, co = ehrhart_a4(lam, mu, nu)
            wit.append({'kind': 'hive', 'lam': list(lam), 'mu': list(mu),
                        'nu': list(nu), 'volz': volz, 'a4': a4,
                        'counts': counts, 'ehrhart': [str(c) for c in co],
                        'nverts': len(V), 'nridges': len(Rg)})
            stale = 0
            if basis.rank % 10 == 0 or basis.rank >= target:
                print('  [rand] rank=%d/%d witnesses=%d stale=%d t=%.0fs'
                      % (basis.rank, target, len(wit), stale, time.time() - t0),
                      flush=True)
        else:
            stale += 1
    return basis, wit, ('reached' if basis.rank >= target else 'plateau')


def collect_lattice_witnesses(basis, wit, target, timebudget, maxb=9):
    rng = random.Random(987654)
    t0 = time.time()
    while time.time() - t0 < timebudget and basis.rank < target:
        b = [rng.randint(-maxb, maxb) for _ in range(len(NORMALS5))]
        try:
            V = vertices(b)
        except Exception:
            continue
        if not V or affine_rank(V) != 6:
            continue
        if any(x.denominator != 1 for v in V for x in v):
            continue
        volz, V2, T, F, Rg = lambda_vector(b, V)
        volz = [x / FACT4 for x in volz]
        if basis.add(volz):
            counts = [lattice_count(list(NORMALS5), [n * x for x in b])
                      for n in range(8)]
            co = interpolate([Fraction(v) for v in counts])
            wit.append({'kind': 'lattice', 'b': list(b), 'volz': volz,
                        'a4': co[4], 'counts': counts,
                        'ehrhart': [str(c) for c in co],
                        'nverts': len(V), 'nridges': len(Rg)})
    return basis, wit


def main():
    B, wedges = build_B()
    # dim ker(B)
    from exactlin import rank as exrank
    rankB = exrank(B)
    kerdim = NCOL - rankB
    print('rank(B)=%d  dim ker(B)=%d' % (rankB, kerdim))

    seedpools = []
    for fn in ('_dim6_seeds.json', '_pool_dim6.json'):
        p = os.path.join(HERE, fn)
        if os.path.exists(p):
            for r in json.load(open(p)):
                seedpools.append((r[0], r[1], r[2]))
    print('seed pool size = %d' % len(seedpools))

    hb = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    lb = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    basis, wit, how = collect_hive_witnesses(kerdim, hb, seedpools)
    print('after hives: rank=%d (%s), hive witnesses=%d'
          % (basis.rank, how, len(wit)))
    hive_rank = basis.rank
    if basis.rank < kerdim:
        basis, wit = collect_lattice_witnesses(basis, wit, kerdim, lb)
        print('after lattice top-up: rank=%d, total witnesses=%d'
              % (basis.rank, len(wit)))

    # --- verifications on the collected witnesses ---
    # M B^T = 0  (every Lambda in ker(B))
    def matvec(M, x):
        return [sum(M[r][c] * x[c] for c in range(len(x))) for r in range(len(M))]
    all_in_ker = True
    all_local = True
    for w in wit:
        Bl = matvec(B, w['volz'])
        if any(x != 0 for x in Bl):
            all_in_ker = False
        local = sum(ALPHA[k] * w['volz'][k] for k in range(NCOL))
        if local != w['a4']:
            all_local = False
            w['local_matches'] = False
        else:
            w['local_matches'] = True

    # rank(M) exactly (independent of the incremental basis)
    Mrows = [w['volz'] for w in wit]
    Mrank = exrank(Mrows)

    # LP: nonnegative mu with M mu = a  on the witnesses  (a = a4 values)
    # columns of the LP are the 342 ridge coordinates; rows are witnesses.
    a = [w['a4'] for w in wit]
    cols = [[Mrows[r][c] for r in range(len(Mrows))] for c in range(NCOL)]
    mu = solve_nonneg(cols, a)
    lp_feasible = mu is not None
    mu_min = min(mu) if mu is not None else None
    mu_ok = None
    if mu is not None:
        chk = [sum(cols[c][r] * mu[c] for c in range(NCOL)) for r in range(len(Mrows))]
        mu_ok = all(chk[r] == a[r] for r in range(len(Mrows))) and all(x >= 0 for x in mu)

    # alpha itself is the trivial certificate here (alpha>=0); record that too
    alpha_nonneg = all(x >= 0 for x in ALPHA)

    out = {
        'rank_B': rankB, 'ker_dim': kerdim,
        'n_witnesses': len(wit),
        'n_hive_witnesses': sum(1 for w in wit if w['kind'] == 'hive'),
        'n_lattice_witnesses': sum(1 for w in wit if w['kind'] == 'lattice'),
        'hive_span_rank': hive_rank,
        'witness_matrix_rank': Mrank,
        'rowspan_M_equals_kerB': (Mrank == kerdim and all_in_ker),
        'all_witness_lambda_in_kerB': all_in_ker,
        'all_local_identities_hold': all_local,
        'alpha_min': str(min(ALPHA)), 'alpha_all_nonneg': alpha_nonneg,
        'lp_nonneg_mu_feasible': lp_feasible,
        'mu_min': str(mu_min) if mu_min is not None else None,
        'mu_verified': mu_ok,
    }
    # persist witnesses (compact) and mu
    wjson = []
    for w in wit:
        d = {'kind': w['kind'], 'a4': str(w['a4']),
             'ehrhart': w['ehrhart'], 'counts': w['counts'],
             'nverts': w['nverts'], 'nridges': w['nridges'],
             'local_matches': w['local_matches'],
             'volz': [str(x) for x in w['volz']]}
        if w['kind'] == 'hive':
            d.update(lam=w['lam'], mu=w['mu'], nu=w['nu'])
        else:
            d.update(b=w['b'])
        wjson.append(d)
    cert = {'summary': out,
            'alpha': [str(x) for x in ALPHA],
            'mu': [str(x) for x in mu] if mu is not None else None,
            'pair_types': [list(p) for p in PAIR_TYPES],
            'witnesses': wjson}
    txt = json.dumps(cert, sort_keys=True)
    out['certificate_sha256'] = hashlib.sha256(txt.encode()).hexdigest()
    with open(os.path.join(HERE, 'e4_certificate.json'), 'w') as f:
        json.dump(cert, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
