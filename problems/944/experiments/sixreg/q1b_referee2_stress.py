#!/usr/bin/env python3
# Adversarial stress test of the PROOF SKELETON's step (3) repair recipes,
# applied EXACTLY as stated, on the extremal configuration of step (2):
#   P-anchors x0,x1,x2 with gamma(x_i)=i, Q-anchors y0,y1,y2 with gamma(y_j)=j,
#   x_i ~ y_j for all i != j, and matched pairs x_i ~ y_i present for an
#   arbitrary subset M of {0,1,2}.
# Recipes quoted from the skeleton:
#   R1: sigma = (2,0,2), tau = (1,0,1)      ("two-valued families")
#   R2: sigma = tau = (1,2,0)               ("cyclic ... when no blockers")
# A recipe SUCCEEDS on (M) iff sigma(i) != i, tau(j) != j (ban-avoidance) and
# sigma(i) != tau(j) for every present anchor-anchor edge (properness).

from itertools import product, combinations
import random

def check(sigma, tau, M):
    fails = []
    for i in range(3):
        if sigma[i] == i: fails.append(f'BAN  sigma({i})={sigma[i]}=gamma(x{i})')
        if tau[i] == i:   fails.append(f'BAN  tau({i})={tau[i]}=gamma(y{i})')
    for i in range(3):
        for j in range(3):
            if (i != j or i in M) and sigma[i] == tau[j]:
                fails.append(f'EDGE x{i}~y{j} monochromatic colour {sigma[i]}')
    return fails

print('=== Recipe R1: sigma=(2,0,2), tau=(1,0,1), applied verbatim ===')
for r in range(4):
    for M in combinations(range(3), r):
        f = check((2,0,2), (1,0,1), set(M))
        print(f'  matched set {set(M) if M else "{}"}: '
              f'{"OK" if not f else "FAILS: " + "; ".join(f)}')

print('=== Recipe R2: sigma=tau=(1,2,0), applied verbatim ===')
for r in range(4):
    for M in combinations(range(3), r):
        f = check((1,2,0), (1,2,0), set(M))
        print(f'  matched set {set(M) if M else "{}"}: '
              f'{"OK" if not f else "FAILS: " + "; ".join(f)}')

print()
print('=== Exhaustive core solubility per matched set (729 assignments) ===')
for r in range(4):
    for M in combinations(range(3), r):
        sols = [st for st in product(range(3), repeat=6)
                if not check(st[:3], st[3:], set(M))]
        print(f'  matched set {set(M) if M else "{}"}: {len(sols)} solutions'
              + (f' {sols}' if 0 < len(sols) <= 3 else ''))

# ---------------------------------------------------------------------------
# Random instances of the extremal configuration: embed the FULL K_{3,3}
# anchor core (rainbow gammas both sides) into a random hypothesis-compliant
# graph; the lemma must then fail for EVERY such graph. We test many wirings.
# Construction: anchors as in counterexample A; the deg-6 padding vertices
# u1..u6 / w1..w6 are wired by a random 5-regular bipartite graph (random
# union of 5 disjoint perfect matchings, retry on collision), and each x_i /
# y_j gets 2 private padding neighbours via a random assignment.
# ---------------------------------------------------------------------------
from collections import deque

def random_instance(rng):
    P = [f'x{i}' for i in range(3)] + [f'u{k}' for k in range(1, 7)]
    Q = [f'y{j}' for j in range(3)] + [f'w{k}' for k in range(1, 7)]
    E = [(f'x{i}', f'y{j}') for i in range(3) for j in range(3)]  # full K33
    # random assignment of the 6 w's (2 each) to x's, 6 u's (2 each) to y's
    ws = rng.sample(range(1, 7), 6); us = rng.sample(range(1, 7), 6)
    for i in range(3):
        E += [(f'x{i}', f'w{ws[2*i]}'), (f'x{i}', f'w{ws[2*i+1]}')]
        E += [(f'y{i}', f'u{us[2*i]}'), (f'y{i}', f'u{us[2*i+1]}')]
    # random 5-regular simple bipartite graph on u1..6 x w1..6
    while True:
        used = set(); ok = True
        for _ in range(5):
            perm = rng.sample(range(1, 7), 6)
            pairs = list(zip(range(1, 7), perm))
            if any(p in used for p in pairs): ok = False; break
            used |= set(pairs)
        if ok: break
    E += [(f'u{k}', f'w{l}') for k, l in used]
    return P, Q, E

def hypotheses_ok(P, Q, E):
    V = P + Q; adj = {v: set() for v in V}
    es = set()
    for a, b in E:
        e = frozenset((a, b))
        if e in es: return None
        es.add(e); adj[a].add(b); adj[b].add(a)
    deg = {v: len(adj[v]) for v in V}
    if max(deg.values()) > 6: return None
    if sorted(v for v in V if deg[v] == 5) != ['x0','x1','x2','y0','y1','y2']:
        return None
    if any(deg[v] != 6 for v in V if deg[v] != 5): return None
    seen = {V[0]}; dq = deque([V[0]])
    while dq:
        v = dq.popleft()
        for u in adj[v]:
            if u not in seen: seen.add(u); dq.append(u)
    if len(seen) != len(V): return None
    return adj

BAN = {'x0': 0, 'x1': 1, 'x2': 2, 'y0': 0, 'y1': 1, 'y2': 2}

def exact_count(P, Q, adj):
    total = 0
    for assign in product(range(3), repeat=len(P)):
        col = dict(zip(P, assign))
        if any(col[a] == BAN[a] for a in P if a in BAN): continue
        ways = 1
        for q in Q:
            used = {col[p] for p in adj[q]}
            ways *= sum(1 for c in range(3)
                        if c not in used and c != BAN.get(q, -1))
            if ways == 0: break
        total += ways
    return total

print()
print('=== 30 RANDOM hypothesis-compliant graphs containing the full-K33 '
      'rainbow core ===')
rng = random.Random(944)
made = 0; tried = 0
while made < 30 and tried < 2000:
    tried += 1
    P, Q, E = random_instance(rng)
    adj = hypotheses_ok(P, Q, E)
    if adj is None: continue
    made += 1
    t = exact_count(P, Q, adj)
    status = 'counterexample (0 colourings)' if t == 0 else f'LEMMA SURVIVES ({t})'
    print(f'  instance {made:2d}: |E|={len(E)}  -> {status}')
    assert t == 0
print(f'generated {made} valid random instances out of {tried} attempts; '
      f'ALL are counterexamples.')
