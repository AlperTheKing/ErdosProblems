"""Exact weighted monotonicity gate for sibling PMS-5 supergraph rows.

For the 14 overloaded sibling rows that are equality-atom rows plus one extra
blue edge, test the blow-up analogue:

    I_eq(mapped row; pulled-back weights) >= I_sib(row; sibling weights).

This is a gate for the proposed proof subtarget, not a theorem.
"""

from __future__ import annotations

import argparse
import random
from collections import deque
from fractions import Fraction as F
from itertools import product

from _h import dec
from _codex_ocpms_sibling_embedding import (
    EQ,
    SIB,
    image_edges,
    image_path,
    norm,
    overloaded_rows,
    side_image,
    subgraph_embeddings,
)


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


def is_qmax(g6, side_string, weights):
    return qcut_value(g6, side_string, weights) == qmaxcut_value(g6, weights)


def weighted_I(g6, side_string, row, weights):
    n, E = edges_of(g6)
    assert len(weights) == n
    side = side_tuple(side_string)
    B = b_edges(E, side)
    M = m_edges(E, side)
    row_set = set(row)
    total = F(0)
    for a, b in sorted(M):
        paths = shortest_paths(n, B, a, b)
        if not paths:
            raise RuntimeError((g6, side_string, "no B path", (a, b)))
        Z = sum(path_weight(p, weights) for p in paths)
        if Z == 0:
            continue
        endpoint_sum = 0
        if a in row_set:
            endpoint_sum += weights[b]
        if b in row_set:
            endpoint_sum += weights[a]
        internal_sum = F(0)
        for p in paths:
            wp = path_weight(p, weights)
            for v in p[1:-1]:
                if v in row_set:
                    internal_sum += F(wp, weights[v])
        total += endpoint_sum + F(weights[a] * weights[b], Z) * internal_sum
    return total


def matched_pairs():
    eq_rows = overloaded_rows(EQ)
    sib_rows = overloaded_rows(SIB)
    embs = subgraph_embeddings(eq_rows[0]["E"], sib_rows[0]["E"])
    out = []
    for sr in sib_rows:
        for er in eq_rows:
            for mp in embs:
                if side_image(er["side"], mp) != sr["side"]:
                    continue
                mapped_p = image_path(er["P"], mp)
                if mapped_p != sr["P"] and tuple(reversed(mapped_p)) != sr["P"]:
                    continue
                if image_edges(er["M"], mp) != sr["M"]:
                    continue
                extra = sr["E"] - image_edges(er["E"], mp)
                if not extra or not extra <= sr["B"]:
                    continue
                out.append((er, sr, mp, extra))
                break
            else:
                continue
            break
    return out


def pullback_weights(weights_sib, mp):
    # mp maps equality vertex -> sibling vertex.
    return [weights_sib[mp[i]] for i in range(len(weights_sib))]


def check_weight(weights_sib, pairs):
    for er, sr, mp, extra in pairs:
        weights_eq = pullback_weights(weights_sib, mp)
        ieq = weighted_I(EQ, er["side"], er["P"], weights_eq)
        isib = weighted_I(SIB, sr["side"], sr["P"], weights_sib)
        if ieq < isib:
            return {
                "weights_sib": weights_sib,
                "eq_side": er["side"],
                "eq_P": er["P"],
                "sib_side": sr["side"],
                "sib_P": sr["P"],
                "extra": sorted(extra),
                "I_eq": ieq,
                "I_sib": isib,
                "gap": ieq - isib,
            }
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-weight", type=int, default=3)
    ap.add_argument("--mode", choices=["exhaustive", "random"], default="exhaustive")
    ap.add_argument("--samples", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=230701)
    ap.add_argument("--require-qmax", action="store_true")
    ap.add_argument("--require-over-sib", action="store_true")
    args = ap.parse_args()

    pairs = matched_pairs()
    print("matched_pairs", len(pairs))
    first_fail = None
    checked = 0
    feasible = 0
    min_gap = None
    min_case = None
    qmax_cache = {}
    wi_cache = {}

    def cached_is_qmax(g6, side, weights0):
        key = (g6, tuple(weights0))
        if key not in qmax_cache:
            qmax_cache[key] = qmaxcut_value(g6, list(weights0))
        return qcut_value(g6, side, list(weights0)) == qmax_cache[key]

    def cached_weighted_I(g6, side, row, weights0):
        key = (g6, side, tuple(row), tuple(weights0))
        if key not in wi_cache:
            wi_cache[key] = weighted_I(g6, side, row, list(weights0))
        return wi_cache[key]

    if args.mode == "exhaustive":
        iterator = product(range(1, args.max_weight + 1), repeat=10)
    else:
        rng = random.Random(args.seed)
        iterator = (
            tuple(rng.randint(1, args.max_weight) for _ in range(10))
            for _ in range(args.samples)
        )

    for weights in iterator:
        weights = list(weights)
        checked += 1
        for er, sr, mp, extra in pairs:
            weights_eq = pullback_weights(weights, mp)
            isib = cached_weighted_I(SIB, sr["side"], sr["P"], weights)
            if args.require_over_sib and isib <= sum(weights):
                continue
            if args.require_qmax and (not cached_is_qmax(SIB, sr["side"], weights) or not cached_is_qmax(EQ, er["side"], weights_eq)):
                continue
            feasible += 1
            ieq = cached_weighted_I(EQ, er["side"], er["P"], weights_eq)
            gap = ieq - isib
            if min_gap is None or gap < min_gap:
                min_gap = gap
                min_case = (weights, er["side"], er["P"], sr["side"], sr["P"], gap)
            if gap < 0:
                first_fail = {
                    "weights_sib": weights,
                    "eq_side": er["side"],
                    "eq_P": er["P"],
                    "sib_side": sr["side"],
                    "sib_P": sr["P"],
                    "extra": sorted(extra),
                    "I_eq": ieq,
                    "I_sib": isib,
                    "gap": gap,
                }
                break
        if first_fail is not None:
            break

    print("checked_weights", checked)
    print("feasible_pair_checks", feasible)
    print("min_gap", min_gap)
    print("min_case", min_case)
    print("first_fail", first_fail)
    print("VERDICT", "PASS" if first_fail is None else "FAIL")


if __name__ == "__main__":
    main()





