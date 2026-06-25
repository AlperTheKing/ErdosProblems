# Q1'b "spread bipartite avoid-completeness" lemma: COUNTEREXAMPLE VERIFIER
#
# Lemma under test: H connected bipartite, Delta<=6, EXACTLY six degree-5 vertices
# ("anchors"), all others degree 6.  Claim: for every gamma assigning ONE banned
# colour in {0,1,2} per anchor, H has a proper 3-colouring avoiding all bans.
#
# COUNTEREXAMPLE H1 (18 vertices): anchors x1,x2,x3 in P, y1,y2,y3 in Q forming a
# FULL K_{3,3}; rainbow bans gamma(x_i)=i-1, gamma(y_j)=j-1.  Filler: each anchor
# gets 2 private filler neighbours; filler-filler graph = K_{6,6} minus a perfect
# matching (5-regular).  All non-anchors have degree 6.
#
# COUNTEREXAMPLE H2 (30 vertices): anchor graph = K_{3,3} MINUS the perfect matching
# (no x_iy_i edges at all), same rainbow bans; each anchor gets 3 filler neighbours;
# fillers = two rigid blocks based on K_{6,6}-minus-matching.  Shows the failure is
# not only the matched-edge case: a rigid environment kills the cyclic repair too.
#
# COUNTEREXAMPLE H3 (24 vertices): same anchor graph as H2 (no matched edges!) but a
# plain circulant filler -- ALSO uncolourable.  (Discovered while testing: even
# generic-looking fillers can block the forced cyclic repair.)
#
# DELINEATION: randomized search over 5-regular fillers for the M=empty extremal
# configuration, to see whether ANY filler admits a colouring (i.e. whether the
# extremal anchors alone decide the answer, or the filler does).

from collections import deque
import itertools

def build(P, Q, E):
    V = P + Q
    adj = {v: set() for v in V}
    for u, v in E:
        adj[u].add(v); adj[v].add(u)
    return V, adj

def structural_check(name, P, Q, E, adj, anchors):
    V = P + Q
    assert all(((u in P) != (v in P)) for u, v in E), "not bipartite"
    deg5 = sorted(v for v in V if len(adj[v]) == 5)
    assert deg5 == sorted(anchors), (name, deg5)
    assert all(len(adj[v]) == 6 for v in V if v not in deg5)
    seen = {V[0]}; dq = deque([V[0]])
    while dq:
        u = dq.popleft()
        for w in adj[u]:
            if w not in seen:
                seen.add(w); dq.append(w)
    assert len(seen) == len(V), "not connected"
    print(f"{name} OK: |V|={len(V)}, |E|={len(E)}, bipartite, connected, "
          f"exactly six degree-5 vertices (the anchors), rest degree 6")

def colourable(V, adj, banned, order):
    """Complete backtracking: returns a proper ban-avoiding 3-colouring or None."""
    col = {}
    def bt(k):
        if k == len(order):
            return dict(col)
        v = order[k]
        for c in (0, 1, 2):
            if c == banned.get(v, -1):
                continue
            if any(col.get(w) == c for w in adj[v]):
                continue
            col[v] = c
            r = bt(k + 1)
            if r is not None:
                return r
            del col[v]
        return None
    return bt(0)

def check(name, P, Q, E, adj, banned, expect):
    V = P + Q
    anchors = [v for v in V if v[0] in 'xy']
    last = None
    for order in (anchors + [v for v in V if v not in anchors],
                  [v for v in V if v not in anchors] + anchors,
                  sorted(V), sorted(V, reverse=True)):
        res = colourable(V, adj, banned, order)
        if res is not None:  # verify witness independently
            assert all(res[u] != res[v] for u, v in E)
            assert all(res[a] != banned[a] for a in banned)
        if last is not None:
            assert (res is None) == (last is None), "order-dependent result: bug"
        last = res
        print(f"  {name}: order starting {order[0]}: "
              f"{'COLOURABLE' if res is not None else 'UNSAT'}")
    assert (last is not None) == expect, f"{name}: unexpected outcome"
    return last

ANCH = ['x1', 'x2', 'x3', 'y1', 'y2', 'y3']
RAINBOW = {'x1': 0, 'x2': 1, 'x3': 2, 'y1': 0, 'y2': 1, 'y3': 2}

# ================= H1: full anchor K_{3,3} =================
P1 = ['x1', 'x2', 'x3'] + [f'p{i}' for i in range(6)]
Q1 = ['y1', 'y2', 'y3'] + [f'q{i}' for i in range(6)]
E1 = set()
for i in (1, 2, 3):
    for j in (1, 2, 3):
        E1.add((f'x{i}', f'y{j}'))                          # full K_{3,3}
for i, (a, b) in zip((1, 2, 3), [(0, 1), (2, 3), (4, 5)]):
    E1.add((f'x{i}', f'q{a}')); E1.add((f'x{i}', f'q{b}'))
    E1.add((f'y{i}', f'p{a}')); E1.add((f'y{i}', f'p{b}'))
for i in range(6):
    for j in range(6):
        if i != j:
            E1.add((f'p{i}', f'q{j}'))                      # K_{6,6} - PM
V1, adj1 = build(P1, Q1, E1)
structural_check("H1", P1, Q1, E1, adj1, ANCH)
print("H1 + rainbow bans (main counterexample, expect UNSAT):")
check("H1/rainbow", P1, Q1, E1, adj1, RAINBOW, expect=False)
print("H1 + non-rainbow bans (control, expect colourable):")
b = dict(RAINBOW); b['x3'] = 1
check("H1/ctrl", P1, Q1, E1, adj1, b, expect=True)

# independent verification of the anchor-local argument: 3^6 enumeration
anchor_edges = [(f'x{i}', f'y{j}') for i in (1, 2, 3) for j in (1, 2, 3)]
proper = viol = 0
for cs in itertools.product((0, 1, 2), repeat=6):
    col = dict(zip(ANCH, cs))
    if all(col[u] != col[v] for u, v in anchor_edges):
        proper += 1
        if any(col[a] == RAINBOW[a] for a in ANCH):
            viol += 1
print(f"anchor K33 alone: proper colourings={proper}, all violate a ban: {viol == proper}\n")
assert proper > 0 and viol == proper

# ============ anchor-level (sigma,tau) feasibility vs matched-edge set M ============
print("(sigma,tau) feasibility, anchor graph = {x_iy_j : i!=j} + matched set M:")
for mask in range(8):
    M = [i for i in range(3) if mask >> i & 1]
    edges = [(i, j) for i in range(3) for j in range(3) if i != j] + [(i, i) for i in M]
    sols = [(s, t) for s in itertools.product((0, 1, 2), repeat=3)
            for t in itertools.product((0, 1, 2), repeat=3)
            if all(s[i] != i for i in range(3)) and all(t[j] != j for j in range(3))
            and all(s[i] != t[j] for i, j in edges)]
    lab = ','.join(str(i + 1) for i in M) or '-'
    print(f"  M={{{lab}}}: {len(sols)} solutions" +
          (f"   e.g. sigma,tau={sols[0]}" if sols else "   INFEASIBLE"))
print()

# ================= H2: anchor K_{3,3} MINUS perfect matching, rigid filler =================
# copies A (p0..p5/q0..q5) and B (p6..p11/q6..q11), each K_{6,6} minus PM;
# in copy B the matching edges p9q9,p10q10,p11q11 are ADDED back to absorb spare slots.
P2 = ['x1', 'x2', 'x3'] + [f'p{i}' for i in range(12)]
Q2 = ['y1', 'y2', 'y3'] + [f'q{i}' for i in range(12)]
E2 = set()
for i in (1, 2, 3):
    for j in (1, 2, 3):
        if i != j:
            E2.add((f'x{i}', f'y{j}'))                      # K_{3,3} - PM
fill = {1: (0, 1), 2: (2, 3), 3: (4, 5)}
for i in (1, 2, 3):
    a, c = fill[i]
    E2.add((f'x{i}', f'q{a}')); E2.add((f'x{i}', f'q{c}')); E2.add((f'x{i}', f'q{i+5}'))
    E2.add((f'y{i}', f'p{a}')); E2.add((f'y{i}', f'p{c}')); E2.add((f'y{i}', f'p{i+5}'))
for blk in (0, 6):
    for i in range(6):
        for j in range(6):
            if i != j:
                E2.add((f'p{blk+i}', f'q{blk+j}'))
for i in (9, 10, 11):
    E2.add((f'p{i}', f'q{i}'))
V2, adj2 = build(P2, Q2, E2)
structural_check("H2", P2, Q2, E2, adj2, ANCH)
print("H2 + rainbow bans (second counterexample, expect UNSAT):")
check("H2/rainbow", P2, Q2, E2, adj2, RAINBOW, expect=False)
print("H2 + non-rainbow bans (control, expect colourable):")
b = dict(RAINBOW); b['x3'] = 1
check("H2/ctrl", P2, Q2, E2, adj2, b, expect=True)

# ================= H3: same anchors as H2, circulant filler =================
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
        E3.add((f'y{i}', f'p{3*(i-1)+t}'))
for i in range(9):
    for k in range(5):
        E3.add((f'p{i}', f'q{(i+k) % 9}'))                  # 5-regular circulant
V3, adj3 = build(P3, Q3, E3)
structural_check("H3", P3, Q3, E3, adj3, ANCH)
print("H3 + rainbow bans (third counterexample -- NO matched anchor edges, expect UNSAT):")
check("H3/rainbow", P3, Q3, E3, adj3, RAINBOW, expect=False)

# ============ randomized delineation: vary the 5-regular filler ============
import random
random.seed(944)
print("\nRandom 5-regular fillers on 9+9 (anchor graph = K33 - PM, rainbow bans):")
n_col = n_unsat = 0
example = None
for trial in range(200):
    # filler = union of 5 random disjoint perfect matchings p_i ~ q_{perm(i)}
    while True:
        perms = []
        used = set()
        ok = True
        for _ in range(5):
            for _ in range(400):
                pi = list(range(9)); random.shuffle(pi)
                if all((i, pi[i]) not in used for i in range(9)):
                    perms.append(pi)
                    used.update((i, pi[i]) for i in range(9))
                    break
            else:
                ok = False
                break
        if ok:
            break
    Ef = set(E3) - {e for e in E3 if e[0][0] == 'p'}
    for pi in perms:
        for i in range(9):
            Ef.add((f'p{i}', f'q{pi[i]}'))
    Vf, adjf = build(P3, Q3, Ef)
    if not all(len(adjf[v]) in (5, 6) for v in Vf):
        continue
    if sorted(v for v in Vf if len(adjf[v]) == 5) != sorted(ANCH):
        continue
    res = colourable(Vf, adjf, RAINBOW,
                     ANCH + [v for v in Vf if v not in ANCH])
    if res is not None:
        assert all(res[u] != res[v] for u, v in Ef)
        assert all(res[a] != RAINBOW[a] for a in ANCH)
        n_col += 1
        if example is None:
            example = perms
    else:
        n_unsat += 1
print(f"  trials with valid degree profile: {n_col + n_unsat}, "
      f"COLOURABLE: {n_col}, UNSAT: {n_unsat}")
if example:
    print(f"  example colourable filler (5 matchings): {example}")

# ================= H4: M=empty extremal anchors + twin-structured filler =================
# Hand-designed 5-regular filler F* that DOES extend (delineation: the M=empty case is
# filler-dependent; random/expander fillers fail, this degenerate one succeeds).
FSTAR = {
    'q0': ['p1', 'p2', 'p3', 'p4', 'p5'],
    'q1': ['p0', 'p2', 'p3', 'p4', 'p5'],
    'q2': ['p0', 'p1', 'p3', 'p4', 'p5'],
    'q3': ['p0', 'p3', 'p6', 'p7', 'p8'],
    'q4': ['p1', 'p3', 'p6', 'p7', 'p8'],
    'q5': ['p0', 'p1', 'p5', 'p6', 'p7'],
    'q6': ['p2', 'p4', 'p6', 'p7', 'p8'],
    'q7': ['p0', 'p2', 'p5', 'p6', 'p8'],
    'q8': ['p1', 'p2', 'p4', 'p7', 'p8'],
}
E4 = {e for e in E3 if e[0][0] != 'p'}          # keep anchor + anchor-filler edges
for q, ps in FSTAR.items():
    for p in ps:
        E4.add((p, q))
V4, adj4 = build(P3, Q3, E4)
structural_check("H4", P3, Q3, E4, adj4, ANCH)
print("H4 + rainbow bans (twin-structured filler, expect COLOURABLE):")
check("H4/rainbow", P3, Q3, E4, adj4, RAINBOW, expect=True)
# verify the hand-constructed explicit colouring too
psi = {'x1': 1, 'x2': 2, 'x3': 0, 'y1': 1, 'y2': 2, 'y3': 0}
for i in range(9):
    psi[f'p{i}'] = 0 if i < 6 else 2
    psi[f'q{i}'] = 2 if i < 3 else 1
assert all(psi[u] != psi[v] for u, v in E4)
assert all(psi[a] != RAINBOW[a] for a in ANCH)
print("  hand-constructed explicit colouring for H4 verified")

print("\nALL CHECKS PASSED: lemma REFUTED (H1, H2, H3 with rainbow bans);")
print("H4 shows the M=empty extremal case is filler-dependent (not always UNSAT).")
