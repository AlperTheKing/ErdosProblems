#!/usr/bin/env python3
"""My exhaustive gate of GPT R39's 8-vertex four-state neutral square rotor.
Claims to verify (ALL my own code):
  G1 graph: 8 vtx, blue {ax,yb,pm,vq,xm,my,yv,vx}, bad {ab,pq}; bipartition {x,y,p,q}|{m,v,a,b};
     triangle-free; blue graph connected.
  G2 maxcut: displayed cut = 8 = exhaustive maximum over 2^8 cuts (and blue = exactly the cross edges).
  G3 row DB completeness: 4-edge blue paths a->b are exactly {A_m,A_v}; p->q exactly {B_x,B_y} (my DFS).
  G4 the four states cycle by two-edge detours: per state, the unselected square edge is as tabled; the
     transition replaces exactly the middle of one row with the other middle, and the replacement is a
     member of the family (completeness realized).
  G5 scoped semantics per state: active graph = the single unselected square edge; its component contains
     NO bad atom's endpoint pair => NO active bad-containing component => scoped obligations = 0 =>
     collision defect 0 in every state (so the bare rotor is NOT a positive-defect falsifier — consistent
     with GPT's own honesty and with the N<=12 census).
  G6 collision-mass rotation: per state, the two selected rows share exactly the two tabled colliding
     vertices, each with pair-multiplicity 2 => 2 owners x 2 units x 2 halves = 8 halves (if scope were
     forced active) — the "mass rotates, never grows" claim.
ASCII prints only."""
from itertools import combinations

names = ['a', 'b', 'p', 'q', 'x', 'y', 'm', 'v']
idx = {s: i for i, s in enumerate(names)}
a, b, p, q, x, y, m, v = (idx[s] for s in names)

blue = {frozenset(e) for e in [(a, x), (y, b), (p, m), (v, q), (x, m), (m, y), (y, v), (v, x)]}
bad = {frozenset(e) for e in [(a, b), (p, q)]}
edges = blue | bad
assert len(edges) == 10 and not (blue & bad)

adj = [set() for _ in range(8)]
for e in edges:
    u, w = tuple(e)
    adj[u].add(w)
    adj[w].add(u)

# G1 triangle-free + bipartition realizes blue as cross
tri = any(adj[u] & adj[w] for u, w in combinations(range(8), 2) if w in adj[u])
assert not tri, "triangle"
sideA = {x, y, p, q}
def side(u):
    return u in sideA
for e in blue:
    u, w = tuple(e)
    assert side(u) != side(w), "blue not cross"
for e in bad:
    u, w = tuple(e)
    assert side(u) == side(w), "bad not same-side"
# blue connectivity
seen = {a}
stack = [a]
while stack:
    u = stack.pop()
    for w in adj[u]:
        if frozenset((u, w)) in blue and w not in seen:
            seen.add(w)
            stack.append(w)
assert seen == set(range(8)), "blue graph disconnected"

# G2 exhaustive maxcut over 2^8
best = 0
for mask in range(256):
    c = sum(1 for e in edges for u, w in [tuple(e)] if ((mask >> u) ^ (mask >> w)) & 1)
    best = max(best, c)
shown = sum(1 for e in edges for u, w in [tuple(e)] if side(u) != side(w))
assert shown == len(blue) == 8 and best == 8, (shown, best)

# G3 complete row families (my DFS over blue 4-paths)
def rows_between(s, t):
    out = []
    def dfs(path):
        if len(path) == 5:
            if path[-1] == t:
                out.append(tuple(path))
            return
        for w in range(8):
            if w not in path and frozenset((path[-1], w)) in blue:
                if len(path) == 4 and w != t:
                    continue
                dfs(path + [w])
    dfs([s])
    return sorted(out)

fam_ab = rows_between(a, b)
fam_pq = rows_between(p, q)
A_m, A_v = (a, x, m, y, b), (a, x, v, y, b)
B_x, B_y = (p, m, x, v, q), (p, m, y, v, q)
assert sorted([A_m, A_v]) == fam_ab, fam_ab
assert sorted([B_x, B_y]) == fam_pq, fam_pq

# G4 four states + detour cycle + per-state unselected square edge
square = [frozenset((x, m)), frozenset((m, y)), frozenset((y, v)), frozenset((v, x))]
states = {
    'w_mx': (A_m, B_x), 'w_my': (A_m, B_y), 'w_vy': (A_v, B_y), 'w_vx': (A_v, B_x),
}
expected_missing = {'w_mx': frozenset((y, v)), 'w_my': frozenset((x, v)),
                    'w_vy': frozenset((x, m)), 'w_vx': frozenset((m, y))}
def support(rows):
    return {frozenset((r[i], r[i + 1])) for r in rows for i in range(4)}
for st, rows in states.items():
    sup = support(rows)
    missing = [e for e in square if e not in sup]
    assert len(missing) == 1 and missing[0] == expected_missing[st], (st, missing)
# transitions: w_mx -> w_my replaces B_x by B_y = middle x -> y? B_x=(p,m,x,v,q), B_y=(p,m,y,v,q):
# differ exactly at position 2 (middle of the inner triple m,?,v). Check all four cycle steps are
# one-row middle-replacements within the same family:
cycle = [('w_mx', 'w_my'), ('w_my', 'w_vy'), ('w_vy', 'w_vx'), ('w_vx', 'w_mx')]
for s1, s2 in cycle:
    r1, r2 = states[s1], states[s2]
    diff = [(u, w) for u, w in zip(r1, r2) if u != w]
    assert len(diff) == 1, (s1, s2)
    old, new = diff[0]
    delta = [i for i in range(5) if old[i] != new[i]]
    assert len(delta) == 1 and delta[0] in (1, 2, 3), (old, new)  # a middle vertex swap
    # replacement stays in the same complete family
    fam = fam_ab if old[0] == a else fam_pq
    assert old in fam and new in fam

# G5 scoped semantics: active graph per state = the missing square edge only; no bad-containing component
for st, rows in states.items():
    sup = support(rows)
    sel = {u for r in rows for u in r}
    assert sel == set(range(8))
    act = {e for e in blue if tuple(e)[0] in sel and tuple(e)[1] in sel and e not in sup}
    assert act == {expected_missing[st]}, (st, act)
    comp = set(expected_missing[st])
    has_bad = any(set(t) <= comp for t in (map(tuple, bad)))
    assert not has_bad
    # => no active bad-containing component => no scoped obligations => defect 0

# G6 collision mass rotates: per state the two rows co-occur exactly on the tabled pair of vertices
expected_colliders = {'w_mx': {m, x}, 'w_my': {m, y}, 'w_vy': {v, y}, 'w_vx': {v, x}}
for st, rows in states.items():
    shared = set(rows[0]) & set(rows[1])
    assert shared == expected_colliders[st], (st, shared)
    # each shared vertex is in both rows: diagonal multiplicity 2 => 1 excess => 2 halves; and the PAIR
    # (u,w) for u,w shared appears in both rows => 1 excess => 2 halves each direction.
    u, w = tuple(shared)
    units = 0
    for vert in (u, w):
        occ = sum(1 for r in rows if vert in r)
        units += max(0, occ - 1)          # diagonal
        pc = sum(1 for r in rows if u in r and w in r)
        units += max(0, pc - 1)           # off-diagonal with the other shared vertex
    assert units == 4, (st, units)         # 4 units x 2 halves = 8 halves, identical in every state

print("CLAUDE-GATE=PASS (exhaustive)")
print("G1 tri-free, blue=cross bipartition, blue-connected | G2 maxcut=8 exhaustive(2^8) = displayed")
print("G3 families complete: ab={A_m,A_v}, pq={B_x,B_y} (my DFS) | G4 4-state cycle = one-middle swaps in-family")
print("G5 active graph per state = the single missing square edge, NO bad-containing component => defect 0")
print("G6 collision mass rotates: 8 halves in every state (pairs {mx},{my},{vy},{vx})")
print("VERDICT: rotor construction GENUINE; bare rotor NOT a falsifier (vacuous scope); graft question OPEN")
