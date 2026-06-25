"""Diagonal-partner criticality-unlock test (S-B2 vs S-K tension).
For an always-balanced shore-shaped B (conn, Delta<=6, e=3n-3, sum b=6, 3-col,
every proper colouring has cut-weight vector (2,2,2)):
  pick a 3+3 split of the six cut UNITS (vertex v contributes b[v] units) into
  T_p, T_l. A diagonal partner A forces p=l=c; G-w is 3-colourable iff B-w has a
  proper colouring with a colour c absent from BOTH T_p and T_l restricted to
  units not on w.  B is criticality-FEASIBLE for this split iff EVERY w in B
  unlocks.  Question: does ANY (B, split) achieve all-vertex unlock?
Reads g6 on stdin (any graphs); filters to always-balanced; tests all splits.
usage: geng -c -D6 n e:e | python diag_unlock.py n
"""
import sys, itertools
n = int(sys.argv[1])
def g6decode(s):
    nn = ord(s[0]) - 63
    adj = [set() for _ in range(nn)]
    bit = 0
    for j in range(1, nn):
        for i in range(j):
            byte = 1 + bit // 6; off = 5 - bit % 6
            if (ord(s[byte]) - 63) >> off & 1:
                adj[i].add(j); adj[j].add(i)
            bit += 1
    return nn, adj
def all_colourings(nn, adj, skip=-1):
    verts = [v for v in range(nn) if v != skip]
    verts.sort(key=lambda v: -len(adj[v]))
    col = {}
    def bt(i):
        if i == len(verts):
            yield dict(col); return
        v = verts[i]
        used = {col[u] for u in adj[v] if u in col}
        for c in range(3):
            if c in used: continue
            col[v] = c
            yield from bt(i+1)
            del col[v]
    yield from bt(0)
def always_balanced(nn, adj, b):
    any_col = False
    for col in all_colourings(nn, adj):
        w = [0,0,0]
        for v in range(nn): w[col[v]] += b[v]
        if tuple(sorted(w)) != (2,2,2): return False
        any_col = True
    return any_col
checked = 0; ab = 0; feasible = 0
feas_examples = []
for line in sys.stdin:
    line = line.strip()
    if not line or line[0] == '>': continue
    nn, adj = g6decode(line)
    b = [6 - len(adj[v]) for v in range(nn)]
    if sum(b) != 6: continue
    # connected
    seen={0}; st=[0]
    while st:
        x=st.pop()
        for y in adj[x]:
            if y not in seen: seen.add(y); st.append(y)
    if len(seen)!=nn: continue
    checked += 1
    if not always_balanced(nn, adj, b): continue
    ab += 1
    # units: list of vertices, with multiplicity b[v]
    units = []
    for v in range(nn):
        units += [v]*b[v]
    # precompute, for each w, all colourings of B-w (store per-vertex colour maps)
    cols_minus = {}
    for w in range(nn):
        cols_minus[w] = list(all_colourings(nn, adj, skip=w))
    # try every 3+3 split of the 6 unit-slots (indices into units)
    slot_idx = list(range(6))
    good_split = None
    seen_splits = set()
    for Tp_slots in itertools.combinations(slot_idx, 3):
        Tp = tuple(sorted(units[i] for i in Tp_slots))
        Tl = tuple(sorted(units[i] for i in slot_idx if i not in Tp_slots))
        key = (Tp, Tl) if Tp <= Tl else (Tl, Tp)
        if key in seen_splits: continue
        seen_splits.add(key)
        # check all w unlock
        all_unlock = True
        for w in range(nn):
            unlocked = False
            for col in cols_minus[w]:
                # union colours of Tp and Tl, units on w removed
                present = [False,False,False]
                for v in list(Tp)+list(Tl):
                    if v == w: continue   # w deleted -> its units gone
                    present[col[v]] = True
                if not all(present):   # some colour c missing from union
                    unlocked = True; break
            if not unlocked:
                all_unlock = False; break
        if all_unlock:
            good_split = (Tp, Tl); break
    if good_split:
        feasible += 1
        if len(feas_examples) < 5:
            feas_examples.append((line, good_split))
print(f"n={n} checked={checked} alwaysBalanced={ab} criticalityFeasible={feasible}")
for g, sp in feas_examples:
    print(f"  FEASIBLE g6={g} split={sp}")
