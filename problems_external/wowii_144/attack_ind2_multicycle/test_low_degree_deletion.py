"""Exact low-degree audit for the W144-IND2 deletion frontier."""

from __future__ import annotations

import argparse
from collections import Counter

import networkx as nx

from analyze_tight_deletions import center_depth, cycle_rank, girth, records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("max_order", type=int)
    args = parser.parse_args()

    graph_count = 0
    positive_count = 0
    low_degree_failures = []
    drop_counter = Counter()
    winner_degree_counter = Counter()
    winner_core_degree_counter = Counter()
    for order in range(5, args.max_order + 1):
        order_count = 0
        for code, graph in records(order):
            g = girth(graph)
            if g is None or g < 5 or cycle_rank(graph) < 2:
                continue
            graph_count += 1
            order_count += 1
            e, _ = center_depth(graph)
            if e > 0:
                positive_count += 1
            core = nx.k_core(graph, 2)
            good = []
            for v in graph:
                h = graph.copy()
                h.remove_node(v)
                if not nx.is_connected(h) or cycle_rank(h) < 1:
                    continue
                gh = girth(h)
                assert gh is not None
                eh, _ = center_depth(h)
                drop_counter[eh - e] += 1
                if gh + eh >= g + e:
                    good.append(v)
            assert good
            winner_degree_counter[min(graph.degree[v] for v in good)] += 1
            winner_core_degree_counter[
                min(core.degree[v] if v in core else -1 for v in good)
            ] += 1
            if e > 0 and not any(graph.degree[v] <= 2 for v in good):
                low_degree_failures.append(
                    (
                        code.decode(),
                        order,
                        g,
                        e,
                        cycle_rank(graph),
                        sorted(dict(graph.degree()).values()),
                        [(v, graph.degree[v]) for v in good],
                    )
                )
                if len(low_degree_failures) >= 20:
                    break
        print("ORDER", order, order_count)
        if len(low_degree_failures) >= 20:
            break
    print("GRAPHS", graph_count, "POSITIVE_E", positive_count)
    print("MIN_WINNER_DEGREE", sorted(winner_degree_counter.items()))
    print("MIN_WINNER_CORE_DEGREE", sorted(winner_core_degree_counter.items()))
    print("CENTER_DEPTH_DELTAS", sorted(drop_counter.items()))
    print("LOW_DEGREE_FAILURES", len(low_degree_failures))
    for item in low_degree_failures:
        print(item)


if __name__ == "__main__":
    main()
