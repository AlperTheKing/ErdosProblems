"""Exact max-flow checker for the P5 support-Hall certificate.

The subset condition

    sum_{f in F'} c_f <= | union_{f in F'} supp(p_f) |

is equivalent to a fractional bipartite flow from bad edges to vertices:
each bad edge f has demand c_f, each graph vertex has capacity 1, and f
may send flow only to supp(p_f).  This script checks that condition by
an exact Fraction Edmonds-Karp max-flow, avoiding 2^|M| subset enumeration.
"""
from collections import deque
from fractions import Fraction as F
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from _test_fullg import build_K
from _satzmu_conn import struct_for_side


def support_hall_data(n, adj, side):
    """Return (o, demands, supports, K, T, M) for singleton overload cuts."""
    r = build_K(adj, side, n)
    if r is None:
        return None
    K, T = r
    O = [v for v in range(n) if T[v] > n]
    if len(O) != 1:
        return None
    o = O[0]
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, _T2, _mu, cyc = st

    psi = [F(0) for _ in range(n)]
    psi[o] = F(1)
    for q in range(n):
        if q == o:
            continue
        a = K[o][q]
        if a > 0:
            den = F(n) - 4 * a
            if den <= 0:
                raise ValueError(("nonpositive denominator", q, a, den))
            psi[q] = a / den

    demands = []
    supports = []
    for f in M:
        Ps = cyc[f]
        pf = [F(0) for _ in range(n)]
        supp = set()
        for P in Ps:
            for v in P:
                pf[v] += F(1, len(Ps))
                supp.add(v)
        x = pf[o]
        c = x * x + sum(
            psi[q] * (ell[f] - 4 * x) * pf[q] for q in range(n) if q != o
        )
        demands.append(c)
        supports.append(supp)
    return o, demands, supports, K, T, M


def exact_hall_flow(n, demands, supports, force_bad=None):
    """Return exact Hall slack and a min-cut bad-edge subset.

    The returned slack is maxflow - total_demand, i.e. the minimum Hall
    slack over all subsets.  It is nonnegative iff support-Hall holds.
    """
    m = len(demands)
    source = 0
    bad0 = 1
    vert0 = bad0 + m
    sink = vert0 + n
    N = sink + 1
    total = sum(demands, F(0))
    inf = total + F(n + 1)

    cap = [[F(0) for _ in range(N)] for _ in range(N)]
    for i, d in enumerate(demands):
        cap[source][bad0 + i] = inf if i == force_bad else d
        for v in supports[i]:
            cap[bad0 + i][vert0 + v] = inf
    for v in range(n):
        cap[vert0 + v][sink] = F(1)

    flow = F(0)
    while True:
        parent = [-1] * N
        parent[source] = source
        q = deque([source])
        while q and parent[sink] < 0:
            u = q.popleft()
            for v in range(N):
                if parent[v] < 0 and cap[u][v] > 0:
                    parent[v] = u
                    q.append(v)
                    if v == sink:
                        break
        if parent[sink] < 0:
            break
        aug = None
        v = sink
        while v != source:
            u = parent[v]
            aug = cap[u][v] if aug is None else min(aug, cap[u][v])
            v = u
        v = sink
        while v != source:
            u = parent[v]
            cap[u][v] -= aug
            cap[v][u] += aug
            v = u
        flow += aug

    seen = {source}
    q = deque([source])
    while q:
        u = q.popleft()
        for v in range(N):
            if v not in seen and cap[u][v] > 0:
                seen.add(v)
                q.append(v)
    cut_bad = [i for i in range(m) if bad0 + i in seen]
    cut_vertices = sorted({v for i in cut_bad for v in supports[i]})
    slack = flow - total
    if cut_bad:
        direct_slack = F(len(cut_vertices)) - sum((demands[i] for i in cut_bad), F(0))
        if direct_slack != slack:
            raise AssertionError((slack, direct_slack, cut_bad))
    return slack, cut_bad, cut_vertices, flow, total


def exact_nonempty_hall_slack(n, demands, supports):
    """Return the minimum Hall slack over nonempty bad-edge subsets."""
    best = None
    for i in range(len(demands)):
        rec = exact_hall_flow(n, demands, supports, force_bad=i)
        if best is None or rec[0] < best[0]:
            best = rec
    return best


def c5_blowup(sizes):
    """Build a complete C5 blow-up and the cut omitting edge V4--V0."""
    offsets = []
    n = 0
    for s in sizes:
        offsets.append(n)
        n += s
    adj = [set() for _ in range(n)]
    for i in range(5):
        j = (i + 1) % 5
        for a in range(sizes[i]):
            for b in range(sizes[j]):
                u = offsets[i] + a
                v = offsets[j] + b
                adj[u].add(v)
                adj[v].add(u)
    side_parts = [0, 1, 0, 1, 0]
    side = []
    for i, s in enumerate(sizes):
        side.extend([side_parts[i]] * s)
    return n, adj, side


def check_c5(sizes):
    n, adj, side = c5_blowup(sizes)
    data = support_hall_data(n, adj, side)
    if data is None:
        return None
    o, demands, supports, _K, T, M = data
    slack, cut_bad, cut_vertices, flow, total = exact_hall_flow(n, demands, supports)
    return {
        "sizes": sizes,
        "n": n,
        "o": o,
        "bad_edges": len(M),
        "T_o": T[o],
        "slack": slack,
        "cut_bad_size": len(cut_bad),
        "cut_vertices_size": len(cut_vertices),
        "flow": flow,
        "total": total,
    }


def main():
    tests = [
        [1, 48, 6, 8, 48],
        [1, 4, 2, 2, 4],
        [1, 8, 4, 2, 8],
        [1, 20, 10, 2, 20],
        [1, 30, 15, 2, 30],
        [1, 64, 16, 7, 64],
    ]
    for sizes in tests:
        r = check_c5(sizes)
        print(r)


if __name__ == "__main__":
    main()
