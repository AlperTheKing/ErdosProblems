"""
G7_battery_deg.py -- same as G7_battery.py but in the DEGREE-RESTRICTED mode:
maximise bip(H[a]) over a >= 0, sum a = q, subject to 3*(A a)_v > q for all v.

This is the quantity that the Brandt-Thomasse reduction actually needs
(Theorem R2 of G7.md): a triangle-free G with delta(G) > N/3 gives, after
maximal-triangle-free completion and twin quotient, exactly a pattern H
together with class sizes a summing to N and min_v (A a)_v = delta > N/3.
"""
import os, sys, time, subprocess
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from G7_run import PATTERNS, edgestr, autfile

EXE = os.path.join(HERE, 'G7_psi_deg.exe')
BUDGET = float(os.environ.get('BUDGET', '200'))
OUT = os.path.join(HERE, os.environ.get('OUTFILE', 'G7_battery_deg_results.txt'))

order = (['Gamma_%d' % i for i in range(2, 8)] +
         [s % i for i in range(2, 6)
          for s in ('Ups_%d-y-2i', 'Ups_%d-y', 'Ups_%d-2i', 'Ups_%d')])

f = open(OUT, 'a')
f.write('# graph n m q Mdeg 25Mdeg q^2 ratio verdict elapsed_ms\n')
for name in order:
    g = PATTERNS[name]
    ap, na = autfile(g, name)
    es = edgestr(g)
    t0 = time.time()
    q, best, bestq = 1, Fraction(0), 0
    while time.time() - t0 < BUDGET:
        r = subprocess.run([EXE, str(g.n()), es, str(q), 'maxdeg', '8', ap],
                           capture_output=True, text=True)
        line = r.stdout.strip().split('\n')[0]
        if not line.startswith('MAXDEG'):
            f.write('%s ERROR %s\n' % (name, (r.stderr or line)[:200])); break
        M = int(line.split('M=')[1].split()[0])
        rat = Fraction(25 * M, q * q)
        verdict = 'OK' if rat <= 1 else 'REFUTATION'
        f.write('%s %d %d %d %d %d %d %s %s\n'
                % (name, g.n(), g.m(), q, M, 25 * M, q * q, rat, verdict))
        f.flush()
        if verdict == 'REFUTATION':
            print('*** REFUTATION *** %s q=%d M=%d' % (name, q, M)); sys.exit(2)
        if rat > best:
            best, bestq = rat, q
        q += 1
    print('%-14s n=%2d  covered q<=%d  max 25Mdeg/q^2 = %-12s (=%.6f at q=%d)'
          % (name, g.n(), q - 1, best, float(best), bestq))
    sys.stdout.flush()
f.close()
