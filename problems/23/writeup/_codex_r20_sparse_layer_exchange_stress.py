"""Exact sparse five-layer falsifier stress for R20 row exchange.

Each trial builds a connected triangle-free graph on five nonempty layers.
Candidate blue edges join only consecutive layers 0-1-2-3-4, while candidate
bad edges join layers 4 and 0.  A literal C5 is retained in every graph, so an
odd cycle is present before the exact cut selector is called.

``_h.loads`` exhaustively selects its Gamma-minimum connected maximum cut.
For a selected all-ell=5 cut whose complete shortest-row product fits the cap,
this gate enumerates every coherent row tuple.  Every failed row-reserved
sameOwner/rowCompanion matching must have a strictly lower obligation score at
Hamming distance at most two.  Such a descent is a necessary consequence of
``HallFailureHasDescent``; a missing descent is therefore a falsifier.

All generator coins, scores, matching capacities, and comparisons are exact
integers.  This is a bounded falsifier search, not a proof of the theorem.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from collections import Counter, deque
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _codex_r20_two_row_exchange_gate as _gate  # noqa: E402
import _h  # noqa: E402


FIRST_FALSIFIER_LIMIT = 10
COUNT_FIELDS = (
    "generatedGraphs",
    "connectedGraphs",
    "triangleFreeGraphs",
    "oddCycleGraphs",
    "noSelectedCutGraphs",
    "selectedCutGraphs",
    "selectedIntendedLayerCutGraphs",
    "selectedAlternateCutGraphs",
    "notAllEll5Graphs",
    "allEll5Graphs",
    "completeShortestRowTuples",
    "overTupleCapGraphs",
    "enumeratedGraphs",
    "rowTuplesEnumerated",
    "matchingPassTuples",
    "matchingFailureTuples",
    "reservedHitAssignments",
    "sameOwnerAssignments",
    "rowCompanionAssignments",
    "failuresWithOneRowDescent",
    "failuresWithOnlyTwoRowDescent",
    "failedMatchingsWithVerifiedDescent",
    "falsifiers",
)


def norm_edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def adjacency(n: int, edges) -> list[set[int]]:
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def is_connected(adj: list[set[int]]) -> bool:
    seen = {0}
    queue = deque([0])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    return len(seen) == len(adj)


def is_triangle_free(adj: list[set[int]], edges) -> bool:
    return all(not (adj[u] & adj[v]) for u, v in edges)


def has_odd_cycle(adj: list[set[int]]) -> bool:
    colors: dict[int, int] = {}
    for root in range(len(adj)):
        if root in colors:
            continue
        colors[root] = 0
        queue = deque([root])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v not in colors:
                    colors[v] = 1 - colors[u]
                    queue.append(v)
                elif colors[v] == colors[u]:
                    return True
    return False


def graph_distance(adj: list[set[int]], start: int, target: int) -> int:
    distances = {start: 0}
    queue = deque([start])
    while queue:
        u = queue.popleft()
        if u == target:
            return distances[u]
        for v in adj[u]:
            if v not in distances:
                distances[v] = distances[u] + 1
                queue.append(v)
    return -1


def positive_composition(total: int, rng: random.Random) -> tuple[int, ...]:
    cuts = sorted(rng.sample(range(1, total), 4))
    return (
        cuts[0],
        cuts[1] - cuts[0],
        cuts[2] - cuts[1],
        cuts[3] - cuts[2],
        total - cuts[3],
    )


def generate_graph(master_seed: int, trial: int, min_order: int, max_order: int):
    trial_seed = master_seed + trial
    rng = random.Random(trial_seed)
    n = rng.randint(min_order, max_order)
    sizes = positive_composition(n, rng)

    layers = []
    offset = 0
    for size in sizes:
        layers.append(tuple(range(offset, offset + size)))
        offset += size
    layers = tuple(layers)
    layer_of = {
        vertex: layer_index
        for layer_index, layer in enumerate(layers)
        for vertex in layer
    }

    anchors = tuple(rng.choice(layer) for layer in layers)
    path_edges = {
        norm_edge(anchors[i], anchors[i + 1]) for i in range(4)
    }
    connected_vertices = set(anchors)
    remaining = [
        vertex
        for layer in layers
        for vertex in layer
        if vertex not in connected_vertices
    ]
    rng.shuffle(remaining)
    for u in remaining:
        layer_index = layer_of[u]
        neighbour_layers = []
        if layer_index > 0:
            neighbour_layers.append(layer_index - 1)
        if layer_index < 4:
            neighbour_layers.append(layer_index + 1)
        candidates = [
            v
            for other_layer in neighbour_layers
            for v in layers[other_layer]
            if v in connected_vertices
        ]
        assert candidates
        path_edges.add(norm_edge(u, rng.choice(candidates)))
        connected_vertices.add(u)

    path_rates = tuple(rng.randint(15, 45) for _ in range(4))
    for layer_index, rate in enumerate(path_rates):
        for u in layers[layer_index]:
            for v in layers[layer_index + 1]:
                candidate = norm_edge(u, v)
                if candidate not in path_edges and rng.randrange(100) < rate:
                    path_edges.add(candidate)

    path_adj = adjacency(n, path_edges)
    valid_bad_candidates = [
        norm_edge(u, v)
        for u in layers[4]
        for v in layers[0]
        if graph_distance(path_adj, u, v) == 4
    ]
    anchor_bad = norm_edge(anchors[4], anchors[0])
    assert anchor_bad in valid_bad_candidates
    bad_rate = rng.randint(8, 30)
    bad_edges = {anchor_bad}
    for candidate in valid_bad_candidates:
        if candidate != anchor_bad and rng.randrange(100) < bad_rate:
            bad_edges.add(candidate)

    edges = tuple(sorted(path_edges | bad_edges))
    adj = adjacency(n, edges)
    assert len(connected_vertices) == n
    assert is_connected(adj)
    assert is_triangle_free(adj, edges)
    assert has_odd_cycle(adj)
    assert all(
        abs(layer_of[u] - layer_of[v]) == 1
        for u, v in path_edges
    )
    assert all(
        {layer_of[u], layer_of[v]} == {0, 4}
        for u, v in bad_edges
    )

    return {
        "masterSeed": master_seed,
        "trial": trial,
        "trialSeed": trial_seed,
        "order": n,
        "layerSizes": sizes,
        "layers": layers,
        "anchors": anchors,
        "pathRatesPercent": path_rates,
        "badRatePercent": bad_rate,
        "candidateBlueEdges": tuple(sorted(path_edges)),
        "candidateBadEdges": tuple(sorted(bad_edges)),
        "edges": edges,
    }


def graph_payload(graph, info) -> dict:
    selected_layer_cut = (
        info["Bset"] == set(graph["candidateBlueEdges"])
        and info["Mset"] == set(graph["candidateBadEdges"])
    )
    return {
        "masterSeed": graph["masterSeed"],
        "trial": graph["trial"],
        "trialSeed": graph["trialSeed"],
        "order": graph["order"],
        "layerSizes": graph["layerSizes"],
        "layers": graph["layers"],
        "anchors": graph["anchors"],
        "pathRatesPercent": graph["pathRatesPercent"],
        "badRatePercent": graph["badRatePercent"],
        "edges": graph["edges"],
        "candidateBlueEdges": graph["candidateBlueEdges"],
        "candidateBadEdges": graph["candidateBadEdges"],
        "selectedSide": info["side"],
        "selectedBlueEdges": tuple(sorted(info["Bset"])),
        "selectedBadEdges": tuple(info["M"]),
        "selectedEll": tuple(
            (bad_edge, info["ell"][bad_edge]) for bad_edge in info["M"]
        ),
        "selectedIntendedLayerCut": selected_layer_cut,
        "selectedGamma": info["G"],
        "selectedCutSize": len(info["Bset"]),
    }


def falsifier_payload(
    graph,
    info,
    family_sizes,
    row_product,
    families,
    choice,
    score,
    best_one,
    best_two,
    matching_failure,
) -> dict:
    rows = tuple(
        families[index][row_index]
        for index, row_index in enumerate(choice)
    )
    return {
        **graph_payload(graph, info),
        "familySizes": family_sizes,
        "completeShortestRowProduct": row_product,
        "rowChoice": choice,
        "rows": rows,
        "obligationScore": score,
        "bestOneRowScore": best_one,
        "bestTwoRowScore": best_two,
        "matchingFailure": matching_failure,
    }


def analyze_trial(task) -> dict:
    master_seed, trial, min_order, max_order, tuple_cap = task
    graph = generate_graph(
        master_seed, trial, min_order, max_order
    )
    n = graph["order"]
    edges = graph["edges"]
    adj = adjacency(n, edges)
    counts = Counter({
        "generatedGraphs": 1,
        "connectedGraphs": int(is_connected(adj)),
        "triangleFreeGraphs": int(is_triangle_free(adj, edges)),
        "oddCycleGraphs": int(has_odd_cycle(adj)),
    })

    info = _h.loads(n, list(edges))
    if info is None:
        counts["noSelectedCutGraphs"] += 1
        return {
            "order": n,
            "status": "skipNoSelectedCut",
            "counts": counts,
            "rowProduct": None,
            "falsifiers": [],
        }

    counts["selectedCutGraphs"] += 1
    selected_layer_cut = (
        info["Bset"] == set(graph["candidateBlueEdges"])
        and info["Mset"] == set(graph["candidateBadEdges"])
    )
    counts[
        "selectedIntendedLayerCutGraphs"
        if selected_layer_cut
        else "selectedAlternateCutGraphs"
    ] += 1
    if any(length != 5 for length in info["ell"].values()):
        counts["notAllEll5Graphs"] += 1
        return {
            "order": n,
            "status": "skipNotAll5",
            "counts": counts,
            "rowProduct": None,
            "falsifiers": [],
        }

    counts["allEll5Graphs"] += 1
    families = _gate.shortest_row_families(info)
    family_sizes = tuple(len(family) for family in families)
    row_product = math.prod(family_sizes)
    counts["completeShortestRowTuples"] += row_product
    if row_product > tuple_cap:
        counts["overTupleCapGraphs"] += 1
        return {
            "order": n,
            "status": "skipTupleCap",
            "counts": counts,
            "rowProduct": row_product,
            "falsifiers": [],
        }

    graph_id = f"sparse5:{master_seed}:{trial}"
    scores: dict[tuple[int, ...], int] = {}
    failed_choices = []
    for choice in product(*(range(size) for size in family_sizes)):
        rows = tuple(
            families[index][row_index]
            for index, row_index in enumerate(choice)
        )
        score = _gate.obligation_score(n, info, rows)
        assert isinstance(score, int)
        scores[choice] = score
        kind, returned_id, detail = _gate.evaluate_rows(
            graph_id, n, info, rows, "row-reserved"
        )
        assert returned_id == graph_id
        counts["rowTuplesEnumerated"] += 1
        counts["reservedHitAssignments"] += detail.get("reservedHits", 0)
        if kind == "pass":
            counts["matchingPassTuples"] += 1
            counts["sameOwnerAssignments"] += detail.get(
                "relations", {}
            ).get("sameOwner", 0)
            counts["rowCompanionAssignments"] += detail.get(
                "relations", {}
            ).get("rowCompanion", 0)
        else:
            assert kind == "fail"
            counts["matchingFailureTuples"] += 1
            failed_choices.append(choice)
    assert len(scores) == row_product

    first_falsifiers = []
    for choice in failed_choices:
        score = scores[choice]
        best_one, best_two = _gate.minimum_neighbor_scores(
            choice, family_sizes, scores
        )
        assert best_one is None or isinstance(best_one, int)
        assert best_two is None or isinstance(best_two, int)
        if best_one is not None and best_one < score:
            counts["failuresWithOneRowDescent"] += 1
            continue
        if best_two is not None and best_two < score:
            counts["failuresWithOnlyTwoRowDescent"] += 1
            continue

        counts["falsifiers"] += 1
        if len(first_falsifiers) >= FIRST_FALSIFIER_LIMIT:
            continue
        rows = tuple(
            families[index][row_index]
            for index, row_index in enumerate(choice)
        )
        kind, returned_id, detail = _gate.evaluate_rows(
            graph_id, n, info, rows, "row-reserved"
        )
        assert kind == "fail" and returned_id == graph_id
        first_falsifiers.append(falsifier_payload(
            graph,
            info,
            family_sizes,
            row_product,
            families,
            choice,
            score,
            best_one,
            best_two,
            detail,
        ))

    verified = (
        counts["failuresWithOneRowDescent"]
        + counts["failuresWithOnlyTwoRowDescent"]
    )
    counts["failedMatchingsWithVerifiedDescent"] += verified
    assert (
        verified + counts["falsifiers"]
        == counts["matchingFailureTuples"]
    )
    counts["enumeratedGraphs"] += 1
    return {
        "order": n,
        "status": "enumerated",
        "counts": counts,
        "rowProduct": row_product,
        "falsifiers": first_falsifiers,
    }


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260711)
    parser.add_argument("--trials", type=positive_int, default=256)
    parser.add_argument("--min-order", type=positive_int, default=12)
    parser.add_argument("--max-order", type=positive_int, default=18)
    parser.add_argument(
        "--workers",
        type=positive_int,
        default=min(61, os.cpu_count() or 1),
    )
    parser.add_argument("--tuple-cap", type=positive_int, default=50000)
    args = parser.parse_args()
    if args.min_order < 5:
        parser.error("--min-order must be at least 5")
    if args.min_order > args.max_order:
        parser.error("--min-order must not exceed --max-order")
    if args.workers > 61:
        parser.error("--workers must not exceed 61")
    return args


def main():
    args = parse_args()
    tasks = [
        (
            args.seed,
            trial,
            args.min_order,
            args.max_order,
            args.tuple_cap,
        )
        for trial in range(args.trials)
    ]

    totals = Counter()
    status = Counter()
    generated_by_order = Counter()
    all5_by_order = Counter()
    enumerated_by_order = Counter()
    first_falsifiers = []
    max_row_product = 0
    max_enumerated_row_product = 0

    if args.workers == 1:
        results = map(analyze_trial, tasks)
        pool = None
    else:
        pool = ProcessPoolExecutor(max_workers=args.workers)
        results = pool.map(analyze_trial, tasks, chunksize=1)

    try:
        for result in results:
            totals.update(result["counts"])
            status[result["status"]] += 1
            order = result["order"]
            generated_by_order[order] += 1
            if result["counts"].get("allEll5Graphs", 0):
                all5_by_order[order] += 1
            if result["status"] == "enumerated":
                enumerated_by_order[order] += 1
            row_product = result["rowProduct"]
            if row_product is not None:
                max_row_product = max(max_row_product, row_product)
                if result["status"] == "enumerated":
                    max_enumerated_row_product = max(
                        max_enumerated_row_product, row_product
                    )
            room = FIRST_FALSIFIER_LIMIT - len(first_falsifiers)
            if room > 0:
                first_falsifiers.extend(result["falsifiers"][:room])
    finally:
        if pool is not None:
            pool.shutdown()

    assert totals["generatedGraphs"] == args.trials
    assert totals["connectedGraphs"] == args.trials
    assert totals["triangleFreeGraphs"] == args.trials
    assert totals["oddCycleGraphs"] == args.trials
    assert (
        totals["selectedCutGraphs"] + totals["noSelectedCutGraphs"]
        == args.trials
    )
    assert (
        totals["allEll5Graphs"] + totals["notAllEll5Graphs"]
        == totals["selectedCutGraphs"]
    )
    assert (
        totals["enumeratedGraphs"] + totals["overTupleCapGraphs"]
        == totals["allEll5Graphs"]
    )
    assert (
        totals["matchingPassTuples"] + totals["matchingFailureTuples"]
        == totals["rowTuplesEnumerated"]
    )
    assert (
        totals["failedMatchingsWithVerifiedDescent"] + totals["falsifiers"]
        == totals["matchingFailureTuples"]
    )
    assert sum(status.values()) == args.trials

    payload = {
        "parameters": {
            "seed": args.seed,
            "trials": args.trials,
            "orders": [args.min_order, args.max_order],
            "workers": args.workers,
            "tupleCap": args.tuple_cap,
        },
        "status": dict(sorted(status.items())),
        "counts": {field: totals[field] for field in COUNT_FIELDS},
        "generatedByOrder": {
            str(order): count
            for order, count in sorted(generated_by_order.items())
        },
        "allEll5ByOrder": {
            str(order): count
            for order, count in sorted(all5_by_order.items())
        },
        "enumeratedByOrder": {
            str(order): count
            for order, count in sorted(enumerated_by_order.items())
        },
        "maxCompleteShortestRowProduct": max_row_product,
        "maxEnumeratedShortestRowProduct": max_enumerated_row_product,
        "verdict": "FALSIFIED" if totals["falsifiers"] else "NO_FALSIFIER",
        "firstFalsifiers": first_falsifiers,
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
