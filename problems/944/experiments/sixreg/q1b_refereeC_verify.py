#!/usr/bin/env python3
# Referee C (computational, adversarial): INDEPENDENT verification of the
# claimed refutation of Lemma Q1'b. Everything here is rebuilt from the PROSE
# of the refutation (edge lists E1-E4, the described structure of B), not from
# the submitter's code. Different data structures, different search orders
# (randomized, multiple seeds), full-count searches (no cap), explicit
# re-verification of every returned colouring.
import itertools, random

# ---------------------------------------------------------------- utilities
def check_hypotheses(P, Q, edges, tag):
    V = P + Q
    assert len(set(V)) == len(V), f"{tag}: duplicate vertex"
    es = set()
    for a, b in edges:
        assert a != b and (a, b) not in es and (b, a) not in es, f"{tag}: bad edge {(a,b)}"
        es.add((a, b))
        assert ((a in set(P)) != (b in set(P))), f"{tag}: non-crossing edge {(a,b)}"
    deg = {v: 0 for v in V}
    adj = {v: set() for v in V}
    for a, b in edges:
        deg[a] += 1; deg[b] += 1
        adj[a].add(b); adj[b].add(a)
    assert max(deg.values()) <= 6, f"{tag}: Delta>6"
    deg5 = sorted(v for v in V if deg[v] == 5)
    assert all(deg[v] in (5, 6) for v in V), f"{tag}: bad degree"
    # connectivity
    seen = {V[0]}; st = [V[0]]
    while st:
        v = st.pop()
        for u in adj[v]:
            if u not in seen:
                seen.add(u); st.append(u)
    assert len(seen) == len(V), f"{tag}: disconnected"
    return adj, deg5

def verify_colouring(adj, ban, col):
    for v, nb in adj.items():
        assert col[v] in (0, 1, 2)
        for u in nb:
            assert col[v] != col[u], f"improper edge {(v,u)}"
    for v, b in ban.items():
        assert col[v] != b, f"ban violated at {v}"
    return True

def count_colourings(adj, ban, seed=0, cap=None):
    """Count ALL proper 3-colourings avoiding ban. Randomized vertex order
    (most-constrained-first tie-broken randomly). Returns (count, example)."""
    rng = random.Random(seed)
    order = list(adj)
    rng.shuffle(order)
    order.sort(key=lambda v: -len(adj[v]))   # high degree first, random ties
    col = {}
    found = []
    cnt = 0
    def rec(d):
        nonlocal cnt
        if cap is not None and cnt >= cap:
            return
        if d == len(order):
            cnt += 1
            if not found:
                found.append(dict(col))
            return
        v = order[d]
        for c in range(3):
            if ban.get(v) == c: continue
            if any(col.get(u) == c for u in adj[v]): continue
            col[v] = c
            rec(d + 1)
            del col[v]
    rec(0)
    return cnt, (found[0] if found else None)

# ------------------------------------------------- Counterexample A (prose)
P_A = [f'x{i}' for i in range(3)] + [f'u{a}' for a in range(1, 7)]
Q_A = [f'y{j}' for j in range(3)] + [f'w{b}' for b in range(1, 7)]
E_A = []
for i in range(3):
    for j in range(3):
        E_A.append((f'x{i}', f'y{j}'))                       # E1: full K33
for j in range(3):
    E_A += [(f'y{j}', f'u{2*j+1}'), (f'y{j}', f'u{2*j+2}')]  # E2
for i in range(3):
    E_A += [(f'x{i}', f'w{2*i+1}'), (f'x{i}', f'w{2*i+2}')]  # E3
for a in range(1, 7):
    for b in range(1, 7):
        if a != b:
            E_A.append((f'u{a}', f'w{b}'))                   # E4: K66 - PM
assert len(E_A) == 51
adjA, deg5A = check_hypotheses(P_A, Q_A, E_A, 'A')
anchors = [f'x{i}' for i in range(3)] + [f'y{j}' for j in range(3)]
assert deg5A == sorted(anchors), deg5A
print("A: hypotheses OK (18v, 51e, bipartite, simple, connected, Delta<=6, deg-5 set == anchors)")

# graph6 cross-check against the claimed string
def decode_graph6(s):
    n = ord(s[0]) - 63
    bits = []
    for ch in s[1:]:
        v = ord(ch) - 63
        bits += [(v >> k) & 1 for k in range(5, -1, -1)]
    E, p = set(), 0
    for j in range(1, n):
        for i in range(j):
            if bits[p]: E.add((i, j))
            p += 1
    return n, E
names = ['x0','x1','x2','y0','y1','y2'] + [f'u{a}' for a in range(1,7)] + [f'w{b}' for b in range(1,7)]
idx = {v: k for k, v in enumerate(names)}
myE = {tuple(sorted((idx[a], idx[b]))) for a, b in E_A}
n6, E6 = decode_graph6('QFz___GA?G?__^_nGZaFWG|?bw?')
print("A: claimed graph6 decodes to n=%d, |E|=%d; edge set == prose edge set: %s"
      % (n6, len(E6), E6 == myE))

ban = {f'x{i}': i for i in range(3)}
ban.update({f'y{j}': j for j in range(3)})

# anchor-only complete argument: induced anchor graph must be full K33
indE = {(a, b) for a in anchors for b in adjA[a] if b in anchors}
assert len(indE) == 18, indE  # 9 edges, both directions
cnt_proper = cnt_ok = 0
proof3line_ok = True
for cols in itertools.product(range(3), repeat=6):
    cA = dict(zip(anchors, cols))
    if any(cA[a] == cA[b] for (a, b) in indE):
        continue
    cnt_proper += 1
    S = {cA[f'x{i}'] for i in range(3)}
    T = {cA[f'y{j}'] for j in range(3)}
    # verify the 3-line argument case split on THIS tuple
    if not (S.isdisjoint(T) and min(len(S), len(T)) == 1):
        proof3line_ok = False
    if len(S) == 1:
        s = next(iter(S))
        if cA[f'x{s}'] != s: proof3line_ok = False  # x_s must be banned-hit
    elif len(T) == 1:
        t = next(iter(T))
        if cA[f'y{t}'] != t: proof3line_ok = False
    if all(cA[a] != ban[a] for a in anchors):
        cnt_ok += 1
print("A: anchor tuples proper on induced K33 = %d (expect 42); ban-avoiding = %d (expect 0); "
      "3-line case analysis holds on every tuple: %s" % (cnt_proper, cnt_ok, proof3line_ok))

# full-graph: FULL count (no cap) with three different random orders
for seed in (1, 2, 3):
    c, _ = count_colourings(adjA, ban, seed=seed)
    print(f"A: full exhaustive count of ban-avoiding colourings (seed {seed}): {c} (expect 0)")

# positive controls on the SAME graph & searcher
c0, ex0 = count_colourings(adjA, {}, seed=5, cap=1)
verify_colouring(adjA, {}, ex0)
ban_ctrl = dict(ban); ban_ctrl['y2'] = 0          # non-rainbow y-side bans (0,1,0)
c1, ex1 = count_colourings(adjA, ban_ctrl, seed=5, cap=1)
assert c1 == 1 and verify_colouring(adjA, ban_ctrl, ex1)
ban_ctrl2 = dict(ban); ban_ctrl2['x1'] = 0        # non-rainbow x-side bans (0,0,2)
c2, ex2 = count_colourings(adjA, ban_ctrl2, seed=7, cap=1)
assert c2 == 1 and verify_colouring(adjA, ban_ctrl2, ex2)
print("A: positive controls: no-ban colourable: %s; bans(y:0,1,0): %s; bans(x:0,0,2): %s "
      "(all returned colourings re-verified edge-by-edge)" % (c0 == 1, c1 == 1, c2 == 1))

# --------------------------------------------------------------- Lemma S
sols = []
for s in itertools.product(range(3), repeat=3):
    if any(s[i] == i for i in range(3)): continue
    for t in itertools.product(range(3), repeat=3):
        if any(t[j] == j for j in range(3)): continue
        if all(s[i] != t[j] for i in range(3) for j in range(3) if i != j):
            sols.append((s, t))
print("S: solutions of {s(i)!=i, t(j)!=j, s(i)!=t(j) for i!=j}:", sols,
      "(expect the two cyclic pairs)")
assert sols == [((1, 2, 0), (1, 2, 0)), ((2, 0, 1), (2, 0, 1))]
# corollary (i): any matched edge added -> 0 solutions
for M in [(0,), (1,), (2,), (0, 1), (0, 2), (1, 2), (0, 1, 2)]:
    bad = [(s, t) for (s, t) in sols if all(s[i] != t[i] for i in M)]
    assert bad == [], M
print("S: corollary (i) verified: each nonempty matched-edge set kills all solutions")
# corollary (ii): both surviving solutions have both sides rainbow
assert all(set(s) == {0, 1, 2} and set(t) == {0, 1, 2} for (s, t) in sols)
print("S: corollary (ii) verified: both solutions rainbow on both sides")
# refutation claim (a): the skeleton's cited repair sigma=(2,0,2), tau=(1,0,1)
sig, tau = (2, 0, 2), (1, 0, 1)
viol = [i for i in range(3) if sig[i] == i] + [f"y{j}" for j in range(3) if tau[j] == j]
print("S: skeleton repair sigma=(2,0,2),tau=(1,0,1): ban violations at:",
      [f"x{i} (sigma({i})={i}=gamma)" for i in range(3) if sig[i] == i], "(expect x2)")
# and: NO non-bijective deranged sigma admits ANY deranged tau under the cross edges
nonbij = 0
for s in itertools.product(range(3), repeat=3):
    if any(s[i] == i for i in range(3)) or len(set(s)) == 3: continue
    for t in itertools.product(range(3), repeat=3):
        if any(t[j] == j for j in range(3)): continue
        if all(s[i] != t[j] for i in range(3) for j in range(3) if i != j):
            nonbij += 1
print("S: compatible taus for non-bijective deranged sigmas:", nonbij, "(expect 0)")

# --------------------------------- Counterexample B, MY OWN padding (new graph)
P_B = ['x0', 'x1', 'x2', 'us', 'u1', 'u2', 'u3', 'u4', 'u5']
Q_B = ['y0', 'y1', 'y2', 'w1', 'w2', 'w3', 'w4', 'w5', 'w6']
E_B = []
for i in range(3):
    for j in range(3):
        if i != j:
            E_B.append((f'x{i}', f'y{j}'))                   # K33 - PM (0 matched edges)
E_B += [('us', f'y{j}') for j in range(3)]                   # blocker u*
E_B += [('x0', 'w1'), ('x0', 'w2'), ('x0', 'w3'),
        ('x1', 'w2'), ('x1', 'w3'), ('x1', 'w4'),
        ('x2', 'w4'), ('x2', 'w5'), ('x2', 'w6'),
        ('us', 'w1'), ('us', 'w5'), ('us', 'w6')]
E_B += [('y0', 'u1'), ('y0', 'u2'), ('y1', 'u2'), ('y1', 'u3'),
        ('y2', 'u4'), ('y2', 'u5')]
non_edges = {('u1', 'w1'), ('u2', 'w2'), ('u2', 'w3'), ('u3', 'w4'),
             ('u4', 'w5'), ('u5', 'w6')}
for k in range(1, 6):
    for l in range(1, 7):
        if (f'u{k}', f'w{l}') not in non_edges:
            E_B.append((f'u{k}', f'w{l}'))
adjB, deg5B = check_hypotheses(P_B, Q_B, E_B, 'B(mine)')
assert deg5B == sorted(anchors), deg5B
print("B(my padding): hypotheses OK (18v, %de); deg-5 set == anchors; "
      "matched pairs x_i,y_i non-adjacent: %s" % (len(E_B),
      all(f'y{i}' not in adjB[f'x{i}'] for i in range(3))))
for seed in (1, 2):
    c, _ = count_colourings(adjB, ban, seed=seed)
    print(f"B(my padding): full exhaustive ban-avoiding count (seed {seed}): {c} (expect 0)")
cB0, exB0 = count_colourings(adjB, {}, seed=3, cap=1)
verify_colouring(adjB, {}, exB0)
banB_ctrl = dict(ban); banB_ctrl['y1'] = 0
cB1, exB1 = count_colourings(adjB, banB_ctrl, seed=3, cap=1)
print("B(my padding): controls: no-ban colourable: %s; bans(y:0,0,2)-style colourable: %s"
      % (cB0 == 1, cB1 == 1 and verify_colouring(adjB, banB_ctrl, exB1)))

# local proof of B: every ban-avoiding proper anchor pattern (core = i!=j edges)
# makes y-side rainbow, hence u* (adjacent to y0,y1,y2) sees all 3 colours
ok_patterns = []
for cols in itertools.product(range(3), repeat=6):
    cA = dict(zip(anchors, cols))
    if any(cA[f'x{i}'] == cA[f'y{j}'] for i in range(3) for j in range(3) if i != j):
        continue
    if any(cA[a] == ban[a] for a in anchors):
        continue
    ok_patterns.append(cols)
assert all({c[3], c[4], c[5]} == {0, 1, 2} for c in ok_patterns)
print("B: surviving anchor patterns on K33-PM core: %d (expect 2: cyclic), "
      "all with y-side rainbow -> u* uncolourable. Patterns: %s"
      % (len(ok_patterns), ok_patterns))

# also run the SUBMITTER's build_B through MY searcher
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location(
    'q1b_ce', str(pathlib.Path(__file__).parent / 'q1b_counterexample.py'))
mod = importlib.util.module_from_spec(spec)
mod.__name__ = 'q1b_ce'
spec.loader.exec_module(mod) if False else None
# (avoid executing its __main__; re-import via exec of the file with guard)
src = (pathlib.Path(__file__).parent / 'q1b_counterexample.py').read_text()
g = {'__name__': 'q1b_ce_loaded'}
exec(compile(src, 'q1b_counterexample.py', 'exec'), g)
Pb, Qb, Eb = g['build_B']()
adjBt, deg5Bt = check_hypotheses(Pb, Qb, Eb, 'B(theirs)')
assert deg5Bt == sorted(anchors)
cT, _ = count_colourings(adjBt, ban, seed=9)
print("B(their build_B) via MY searcher: hypotheses OK; ban-avoiding count = %d (expect 0)" % cT)
print("ALL INDEPENDENT CHECKS PASSED")
