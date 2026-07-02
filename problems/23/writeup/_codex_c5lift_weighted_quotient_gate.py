"""Exact weighted quotient gate for C5-LIFT-PMS on small quotient seeds.

For a quotient graph (equality or sibling seed), a quotient side, and positive
integer class weights, compute for every length-5 shortest bad row Q:

    s_i = component/load contribution at the selected clone of q_i,
    tau = 5m/N,
    d(Q) = sum_i max(0, tau-s_i),
    lift_margin = N + (2/3)eta - (row_sum+d(Q)).

This is a gate for weighted C5-HOM branch stability.
"""

from __future__ import annotations

import argparse
import random
from collections import deque
from fractions import Fraction as F
from itertools import product

from _h import dec
from _codex_ocpms_sibling_embedding import EQ, SIB, norm


def edges_of(g6):
    n, E = dec(g6)
    return n, {norm(e) for e in E}


def side_tuple(side_string):
    return tuple(int(c) for c in side_string)


def b_edges(E, side):
    return {e for e in E if side[e[0]] != side[e[1]]}


def m_edges(E, side):
    return {e for e in E if side[e[0]] == side[e[1]]}


def bdist(n, B, src):
    adj = [set() for _ in range(n)]
    for a, b in B:
        adj[a].add(b)
        adj[b].add(a)
    d = [None] * n
    d[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if d[v] is None:
                d[v] = d[u] + 1
                q.append(v)
    return d


def shortest_paths(n, B, a, b):
    da = bdist(n, B, a)
    db = bdist(n, B, b)
    if da[b] is None:
        return []
    Lm1 = da[b]
    layers = [
        [v for v in range(n) if da[v] == i and db[v] == Lm1 - i]
        for i in range(Lm1 + 1)
    ]
    paths = []

    def rec(i, cur):
        if i == Lm1:
            paths.append(tuple(cur))
            return
        u = cur[-1]
        for v in layers[i + 1]:
            if norm((u, v)) in B:
                cur.append(v)
                rec(i + 1, cur)
                cur.pop()

    rec(0, [a])
    return paths


def path_weight(path, weights):
    out = 1
    for v in path[1:-1]:
        out *= weights[v]
    return out


def qcut_value(g6, side_string, weights):
    _n, E = edges_of(g6)
    side = side_tuple(side_string)
    return sum(weights[a] * weights[b] for a, b in E if side[a] != side[b])


def qmaxcut_value(g6, weights):
    n, E = edges_of(g6)
    best = -1
    for mask in range(1 << n):
        side = tuple((mask >> i) & 1 for i in range(n))
        val = sum(weights[a] * weights[b] for a, b in E if side[a] != side[b])
        if val > best:
            best = val
    return best


def all_rows(g6, side_string):
    n, E = edges_of(g6)
    side = side_tuple(side_string)
    B = b_edges(E, side)
    M = m_edges(E, side)
    out = []
    for e in sorted(M):
        paths = shortest_paths(n, B, e[0], e[1])
        for P in paths:
            out.append((e, P))
    return out


def row_loads(g6, side_string, row, weights):
    n, E = edges_of(g6)
    side = side_tuple(side_string)
    B = b_edges(E, side)
    M = m_edges(E, side)
    row = tuple(row)
    row_pos = {v: i for i, v in enumerate(row)}
    s = [F(0) for _ in row]
    for a, b in sorted(M):
        paths = shortest_paths(n, B, a, b)
        if not paths:
            raise RuntimeError((g6, side_string, "no B path", (a, b)))
        Z = sum(path_weight(p, weights) for p in paths)
        edge_mult = weights[a] * weights[b]
        # Endpoint selected clone probabilities over all clone bad edges.
        if a in row_pos:
            s[row_pos[a]] += weights[b]
        if b in row_pos:
            s[row_pos[b]] += weights[a]
        for p in paths:
            wp = path_weight(p, weights)
            for v in p[1:-1]:
                if v in row_pos:
                    # Probability selected clone in class v is on random path
                    # for random clone bad edge (a,b): edge_mult/Z * wp/weights[v].
                    s[row_pos[v]] += F(edge_mult * wp, Z * weights[v])
    return s


def c5lift_record(g6, side_string, row, weights):
    n, E = edges_of(g6)
    side = side_tuple(side_string)
    M = m_edges(E, side)
    N = sum(weights)
    m = sum(weights[a] * weights[b] for a, b in M)
    eta = F(N * N, 25) - m
    tau = F(5 * m, N)
    s = row_loads(g6, side_string, row, weights)
    row_sum = sum(s)
    d = sum(max(F(0), tau - x) for x in s)
    lift_margin = N + F(2, 3) * eta - row_sum - d
    c5rs_margin = N + eta - row_sum - d
    return dict(
        N=N,
        m=m,
        eta=eta,
        tau=tau,
        s=s,
        row_sum=row_sum,
        inactive_deficit=d,
        lift_margin=lift_margin,
        c5rs_margin=c5rs_margin,
        active=[i for i, x in enumerate(s) if x > tau],
    )


def sides_to_scan(g6):
    n, _E = edges_of(g6)
    # normalize by side[0]=0 to avoid complements.
    for mask in range(1 << (n - 1)):
        bits = [0] + [(mask >> (i - 1)) & 1 for i in range(1, n)]
        yield "".join(map(str, bits))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", choices=["eq", "sib"], default="sib")
    ap.add_argument("--mode", choices=["exhaustive", "random"], default="exhaustive")
    ap.add_argument("--max-weight", type=int, default=2)
    ap.add_argument("--samples", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=230701)
    ap.add_argument("--require-qmax", action="store_true")
    ap.add_argument("--require-over", action="store_true")
    ap.add_argument("--only-length5", action="store_true")
    args = ap.parse_args()

    g6 = EQ if args.graph == "eq" else SIB
    n, _E = edges_of(g6)
    qmax_cache = {}
    rows_cache = {}

    def qmax(weights0):
        key = tuple(weights0)
        if key not in qmax_cache:
            qmax_cache[key] = qmaxcut_value(g6, list(weights0))
        return qmax_cache[key]

    def rows(side):
        if side not in rows_cache:
            rows_cache[side] = all_rows(g6, side)
        return rows_cache[side]

    if args.mode == "exhaustive":
        weights_iter = product(range(1, args.max_weight + 1), repeat=n)
    else:
        rng = random.Random(args.seed)
        weights_iter = (
            tuple(rng.randint(1, args.max_weight) for _ in range(n))
            for _ in range(args.samples)
        )

    checked_weights = 0
    checked_rows = 0
    first_fail = None
    min_lift = None
    min_case = None
    for weights0 in weights_iter:
        weights = list(weights0)
        checked_weights += 1
        best = qmax(weights) if args.require_qmax else None
        for side in sides_to_scan(g6):
            if args.require_qmax and qcut_value(g6, side, weights) != best:
                continue
            for _f, row in rows(side):
                if args.only_length5 and len(row) != 5:
                    continue
                rec = c5lift_record(g6, side, row, weights)
                if args.require_over and rec["row_sum"] <= rec["N"]:
                    continue
                checked_rows += 1
                lm = rec["lift_margin"]
                if min_lift is None or lm < min_lift:
                    min_lift = lm
                    min_case = (weights, side, row, rec)
                if lm < 0:
                    first_fail = (weights, side, row, rec)
                    break
            if first_fail:
                break
        if first_fail:
            break

    print("graph", args.graph, g6)
    print("checked_weights", checked_weights)
    print("checked_rows", checked_rows)
    print("min_lift", min_lift)
    print("min_case", min_case)
    print("first_fail", first_fail)
    print("VERDICT", "PASS" if first_fail is None else "FAIL")


if __name__ == "__main__":
    main()
