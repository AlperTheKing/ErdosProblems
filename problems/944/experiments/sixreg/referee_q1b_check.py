#!/usr/bin/env python3
# Independent adversarial re-verification of q1b_counterexample.py.
# Rebuilds both graphs, re-validates every lemma hypothesis with separate code,
# then counts ALL valid colourings by a different exhaustive method:
#   enumerate all 2^6 = 64 ban-respecting anchor assignments, filter by
#   anchor-anchor edges, and for each survivor do an UNCAPPED backtracking
#   extension over the 12 non-anchors in BFS order.
from collections import deque
from itertools import product

def build_A():
    E = []
    for i in range(3):
        for j in range(3):
            E.append((f'x{i}', f'y{j}'))
        E += [(f'x{i}', f'w{2*i+1}'), (f'x{i}', f'w{2*i+2}'),
              (f'y{i}', f'u{2*i+1}'), (f'y{i}', f'u{2*i+2}')]
    for k in range(1, 7):
        for l in range(1, 7):
            if k != l:
                E.append((f'u{k}', f'w{l}'))
    P = [f'x{i}' for i in range(3)] + [f'u{k}' for k in range(1, 7)]
    Q = [f'y{j}' for j in range(3)] + [f'w{k}' for k in range(1, 7)]
    return P, Q, E

def build_B():
    E = []
    for i in range(3):
        for j in range(3):
            if i != j:
                E.append((f'x{i}', f'y{j}'))
    for j in range(3):
        E.append(('us', f'y{j}'))
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
                E.append((f'u{k}', f'w{l}'))
    P = [f'x{i}' for i in range(3)] + ['us'] + [f'u{k}' for k in range(1, 6)]
    Q = [f'y{j}' for j in range(3)] + [f'w{k}' for k in range(1, 7)]
    return P, Q, E

ANCHORS = ['x0','x1','x2','y0','y1','y2']
BAN = {'x0':0,'x1':1,'x2':2,'y0':0,'y1':1,'y2':2}

def validate(P, Q, E, name):
    V = P + Q
    assert len(set(V)) == 18 and len(V) == 18
    pairs = set()
    for a, b in E:
        assert a != b
        key = (min(a,b), max(a,b))
        assert key not in pairs, f'multi-edge {key}'
        pairs.add(key)
    sP, sQ = set(P), set(Q)
    assert all((a in sP and b in sQ) or (a in sQ and b in sP) for a, b in E), 'not bipartite layout'
    deg = {v: 0 for v in V}
    adj = {v: [] for v in V}
    for a, b in E:
        deg[a] += 1; deg[b] += 1
        adj[a].append(b); adj[b].append(a)
    assert all(d <= 6 for d in deg.values()), 'Delta>6'
    d5 = sorted(v for v in V if deg[v] == 5)
    d6 = sorted(v for v in V if deg[v] == 6)
    assert d5 == sorted(ANCHORS), f'deg-5 set wrong: {d5}'
    assert len(d5) + len(d6) == 18, 'a vertex has degree not in {5,6}'
    # connectivity (independent BFS)
    seen = {V[0]}; dq = deque([V[0]])
    while dq:
        v = dq.popleft()
        for u in adj[v]:
            if u not in seen:
                seen.add(u); dq.append(u)
    assert len(seen) == 18, 'disconnected'
    # no odd cycle double-check: 2-colour BFS
    side = {V[0]: 0}; dq = deque([V[0]])
    while dq:
        v = dq.popleft()
        for u in adj[v]:
            if u not in side:
                side[u] = 1 - side[v]; dq.append(u)
            else:
                assert side[u] != side[v], 'odd cycle!'
    print(f'{name}: hypotheses OK (18 vtx, 51 edges={len(E)}, bipartite/simple/'
          f'connected, Delta<=6, deg-5 set == anchors)')
    return adj

def count_all(adj, name):
    anchor_edges = [(a, b) for a in ANCHORS for b in adj[a] if b in ANCHORS and a < b]
    rest = [v for v in adj if v not in ANCHORS]
    # BFS order over non-anchors starting from neighbours of anchors
    order, seen = [], set(ANCHORS)
    dq = deque(ANCHORS)
    while dq:
        v = dq.popleft()
        for u in adj[v]:
            if u not in seen:
                seen.add(u); order.append(u); dq.append(u)
    assert sorted(order) == sorted(rest)
    total, anchor_ok = 0, 0
    for cs in product(range(3), repeat=6):
        col = dict(zip(ANCHORS, cs))
        if any(col[a] == BAN[a] for a in ANCHORS):
            continue
        if any(col[a] == col[b] for a, b in anchor_edges):
            continue
        anchor_ok += 1
        # uncapped exhaustive extension
        def ext(d):
            nonlocal total
            if d == len(order):
                total += 1; return
            v = order[d]
            for c in range(3):
                if all(col.get(u) != c for u in adj[v]):
                    col[v] = c; ext(d + 1); del col[v]
        ext(0)
        for v in order:
            col.pop(v, None)
    print(f'{name}: ban+edge-respecting anchor assignments = {anchor_ok}; '
          f'TOTAL valid colourings of H (uncapped) = {total}')
    return anchor_ok, total

if __name__ == '__main__':
    for name, build in (('A', build_A), ('B', build_B)):
        P, Q, E = build()
        adj = validate(P, Q, E, name)
        aok, tot = count_all(adj, name)
        assert tot == 0, f'{name}: COLOURING EXISTS -> refutation wrong'
    # independent re-check of the matched-edge core enumeration
    for matched in ([], [0], [1], [2], [0,1], [0,2], [1,2], [0,1,2]):
        sols = []
        for st in product(range(3), repeat=6):
            s, t = st[:3], st[3:]
            if any(s[i] == i or t[i] == i for i in range(3)): continue
            bad = False
            for i in range(3):
                for j in range(3):
                    if (i != j or i in matched) and s[i] == t[j]:
                        bad = True
            if not bad: sols.append((s, t))
        print(f'core matched={matched}: {len(sols)} sols {sols if len(sols)<=4 else ""}')
    print('REFEREE: refutation independently CONFIRMED.')
