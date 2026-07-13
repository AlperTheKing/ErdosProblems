#!/usr/bin/env python3
"""Constraint-variant probe for #264 circuit reconstruction."""
import sys
from collections import defaultdict
sys.path.insert(0, '.')
from fixture_atoms_exact import build
from fixture_atoms_v3 import matching_size

def find(fx, owners_excl, cap=50, need_mult2=True, owner_deg=5):
    cand = fx['cand']
    edges = sorted(tuple(sorted(e)) for e in fx['edges'])
    eidx = {e: i for i, e in enumerate(edges)}
    usable = []
    for a in cand:
        excl = False
        for owner in owners_excl:
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
    root = (2, 3)
    if root not in foot:
        return [], len(usable)
    order = sorted(usable, key=lambda a: (a != root,))
    K = len(order)
    res = []
    chosen = []
    degM = defaultdict(int)
    badadj = defaultdict(set)
    edge_cnt = [0] * 24

    def rec(start, left):
        if len(res) >= cap:
            return
        if left == 0:
            if degM[0] != owner_deg or degM[1] != owner_deg:
                return
            if need_mult2 and any(c < 2 for c in edge_cnt):
                return
            if not need_mult2 and any(c < 1 for c in edge_cnt):
                return
            fms = [foot[a] for a in chosen]
            if matching_size(fms) != 24:
                return
            for k in range(25):
                if matching_size(fms[:k] + fms[k+1:]) != 24:
                    return
            res.append(list(chosen))
            return
        if K - start < left:
            return
        if degM[0] > owner_deg or degM[1] > owner_deg:
            return
        thresh = 2 if need_mult2 else 1
        for e in range(24):
            if edge_cnt[e] + sum(1 for i in range(start, K) if (foot[order[i]] >> e) & 1) < thresh:
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

    u, w = root
    chosen.append(root); degM[u] += 1; degM[w] += 1
    badadj[u].add(w); badadj[w].add(u)
    for e in range(24):
        if (foot[root] >> e) & 1:
            edge_cnt[e] += 1
    rec(1, 24)
    return res, len(usable)

fx = build('264')
for label, owners, mult2 in [
    ("excl {0,1} mult2", (0, 1), True),
    ("excl {0} mult2", (0,), True),
    ("excl {} mult2", (), True),
    ("excl {} mult1", (), False),
]:
    res, nus = find(fx, owners, cap=20, need_mult2=mult2)
    print(f"{label}: usable={nus} circuits={len(res)}")
    if res:
        print("  first:", sorted(res[0]))
