#!/usr/bin/env python3
# INDEPENDENT cross-check of the Q1'b refutation (written from scratch,
# different data structures / search order than q1b_counterexample.py).
#
# Counterexample A: 18-vertex bipartite H, anchors = full K_{3,3} rainbow core.
# Verifies: hypotheses of the lemma; NO ban-avoiding proper 3-colouring
# (two ways: anchor-only 729-tuple enumeration, and full-graph DFS);
# positive control with a non-rainbow gamma' (colouring exists -> DFS sound).
import itertools

names = ['x0','x1','x2','y0','y1','y2'] + [f'u{a}' for a in range(1,7)] + [f'w{b}' for b in range(1,7)]
idx = {n: i for i, n in enumerate(names)}
N = len(names)
adj = [set() for _ in range(N)]
def add(a, b):
    ia, ib = idx[a], idx[b]
    assert ib not in adj[ia], (a, b)
    adj[ia].add(ib); adj[ib].add(ia)

for i in range(3):
    for j in range(3):
        add(f'x{i}', f'y{j}')                                # full K_{3,3} core
for j in range(3):
    add(f'y{j}', f'u{2*j+1}'); add(f'y{j}', f'u{2*j+2}')
for i in range(3):
    add(f'x{i}', f'w{2*i+1}'); add(f'x{i}', f'w{2*i+2}')
for a in range(1, 7):
    for b in range(1, 7):
        if a != b:
            add(f'u{a}', f'w{b}')                            # K_{6,6} - PM

# hypothesis checks
P = {idx[n] for n in names if n[0] in 'xu'}
assert all(((v in P) != (u in P)) for v in range(N) for u in adj[v]), "bipartite"
deg = [len(adj[v]) for v in range(N)]
anchors = [idx[f'x{i}'] for i in range(3)] + [idx[f'y{j}'] for j in range(3)]
assert sorted(deg) == [5]*6 + [6]*12, deg
assert all(deg[a] == 5 for a in anchors)
seen = {0}; stack = [0]
while stack:
    v = stack.pop()
    for u in adj[v]:
        if u not in seen:
            seen.add(u); stack.append(u)
assert len(seen) == N, "connected"
print("check0: H OK (18 vtcs, bipartite, simple, connected, six deg-5 anchors, rest deg-6).")

ban = {idx[f'x{i}']: i for i in range(3)}
ban.update({idx[f'y{j}']: j for j in range(3)})

# check 1: anchor-only infeasibility (full K33 => already contradictory)
cnt_proper = cnt_ok = 0
for cols in itertools.product(range(3), repeat=6):
    cA = dict(zip(anchors, cols))
    if any(cA[idx[f'x{i}']] == cA[idx[f'y{j}']] for i in range(3) for j in range(3)):
        continue
    cnt_proper += 1
    if all(cA[a] != ban[a] for a in anchors):
        cnt_ok += 1
print(f"check1: anchor tuples proper on K33: {cnt_proper}; ban-avoiding among them: {cnt_ok} (expect 0)")

# check 2: full-graph exhaustive DFS, non-anchors FIRST (opposite order to the other script)
order = [v for v in range(N) if v not in anchors] + anchors
color = [-1]*N
def dfs(k, banmap):
    if k == N:
        return True
    v = order[k]
    for c in range(3):
        if banmap.get(v) == c:
            continue
        if any(color[u] == c for u in adj[v]):
            continue
        color[v] = c
        if dfs(k + 1, banmap):
            return True
        color[v] = -1
    return False
print("check2: ban-avoiding proper 3-colouring exists:", dfs(0, ban), "(expect False)")

# check 3: positive control -- gamma' with y-bans (0,1,0): colouring must exist
ban2 = dict(ban); ban2[idx['y2']] = 0
color = [-1]*N
print("check3: control gamma' (y2 ban -> 0) colouring exists:", dfs(0, ban2), "(expect True)")

# check 4: classification of anchor-core solutions (sigma,tau)
sols = []
for s in itertools.product(range(3), repeat=3):
    if any(s[i] == i for i in range(3)):
        continue
    for t in itertools.product(range(3), repeat=3):
        if any(t[j] == j for j in range(3)):
            continue
        if all(s[i] != t[j] for i in range(3) for j in range(3) if i != j):
            sols.append((s, t))
print("check4: solutions of {sigma(i)!=i, tau(j)!=j, sigma(i)!=tau(j) for i!=j}:", sols)

# graph6 of H
def graph6(n, edges):
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (i, j) in edges else 0)
    while len(bits) % 6:
        bits.append(0)
    s = chr(n + 63)
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k+6]:
            v = v * 2 + b
        s += chr(v + 63)
    return s
E = {(min(v, u), max(v, u)) for v in range(N) for u in adj[v]}
print("graph6:", graph6(N, E))
