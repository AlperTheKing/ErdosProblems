"""Weighted quotient formulas for the N=10 OC-PMS equality atom.

For a blow-up of the N=10 equality atom, this computes the row-overlap
quantity I(P) directly from the 10 quotient weights, without expanding all
clones.  It is intended to turn the observed weighted-stability phenomenon
into algebra.
"""

from fractions import Fraction as F
from collections import deque

from _codex_ocpms_petersen_blow import base_E, base_n, base_side, blow
from _satzmu_conn import struct_for_side

BASE_ROW = (7, 5, 8, 6, 9)
BASE_BAD = [(1, 9), (2, 7), (7, 9)]


def b_edges():
    return [e for e in base_E if base_side[e[0]] != base_side[e[1]]]


def m_edges():
    return [e for e in base_E if base_side[e[0]] == base_side[e[1]]]


def bdist(src):
    adj = [set() for _ in range(base_n)]
    for a, b in b_edges():
        adj[a].add(b)
        adj[b].add(a)
    d = [None] * base_n
    d[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if d[v] is None:
                d[v] = d[u] + 1
                q.append(v)
    return d


def base_shortest_paths(a, b):
    da = bdist(a)
    db = bdist(b)
    Lm1 = da[b]
    layers = [
        [v for v in range(base_n) if da[v] == i and db[v] == Lm1 - i]
        for i in range(Lm1 + 1)
    ]
    paths = []

    def rec(i, cur):
        if i == Lm1:
            paths.append(tuple(cur))
            return
        u = cur[-1]
        for v in layers[i + 1]:
            if (min(u, v), max(u, v)) in {tuple(sorted(e)) for e in b_edges()}:
                cur.append(v)
                rec(i + 1, cur)
                cur.pop()

    rec(0, [a])
    return paths


def path_weight(path, weights):
    out = 1
    # endpoints are fixed clones when evaluating a fixed clone bad edge, so
    # only internal quotient classes contribute multiplicity.
    for v in path[1:-1]:
        out *= weights[v]
    return out


def weighted_I_for_row(weights, row=BASE_ROW):
    """Return I(P) for a selected clone row of quotient classes `row`.

    This sums over every clone bad edge in the blow-up, using weighted
    shortest-path counts on the quotient.
    """
    row_set = set(row)
    total_I = F(0)
    for a, b in m_edges():
        paths = base_shortest_paths(a, b)
        Z = sum(path_weight(p, weights) for p in paths)
        if Z == 0:
            continue

        # Endpoint contribution over all clone bad edges: selected row clones
        # are only one clone in their class.
        endpoint_sum = 0
        if a in row_set:
            endpoint_sum += weights[b]
        if b in row_set:
            endpoint_sum += weights[a]

        internal_sum = F(0)
        for p in paths:
            wp = path_weight(p, weights)
            for pos_v in p[1:-1]:
                if pos_v in row_set:
                    # Among weights[pos_v] clones in this quotient class,
                    # exactly one is the selected row clone.
                    internal_sum += F(wp, weights[pos_v])

        total_I += endpoint_sum + F(weights[a] * weights[b], Z) * internal_sum
    return total_I


def explicit_I(weights, row_classes=BASE_ROW):
    n, E, side = blow(weights)
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    st = struct_for_side(n, adj, side)
    M, cyc = st[0], st[4]
    # choose the first clone in each row class
    off = []
    s = 0
    for w in weights:
        off.append(s)
        s += w
    row = tuple(off[c] for c in row_classes)
    Pset = set(row)
    return sum(
        F(1, len(cyc[g])) * sum(len(Pset & set(Q)) for Q in cyc[g])
        for g in M
    )


def qcut_value(weights, side):
    return sum(
        weights[a] * weights[b]
        for a, b in base_E
        if side[a] != side[b]
    )


def qmaxcut(weights):
    best = -1
    bestmask = None
    for mask in range(1 << base_n):
        side = [(mask >> i) & 1 for i in range(base_n)]
        val = qcut_value(weights, side)
        if val > best:
            best = val
            bestmask = mask
    return best, bestmask


def main():
    tests = [
        [1] * 10,
        [2] * 10,
        [3] * 10,
        [1, 1, 1, 1, 2, 2, 1, 1, 2, 1],
        [3, 3, 1, 2, 1, 3, 3, 1, 3, 1],
        [1, 2, 1, 1, 1, 1, 1, 1, 1, 1],
    ]
    for w in tests:
        wi = weighted_I_for_row(w)
        ei = explicit_I(w) if sum(w) <= 25 else None
        inherited = qcut_value(w, base_side)
        best, mask = qmaxcut(w)
        print(
            "w",
            w,
            "N",
            sum(w),
            "I_formula",
            wi,
            "I_explicit",
            ei,
            "over",
            wi - sum(w),
            "qmax",
            inherited == best,
            "gap",
            best - inherited,
        )


if __name__ == "__main__":
    main()

