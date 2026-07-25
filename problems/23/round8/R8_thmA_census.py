"""R8_thmA_census.py -- EXHAUSTIVE falsification search.

Generates every triangle-free graph on n <= NMAX vertices up to isomorphism by
vertex extension (deleting a vertex from a triangle-free graph leaves one, so
the generation is complete), validates the counts against the known sequence
1, 2, 3, 7, 14, 38, 107, 410, 1897, 12172  (A006785), then computes
max_x Lambda(G,x) for every MAXIMAL non-bipartite one.

Restricting to maximal graphs is WLOG: adding an edge can only shrink the set of
feasible covers, so Lambda(G,x) is monotone non-decreasing in the edge set, and
every triangle-free graph is a spanning subgraph of a maximal one.
"""

import sys
import time
from fractions import Fraction

import networkx as nx

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from R8_thmA_lib import *          # noqa
from R8_thmA_search import maximize, exact_check, c5_starts, five_cycles   # noqa
from R8_thmA_sweep import leak_scan, exact_probe, VIOL                     # noqa

KNOWN = [1, 2, 3, 7, 14, 38, 107, 410, 1897, 12172, 105071]
ONE25 = Fraction(1, 25)


def wl_key(n, adjbits):
    lab = [bin(adjbits[v]).count("1") for v in range(n)]
    for _ in range(3):
        new = []
        for v in range(n):
            nb = sorted(lab[u] for u in range(n) if (adjbits[v] >> u) & 1)
            new.append(hash((lab[v], tuple(nb))))
        rank = {h: i for i, h in enumerate(sorted(set(new)))}
        lab = [rank[h] for h in new]
    return (n, sum(bin(a).count("1") for a in adjbits) // 2, tuple(sorted(lab)),
            hash(tuple(sorted(hash((lab[v], tuple(sorted(lab[u] for u in range(n)
                 if (adjbits[v] >> u) & 1)))) for v in range(n)))))


def to_nx(n, adjbits):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for v in range(n):
        for u in range(v):
            if (adjbits[v] >> u) & 1:
                G.add_edge(u, v)
    return G


def extend(level, n):
    """level: list of adjbit-tuples on n vertices -> all on n+1, up to iso."""
    buckets = {}
    out = []
    for adj in level:
        # candidate neighbourhoods of the new vertex = independent sets
        cands = [0]
        for v in range(n):
            new = []
            for S in cands:
                if not (adj[v] & S):          # v not adjacent to anything in S
                    new.append(S | (1 << v))
            cands += new
        for S in cands:
            na = list(adj)
            for v in range(n):
                if (S >> v) & 1:
                    na[v] |= 1 << n
            na.append(S)
            na = tuple(na)
            k = wl_key(n + 1, na)
            b = buckets.setdefault(k, [])
            G = None
            dup = False
            for (oa, oG) in b:
                if oa == na:
                    dup = True
                    break
                if G is None:
                    G = to_nx(n + 1, na)
                if nx.is_isomorphic(G, oG):
                    dup = True
                    break
            if not dup:
                b.append((na, G if G is not None else to_nx(n + 1, na)))
                out.append(na)
    return out


if __name__ == "__main__":
    NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    level = [(0,)]
    allg = {1: level}
    print("exhaustive generation of triangle-free graphs up to isomorphism")
    for n in range(1, NMAX):
        t0 = time.time()
        level = extend(level, n)
        allg[n + 1] = level
        ok = "OK" if (n + 1 <= len(KNOWN) and len(level) == KNOWN[n]) else "MISMATCH"
        print("  n=%2d : %6d triangle-free graphs  (known %s)  %s   [%.0fs]"
              % (n + 1, len(level), KNOWN[n] if n < len(KNOWN) else "?", ok, time.time() - t0))
        sys.stdout.flush()
        if ok == "MISMATCH":
            print("  ABORT: generator disagrees with the known count")
            sys.exit(1)

    print()
    print("max_x Lambda over every MAXIMAL non-bipartite triangle-free graph:")
    overall = Fraction(0)
    for n in range(5, NMAX + 1):
        gs = []
        for adj in allg[n]:
            edges = [(u, v) for v in range(n) for u in range(v) if (adj[v] >> u) & 1]
            g = Graph(n, edges)
            if g.is_bipartite():
                continue
            # maximal?
            maximal = True
            for v in range(n):
                for u in range(v):
                    if u not in g.adj[v] and not (g.adj[u] & g.adj[v]):
                        maximal = False
                        break
                if not maximal:
                    break
            if maximal:
                gs.append(g)
        t0 = time.time()
        best = Fraction(0)
        wit = None
        for i, g in enumerate(gs):
            b, bx, ev = maximize(g, restarts=6, iters=20, seed=i, x0list=c5_starts(g, k=2, eps=(0.0, 0.05)))
            val, xr, _ = exact_check(g, bx)
            exact_probe(g, xr, "census")
            val = max(val, leak_scan(g, ncyc=3), exact_probe(g, [Fraction(1, n)] * n, "unif"))
            if val > best:
                best, wit = val, g.graph6()
            if val > ONE25:
                print("   *** OVER 1/25 ***", g.graph6(), val)
        overall = max(overall, best)
        print("  n=%2d : %4d maximal non-bipartite triangle-free graphs | max exact Lambda = %-8s = %.12f %s [%.0fs]"
              % (n, len(gs), best, float(best),
                 "== 1/25" if best == ONE25 else ("OVER" if best > ONE25 else "< 1/25"), time.time() - t0))
        sys.stdout.flush()
    print()
    print("OVERALL max exact Lambda over the full census = %s = %.12f" % (overall, float(overall)))
    print("VIOLATIONS (Lambda > proof bound, gamma < 25/2, bad certificate, or > 1/25):",
          VIOL if VIOL else "none")
