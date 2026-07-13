#!/usr/bin/env python3
"""AGENT-HOMOLOGY Check 4: airtight verification of the #264 blockade + corner
owner-eligibility + one-atom 4-cycle variants + explicit L1/L2/L3 zeros.
"""
import sys
from itertools import combinations, product
from collections import defaultdict
sys.path.insert(0, '.')
from fixture_atoms_exact import build
from fixture_264_variants import find as find_variant
from fixture_atoms_v3 import find_circuits_v3
from fixture_state_graph import classify

fx = build('264')
subs, _ = find_variant(fx, (0,), cap=1000)
subs = [sorted(map(tuple, s)) for s in subs]
print(f"#264 circuits: {len(subs)}")

circ = subs[1]  # the first with rotor cores
chosen = set(circ)
sq = (0, 9, 1, 10)
sq_edges = [frozenset((0, 9)), frozenset((9, 1)), frozenset((1, 10)), frozenset((10, 0))]
print(f"\nsquare {sq}; edges {[tuple(sorted(e)) for e in sq_edges]}")
print(f"movers: AB=(2,3) rows:", fx['rows'][(2, 3)])
print(f"        PQ=(15,17) rows:", fx['rows'][(15, 17)])

for a in [(1, 8), (14, 17)]:
    print(f"\nblocked atom {a}: {len(fx['rows'][a])} rows, per-row square edges used:")
    for r in fx['rows'][a]:
        used = [tuple(sorted(e)) for i in range(4)
                for e in [frozenset((r[i], r[i+1]))] if e in sq_edges]
        print(f"   {r} -> {used}")
        assert used, "FAIL: found a square-avoiding row"
print("\nBLOCKADE VERIFIED: every row of (1,8) and (14,17) uses >=1 square edge")
print("=> in every tuple their fixed selected rows pin >=1 square edge at multiplicity >=1")
print("=> the four square edges can never all serve as holes along a period-4 rotor")

# corner owner-eligibility across all circuits
for si, s in enumerate(subs):
    dM = defaultdict(int)
    for u, w in s:
        dM[u] += 1; dM[w] += 1
    elig = sorted(u for u in range(fx['n']) if len(fx['adj'][u]) == 5 and dM[u] == 5)
    print(f"circuit#{si}: equality-scale owners (degB=degM=5): {elig}")

# one-atom 4-cycles in row-swap graphs (single-middle steps)
def row_moves(fam):
    g = defaultdict(list)
    for i, r1 in enumerate(fam):
        for j, r2 in enumerate(fam):
            if i == j:
                continue
            diff = [p for p in range(5) if r1[p] != r2[p]]
            if len(diff) == 1 and diff[0] in (1, 2, 3):
                g[i].append(j)
    return g

print("\none-atom row-swap graphs (chosen atoms, #264 circuit#1):")
tot4 = 0
for a in circ:
    fam = fx['rows'][a]
    if len(fam) < 3:
        continue
    g = row_moves(fam)
    # count directed 4-cycles visiting 4 distinct rows
    c4 = 0
    n = len(fam)
    for quad in combinations(range(n), 4):
        for perm in [(quad[0], x, y, z) for x, y, z in
                     [(b, c, d) for b in quad[1:] for c in quad[1:] for d in quad[1:]
                      if len({b, c, d}) == 3]]:
            a0, b0, c0, d0 = perm
            if b0 in g[a0] and c0 in g[b0] and d0 in g[c0] and a0 in g[d0]:
                c4 += 1
    if c4:
        print(f"  atom {a}: {len(fam)} rows, directed 4-cycles (distinct rows): {c4}")
        tot4 += c4
print(f"total one-atom 4-cycle skeletons: {tot4}")

# explicit L1/L2/L3 zeros on circuit#1 (bigger sample, explicit keys)
import random
atoms = circ
rows = {a: fx['rows'][a] for a in atoms}
sub = dict(tag='264-c1', edges=fx['edges'], adj=fx['adj'], color=fx['color'],
           atoms=atoms, rows=rows, bad={frozenset(a) for a in atoms},
           degB={u: len(fx['adj'][u]) for u in range(fx['n'])}, degM=defaultdict(int))
for u, w in atoms:
    sub['degM'][u] += 1; sub['degM'][w] += 1
rng = random.Random(99)
sizes = [len(rows[a]) for a in atoms]
cnt = defaultdict(int)
for _ in range(30000):
    om = tuple(rng.randrange(s) for s in sizes)
    dts, st = classify(sub, om)
    for d in dts:
        cnt['L0'] += 1
        cnt['L1'] += d['l1']
        cnt['L2'] += d['l2']
        cnt['L3'] += d['l3']
        cnt['profile'] += (d['okdeg'] and d['onelat'] and d['rt'] and d['cov'])
print(f"\n[264-c1] 30000-tuple census: {dict(cnt)}")
