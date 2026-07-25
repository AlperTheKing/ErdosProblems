#!/usr/bin/env python3
"""Per-witness engine cross-check for the hive witnesses in e4_certificate.json.

For each hive witness whose stretched profile stays inside the engines' count
range, run BOTH engines on n*(lam,mu,nu) for n=1..NMAX, interpolate a_4 from
each engine's profile, and require

    a_4(engine A) == a_4(engine B) == a_4(lattice count, stored in certificate).

This directly ties every checked witness's certified a_4 to both independent
Littlewood--Richardson oracles.
"""
import json
import os
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from exactlin import interpolate  # noqa: E402

ENG = os.path.join(HERE, '..', 'engine')
ENGA = os.path.abspath(os.path.join(ENG, 'lr_hive.exe'))
ENGB = os.path.abspath(os.path.join(ENG, 'engineB_lrrule.py'))
CAP = 10 ** 15


def fmt(p):
    q = [x for x in p if x > 0]
    return ','.join(str(x) for x in q) if q else '0'


def run_batch(kind, triples):
    path = os.path.join(HERE, '_xw_%s.batch' % kind)
    with open(path, 'w') as f:
        for lam, mu, nu in triples:
            f.write('%s;%s;%s;%d\n' % (fmt(lam), fmt(mu), fmt(nu), CAP))
    cmd = ([ENGA, '--batch', path] if kind == 'A'
           else [sys.executable, ENGB, '--batch', path])
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    vals = [ln.strip() for ln in out.stdout.strip().splitlines() if ln.strip()]
    return vals                       # raw strings; may be 'CAP_EXCEEDED'


def main():
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    nwit = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    cert = json.load(open(os.path.join(HERE, 'e4_certificate.json')))
    hives = [w for w in cert['witnesses'] if w['kind'] == 'hive']
    hives.sort(key=lambda w: sum(w['nu']))
    checked = hives[:nwit]
    triples = []
    for w in checked:
        for n in range(1, nmax + 1):
            triples.append(([n * x for x in w['lam']], [n * x for x in w['mu']],
                            [n * x for x in w['nu']]))
    va = run_batch('A', triples)
    vb = run_batch('B', triples)
    ok = 0
    skipped = 0
    bad = []
    for i, w in enumerate(checked):
        sa = va[i * nmax:(i + 1) * nmax]
        sb = vb[i * nmax:(i + 1) * nmax]
        if any(x == 'CAP_EXCEEDED' for x in sa + sb):
            skipped += 1
            continue
        ea = [1] + [int(x) for x in sa]
        eb = [1] + [int(x) for x in sb]
        ca = interpolate([Fraction(v) for v in ea])
        cb = interpolate([Fraction(v) for v in eb])
        a4_store = Fraction(w['a4'])
        counts_prefix = w['counts'][:len(ea)]
        if ca[4] == cb[4] == a4_store and ea == eb == counts_prefix:
            ok += 1
        else:
            bad.append({'lam': w['lam'], 'mu': w['mu'], 'nu': w['nu'],
                        'a4_store': str(a4_store), 'a4_A': str(ca[4]),
                        'a4_B': str(cb[4])})
    res = {'hive_witnesses_total': len(hives),
           'attempted': len(checked), 'skipped_engine_cap': skipped,
           'engineA_eq_engineB_eq_certificate': ok,
           'failures': bad,
           'status': 'PASS' if not bad and ok > 0 else 'FAIL'}
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
