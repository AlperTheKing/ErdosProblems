#!/usr/bin/env python3
# Refutation of LEMMA Q1'b ("spread bipartite avoid-completeness").
#
# Two explicit counterexamples, each: connected bipartite H, Delta<=6,
# EXACTLY six degree-5 vertices (anchors x0,x1,x2 in P; y0,y1,y2 in Q),
# all other vertices degree 6, gamma(x_i)=i, gamma(y_j)=j, and NO proper
# 3-colouring psi with psi(a) != gamma(a) for every anchor a.
#
#   A: anchors induce the FULL K_{3,3}.
#   B: anchors induce K_{3,3} MINUS the perfect matching (exactly the
#      "extremal configuration" of skeleton step (2), zero matched edges),
#      plus one non-anchor blocker u* adjacent to y0,y1,y2.
#
# Also enumerates the 3^6 = 729 anchor-core assignments to prove:
# with zero matched edges the ONLY solutions are sigma = tau = a 3-cycle
# (so both sides are forced RAINBOW), and any matched edge kills both.

from itertools import product
from collections import deque

def build_A():
    P = [f'x{i}' for i in range(3)] + [f'u{k}' for k in range(1, 7)]
    Q = [f'y{j}' for j in range(3)] + [f'w{k}' for k in range(1, 7)]
    E = []
    for i in range(3):
        for j in range(3):
            E.append((f'x{i}', f'y{j}'))                 # full K_{3,3} core
    for i in range(3):
        E.append((f'x{i}', f'w{2*i+1}')); E.append((f'x{i}', f'w{2*i+2}'))
        E.append((f'y{i}', f'u{2*i+1}')); E.append((f'y{i}', f'u{2*i+2}'))
    for k in range(1, 7):
        for l in range(1, 7):
            if k != l:
                E.append((f'u{k}', f'w{l}'))             # K_{6,6} minus PM
    return P, Q, E

def build_B():
    P = [f'x{i}' for i in range(3)] + ['us'] + [f'u{k}' for k in range(1, 6)]
    Q = [f'y{j}' for j in range(3)] + [f'w{k}' for k in range(1, 7)]
    E = []
    for i in range(3):
        for j in range(3):
            if i != j:
                E.append((f'x{i}', f'y{j}'))             # K_{3,3} minus PM
    for j in range(3):
        E.append(('us', f'y{j}'))                        # blocker u*
    for w in (1, 2, 3): E.append(('x0', f'w{w}'))
    for w in (4, 5, 6): E.append(('x1', f'w{w}'))
    for w in (1, 2, 4): E.append(('x2', f'w{w}'))
    for w in (3, 5, 6): E.append(('us', f'w{w}'))
    E += [('y0','u1'), ('y0','u2'), ('y1','u3'), ('y1','u4'),
          ('y2','u5'), ('y2','u1')]
    removed = {(1,1), (1,2), (2,3), (3,4), (4,5), (5,6)}
    for k in range(1, 6):
        for l in range(1, 7):
            if (k, l) not in removed:
                E.append((f'u{k}', f'w{l}'))             # K_{5,6} minus 6 edges
    return P, Q, E

def validate(P, Q, E, name):
    V = P + Q
    assert len(set(V)) == len(V)
    es = set(map(frozenset, E))
    assert len(es) == len(E), 'multi-edge'
    sP, sQ = set(P), set(Q)
    for a, b in E:
        assert (a in sP) != (b in sP), 'edge inside one side -> not bipartite'
    deg = {v: 0 for v in V}
    for a, b in E:
        deg[a] += 1; deg[b] += 1
    assert max(deg.values()) <= 6
    five = sorted(v for v in V if deg[v] == 5)
    assert five == ['x0','x1','x2','y0','y1','y2'], five
    assert all(deg[v] == 6 for v in V if v not in five)
    adj = {v: set() for v in V}
    for a, b in E:
        adj[a].add(b); adj[b].add(a)
    seen = {V[0]}; dq = deque([V[0]])
    while dq:
        v = dq.popleft()
        for u in adj[v]:
            if u not in seen:
                seen.add(u); dq.append(u)
    assert len(seen) == len(V), 'not connected'
    print(f'{name}: |V|={len(V)} |E|={len(E)} bipartite, simple, connected, '
          f'Delta<=6, exactly six deg-5 vertices = anchors. OK')
    return adj

def count_colourings(adj, banned, cap=2):
    # anchors first => failures detected at depth <= 7
    anchors = ['x0','x1','x2','y0','y1','y2']
    order = anchors + [v for v in adj if v not in anchors]
    col, n, cnt = {}, len(order), 0
    def rec(d):
        nonlocal cnt
        if cnt >= cap: return
        if d == n:
            cnt += 1; return
        v = order[d]
        for c in range(3):
            if c == banned.get(v, -1): continue
            if any(col.get(u) == c for u in adj[v]): continue
            col[v] = c; rec(d + 1); del col[v]
    rec(0)
    return cnt

def core_solutions(matched):
    # sigma(i)!=i, tau(j)!=j, sigma(i)!=tau(j) for i!=j, and also for i=j in `matched`
    sols = []
    for st in product(range(3), repeat=6):
        s, t = st[:3], st[3:]
        if any(s[i] == i or t[i] == i for i in range(3)): continue
        if any(s[i] == t[j] for i in range(3) for j in range(3)
               if i != j or i in matched): continue
        sols.append((s, t))
    return sols

if __name__ == '__main__':
    banned = {'x0':0, 'x1':1, 'x2':2, 'y0':0, 'y1':1, 'y2':2}
    for name, build in (('A (full K33 core)', build_A),
                        ('B (K33-PM core + blocker u*)', build_B)):
        P, Q, E = build()
        adj = validate(P, Q, E, name)
        m = count_colourings(adj, banned)
        print(f'{name}: number of valid colourings found (cap 2) = {m}')
        assert m == 0, 'LEMMA NOT REFUTED?!'
    print()
    print('anchor-core solution sets (sigma|tau), constraints of skeleton step (2):')
    for matched in ([], [0], [1], [2], [0,1], [0,2], [1,2], [0,1,2]):
        sols = core_solutions(matched)
        print(f'  matched edges {matched}: {len(sols)} solutions '
              f'{sols if len(sols) <= 4 else ""}')
    print()
    print('LEMMA Q1\'b REFUTED by counterexamples A and B.')
