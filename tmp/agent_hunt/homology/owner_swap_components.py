#!/usr/bin/env python3
"""AGENT-HOMOLOGY Check 5: owner-swap component analysis (the full-period kill).

Exact facts used (both verified in this session's earlier checks):
  F1 A live transition's entering vertex is a scoped profile owner; at the equality
     scale t the owner has deg_B = deg_M = t.  On a circuit the eligible owner set
     OWN = {u : deg_B(u) = t and chosen bad degree(u) = t} is computable exactly.
  F2 Along any directed cycle of live middle-swaps, each touched atom's selected row
     returns; a middle expelled from an atom can only be restored by a later swap on
     the same atom, whose inserted vertex is the entering owner of that swap.  Hence
     every middle ever expelled along the cycle is itself in OWN, and each touched
     atom's row walks a closed walk inside its OWNER-SWAP GRAPH: vertices = DB rows,
     arcs = single-interior-position replacements whose inserted vertex is in OWN and
     whose expelled vertex is in OWN.
  F3 If every component of every atom's owner-swap graph is a single edge or vertex
     (bounce-only), every all-live cycle is a period-2 bounce; no balanced rotor of
     any period exists on the circuit, for any tuple.

This script computes the owner-swap graphs for all reconstructed circuits of #298
and #264 and reports component structure.
"""
import sys
from itertools import combinations
from collections import defaultdict
sys.path.insert(0, '.')
from fixture_atoms_exact import build
from fixture_atoms_v3 import find_circuits_v3
from fixture_264_variants import find as find_variant

def owner_swap_analysis(fx, circ, label):
    dM = defaultdict(int)
    for u, w in circ:
        dM[u] += 1; dM[w] += 1
    OWN = {u for u in range(fx['n']) if len(fx['adj'][u]) == 5 and dM[u] == 5}
    print(f"  [{label}] eligible equality-scale owners: {sorted(OWN)}")
    bounce_only = True
    touched_atoms = 0
    for a in circ:
        fam = fx['rows'][a]
        arcs = []
        for i, r1 in enumerate(fam):
            for j, r2 in enumerate(fam):
                if i == j:
                    continue
                diff = [p for p in range(5) if r1[p] != r2[p]]
                if len(diff) == 1 and diff[0] in (1, 2, 3):
                    p = diff[0]
                    if r2[p] in OWN and r1[p] in OWN:
                        arcs.append((i, j))
        if not arcs:
            continue
        touched_atoms += 1
        # component structure of the owner-swap graph
        gadj = defaultdict(set)
        for i, j in arcs:
            gadj[i].add(j); gadj[j].add(i)
        seen = set()
        comps = []
        for s in gadj:
            if s in seen:
                continue
            stack = [s]; comp = {s}; seen.add(s)
            while stack:
                x = stack.pop()
                for y in gadj[x]:
                    if y not in seen:
                        seen.add(y); comp.add(y); stack.append(y)
            comps.append(comp)
        maxc = max(len(c) for c in comps)
        cyc = any(sum(len(gadj[x]) for x in c) // 2 >= len(c) for c in comps)
        if maxc > 2 or cyc:
            bounce_only = False
        print(f"    atom {a}: owner-swap arcs {len(arcs)}, components "
              f"{sorted(len(c) for c in comps)}, contains cycle: {cyc}")
        for i, j in arcs[:4]:
            p, = [q for q in range(5) if fam[i][q] != fam[j][q]]
            print(f"      {fam[i]} -> {fam[j]} (expel {fam[i][p]}, enter {fam[j][p]})")
    print(f"  [{label}] owner-swappable atoms: {touched_atoms}; "
          f"VERDICT: {'BOUNCE-ONLY => no all-live rotor of any period on this circuit'
                      if bounce_only else 'larger owner-swap components exist (needs deeper check)'}")
    return bounce_only

if __name__ == '__main__':
    for tag in ('298', '264'):
        fx = build(tag)
        if tag == '298':
            subs = find_circuits_v3(fx, cap=1000)
        else:
            subs, _ = find_variant(fx, (0,), cap=1000)
        subs = [sorted(map(tuple, s)) for s in subs]
        print(f"\n===== {tag}: {len(subs)} circuits =====")
        allb = True
        for si, s in enumerate(subs):
            allb &= owner_swap_analysis(fx, s, f"{tag}-c{si}")
        print(f"===== {tag}: ALL CIRCUITS BOUNCE-ONLY: {allb} =====")
