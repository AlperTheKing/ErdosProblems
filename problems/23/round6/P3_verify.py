"""P3_verify.py -- INDEPENDENT re-verification of the exhaustive psi search.

Deliberately shares no code with P3_psi.cpp:
  * no automorphism reduction (every weighting is processed)
  * no cut cache, no local search: the FULL 2^(n-1) cut set is evaluated for every weighting
  * exact integer arithmetic via numpy int64 (values are tiny: mono <= q^2 <= 10^3)
  * the graph is re-read from the graph6 file P3_vega.g6, not from P3_input.txt

Reports: number of weightings, max bip, whether 25*bip <= q^2 always, and the equality census
(number of weightings and of Aut-orbits with 25*bip == q^2).
"""
import sys, itertools
from fractions import Fraction
import numpy as np
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher


def read_g6_file(path):
    out = []
    for line in open(path):
        line = line.rstrip('\n')
        if not line:
            continue
        g6, ann = line.split('\t')
        name = ann.split()[0]
        out.append((name, nx.from_graph6_bytes(g6.encode()), ann))
    return out


def compositions(q, n):
    """all a >= 0 with sum a = q, as tuples"""
    if n == 1:
        yield (q,)
        return
    for t in range(q + 1):
        for rest in compositions(q - t, n - 1):
            yield (t,) + rest


def run(name, G, q, report_eq=True):
    n = G.number_of_nodes()
    E = [(u, v) for u, v in G.edges()]
    m = len(E)
    ncuts = 1 << (n - 1)
    # mono[c, e] = 1 iff edge e is monochromatic in cut c  (vertex 0 pinned to side 0)
    cuts = np.arange(ncuts, dtype=np.int64)
    M = np.zeros((ncuts, m), dtype=np.int64)
    for e, (u, v) in enumerate(E):
        su = (cuts >> u) & 1
        sv = (cuts >> v) & 1
        M[:, e] = (su == sv).astype(np.int64)
    A = np.array(list(compositions(q, n)), dtype=np.int64)
    eu = np.array([u for u, v in E]); ev = np.array([v for u, v in E])
    best = -1
    eqrows = []
    B = 20000
    bipall = np.empty(A.shape[0], dtype=np.int64)
    for s in range(0, A.shape[0], B):
        blk = A[s:s + B]
        prod = blk[:, eu] * blk[:, ev]          # (B, m)
        mono = prod @ M.T                        # (B, ncuts)
        bip = mono.min(axis=1)
        bipall[s:s + blk.shape[0]] = bip
    best = int(bipall.max())
    viol = np.nonzero(25 * bipall > q * q)[0]
    eqidx = np.nonzero(25 * bipall == q * q)[0]
    orbits = None
    if report_eq and len(eqidx) and len(eqidx) < 200000:
        gm = GraphMatcher(G, G)
        perms = [tuple(mp[t] for t in range(n)) for mp in gm.isomorphisms_iter()]
        seen = set(); reps = 0
        for k in eqidx:
            a = tuple(int(t) for t in A[k])
            if a in seen:
                continue
            reps += 1
            for p in perms:
                seen.add(tuple(a[p[t]] for t in range(n)))
        orbits = reps
    return dict(name=name, n=n, m=m, q=q, count=int(A.shape[0]), maxbip=best,
                viol=len(viol), eq=len(eqidx), eqorbits=orbits,
                psi=Fraction(best, q * q), le=(25 * best <= q * q))


if __name__ == '__main__':
    gs = read_g6_file('P3_vega.g6')
    sel = sys.argv[1] if len(sys.argv) > 1 else 'Ups_2-y-2i'
    qs = [int(t) for t in sys.argv[2].split(',')] if len(sys.argv) > 2 else [6, 7, 8]
    for name, G, ann in gs:
        if sel != 'ALL' and name != sel:
            continue
        for q in qs:
            r = run(name, G, q)
            print('%-12s n=%2d m=%3d q=%2d  #a=%9d  maxbip=%4d  psi=%-10s  25*bip<=q^2: %s '
                  ' violations=%d  equalities=%d (orbits=%s)'
                  % (r['name'], r['n'], r['m'], r['q'], r['count'], r['maxbip'], r['psi'],
                     r['le'], r['viol'], r['eq'], r['eqorbits']))
            sys.stdout.flush()
