#!/usr/bin/env python3
"""AGENT-HOMOLOGY Check 2c: exact 25-atom circuit reconstruction, v2.

Circuit = transversal-matroid circuit: ground set = 24 support edges; atom a's set =
union of its rows' edges; the 25-family has NO SDR (forced: 25 > 24) and EVERY
24-subfamily (delete one atom) HAS an SDR (deletion-SDRs).  Plus: chosen union = all 24
edges; chosen bad graph triangle-free; owners 0,1 have bad degree exactly 5; rooted atom
(2,3) chosen.  Then census the valid circuits.
"""
import sys
from itertools import combinations, product
from collections import defaultdict
sys.path.insert(0, '.')
from fixture_atoms_exact import build, census_subset

def hopcroft_karp(sets, universe):
    # simple augmenting-path matching: sets = list of iterables of hashable elems
    matchL = {}
    matchR = {}
    def try_aug(i, seen):
        for e in sets[i]:
            if e in seen:
                continue
            seen.add(e)
            if e not in matchR or try_aug(matchR[e], seen):
                matchL[i] = e
                matchR[e] = i
                return True
        return False
    size = 0
    for i in range(len(sets)):
        if try_aug(i, set()):
            size += 1
    return size

def find_circuits(fx, cap=100):
    cand = fx['cand']
    edges = fx['edges']
    eu = fx['edge_union']
    root = (2, 3)
    # forced atoms: all candidate atoms at owners 0,1 IF owner candidate degree == 5
    dM = defaultdict(int)
    for u, w in cand:
        dM[u] += 1; dM[w] += 1
    res = []
    K = len(cand)
    chosen = []
    degM = defaultdict(int)
    badadj = defaultdict(set)
    cnt = [0]

    def full_checks():
        if degM[0] != 5 or degM[1] != 5:
            return
        uni = set()
        for a in chosen:
            uni |= eu[a]
        if uni != edges:
            return
        # defect: full family matching size must be 24 (defect exactly 1)
        sets = [tuple(eu[a]) for a in chosen]
        if hopcroft_karp(sets, edges) != 24:
            return
        # every deletion has an SDR (perfect matching of 24)
        for k in range(25):
            sub = sets[:k] + sets[k+1:]
            if hopcroft_karp(sub, edges) != 24:
                return
        res.append(list(chosen))
        cnt[0] += 1

    def rec(start, left):
        if cnt[0] >= cap:
            return
        if left == 0:
            full_checks()
            return
        if K - start < left:
            return
        if degM[0] > 5 or degM[1] > 5:
            return
        for i in range(start, K):
            if cnt[0] >= cap:
                return
            a = cand[i]
            u, w = a
            if a != root and (badadj[u] & badadj[w]):
                continue
            if badadj[u] & badadj[w]:
                continue
            chosen.append(a)
            degM[u] += 1; degM[w] += 1
            badadj[u].add(w); badadj[w].add(u)
            rec(i + 1, left - 1)
            chosen.pop()
            degM[u] -= 1; degM[w] -= 1
            badadj[u].discard(w); badadj[w].discard(u)

    # seed with the rooted atom
    u, w = root
    chosen.append(root); degM[u] += 1; degM[w] += 1
    badadj[u].add(w); badadj[w].add(u)
    rec(0, 24)
    uniq = []
    seen = set()
    for s in res:
        key = tuple(sorted(set(s)))
        if key not in seen and len(key) == 25:
            seen.add(key)
            uniq.append(sorted(set(s)))
    return uniq

if __name__ == '__main__':
    for tag in ('298', '264'):
        fx = build(tag)
        subs = find_circuits(fx, cap=20)
        print(f"\n===== {tag}: valid 25-atom transversal circuits (cap 20): {len(subs)} =====")
        for si, s in enumerate(subs[:2]):
            print(f" subset#{si}: {s}")
            census_subset(fx, s, f"-v2s{si}", max_states=120000, sample=25000)
