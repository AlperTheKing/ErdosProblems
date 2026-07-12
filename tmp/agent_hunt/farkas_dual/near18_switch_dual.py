#!/usr/bin/env python3
"""AGENT farkas_dual — Script B: the R46 18-vtx near-candidate, exact replay + the
switch-demand Farkas dual (the LP whose infeasibility certificates killed #264/#298-era
candidates), measured on the profile-realizing fixture.

Fixture (R46 sec 8): L = {v,m,a,b0..b4}, R = {x0..x4,y0..y4}; blue: v-xi (5), m-xi (5),
a-x0..x3 (4), a-yj (5), bj-yj (5) = 24 edges; atoms: vbj, mbj, bibj, x4yj = 25.

Checks:
  B1  blue bipartite L|R, connected; the 25 listed atoms are EXACTLY the same-shore
      blue-distance-4 pairs (atom choice forced); atom endpoint graph triangle count = 30
      (K5 on b's: 10; owner triangles v/m-bi-bj: 20)  [the known kill];
  B2  transversal circuit: |F*| = 24 = |A|-1 (F_a = union of ALL shortest-row edges),
      max SDR = 24 (deficiency exactly 1), every 1-atom deletion has a full SDR;
  B3  profile realization: owner v, active edge v-x4: a tuple with r(v)=5, v-x4 unselected,
      v-x0..x3 selected, every star pair {x4,xi} covered by a row avoiding v (and same for m);
  B4  THE SWITCH DUAL: exact sweep of kappa(S) = |M cap delta(S)| - |B0 cap delta(S)| over
      all 2^18 subsets: max kappa, argmax, count of positive-demand switches, values at
      natural clusters ({b's}, {v}, {m}, {v,m}, {v,m,b's});
  B5  singleSafe relaxed capacity (R47 first-stage): candidate ambient cross-shore edges
      that (i) create no triangle in blue+bad+e, (ii) for EVERY atom (s,t):
      min over orientations d(s,u)+1+d(w,t) >= 5 (no new path of length <= 4);
      per max-demand switch: capRelaxed(S) = #singleSafe crossing; report demand - capacity
      (positive = intrinsic-18 Farkas kill certificate; ambient extra vertices out of scope,
      flagged).
All integer arithmetic; ASCII only.
"""
from itertools import combinations
from collections import deque

# ---- build fixture ----
L = ['v', 'm', 'a'] + ['b%d' % j for j in range(5)]
R = ['x%d' % i for i in range(5)] + ['y%d' % j for j in range(5)]
names = L + R
idx = {s: i for i, s in enumerate(names)}
n = len(names)
assert n == 18

blue = set()
for i in range(5):
    blue.add(frozenset((idx['v'], idx['x%d' % i])))
    blue.add(frozenset((idx['m'], idx['x%d' % i])))
for i in range(4):
    blue.add(frozenset((idx['a'], idx['x%d' % i])))
for j in range(5):
    blue.add(frozenset((idx['a'], idx['y%d' % j])))
    blue.add(frozenset((idx['b%d' % j], idx['y%d' % j])))
assert len(blue) == 24

atoms = []
for j in range(5):
    atoms.append(frozenset((idx['v'], idx['b%d' % j])))
    atoms.append(frozenset((idx['m'], idx['b%d' % j])))
for i, j in combinations(range(5), 2):
    atoms.append(frozenset((idx['b%d' % i], idx['b%d' % j])))
for j in range(5):
    atoms.append(frozenset((idx['x4'], idx['y%d' % j])))
assert len(atoms) == 25
M = set(atoms)

Lset = {idx[s] for s in L}
badj = [set() for _ in range(n)]
bluadj = [set() for _ in range(n)]
for e in blue:
    u, w = tuple(e)
    bluadj[u].add(w)
    bluadj[w].add(u)
for e in M:
    u, w = tuple(e)
    badj[u].add(w)
    badj[w].add(u)

# ---- B1 ----
for e in blue:
    u, w = tuple(e)
    assert (u in Lset) != (w in Lset)
for e in M:
    u, w = tuple(e)
    assert (u in Lset) == (w in Lset)
# blue connected
seen = {0}
dq = deque([0])
while dq:
    u = dq.popleft()
    for w in bluadj[u]:
        if w not in seen:
            seen.add(w)
            dq.append(w)
assert seen == set(range(n)), "blue disconnected"

def bfs_dist(src):
    d = [None] * n
    d[src] = 0
    dq2 = deque([src])
    while dq2:
        u = dq2.popleft()
        for w in bluadj[u]:
            if d[w] is None:
                d[w] = d[u] + 1
                dq2.append(w)
    return d

dist = [bfs_dist(u) for u in range(n)]
d4pairs = set()
for u, w in combinations(range(n), 2):
    if ((u in Lset) == (w in Lset)) and dist[u][w] == 4:
        d4pairs.add(frozenset((u, w)))
assert d4pairs == M, ("atom set differs from forced distance-4 set",
                      len(d4pairs), len(M))
# atom endpoint graph triangles
tri = 0
for u, w, z in combinations(range(n), 3):
    if (frozenset((u, w)) in M and frozenset((u, z)) in M and frozenset((w, z)) in M):
        tri += 1
tri_all = tri
assert tri_all == 30, tri_all  # R46: K5 on b's (10) + owner triangles v/m-bi-bj (20)
cnt_owner = 0
for i, j in combinations(range(5), 2):
    if (frozenset((idx['v'], idx['b%d' % i])) in M and
            frozenset((idx['v'], idx['b%d' % j])) in M and
            frozenset((idx['b%d' % i], idx['b%d' % j])) in M):
        cnt_owner += 1
print("B1 triangle audit: total triangles in atom graph = %d (K5 gives 10; owner v pairs = %d)"
      % (tri_all, cnt_owner))

# ---- B2 circuit ----
def all_rows(s, t):
    out = []
    def dfs(path):
        if len(path) == 5:
            if path[-1] == t:
                out.append(tuple(path))
            return
        for w2 in bluadj[path[-1]]:
            if w2 not in path:
                if len(path) == 4 and w2 != t:
                    continue
                dfs(path + [w2])
    dfs([s])
    return out

rowdb = {}
F = {}
for at in atoms:
    s, t = sorted(at)
    rows = all_rows(s, t)
    rows = [r for r in rows if len(r) == 5]
    assert rows, ("no rows", names[s], names[t])
    rowdb[at] = rows
    F[at] = {frozenset((r[i], r[i + 1])) for r in rows for i in range(4)}

Fstar = set()
for at in atoms:
    Fstar |= F[at]
assert Fstar <= blue
print("B2 |F*| = %d (atoms %d)" % (len(Fstar), len(atoms)))
assert len(Fstar) == 24

def max_sdr(atom_list, forbidden_atom=None):
    # bipartite matching atoms -> edges of their F sets (Hungarian augmenting path)
    use = [at for at in atom_list if at != forbidden_atom]
    edge_ids = {e: i for i, e in enumerate(sorted(Fstar, key=lambda e: sorted(e)))}
    match_edge = {}
    def try_aug(ai, vis):
        for e in F[use[ai]]:
            ei = edge_ids[e]
            if ei in vis:
                continue
            vis.add(ei)
            if ei not in match_edge or try_aug(match_edge[ei], vis):
                match_edge[ei] = ai
                return True
        return False
    cnt = 0
    for ai in range(len(use)):
        if try_aug(ai, set()):
            cnt += 1
    return cnt

full = max_sdr(atoms)
print("B2 max SDR over all 25 atoms = %d (deficiency %d)" % (full, 25 - full))
assert full == 24
for at in atoms:
    assert max_sdr(atoms, at) == 24, ("deletion fails SDR", at)
print("B2 PASS: transversal circuit — every 1-atom deletion has a full 24-SDR")

# ---- B3 profile realization ----
def realize_profile(owner, middle, active_x='x4'):
    ow, mid, ax = idx[owner], idx[middle], idx[active_x]
    # rows for owner-b atoms: (owner, xi, a, yj, bj) i in 0..3: pick i to cover x0..x3
    sel = {}
    for j in range(5):
        at = frozenset((ow, idx['b%d' % j]))
        rows = [r for r in rowdb[at] if r[0] == ow or r[-1] == ow]
        want_i = min(j, 3)
        pick = [r for r in rows if idx['x%d' % want_i] in r]
        assert pick
        sel[at] = pick[0]
    for j in range(5):
        at = frozenset((mid, idx['b%d' % j]))
        sel[at] = rowdb[at][0]
    for i, j in combinations(range(5), 2):
        at = frozenset((idx['b%d' % i], idx['b%d' % j]))
        sel[at] = rowdb[at][0]
    for j in range(5):
        at = frozenset((idx['x4'], idx['y%d' % j]))
        # coverage row avoiding owner: middle = the OTHER owner; distribute xi over x0..x3
        want_x = idx['x%d' % min(j, 3)]
        pick = [r for r in rowdb[at] if ow not in r and mid in r and want_x in r]
        assert pick, "no coverage row avoiding owner"
        sel[at] = pick[0]
    # audit
    rcount = sum(1 for at, r in sel.items() if ow in r)
    sup = {frozenset((r[i], r[i + 1])) for r in sel.values() for i in range(4)}
    active_unsel = frozenset((ow, ax)) not in sup
    star_sel = all(frozenset((ow, idx['x%d' % i])) in sup for i in range(4))
    covered = all(any(ow not in r and idx['x%d' % i] in r and ax in r
                      for r in [sel[frozenset((idx['x4'], idx['y%d' % j])) ]])
                  for i in range(4) for j in range(5)
                  if idx['x%d' % i] in sel[frozenset((idx['x4'], idx['y%d' % j]))])
    return rcount, active_unsel, star_sel, sel

rc, act_unsel, star_sel, selv = realize_profile('v', 'm')
print("B3 owner v: r(v)=%d (target 5), v-x4 unselected=%s, v-x0..x3 all selected=%s"
      % (rc, act_unsel, star_sel))
assert rc == 5 and act_unsel and star_sel
# coverage: every star pair {x4, xi} i<=3 covered by SOME selected row avoiding v containing both
sup_rows = list(selv.values())
cov_ok = True
for i in range(4):
    found = any((idx['v'] not in r) and (idx['x4'] in r) and (idx['x%d' % i] in r)
                for r in sup_rows)
    cov_ok = cov_ok and found
print("B3 owner v: all 4 star pairs {x4,xi} covered by selected rows avoiding v: %s" % cov_ok)
assert cov_ok
rc2, a2, s2, selm = realize_profile('m', 'v')
assert rc2 == 5 and a2 and s2
print("B3 PASS: full T5 profile realized at BOTH owners (v and m) — matches R46")

# ---- B4 switch sweep ----
bad_edges = [tuple(sorted(e)) for e in M]
blue_edges = [tuple(sorted(e)) for e in blue]
maxk = -10**9
argmax = None
pos_count = 0
histo = {}
for mask in range(1 << n):
    kb = 0
    for u, w in bad_edges:
        kb += ((mask >> u) ^ (mask >> w)) & 1
    ks = 0
    for u, w in blue_edges:
        ks += ((mask >> u) ^ (mask >> w)) & 1
    k = kb - ks
    if k > maxk:
        maxk, argmax = k, mask
    if k > 0:
        pos_count += 1
    histo[k] = histo.get(k, 0) + 1

def show(mask):
    return sorted(names[u] for u in range(n) if (mask >> u) & 1)

print("B4 max kappa = %d at S = %s" % (maxk, show(argmax)))
print("B4 positive-demand switches: %d of %d; demand histogram (kappa: count) = %s"
      % (pos_count, 1 << n, {k: histo[k] for k in sorted(histo) if k >= max(1, maxk - 3)}))
for tag, S in [("{b0..b4}", [idx['b%d' % j] for j in range(5)]),
               ("{v}", [idx['v']]), ("{m}", [idx['m']]), ("{v,m}", [idx['v'], idx['m']]),
               ("{v,m,b0..b4}", [idx['v'], idx['m']] + [idx['b%d' % j] for j in range(5)])]:
    mask = 0
    for u in S:
        mask |= 1 << u
    kb = sum(((mask >> u) ^ (mask >> w)) & 1 for u, w in bad_edges)
    ks = sum(((mask >> u) ^ (mask >> w)) & 1 for u, w in blue_edges)
    print("   kappa(%s) = %d - %d = %d" % (tag, kb, ks, kb - ks))

# ---- B5 singleSafe relaxed capacity ----
Gadj = [bluadj[u] | badj[u] for u in range(n)]
cands = []
for u in sorted(Lset):
    for w in sorted(set(range(n)) - Lset):
        e = frozenset((u, w))
        if e in blue:
            continue
        # triangle test in blue+bad+e
        if Gadj[u] & Gadj[w]:
            continue
        ok = True
        for at in atoms:
            s, t = tuple(at)
            best = min(dist[s][u] + 1 + dist[w][t], dist[s][w] + 1 + dist[u][t])
            if best <= 4:
                ok = False
                break
        if ok:
            cands.append(e)
print("B5 singleSafe ambient cross-shore candidates on the 18 intrinsic vertices: %d of %d non-blue pairs"
      % (len(cands), 8 * 10 - 24))
mask = argmax
cross_cap = sum(1 for e in cands for u, w in [tuple(e)] if ((mask >> u) ^ (mask >> w)) & 1)
print("B5 at the max-demand switch: demand %d vs singleSafe capacity %d => intrinsic gap %d"
      % (maxk, cross_cap, maxk - cross_cap))
# scan: largest (kappa - capRelaxed) over all switches
worst = -10**9
worst_mask = None
for mask in range(1 << n):
    kb = 0
    for u, w in bad_edges:
        kb += ((mask >> u) ^ (mask >> w)) & 1
    if kb == 0:
        continue
    ks = 0
    for u, w in blue_edges:
        ks += ((mask >> u) ^ (mask >> w)) & 1
    k = kb - ks
    if k <= 0:
        continue
    cap = sum(1 for e in cands for u, w in [tuple(e)] if ((mask >> u) ^ (mask >> w)) & 1)
    g = k - cap
    if g > worst:
        worst, worst_mask = g, mask
print("B5 worst intrinsic Farkas gap (kappa - capRelaxed) = %d at S = %s"
      % (worst, show(worst_mask) if worst_mask is not None else None))
print("B5 NOTE: production N=25 has >=7 extra ambient vertices (columns NOT counted here);")
print("         intrinsic gap > 0 = the R47-shaped one-switch certificate ON the 18 support")
print("         vertices only. Extra-vertex channels were engine-killed per split (R50).")
print("DONE near18")
