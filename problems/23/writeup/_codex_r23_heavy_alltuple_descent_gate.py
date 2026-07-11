"""Exact tuple-sharded Hall/descent gate for the order-12 heavy tail.

Pass one identifies eligible all-ell=5 graphs whose row-choice product is
above a requested threshold.  Pass two partitions every such mixed-radix row
space into bounded chunks.  Each positive-demand tuple is checked by exact
integer owner flow; every Hall failure is checked against every Hamming-one
row replacement for a strict active-scoped score descent.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from fractions import Fraction

from _codex_r19_global_base_census import dec, graph6_for_orders, loads
from _codex_r20_two_row_exchange_gate import multiplicities, shortest_row_families
from _codex_r23_order12_preflight import inspect
from _codex_scoped_variation_anatomy import (
    component_transport_flow,
    owner_shore_source_count,
    scoped_state,
)
from _codex_r23_outside_attachment_full_obligation_gate import (
    active_scoped_obligation_parts,
    active_scoped_obligation_score,
    full_owner_flow,
)


@lru_cache(maxsize=4)
def graph_context(g6):
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None or any(length != 5 for length in info["ell"].values()):
        raise ValueError("ineligible graph reached heavy tuple pass")
    families = shortest_row_families(info)
    sizes = tuple(len(family) for family in families)
    return n, info, families, sizes


def choice_at(index, sizes):
    values = [0] * len(sizes)
    for position in range(len(sizes) - 1, -1, -1):
        values[position] = index % sizes[position]
        index //= sizes[position]
    assert index == 0
    return tuple(values)


def rows_for_choice(families, choice):
    return tuple(families[i][choice[i]] for i in range(len(choice)))


def scoped_score(n, info, rows):
    return active_scoped_obligation_score(
        n, set(info["Bset"]), set(info["Mset"]), rows
    )


def scoped_parts(n, info, rows):
    return active_scoped_obligation_parts(
        n, set(info["Bset"]), set(info["Mset"]), rows
    )


def raw_collision_score(n, rows):
    count = multiplicities(n, rows)
    return 2 * sum(
        max(0, count[x][y] - 1)
        for x in range(n)
        for y in range(n)
    )


def analyze_chunk(task):
    g6, start, stop = task
    n, info, families, sizes = graph_context(g6)
    checked = 0
    positive = 0
    failures = 0
    descents = 0
    no_descent = 0
    negative_delta_sum = 0
    nonnegative_delta_sum = 0
    variation_deficiency_bound_failures = 0
    variation_alternative_deficiency_bound_failures = 0
    collision_alternative_deficiency_bound_failures = 0
    positive_hitneed_variation = 0
    coordinate_collision_deficiency_bound_failures = 0
    positive_coordinate_hitneed_variation = 0
    coordinate_raw_collision_deficiency_bound_failures = 0
    component_transport_failures = 0
    min_negative_variation_per_deficiency = None
    min_normalized_ratio = None
    min_normalized_record = None
    first_failure = None
    first_no_descent = None
    first_nonnegative_delta_sum = None
    first_variation_deficiency_bound_failure = None
    first_variation_alternative_deficiency_bound_failure = None
    first_collision_alternative_deficiency_bound_failure = None
    first_positive_hitneed_variation = None
    first_coordinate_collision_deficiency_bound_failure = None
    first_positive_coordinate_hitneed_variation = None
    first_coordinate_raw_collision_deficiency_bound_failure = None
    first_component_transport_failure = None
    for tuple_index in range(start, stop):
        checked += 1
        choice = choice_at(tuple_index, sizes)
        rows = rows_for_choice(families, choice)
        old_collision, old_hitneed = scoped_parts(n, info, rows)
        old_raw_collision = raw_collision_score(n, rows)
        score = old_collision + old_hitneed
        if score == 0:
            continue
        positive += 1
        flow = full_owner_flow(
            n,
            set(info["Bset"]),
            set(info["Mset"]),
            rows,
            g6,
            require_full=False,
            quiet=True,
            scope="active",
            include_outside=False,
        )
        if flow["full"]:
            continue
        failures += 1
        old_state = scoped_state(
            n, set(info["Bset"]), set(info["Mset"]), rows
        )
        _, source_by_owner, source_capacities = owner_shore_source_count(
            n,
            set(info["Bset"]),
            set(info["Mset"]),
            old_state,
            flow["deficientOwners"],
        )
        deficient_owner_set = set(flow["deficientOwners"])
        best = score
        witness = None
        delta_sum = 0
        collision_delta_sum = 0
        hitneed_delta_sum = 0
        coordinate_collision_failures = []
        coordinate_hitneed_positive = []
        coordinate_raw_collision_failures = []
        coordinate_transport_failures = []
        for index, family in enumerate(families):
            coordinate_collision_delta = 0
            coordinate_hitneed_delta = 0
            coordinate_raw_collision_delta = 0
            coordinate_states = []
            coordinate_rows = []
            for replacement, replacement_row in enumerate(family):
                if replacement == choice[index]:
                    continue
                new_rows = rows[:index] + (replacement_row,) + rows[index + 1:]
                new_collision, new_hitneed = scoped_parts(n, info, new_rows)
                new_raw_collision = raw_collision_score(n, new_rows)
                coordinate_states.append(
                    scoped_state(
                        n, set(info["Bset"]), set(info["Mset"]), new_rows
                    )
                )
                coordinate_rows.append(replacement_row)
                new_score = new_collision + new_hitneed
                delta_sum += new_score - score
                collision_delta_sum += new_collision - old_collision
                hitneed_delta_sum += new_hitneed - old_hitneed
                coordinate_collision_delta += new_collision - old_collision
                coordinate_hitneed_delta += new_hitneed - old_hitneed
                coordinate_raw_collision_delta += (
                    new_raw_collision - old_raw_collision
                )
                if new_score < best:
                    best = new_score
                    witness = {
                        "changedRow": index,
                        "replacement": replacement,
                        "oldRow": list(rows[index]),
                        "newRow": list(replacement_row),
                        "newScore": new_score,
                    }
            coordinate_bound = -(len(family) - 1) * flow["deficiency"]
            if coordinate_collision_delta > coordinate_bound:
                coordinate_collision_failures.append({
                    "index": index,
                    "familySize": len(family),
                    "collisionDelta": coordinate_collision_delta,
                    "bound": coordinate_bound,
                })
            if coordinate_hitneed_delta > 0:
                coordinate_hitneed_positive.append({
                    "index": index,
                    "familySize": len(family),
                    "hitNeedDelta": coordinate_hitneed_delta,
                })
            if coordinate_raw_collision_delta > coordinate_bound:
                coordinate_raw_collision_failures.append({
                    "index": index,
                    "familySize": len(family),
                    "rawCollisionDelta": coordinate_raw_collision_delta,
                    "bound": coordinate_bound,
                })
            transport = component_transport_flow(
                old_state,
                deficient_owner_set,
                source_by_owner,
                source_capacities,
                coordinate_states,
                rows[index],
                coordinate_rows,
            )
            if transport["gap"]:
                coordinate_transport_failures.append({
                    "index": index,
                    "familySize": len(family),
                    "transport": transport,
                })
        record = {
            "g6": g6,
            "tupleIndex": tuple_index,
            "choice": list(choice),
            "rows": [list(row) for row in rows],
            "score": score,
            "flow": flow,
            "bestNeighborScore": best,
            "deltaSum": delta_sum,
            "collisionDeltaSum": collision_delta_sum,
            "hitNeedDeltaSum": hitneed_delta_sum,
            "coordinateCollisionFailures": coordinate_collision_failures,
            "positiveCoordinateHitNeed": coordinate_hitneed_positive,
            "coordinateRawCollisionFailures":
                coordinate_raw_collision_failures,
            "coordinateTransportFailures": coordinate_transport_failures,
            "descent": witness,
        }
        if first_failure is None:
            first_failure = record
        if best < score:
            descents += 1
        else:
            no_descent += 1
            if first_no_descent is None:
                first_no_descent = record
        if delta_sum < 0:
            negative_delta_sum += 1
        else:
            nonnegative_delta_sum += 1
            if first_nonnegative_delta_sum is None:
                first_nonnegative_delta_sum = record
        ratio = Fraction(-delta_sum, flow["deficiency"])
        if (
            min_negative_variation_per_deficiency is None
            or ratio < min_negative_variation_per_deficiency
        ):
            min_negative_variation_per_deficiency = ratio
        if delta_sum > -flow["deficiency"]:
            variation_deficiency_bound_failures += 1
            if first_variation_deficiency_bound_failure is None:
                first_variation_deficiency_bound_failure = record
        alternative_count = sum(size - 1 for size in sizes)
        normalized_ratio = Fraction(
            -delta_sum, flow["deficiency"] * alternative_count
        )
        if min_normalized_ratio is None or normalized_ratio < min_normalized_ratio:
            min_normalized_ratio = normalized_ratio
            min_normalized_record = record
        if delta_sum > -flow["deficiency"] * alternative_count:
            variation_alternative_deficiency_bound_failures += 1
            if first_variation_alternative_deficiency_bound_failure is None:
                first_variation_alternative_deficiency_bound_failure = record
        if collision_delta_sum > -flow["deficiency"] * alternative_count:
            collision_alternative_deficiency_bound_failures += 1
            if first_collision_alternative_deficiency_bound_failure is None:
                first_collision_alternative_deficiency_bound_failure = record
        if hitneed_delta_sum > 0:
            positive_hitneed_variation += 1
            if first_positive_hitneed_variation is None:
                first_positive_hitneed_variation = record
        if coordinate_collision_failures:
            coordinate_collision_deficiency_bound_failures += 1
            if first_coordinate_collision_deficiency_bound_failure is None:
                first_coordinate_collision_deficiency_bound_failure = record
        if coordinate_hitneed_positive:
            positive_coordinate_hitneed_variation += 1
            if first_positive_coordinate_hitneed_variation is None:
                first_positive_coordinate_hitneed_variation = record
        if coordinate_raw_collision_failures:
            coordinate_raw_collision_deficiency_bound_failures += 1
            if first_coordinate_raw_collision_deficiency_bound_failure is None:
                first_coordinate_raw_collision_deficiency_bound_failure = record
        if coordinate_transport_failures:
            component_transport_failures += 1
            if first_component_transport_failure is None:
                first_component_transport_failure = record
    return {
        "checked": checked,
        "positive": positive,
        "failures": failures,
        "descents": descents,
        "noDescent": no_descent,
        "negativeDeltaSum": negative_delta_sum,
        "nonnegativeDeltaSum": nonnegative_delta_sum,
        "variationDeficiencyBoundFailures": variation_deficiency_bound_failures,
        "variationAlternativeDeficiencyBoundFailures":
            variation_alternative_deficiency_bound_failures,
        "collisionAlternativeDeficiencyBoundFailures":
            collision_alternative_deficiency_bound_failures,
        "positiveHitNeedVariation": positive_hitneed_variation,
        "coordinateCollisionDeficiencyBoundFailures":
            coordinate_collision_deficiency_bound_failures,
        "positiveCoordinateHitNeedVariation":
            positive_coordinate_hitneed_variation,
        "coordinateRawCollisionDeficiencyBoundFailures":
            coordinate_raw_collision_deficiency_bound_failures,
        "componentTransportFailures": component_transport_failures,
        "minRatio": (
            None if min_negative_variation_per_deficiency is None else
            [
                min_negative_variation_per_deficiency.numerator,
                min_negative_variation_per_deficiency.denominator,
            ]
        ),
        "minNormalizedRatio": (
            None if min_normalized_ratio is None else
            [min_normalized_ratio.numerator, min_normalized_ratio.denominator]
        ),
        "minNormalizedRecord": min_normalized_record,
        "firstFailure": first_failure,
        "firstNoDescent": first_no_descent,
        "firstNonnegativeDeltaSum": first_nonnegative_delta_sum,
        "firstVariationDeficiencyBoundFailure":
            first_variation_deficiency_bound_failure,
        "firstVariationAlternativeDeficiencyBoundFailure":
            first_variation_alternative_deficiency_bound_failure,
        "firstCollisionAlternativeDeficiencyBoundFailure":
            first_collision_alternative_deficiency_bound_failure,
        "firstPositiveHitNeedVariation": first_positive_hitneed_variation,
        "firstCoordinateCollisionDeficiencyBoundFailure":
            first_coordinate_collision_deficiency_bound_failure,
        "firstPositiveCoordinateHitNeedVariation":
            first_positive_coordinate_hitneed_variation,
        "firstCoordinateRawCollisionDeficiencyBoundFailure":
            first_coordinate_raw_collision_deficiency_bound_failure,
        "firstComponentTransportFailure": first_component_transport_failure,
    }


def positive(value):
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--order", type=positive, default=12)
    parser.add_argument("--min-product", type=positive, default=4097)
    parser.add_argument("--max-product", type=int, default=0)
    parser.add_argument("--chunk", type=positive, default=2048)
    parser.add_argument("--workers", type=positive, default=min(61, os.cpu_count() or 1))
    parser.add_argument("--expected-tuples", type=int, default=0)
    args = parser.parse_args()
    if args.workers > 61:
        parser.error("Windows ProcessPoolExecutor supports at most 61 workers")

    graph6, generated = graph6_for_orders(args.order, args.order)
    status = Counter()
    heavy = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for kind, g6, count, sizes, bads in pool.map(inspect, graph6, chunksize=64):
            status[kind] += 1
            if (
                kind == "eligible"
                and count >= args.min_product
                and (not args.max_product or count <= args.max_product)
            ):
                heavy.append((g6, count, sizes, bads))
    heavy.sort(key=lambda item: (-item[1], item[0]))
    heavy_tuples = sum(item[1] for item in heavy)
    if args.expected_tuples:
        assert heavy_tuples == args.expected_tuples

    tasks = []
    for g6, total, _, _ in heavy:
        tasks.extend(
            (g6, start, min(total, start + args.chunk))
            for start in range(0, total, args.chunk)
        )

    aggregate = Counter()
    first_failure = None
    first_no_descent = None
    first_nonnegative_delta_sum = None
    first_variation_deficiency_bound_failure = None
    first_variation_alternative_deficiency_bound_failure = None
    first_collision_alternative_deficiency_bound_failure = None
    first_positive_hitneed_variation = None
    first_coordinate_collision_deficiency_bound_failure = None
    first_positive_coordinate_hitneed_variation = None
    first_coordinate_raw_collision_deficiency_bound_failure = None
    first_component_transport_failure = None
    min_ratio = None
    min_normalized_ratio = None
    min_normalized_record = None
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(analyze_chunk, tasks, chunksize=1):
            aggregate["checked"] += result["checked"]
            aggregate["positive"] += result["positive"]
            aggregate["failures"] += result["failures"]
            aggregate["descents"] += result["descents"]
            aggregate["noDescent"] += result["noDescent"]
            aggregate["negativeDeltaSum"] += result["negativeDeltaSum"]
            aggregate["nonnegativeDeltaSum"] += result["nonnegativeDeltaSum"]
            aggregate["variationDeficiencyBoundFailures"] += (
                result["variationDeficiencyBoundFailures"]
            )
            aggregate["variationAlternativeDeficiencyBoundFailures"] += (
                result["variationAlternativeDeficiencyBoundFailures"]
            )
            aggregate["collisionAlternativeDeficiencyBoundFailures"] += (
                result["collisionAlternativeDeficiencyBoundFailures"]
            )
            aggregate["positiveHitNeedVariation"] += (
                result["positiveHitNeedVariation"]
            )
            aggregate["coordinateCollisionDeficiencyBoundFailures"] += (
                result["coordinateCollisionDeficiencyBoundFailures"]
            )
            aggregate["positiveCoordinateHitNeedVariation"] += (
                result["positiveCoordinateHitNeedVariation"]
            )
            aggregate["coordinateRawCollisionDeficiencyBoundFailures"] += (
                result["coordinateRawCollisionDeficiencyBoundFailures"]
            )
            aggregate["componentTransportFailures"] += (
                result["componentTransportFailures"]
            )
            if result["minRatio"] is not None:
                ratio = Fraction(*result["minRatio"])
                if min_ratio is None or ratio < min_ratio:
                    min_ratio = ratio
            if result["minNormalizedRatio"] is not None:
                ratio = Fraction(*result["minNormalizedRatio"])
                if min_normalized_ratio is None or ratio < min_normalized_ratio:
                    min_normalized_ratio = ratio
                    min_normalized_record = result["minNormalizedRecord"]
            if first_failure is None and result["firstFailure"] is not None:
                first_failure = result["firstFailure"]
            if first_no_descent is None and result["firstNoDescent"] is not None:
                first_no_descent = result["firstNoDescent"]
            if (
                first_nonnegative_delta_sum is None
                and result["firstNonnegativeDeltaSum"] is not None
            ):
                first_nonnegative_delta_sum = result["firstNonnegativeDeltaSum"]
            if (
                first_variation_deficiency_bound_failure is None
                and result["firstVariationDeficiencyBoundFailure"] is not None
            ):
                first_variation_deficiency_bound_failure = (
                    result["firstVariationDeficiencyBoundFailure"]
                )
            if (
                first_variation_alternative_deficiency_bound_failure is None
                and result["firstVariationAlternativeDeficiencyBoundFailure"]
                is not None
            ):
                first_variation_alternative_deficiency_bound_failure = (
                    result["firstVariationAlternativeDeficiencyBoundFailure"]
                )
            if (
                first_collision_alternative_deficiency_bound_failure is None
                and result["firstCollisionAlternativeDeficiencyBoundFailure"]
                is not None
            ):
                first_collision_alternative_deficiency_bound_failure = (
                    result["firstCollisionAlternativeDeficiencyBoundFailure"]
                )
            if (
                first_positive_hitneed_variation is None
                and result["firstPositiveHitNeedVariation"] is not None
            ):
                first_positive_hitneed_variation = (
                    result["firstPositiveHitNeedVariation"]
                )
            if (
                first_coordinate_collision_deficiency_bound_failure is None
                and result["firstCoordinateCollisionDeficiencyBoundFailure"]
                is not None
            ):
                first_coordinate_collision_deficiency_bound_failure = (
                    result["firstCoordinateCollisionDeficiencyBoundFailure"]
                )
            if (
                first_positive_coordinate_hitneed_variation is None
                and result["firstPositiveCoordinateHitNeedVariation"] is not None
            ):
                first_positive_coordinate_hitneed_variation = (
                    result["firstPositiveCoordinateHitNeedVariation"]
                )
            if (
                first_coordinate_raw_collision_deficiency_bound_failure is None
                and result["firstCoordinateRawCollisionDeficiencyBoundFailure"]
                is not None
            ):
                first_coordinate_raw_collision_deficiency_bound_failure = (
                    result["firstCoordinateRawCollisionDeficiencyBoundFailure"]
                )
            if (
                first_component_transport_failure is None
                and result["firstComponentTransportFailure"] is not None
            ):
                first_component_transport_failure = (
                    result["firstComponentTransportFailure"]
                )
    assert aggregate["checked"] == heavy_tuples
    assert aggregate["failures"] == aggregate["descents"] + aggregate["noDescent"]
    assert aggregate["failures"] == (
        aggregate["negativeDeltaSum"] + aggregate["nonnegativeDeltaSum"]
    )

    payload = {
        "order": args.order,
        "workers": args.workers,
        "chunk": args.chunk,
        "minProduct": args.min_product,
        "maxProduct": args.max_product,
        "generatedGraphs": generated,
        "status": dict(sorted(status.items())),
        "heavyGraphs": len(heavy),
        "heavyTuples": heavy_tuples,
        "chunks": len(tasks),
        **dict(aggregate),
        "firstFailure": first_failure,
        "firstNoDescent": first_no_descent,
        "firstNonnegativeDeltaSum": first_nonnegative_delta_sum,
        "firstVariationDeficiencyBoundFailure":
            first_variation_deficiency_bound_failure,
        "firstVariationAlternativeDeficiencyBoundFailure":
            first_variation_alternative_deficiency_bound_failure,
        "firstCollisionAlternativeDeficiencyBoundFailure":
            first_collision_alternative_deficiency_bound_failure,
        "firstPositiveHitNeedVariation": first_positive_hitneed_variation,
        "firstCoordinateCollisionDeficiencyBoundFailure":
            first_coordinate_collision_deficiency_bound_failure,
        "firstPositiveCoordinateHitNeedVariation":
            first_positive_coordinate_hitneed_variation,
        "firstCoordinateRawCollisionDeficiencyBoundFailure":
            first_coordinate_raw_collision_deficiency_bound_failure,
        "firstComponentTransportFailure": first_component_transport_failure,
        "minNegativeVariationPerDeficiency": (
            None if min_ratio is None else [min_ratio.numerator, min_ratio.denominator]
        ),
        "minNormalizedRatio": (
            None if min_normalized_ratio is None else
            [min_normalized_ratio.numerator, min_normalized_ratio.denominator]
        ),
        "minNormalizedRecord": min_normalized_record,
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 1 if aggregate["noDescent"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
