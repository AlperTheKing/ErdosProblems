#!/usr/bin/env python3
"""Exact falsifier gate for cut-independent image-shell charges.

At a cutoff X, a static fractional charge assigns one unit from each hard
root to nonhard roots, with capacity one at every target.  A charge h -> r
is admissible only when every one-step image in which h is unhealed also
heals r.  This script synthesizes that universal-implication graph by CEGIS.

Every rejected edge is accompanied by a concrete forward-closed source.
If the remaining supergraph has a Hall deficit, an exact set-cover solve
minimizes the concrete witnesses needed to certify all crossing nonedges.
The verifier replays those witnesses without invoking a solver.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

from ortools.sat.python import cp_model


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


def admissible_pairs(value: int) -> list[tuple[int, int]]:
    product = value + 1
    result: list[tuple[int, int]] = []
    for left in range(2, math.isqrt(product) + 1):
        if product % left:
            continue
        right = product // left
        if left < right and allowed(left) and allowed(right):
            result.append((left, right))
    return result


def hard_shape(value: int, pairs: list[tuple[int, int]]) -> bool:
    if value % 2 or not pairs:
        return False
    if (value + 1) % 3:
        return True
    parent = (value + 1) // 3
    return not (allowed(parent) and parent != 3)


def chain_top(root: int, cutoff: int) -> int:
    value = root
    while 2 * value - 1 <= cutoff:
        value = 2 * value - 1
    return value


def grounded_set(
    values: list[int], pairs: dict[int, list[tuple[int, int]]]
) -> set[int]:
    generated = {2, 3}
    for value in values:
        if value in generated:
            continue
        if any(left in generated and right in generated for left, right in pairs[value]):
            generated.add(value)
    return generated


def support_image(
    source: set[int], values: list[int], pairs: dict[int, list[tuple[int, int]]]
) -> set[int]:
    image = {2, 3}
    for value in values:
        if value in image:
            continue
        if any(left in source and right in source for left, right in pairs[value]):
            image.add(value)
    return image


def forward_closed(
    source: set[int], values: list[int], pairs: dict[int, list[tuple[int, int]]]
) -> bool:
    if not {2, 3}.issubset(source):
        return False
    return all(
        value in source
        for value in values
        for left, right in pairs[value]
        if left in source and right in source
    )


def shell_sets(
    image: set[int],
    hard_roots: list[int],
    target_roots: list[int],
    cutoff: int,
) -> tuple[set[int], set[int]]:
    unhealed = {
        root for root in hard_roots if chain_top(root, cutoff) not in image
    }
    healed = {
        root
        for root in target_roots
        if root not in image and chain_top(root, cutoff) in image
    }
    return unhealed, healed


@dataclass
class ImageModel:
    cutoff: int
    values: list[int]
    pairs: dict[int, list[tuple[int, int]]]
    generated: set[int]
    hard_roots: list[int]
    target_roots: list[int]
    model: cp_model.CpModel
    source: dict[int, cp_model.IntVar]
    image: dict[int, cp_model.IntVar]
    healed: dict[int, cp_model.IntVar]


def and_var(
    model: cp_model.CpModel,
    left: cp_model.IntVar,
    right: cp_model.IntVar,
    name: str,
) -> cp_model.IntVar:
    result = model.new_bool_var(name)
    model.add(result <= left)
    model.add(result <= right)
    model.add(result >= left + right - 1)
    return result


def build_model(cutoff: int) -> ImageModel:
    require(cutoff >= 3, ("cutoff-below-seeds", cutoff))
    values = [value for value in range(2, cutoff + 1) if allowed(value)]
    pairs = {value: admissible_pairs(value) for value in values}
    generated = grounded_set(values, pairs)
    hard_roots = [
        value
        for value in values
        if value % 2 == 0
        and value not in generated
        and hard_shape(value, pairs[value])
        and chain_top(value, cutoff) not in generated
    ]
    target_roots = [
        value
        for value in values
        if value % 2 == 0
        and value not in generated
        and not hard_shape(value, pairs[value])
        and chain_top(value, cutoff) > value
    ]

    model = cp_model.CpModel()
    source = {value: model.new_bool_var(f"s_{value}") for value in values}
    image = {value: model.new_bool_var(f"f_{value}") for value in values}
    model.add(source[2] == 1)
    model.add(source[3] == 1)
    model.add(image[2] == 1)
    model.add(image[3] == 1)

    for value in values:
        if value in (2, 3):
            continue
        witnesses: list[cp_model.IntVar] = []
        for index, (left, right) in enumerate(pairs[value]):
            model.add(source[left] + source[right] - source[value] <= 1)
            witnesses.append(
                and_var(model, source[left], source[right], f"w_{value}_{index}")
            )
        if witnesses:
            for witness in witnesses:
                model.add(image[value] >= witness)
            model.add(image[value] <= sum(witnesses))
        else:
            model.add(image[value] == 0)

    healed: dict[int, cp_model.IntVar] = {}
    for root in target_roots:
        top = chain_top(root, cutoff)
        event = model.new_bool_var(f"healed_{root}")
        model.add(event <= image[top])
        model.add(event <= 1 - image[root])
        model.add(event >= image[top] - image[root])
        healed[root] = event

    return ImageModel(
        cutoff,
        values,
        pairs,
        generated,
        hard_roots,
        target_roots,
        model,
        source,
        image,
        healed,
    )


def maximum_matching(
    lefts: list[int], adjacency: dict[int, set[int]]
) -> tuple[dict[int, int], dict[int, int]]:
    right_to_left: dict[int, int] = {}

    def augment(left: int, seen: set[int]) -> bool:
        for right in sorted(adjacency[left]):
            if right in seen:
                continue
            seen.add(right)
            owner = right_to_left.get(right)
            if owner is None or augment(owner, seen):
                right_to_left[right] = left
                return True
        return False

    for left in lefts:
        augment(left, set())
    left_to_right = {left: right for right, left in right_to_left.items()}
    return left_to_right, right_to_left


def hall_set(
    lefts: list[int],
    adjacency: dict[int, set[int]],
    left_to_right: dict[int, int],
    right_to_left: dict[int, int],
) -> tuple[set[int], set[int]]:
    reachable_left = {left for left in lefts if left not in left_to_right}
    reachable_right: set[int] = set()
    queue = list(sorted(reachable_left))
    while queue:
        left = queue.pop()
        matched_right = left_to_right.get(left)
        for right in adjacency[left]:
            if right == matched_right or right in reachable_right:
                continue
            reachable_right.add(right)
            owner = right_to_left.get(right)
            if owner is not None and owner not in reachable_left:
                reachable_left.add(owner)
                queue.append(owner)
    neighbors = set().union(*(adjacency[left] for left in reachable_left))
    require(neighbors == reachable_right, ("alternating-neighborhood", neighbors, reachable_right))
    require(len(neighbors) < len(reachable_left), ("not-a-Hall-deficit", reachable_left, neighbors))
    return reachable_left, neighbors


def query_edge(
    data: ImageModel,
    hard: int,
    target: int,
    workers: int,
    time_limit: int,
) -> tuple[str, list[int] | None]:
    data.model.clear_assumptions()
    hard_top = chain_top(hard, data.cutoff)
    data.model.add_assumptions([data.image[hard_top].Not(), data.healed[target].Not()])
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit
    status_code = solver.solve(data.model)
    status = solver.status_name(status_code)
    if status in {"OPTIMAL", "FEASIBLE"}:
        source = sorted(value for value in data.values if solver.value(data.source[value]))
        return status, source
    return status, None


def witness_key(source: list[int]) -> tuple[int, ...]:
    return tuple(source)


def replay_source(data: ImageModel, source_values: list[int]) -> tuple[set[int], set[int], set[int]]:
    source = set(source_values)
    require(source <= set(data.values), ("source-outside-domain", sorted(source - set(data.values))))
    require(forward_closed(source, data.values, data.pairs), "source-not-forward-closed")
    image = support_image(source, data.values, data.pairs)
    unhealed, healed = shell_sets(
        image, data.hard_roots, data.target_roots, data.cutoff
    )
    return image, unhealed, healed


def minimize_witness_cover(
    data: ImageModel,
    universe: set[tuple[int, int]],
    sources: list[list[int]],
    workers: int,
    time_limit: int,
) -> list[dict]:
    candidates: list[tuple[list[int], set[tuple[int, int]], set[int], set[int]]] = []
    seen: set[tuple[int, ...]] = set()
    for source in sources:
        key = witness_key(source)
        if key in seen:
            continue
        seen.add(key)
        image, unhealed, healed = replay_source(data, source)
        covered = {
            (hard, target)
            for hard, target in universe
            if hard in unhealed and target not in healed
        }
        if covered:
            candidates.append((source, covered, unhealed, healed))

    for edge in universe:
        require(any(edge in row[1] for row in candidates), ("uncovered-invalid-edge", edge))

    model = cp_model.CpModel()
    take = [model.new_bool_var(f"take_{index}") for index in range(len(candidates))]
    for edge in sorted(universe):
        model.add(sum(take[index] for index, row in enumerate(candidates) if edge in row[1]) >= 1)
    model.minimize(sum(take))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit
    status_code = solver.solve(model)
    status = solver.status_name(status_code)
    require(status == "OPTIMAL", ("set-cover-not-exact", status))

    selected = []
    for index, (source, covered, unhealed, healed) in enumerate(candidates):
        if not solver.value(take[index]):
            continue
        image = support_image(set(source), data.values, data.pairs)
        selected.append(
            {
                "source_members": source,
                "image_members": sorted(image),
                "unhealed_hard_roots": sorted(unhealed),
                "healed_nonhard_roots": sorted(healed),
                "covers_crossing_edges": [list(edge) for edge in sorted(covered)],
            }
        )
    return selected


def synthesize_cutoff(
    cutoff: int,
    workers: int,
    time_limit: int,
) -> dict:
    data = build_model(cutoff)
    adjacency = {hard: set(data.target_roots) for hard in data.hard_roots}
    rejected: dict[tuple[int, int], list[int]] = {}
    universal: set[tuple[int, int]] = set()
    query_count = 0

    while True:
        left_to_right, right_to_left = maximum_matching(data.hard_roots, adjacency)
        if len(left_to_right) < len(data.hard_roots):
            deficient_left, neighbors = hall_set(
                data.hard_roots, adjacency, left_to_right, right_to_left
            )
            outside = set(data.target_roots) - neighbors
            crossing = {(hard, target) for hard in deficient_left for target in outside}
            require(crossing <= set(rejected), ("crossing-edge-not-rejected", sorted(crossing - set(rejected))))
            selected = minimize_witness_cover(
                data,
                crossing,
                list(rejected.values()),
                workers,
                time_limit,
            )
            return {
                "cutoff": cutoff,
                "status": "HALL_OBSTRUCTION",
                "hard_roots": data.hard_roots,
                "candidate_nonhard_roots": data.target_roots,
                "sat_queries": query_count,
                "rejected_edges": len(rejected),
                "certified_universal_edges": [list(edge) for edge in sorted(universal)],
                "hall_hard_set": sorted(deficient_left),
                "hall_neighbor_set_in_supergraph": sorted(neighbors),
                "hall_deficit": len(deficient_left) - len(neighbors),
                "crossing_nonedges": len(crossing),
                "minimum_witness_count": len(selected),
                "witnesses": selected,
            }

        invalid_this_round = 0
        for hard, target in sorted(left_to_right.items()):
            edge = (hard, target)
            if edge in universal:
                continue
            status, source = query_edge(data, hard, target, workers, time_limit)
            query_count += 1
            if source is not None:
                image, unhealed, healed = replay_source(data, source)
                require(hard in unhealed, ("query-hard-not-unhealed", edge))
                require(target not in healed, ("query-target-healed", edge))
                require(image == support_image(set(source), data.values, data.pairs), "image-replay")
                adjacency[hard].remove(target)
                rejected[edge] = source
                invalid_this_round += 1
            elif status == "INFEASIBLE":
                universal.add(edge)
            else:
                raise RuntimeError(("edge-query-not-exact", edge, status))

        if invalid_this_round == 0:
            require(
                all((hard, target) in universal for hard, target in left_to_right.items()),
                "matching-has-uncertified-edge",
            )
            return {
                "cutoff": cutoff,
                "status": "STATIC_CHARGE_EXISTS",
                "hard_roots": data.hard_roots,
                "candidate_nonhard_roots": data.target_roots,
                "sat_queries": query_count,
                "rejected_edges": len(rejected),
                "universal_matching": [
                    [hard, left_to_right[hard]] for hard in sorted(left_to_right)
                ],
            }


def verify_obstruction(row: dict) -> dict:
    cutoff = int(row["cutoff"])
    data = build_model(cutoff)
    require(data.hard_roots == list(map(int, row["hard_roots"])), "hard-root-list")
    require(
        data.target_roots == list(map(int, row["candidate_nonhard_roots"])),
        "target-root-list",
    )
    hall_hard = set(map(int, row["hall_hard_set"]))
    hall_neighbors = set(map(int, row["hall_neighbor_set_in_supergraph"]))
    require(hall_hard <= set(data.hard_roots), "hall-hard-domain")
    require(hall_neighbors <= set(data.target_roots), "hall-target-domain")
    require(len(hall_neighbors) < len(hall_hard), "hall-count")
    universe = {
        (hard, target)
        for hard in hall_hard
        for target in set(data.target_roots) - hall_neighbors
    }
    covered: set[tuple[int, int]] = set()
    replayed = []
    for witness in row["witnesses"]:
        source_values = list(map(int, witness["source_members"]))
        image, unhealed, healed = replay_source(data, source_values)
        require(sorted(image) == list(map(int, witness["image_members"])), "saved-image")
        local_cover = {
            edge
            for edge in universe
            if edge[0] in unhealed and edge[1] not in healed
        }
        covered |= local_cover
        replayed.append(
            {
                "source_size": len(source_values),
                "image_size": len(image),
                "covered_crossing_edges": len(local_cover),
                "image_excess": len(unhealed) - len(healed),
            }
        )
    require(covered == universe, ("witness-cover", sorted(universe - covered)))
    return {
        "cutoff": cutoff,
        "hall_hard_count": len(hall_hard),
        "hall_neighbor_count": len(hall_neighbors),
        "crossing_edges_replayed": len(covered),
        "witnesses_replayed": len(replayed),
        "witness_summaries": replayed,
        "solver_free_obstruction_verified": True,
    }


def scan(stop: int, workers: int, time_limit: int) -> dict:
    tested = []
    for cutoff in range(3, stop + 1):
        data = build_model(cutoff)
        if cutoff not in data.hard_roots:
            continue
        row = synthesize_cutoff(cutoff, workers, time_limit)
        tested.append(row)
        print(
            f"X={cutoff} status={row['status']} hard={len(row['hard_roots'])} "
            f"targets={len(row['candidate_nonhard_roots'])} queries={row['sat_queries']}"
        )
        if row["status"] == "HALL_OBSTRUCTION":
            break
    return {"schema_version": 1, "scan_stop": stop, "cutoffs": tested}


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--scan-stop", type=int)
    mode.add_argument("--cutoff", type=int)
    mode.add_argument("--verify", type=Path)
    parser.add_argument("--workers", type=int, default=64)
    parser.add_argument("--time-limit", type=int, default=30)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.verify is not None:
        saved = json.loads(args.verify.read_text(encoding="utf-8"))
        obstruction = next(
            row for row in saved["cutoffs"] if row["status"] == "HALL_OBSTRUCTION"
        )
        result = {"schema_version": 1, "verification": verify_obstruction(obstruction)}
    elif args.cutoff is not None:
        result = {
            "schema_version": 1,
            "scan_stop": args.cutoff,
            "cutoffs": [synthesize_cutoff(args.cutoff, args.workers, args.time_limit)],
        }
    else:
        result = scan(args.scan_stop, args.workers, args.time_limit)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if args.verify is not None:
        print(json.dumps(result["verification"], sort_keys=True))


if __name__ == "__main__":
    main()
