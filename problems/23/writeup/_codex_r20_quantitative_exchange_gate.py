"""Compare maximum Hall deficiency with the best <=2-row score descent."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from itertools import combinations, product

from _codex_r19_global_base_census import dec, edge, full_matching, global_candidates, graph6_for_orders, loads, multiplicities, owner_demands
from _codex_r20_two_row_atom_analysis import score_detail
from _codex_r20_two_row_exchange_gate import shortest_row_families


def matching_instance(n, info, rows):
    count = multiplicities(n, rows)
    component = set().union(*(set(row) for row in rows)) if rows else set()
    support = {edge(u, v) for row in rows for u, v in zip(row, row[1:])}
    active = {
        e for e in info["Bset"]
        if e[0] in component and e[1] in component and e not in support
    }
    reserved = {
        source for u, v in active for source in ((u, v, 0), (v, u, 0))
    }
    raw = owner_demands(count, component, active)
    demand = {
        owner: sum(item[0] == "collision" for item in items)
        for owner, items in raw.items()
    }
    demand = {owner: value for owner, value in demand.items() if value}
    candidates = {
        owner: {
            source for source in global_candidates(
                owner, n, count, info["adj"], info["Bset"], info["Mset"],
                "row-reserved",
            )
            if source not in reserved
        }
        for owner in demand
    }
    return demand, candidates


def maximum_deficiency(demand, candidates):
    owners = sorted(demand)
    sources = sorted(set().union(*(candidates[o] for o in owners)))
    source_id = {source: i for i, source in enumerate(sources)}
    masks = [sum(1 << source_id[s] for s in candidates[o]) for o in owners]
    states = [(0, 0)]
    maximum = 0
    for owner, mask in zip(owners, masks):
        add = demand[owner]
        old = list(states)
        states.extend((value + add, union | mask) for value, union in old)
    for value, union in states:
        maximum = max(maximum, value - union.bit_count())
    return maximum


def best_descent(choice, sizes, scores):
    old = scores[choice][0]
    best = old
    for i, size in enumerate(sizes):
        for ri in range(size):
            if ri == choice[i]:
                continue
            neighbor = choice[:i] + (ri,) + choice[i + 1:]
            best = min(best, scores[neighbor][0])
    for i, j in combinations(range(len(choice)), 2):
        for ri in range(sizes[i]):
            if ri == choice[i]:
                continue
            for rj in range(sizes[j]):
                if rj == choice[j]:
                    continue
                neighbor = list(choice)
                neighbor[i] = ri
                neighbor[j] = rj
                best = min(best, scores[tuple(neighbor)][0])
    return old - best


def analyze_graph(g6):
    n, graph_edges = dec(g6)
    info = loads(n, graph_edges)
    if info is None or any(length != 5 for length in info["ell"].values()):
        return None
    families = shortest_row_families(info)
    sizes = tuple(map(len, families))
    choices = list(product(*(range(size) for size in sizes)))
    scores = {}
    instances = {}
    for choice in choices:
        rows = tuple(families[i][choice[i]] for i in range(len(choice)))
        scores[choice] = score_detail(n, info, rows)
        demand, candidates = matching_instance(n, info, rows)
        expanded = {owner: list(range(value)) for owner, value in demand.items()}
        _, unmatched = full_matching(expanded, candidates)
        if not unmatched:
            continue
        deficiency = maximum_deficiency(demand, candidates)
        if deficiency > 0:
            instances[choice] = deficiency
    out = []
    for choice, deficiency in instances.items():
        drop = best_descent(choice, sizes, scores)
        out.append((deficiency, drop, choice))
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-order", type=int, default=5)
    parser.add_argument("--max-order", type=int, default=11)
    parser.add_argument("--workers", type=int, default=min(61, os.cpu_count() or 1))
    args = parser.parse_args()
    if not (1 <= args.workers <= 61):
        parser.error("--workers must be between 1 and 61 on Windows")
    graph6, generated = graph6_for_orders(args.min_order, args.max_order)
    count = 0
    violations = Counter()
    ratio_hist = Counter()
    minimum_ratio = None
    witness = None
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for g6, result in zip(graph6, pool.map(analyze_graph, graph6, chunksize=8)):
            if result is None:
                continue
            for deficiency, drop, choice in result:
                count += 1
                ratio = Fraction(drop, deficiency)
                ratio_hist[str(ratio)] += 1
                if minimum_ratio is None or ratio < minimum_ratio:
                    minimum_ratio = ratio
                    witness = {"g6": g6, "choice": choice, "deficiency": deficiency, "drop": drop}
                if drop < deficiency:
                    violations["drop_lt_deficiency"] += 1
                if drop < 2 * deficiency:
                    violations["drop_lt_2deficiency"] += 1
    print(json.dumps({
        "orders": [args.min_order, args.max_order],
        "workers": args.workers,
        "generatedByOrder": generated,
        "failedTuples": count,
        "violations": dict(sorted(violations.items())),
        "minimumRatio": None if minimum_ratio is None else str(minimum_ratio),
        "minimumRatioWitness": witness,
        "ratioHistogram": dict(sorted(ratio_hist.items())),
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
