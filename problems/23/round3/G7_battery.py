"""
G7_battery.py -- run the exact engine on EVERY Brandt-Thomasse pattern for
q = 1,2,3,... until a per-graph wall-clock budget is spent, recording the exact
rational 25*M(H,q)/q^2.  Any value > 1 is a refutation of Erdos #23.

Results appended to G7_battery_results.txt (one line per (graph,q)).
"""
import os, sys, time, subprocess
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from G7_run import PATTERNS, edgestr, autfile, EXE

BUDGET = float(os.environ.get('BUDGET', '240'))     # seconds per graph
OUT = os.path.join(HERE, os.environ.get('OUTFILE', 'G7_battery_results.txt'))

order = (['Gamma_%d' % i for i in range(1, 9)] +
         [s % i for i in range(2, 7)
          for s in ('Ups_%d-y-2i', 'Ups_%d-y', 'Ups_%d-2i', 'Ups_%d')])

f = open(OUT, 'a')
f.write('# graph n m q M 25M q^2 ratio verdict elapsed_ms\n')
for name in order:
    g = PATTERNS[name]
    ap, na = autfile(g, name)
    es = edgestr(g)
    t0 = time.time()
    q = 1
    best = Fraction(0)
    while time.time() - t0 < BUDGET:
        s = time.time()
        r = subprocess.run([EXE, str(g.n()), es, str(q), 'max', '8', ap],
                           capture_output=True, text=True)
        el = int((time.time() - s) * 1000)
        line = r.stdout.strip().split('\n')[0]
        if not line.startswith('MAX'):
            f.write('%s ERROR %s\n' % (name, r.stderr.strip()[:200])); break
        M = int(line.split('M=')[1].split()[0])
        rat = Fraction(25 * M, q * q)
        verdict = 'OK' if rat <= 1 else 'REFUTATION'
        if rat > best:
            best = rat
        f.write('%s %d %d %d %d %d %d %s %s %d\n'
                % (name, g.n(), g.m(), q, M, 25 * M, q * q, rat, verdict, el))
        f.flush()
        if verdict == 'REFUTATION':
            print('*** REFUTATION *** %s q=%d M=%d' % (name, q, M))
            sys.exit(2)
        q += 1
    print('%-14s n=%2d  covered q<=%d  max 25M/q^2 = %s' % (name, g.n(), q - 1, best))
    sys.stdout.flush()
f.close()
