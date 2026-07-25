#!/usr/bin/env python3
"""GATE 1: the r=5 hive polytope constructor must reproduce the Littlewood--
Richardson coefficient computed by BOTH independent engines.

For every triple, three numbers must agree:
    engine A  (lr_hive.exe, C++ hive DFS, side = #parts(nu))
    engine B  (engineB_lrrule.py, LR skew-tableau rule)
    this build:  #{h in Z^6 : A5 h <= b(lam,mu,nu)}

Usage:  python validate_hive5.py [n_nonzero] [n_zero] [seed]
"""
import json
import os
import random
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hive5 import build_hive5, lattice_count  # noqa: E402

ENG = os.path.join(HERE, '..', 'engine')
ENGA = os.path.abspath(os.path.join(ENG, 'lr_hive.exe'))
ENGB = os.path.abspath(os.path.join(ENG, 'engineB_lrrule.py'))


def fmt(p):
    """Engine part separator is a COMMA.  Space-separated input is silently
    misparsed by both engines, so never use spaces here."""
    q = [x for x in p if x > 0]
    return ','.join(str(x) for x in q) if q else '0'


def run_batch(exe_kind, triples):
    path = os.path.join(HERE, '_val_%s.batch' % exe_kind)
    with open(path, 'w') as f:
        for lam, mu, nu in triples:
            f.write('%s;%s;%s\n' % (fmt(lam), fmt(mu), fmt(nu)))
    if exe_kind == 'A':
        cmd = [ENGA, '--batch', path]
    else:
        cmd = [sys.executable, ENGB, '--batch', path]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    vals = [ln.strip() for ln in out.stdout.strip().splitlines() if ln.strip()]
    if len(vals) != len(triples):
        raise RuntimeError('engine %s returned %d lines for %d triples'
                           % (exe_kind, len(vals), len(triples)))
    return [int(v) for v in vals]


def rand_partition(rng, nparts, maxpart):
    p = sorted((rng.randint(0, maxpart) for _ in range(nparts)), reverse=True)
    return p


def gen(rng, want_nonzero, want_zero, maxtotal=34, maxpart=7):
    """Generate triples; classify by engine A."""
    nonzero, zero = [], []
    tried = set()
    while len(nonzero) < want_nonzero or len(zero) < want_zero:
        batch = []
        for _ in range(400):
            la = rand_partition(rng, rng.randint(2, 5), rng.randint(1, maxpart))
            mm = rand_partition(rng, rng.randint(2, 5), rng.randint(1, maxpart))
            N = sum(la) + sum(mm)
            if N == 0 or N > maxtotal:
                continue
            # nu: random partition of N into at most 5 parts
            cuts = sorted(rng.randint(0, N) for _ in range(4))
            parts = [cuts[0], cuts[1] - cuts[0], cuts[2] - cuts[1],
                     cuts[3] - cuts[2], N - cuts[3]]
            nu = sorted(parts, reverse=True)
            key = (tuple(la), tuple(mm), tuple(nu))
            if key in tried:
                continue
            tried.add(key)
            batch.append((la, mm, nu))
        if not batch:
            continue
        va = run_batch('A', batch)
        for t, v in zip(batch, va):
            if v > 0 and len(nonzero) < want_nonzero:
                nonzero.append((t, v))
            elif v == 0 and len(zero) < want_zero:
                zero.append((t, v))
    return nonzero, zero


def main():
    nz = int(sys.argv[1]) if len(sys.argv) > 1 else 220
    zz = int(sys.argv[2]) if len(sys.argv) > 2 else 130
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 20260722
    rng = random.Random(seed)
    t0 = time.time()
    mt = int(sys.argv[4]) if len(sys.argv) > 4 else 34
    mp = int(sys.argv[5]) if len(sys.argv) > 5 else 7
    nonzero, zero = gen(rng, nz, zz, mt, mp)
    cases = nonzero + zero
    triples = [t for t, _ in cases]
    va = [v for _, v in cases]
    vb = run_batch('B', triples)
    rec = []
    bad = []
    maxc = 0
    for (lam, mu, nu), a, b in zip(triples, va, vb):
        H = build_hive5(lam, mu, nu)
        if not H['ok']:
            mine = 0
        else:
            mine = lattice_count(H['A'], H['b'])
        maxc = max(maxc, mine)
        ok = (a == b == mine)
        rec.append({'lam': lam, 'mu': mu, 'nu': nu, 'A': a, 'B': b, 'mine': mine,
                    'ok': ok})
        if not ok:
            bad.append(rec[-1])
    res = {'n_triples': len(rec), 'n_nonzero': sum(1 for r in rec if r['A'] > 0),
           'n_zero': sum(1 for r in rec if r['A'] == 0),
           'max_lr': maxc, 'mismatches': bad, 'seed': seed,
           'status': 'PASS' if not bad else 'FAIL',
           'seconds': round(time.time() - t0, 1)}
    with open(os.path.join(HERE, os.environ.get('VALOUT','validation_hive5.json')), 'w') as f:
        json.dump({'summary': res, 'records': rec}, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
