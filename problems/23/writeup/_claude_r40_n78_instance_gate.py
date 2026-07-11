#!/usr/bin/env python3
"""My independent gate of GPT R40's explicit N=78 grafted-rotor instance (built from the pinned spec ONLY).
Verifies: counts N=78/|B|=137/|M|=27/|E|=164; triangle-free; displayed cut = 137; blue connected; all 27
bads blue-distance exactly 4; rotor row histogram {54:7, 63:10, 75:1} (my DFS); support bads unique rows;
9/8 inclusion-minimality arithmetic; per-state active scope {24,18,18,24} + scoped collision demand
{264,180,180,264}; and the collapse mechanism sanity (P1-style zero-pair supply >= demand per owner).
ASCII prints only."""
from itertools import combinations, product
import collections

A = list(range(0, 3)); B = list(range(3, 6)); P = list(range(6, 9)); Q = list(range(9, 12))
X = list(range(12, 15)); Y = list(range(15, 18)); M = list(range(18, 21)); V = list(range(21, 24))
r_, cL, cR = 24, 25, 26
L = [27, 28, 29]; R = [30, 31, 32]

blue, bad = set(), set()
def be(u, v): blue.add(frozenset((u, v)))
def me(u, v): bad.add(frozenset((u, v)))
for cls_a, cls_b in [(A, X), (Y, B), (P, M), (V, Q), (X, M), (M, Y), (Y, V), (V, X)]:
    for u, v in product(cls_a, cls_b): be(u, v)
for u, v in product(A, B): me(u, v)
for u, v in product(P, Q): me(u, v)
be(0, 6); be(1, 9)                                    # grafts
for e in [(r_, cL), (r_, cR)] + [(cL, l) for l in L] + [(cR, rr) for rr in R]: be(*e)
for u, v in product(L, R): me(u, v)
locks = []
k = 0
for l in L:
    for rr in R:                                       # lex order over L x R
        priv = list(range(33 + 5 * k, 38 + 5 * k))
        path = [l] + priv + [rr]
        for i in range(6): be(path[i], path[i + 1])
        locks.append((l, rr, priv))
        k += 1
be(2, 34)                                              # bridge
E = blue | bad
N = 78
assert len(blue) == 137 and len(bad) == 27 and len(E) == 164, (len(blue), len(bad), len(E))
assert max(max(e) for e in E) == 77

adj = [set() for _ in range(N)]
for e in E:
    u, v = tuple(e)
    adj[u].add(v); adj[v].add(u)

# triangle-free
for u, v in combinations(range(N), 2):
    if v in adj[u]:
        assert not (adj[u] & adj[v]), f"triangle at {u},{v}"

# displayed cut: side0 = X,Y,P,Q + L,R,r_ + lock privates p2,p4; side1 = A,B,M,V + cL,cR + p1,p3,p5
side0 = set(X) | set(Y) | set(P) | set(Q) | {r_} | set(L) | set(R)
for (l, rr, priv) in locks:
    side0 |= {priv[1], priv[3]}
side = [0 if v in side0 else 1 for v in range(N)]
for e in blue:
    u, v = tuple(e); assert side[u] != side[v], f"blue not cross {e}"
for e in bad:
    u, v = tuple(e); assert side[u] == side[v], f"bad not same {e}"
cut = sum(1 for e in E for u, v in [tuple(e)] if side[u] != side[v])
assert cut == 137

# blue connectivity
seen, stack = {0}, [0]
while stack:
    u = stack.pop()
    for w in adj[u]:
        if frozenset((u, w)) in blue and w not in seen:
            seen.add(w); stack.append(w)
assert seen == set(range(N)), f"blue disconnected: {len(seen)}"

# bad distances exactly 4 in blue graph (BFS)
def bfs_blue(s):
    d = {s: 0}; dq = collections.deque([s])
    while dq:
        u = dq.popleft()
        for w in adj[u]:
            if frozenset((u, w)) in blue and w not in d:
                d[w] = d[u] + 1; dq.append(w)
    return d
for e in bad:
    u, v = tuple(e)
    assert bfs_blue(u).get(v) == 4, f"bad {e} not dist 4"

# complete row families (my DFS)
def rows_between(s, t):
    out = []
    def dfs(path):
        if len(path) == 5:
            if path[-1] == t: out.append(tuple(path))
            return
        for w in adj[path[-1]]:
            if w not in path and frozenset((path[-1], w)) in blue:
                if len(path) == 4 and w != t: continue
                dfs(path + [w])
    dfs([s])
    return out

rotor_bads = sorted(tuple(sorted(e)) for e in bad if max(e) < 24)
supp_bads = sorted(tuple(sorted(e)) for e in bad if min(e) >= 27)
hist = collections.Counter()
fams = {}
for u, v in rotor_bads:
    f = rows_between(u, v); fams[(u, v)] = f; hist[len(f)] += 1
assert dict(hist) == {54: 7, 63: 10, 75: 1}, dict(hist)
for u, v in supp_bads:
    f = rows_between(u, v); fams[(u, v)] = f
    assert len(f) == 1, (u, v, len(f))

# 9/8 minimality arithmetic
for size in range(1, 9):
    for sub in combinations(list(product(L, R)), size):
        Ls = {l for l, _ in sub}; Rs = {rr for _, rr in sub}
        assert len(sub) <= 2 + len(Ls) + len(Rs)
assert 9 > 2 + 3 + 3

# four macro states
def rowAM(i, j): return (A[i], X[i], M[(i + j) % 3], Y[j], B[j])
def rowAV(i, j): return (A[i], X[i], V[(i + j) % 3], Y[j], B[j])
def rowBX(i, j): return (P[i], M[i], X[(i + j) % 3], V[j], Q[j])
def rowBY(i, j): return (P[i], M[i], Y[(i + j) % 3], V[j], Q[j])
def supprow(l, rr): return (l, cL, r_, cR, rr)

states = []
for aw, bw in [(rowAM, rowBX), (rowAM, rowBY), (rowAV, rowBY), (rowAV, rowBX)]:
    rows = [aw(i, j) for i in range(3) for j in range(3)] + \
           [bw(i, j) for i in range(3) for j in range(3)] + \
           [supprow(l, rr) for l in L for rr in R]
    states.append(rows)

# every selected row is a member of its complete family
for rows in states:
    for row in rows:
        key = tuple(sorted((row[0], row[4])))
        assert row in fams[key] or tuple(reversed(row)) in fams[key], f"row {row} not in family"

def active_scope(rows):
    support = {frozenset((rr[i], rr[i + 1])) for rr in rows for i in range(4)}
    sel = {v for rr in rows for v in rr}
    act_e = {e for e in blue if tuple(e)[0] in sel and tuple(e)[1] in sel and e not in support}
    aadj = collections.defaultdict(set)
    for e in act_e:
        u, v = tuple(e); aadj[u].add(v); aadj[v].add(u)
    seenv, comps = set(), []
    for s in aadj:
        if s in seenv: continue
        comp, dq = {s}, collections.deque([s]); seenv.add(s)
        while dq:
            u = dq.popleft()
            for w in aadj[u]:
                if w not in seenv:
                    seenv.add(w); comp.add(w); dq.append(w)
        comps.append(comp)
    act_v = set()
    for comp in comps:
        if any(set(tuple(e)) <= comp for e in bad):
            act_v |= comp
    return sel, support, act_v

expect_active = [24, 18, 18, 24]
expect_demand = [264, 180, 180, 264]
for st, rows in enumerate(states):
    sel, support, act_v = active_scope(rows)
    assert len(sel) == 33, len(sel)
    assert len(act_v) == expect_active[st], (st, len(act_v))
    def pc(x, z):
        return sum(1 for rr in rows if x in rr and z in rr)
    demand = 0
    p1_ok = True
    for v in sorted(act_v):
        d = 0
        for z in range(N):
            c = sum(1 for rr in rows if v in rr) if z == v else pc(v, z)
            d += 2 * max(0, c - 1)
        demand += d
        if d:
            # P1-style supply: ordered zero-pairs with first coord = v (my sanity layer for the collapse)
            supply = 2 * sum(1 for z in range(N) if z != v and pc(v, z) == 0 and z in sel)
            if supply < d: p1_ok = False
    assert demand == expect_demand[st], (st, demand)
    assert p1_ok, f"state {st}: some owner P1-starved (collapse mechanism NOT sane)"

print("CLAUDE-GATE=PASS")
print("counts 78/137/27/164 tri-free cut=137 blue-connected bads-dist-4 all")
print("rotor histogram {54:7,63:10,75:1} (my DFS) == GPT claim; support rows unique; 9/8 minimality arithmetic OK")
print(f"active verts per state {expect_active} demand per state {expect_demand} == GPT table (my scoped recount)")
print("P1-style zero-pair supply >= demand at EVERY owner in EVERY state -> collapse mechanism CONFIRMED (defect-0 plausible; full production matching = Codex)")
