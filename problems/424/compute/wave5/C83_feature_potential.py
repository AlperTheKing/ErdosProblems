#!/usr/bin/env python3
"""Exact synthesis and falsification of feature-symmetric image charges.

A feature potential assigns the same pair weight w(A, B) to every hard root
of feature A and every nonhard root of feature B.  The features may include
residue/parity, exact obstruction rank, dyadic scale, pair count, and a full
factor-endpoint signature.  Positive weight is safe only if every pair in
the corresponding feature block is a universal image-shell implication.

The class transportation LP is a bipartite flow problem, so an integral
matching is an exact rational synthesis oracle.  CEGIS deletes a block as
soon as SAT returns one concrete countercut.  If flow then fails, a class
Hall deficit plus one replayable countercut per crossing block is an exact
falsifier for the whole feature-potential family.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Hashable


HERE = Path(__file__).resolve().parent
STATIC_PATH = HERE / "C83_static_charge.py"
SPEC = importlib.util.spec_from_file_location("c83_static_charge", STATIC_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load C83_static_charge.py")
C83 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = C83
SPEC.loader.exec_module(C83)


Feature = tuple[Hashable, ...]
Block = tuple[Feature, Feature]


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def dyadic_scale(outer: int, inner: int) -> int:
    require(outer >= inner >= 1, ("bad-scale", outer, inner))
    return (outer // inner).bit_length() - 1


def obstruction_ranks(data: C83.ImageModel) -> dict[int, int]:
    ranks: dict[int, int] = {}
    for value in data.values:
        if value in data.generated:
            continue
        pairs = data.pairs[value]
        if not pairs:
            ranks[value] = 0
            continue
        minima = []
        for left, right in pairs:
            blockers = [
                ranks[parent]
                for parent in (left, right)
                if parent not in data.generated
            ]
            require(blockers, ("grounded-pair-for-hole", value, left, right))
            minima.append(min(blockers))
        ranks[value] = 1 + max(minima)
    return ranks


def endpoint_signature(
    endpoint: int,
    output: int,
    generated: set[int],
    ranks: dict[int, int],
) -> tuple:
    state = ("G",) if endpoint in generated else ("H", ranks[endpoint])
    return state + (endpoint % 6, dyadic_scale(output, endpoint))


def factor_signature(
    root: int,
    data: C83.ImageModel,
    ranks: dict[int, int],
) -> tuple:
    rows = []
    for left, right in data.pairs[root]:
        endpoints = sorted(
            (
                endpoint_signature(left, root, data.generated, ranks),
                endpoint_signature(right, root, data.generated, ranks),
            )
        )
        rows.append(tuple(endpoints))
    return tuple(sorted(rows))


def root_feature(
    root: int,
    side: str,
    mode: str,
    data: C83.ImageModel,
    ranks: dict[int, int],
) -> Feature:
    pairs = data.pairs[root]
    root_type = "hard" if side == "H" else ("splitless" if not pairs else "seed3")
    base: Feature = (
        root_type,
        root % 18,
        ranks[root],
        dyadic_scale(data.cutoff, root),
        len(pairs),
    )
    if mode == "coarse":
        return base
    if mode == "full":
        return base + (factor_signature(root, data, ranks),)
    raise ValueError(mode)


def feature_text(feature: Feature) -> str:
    return json.dumps(feature, separators=(",", ":"))


def json_feature(feature: Feature) -> list:
    return json.loads(json.dumps(feature))


def build_classes(
    cutoff: int, mode: str
) -> tuple[
    C83.ImageModel,
    dict[int, Feature],
    dict[int, Feature],
    dict[Feature, list[int]],
    dict[Feature, list[int]],
]:
    data = C83.build_model(cutoff)
    ranks = obstruction_ranks(data)
    hard_feature = {
        root: root_feature(root, "H", mode, data, ranks)
        for root in data.hard_roots
    }
    target_feature = {
        root: root_feature(root, "N", mode, data, ranks)
        for root in data.target_roots
    }
    hard_classes: dict[Feature, list[int]] = defaultdict(list)
    target_classes: dict[Feature, list[int]] = defaultdict(list)
    for root, feature in hard_feature.items():
        hard_classes[feature].append(root)
    for root, feature in target_feature.items():
        target_classes[feature].append(root)
    return (
        data,
        hard_feature,
        target_feature,
        dict(hard_classes),
        dict(target_classes),
    )


def sorted_features(classes: dict[Feature, list[int]]) -> list[Feature]:
    return sorted(classes, key=feature_text)


def class_records(prefix: str, classes: dict[Feature, list[int]]) -> tuple[dict[Feature, str], list[dict]]:
    ids: dict[Feature, str] = {}
    records = []
    for index, feature in enumerate(sorted_features(classes)):
        class_id = f"{prefix}{index}"
        ids[feature] = class_id
        records.append(
            {
                "id": class_id,
                "feature": json_feature(feature),
                "members": sorted(classes[feature]),
            }
        )
    return ids, records


def adjacency_from_blocks(
    hard_roots: list[int],
    target_classes: dict[Feature, list[int]],
    hard_feature: dict[int, Feature],
    allowed_blocks: set[Block],
) -> dict[int, set[int]]:
    result = {}
    for hard in hard_roots:
        feature = hard_feature[hard]
        neighbors: set[int] = set()
        for target_feature, targets in target_classes.items():
            if (feature, target_feature) in allowed_blocks:
                neighbors.update(targets)
        result[hard] = neighbors
    return result


def block_counterexample(
    data: C83.ImageModel,
    hard_members: list[int],
    target_members: list[int],
    workers: int,
    time_limit: int,
) -> tuple[tuple[int, int, list[int]] | None, int]:
    queries = 0
    for hard in sorted(hard_members):
        for target in sorted(target_members):
            status, source = C83.query_edge(
                data, hard, target, workers, time_limit
            )
            queries += 1
            if source is not None:
                _, unhealed, healed = C83.replay_source(data, source)
                require(hard in unhealed and target not in healed, ("bad-block-witness", hard, target))
                return (hard, target, source), queries
            require(status == "INFEASIBLE", ("block-query-not-exact", hard, target, status))
    return None, queries


def hall_class_obstruction(
    data: C83.ImageModel,
    hard_feature: dict[int, Feature],
    target_feature: dict[int, Feature],
    hard_classes: dict[Feature, list[int]],
    target_classes: dict[Feature, list[int]],
    allowed_blocks: set[Block],
    rejected: dict[Block, tuple[int, int, list[int]]],
) -> dict:
    adjacency = adjacency_from_blocks(
        data.hard_roots, target_classes, hard_feature, allowed_blocks
    )
    left_to_right, right_to_left = C83.maximum_matching(data.hard_roots, adjacency)
    reachable_hard, _ = C83.hall_set(
        data.hard_roots, adjacency, left_to_right, right_to_left
    )
    hall_hard_features = {hard_feature[root] for root in reachable_hard}
    hall_hards = {
        root for feature in hall_hard_features for root in hard_classes[feature]
    }
    neighbor_features = {
        target_f
        for hard_f in hall_hard_features
        for target_f in target_classes
        if (hard_f, target_f) in allowed_blocks
    }
    hall_targets = {
        root for feature in neighbor_features for root in target_classes[feature]
    }
    require(len(hall_targets) < len(hall_hards), ("class-Hall-not-deficient", hall_hards, hall_targets))
    outside_features = set(target_classes) - neighbor_features
    crossing_blocks = {
        (hard_f, target_f)
        for hard_f in hall_hard_features
        for target_f in outside_features
    }
    require(crossing_blocks <= set(rejected), ("unrejected-crossing-block", len(crossing_blocks - set(rejected))))

    hard_ids, hard_records = class_records("H", hard_classes)
    target_ids, target_records = class_records("N", target_classes)
    candidate_sources: dict[tuple[int, ...], list[int]] = {}
    grounded_source = sorted(data.generated)
    candidate_sources[tuple(grounded_source)] = grounded_source
    for _, _, source in rejected.values():
        candidate_sources.setdefault(tuple(source), source)
    candidates = []
    for source in candidate_sources.values():
        image, unhealed, healed = C83.replay_source(data, source)
        covered: dict[Block, tuple[int, int]] = {}
        for block in crossing_blocks:
            invalid_hard = next(
                (root for root in hard_classes[block[0]] if root in unhealed),
                None,
            )
            invalid_target = next(
                (root for root in target_classes[block[1]] if root not in healed),
                None,
            )
            if invalid_hard is not None and invalid_target is not None:
                covered[block] = (invalid_hard, invalid_target)
        if covered:
            candidates.append((source, image, unhealed, healed, covered))
    for block in crossing_blocks:
        require(any(block in row[4] for row in candidates), ("block-not-covered", block))

    cover_model = C83.cp_model.CpModel()
    take = [
        cover_model.new_bool_var(f"take_{index}")
        for index in range(len(candidates))
    ]
    for block in crossing_blocks:
        cover_model.add(
            sum(take[index] for index, row in enumerate(candidates) if block in row[4])
            >= 1
        )
    cover_model.minimize(sum(take))
    cover_solver = C83.cp_model.CpSolver()
    cover_solver.parameters.num_search_workers = 1
    cover_status = cover_solver.status_name(cover_solver.solve(cover_model))
    require(cover_status == "OPTIMAL", ("block-cover-not-exact", cover_status))

    witnesses = []
    for index, (source, image, unhealed, healed, covered) in enumerate(candidates):
        if not cover_solver.value(take[index]):
            continue
        blocks = []
        for block, invalid_pair in sorted(
            covered.items(),
            key=lambda item: (feature_text(item[0][0]), feature_text(item[0][1])),
        ):
            blocks.append(
                {
                    "hard_class": hard_ids[block[0]],
                    "target_class": target_ids[block[1]],
                    "invalid_pair": list(invalid_pair),
                }
            )
        witnesses.append(
            {
                "source_members": source,
                "image_members": sorted(image),
                "unhealed_hard_roots": sorted(unhealed),
                "healed_nonhard_roots": sorted(healed),
                "invalid_feature_blocks": blocks,
            }
        )
    return {
        "hard_classes": hard_records,
        "target_classes": target_records,
        "hall_hard_classes": [hard_ids[feature] for feature in sorted(hall_hard_features, key=feature_text)],
        "hall_neighbor_classes": [target_ids[feature] for feature in sorted(neighbor_features, key=feature_text)],
        "hall_hard_count": len(hall_hards),
        "hall_neighbor_capacity": len(hall_targets),
        "hall_deficit": len(hall_hards) - len(hall_targets),
        "crossing_feature_blocks": len(crossing_blocks),
        "minimum_countercut_count": len(witnesses),
        "crossing_block_witnesses": witnesses,
    }


def exact_potential(
    matching: dict[int, int],
    hard_feature: dict[int, Feature],
    target_feature: dict[int, Feature],
    hard_classes: dict[Feature, list[int]],
    target_classes: dict[Feature, list[int]],
) -> list[dict]:
    counts = Counter((hard_feature[hard], target_feature[target]) for hard, target in matching.items())
    rows = []
    for (hard_f, target_f), count in sorted(
        counts.items(), key=lambda item: (feature_text(item[0][0]), feature_text(item[0][1]))
    ):
        denominator = len(hard_classes[hard_f]) * len(target_classes[target_f])
        weight = Fraction(count, denominator)
        rows.append(
            {
                "hard_feature": json_feature(hard_f),
                "target_feature": json_feature(target_f),
                "matched_mass": count,
                "pair_weight": [weight.numerator, weight.denominator],
            }
        )
    return rows


def synthesize(cutoff: int, mode: str, workers: int, time_limit: int) -> dict:
    data, hard_feature, target_feature, hard_classes, target_classes = build_classes(cutoff, mode)
    allowed_blocks: set[Block] = {
        (hard_f, target_f) for hard_f in hard_classes for target_f in target_classes
    }
    rejected: dict[Block, tuple[int, int, list[int]]] = {}
    certified: set[Block] = set()
    queries = 0

    while True:
        adjacency = adjacency_from_blocks(
            data.hard_roots, target_classes, hard_feature, allowed_blocks
        )
        left_to_right, right_to_left = C83.maximum_matching(data.hard_roots, adjacency)
        if len(left_to_right) < len(data.hard_roots):
            obstruction = hall_class_obstruction(
                data,
                hard_feature,
                target_feature,
                hard_classes,
                target_classes,
                allowed_blocks,
                rejected,
            )
            return {
                "cutoff": cutoff,
                "feature_mode": mode,
                "status": "FEATURE_HALL_OBSTRUCTION",
                "hard_roots": data.hard_roots,
                "candidate_nonhard_roots": data.target_roots,
                "hard_class_count": len(hard_classes),
                "target_class_count": len(target_classes),
                "sat_queries": queries,
                "rejected_feature_blocks": len(rejected),
                **obstruction,
            }

        used_blocks = {
            (hard_feature[hard], target_feature[target])
            for hard, target in left_to_right.items()
        }
        removed = 0
        for block in sorted(used_blocks, key=lambda item: (feature_text(item[0]), feature_text(item[1]))):
            if block in certified:
                continue
            counterexample, local_queries = block_counterexample(
                data,
                hard_classes[block[0]],
                target_classes[block[1]],
                workers,
                time_limit,
            )
            queries += local_queries
            if counterexample is None:
                certified.add(block)
            else:
                allowed_blocks.remove(block)
                rejected[block] = counterexample
                removed += 1
        if removed == 0:
            require(used_blocks <= certified, "uncertified-potential-block")
            hard_ids, hard_records = class_records("H", hard_classes)
            target_ids, target_records = class_records("N", target_classes)
            return {
                "cutoff": cutoff,
                "feature_mode": mode,
                "status": "FEATURE_POTENTIAL_EXISTS",
                "hard_roots": data.hard_roots,
                "candidate_nonhard_roots": data.target_roots,
                "hard_class_count": len(hard_classes),
                "target_class_count": len(target_classes),
                "sat_queries": queries,
                "rejected_feature_blocks": len(rejected),
                "hard_classes": hard_records,
                "target_classes": target_records,
                "exact_pair_weights": exact_potential(
                    left_to_right,
                    hard_feature,
                    target_feature,
                    hard_classes,
                    target_classes,
                ),
                "certified_blocks_used": [
                    [hard_ids[block[0]], target_ids[block[1]]]
                    for block in sorted(used_blocks, key=lambda item: (feature_text(item[0]), feature_text(item[1])))
                ],
            }


def records_by_id(records: list[dict]) -> dict[str, dict]:
    return {str(record["id"]): record for record in records}


def verify_obstruction(row: dict) -> dict:
    cutoff = int(row["cutoff"])
    mode = str(row["feature_mode"])
    data, hard_feature, target_feature, hard_classes, target_classes = build_classes(cutoff, mode)
    hard_ids, hard_records = class_records("H", hard_classes)
    target_ids, target_records = class_records("N", target_classes)
    require(hard_records == row["hard_classes"], "hard-class-replay")
    require(target_records == row["target_classes"], "target-class-replay")
    inverse_hard = {class_id: feature for feature, class_id in hard_ids.items()}
    inverse_target = {class_id: feature for feature, class_id in target_ids.items()}
    hall_hard_features = {inverse_hard[str(class_id)] for class_id in row["hall_hard_classes"]}
    neighbor_features = {inverse_target[str(class_id)] for class_id in row["hall_neighbor_classes"]}
    hall_hard_count = sum(len(hard_classes[feature]) for feature in hall_hard_features)
    neighbor_count = sum(len(target_classes[feature]) for feature in neighbor_features)
    require(hall_hard_count > neighbor_count, "saved-Hall-count")
    crossing = {
        (hard_f, target_f)
        for hard_f in hall_hard_features
        for target_f in set(target_classes) - neighbor_features
    }
    witnessed: set[Block] = set()
    for witness in row["crossing_block_witnesses"]:
        image, unhealed, healed = C83.replay_source(
            data, list(map(int, witness["source_members"]))
        )
        require(sorted(image) == list(map(int, witness["image_members"])), "image-replay")
        for item in witness["invalid_feature_blocks"]:
            block = (
                inverse_hard[str(item["hard_class"])],
                inverse_target[str(item["target_class"])],
            )
            hard, target = map(int, item["invalid_pair"])
            require(hard_feature[hard] == block[0], ("hard-feature", hard))
            require(target_feature[target] == block[1], ("target-feature", target))
            require(
                hard in unhealed and target not in healed,
                ("invalid-pair-replay", hard, target),
            )
            witnessed.add(block)
    require(witnessed == crossing, ("crossing-block-replay", len(crossing - witnessed)))
    return {
        "cutoff": cutoff,
        "feature_mode": mode,
        "hall_hard_count": hall_hard_count,
        "hall_neighbor_capacity": neighbor_count,
        "crossing_blocks_replayed": len(witnessed),
        "solver_free_feature_obstruction_verified": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--cutoff", type=int)
    mode.add_argument("--verify", type=Path)
    parser.add_argument("--feature-mode", choices=("coarse", "full"), default="full")
    parser.add_argument("--workers", type=int, default=64)
    parser.add_argument("--time-limit", type=int, default=30)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.verify is not None:
        saved = json.loads(args.verify.read_text(encoding="utf-8"))
        result = {"schema_version": 1, "verification": verify_obstruction(saved["result"])}
    else:
        result = {
            "schema_version": 1,
            "result": synthesize(
                args.cutoff, args.feature_mode, args.workers, args.time_limit
            ),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    row = result.get("result", result.get("verification"))
    print(
        f"X={row['cutoff']} status={row.get('status', 'VERIFIED')} "
        f"mode={row['feature_mode']} "
        f"hard={len(row.get('hard_roots', [])) or row.get('hall_hard_count')} "
        f"queries={row.get('sat_queries', 0)}"
    )


if __name__ == "__main__":
    main()
