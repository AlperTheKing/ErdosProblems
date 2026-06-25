# referee2_q1b_independent.py
# Second-referee INDEPENDENT verification of the claimed refutation of Lemma Q1'b.
# All solvers here are COMPLETE enumerations (no backtracking-order trust needed):
#   stage 1: enumerate all 3^6 anchor colourings (proper + ban-avoiding),
#   stage 2: enumerate P-side filler colourings from per-vertex allowed lists,
#   stage 3: Q-side fillers are mutually non-adjacent (bipartite), so count
#            free colours per vertex and multiply. Exact count of all proper
#            ban-avoiding 3-colourings.
import itertools
from collections import deque

COL = (0, 1, 2)

def build(edges):
    adj = {}
    for u, v in edges:
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u)
    return adj

def connected(adj):
    vs = list(adj)
    seen = {vs[0]}; dq = deque([vs[0]])
    while dq:
        u = dq.popleft()
        for w in adj[u]:
            if w not in seen:
                seen.add(w); dq.append(w)
    return len(seen) == len(adj)

def hyp_check(name, P, Q, edges, anchors):
    """Verify ALL hypotheses of Lemma Q1'b. Returns adjacency."""
    adj = build(edges)
    Pset, Aset = set(P), set(anchors)
    assert set(adj) == set(P) | set(Q), name + ": isolated vertex"
    assert all((u in Pset) != (v in Pset) for u, v in edges), name + ": not bipartite"
    d5 = sorted(v for v in adj if len(adj[v]) == 5)
    assert d5 == sorted(anchors), (name, "deg-5 set wrong", d5)
    assert all(len(adj[v]) == 6 for v in adj if v not in Aset), name + ": non-anchor deg != 6"
    assert connected(adj), name + ": disconnected"
    return adj

def exact_count(P, Q, adj, anchors, banned, cap=10**9):
    """EXACT number of proper 3-colourings avoiding all bans. Complete."""
    Aset = set(anchors)
    pF = [v for v in P if v not in Aset]
    qF = [v for v in Q if v not in Aset]
    # sanity: Q-side fillers only see P-side vertices (true by bipartiteness)
    total = 0
    anchor_feasible = 0
    for ac in itertools.product(COL, repeat=len(anchors)):
        col = dict(zip(anchors, ac))
        if any(col[a] == banned.get(a, -1) for a in anchors):
            continue
        if any(w in col and col[w] == col[a] for a in anchors for w in adj[a]):
            continue
        anchor_feasible += 1
        allowed = []
        ok = True
        for pv in pF:
            al = [c for c in COL if all(col.get(w) != c for w in adj[pv])]
            if not al:
                ok = False; break
            allowed.append(al)
        if not ok:
            continue
        for pc in itertools.product(*allowed):
            colp = dict(zip(pF, pc))
            ways = 1
            for qv in qF:
                free = {0, 1, 2}
                for w in adj[qv]:
                    free.discard(col[w] if w in col else colp[w])
                ways *= len(free)
                if not ways:
                    break
            total += ways
            if total > cap:
                return total, anchor_feasible
    return total, anchor_feasible

def find_witness(P, Q, adj, anchors, banned):
    """Return one proper ban-avoiding colouring or None. Complete."""
    Aset = set(anchors)
    pF = [v for v in P if v not in Aset]
    qF = [v for v in Q if v not in Aset]
    for ac in itertools.product(COL, repeat=len(anchors)):
        col = dict(zip(anchors, ac))
        if any(col[a] == banned.get(a, -1) for a in anchors):
            continue
        if any(w in col and col[w] == col[a] for a in anchors for w in adj[a]):
            continue
        allowed = []
        ok = True
        for pv in pF:
            al = [c for c in COL if all(col.get(w) != c for w in adj[pv])]
            if not al:
                ok = False; break
            allowed.append(al)
        if not ok:
            continue
        for pc in itertools.product(*allowed):
            colp = dict(zip(pF, pc))
            psi = dict(col); psi.update(colp)
            good = True
            for qv in qF:
                free = {0, 1, 2}
                for w in adj[qv]:
                    free.discard(psi.get(w, -1))
                if not free:
                    good = False; break
                psi[qv] = min(free)
            if good:
                return psi
    return None

def verify_colouring(psi, edges, banned):
    assert all(psi[u] != psi[v] for u, v in edges), "improper"
    assert all(psi[a] != b for a, b in banned.items()), "ban violated"

ANCH = ['x1', 'x2', 'x3', 'y1', 'y2', 'y3']
RAINBOW = {'x1': 0, 'x2': 1, 'x3': 2, 'y1': 0, 'y2': 1, 'y3': 2}

# ================= H1 =================
P1 = ['x1', 'x2', 'x3'] + [f'p{i}' for i in range(6)]
Q1 = ['y1', 'y2', 'y3'] + [f'q{i}' for i in range(6)]
E1 = set()
for i in (1, 2, 3):
    for j in (1, 2, 3):
        E1.add((f'x{i}', f'y{j}'))
for i, (a, b) in zip((1, 2, 3), [(0, 1), (2, 3), (4, 5)]):
    E1 |= {(f'x{i}', f'q{a}'), (f'x{i}', f'q{b}'), (f'p{a}', f'y{i}'), (f'p{b}', f'y{i}')}
for i in range(6):
    for j in range(6):
        if i != j:
            E1.add((f'p{i}', f'q{j}'))
adj1 = hyp_check("H1", P1, Q1, E1, ANCH)
print(f"H1 hypotheses OK: |V|={len(P1)+len(Q1)}, |E|={len(E1)}, maxdeg={max(len(adj1[v]) for v in adj1)}")

# Independent anchor-local proof: anchors form K_{3,3}; enumerate 3^6.
proper = banfree = 0
for cs in itertools.product(COL, repeat=6):
    col = dict(zip(ANCH, cs))
    if all(col[f'x{i}'] != col[f'y{j}'] for i in (1, 2, 3) for j in (1, 2, 3)):
        proper += 1
        if all(col[a] != RAINBOW[a] for a in ANCH):
            banfree += 1
print(f"H1 anchor K33: proper colourings = {proper}, ban-avoiding among them = {banfree}")
assert proper == 42 and banfree == 0

cnt1, af1 = exact_count(P1, Q1, adj1, ANCH, RAINBOW)
print(f"H1/rainbow EXACT count of proper ban-avoiding colourings = {cnt1} (anchor-feasible stage-1 = {af1})")
assert cnt1 == 0
ctrl = dict(RAINBOW); ctrl['x3'] = 1
w = find_witness(P1, Q1, adj1, ANCH, ctrl)
assert w is not None; verify_colouring(w, E1, ctrl)
print("H1/ctrl (x3 ban -> 1): COLOURABLE, witness verified edge-by-edge")

# ================= (sigma,tau) feasibility, my own enumeration =================
print("\n(sigma,tau) anchor-restriction feasibility (cross edges i!=j always present):")
for mask in range(8):
    M = [i for i in range(3) if mask >> i & 1]
    edges = [(i, j) for i in range(3) for j in range(3) if i != j] + [(i, i) for i in M]
    sols = [(s, t) for s in itertools.product(COL, repeat=3)
            for t in itertools.product(COL, repeat=3)
            if all(s[i] != i for i in range(3)) and all(t[j] != j for j in range(3))
            and all(s[i] != t[j] for i, j in edges)]
    print(f"  M={M}: {len(sols)} -> {sols if len(sols) <= 2 else ''}")
    if not M:
        assert sorted(sols) == [((1, 2, 0), (1, 2, 0)), ((2, 0, 1), (2, 0, 1))]
    else:
        assert sols == []
# The original skeleton's example repair sigma=(2,0,2), tau=(1,0,1):
s, t = (2, 0, 2), (1, 0, 1)
print(f"  skeleton's example sigma={s}: ban-respecting? {all(s[i] != i for i in range(3))} "
      f"(sigma(3)=2 = banned colour of x3 -> the skeleton's own example was ILLEGAL)")

# ================= H2 =================
P2 = ['x1', 'x2', 'x3'] + [f'p{i}' for i in range(12)]
Q2 = ['y1', 'y2', 'y3'] + [f'q{i}' for i in range(12)]
E2 = set()
for i in (1, 2, 3):
    for j in (1, 2, 3):
        if i != j:
            E2.add((f'x{i}', f'y{j}'))
fill = {1: (0, 1), 2: (2, 3), 3: (4, 5)}
for i in (1, 2, 3):
    a, c = fill[i]
    E2 |= {(f'x{i}', f'q{a}'), (f'x{i}', f'q{c}'), (f'x{i}', f'q{i+5}'),
           (f'p{a}', f'y{i}'), (f'p{c}', f'y{i}'), (f'p{i+5}', f'y{i}')}
for blk in (0, 6):
    for i in range(6):
        for j in range(6):
            if i != j:
                E2.add((f'p{blk+i}', f'q{blk+j}'))
for i in (9, 10, 11):
    E2.add((f'p{i}', f'q{i}'))
adj2 = hyp_check("H2", P2, Q2, E2, ANCH)
cnt2, af2 = exact_count(P2, Q2, adj2, ANCH, RAINBOW)
print(f"\nH2 hypotheses OK. H2/rainbow EXACT count = {cnt2} (anchor-feasible = {af2})")
assert cnt2 == 0
w = find_witness(P2, Q2, adj2, ANCH, ctrl)
assert w is not None; verify_colouring(w, E2, ctrl)
print("H2/ctrl: COLOURABLE, witness verified")

# ================= H3 =================
P3 = ['x1', 'x2', 'x3'] + [f'p{i}' for i in range(9)]
Q3 = ['y1', 'y2', 'y3'] + [f'q{i}' for i in range(9)]
E3 = set()
for i in (1, 2, 3):
    for j in (1, 2, 3):
        if i != j:
            E3.add((f'x{i}', f'y{j}'))
for i in (1, 2, 3):
    for t in range(3):
        E3.add((f'x{i}', f'q{3*(i-1)+t}'))
        E3.add((f'p{3*(i-1)+t}', f'y{i}'))
for i in range(9):
    for k in range(5):
        E3.add((f'p{i}', f'q{(i+k) % 9}'))
adj3 = hyp_check("H3", P3, Q3, E3, ANCH)
cnt3, af3 = exact_count(P3, Q3, adj3, ANCH, RAINBOW)
print(f"H3 hypotheses OK. H3/rainbow EXACT count = {cnt3} (anchor-feasible = {af3})")
assert cnt3 == 0

# ================= H4 =================
FSTAR = {
 'q0': ['p1', 'p2', 'p3', 'p4', 'p5'], 'q1': ['p0', 'p2', 'p3', 'p4', 'p5'],
 'q2': ['p0', 'p1', 'p3', 'p4', 'p5'], 'q3': ['p0', 'p3', 'p6', 'p7', 'p8'],
 'q4': ['p1', 'p3', 'p6', 'p7', 'p8'], 'q5': ['p0', 'p1', 'p5', 'p6', 'p7'],
 'q6': ['p2', 'p4', 'p6', 'p7', 'p8'], 'q7': ['p0', 'p2', 'p5', 'p6', 'p8'],
 'q8': ['p1', 'p2', 'p4', 'p7', 'p8']}
E4 = {e for e in E3 if not e[0].startswith('p')}
# E3 stores p-edges as (p, q) or (p, y); keep anchor-anchor + x-q + p-y? NO:
# rebuild cleanly: anchors + anchor-filler edges as in H3, filler block = FSTAR.
E4 = set()
for i in (1, 2, 3):
    for j in (1, 2, 3):
        if i != j:
            E4.add((f'x{i}', f'y{j}'))
for i in (1, 2, 3):
    for t in range(3):
        E4.add((f'x{i}', f'q{3*(i-1)+t}'))
        E4.add((f'p{3*(i-1)+t}', f'y{i}'))
for q, ps in FSTAR.items():
    for p in ps:
        E4.add((p, q))
adj4 = hyp_check("H4", P3, Q3, E4, ANCH)
cnt4, af4 = exact_count(P3, Q3, adj4, ANCH, RAINBOW, cap=10**7)
print(f"H4 hypotheses OK. H4/rainbow EXACT count = {cnt4} (>0 means colourable)")
assert cnt4 > 0
# the explicit witness from the writeup, verbatim:
psi = {'x1': 1, 'x2': 2, 'x3': 0, 'y1': 1, 'y2': 2, 'y3': 0}
for i in range(9):
    psi[f'p{i}'] = 0 if i < 6 else 2
    psi[f'q{i}'] = 2 if i < 3 else 1
verify_colouring(psi, E4, RAINBOW)
print("H4 explicit witness from the writeup verified edge-by-edge + ban-by-ban")

print("\nINDEPENDENT VERIFICATION COMPLETE: H1,H2,H3 UNSAT by exact exhaustive count; H4 SAT.")
