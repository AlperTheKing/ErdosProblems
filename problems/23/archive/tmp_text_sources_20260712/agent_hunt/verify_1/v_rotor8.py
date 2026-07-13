#!/usr/bin/env python3
"""VERIFIER (adversarial) -- independent replay of farkas_dual Findings 1-3 on the
8-vtx rotor. Everything rebuilt from the R39 writeup text only. Pure integers.

Checks:
  V1  fixture: triangle-free, blue=cross of {x,y,p,q}|{m,v,a,b}, bads same-shore,
      blue connected, d_blue(a,b)=d_blue(p,q)=4, complete row DB = exactly
      {A_m,A_v} for ab and {B_x,B_y} for pq, maxcut over all 2^8 cuts = 8 =
      displayed cut, R39 four-C5 double cover (every edge in exactly 2 of 4 C5s).
  V2  sigma=(x m y v)(a p b q): order 4, blue->blue, bad->bad, swaps shores,
      maps state i to state i+1 of the R39 orbit. Also sigma^2 preserves shores
      (so even shore-ORIENTED canonical potentials die on the orbit).
  V3  tuple space = 4; one-row replacement digraph arcs; Bellman-Ford proves the
      difference-constraint system p(w')<=p(w)-1 infeasible (negative cycle);
      the R39 4-cycle telescopes to 0 <= -4 with weights (1,1,1,1).
      PLUS the sector fact: every state's internal component has NO atom endpoint
      (scope-vacuous) => the ACTIVE-restricted digraph D_act on this cage is EMPTY.
  V4  per state: |support|=7, the unselected blue edge matches R39 (yv/xv/xm/my);
      kappa_support(S)=|bad cap delta(S)|-|sup cap delta(S)| over all 2^8:
      max=1; at EVERY argmax the internal edge crosses and kappa_full=0;
      max over S of kappa_full = 0 (consistent with maxcut).
"""
from itertools import combinations

names = ['a', 'b', 'p', 'q', 'x', 'y', 'm', 'v']
I = {s: k for k, s in enumerate(names)}
a, b, p, q, x, y, m, v = (I[s] for s in names)

BLUE = frozenset(frozenset(e) for e in
                 [(a, x), (y, b), (p, m), (v, q), (x, m), (m, y), (y, v), (v, x)])
BAD = frozenset(frozenset(e) for e in [(a, b), (p, q)])
N = 8

adj_all = [set() for _ in range(N)]
adj_blue = [set() for _ in range(N)]
for e in BLUE | BAD:
    u, w = tuple(e)
    adj_all[u].add(w); adj_all[w].add(u)
for e in BLUE:
    u, w = tuple(e)
    adj_blue[u].add(w); adj_blue[w].add(u)

# ---------- V1 ----------
assert not any(adj_all[u] & adj_all[w] for u in range(N) for w in adj_all[u]), "triangle"
shoreA = {x, y, p, q}
for e in BLUE:
    u, w = tuple(e); assert (u in shoreA) != (w in shoreA)
for e in BAD:
    u, w = tuple(e); assert (u in shoreA) == (w in shoreA)

def bfs(src):
    d = {src: 0}; frontier = [src]
    while frontier:
        nxt = []
        for u in frontier:
            for w in adj_blue[u]:
                if w not in d:
                    d[w] = d[u] + 1; nxt.append(w)
        frontier = nxt
    return d

db_a = bfs(a); db_p = bfs(p)
assert len(db_a) == N, "blue disconnected"
assert db_a[b] == 4 and db_p[q] == 4, (db_a.get(b), db_p.get(q))

def four_paths(s, t):
    """all simple blue paths s..t with exactly 4 edges"""
    res = []
    for n1 in adj_blue[s]:
        for n2 in adj_blue[n1]:
            if n2 in (s,):
                continue
            for n3 in adj_blue[n2]:
                if n3 in (s, n1):
                    continue
                if t in adj_blue[n3] and t not in (s, n1, n2):
                    res.append((s, n1, n2, n3, t))
    return sorted(res)

A_m, A_v = (a, x, m, y, b), (a, x, v, y, b)
B_x, B_y = (p, m, x, v, q), (p, m, y, v, q)
assert four_paths(a, b) == sorted([A_m, A_v])
assert four_paths(p, q) == sorted([B_x, B_y])

def cutval(mask):
    return sum(1 for e in BLUE | BAD
               for u, w in [tuple(e)] if ((mask >> u) ^ (mask >> w)) & 1)

disp = 0
for u in shoreA:
    disp |= 1 << u
assert cutval(disp) == 8
assert max(cutval(mk) for mk in range(1 << N)) == 8

# four-C5 double cover
def path_edges(r):
    return {frozenset((r[k], r[k + 1])) for k in range(4)}
C5s = [path_edges(A_m) | {frozenset((a, b))}, path_edges(A_v) | {frozenset((a, b))},
       path_edges(B_x) | {frozenset((p, q))}, path_edges(B_y) | {frozenset((p, q))}]
for e in BLUE | BAD:
    assert sum(1 for c in C5s if e in c) == 2, ("double-cover fails", tuple(e))
print("V1 PASS: fixture, complete DB {A_m,A_v}/{B_x,B_y}, maxcut=8 exhaustive, 4xC5 double cover")

# ---------- V2 ----------
sig = {x: m, m: y, y: v, v: x, a: p, p: b, b: q, q: a}
perm = dict(sig)
order = 1
cur = dict(sig)
while any(cur[u] != u for u in range(N)):
    cur = {u: sig[cur[u]] for u in range(N)}
    order += 1
assert order == 4
assert {frozenset((sig[u], sig[w])) for e in BLUE for u, w in [tuple(e)]} == set(BLUE)
assert {frozenset((sig[u], sig[w])) for e in BAD for u, w in [tuple(e)]} == set(BAD)
assert {sig[u] for u in shoreA} == set(range(N)) - shoreA
sig2 = {u: sig[sig[u]] for u in range(N)}
assert {sig2[u] for u in shoreA} == shoreA  # sigma^2 preserves shores

def canon_row(r):
    return min(tuple(r), tuple(reversed(r)))

def canon_state(st):
    return frozenset(canon_row(r) for r in st)

orbit = [(A_m, B_x), (A_m, B_y), (A_v, B_y), (A_v, B_x)]   # w_mx w_my w_vy w_vx
for k in range(4):
    img = canon_state([tuple(sig[u] for u in r) for r in orbit[k]])
    assert img == canon_state(orbit[(k + 1) % 4]), k
print("V2 PASS: sigma order-4 colour automorphism, swaps shores, state_i -> state_{i+1};"
      " sigma^2 shore-preserving")

# ---------- V3 ----------
tuples = [(ra, rb) for ra in (A_m, A_v) for rb in (B_x, B_y)]
assert len(tuples) == 4
arcs = [(t1, t2) for t1 in tuples for t2 in tuples
        if t1 != t2 and sum(1 for r1, r2 in zip(t1, t2) if r1 != r2) == 1]
assert len(arcs) == 8
# Bellman-Ford on constraint graph: arc (t1->t2) weight -1 encodes p(t2) <= p(t1) - 1
dist = {t: 0 for t in tuples}
neg_cycle = False
for it in range(len(tuples)):
    changed = False
    for t1, t2 in arcs:
        if dist[t1] - 1 < dist[t2]:
            dist[t2] = dist[t1] - 1; changed = True
    if it == len(tuples) - 1 and changed:
        neg_cycle = True
assert neg_cycle, "system unexpectedly feasible"
# R39 orbit is a directed cycle of arcs; weights 1,1,1,1 telescope to 0 <= -4
coeff = {}
rhs = 0
for k in range(4):
    t1, t2 = orbit[k], orbit[(k + 1) % 4]
    assert (t1, t2) in [(u, w) for u, w in arcs]
    coeff[t2] = coeff.get(t2, 0) + 1
    coeff[t1] = coeff.get(t1, 0) - 1
    rhs += -1
assert all(c == 0 for c in coeff.values()) and rhs == -4
# sector fact: every state is scope-vacuous (internal component has no atom endpoint)
atom_endpoints = {a, b, p, q}
for st in tuples:
    sup = set()
    for r in st:
        sup |= path_edges(r)
    internal = set(BLUE) - sup
    assert len(internal) == 1
    comp = set(tuple(next(iter(internal))))
    assert not (comp & atom_endpoints), "state NOT scope-vacuous?!"
print("V3 PASS: 4 tuples, 8 arcs, Bellman-Ford negative cycle => potential LP INFEASIBLE;")
print("         orbit telescopes 0 <= -4; ALL 4 states scope-vacuous => D_act(this cage) EMPTY")

# ---------- V4 ----------
expect_unsel = {0: frozenset((y, v)), 1: frozenset((x, v)),
                2: frozenset((x, m)), 3: frozenset((m, y))}
for k, st in enumerate(orbit):
    sup = set()
    for r in st:
        sup |= path_edges(r)
    assert len(sup) == 7
    internal = set(BLUE) - sup
    assert internal == {expect_unsel[k]}, (k, internal)
    ie = next(iter(internal))
    iu, iw = tuple(ie)
    best = -99; argmaxes = []
    for mk in range(1 << N):
        kb = sum(1 for e in BAD for u, w in [tuple(e)] if ((mk >> u) ^ (mk >> w)) & 1)
        ks = sum(1 for e in sup for u, w in [tuple(e)] if ((mk >> u) ^ (mk >> w)) & 1)
        val = kb - ks
        if val > best:
            best = val; argmaxes = [mk]
        elif val == best:
            argmaxes.append(mk)
    assert best == 1, (k, best)
    full_ok = True
    for mk in argmaxes:
        crosses = ((mk >> iu) ^ (mk >> iw)) & 1
        assert crosses == 1, ("internal edge misses an argmax switch", k, mk)
        kb = sum(1 for e in BAD for u, w in [tuple(e)] if ((mk >> u) ^ (mk >> w)) & 1)
        kf = sum(1 for e in BLUE for u, w in [tuple(e)] if ((mk >> u) ^ (mk >> w)) & 1)
        full_ok = full_ok and (kb - kf == 0)
    assert full_ok
    # kappa_full <= 0 everywhere (maxcut) with equality attained
    mx_full = max(sum(1 for e in BAD for u, w in [tuple(e)] if ((mk >> u) ^ (mk >> w)) & 1)
                  - sum(1 for e in BLUE for u, w in [tuple(e)] if ((mk >> u) ^ (mk >> w)) & 1)
                  for mk in range(1 << N))
    assert mx_full == 0
    ex = sorted(names[u] for u in range(N) if (argmaxes[0] >> u) & 1)
    print("V4 state %d: max kappa_support = 1 over %d argmax switches (e.g. S=%s);"
          " internal edge crosses ALL of them; kappa_full=0 at each" % (k, len(argmaxes), ex))
print("V4 PASS: demand exactly 1 per state, unique internal edge is the payer, zero slack")
print("DONE v_rotor8")
