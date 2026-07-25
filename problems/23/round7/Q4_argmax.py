"""Q4: enumerate ALL exact integer maximisers of bip(H[a])/N^2 (i.e. 25*bip == N^2) for given N.
Determines the exact zero set of any tight certificate, hence the exact kernel of its Gram.
"""
import sys
from itertools import combinations_with_replacement
from Q4_graphs import gamma_graph, all_cuts, nondominated_cuts

m = int(sys.argv[1]) if len(sys.argv) > 1 else 8
Ns = [int(t) for t in sys.argv[2].split(',')] if len(sys.argv) > 2 else [10, 15]
n, E = gamma_graph(m)
cuts = nondominated_cuts(all_cuts(n, E))
mono = [[E[k] for k in c[1]] for c in cuts]


def comps(n, N):
    def rec(i, rem, cur):
        if i == n - 1:
            yield tuple(cur + [rem])
            return
        for v in range(rem + 1):
            yield from rec(i + 1, rem - v, cur + [v])
    yield from rec(0, N, [])


for N in Ns:
    hits = []
    for a in comps(n, N):
        b = min(sum(a[u] * a[v] for u, v in c) for c in mono)
        if 25 * b >= N * N:
            hits.append((a, b))
    print(f"N={N}: {len(hits)} maximisers with 25*bip == N^2")
    supports = {}
    for a, b in hits:
        supports.setdefault(frozenset(i for i in range(n) if a[i]), []).append(a)
    for s, lst in sorted(supports.items(), key=lambda t: sorted(t[0])):
        print(f"   support {sorted(s)}: {len(lst)} vectors, e.g. {lst[0]}")
