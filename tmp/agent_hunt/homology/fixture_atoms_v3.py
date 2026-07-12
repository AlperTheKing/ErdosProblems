#!/usr/bin/env python3
"""AGENT-HOMOLOGY Check 2d: exact circuit reconstruction v3, matching the generator
(tmp/fanout/r42_graph_specific_exclusion/rooted_t5_support_cp_sat.py) exactly:
  - 25 atoms among same-shore d4 pairs, rooted atom (2,3) required;
  - owners 0,1: selected bad degree exactly 5;
  - full graph (support+bad) triangle-free;
  - every support edge in >= 2 chosen footprints;
  - deletion-SDR: for every chosen atom ex, the remaining 24 atoms perfectly match
    the 24 support edges within footprints;
  - Forced=Inc for owners 0,1: nonincident candidate atoms whose EVERY row contains
    the owner are excluded from selection.
Then: exhaustive/sampled L0-L3 liveness census per circuit found + rotor-core presence.
"""
import sys
from itertools import combinations, product
from collections import defaultdict
sys.path.insert(0, '.')
from fixture_atoms_exact import build, census_subset

def perfect_sdr(footmasks, edge_count=24):
    """footmasks: list of ints (bitmask of edges). Perfect matching atoms->edges?"""
    n = len(footmasks)
    matchR = [-1] * edge_count
    def aug(i, seen):
        m = footmasks[i]
        while m:
            e = (m & -m).bit_length() - 1
            m &= m - 1
            if not (seen >> e) & 1:
                seen |= 1 << e
                if matchR[e] == -1 or aug(matchR[e], seen):
                    matchR[e] = i
                    return True, seen
            # note: seen not propagated back from failed branch is fine (monotone set)
        return False, seen
    size = 0
    for i in range(n):
        okf, _ = aug2(footmasks, i, matchR)
        if okf:
            size += 1
    return size

def aug2(footmasks, i, matchR, seen=None):
    if seen is None:
        seen = set()
    m = footmasks[i]
    while m:
        e = (m & -m).bit_length() - 1
        m &= m - 1
        if e in seen:
            continue
        seen.add(e)
        if matchR[e] == -1 or aug2(footmasks, matchR[e], matchR, seen)[0]:
            matchR[e] = i
            return True, seen
    return False, seen

def matching_size(footmasks, edge_count=24):
    matchR = [-1] * edge_count
    size = 0
    for i in range(len(footmasks)):
        ok, _ = aug2(footmasks, i, matchR)
        if ok:
            size += 1
    return size

def find_circuits_v3(fx, cap=200):
    cand = fx['cand']
    edges = sorted(tuple(sorted(e)) for e in fx['edges'])
    eidx = {e: i for i, e in enumerate(edges)}
    # Forced=Inc exclusions for owners 0,1
    usable = []
    for a in cand:
        excl = False
        for owner in (0, 1):
            if owner not in a and all(owner in row for row in fx['rows'][a]):
                excl = True
        if not excl:
            usable.append(a)
    foot = {}
    for a in usable:
        m = 0
        for e in fx['edge_union'][a]:
            m |= 1 << eidx[tuple(sorted(e))]
        foot[a] = m
    print(f"  candidates {len(cand)} -> usable after Forced=Inc exclusion {len(usable)}")
    root = (2, 3)
    assert root in foot
    K = len(usable)
    order = sorted(usable, key=lambda a: (a != root,))
    res = []
    chosen = []
    degM = defaultdict(int)
    badadj = defaultdict(set)
    edge_cnt = [0] * 24
    # per-edge available counts for pruning
    avail = [0] * 24
    for a in usable:
        for e in range(24):
            if (foot[a] >> e) & 1:
                avail[e] += 1

    def rec(start, left):
        if len(res) >= cap:
            return
        if left == 0:
            if degM[0] != 5 or degM[1] != 5:
                return
            if any(c < 2 for c in edge_cnt):
                return
            fms = [foot[a] for a in chosen]
            if matching_size(fms) != 24:
                return
            for k in range(25):
                sub = fms[:k] + fms[k+1:]
                if matching_size(sub) != 24:
                    return
            res.append(list(chosen))
            return
        if K - start < left:
            return
        if degM[0] > 5 or degM[1] > 5:
            return
        # multiplicity feasibility: remaining candidates must be able to lift each edge to 2
        for e in range(24):
            if edge_cnt[e] + sum(1 for i in range(start, K) if (foot[order[i]] >> e) & 1) < 2:
                return
        for i in range(start, K):
            if len(res) >= cap:
                return
            a = order[i]
            u, w = a
            if badadj[u] & badadj[w]:
                continue
            chosen.append(a)
            degM[u] += 1; degM[w] += 1
            badadj[u].add(w); badadj[w].add(u)
            for e in range(24):
                if (foot[a] >> e) & 1:
                    edge_cnt[e] += 1
            rec(i + 1, left - 1)
            chosen.pop()
            degM[u] -= 1; degM[w] -= 1
            badadj[u].discard(w); badadj[w].discard(u)
            for e in range(24):
                if (foot[a] >> e) & 1:
                    edge_cnt[e] -= 1

    # seed root
    u, w = root
    chosen.append(root); degM[u] += 1; degM[w] += 1
    badadj[u].add(w); badadj[w].add(u)
    for e in range(24):
        if (foot[root] >> e) & 1:
            edge_cnt[e] += 1
    rec(1, 24)
    return res

if __name__ == '__main__':
    import time
    for tag in ('298', '264'):
        fx = build(tag)
        t0 = time.time()
        subs = find_circuits_v3(fx, cap=1000)
        print(f"===== {tag}: valid circuits (cap 1000): {len(subs)} in {time.time()-t0:.1f}s =====")
        for si, s in enumerate(subs[:2]):
            print(f" subset#{si}: {sorted(s)}")
            census_subset(fx, sorted(s), f"-v3s{si}", max_states=120000, sample=20000)
