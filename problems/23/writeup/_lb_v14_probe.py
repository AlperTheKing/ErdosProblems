"""Exhaustive probe of v=14 at the (LB) break-candidate site:
   H?AFBo] t=2 blowup, side=101111111111000000, R[14]=-8, Gamma0=296 (non-gamma-min; min=200).
The |S|<=6 brute found NO neutral Gamma-drop switch through v=14.  Push harder:
  (P1) raise |S| to 8 (full enumeration C(17,k), k<=7) for a neutral B-conn Gamma-DROP switch THROUGH v=14;
  (P2) BFS-connected-flip search: only connected vertex subsets containing v=14 (in the original graph), |S|<=10,
       neutral + B-conn-after + Gamma-drop;
  (P3) does ANY neutral B-conn Gamma-drop switch through v=14 exist that uses the v=2 witness extended?
  (P4) report the structure: which vertices are 'symmetric' to v=14, and whether the GRAPH-WIDE descent
       (some neutral Gamma-drop switch, not nec. through v=14) holds (it does: drop 96 at S={0,2,12,13}).
Exact Fraction.  Run: python _lb_v14_probe.py
"""
import itertools
from collections import deque
from fractions import Fraction as F
from _h import dec, Bconn
from _satzmu_conn import struct_for_side
from _csmspec import build_K2


def vertex_blowup(n, E, t):
    EE = []
    for (u, v) in E:
        for a in range(t):
            for b in range(t):
                EE.append((u * t + a, v * t + b))
    return n * t, EE


def gamma_of(n, adj, side):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return F(0)
    M, ell = st[0], st[1]
    return sum(ell[f] * ell[f] for f in M)


def boundary_delta(n, adj, side, Sset):
    dB = dM = 0
    for u in Sset:
        for w in adj[u]:
            if w in Sset:
                continue
            if side[u] != side[w]:
                dB += 1
            else:
                dM += 1
    return dB - dM


def flip(side, Sset):
    s = side[:]
    for u in Sset:
        s[u] ^= 1
    return s


def main():
    hN, hE = dec("H?AFBo]")
    n, E = vertex_blowup(hN, hE, 2)
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    side = [int(c) for c in "101111111111000000"]
    st = struct_for_side(n, adj, side)
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    gamma0 = sum(ell[f] ** 2 for f in M)
    v = 14
    print("site: N=%d Gamma0=%d v=%d  (min Gamma over graph = 200)" % (n, gamma0, v))

    # (P1) full enumeration up to |S|=8 (k<=7 others)
    others = [u for u in range(n) if u != v]
    found = None
    for k in range(0, 8):
        cnt = 0
        for combo in itertools.combinations(others, k):
            Sset = (v,) + combo
            if boundary_delta(n, adj, side, Sset) != 0:
                continue
            s2 = flip(side, Sset)
            if not Bconn(n, adj, s2):
                continue
            g2 = gamma_of(n, adj, s2)
            if g2 is not None and g2 < gamma0:
                found = (sorted(Sset), int(gamma0 - g2)); break
            cnt += 1
        print("  |S|=%d : neutral B-conn switches scanned, drop-switch=%s" % (k + 1, found))
        if found:
            break
    print("(P1) full |S|<=8 through v=14: %s" % (str(found) if found else "NONE"))

    # (P2) connected-subset BFS flip search (subset connected in original graph, contains v), |S|<=10
    def connected_subsets_containing(v, maxsize):
        # grow connected subsets via BFS frontier; yield each once
        seen = set()
        start = frozenset([v])
        stack = [start]
        seen.add(start)
        while stack:
            S = stack.pop()
            yield S
            if len(S) >= maxsize:
                continue
            frontier = set()
            for u in S:
                frontier |= adj[u]
            frontier -= S
            for w in frontier:
                S2 = S | {w}
                if S2 not in seen:
                    seen.add(S2)
                    stack.append(S2)

    found2 = None; scanned = 0
    for S in connected_subsets_containing(v, 10):
        if len(S) in (0, n):
            continue
        if boundary_delta(n, adj, side, S) != 0:
            continue
        s2 = flip(side, S)
        if not Bconn(n, adj, s2):
            continue
        scanned += 1
        g2 = gamma_of(n, adj, s2)
        if g2 is not None and g2 < gamma0:
            found2 = (sorted(S), int(gamma0 - g2)); break
    print("(P2) connected-subset(orig graph) flip through v=14, |S|<=10: scanned %d neutral; drop=%s"
          % (scanned, found2 if found2 else "NONE"))

    # (P3) graph-wide descent (some neutral Gamma-drop switch, not nec through v=14) -- known S={0,2,12,13}
    Sw = [0, 2, 12, 13]
    g2 = gamma_of(n, adj, flip(side, Sw))
    print("(P3) graph-wide neutral switch S={0,2,12,13}: neutral=%s drop=%s"
          % (boundary_delta(n, adj, side, Sw) == 0, (gamma0 - g2) if g2 is not None else None))

    # (P4) is v=14 EVEN required to host a switch?  Test: does a neutral Gamma-drop switch through v=14
    #      exist using larger sets that DO move v=14 plus a known descending block?
    #      try S = {0,2,12,13} + {14, partner} variants (extend the working witness to cover 14)
    print("(P4) extend working witness to cover v=14:")
    base = {0, 2, 12, 13}
    for extra in itertools.chain.from_iterable(itertools.combinations([14, 15, 1, 3, 8, 9, 10, 11], r) for r in range(1, 5)):
        if 14 not in set(extra):
            continue
        S = frozenset(base | set(extra))
        if boundary_delta(n, adj, side, S) != 0:
            continue
        s2 = flip(side, S)
        if not Bconn(n, adj, s2):
            continue
        g2 = gamma_of(n, adj, s2)
        if g2 is not None and g2 < gamma0:
            print("     S=%s drop=%d (covers v=14)" % (sorted(S), int(gamma0 - g2)))
            break
    else:
        print("     no extension of {0,2,12,13} covering v=14 with a Gamma drop found")

    print("=" * 60)
    if found or found2:
        w = found or found2
        print("CONCLUSION: a neutral B-conn Gamma-DROP switch THROUGH v=14 EXISTS: S=%s drop=%s. "
              "(LB)-spirit holds at v=14; length-bundle + |S|<=6 selectors were just too narrow." % (w[0], w[1]))
    else:
        print("CONCLUSION: NO neutral B-conn Gamma-DROP switch THROUGH v=14 (|S|<=8 full, |S|<=10 connected). "
              "v=14 has R<0 yet hosts no per-vertex descent witness -> the PER-VERTEX (through-v) form of (LB) is "
              "FALSE here, EVEN THOUGH the graph-wide descent (drop 96 elsewhere) holds and the cut is NON-gamma-min.")


if __name__ == "__main__":
    main()
