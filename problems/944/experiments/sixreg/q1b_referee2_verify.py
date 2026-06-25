#!/usr/bin/env python3
# INDEPENDENT adversarial re-verification of the claimed Q1'b refutation.
# Method differs from the claimant's backtracker: since H is bipartite,
# enumerate ALL 3^|P| assignments to P (P is an independent set, so any
# assignment is proper on P); given that, Q-vertices are mutually
# independent, so the number of completions is the product over q in Q of
# |{c in {0,1,2} : c != ban(q), c not used by any P-neighbour of q}|.
# This gives the EXACT total count of valid colourings (no cap, no pruning).

from itertools import product
from collections import deque
import sys

sys.path.insert(0, r'E:\Projects\ErdosProblems\problems\944\experiments\sixreg')
from q1b_counterexample import build_A, build_B   # graphs as DATA only

BAN = {'x0': 0, 'x1': 1, 'x2': 2, 'y0': 0, 'y1': 1, 'y2': 2}
ANCH = ['x0', 'x1', 'x2', 'y0', 'y1', 'y2']

def my_validate(P, Q, E, name):
    V = P + Q
    ok = True
    # simple graph, no self loops, no multi-edges
    es = set()
    for a, b in E:
        assert a != b, f'{name}: self-loop'
        e = frozenset((a, b))
        assert e not in es, f'{name}: multi-edge {a},{b}'
        es.add(e)
    adj = {v: set() for v in V}
    for a, b in E:
        adj[a].add(b); adj[b].add(a)
    # connectivity + bipartiteness checked from scratch by BFS 2-colouring,
    # ignoring the declared parts:
    side = {V[0]: 0}; dq = deque([V[0]])
    while dq:
        v = dq.popleft()
        for u in adj[v]:
            if u not in side:
                side[u] = 1 - side[v]; dq.append(u)
            else:
                assert side[u] != side[v], f'{name}: ODD CYCLE -> not bipartite'
    assert len(side) == len(V), f'{name}: NOT connected'
    # declared parts consistent with BFS sides
    s0 = {v for v in V if side[v] == 0}
    assert s0 == set(P) or s0 == set(Q), f'{name}: declared parts wrong'
    # degree profile
    deg = {v: len(adj[v]) for v in V}
    assert max(deg.values()) <= 6, f'{name}: Delta>6'
    five = sorted(v for v in V if deg[v] == 5)
    assert five == sorted(ANCH), f'{name}: deg-5 set is {five}'
    assert all(deg[v] == 6 for v in V if v not in ANCH), f'{name}: non-anchor not deg 6'
    print(f'{name}: hypotheses INDEPENDENTLY verified '
          f'(|V|={len(V)}, |E|={len(E)}, bipartite by BFS, connected, '
          f'Delta<=6, deg-5 set == anchors, rest deg 6)')
    return adj

def exact_count(P, Q, adj):
    total = 0
    n = len(P)
    for assign in product(range(3), repeat=n):
        col = dict(zip(P, assign))
        # respect bans on P-side anchors
        if any(col[a] == BAN[a] for a in P if a in BAN):
            continue
        ways = 1
        for q in Q:
            used = {col[p] for p in adj[q]}        # all nbrs of q are in P
            avail = [c for c in range(3) if c not in used and c != BAN.get(q, -1)]
            ways *= len(avail)
            if ways == 0:
                break
        total += ways
    return total

if __name__ == '__main__':
    for name, build in (('A', build_A), ('B', build_B)):
        P, Q, E = build()
        adj = my_validate(P, Q, E, name)
        # sanity: every Q-vertex's neighbours really are all in P (bipartite data)
        sP = set(P)
        assert all(adj[q] <= sP for q in Q)
        t = exact_count(P, Q, adj)
        print(f'{name}: EXACT number of proper 3-colourings avoiding all bans = {t}')
        # control: same graph, bans removed -> should be > 0 (graph is 2-colourable!)
        nb = BAN.copy(); BAN.clear()
        t2 = exact_count(P, Q, adj)
        BAN.update(nb)
        print(f'{name}: control without bans: {t2} proper 3-colourings (>0 expected)')
        assert t2 > 0
        assert t == 0, f'{name}: REFUTATION FAILS, found {t} colourings'
    print('\nBOTH counterexamples INDEPENDENTLY CONFIRMED: 0 ban-avoiding colourings.')
