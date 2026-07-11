"""Exact R20 matcher gate for every globally minimum row tuple.

For each connected triangle-free graph, enumerate canonical maximum cuts and
retain every Gamma-minimum B-connected cut with a nonempty bad-edge set.  If a
retained cut has ell=5 on every bad edge, construct its complete shortest-row
families and evaluate every coherent row tuple with the row-reserved
sameOwner/rowCompanion matcher.  The gate counts every tuple tied at the
global obligation-score minimum of its cut, rather than selecting one
lexicographic minimizer.

All cut, Gamma, score, matching, and census calculations are integer exact.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter, deque
from concurrent.futures import ProcessPoolExecutor
from itertools import product, repeat
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _codex_r20_two_row_exchange_gate import (  # noqa: E402
    dec,
    evaluate_rows,
    graph6_for_orders,
    obligation_score,
    shortest_row_families,
)
from _h import Bconn, bdist_restr, geos, maxcut_all  # noqa: E402


STAT_FIELDS = (
    "graphs",
    "connectedTriangleFreeGraphs",
    "graphsWithGammaMinCuts",
    "graphsWithEligibleCuts",
    "maximumCuts",
    "bConnectedMaximumCuts",
    "bConnectedCutsWithBadEdges",
    "gammaMinCuts",
    "gammaMinCutsNotAll5",
    "eligibleCuts",
    "totalTuples",
    "matcherFailingTuples",
    "minimizingTuples",
    "hallFailingMinimizingTuples",
    "cutsWithMultipleMinimizers",
    "cutsWithHallFailingMinimizers",
)


def empty_stats() -> dict[str, int]:
    return {field: 0 for field in STAT_FIELDS}


def add_stats(target: dict[str, int], source) -> None:
    for field in STAT_FIELDS:
        target[field] += source.get(field, 0)


def graph_domain_status(n: int, adjacency: list[set[int]]) -> str:
    """Verify fixture inputs satisfy the domain guaranteed by ``geng -tc``."""
    if n == 0:
        return "skipDisconnected"
    seen = {0}
    queue = deque([0])
    while queue:
        u = queue.popleft()
        for v in adjacency[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    if len(seen) != n:
        return "skipDisconnected"
    if any(
        adjacency[u] & adjacency[v]
        for u in range(n)
        for v in adjacency[u]
        if u < v
    ):
        return "skipNotTriangleFree"
    return "connectedTriangleFree"


def canonical_side(side: list[int] | tuple[int, ...]) -> tuple[int, tuple[int, ...]]:
    """Canonicalize a cut modulo exchange of its two sides."""
    n = len(side)
    mask = sum(int(bit) << vertex for vertex, bit in enumerate(side))
    complement = ((1 << n) - 1) ^ mask
    canonical_mask = min(mask, complement)
    canonical = tuple(
        (canonical_mask >> vertex) & 1 for vertex in range(n)
    )
    return canonical_mask, canonical


def graph_edges_of(
    n: int, adjacency: list[set[int]]
) -> tuple[tuple[int, int], ...]:
    return tuple(
        (u, v)
        for u in range(n)
        for v in sorted(adjacency[u])
        if u < v
    )


def cut_gamma_data(
    adjacency: list[set[int]],
    graph_edges: tuple[tuple[int, int], ...],
    side: tuple[int, ...],
):
    """Return bad edges, lengths, and Gamma for a connected nonempty cut."""
    bad_edges = tuple(
        graph_edge
        for graph_edge in graph_edges
        if side[graph_edge[0]] == side[graph_edge[1]]
    )
    if not bad_edges:
        return None
    lengths = {}
    for u, v in bad_edges:
        distance = bdist_restr(adjacency, side, u, v)
        assert distance >= 0
        lengths[(u, v)] = distance + 1
    gamma = sum(length * length for length in lengths.values())
    return bad_edges, lengths, gamma


def complete_cut_info(
    n: int,
    adjacency: list[set[int]],
    graph_edges: tuple[tuple[int, int], ...],
    side: tuple[int, ...],
    side_bitmask: int,
    bad_edges: tuple[tuple[int, int], ...],
    lengths: dict[tuple[int, int], int],
    gamma: int,
):
    """Build literal complete shortest-row families for one retained cut."""
    blue = {
        graph_edge
        for graph_edge in graph_edges
        if side[graph_edge[0]] != side[graph_edge[1]]
    }
    bad = set(bad_edges)
    rows_by_edge = {}
    for bad_edge in bad_edges:
        rows = tuple(sorted(
            tuple(row)
            for row in geos(
                adjacency, side, bad_edge[0], bad_edge[1]
            )
        ))
        assert rows
        assert all(len(row) == lengths[bad_edge] for row in rows)
        rows_by_edge[bad_edge] = rows
    return {
        "n": n,
        "adj": adjacency,
        "side": side,
        "sideBitmask": side_bitmask,
        "M": bad_edges,
        "ell": lengths,
        "Bset": blue,
        "Mset": bad,
        "cyc": rows_by_edge,
        "G": gamma,
    }


def exact_falsifier(
    g6: str,
    n: int,
    info,
    family_sizes: tuple[int, ...],
    total_tuples: int,
    choice: tuple[int, ...],
    rows: tuple[tuple[int, ...], ...],
    score: int,
    matching_failure,
):
    return {
        "g6": g6,
        "order": n,
        "sideBitmask": info["sideBitmask"],
        "gamma": info["G"],
        "badEdges": [list(bad_edge) for bad_edge in info["M"]],
        "familySizes": list(family_sizes),
        "totalTuplesForCut": total_tuples,
        "globalMinimumScore": score,
        "rowChoices": list(choice),
        "rows": [list(row) for row in rows],
        "matchingFailure": matching_failure,
    }


def evaluate_cut(g6: str, n: int, info, falsifier_limit: int):
    """Evaluate all tuples and retain every tie at this cut's global minimum."""
    families = shortest_row_families(info)
    family_sizes = tuple(len(family) for family in families)
    total_tuples = math.prod(family_sizes)
    assert total_tuples > 0

    global_minimum = None
    minimizing_tuples = 0
    failing_minimizers = 0
    matcher_failures = 0
    first_falsifiers = []

    for choice in product(*(range(size) for size in family_sizes)):
        rows = tuple(
            families[index][row_index]
            for index, row_index in enumerate(choice)
        )
        score = obligation_score(n, info, rows)
        assert isinstance(score, int)
        kind, returned_g6, detail = evaluate_rows(
            g6, n, info, rows, "row-reserved"
        )
        assert returned_g6 == g6
        assert kind in {"pass", "fail"}
        failed = kind == "fail"
        matcher_failures += int(failed)

        if global_minimum is None or score < global_minimum:
            global_minimum = score
            minimizing_tuples = 1
            failing_minimizers = int(failed)
            first_falsifiers = []
            if failed and falsifier_limit > 0:
                first_falsifiers.append(exact_falsifier(
                    g6,
                    n,
                    info,
                    family_sizes,
                    total_tuples,
                    choice,
                    rows,
                    score,
                    detail,
                ))
        elif score == global_minimum:
            minimizing_tuples += 1
            failing_minimizers += int(failed)
            if failed and len(first_falsifiers) < falsifier_limit:
                first_falsifiers.append(exact_falsifier(
                    g6,
                    n,
                    info,
                    family_sizes,
                    total_tuples,
                    choice,
                    rows,
                    score,
                    detail,
                ))

    assert global_minimum is not None
    assert 0 < minimizing_tuples <= total_tuples
    assert 0 <= failing_minimizers <= minimizing_tuples
    for falsifier in first_falsifiers:
        falsifier["minimizingTuplesForCut"] = minimizing_tuples
        falsifier["hallFailingMinimizingTuplesForCut"] = failing_minimizers
    return {
        "totalTuples": total_tuples,
        "matcherFailingTuples": matcher_failures,
        "minimizingTuples": minimizing_tuples,
        "hallFailingMinimizingTuples": failing_minimizers,
        "cutsWithMultipleMinimizers": int(minimizing_tuples > 1),
        "cutsWithHallFailingMinimizers": int(failing_minimizers > 0),
    }, global_minimum, first_falsifiers


def evaluate_graph(g6: str, falsifier_limit: int):
    """Evaluate every canonical Gamma-minimum connected maximum-cut tie."""
    n, decoded_edges = dec(g6)
    adjacency = [set() for _ in range(n)]
    for u, v in decoded_edges:
        adjacency[u].add(v)
        adjacency[v].add(u)

    stats = empty_stats()
    stats["graphs"] = 1
    status = graph_domain_status(n, adjacency)
    if status != "connectedTriangleFree":
        return {
            "order": n,
            "status": status,
            **stats,
            "minimumScoreHistogram": {},
            "minimizingByScore": {},
            "failingMinimizingByScore": {},
            "firstFalsifiers": [],
        }
    stats["connectedTriangleFreeGraphs"] = 1

    graph_edges = graph_edges_of(n, adjacency)
    canonical_cuts = {}
    for raw_side in maxcut_all(n, adjacency):
        side_bitmask, side = canonical_side(raw_side)
        canonical_cuts.setdefault(side_bitmask, side)
    stats["maximumCuts"] = len(canonical_cuts)

    candidates = []
    for side_bitmask, side in sorted(canonical_cuts.items()):
        if not Bconn(n, adjacency, side):
            continue
        stats["bConnectedMaximumCuts"] += 1
        gamma_data = cut_gamma_data(adjacency, graph_edges, side)
        if gamma_data is None:
            continue
        stats["bConnectedCutsWithBadEdges"] += 1
        bad_edges, lengths, gamma = gamma_data
        candidates.append((gamma, side_bitmask, side, bad_edges, lengths))

    if not candidates:
        return {
            "order": n,
            "status": "skipNoGammaCut",
            **stats,
            "minimumScoreHistogram": {},
            "minimizingByScore": {},
            "failingMinimizingByScore": {},
            "firstFalsifiers": [],
        }

    minimum_gamma = min(candidate[0] for candidate in candidates)
    gamma_min_cuts = [
        candidate for candidate in candidates if candidate[0] == minimum_gamma
    ]
    stats["graphsWithGammaMinCuts"] = 1
    stats["gammaMinCuts"] = len(gamma_min_cuts)

    minimum_score_histogram = Counter()
    minimizing_by_score = Counter()
    failing_minimizing_by_score = Counter()
    first_falsifiers = []
    for gamma, side_bitmask, side, bad_edges, lengths in gamma_min_cuts:
        if any(length != 5 for length in lengths.values()):
            stats["gammaMinCutsNotAll5"] += 1
            continue
        info = complete_cut_info(
            n,
            adjacency,
            graph_edges,
            side,
            side_bitmask,
            bad_edges,
            lengths,
            gamma,
        )
        stats["eligibleCuts"] += 1
        cut_stats, global_minimum, cut_falsifiers = evaluate_cut(
            g6, n, info, falsifier_limit
        )
        add_stats(stats, cut_stats)
        minimum_score_histogram[global_minimum] += 1
        minimizing_by_score[global_minimum] += cut_stats["minimizingTuples"]
        failing_minimizing_by_score[global_minimum] += cut_stats[
            "hallFailingMinimizingTuples"
        ]
        remaining = falsifier_limit - len(first_falsifiers)
        if remaining > 0:
            first_falsifiers.extend(cut_falsifiers[:remaining])

    stats["graphsWithEligibleCuts"] = int(stats["eligibleCuts"] > 0)
    graph_status = "eligible" if stats["eligibleCuts"] else "skipNotAll5"
    return {
        "order": n,
        "status": graph_status,
        **stats,
        "minimumScoreHistogram": dict(minimum_score_histogram),
        "minimizingByScore": dict(minimizing_by_score),
        "failingMinimizingByScore": dict(failing_minimizing_by_score),
        "firstFalsifiers": first_falsifiers,
    }


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be a nonnegative integer")
    return parsed


def render_counter(counter: Counter) -> dict[str, int]:
    return {str(key): counter[key] for key in sorted(counter)}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-order", type=positive_int, default=5)
    parser.add_argument("--max-order", type=positive_int, default=10)
    parser.add_argument(
        "--workers",
        type=positive_int,
        default=min(48, os.cpu_count() or 1),
    )
    parser.add_argument(
        "--max-falsifiers",
        type=nonnegative_int,
        default=20,
        help="maximum number of first failing global minimizers to include",
    )
    parser.add_argument(
        "--graph6",
        action="append",
        default=[],
        help="test a connected triangle-free graph6 fixture; repeatable",
    )
    args = parser.parse_args()
    if args.min_order > args.max_order:
        parser.error("--min-order must not exceed --max-order")
    if args.workers > 48:
        parser.error("--workers must not exceed 48")
    return args


def main() -> None:
    args = parse_args()
    if args.graph6:
        graph6 = args.graph6
        generated = dict(sorted(Counter(dec(g6)[0] for g6 in graph6).items()))
    else:
        graph6, generated = graph6_for_orders(
            args.min_order, args.max_order
        )

    aggregate = empty_stats()
    statuses = Counter()
    minimum_score_histogram = Counter()
    minimizing_by_score = Counter()
    failing_minimizing_by_score = Counter()
    by_order = {}
    first_falsifiers = []

    if args.workers == 1:
        results = map(evaluate_graph, graph6, repeat(args.max_falsifiers))
        pool = None
    else:
        pool = ProcessPoolExecutor(max_workers=args.workers)
        results = pool.map(
            evaluate_graph,
            graph6,
            repeat(args.max_falsifiers),
            chunksize=4,
        )

    try:
        for result in results:
            statuses[result["status"]] += 1
            add_stats(aggregate, result)
            minimum_score_histogram.update(result["minimumScoreHistogram"])
            minimizing_by_score.update(result["minimizingByScore"])
            failing_minimizing_by_score.update(
                result["failingMinimizingByScore"]
            )

            order_data = by_order.setdefault(result["order"], {
                "stats": empty_stats(),
                "minimumScoreHistogram": Counter(),
                "minimizingByScore": Counter(),
                "failingMinimizingByScore": Counter(),
            })
            add_stats(order_data["stats"], result)
            order_data["minimumScoreHistogram"].update(
                result["minimumScoreHistogram"]
            )
            order_data["minimizingByScore"].update(
                result["minimizingByScore"]
            )
            order_data["failingMinimizingByScore"].update(
                result["failingMinimizingByScore"]
            )

            remaining = args.max_falsifiers - len(first_falsifiers)
            if remaining > 0:
                first_falsifiers.extend(
                    result["firstFalsifiers"][:remaining]
                )
    finally:
        if pool is not None:
            pool.shutdown()

    score_range = (
        [min(minimum_score_histogram), max(minimum_score_histogram)]
        if minimum_score_histogram else None
    )
    rendered_by_order = {}
    for order, order_data in sorted(by_order.items()):
        rendered_by_order[str(order)] = {
            **order_data["stats"],
            "globalMinimumScoreHistogram": render_counter(
                order_data["minimumScoreHistogram"]
            ),
            "minimizingTuplesByScore": render_counter(
                order_data["minimizingByScore"]
            ),
            "hallFailingMinimizingTuplesByScore": render_counter(
                order_data["failingMinimizingByScore"]
            ),
        }

    payload = {
        "orders": [args.min_order, args.max_order],
        "workers": args.workers,
        "fixtureMode": bool(args.graph6),
        "generatedGraphs": len(graph6),
        "generatedByOrder": {
            str(order): count for order, count in sorted(generated.items())
        },
        "status": dict(sorted(statuses.items())),
        "cutIdConvention": "sideBitmask=sum(side[v]*2^v),min(complements)",
        "globalMinimumScope": "each eligible Gamma-min cut",
        **aggregate,
        "globalMinimumScoreRange": score_range,
        "globalMinimumScoreHistogram": render_counter(
            minimum_score_histogram
        ),
        "minimizingTuplesByScore": render_counter(minimizing_by_score),
        "hallFailingMinimizingTuplesByScore": render_counter(
            failing_minimizing_by_score
        ),
        "byOrder": rendered_by_order,
        "firstFalsifiersLimit": args.max_falsifiers,
        "firstFalsifiersTruncated": (
            aggregate["hallFailingMinimizingTuples"]
            > len(first_falsifiers)
        ),
        "firstFalsifiers": first_falsifiers,
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
