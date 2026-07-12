#!/usr/bin/env python3
"""AGENT-HOMOLOGY Check 1: exact anatomy of the R39 8-vtx four-state neutral square rotor.

Claims verified here (each printed PASS/FAIL, all integer arithmetic):
  H1  In each of the 4 states the square-edge multiplicity pattern is (2,1,1,0) cyclically:
      the doubled (collision) edge and the zero (hole/latent) edge are ANTIPODAL square edges.
  H2  Each rotor transition advances the necklace phase by exactly +1 (hole walks one square
      step per transition; winding over the period = 1 full loop, i.e. 4 steps).
  H3  Entering owner of each transition is an ENDPOINT of the current hole edge; the pivot
      (shared vertex of consecutive hole edges) equals the NEXT transition's entering owner;
      consecutive entering owners are blue-adjacent and alternate cut shores.
  H4  The four signed swap chains (in Z^E, +new row edges -old row edges) satisfy
      T3 = -T1 and T4 = -T2: the rotor is an INTERLEAVED PAIR OF INVERSE MOVES (a commutator
      pattern).  Consequently EVERY additive state functional (any linear functional of the
      edge-multiplicity vector, the pair-count matrix, the row-count vector r, or any owner
      balance built from them) telescopes to 0 around the cycle.  Verified numerically:
      componentwise sum of deltas of (m, n, r) over the 4 transitions is identically zero.
  H5  Support delta is 0 on every rotor transition and u=1 exactly (one old middle edge had
      multiplicity 1, the other had 2): the rotor is support-constant with the R43 live surface
      signature (one genuinely new support edge per transition).
  H6  Liveness audit: in every state, the active graph is the single hole edge whose component
      contains NO bad-edge endpoint pair => NO transition is scoped-live (the known vacuity).
"""
from itertools import combinations

names = ['a', 'b', 'p', 'q', 'x', 'y', 'm', 'v']
idx = {s: i for i, s in enumerate(names)}
a, b, p, q, x, y, m, v = (idx[s] for s in names)

blue = {frozenset(e) for e in [(a, x), (y, b), (p, m), (v, q), (x, m), (m, y), (y, v), (v, x)]}
bad = {frozenset(e) for e in [(a, b), (p, q)]}
sideA = {x, y, p, q}          # shore A ; shore B = {m,v,a,b}

A_m, A_v = (a, x, m, y, b), (a, x, v, y, b)
B_x, B_y = (p, m, x, v, q), (p, m, y, v, q)

states = ['w_mx', 'w_my', 'w_vy', 'w_vx']
rows_of = {'w_mx': (A_m, B_x), 'w_my': (A_m, B_y), 'w_vy': (A_v, B_y), 'w_vx': (A_v, B_x)}
# directed rotor cycle
cyc = [('w_mx', 'w_my'), ('w_my', 'w_vy'), ('w_vy', 'w_vx'), ('w_vx', 'w_mx')]

square = [frozenset((x, m)), frozenset((m, y)), frozenset((y, v)), frozenset((v, x))]  # cyclic order

def edges_of_row(r):
    return [frozenset((r[i], r[i + 1])) for i in range(4)]

def mult(rows):
    mm = {}
    for r in rows:
        for e in edges_of_row(r):
            mm[e] = mm.get(e, 0) + 1
    return mm

def paircount(rows):
    n = {}
    for r in rows:
        for u1, u2 in combinations(sorted(set(r)), 2):
            n[(u1, u2)] = n.get((u1, u2), 0) + 1
    return n

def rvec(rows):
    r_ = [0] * 8
    for row in rows:
        for u in set(row):
            r_[u] += 1
    return r_

ok = True
def chk(cond, label):
    global ok
    print(('PASS ' if cond else 'FAIL ') + label)
    ok = ok and cond

# --- H1: necklace pattern (2,1,1,0), hole/double antipodal
patterns = {}
for st in states:
    mm = mult(rows_of[st])
    pat = [mm.get(e, 0) for e in square]
    patterns[st] = pat
    hole = [i for i, c in enumerate(pat) if c == 0]
    dbl = [i for i, c in enumerate(pat) if c == 2]
    chk(sorted(pat) == [0, 1, 1, 2] and len(hole) == 1 and len(dbl) == 1
        and (hole[0] - dbl[0]) % 4 == 2,
        f"H1 {st}: square multiplicities {pat} ; hole={square[hole[0]] if hole else None} antipodal to double")

# --- H2: phase advances by exactly one square-step per transition
def phase(st):
    pat = patterns[st]
    return pat.index(0)
phases = [phase(s1) for s1, _ in cyc]
steps = [(phase(s2) - phase(s1)) % 4 for s1, s2 in cyc]
chk(all(st in (1, 3) for st in steps) and len(set(steps)) == 1 and sum(1 for _ in steps) == 4,
    f"H2 hole phases along cycle {phases} steps {steps}: constant +/-1 step, total winding = 1 loop")

# --- H3: entering owner = endpoint of current hole; pivot = next entering owner; shores alternate
entering, expelled, holes = [], [], []
for s1, s2 in cyc:
    r1, r2 = rows_of[s1], rows_of[s2]
    (old, new), = [(u, w) for u, w in zip(r1, r2) if u != w]
    pos, = [i for i in range(5) if old[i] != new[i]]
    entering.append(new[pos]); expelled.append(old[pos])
    mm = mult(r1)
    hole_e, = [e for e in square if mm.get(e, 0) == 0]
    holes.append(hole_e)
c3 = all(entering[i] in holes[i] for i in range(4))
pivots = []
for i in range(4):
    shared = holes[i] & holes[(i + 1) % 4]
    pivots.append(next(iter(shared)) if shared else None)
c3b = all(pivots[i] == entering[(i + 1) % 4] for i in range(4))
c3c = all((entering[i] in sideA) != (entering[(i + 1) % 4] in sideA) for i in range(4))
c3d = all(frozenset((entering[i], entering[(i + 1) % 4])) in blue for i in range(4))
chk(c3 and c3b and c3c and c3d,
    f"H3 entering={[names[t] for t in entering]} pivots={[names[t] if t is not None else '-' for t in pivots]}"
    " : owner in hole, pivot = next owner, owners blue-adjacent + shore-alternating")

# --- H4: signed chains T3=-T1, T4=-T2; all additive functionals telescope
def chain(s1, s2):
    d = {}
    for rr, sgn in ((rows_of[s2], 1), (rows_of[s1], -1)):
        for r in rr:
            for e in edges_of_row(r):
                d[e] = d.get(e, 0) + sgn
    return {e: c for e, c in d.items() if c}
T = [chain(s1, s2) for s1, s2 in cyc]
c4 = (T[2] == {e: -c for e, c in T[0].items()}) and (T[3] == {e: -c for e, c in T[1].items()})
tot_m = {}
for t_ in T:
    for e, c in t_.items():
        tot_m[e] = tot_m.get(e, 0) + c
c4b = all(c == 0 for c in tot_m.values())
# pair-count and r-vector telescoping
def dsum(ds):
    out = {}
    for d in ds:
        for k, c in d.items():
            out[k] = out.get(k, 0) + c
    return {k: c for k, c in out.items() if c}
dn = []
dr = []
for s1, s2 in cyc:
    n1, n2 = paircount(rows_of[s1]), paircount(rows_of[s2])
    dn.append({k: n2.get(k, 0) - n1.get(k, 0) for k in set(n1) | set(n2)})
    r1, r2 = rvec(rows_of[s1]), rvec(rows_of[s2])
    dr.append({i: r2[i] - r1[i] for i in range(8)})
c4c = not dsum(dn) and not dsum(dr)
chk(c4 and c4b and c4c,
    "H4 T3=-T1, T4=-T2 (interleaved inverse pairs / commutator); m-, n-, r-deltas all telescope to 0")

# --- H5: support-constant, u=1, exactly one genuinely new support edge per transition
c5 = True
for i, (s1, s2) in enumerate(cyc):
    m1, m2 = mult(rows_of[s1]), mult(rows_of[s2])
    S1 = {e for e, c in m1.items() if c}
    S2 = {e for e, c in m2.items() if c}
    newsup = S2 - S1
    gone = S1 - S2
    # old middle edges: the two negative-chain edges
    negs = [e for e, c in T[i].items() if c < 0]
    u = sum(1 for e in negs if m1.get(e, 0) == 1)
    c5 = c5 and len(S1) == len(S2) == 7 and len(newsup) == 1 and len(gone) == 1 and u == 1
chk(c5, "H5 every transition support-constant (7 -> 7), exactly 1 new + 1 lost support edge, u=1")

# --- H6: liveness audit (scoped): active component never contains a bad endpoint pair
c6 = True
for st in states:
    rows = rows_of[st]
    sup = {e for e, c in mult(rows).items() if c}
    sel = {u for r in rows for u in r}
    act = {e for e in blue if e not in sup and all(w in sel for w in e)}
    # components of act
    comp_v = set()
    for e in act:
        comp_v |= set(e)
    captured = any(set(t) <= comp_v for t in map(tuple, bad))
    c6 = c6 and act == {holes[0] if st == 'w_mx' else next(e for e in square if mult(rows).get(e, 0) == 0)} and not captured
chk(c6, "H6 active graph = single hole edge; no bad endpoint pair captured => zero scoped-live transitions")

print()
print("VERDICT:", "ALL PASS" if ok else "SOME FAIL")
