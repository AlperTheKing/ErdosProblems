#!/usr/bin/env python3
"""AGENT farkas_dual — Script D: reconstruct the engine's 25-atom selections for the two
t=5 hits by exhaustive filtering, then redo the switch-dual measurements EXACTLY.

Selection constraints (all from the published circuit axioms):
  (a) 25 atoms chosen from the available same-shore distance-4 pairs (32 for #298, 30 for #264);
  (b) atom graph triangle-free (all 3-bad triangles killed by the drops);
  (c) union of complete shortest-row supports of the kept atoms = all 24 blue edges;
  (d) transversal circuit: max SDR = 24 (deficiency exactly 1) AND every 1-atom deletion
      admits a full 24-SDR;
  (e) the profile owner keeps all 5 of its bad atoms (r=5 zero-vector profile exists).
For every surviving selection: kappa sweep (max, argmax) + singleSafe count + worst gap.
If several selections survive, report the RANGE across them (dual-shape robustness).
All integer arithmetic; ASCII only.
"""
from itertools import combinations
from collections import deque
import sys

def g6_decode(s):
    data = [ord(c) - 63 for c in s]
    n = data[0]
    bits = []
    for v in data[1:]:
        for k in range(5, -1, -1):
            bits.append((v >> k) & 1)
    edges = set()
    t = 0
    for j in range(1, n):
        for i in range(j):
            if bits[t]:
                edges.add(frozenset((i, j)))
            t += 1
    return n, edges

def build(g6):
    n, blue = g6_decode(g6)
    bluadj = [set() for _ in range(n)]
    for e in blue:
        u, w = tuple(e)
        bluadj[u].add(w)
        bluadj[w].add(u)
    color = [None] * n
    color[0] = 0
    dq = deque([0])
    while dq:
        u = dq.popleft()
        for w in bluadj[u]:
            if color[w] is None:
                color[w] = 1 - color[u]
                dq.append(w)
    def bfs(src):
        d = [None] * n
        d[src] = 0
        dq2 = deque([src])
        while dq2:
            u = dq2.popleft()
            for w in bluadj[u]:
                if d[w] is None:
                    d[w] = d[u] + 1
                    dq2.append(w)
        return d
    dist = [bfs(u) for u in range(n)]
    avail = set()
    for u, w in combinations(range(n), 2):
        if color[u] == color[w] and dist[u][w] == 4:
            avail.add(frozenset((u, w)))
    return n, blue, bluadj, color, dist, sorted(avail, key=sorted)

def rows_and_support(bluadj, at):
    s, t = sorted(at)
    out = []
    def dfs(path):
        if len(path) == 5:
            if path[-1] == t:
                out.append(tuple(path))
            return
        for w2 in bluadj[path[-1]]:
            if w2 not in path:
                if len(path) == 4 and w2 != t:
                    continue
                dfs(path + [w2])
    dfs([s])
    sup = {frozenset((r[i], r[i + 1])) for r in out for i in range(4)}
    return out, sup

def max_sdr(kept, F, universe_edges, forbidden=None):
    use = [at for at in kept if at != forbidden]
    eid = {e: i for i, e in enumerate(universe_edges)}
    match = {}
    def aug(ai, vis):
        for e in F[use[ai]]:
            i = eid[e]
            if i in vis:
                continue
            vis.add(i)
            if i not in match or aug(match[i], vis):
                match[i] = ai
                return True
        return False
    c = 0
    for ai in range(len(use)):
        if aug(ai, set()):
            c += 1
    return c

def process(tag, g6, owner, drops_k):
    print("=" * 70)
    n, blue, bluadj, color, dist, avail = build(g6)
    print("%s: available atoms %d, need to drop %d" % (tag, len(avail), drops_k))
    F = {}
    for at in avail:
        _, sup = rows_and_support(bluadj, at)
        F[at] = sup
    aset = set(avail)
    # triangles among available bads
    tris = []
    for A, Bb, C in combinations(range(n), 3):
        if (frozenset((A, Bb)) in aset and frozenset((A, C)) in aset
                and frozenset((Bb, C)) in aset):
            tris.append((frozenset((A, Bb)), frozenset((A, C)), frozenset((Bb, C))))
    print("  3-bad triangles among available atoms: %d" % len(tris))
    owner_bads = [at for at in avail if owner in at]
    print("  owner %d bad atoms: %d (must all be kept)" % (owner, len(owner_bads)))
    droppable = [at for at in avail if owner not in at]
    universe = sorted(blue, key=sorted)
    survivors = []
    tried = 0
    for D in combinations(droppable, drops_k):
        tried += 1
        Ds = set(D)
        ok = True
        for t3 in tris:
            if not (t3[0] in Ds or t3[1] in Ds or t3[2] in Ds):
                ok = False
                break
        if not ok:
            continue
        kept = [at for at in avail if at not in Ds]
        un = set()
        for at in kept:
            un |= F[at]
        if len(un) != 24:
            continue
        if max_sdr(kept, F, universe) != 24:
            continue
        good = all(max_sdr(kept, F, universe, forbidden=at) == 24 for at in kept)
        if not good:
            continue
        survivors.append(kept)
        if len(survivors) >= 2000:
            print("  ... capping survivor enumeration at 2000")
            break
    print("  drop-sets tried: %d ; surviving selections: %d" % (tried, len(survivors)))
    if not survivors:
        return 0
    measured = survivors[:12]
    if len(survivors) > 12:
        print("  measuring the first 12 selections (dual-shape range)")
    survivors = measured
    # dual measurements across survivors
    blue_edges = [tuple(sorted(e)) for e in blue]
    Lset = {u for u in range(n) if color[u] == 0}
    res = []
    for kept in survivors:
        bad_edges = [tuple(sorted(e)) for e in kept]
        badj = [set() for _ in range(n)]
        for e in kept:
            u, w = tuple(e)
            badj[u].add(w)
            badj[w].add(u)
        Gadj = [bluadj[u] | badj[u] for u in range(n)]
        maxk = -10**9
        for mask in range(1 << n):
            kb = 0
            for u, w in bad_edges:
                kb += ((mask >> u) ^ (mask >> w)) & 1
            ks = 0
            for u, w in blue_edges:
                ks += ((mask >> u) ^ (mask >> w)) & 1
            if kb - ks > maxk:
                maxk = kb - ks
        # singleSafe
        cnt = 0
        for u in sorted(Lset):
            for w in sorted(set(range(n)) - Lset):
                e = frozenset((u, w))
                if e in blue:
                    continue
                if Gadj[u] & Gadj[w]:
                    continue
                safe = True
                for at in kept:
                    s, t = tuple(at)
                    b1 = dist[s][u] + 1 + dist[w][t]
                    b2 = dist[s][w] + 1 + dist[u][t]
                    if min(b1, b2) <= 4:
                        safe = False
                        break
                if safe:
                    cnt += 1
        res.append((maxk, cnt))
    ks = sorted(set(r[0] for r in res))
    cs = sorted(set(r[1] for r in res))
    print("  ACROSS measured selections: max-kappa values %s ; singleSafe counts %s"
          % (ks, cs))
    return len(res)

if __name__ == "__main__":
    # #298: owner 0 (active component {0,17}, r(0)=5)
    if not process("hit298", "Q??????wE_[?EGs?D_@A?C_B???", owner=0, drops_k=7):
        process("hit298", "Q??????wE_[?EGs?D_@A?C_B???", owner=1, drops_k=7)
    # #264: owner adjacency to live x=9 uncertain — try 0 then 1
    if not process("hit264", "Q??????wE_Bws?s?DCD??@?@???", owner=0, drops_k=5):
        process("hit264", "Q??????wE_Bws?s?DCD??@?@???", owner=1, drops_k=5)
    print("DONE reconstruct")
