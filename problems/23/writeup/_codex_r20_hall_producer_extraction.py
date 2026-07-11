"""Deterministic producer extraction for R20 collision-Hall failures.

The row-reserved matcher has CollisionHalf demands on the left and eligible,
unreserved FreeHalf sources on the right.  This analyzer constructs that
bipartite graph literally, chooses a deterministic maximum matching, and takes
its canonical alternating closure from all unmatched demands.

Each reachable collision half has a blocked same-owner source
``(owner, other, half)``.  If the selected rows containing ``owner`` and
``other`` are ``P_0, ..., P_k``, collision copy ``j`` canonically produces the
row pair ``(P_0, P_{j+1})``.  These are the only producer edges followed by the
extractor.  It then deterministically chooses the minimum exact-delta object
of the first applicable kind:

* A: one producer row is replaced by a shortest row differing on one
  contiguous interval;
* B: one producer-row pair swaps a nonempty set of columns, and both swapped
  rows occur in their original complete shortest-row families.

Thus extraction scans the finite weighted producer closure, not arbitrary
one- or two-coordinate neighbors.  All matching, scores, deltas, and tie
breaks use exact integers.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, deque
from concurrent.futures import ProcessPoolExecutor
from itertools import product, repeat
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _codex_r19_global_base_census import (  # noqa: E402
    dec,
    edge,
    global_candidates,
    graph6_for_orders,
    loads,
    multiplicities,
    owner_demands,
)
from _codex_r20_two_row_exchange_gate import (  # noqa: E402
    obligation_score,
    shortest_row_families,
)


COUNT_FIELDS = (
    "graphs",
    "eligibleGraphs",
    "totalTuples",
    "matchingPassTuples",
    "failedTuples",
    "hallFailureTuples",
    "reservationConflictTuples",
    "contiguousRerouteCertificates",
    "producerTwoCycleCertificates",
    "unextractedFailures",
    "alternatingDemandNodes",
    "alternatingFreeSourceNodes",
    "alternatingHallEdges",
    "producerEdges",
    "contiguousRerouteArcs",
    "validColumnSwapCycles",
)


def empty_counts() -> dict[str, int]:
    return {field: 0 for field in COUNT_FIELDS}


def add_counts(target: dict[str, int], source: dict[str, int]) -> None:
    for field in COUNT_FIELDS:
        target[field] += source.get(field, 0)


def score_state(n: int, info, rows) -> tuple[int, int, tuple[tuple[int, int], ...]]:
    """Return score, collision units, and sorted active edges."""
    count = multiplicities(n, rows)
    collision_units = sum(
        max(0, count[x][y] - 1)
        for x in range(n)
        for y in range(n)
    )
    vertices = {vertex for row in rows for vertex in row}
    support = {
        edge(u, v)
        for row in rows
        for u, v in zip(row, row[1:])
    }
    active = tuple(sorted(
        graph_edge
        for graph_edge in info["Bset"]
        if graph_edge[0] in vertices
        and graph_edge[1] in vertices
        and graph_edge not in support
    ))
    score = 2 * collision_units + 2 * len(active)
    assert score == obligation_score(n, info, rows)
    return score, collision_units, active


def canonical_full_matching(demands, candidates):
    """Deterministic augmenting-path maximum matching."""
    nodes = [
        (owner, index)
        for owner in sorted(demands)
        for index in range(len(demands[owner]))
    ]
    nodes.sort(key=lambda node: (len(candidates[node[0]]), node))
    source_owner = {}
    demand_source = {}

    def augment(node, seen):
        owner, _ = node
        for source in sorted(candidates[owner]):
            if source in seen:
                continue
            seen.add(source)
            previous = source_owner.get(source)
            if previous is None or augment(previous, seen):
                source_owner[source] = node
                demand_source[node] = source
                return True
        return False

    unmatched = []
    for node in nodes:
        if not augment(node, set()):
            unmatched.append(node)
    assert len(demand_source) + len(unmatched) == len(nodes)
    return demand_source, unmatched


def alternating_closure(demands, candidates, matching, unmatched):
    """Canonical Hall closure under unmatched and matched alternating arcs."""
    source_owner = {source: node for node, source in matching.items()}
    roots = tuple(sorted(unmatched))
    left = set(roots)
    right = set()
    left_order = list(roots)
    right_order = []
    demand_parent = {node: None for node in roots}
    demand_depth = {node: 0 for node in roots}
    source_parent = {}
    queue = deque(roots)

    while queue:
        node = queue.popleft()
        owner, _ = node
        matched_source = matching.get(node)
        for source in sorted(candidates[owner]):
            if source == matched_source or source in right:
                continue
            right.add(source)
            right_order.append(source)
            source_parent[source] = node
            next_node = source_owner.get(source)
            if next_node is not None and next_node not in left:
                left.add(next_node)
                left_order.append(next_node)
                demand_parent[next_node] = source
                demand_depth[next_node] = demand_depth[node] + 1
                queue.append(next_node)

    assert len(left) > len(right)
    return {
        "roots": roots,
        "left": left,
        "right": right,
        "leftOrder": tuple(left_order),
        "rightOrder": tuple(right_order),
        "demandParent": demand_parent,
        "demandDepth": demand_depth,
        "sourceParent": source_parent,
    }


def build_hall_instance(n: int, info, rows):
    """Build the literal CollisionHalf-to-FreeHalf matching instance."""
    count = multiplicities(n, rows)
    vertices = set().union(*(set(row) for row in rows)) if rows else set()
    support = {
        edge(u, v)
        for row in rows
        for u, v in zip(row, row[1:])
    }
    active = {
        graph_edge
        for graph_edge in info["Bset"]
        if graph_edge[0] in vertices
        and graph_edge[1] in vertices
        and graph_edge not in support
    }
    reservation_conflicts = tuple(sorted(
        graph_edge for graph_edge in active
        if count[graph_edge[0]][graph_edge[1]] != 0
    ))
    if reservation_conflicts:
        return {
            "status": "reservationConflict",
            "count": count,
            "active": active,
            "reservationConflicts": reservation_conflicts,
        }

    reserved = {
        source
        for u, v in active
        for source in ((u, v, 0), (v, u, 0))
    }
    raw_demands = owner_demands(count, vertices, active)
    demands = {
        owner: [item for item in items if item[0] == "collision"]
        for owner, items in raw_demands.items()
    }
    demands = {owner: items for owner, items in demands.items() if items}
    if not demands:
        return {
            "status": "pass",
            "count": count,
            "active": active,
            "reserved": reserved,
        }

    candidates = {
        owner: {
            source: relation
            for source, relation in global_candidates(
                owner,
                n,
                count,
                info["adj"],
                info["Bset"],
                info["Mset"],
                "row-reserved",
            ).items()
            if source not in reserved
        }
        for owner in demands
    }
    matching, unmatched = canonical_full_matching(demands, candidates)
    if not unmatched:
        return {
            "status": "pass",
            "count": count,
            "active": active,
            "reserved": reserved,
            "demands": demands,
            "candidates": candidates,
            "matching": matching,
        }

    closure = alternating_closure(
        demands, candidates, matching, unmatched
    )
    return {
        "status": "hallFailure",
        "count": count,
        "active": active,
        "reserved": reserved,
        "demands": demands,
        "candidates": candidates,
        "matching": matching,
        "unmatched": tuple(sorted(unmatched)),
        "closure": closure,
    }


def producer_trace(rows, hall):
    """Attach each reachable collision copy to its canonical producer pair."""
    records = []
    pair_order = []
    row_order = []
    pair_seen = set()
    row_seen = set()
    demands = hall["demands"]
    closure = hall["closure"]

    for trace_index, node in enumerate(closure["leftOrder"]):
        collision = demands[node[0]][node[1]]
        kind, owner, other, copy, half = collision
        assert kind == "collision"
        producers = tuple(
            row_index
            for row_index, row in enumerate(rows)
            if owner in row and other in row
        )
        assert len(producers) == hall["count"][owner][other]
        assert len(producers) > copy + 1
        producer_pair = (producers[0], producers[copy + 1])
        record = {
            "traceIndex": trace_index,
            "demandNode": node,
            "incomingFreeSource": closure["demandParent"][node],
            "alternatingDepth": closure["demandDepth"][node],
            "collision": collision,
            "blockedSource": (owner, other, half),
            "pairCount": len(producers),
            "allProducerRows": producers,
            "producerPair": producer_pair,
        }
        records.append(record)
        if producer_pair not in pair_seen:
            pair_seen.add(producer_pair)
            pair_order.append((producer_pair, trace_index))
        for row_index in producer_pair:
            if row_index not in row_seen:
                row_seen.add(row_index)
                row_order.append((row_index, trace_index))

    return {
        "records": records,
        "pairOrder": pair_order,
        "rowOrder": row_order,
    }


def changed_positions(old_row, new_row) -> tuple[int, ...]:
    return tuple(
        position for position in range(5)
        if old_row[position] != new_row[position]
    )


def is_nonempty_contiguous(positions: tuple[int, ...]) -> bool:
    return bool(positions) and positions == tuple(
        range(positions[0], positions[-1] + 1)
    )


def minimum_contiguous_reroute(
    n: int,
    info,
    families,
    choice,
    rows,
    old_state,
    trace,
):
    """Minimum exact-delta contiguous arc in the producer closure."""
    best = None
    examined = 0
    old_score, old_collision, old_active = old_state
    for producer_rank, (row_index, trace_index) in enumerate(trace["rowOrder"]):
        old_row = rows[row_index]
        for replacement, new_row in enumerate(families[row_index]):
            if replacement == choice[row_index]:
                continue
            positions = changed_positions(old_row, new_row)
            if not is_nonempty_contiguous(positions):
                continue
            examined += 1
            new_rows = list(rows)
            new_rows[row_index] = new_row
            new_state = score_state(n, info, tuple(new_rows))
            delta = new_state[0] - old_score
            candidate = {
                "kind": "contiguousReroute",
                "producerRank": producer_rank,
                "producerTraceIndex": trace_index,
                "rowIndex": row_index,
                "replacement": replacement,
                "changedPositions": positions,
                "oldRow": old_row,
                "newRow": new_row,
                "oldScore": old_score,
                "newScore": new_state[0],
                "scoreDelta": delta,
                "collisionDelta": new_state[1] - old_collision,
                "activeDelta": len(new_state[2]) - len(old_active),
            }
            key = (
                delta,
                producer_rank,
                len(positions),
                positions,
                new_row,
                replacement,
            )
            if best is None or key < best[0]:
                best = (key, candidate)
    return (None if best is None else best[1]), examined


def minimum_producer_two_cycle(
    n: int,
    info,
    families,
    family_index,
    choice,
    rows,
    old_state,
    trace,
):
    """Minimum exact-delta valid column swap on a producer-row 2-cycle."""
    best = None
    valid_cycles = 0
    old_score, old_collision, old_active = old_state
    for pair_rank, ((left, right), trace_index) in enumerate(trace["pairOrder"]):
        old_left = rows[left]
        old_right = rows[right]
        differing = tuple(
            position for position in range(5)
            if old_left[position] != old_right[position]
        )
        for submask in range(1, 1 << len(differing)):
            positions = tuple(
                position
                for bit, position in enumerate(differing)
                if (submask >> bit) & 1
            )
            new_left = tuple(
                old_right[position] if position in positions
                else old_left[position]
                for position in range(5)
            )
            new_right = tuple(
                old_left[position] if position in positions
                else old_right[position]
                for position in range(5)
            )
            left_replacement = family_index[left].get(new_left)
            right_replacement = family_index[right].get(new_right)
            if left_replacement is None or right_replacement is None:
                continue
            valid_cycles += 1
            new_rows = list(rows)
            new_rows[left] = new_left
            new_rows[right] = new_right
            new_state = score_state(n, info, tuple(new_rows))
            delta = new_state[0] - old_score
            candidate = {
                "kind": "producerTwoCycle",
                "producerPairRank": pair_rank,
                "producerTraceIndex": trace_index,
                "leftRowIndex": left,
                "rightRowIndex": right,
                "leftReplacement": left_replacement,
                "rightReplacement": right_replacement,
                "swappedPositions": positions,
                "oldLeftRow": old_left,
                "oldRightRow": old_right,
                "newLeftRow": new_left,
                "newRightRow": new_right,
                "oldScore": old_score,
                "newScore": new_state[0],
                "scoreDelta": delta,
                "collisionDelta": new_state[1] - old_collision,
                "activeDelta": len(new_state[2]) - len(old_active),
            }
            key = (
                delta,
                pair_rank,
                len(positions),
                positions,
                left_replacement,
                right_replacement,
            )
            if best is None or key < best[0]:
                best = (key, candidate)
    return (None if best is None else best[1]), valid_cycles


def extract_certificate(n: int, info, families, family_index, choice, rows, hall):
    """Run the deterministic A-before-B producer extraction rule."""
    old_state = score_state(n, info, rows)
    trace = producer_trace(rows, hall)
    reroute, reroute_count = minimum_contiguous_reroute(
        n, info, families, choice, rows, old_state, trace
    )
    two_cycle, cycle_count = minimum_producer_two_cycle(
        n,
        info,
        families,
        family_index,
        choice,
        rows,
        old_state,
        trace,
    )

    if reroute is not None and reroute["scoreDelta"] < 0:
        certificate = reroute
    elif two_cycle is not None and two_cycle["scoreDelta"] < 0:
        certificate = two_cycle
    else:
        certificate = None

    return {
        "oldState": old_state,
        "trace": trace,
        "bestContiguousReroute": reroute,
        "bestProducerTwoCycle": two_cycle,
        "contiguousRerouteArcs": reroute_count,
        "validColumnSwapCycles": cycle_count,
        "certificate": certificate,
    }


def missing_state(extraction) -> str:
    reroute = extraction["bestContiguousReroute"]
    cycle = extraction["bestProducerTwoCycle"]
    if reroute is None and cycle is None:
        return "producer closure has no contiguous reroute or valid column swap"
    if reroute is None:
        return "valid producer column swaps exist, but all have nonnegative score delta"
    if cycle is None:
        return "contiguous producer reroutes exist, but all have nonnegative score delta"
    return "all contiguous producer reroutes and valid producer column swaps have nonnegative score delta"


def render_hall_failure(hall) -> dict:
    closure = hall["closure"]
    source_owner = {
        source: node for node, source in hall["matching"].items()
    }
    demand_rows = []
    for node in closure["leftOrder"]:
        owner, index = node
        demand_rows.append({
            "node": node,
            "collision": hall["demands"][owner][index],
            "candidateCount": len(hall["candidates"][owner]),
            "incomingFreeSource": closure["demandParent"][node],
            "alternatingDepth": closure["demandDepth"][node],
        })
    source_rows = []
    for source in closure["rightOrder"]:
        parent = closure["sourceParent"][source]
        source_rows.append({
            "source": source,
            "fromDemand": parent,
            "relation": hall["candidates"][parent[0]][source],
            "matchedDemand": source_owner.get(source),
        })
    return {
        "demandCount": sum(map(len, hall["demands"].values())),
        "freeSourceCount": len(set().union(*(
            set(sources) for sources in hall["candidates"].values()
        ))),
        "matched": len(hall["matching"]),
        "unmatched": hall["unmatched"],
        "hallLeft": len(closure["left"]),
        "hallRight": len(closure["right"]),
        "hallDeficiency": len(closure["left"]) - len(closure["right"]),
        "reachableDemands": demand_rows,
        "reachableFreeSources": source_rows,
    }


def falsifier_payload(g6: str, n: int, info, families, choice, rows, hall, extraction):
    old_score, old_collision, old_active = extraction["oldState"]
    return {
        "g6": g6,
        "order": n,
        "edges": sorted(info["Bset"] | info["Mset"]),
        "side": info["side"],
        "badEdges": info["M"],
        "familySizes": [len(family) for family in families],
        "rowChoice": choice,
        "rows": rows,
        "obligationScore": old_score,
        "collisionUnits": old_collision,
        "activeEdges": old_active,
        "missingState": missing_state(extraction),
        "hall": render_hall_failure(hall),
        "producerTrace": extraction["trace"]["records"],
        "bestContiguousReroute": extraction["bestContiguousReroute"],
        "bestProducerTwoCycle": extraction["bestProducerTwoCycle"],
    }


def reservation_falsifier(g6: str, n: int, info, families, choice, rows, hall):
    state = score_state(n, info, rows)
    return {
        "g6": g6,
        "order": n,
        "edges": sorted(info["Bset"] | info["Mset"]),
        "side": info["side"],
        "badEdges": info["M"],
        "familySizes": [len(family) for family in families],
        "rowChoice": choice,
        "rows": rows,
        "obligationScore": state[0],
        "collisionUnits": state[1],
        "activeEdges": state[2],
        "missingState": "reserved active-hit source is not a FreeHalf",
        "reservationConflicts": hall["reservationConflicts"],
    }


def analyze_graph(g6: str):
    n, graph_edges = dec(g6)
    info = loads(n, graph_edges)
    counts = empty_counts()
    counts["graphs"] = 1
    if info is None:
        return {
            "status": "skipNoCut",
            "order": n,
            "counts": counts,
            "signatures": Counter(),
            "firstFalsifier": None,
        }
    if any(length != 5 for length in info["ell"].values()):
        return {
            "status": "skipNotAll5",
            "order": n,
            "counts": counts,
            "signatures": Counter(),
            "firstFalsifier": None,
        }

    counts["eligibleGraphs"] = 1
    families = shortest_row_families(info)
    family_index = tuple(
        {row: index for index, row in enumerate(family)}
        for family in families
    )
    assert all(
        len(index) == len(family)
        for index, family in zip(family_index, families)
    )
    signatures = Counter()
    first_falsifier = None

    for choice in product(*(range(len(family)) for family in families)):
        counts["totalTuples"] += 1
        rows = tuple(
            families[index][row_index]
            for index, row_index in enumerate(choice)
        )
        hall = build_hall_instance(n, info, rows)
        if hall["status"] == "pass":
            counts["matchingPassTuples"] += 1
            continue

        counts["failedTuples"] += 1
        if hall["status"] == "reservationConflict":
            counts["reservationConflictTuples"] += 1
            counts["unextractedFailures"] += 1
            if first_falsifier is None:
                first_falsifier = reservation_falsifier(
                    g6, n, info, families, choice, rows, hall
                )
            continue

        assert hall["status"] == "hallFailure"
        counts["hallFailureTuples"] += 1
        closure = hall["closure"]
        counts["alternatingDemandNodes"] += len(closure["left"])
        counts["alternatingFreeSourceNodes"] += len(closure["right"])
        counts["alternatingHallEdges"] += sum(
            len(hall["candidates"][node[0]])
            for node in closure["left"]
        )

        extraction = extract_certificate(
            n, info, families, family_index, choice, rows, hall
        )
        counts["producerEdges"] += 2 * len(
            extraction["trace"]["records"]
        )
        counts["contiguousRerouteArcs"] += extraction[
            "contiguousRerouteArcs"
        ]
        counts["validColumnSwapCycles"] += extraction[
            "validColumnSwapCycles"
        ]
        certificate = extraction["certificate"]
        if certificate is None:
            counts["unextractedFailures"] += 1
            if first_falsifier is None:
                first_falsifier = falsifier_payload(
                    g6,
                    n,
                    info,
                    families,
                    choice,
                    rows,
                    hall,
                    extraction,
                )
            continue

        signature = (
            certificate["kind"],
            tuple(certificate.get(
                "changedPositions",
                certificate.get("swappedPositions", ()),
            )),
            certificate["collisionDelta"],
            certificate["activeDelta"],
            certificate["scoreDelta"],
        )
        signatures[signature] += 1
        if certificate["kind"] == "contiguousReroute":
            counts["contiguousRerouteCertificates"] += 1
        else:
            assert certificate["kind"] == "producerTwoCycle"
            counts["producerTwoCycleCertificates"] += 1

    assert counts["totalTuples"] == (
        counts["matchingPassTuples"] + counts["failedTuples"]
    )
    assert counts["failedTuples"] == (
        counts["hallFailureTuples"] + counts["reservationConflictTuples"]
    )
    assert counts["failedTuples"] == (
        counts["contiguousRerouteCertificates"]
        + counts["producerTwoCycleCertificates"]
        + counts["unextractedFailures"]
    )
    return {
        "status": "eligible",
        "order": n,
        "counts": counts,
        "signatures": signatures,
        "firstFalsifier": first_falsifier,
    }


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-order", type=positive_int, default=5)
    parser.add_argument("--max-order", type=positive_int, default=11)
    parser.add_argument(
        "--workers",
        type=positive_int,
        default=min(61, os.cpu_count() or 1),
    )
    parser.add_argument(
        "--graph6",
        action="append",
        default=[],
        help="test this graph6 fixture instead of generating an order range; repeatable",
    )
    args = parser.parse_args()
    if args.min_order > args.max_order:
        parser.error("--min-order must not exceed --max-order")
    if args.workers > 61:
        parser.error("--workers must not exceed 61")
    return args


def render_signature(signature, count: int) -> dict:
    kind, positions, collision_delta, active_delta, score_delta = signature
    return {
        "kind": kind,
        "positions": positions,
        "collisionDelta": collision_delta,
        "activeDelta": active_delta,
        "scoreDelta": score_delta,
        "count": count,
    }


def main() -> None:
    args = parse_args()
    if args.graph6:
        graph6 = args.graph6
        generated = dict(sorted(Counter(dec(g6)[0] for g6 in graph6).items()))
        tested_orders = [min(generated), max(generated)]
    else:
        graph6, generated = graph6_for_orders(
            args.min_order, args.max_order
        )
        tested_orders = [args.min_order, args.max_order]

    aggregate = empty_counts()
    by_order = {}
    status = Counter()
    signatures = Counter()
    first_falsifier = None

    if args.workers == 1:
        results = map(analyze_graph, graph6)
        pool = None
    else:
        pool = ProcessPoolExecutor(max_workers=args.workers)
        results = pool.map(analyze_graph, graph6, chunksize=8)

    try:
        for result in results:
            status[result["status"]] += 1
            add_counts(aggregate, result["counts"])
            order_counts = by_order.setdefault(result["order"], empty_counts())
            add_counts(order_counts, result["counts"])
            signatures.update(result["signatures"])
            if first_falsifier is None and result["firstFalsifier"] is not None:
                first_falsifier = result["firstFalsifier"]
    finally:
        if pool is not None:
            pool.shutdown()

    payload = {
        "orders": tested_orders,
        "workers": args.workers,
        "fixtureMode": bool(args.graph6),
        "generatedByOrder": {
            str(order): count for order, count in sorted(generated.items())
        },
        "status": dict(sorted(status.items())),
        "extractionRule": (
            "canonical alternating Hall closure; collision copy j maps to "
            "producer rows P0,P(j+1); minimum exact-delta contiguous arc, "
            "else minimum exact-delta valid column-swap 2-cycle"
        ),
        **aggregate,
        "byOrder": {
            str(order): counts for order, counts in sorted(by_order.items())
        },
        "certificateSignatures": [
            render_signature(signature, count)
            for signature, count in sorted(signatures.items())
        ],
        "firstFalsifier": first_falsifier,
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
