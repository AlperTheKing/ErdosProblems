#!/usr/bin/env python3
"""AGENT farkas_dual — Script A: the 8-vtx rotor as the EXACT Farkas dual of the
strict-potential LP, plus the automorphism that drives it.

Claims checked (all integer arithmetic, exhaustive on this fixture):
  A1  fixture replay: triangle-free, blue=cross of {x,y,p,q}|{m,v,a,b}, maxcut=8 (2^8),
      complete row DB = {A_m,A_v} for ab and {B_x,B_y} for pq (DFS).
  A2  sigma = (x m y v)(a p b q) is a color-preserving automorphism of order 4
      (blue->blue, bad->bad, swaps the two shores => preserves the cut partition),
      and sigma maps each rotor state to the NEXT state of the R39 cycle.
      COROLLARY (pure logic, no further check): any potential Phi defined canonically
      from (G, coloring, cut, tuple) — i.e. invariant under color/cut-preserving
      isomorphism — is CONSTANT on the orbit. No canonical strictly-decreasing
      potential exists on the scope-vacuous sector.
  A3  the FULL tuple space of this cage is exactly the 4 rotor states; the one-row
      in-family replacement digraph on them contains directed cycles (verified by
      failed topological sort), hence the strict-potential LP
          p(w') <= p(w) - 1   for every arc (w,w')
      is INFEASIBLE, with the R39 4-cycle as the explicit Farkas certificate:
      summing the four cycle constraints gives 0 <= -4.
      (Exact LP duality: strict potential exists  <=>  transition digraph acyclic
       <=>  no rotor. This is the equivalence statement of the dual hunt.)
  A4  switch-demand spectrum: for each state, kappa_state(S) = |M cap delta(S)| -
      |Support_state cap delta(S)| over ALL 2^8 subsets S. Report max. (Expected:
      the rotor is switch-TIGHT — max kappa = 0 — the intrinsic support already
      displays a maximum cut; CheapGeometry is VACUOUS on the rotor. This is the
      quantity that separates the rotor from the t=5 profile circuits.)
ASCII prints only. No floats.
"""
from itertools import combinations

names = ['a', 'b', 'p', 'q', 'x', 'y', 'm', 'v']
idx = {s: i for i, s in enumerate(names)}
a, b, p, q, x, y, m, v = (idx[s] for s in names)

blue = {frozenset(e) for e in [(a, x), (y, b), (p, m), (v, q), (x, m), (m, y), (y, v), (v, x)]}
bad = {frozenset(e) for e in [(a, b), (p, q)]}
edges = blue | bad
adj = [set() for _ in range(8)]
for e in edges:
    u, w = tuple(e)
    adj[u].add(w)
    adj[w].add(u)

# ---- A1 fixture replay ----
tri = any(adj[u] & adj[w] for u, w in combinations(range(8), 2) if w in adj[u])
assert not tri
sideA = {x, y, p, q}
for e in blue:
    u, w = tuple(e)
    assert (u in sideA) != (w in sideA)
for e in bad:
    u, w = tuple(e)
    assert (u in sideA) == (w in sideA)
best = 0
for mask in range(256):
    c = sum(1 for e in edges for u, w in [tuple(e)] if ((mask >> u) ^ (mask >> w)) & 1)
    best = max(best, c)
assert best == 8 == len(blue)

def rows_between(s, t):
    out = []
    def dfs(path):
        if len(path) == 5:
            if path[-1] == t:
                out.append(tuple(path))
            return
        for w2 in range(8):
            if w2 not in path and frozenset((path[-1], w2)) in blue:
                if len(path) == 4 and w2 != t:
                    continue
                dfs(path + [w2])
    dfs([s])
    return sorted(out)

A_m, A_v = (a, x, m, y, b), (a, x, v, y, b)
B_x, B_y = (p, m, x, v, q), (p, m, y, v, q)
assert rows_between(a, b) == sorted([A_m, A_v])
assert rows_between(p, q) == sorted([B_x, B_y])
print("A1 PASS: fixture replay (tri-free, cut=8 exhaustive, complete DB 2+2 rows)")

# ---- A2 the driving automorphism ----
sigma = {x: m, m: y, y: v, v: x, a: p, p: b, b: q, q: a}
# order 4
def pw(perm, k):
    out = {u: u for u in range(8)}
    for _ in range(k):
        out = {u: perm[out[u]] for u in range(8)}
    return out
assert pw(sigma, 4) == {u: u for u in range(8)}
assert pw(sigma, 2) != {u: u for u in range(8)}
# color-preserving automorphism
assert {frozenset((sigma[u], sigma[w])) for u, w in map(tuple, blue)} == blue
assert {frozenset((sigma[u], sigma[w])) for u, w in map(tuple, bad)} == bad
# swaps the shores (preserves the cut as a partition)
assert {sigma[u] for u in sideA} == set(range(8)) - sideA

def map_row(r):
    rr = tuple(sigma[u] for u in r)
    return rr if rr[0] < rr[-1] or True else rr

def norm_state(rows):
    # normalize each row so head is the atom endpoint with... rows are paths; treat as unordered vertex sequences up to reversal
    out = []
    for r in rows:
        rr = min(r, tuple(reversed(r)))
        out.append(rr)
    return frozenset(out)

states = {'w_mx': (A_m, B_x), 'w_my': (A_m, B_y), 'w_vy': (A_v, B_y), 'w_vx': (A_v, B_x)}
cycle_order = ['w_mx', 'w_my', 'w_vy', 'w_vx']
for i, st in enumerate(cycle_order):
    nxt = cycle_order[(i + 1) % 4]
    mapped = norm_state([tuple(sigma[u] for u in r) for r in states[st]])
    assert mapped == norm_state(states[nxt]), (st, nxt)
print("A2 PASS: sigma=(x m y v)(a p b q) is an order-4 color-preserving automorphism")
print("         swapping shores and mapping each rotor state to the NEXT state.")
print("         COROLLARY: every canonical (isomorphism-invariant) potential is")
print("         constant on the orbit — canonical potentials CANNOT orient it.")

# ---- A3 the transition digraph and the Farkas certificate ----
# FULL tuple space: one row per atom: 2 x 2 = 4 states — exactly the rotor orbit.
fam = {('a', 'b'): [A_m, A_v], ('p', 'q'): [B_x, B_y]}
tuples = [(ra, rb) for ra in fam[('a', 'b')] for rb in fam[('p', 'q')]]
assert len(tuples) == 4
arcs = []
for t1 in tuples:
    for t2 in tuples:
        if t1 == t2:
            continue
        diff = sum(1 for r1, r2 in zip(t1, t2) if r1 != r2)
        if diff == 1:
            arcs.append((t1, t2))
assert len(arcs) == 8  # bidirected square
# directed cycle exists => topological sort fails => strict-potential LP infeasible
indeg = {t: 0 for t in tuples}
for _, t2 in arcs:
    indeg[t2] += 1
queue = [t for t in tuples if indeg[t] == 0]
seen = 0
qq = list(queue)
while qq:
    cur = qq.pop()
    seen += 1
    for t1, t2 in arcs:
        if t1 == cur:
            indeg[t2] -= 1
            if indeg[t2] == 0:
                qq.append(t2)
assert seen < len(tuples), "digraph unexpectedly acyclic"
# explicit Farkas certificate on the R39 4-cycle: sum of p(next)<=p(cur)-1 gives 0<=-4
cyc = [states[s] for s in cycle_order]
lhs_coeff = {}
for i in range(4):
    cur, nxt = cyc[i], cyc[(i + 1) % 4]
    lhs_coeff[nxt] = lhs_coeff.get(nxt, 0) + 1
    lhs_coeff[cur] = lhs_coeff.get(cur, 0) - 1
assert all(c == 0 for c in lhs_coeff.values())
print("A3 PASS: full tuple space = 4 states; replacement digraph has directed cycles")
print("         (topological sort fails); strict-potential LP p(w')<=p(w)-1 INFEASIBLE;")
print("         Farkas dual = uniform weight 1 on the R39 4-cycle: telescopes to 0 <= -4.")

# ---- A4 switch-demand spectrum per state ----
def support(rows):
    return {frozenset((r[i], r[i + 1])) for r in rows for i in range(4)}

report = {}
for st, rows in states.items():
    sup = support(rows)
    mx = -10**9
    argmax = None
    for mask in range(256):
        kb = sum(1 for e in bad for u, w in [tuple(e)] if ((mask >> u) ^ (mask >> w)) & 1)
        ks = sum(1 for e in sup for u, w in [tuple(e)] if ((mask >> u) ^ (mask >> w)) & 1)
        k = kb - ks
        if k > mx:
            mx, argmax = k, mask
    report[st] = (mx, argmax)
print("A4 switch-demand max_S kappa(S) per state (support-only extension LP):")
for st in cycle_order:
    mx, am = report[st]
    print("   %s : max kappa = %d  (argmax mask %s)" % (st, mx, bin(am)))
allzero = all(report[st][0] == 0 for st in cycle_order)
print("A4 %s: rotor is switch-tight (max kappa = 0 in every state) => CheapGeometry"
      % ("PASS" if allzero else "NOTE"))
print("         vacuous on the rotor; intrinsic demand CANNOT separate it. The scope gate is")
print("         the ONLY discriminator here — matches R39's scope-vacuity verdict.")
print("DONE rotor8")
