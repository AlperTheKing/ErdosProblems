#!/usr/bin/env python3
"""
Verify the LOAD-BEARING claim of Q10 section 5 (the 6th anticomplete root):
For an induced C5 = c_0..c_4 in the Clebsch graph K and the (unique) vertex z
ANTICOMPLETE to that C5, the 6-bit signature
   sig(w) = (1[w~c_0], ..., 1[w~c_4], 1[w~z])
is DISTINCT over all 16 Clebsch vertices.
If so, every Clebsch-blowup vertex is uniquely identified by its frame-signature, so
the canonical (realized-type -> Clebsch-vertex) map gives cost 0 on Clebsch blowups
==> F_{C,z}^(6) = 0 there, which (with F_C suffices-generically, verify_FC_c5root.py)
makes RR = min{min_C F_C, min_{C,z} F_{C,z}} <= (N^2/5-e)/2 hold on band graphs incl. Clebsch[t].
Also confirm Q10 eq (13): the 6 ABSENT (P_C, 1[~z]) types are (emptyset,1) and ({i},1).
"""
import itertools

labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]
N = 16
idx = {labels[i]: i for i in range(16)}
adj = [set() for _ in range(16)]
for i in range(16):
    for j in range(16):
        if i != j and bin(labels[i] ^ labels[j]).count('1') == 4:
            adj[i].add(j)

# find an induced C5 in Clebsch
def find_induced_C5():
    for combo in itertools.combinations(range(16), 5):
        sub = [(a, b) for a, b in itertools.combinations(combo, 2) if b in adj[a]]
        if len(sub) != 5:
            continue
        d = {v: 0 for v in combo}
        for a, b in sub:
            d[a] += 1; d[b] += 1
        if all(d[v] == 2 for v in combo):
            # order into a cycle
            start = combo[0]; cyc = [start]; prev = None; cur = start
            for _ in range(4):
                nxt = [w for w in adj[cur] if w in d and w != prev][0]
                cyc.append(nxt); prev, cur = cur, nxt
            return cyc
    return None

C = find_induced_C5()
print(f"Induced C5 in Clebsch: {C} (labels {[bin(labels[c]) for c in C]})")

# vertices anticomplete to C (no neighbor in C)
Cset = set(C)
anti = [w for w in range(16) if w not in Cset and not (adj[w] & Cset)]
print(f"Vertices anticomplete to C: {anti} (count {len(anti)})")
z = anti[0]

# 6-bit signatures
sigs = {}
for w in range(16):
    s = tuple(1 if (C[i] in adj[w] or C[i] == w) else 0 for i in range(5)) + (1 if (w in adj[z] or w == z) else 0,)
    sigs[w] = s
distinct = len(set(sigs.values())) == 16
print(f"16 six-bit signatures all DISTINCT? {distinct}  (#distinct={len(set(sigs.values()))})")

# Without z (5-bit): how many distinct? (should be < 16 -> the twin-pair collision)
sigs5 = {}
for w in range(16):
    sigs5[w] = tuple(1 if (C[i] in adj[w] or C[i] == w) else 0 for i in range(5))
print(f"Without z (5-bit): #distinct = {len(set(sigs5.values()))} (collisions = the Clebsch twin-pairs the 5-root can't separate)")

# Confirm eq(13): the (P_C-type, 1[~z]) realized types, and which formal types are absent.
# P_C type for a Clebsch vertex w: the set {i : w~c_i}; for triangle-free C5 nbhd it is
# emptyset / {i} / {i-1,i+1}. Plus the z-bit.
def pc_type(w):
    P = tuple(sorted(i for i in range(5) if C[i] in adj[w]))
    return P
realized = set()
for w in range(16):
    P = pc_type(w)
    zb = 1 if w in adj[z] else 0
    realized.add((P, zb))
# all FORMAL types: P in {(), (i,), (i-1,i+1)} x zb in {0,1} = 11*2 = 22
formal = set()
for zb in (0, 1):
    formal.add(((), zb))
    for i in range(5):
        formal.add(((i,), zb))
        formal.add((tuple(sorted(((i-1) % 5, (i+1) % 5))), zb))
absent = formal - realized
print(f"#realized (P_C,zbit) types = {len(realized)} of 22 formal; #absent = {len(absent)}")
print(f"Absent types: {sorted(absent)}")
print("Q10 eq(13) claims the 6 absent are (emptyset,1) and ({i},1) for i in Z5.")
print("DONE")
