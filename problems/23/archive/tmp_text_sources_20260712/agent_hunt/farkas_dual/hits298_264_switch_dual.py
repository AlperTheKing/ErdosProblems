#!/usr/bin/env python3
"""AGENT farkas_dual — Script C: exact switch-demand duals on the two REAL t=5 zero-vector
engine hits (#298 from R49, #264 from R50), decoded from their archived graph6 strings.

Cross-checks against engine-published numbers:
  #298: displayed cut fails maxcut with min switch sigma -20  => my max kappa should be 20.
  #264: switch S = {4,5,6,7,8,11,14,16}: badCross 23, fixedBlue 2 => kappa 21.

Then the same dual measurements as the near-candidate:
  - shores = unique 2-coloring of the connected bipartite blue graph;
  - atoms = same-shore blue-distance-4 pairs (report count; 25 = forced choice);
  - triangle count of blue+atoms (both hits are triangle-free per engine);
  - kappa sweep over all 2^18 switches: max, argmax, positive count;
  - kappa at the owner b-cluster (bad neighbours of the profile owner);
  - singleSafe intrinsic candidates + worst Farkas gap (kappa - capRelaxed).
All integer arithmetic; ASCII only.
"""
from itertools import combinations
from collections import deque

def g6_decode(s):
    data = [ord(c) - 63 for c in s]
    n = data[0]
    assert 0 <= n <= 62
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

FIXTURES = {
    "hit298": "Q??????wE_[?EGs?D_@A?C_B???",
    "hit264": "Q??????wE_Bws?s?DCD??@?@???",
}

def analyze(tag, g6, check_S=None, check_bad=None, check_blue=None, expect_maxk=None):
    print("=" * 70)
    n, blue = g6_decode(g6)
    print("%s: n=%d, blue support edges=%d" % (tag, n, len(blue)))
    assert n == 18
    bluadj = [set() for _ in range(n)]
    for e in blue:
        u, w = tuple(e)
        bluadj[u].add(w)
        bluadj[w].add(u)
    # connected + bipartite 2-coloring
    color = [None] * n
    color[0] = 0
    dq = deque([0])
    while dq:
        u = dq.popleft()
        for w in bluadj[u]:
            if color[w] is None:
                color[w] = 1 - color[u]
                dq.append(w)
            else:
                assert color[w] != color[u], "blue graph not bipartite"
    assert all(c is not None for c in color), "blue graph disconnected"
    Lset = {u for u in range(n) if color[u] == 0}
    print("  shores: %s | %s" % (sorted(Lset), sorted(set(range(n)) - Lset)))

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
    atoms = set()
    for u, w in combinations(range(n), 2):
        if (color[u] == color[w]) and dist[u][w] == 4:
            atoms.add(frozenset((u, w)))
    print("  same-shore blue-distance-4 pairs (available atoms): %d %s"
          % (len(atoms), "(FORCED = the 25 selected)" if len(atoms) == 25 else "(CHOICE!)"))
    badj = [set() for _ in range(n)]
    for e in atoms:
        u, w = tuple(e)
        badj[u].add(w)
        badj[w].add(u)
    # triangle count in blue+atoms
    Gadj = [bluadj[u] | badj[u] for u in range(n)]
    tri = sum(1 for u, w, z in combinations(range(n), 3)
              if w in Gadj[u] and z in Gadj[u] and z in Gadj[w])
    print("  triangles in blue+atoms: %d" % tri)
    # profile owner scan: blue degree 5 and bad degree 5
    owners = [u for u in range(n) if len(bluadj[u]) == 5 and len(badj[u]) == 5]
    print("  candidate profile owners (dB=dM=5): %s" % owners)

    bad_edges = [tuple(sorted(e)) for e in atoms]
    blue_edges = [tuple(sorted(e)) for e in blue]
    # engine cross-check
    if check_S is not None:
        mask = 0
        for u in check_S:
            mask |= 1 << u
        kb = sum(((mask >> u) ^ (mask >> w)) & 1 for u, w in bad_edges)
        ks = sum(((mask >> u) ^ (mask >> w)) & 1 for u, w in blue_edges)
        print("  ENGINE CHECK at S=%s: badCross=%d (expect %s), fixedBlue=%d (expect %s), kappa=%d"
              % (sorted(check_S), kb, check_bad, ks, check_blue, kb - ks))
        assert (check_bad is None or kb == check_bad) and (check_blue is None or ks == check_blue)
    # kappa sweep
    maxk = -10**9
    argmax = None
    pos = 0
    for mask in range(1 << n):
        kb = 0
        for u, w in bad_edges:
            kb += ((mask >> u) ^ (mask >> w)) & 1
        ks = 0
        for u, w in blue_edges:
            ks += ((mask >> u) ^ (mask >> w)) & 1
        k = kb - ks
        if k > maxk:
            maxk, argmax = k, mask
        if k > 0:
            pos += 1
    amset = sorted(u for u in range(n) if (argmax >> u) & 1)
    print("  max kappa = %d at S = %s ; positive-demand switches = %d" % (maxk, amset, pos))
    if expect_maxk is not None:
        print("  ENGINE CHECK max kappa: %d (expect %d) %s"
              % (maxk, expect_maxk, "PASS" if maxk == expect_maxk else "MISMATCH"))
    # owner b-cluster demands
    for v in owners:
        S = badj[v]
        mask = 0
        for u in S:
            mask |= 1 << u
        kb = sum(((mask >> u) ^ (mask >> w)) & 1 for u, w in bad_edges)
        ks = sum(((mask >> u) ^ (mask >> w)) & 1 for u, w in blue_edges)
        mask2 = mask | (1 << v)
        kb2 = sum(((mask2 >> u) ^ (mask2 >> w)) & 1 for u, w in bad_edges)
        ks2 = sum(((mask2 >> u) ^ (mask2 >> w)) & 1 for u, w in blue_edges)
        print("  owner %d: kappa(badNbrs)=%d ; kappa(badNbrs+owner)=%d"
              % (v, kb - ks, kb2 - ks2))
    # singleSafe intrinsic candidates
    cands = []
    for u in sorted(Lset):
        for w in sorted(set(range(n)) - Lset):
            e = frozenset((u, w))
            if e in blue:
                continue
            if Gadj[u] & Gadj[w]:
                continue
            ok = True
            for at in atoms:
                s, t = tuple(at)
                du = dist[s][u]; dw = dist[w][t]; du2 = dist[s][w]; dw2 = dist[u][t]
                b1 = (du + 1 + dw) if (du is not None and dw is not None) else 99
                b2 = (du2 + 1 + dw2) if (du2 is not None and dw2 is not None) else 99
                if min(b1, b2) <= 4:
                    ok = False
                    break
            if ok:
                cands.append(e)
    tot_pairs = len(Lset) * (n - len(Lset)) - len(blue)
    print("  singleSafe intrinsic candidates: %d of %d non-blue cross pairs" % (len(cands), tot_pairs))
    worst = -10**9
    worst_mask = None
    for mask in range(1 << n):
        kb = 0
        for u, w in bad_edges:
            kb += ((mask >> u) ^ (mask >> w)) & 1
        if kb == 0:
            continue
        ks = 0
        for u, w in blue_edges:
            ks += ((mask >> u) ^ (mask >> w)) & 1
        k = kb - ks
        if k <= 0:
            continue
        cap = sum(1 for e in cands for u, w in [tuple(e)] if ((mask >> u) ^ (mask >> w)) & 1)
        if k - cap > worst:
            worst, worst_mask = k - cap, mask
    print("  worst intrinsic Farkas gap (kappa - capRelaxed) = %d at S = %s"
          % (worst, sorted(u for u in range(n) if (worst_mask >> u) & 1)))
    return maxk, worst

analyze("hit298", FIXTURES["hit298"], expect_maxk=20)
analyze("hit264", FIXTURES["hit264"], check_S={4, 5, 6, 7, 8, 11, 14, 16},
         check_bad=23, check_blue=2)
print("DONE hits")
