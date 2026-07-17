#!/usr/bin/env python3
"""Exact combinatorial audits for the C23 unconditional image lemma.

The script deliberately avoids the LP relaxation.  It has two roles:

1. replay saved CP-SAT witnesses from their source membership lists and
   audit chain-shell and local-descent assertions; and
2. use a Boolean CP-SAT model to find exact counterexamples to strengthenings
   obtained by deleting terms from C23's transition identity.

All factorizations use distinct allowed factors.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path
from typing import Iterable

from ortools.sat.python import cp_model


ROOT = Path(__file__).resolve().parents[4]


def allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


def admissible_pairs(value: int) -> list[tuple[int, int]]:
    product = value + 1
    result: list[tuple[int, int]] = []
    left = 2
    while left * left < product:
        if product % left == 0:
            right = product // left
            if allowed(left) and allowed(right):
                result.append((left, right))
        left += 1
    return result


def hard_shape(value: int, pairs: list[tuple[int, int]] | None = None) -> bool:
    local_pairs = admissible_pairs(value) if pairs is None else pairs
    if value % 2 or not local_pairs:
        return False
    if (value + 1) % 3:
        return True
    parent = (value + 1) // 3
    return not (allowed(parent) and parent != 3)


def seed_root(value: int) -> int:
    while value % 2:
        value = (value + 1) // 2
    return value


def chain_top(root: int, cutoff: int) -> int:
    value = root
    while 2 * value - 1 <= cutoff:
        value = 2 * value - 1
    return value


def support_core(
    source: set[int], limit: int, pairs: dict[int, list[tuple[int, int]]]
) -> set[int]:
    image = {2, 3}
    for value in range(4, limit + 1):
        if not allowed(value):
            continue
        if any(left in source and right in source for left, right in pairs[value]):
            image.add(value)
    return image


def forward_closed(
    source: set[int], limit: int, pairs: dict[int, list[tuple[int, int]]]
) -> bool:
    if not {2, 3}.issubset(source):
        return False
    return all(
        value in source
        for value in range(4, limit + 1)
        if allowed(value)
        for left, right in pairs[value]
        if left in source and right in source
    )


def hard_holes_and_boundaries(
    members: set[int], limit: int, pairs: dict[int, list[tuple[int, int]]]
) -> tuple[list[int], list[int]]:
    hard_holes = [
        value
        for value in range(2, limit + 1)
        if allowed(value)
        and hard_shape(value, pairs[value])
        and value not in members
    ]
    boundaries = [
        2 * parent - 1
        for parent in range(2, (limit + 1) // 2 + 1)
        if allowed(parent)
        and parent not in members
        and 2 * parent - 1 in members
    ]
    return hard_holes, boundaries


def unsupported(
    source: set[int], image: set[int], limit: int
) -> list[int]:
    return sorted((source - image) - {2, 3})


def shell_sets(
    members: set[int], limit: int, pairs: dict[int, list[tuple[int, int]]]
) -> tuple[list[int], list[int]]:
    """Return unhealed hard roots and healed nonhard roots at ``limit``."""
    unhealed_hard: list[int] = []
    healed_nonhard: list[int] = []
    for root in range(2, limit + 1, 2):
        if not allowed(root) or root in members:
            continue
        top = chain_top(root, limit)
        healed = top in members
        if hard_shape(root, pairs[root]):
            if not healed:
                unhealed_hard.append(root)
        elif healed:
            healed_nonhard.append(root)
    return unhealed_hard, healed_nonhard


def local_reach(
    start: int,
    present: set[int],
    image: set[int],
    cutoff: int,
    pairs: dict[int, list[tuple[int, int]]],
) -> set[int]:
    """Blocked-factor reachability along every missing image-chain segment."""
    reached = {start}
    queue = deque([start])
    while queue:
        root = queue.popleft()
        value = root
        while value <= cutoff and value not in image:
            for left, right in pairs[value]:
                for parent in (left, right):
                    if parent not in present:
                        next_root = seed_root(parent)
                        if next_root not in reached:
                            reached.add(next_root)
                            queue.append(next_root)
            value = 2 * value - 1
    return reached


def maximum_matching(graph: dict[int, set[int]]) -> tuple[int, dict[int, int]]:
    right_to_left: dict[int, int] = {}

    def augment(left: int, seen: set[int]) -> bool:
        for right in sorted(graph[left]):
            if right in seen:
                continue
            seen.add(right)
            if right not in right_to_left or augment(right_to_left[right], seen):
                right_to_left[right] = left
                return True
        return False

    size = 0
    for left in sorted(graph):
        size += augment(left, set())
    return size, {left: right for right, left in right_to_left.items()}


def grounded_set(limit: int, pairs: dict[int, list[tuple[int, int]]]) -> set[int]:
    members = {2, 3}
    for value in range(4, limit + 1):
        if not allowed(value):
            continue
        if any(left in members and right in members for left, right in pairs[value]):
            members.add(value)
    return members


def obstruction_ranks(
    limit: int,
    grounded: set[int],
    pairs: dict[int, list[tuple[int, int]]],
) -> dict[int, int]:
    ranks: dict[int, int] = {}
    for value in range(2, limit + 1):
        if not allowed(value) or value in grounded:
            continue
        if not pairs[value]:
            ranks[value] = 0
            continue
        pair_minima = []
        for left, right in pairs[value]:
            missing = [parent for parent in (left, right) if parent not in grounded]
            if not missing:
                raise AssertionError(("grounded hole has grounded pair", value))
            pair_minima.append(min(ranks[parent] for parent in missing))
        ranks[value] = 1 + max(pair_minima)
    return ranks


def immediate_healed_parent_graph(
    hard_roots: Iterable[int],
    source: set[int],
    image: set[int],
    cutoff: int,
    pairs: dict[int, list[tuple[int, int]]],
) -> dict[int, set[int]]:
    boundary_parents = {
        parent
        for parent in range(2, (cutoff + 1) // 2 + 1)
        if allowed(parent)
        and parent not in image
        and 2 * parent - 1 in image
    }
    return {
        hard: {
            parent
            for pair in pairs[hard]
            for parent in pair
            if parent not in source and parent in boundary_parents
        }
        for hard in hard_roots
    }


def witness_audit(path: Path) -> dict:
    saved = json.loads(path.read_text())
    cutoff = int(saved["selected_cutoff"])
    values = [value for value in range(2, cutoff + 1) if allowed(value)]
    pairs = {value: admissible_pairs(value) for value in values}
    source = set(map(int, saved["previous_members"]))
    image = support_core(source, cutoff, pairs)
    if not forward_closed(source, cutoff, pairs):
        raise AssertionError((path, "source is not forward closed"))
    if image != set(map(int, saved["following_members"])):
        raise AssertionError((path, "image mismatch"))

    source_hard, source_q = hard_holes_and_boundaries(source, cutoff, pairs)
    image_hard, image_q = hard_holes_and_boundaries(image, cutoff, pairs)
    if source_hard != saved["previous_hard_holes"] or source_q != saved["previous_boundary_children"]:
        raise AssertionError((path, "source event mismatch"))
    if image_hard != saved["following_hard_holes"] or image_q != saved["following_boundary_children"]:
        raise AssertionError((path, "image event mismatch"))

    removed = unsupported(source, image, cutoff)
    half = (cutoff + 1) // 2
    late_danger = [
        value
        for value in removed
        if value > half and (value % 2 or hard_shape(value, pairs[value]))
    ]
    early_nonhard = [
        value
        for value in removed
        if value <= half and value % 2 == 0 and not hard_shape(value, pairs[value])
    ]
    old_slack = len(source_q) - len(source_hard)
    new_slack = len(image_q) - len(image_hard)
    if new_slack != old_slack - len(late_danger) + len(early_nonhard):
        raise AssertionError((path, "transition identity mismatch"))

    unhealed_hard, healed_nonhard = shell_sets(image, cutoff, pairs)
    if new_slack != len(healed_nonhard) - len(unhealed_hard):
        raise AssertionError((path, "shell identity mismatch"))

    immediate = immediate_healed_parent_graph(
        unhealed_hard, source, image, cutoff, pairs
    )
    immediate_size, immediate_match = maximum_matching(immediate)
    blocker_transitive = {
        hard: local_reach(hard, source, image, cutoff, pairs)
        & set(healed_nonhard)
        for hard in unhealed_hard
    }
    blocker_transitive_size, blocker_transitive_match = maximum_matching(
        blocker_transitive
    )
    image_hole_transitive = {
        hard: local_reach(hard, image, image, cutoff, pairs)
        & set(healed_nonhard)
        for hard in unhealed_hard
    }
    image_hole_transitive_size, image_hole_transitive_match = maximum_matching(
        image_hole_transitive
    )

    direct_bank = [
        root
        for root in healed_nonhard
        if not pairs[root] or hard_shape(root, pairs[root])
    ]

    return {
        "file": str(path.relative_to(ROOT)),
        "cutoff": cutoff,
        "status": saved.get("status"),
        "objective_excess": len(image_hard) - len(image_q),
        "source_slack": old_slack,
        "late_dangerous_thresholds": late_danger,
        "early_nonhard_thresholds": early_nonhard,
        "unhealed_hard_roots": unhealed_hard,
        "healed_nonhard_roots": healed_nonhard,
        "immediate_healed_parent_matching": {
            "size": immediate_size,
            "required": len(unhealed_hard),
            "matching": immediate_match,
            "zero_degree": [hard for hard in unhealed_hard if not immediate[hard]],
        },
        "full_blocked_chain_matching": {
            "size": blocker_transitive_size,
            "required": len(unhealed_hard),
            "matching": blocker_transitive_match,
            "neighbors": {
                str(hard): sorted(blocker_transitive[hard])
                for hard in unhealed_hard
            },
        },
        "full_image_hole_chain_matching": {
            "size": image_hole_transitive_size,
            "required": len(unhealed_hard),
            "matching": image_hole_transitive_match,
            "neighbors": {
                str(hard): sorted(image_hole_transitive[hard])
                for hard in unhealed_hard
            },
        },
        "direct_structural_bank": {
            "roots": direct_bank,
            "size": len(direct_bank),
            "required": len(unhealed_hard),
        },
    }


def bool_and(model: cp_model.CpModel, left, right, name: str):
    result = model.new_bool_var(name)
    model.add(result <= left)
    model.add(result <= right)
    model.add(result >= left + right - 1)
    return result


def boundary_var(model: cp_model.CpModel, parent, child, name: str):
    result = model.new_bool_var(name)
    model.add(result <= 1 - parent)
    model.add(result <= child)
    model.add(result >= child - parent)
    return result


def optimize_transition_variant(
    cutoff: int,
    variant: str,
    workers: int,
    time_limit: float,
) -> dict:
    values = [value for value in range(2, cutoff + 1) if allowed(value)]
    pairs = {value: admissible_pairs(value) for value in values}
    hard_values = [value for value in values if hard_shape(value, pairs[value])]
    hard_set = set(hard_values)

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
        local_witnesses = []
        for index, (left, right) in enumerate(pairs[value]):
            model.add(source[left] + source[right] - 1 <= source[value])
            local_witnesses.append(
                bool_and(model, source[left], source[right], f"w_{value}_{index}")
            )
        if local_witnesses:
            for witness in local_witnesses:
                model.add(image[value] >= witness)
            model.add(image[value] <= sum(local_witnesses))
        else:
            model.add(image[value] == 0)

    source_boundaries = []
    for parent in values:
        child = 2 * parent - 1
        if child <= cutoff:
            source_boundaries.append(
                boundary_var(model, source[parent], source[child], f"q_{child}")
            )

    source_hard = [1 - source[value] for value in hard_values]
    old_slack = sum(source_boundaries) - sum(source_hard)
    half = (cutoff + 1) // 2
    late_terms = [
        source[value] - image[value]
        for value in values
        if value > half and (value % 2 or value in hard_set)
    ]
    helper_terms = [
        source[value] - image[value]
        for value in values
        if value <= half and value % 2 == 0 and value not in hard_set
    ]

    if variant == "no_helper":
        violation = sum(late_terms) - old_slack
    elif variant == "helper_only":
        violation = -old_slack - sum(helper_terms)
    elif variant == "thresholds_pay_themselves":
        violation = sum(late_terms) - sum(helper_terms)
    elif variant == "image":
        violation = sum(late_terms) - sum(helper_terms) - old_slack
    else:
        raise ValueError(variant)
    model.maximize(violation)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit
    status_code = solver.solve(model)
    status = solver.status_name(status_code)
    result = {
        "cutoff": cutoff,
        "variant": variant,
        "status": status,
        "best_objective_bound": solver.best_objective_bound,
    }
    if status not in {"OPTIMAL", "FEASIBLE"}:
        return result

    source_members = {value for value in values if solver.value(source[value])}
    image_members = {value for value in values if solver.value(image[value])}
    exact_image = support_core(source_members, cutoff, pairs)
    if exact_image != image_members or not forward_closed(source_members, cutoff, pairs):
        raise AssertionError("model replay failed")
    source_holes, source_q = hard_holes_and_boundaries(source_members, cutoff, pairs)
    image_holes, image_q = hard_holes_and_boundaries(image_members, cutoff, pairs)
    removed = unsupported(source_members, image_members, cutoff)
    late = [
        value
        for value in removed
        if value > half and (value % 2 or hard_shape(value, pairs[value]))
    ]
    helpers = [
        value
        for value in removed
        if value <= half and value % 2 == 0 and not hard_shape(value, pairs[value])
    ]
    replay_old_slack = len(source_q) - len(source_holes)
    replay_values = {
        "no_helper": len(late) - replay_old_slack,
        "helper_only": -replay_old_slack - len(helpers),
        "thresholds_pay_themselves": len(late) - len(helpers),
        "image": len(late) - len(helpers) - replay_old_slack,
    }
    objective = replay_values[variant]
    if objective != round(solver.objective_value):
        raise AssertionError((objective, solver.objective_value))

    result.update(
        {
            "objective_violation": objective,
            "source_members": sorted(source_members),
            "image_members": sorted(image_members),
            "source_hard_holes": source_holes,
            "source_boundary_children": source_q,
            "image_hard_holes": image_holes,
            "image_boundary_children": image_q,
            "unsupported": removed,
            "half": half,
            "old_slack": replay_old_slack,
            "late_dangerous_thresholds": late,
            "early_nonhard_thresholds": helpers,
        }
    )
    return result


def scan_variant(
    stop: int, variant: str, workers: int, time_limit: float
) -> dict:
    tested = 0
    last: dict | None = None
    for cutoff in range(2, stop + 1):
        if not allowed(cutoff) or not hard_shape(cutoff):
            continue
        tested += 1
        last = optimize_transition_variant(cutoff, variant, workers, time_limit)
        if last["status"] != "OPTIMAL":
            return {"tested": tested, "first_nonoptimal": last}
        if last["objective_violation"] > 0:
            return {"tested": tested, "first_failure": last}
    return {"tested": tested, "first_failure": None, "last": last}


def canonical_guardrails(limit: int = 362) -> dict:
    pairs = {
        value: admissible_pairs(value)
        for value in range(2, limit + 1)
        if allowed(value)
    }
    grounded = grounded_set(limit, pairs)
    ranks = obstruction_ranks(limit, grounded, pairs)
    rows = {}
    for cutoff in (54, 74, 186, 362):
        local_pairs = {value: pairs[value] for value in pairs if value <= cutoff}
        local_grounded = {value for value in grounded if value <= cutoff}
        hard_holes, boundary_children = hard_holes_and_boundaries(
            local_grounded, cutoff, local_pairs
        )
        unhealed, healed = shell_sets(local_grounded, cutoff, local_pairs)
        direct_bank = [
            root
            for root in healed
            if not local_pairs[root] or hard_shape(root, local_pairs[root])
        ]
        rows[str(cutoff)] = {
            "hard_holes": hard_holes,
            "boundary_children": boundary_children,
            "unhealed_hard_roots": unhealed,
            "healed_nonhard_roots": healed,
            "direct_structural_bank": direct_bank,
        }

    rank_cutoff = 362
    hard_rank_prefix = [
        value
        for value in rows[str(rank_cutoff)]["hard_holes"]
        if ranks[value] <= 2
    ]
    boundary_parent_rank_prefix = [
        (child + 1) // 2
        for child in rows[str(rank_cutoff)]["boundary_children"]
        if ranks[(child + 1) // 2] <= 2
    ]
    rows["362"]["rank_two_hard_holes"] = hard_rank_prefix
    rows["362"]["rank_two_boundary_parents"] = boundary_parent_rank_prefix
    rows["362"]["rank_two_excess"] = (
        len(hard_rank_prefix) - len(boundary_parent_rank_prefix)
    )
    return rows


def flow_audit(path: Path) -> dict:
    saved = json.loads(path.read_text())
    limit = int(saved["limit"])
    values = [value for value in range(2, limit + 1) if allowed(value)]
    pairs = {value: admissible_pairs(value) for value in values}
    grounded = grounded_set(limit, pairs)
    holes = set(values) - grounded
    hard_holes = {
        value for value in holes if hard_shape(value, pairs[value])
    }
    splitless = {value for value in holes if not pairs[value]}
    source = limit + 1
    sink = limit + 2
    used_seed_edges: set[tuple[int, int]] = set()
    used_hard_sources: set[int] = set()
    unary_edges: set[tuple[int, int, int]] = set()
    checked_paths = 0

    for index, row in enumerate(saved["path_certificate"], start=1):
        vertices = list(map(int, row["vertices"]))
        if len(vertices) < 3 or vertices[0] != source or vertices[-1] != sink:
            raise AssertionError((path, "bad path endpoints", vertices))
        first = vertices[1]
        if first not in splitless and first not in hard_holes:
            raise AssertionError((path, "bad source arc", first))
        if first in hard_holes:
            if first in used_hard_sources:
                raise AssertionError((path, "reused hard source", first))
            used_hard_sources.add(first)

        for left, right in zip(vertices[1:-2], vertices[2:-1]):
            if right == 2 * left - 1 and right <= limit and right in holes:
                edge = (left, right)
                if edge in used_seed_edges:
                    raise AssertionError((path, "reused seed edge", edge))
                used_seed_edges.add(edge)
                continue
            if right not in holes or (left + 1) % right:
                raise AssertionError((path, "bad internal edge", left, right))
            generated_factor = (left + 1) // right
            if (
                generated_factor not in grounded
                or generated_factor == right
                or tuple(sorted((generated_factor, right))) not in pairs[left]
            ):
                raise AssertionError(
                    (path, "bad unary edge", left, right, generated_factor)
                )
            unary_edges.add((left, right, generated_factor))

        terminal_parent = vertices[-2]
        terminal_child = 2 * terminal_parent - 1
        if terminal_child > limit or terminal_child not in grounded:
            raise AssertionError(
                (path, "bad terminal seed edge", terminal_parent, terminal_child)
            )
        terminal_edge = (terminal_parent, terminal_child)
        if terminal_edge in used_seed_edges:
            raise AssertionError((path, "reused terminal edge", terminal_edge))
        used_seed_edges.add(terminal_edge)

        expected_cutoff = sorted(hard_holes)[index - 1]
        if int(row["root_cutoff"]) != expected_cutoff:
            raise AssertionError(
                (path, "augmentation order mismatch", row["root_cutoff"], expected_cutoff)
            )
        checked_paths += 1

    if checked_paths != int(saved["final_flow"]):
        raise AssertionError((path, "flow count mismatch"))
    if checked_paths < len(hard_holes):
        raise AssertionError((path, "hard demand not saturated"))
    if int(saved["reverse_augmentations"]) != 0:
        raise AssertionError((path, "certificate is not forward-only"))

    return {
        "file": str(path.relative_to(ROOT)),
        "limit": limit,
        "hard_demand": len(hard_holes),
        "checked_paths": checked_paths,
        "distinct_seed_edges": len(used_seed_edges),
        "distinct_unary_edges": [
            {"from": left, "to": right, "generated_factor": factor}
            for left, right, factor in sorted(unary_edges)
        ],
        "directly_healed_sources": int(saved["directly_healed_sources"]),
        "first_direct_bank_failure": saved["first_direct_bank_failure"],
    }


def default_witnesses() -> list[Path]:
    c23 = ROOT / "problems/424/compute/wave3/C23_grounded_horn"
    c78 = ROOT / "problems/424/compute/wave5"
    candidates = [
        c78 / "C78_optimizer_54.json",
        c78 / "C78_optimizer_74.json",
        c78 / "C78_optimizer_186.json",
        c78 / "C78_optimizer_362.json",
        c23 / "unconditional_selected_2000.json",
        c23 / "unconditional_selected_5000.json",
        c23 / "unconditional_selected_10000.json",
        c23 / "unconditional_endpoint_10000.json",
    ]
    return [path for path in candidates if path.exists()]


def default_flows() -> list[Path]:
    directory = ROOT / "problems/424/compute/wave5"
    return [
        path
        for cutoff in (54, 74, 186, 362)
        for path in [directory / f"C78_forward_paths_{cutoff}.json"]
        if path.exists()
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scan-stop", type=int, default=500)
    parser.add_argument(
        "--variants",
        nargs="+",
        choices=("no_helper", "helper_only", "thresholds_pay_themselves", "image"),
        default=("no_helper", "helper_only", "thresholds_pay_themselves"),
    )
    parser.add_argument("--workers", type=int, default=64)
    parser.add_argument("--time-limit", type=float, default=30.0)
    args = parser.parse_args()

    result = {
        "schema_version": 1,
        "witness_audits": [witness_audit(path) for path in default_witnesses()],
        "flow_audits": [flow_audit(path) for path in default_flows()],
        "canonical_guardrails": canonical_guardrails(),
        "variant_scans": {
            variant: scan_variant(
                args.scan_stop, variant, args.workers, args.time_limit
            )
            for variant in args.variants
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        f"witnesses={len(result['witness_audits'])} "
        f"variants={','.join(args.variants)}"
    )
    for variant, row in result["variant_scans"].items():
        failure = row.get("first_failure")
        print(
            f"{variant}: tested={row['tested']} "
            f"failure={None if failure is None else failure['cutoff']}"
        )


if __name__ == "__main__":
    main()
