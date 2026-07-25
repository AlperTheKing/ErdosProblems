"""Q3 round 7 -- driver: run the exhaustive weighting enumeration over a list of patterns and
aggregate the exact Pareto frontiers into the global stability curve

        Psi(t) = max { bip/Q^2 : dist/Q^2 >= t }   (over everything enumerated)

usage: python Q3_batch.py <patternfile> <Q> <num> <den> <threads> <outprefix>
Every printed number is an exact rational.
"""
import subprocess
import sys
from fractions import Fraction as F

EXE = 'E:/Projects/ErdosProblems/problems/23/round7/Q3_exhaust.exe'


def main():
    pf, Q, num, den, th, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]
    pats = [l.split()[0] for l in open(pf) if l.strip()]
    rows = []
    with open(out + '_raw.tsv', 'w') as raw:
        raw.write('g6\tQ\tdist\tbip\tw\n')
        for i, p in enumerate(pats):
            r = subprocess.run([EXE, p, Q, num, den, th], capture_output=True, text=True)
            for line in r.stdout.splitlines():
                if line.startswith('#') or line.startswith('dist'):
                    continue
                parts = line.split('\t')
                if len(parts) < 3:
                    continue
                d, b, w = int(parts[0]), int(parts[1]), parts[2]
                rows.append((p, int(Q), d, b, w))
                raw.write('%s\t%s\t%d\t%d\t%s\n' % (p, Q, d, b, w))
            if (i + 1) % 25 == 0:
                print('  ... %d/%d patterns' % (i + 1, len(pats)), flush=True)
    QQ = int(Q) ** 2
    # global envelope
    ds = sorted(set(d for (_, _, d, _, _) in rows))
    print('pattern file %s, Q=%s, %d patterns, %d frontier points' % (pf, Q, len(pats), len(rows)))
    print('%-10s %-12s %-12s %-12s %s' % ('t (=D/Q^2)', 'Psi(t)', 'decimal', 'deficit', 'witness'))
    best_at = {}
    for (p, q, d, b, w) in rows:
        for t in ds:
            if d >= t:
                if t not in best_at or b > best_at[t][0]:
                    best_at[t] = (b, p, d, w)
    for t in ds:
        b, p, d, w = best_at[t]
        print('%-10s %-12s %-12.7f %-12.7f %s d=%d w=%s'
              % ('%d/%d' % (t, QQ), '%d/%d' % (b, QQ), b / QQ, float(F(1, 25) - F(b, QQ)), p, d, w))


if __name__ == '__main__':
    main()
