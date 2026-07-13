#!/usr/bin/env python3
"""AGENT-HOMOLOGY Check 2b: derive the exact 25-atom subsets for #298/#264 and re-run
the liveness census on valid circuits.

Valid subset conditions (rooted t=5 circuit):
  C1 exactly 25 atoms chosen among the same-shore d4 pairs;
  C2 owners 0 and 1 have bad degree exactly 5;
  C3 chosen bad graph triangle-free (bad-bad-bad; other triangle types impossible);
  C4 union of chosen atoms' complete row families = all 24 support edges;
  C5 inclusion-minimality: for every support edge e some chosen atom has ALL its rows using e;
  C6 the rooted atom (2,3) is chosen with both prescribed rows.
Then for each valid subset (up to a cap): exhaustive-or-sampled transition census with layers
L0/L1/L2/L3 and full-profile flags; rotor-core presence within the chosen atom set.
"""
import sys
from itertools import combinations, product
from collections import defaultdict
sys.path.insert(0, '.')
from fixture_state_graph import g6_decode, bipartition, all_4paths, FIX, T, state_data, detours, classify

import collections

def build(tag):
    n, edges = g6_decode(FIX[tag])
    color, adj = bipartition(n, edges)
    shore = lambda u: color.get(u, 0)
    def bfs(u):
        d = {u: 0}
        q = collections.deque([u])
        while q:
            a = q.popleft()
            for b in adj[a]:
                if b not in d:
                    d[b] = d[a] + 1
                    q.append(b)
        return d
    dist = {u: bfs(u) for u in range(n)}
    cand = []
    for u, w in combinations(range(n), 2):
        if shore(u) == shore(w) and dist[u].get(w) == 4:
            cand.append((u, w))
    rows = {a: all_4paths(adj, a[0], a[1]) for a in cand}
    # per-atom edge sets and critical-edge sets (edges used by EVERY row of the atom)
    edge_union = {}
    edge_forced = {}
    for a in cand:
        uni = set(); forced = None
        for r in rows[a]:
            es = {frozenset((r[i], r[i+1])) for i in range(4)}
            uni |= es
            forced = es if forced is None else (forced & es)
        edge_union[a] = uni
        edge_forced[a] = forced
    return dict(tag=tag, n=n, edges=edges, adj=adj, color=color, cand=cand, rows=rows,
                edge_union=edge_union, edge_forced=edge_forced)

def valid_subsets(fx, cap=200000):
    cand = fx['cand']; edges = fx['edges']
    idx = {a: i for i, a in enumerate(cand)}
    K = len(cand)
    need = 25
    # precompute adjacency for triangle checks among candidate atoms
    out = []
    root = (2, 3)
    assert root in idx, "rooted atom missing"
    # DFS over combinations with pruning
    cnt = [0]
    chosen = []
    degM = defaultdict(int)
    badadj = defaultdict(set)

    def tri_ok(a):
        u, w = a
        return not (badadj[u] & badadj[w])

    def rec(start, left):
        if cnt[0] >= cap:
            return
        if left == 0:
            # C2 owners degree exactly 5
            if degM[0] != 5 or degM[1] != 5:
                return
            # C4 union covers all edges
            uni = set()
            for a in chosen:
                uni |= fx['edge_union'][a]
            if uni != edges:
                return
            # C5 minimality
            for e in edges:
                if not any(e in fx['edge_forced'][a] for a in chosen):
                    return
            out.append(list(chosen))
            cnt[0] += 1
            return
        if K - start < left:
            return
        # prune: owners cannot exceed 5
        if degM[0] > 5 or degM[1] > 5:
            return
        for i in range(start, K):
            a = cand[i]
            if not tri_ok(a):
                continue
            u, w = a
            chosen.append(a)
            degM[u] += 1; degM[w] += 1
            badadj[u].add(w); badadj[w].add(u)
            rec(i + 1, left - 1)
            chosen.pop()
            degM[u] -= 1; degM[w] -= 1
            badadj[u].discard(w); badadj[w].discard(u)
    # force root atom first for speed: iterate with root included
    a = root
    chosen.append(a); degM[2] += 1; degM[3] += 1
    badadj[2].add(3); badadj[3].add(2)
    rec(0, need - 1)
    # note: rec may re-add root; exclude duplicates
    res = []
    seen = set()
    for s in out:
        key = tuple(sorted(set(s)))
        if len(key) == 25 and key not in seen:
            seen.add(key)
            res.append(sorted(set(s)))
    return res

def census_subset(fx, atoms, label, max_states=250000, sample=40000):
    rows = {a: fx['rows'][a] for a in atoms}
    sub = dict(tag=fx['tag'] + label, edges=fx['edges'], adj=fx['adj'], color=fx['color'],
               atoms=atoms, rows=rows,
               bad={frozenset(a) for a in atoms},
               degB={u: len(fx['adj'][u]) for u in range(fx['n'])},
               degM=defaultdict(int), total=1, multi=[])
    for u, w in atoms:
        sub['degM'][u] += 1; sub['degM'][w] += 1
    tot = 1
    for a in atoms:
        tot *= len(rows[a])
    sub['total'] = tot
    counts = defaultdict(int)
    L1_examples = []
    if tot <= max_states:
        it = product(*[range(len(rows[a])) for a in atoms])
        mode = f'EXHAUSTIVE {tot}'
    else:
        import random
        random.seed(17)
        it = (tuple(random.randrange(len(rows[a])) for a in atoms) for _ in range(sample))
        mode = f'SAMPLED {sample} of {tot}'
    nst = 0
    for omega in it:
        nst += 1
        dts, st = classify(sub, omega)
        for d in dts:
            counts['L0'] += 1
            for k in ('l1', 'l2', 'l3'):
                if d[k]:
                    counts[k.upper()] += 1
            if d['okdeg'] and d['onelat'] and d['rt'] and d['cov']:
                counts['P_full_profile'] += 1
                if d['l1']:
                    counts['P_full_profile_active'] += 1
            if d['l1'] and len(L1_examples) < 5:
                L1_examples.append((omega, d))
    print(f"  [{sub['tag']}] census ({mode}): {dict(counts)}")
    if L1_examples:
        for om, d in L1_examples[:2]:
            print(f"    L1 example: atom {atoms[d['atom']]} enter {d['vnew']} expel {d['vold']}")
    return counts

if __name__ == '__main__':
    for tag in ('298', '264'):
        fx = build(tag)
        print(f"\n===== fixture {tag}: {len(fx['cand'])} candidate atoms =====")
        subs = valid_subsets(fx, cap=50)
        print(f"valid 25-atom circuits found (cap 50): {len(subs)}")
        for si, s in enumerate(subs[:3]):
            # rotor-core presence within chosen atoms
            chosen = set(map(tuple, s))
            cores = []
            for (u, w) in combinations(range(fx['n']), 2):
                if fx['color'].get(u) != fx['color'].get(w) or w in fx['adj'][u]:
                    continue
                cn = sorted(fx['adj'][u] & fx['adj'][w])
                for c1, c2 in combinations(cn, 2):
                    sA = any(((a1, b1) if a1 < b1 else (b1, a1)) in chosen
                             and (a1, c1, u, c2, b1) in fx['rows'].get((a1, b1) if a1 < b1 else (b1, a1), [])
                             and (a1, c1, w, c2, b1) in fx['rows'].get((a1, b1) if a1 < b1 else (b1, a1), [])
                             for a1 in fx['adj'][c1] - {u, w} for b1 in fx['adj'][c2] - {u, w, a1})
                    sB = any(((p1, q1) if p1 < q1 else (q1, p1)) in chosen
                             and (p1, u, c1, w, q1) in fx['rows'].get((p1, q1) if p1 < q1 else (q1, p1), [])
                             and (p1, u, c2, w, q1) in fx['rows'].get((p1, q1) if p1 < q1 else (q1, p1), [])
                             for p1 in fx['adj'][u] - {c1, c2} for q1 in fx['adj'][w] - {c1, c2, p1})
                    if sA and sB:
                        cores.append((u, c1, w, c2))
            print(f" subset#{si}: atoms={s}")
            print(f"   full rotor cores inside chosen atoms: {cores}")
            census_subset(fx, s, f"-s{si}")
