#!/usr/bin/env python3
"""Debug which circuit constraint blocks the 25-atom reconstruction."""
import sys
from itertools import combinations
from collections import defaultdict
sys.path.insert(0, '.')
from fixture_atoms_exact import build

def probe(tag):
    fx = build(tag)
    cand = fx['cand']; edges = fx['edges']
    print(f"\n=== {tag}: {len(cand)} candidates ===")
    # per-owner candidate degrees
    dM = defaultdict(int)
    for u, w in cand:
        dM[u] += 1; dM[w] += 1
    print("candidate dM:", dict(sorted(dM.items())))
    # forced-edge coverage: which edges are 'forced' by which atoms
    forced_by = {tuple(sorted(e)): [] for e in map(tuple, edges)}
    for a in cand:
        for e in fx['edge_forced'][a]:
            forced_by[tuple(sorted(e))].append(a)
    nof = [e for e, lst in forced_by.items() if not lst]
    print(f"edges forced by NO candidate atom: {len(nof)} {nof[:10]}")
    # union coverage by all candidates
    uni = set()
    for a in cand:
        uni |= fx['edge_union'][a]
    print(f"union of ALL candidates covers all edges: {uni == edges}")
    # bad-graph triangles among candidates
    badadj = defaultdict(set)
    for u, w in cand:
        badadj[u].add(w); badadj[w].add(u)
    tris = [(u, w, z) for u, w in cand for z in sorted(badadj[u] & badadj[w]) if z > w]
    print(f"candidate bad triangles: {len(tris)} {tris[:6]}")
    # how many candidates are triangle-involved
    tv = {v for t in tris for v in t}
    print(f"triangle-involved vertices: {sorted(tv)}")

for tag in ('298', '264'):
    probe(tag)
