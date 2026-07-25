"""
G7_run.py -- driver: builds every Brandt-Thomasse pattern, dumps its edge list
and automorphism group, calls the exact engine G7_psi_search.exe, and prints an
exact rational table of

     25 * M(H,q) / q^2      (must be <= 1 for the conjecture)

together with the accepted-fact-3 induced-C5 lower bound (which is exactly
1/25 whenever H has odd girth 5, i.e. contains an induced C5).

usage:  python G7_run.py <mode> <graphs...>
"""
import os, sys, subprocess, itertools
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from G7_patterns import (gamma, upsilon, grotzsch, automorphism_group,
                         triangle_free)

EXE = os.path.join(HERE, 'G7_psi_search.exe')


def edgestr(g):
    return ','.join('%d-%d' % (g.idx[u], g.idx[v]) for u, v in g.edges())


def autfile(g, name):
    p = os.path.join(HERE, 'G7_aut_%s.txt' % name)
    A = automorphism_group(g)
    with open(p, 'w') as f:
        for s in A:
            f.write(' '.join(map(str, s)) + '\n')
    return p, len(A)


def induced_c5(g):
    """return an induced 5-cycle as a vertex list, or None"""
    n = g.n()
    idx = g.idx
    A = [[0] * n for _ in range(n)]
    for u, v in g.edges():
        A[idx[u]][idx[v]] = A[idx[v]][idx[u]] = 1
    for S in itertools.combinations(range(n), 5):
        deg = [sum(A[a][b] for b in S) for a in S]
        if deg != [2, 2, 2, 2, 2]:
            continue
        # connected 2-regular on 5 vertices == C5
        seen, cur, prev = {S[0]}, S[0], None
        for _ in range(4):
            nxt = [b for b in S if A[cur][b] and b != prev]
            if not nxt:
                break
            prev, cur = cur, (nxt[0] if nxt[0] not in seen or len(seen) == 5 else
                              (nxt[1] if len(nxt) > 1 else nxt[0]))
            seen.add(cur)
        if len(seen) == 5:
            return list(S)
    return None


def run(g, name, qs, mode='max', threads=8, aut=True):
    es = edgestr(g)
    ap, na = autfile(g, name) if aut else (None, 0)
    out = []
    for q in qs:
        cmd = [EXE, str(g.n()), es, str(q), mode, str(threads)]
        if ap:
            cmd.append(ap)
        r = subprocess.run(cmd, capture_output=True, text=True)
        out.append((q, r.stdout.strip()))
    return out, na


PATTERNS = {}
for i in range(1, 9):
    PATTERNS['Gamma_%d' % i] = gamma(i)
for i in range(2, 7):
    PATTERNS['Ups_%d' % i] = upsilon(i, False, False)[0]
    PATTERNS['Ups_%d-y' % i] = upsilon(i, True, False)[0]
    PATTERNS['Ups_%d-2i' % i] = upsilon(i, False, True)[0]
    PATTERNS['Ups_%d-y-2i' % i] = upsilon(i, True, True)[0]


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'max'
    names = sys.argv[2:] if len(sys.argv) > 2 else list(PATTERNS)
    for name in names:
        g = PATTERNS[name]
        assert triangle_free(g)
        c5 = induced_c5(g)
        print('### %s  n=%d m=%d  inducedC5=%s  C5-lower-bound on max psi = %s'
              % (name, g.n(), g.m(), c5 is not None,
                 '1/25' if c5 else '0'))
        sys.stdout.flush()
        qs = [int(t) for t in os.environ.get('QS', '5,10,15,20,25,30').split(',')]
        res, na = run(g, name, qs, mode)
        print('    |Aut| = %d' % na)
        for q, line in res:
            if line.startswith('MAX'):
                M = int(line.split('M=')[1].split()[0])
                print('    q=%-4d M=%-8d 25M/q^2 = %-12s %s'
                      % (q, M, Fraction(25 * M, q * q),
                         'OK' if 25 * M <= q * q else '*** REFUTATION ***'))
            else:
                print('    ' + line.replace('\n', ' | '))
            sys.stdout.flush()
